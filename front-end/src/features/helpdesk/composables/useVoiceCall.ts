import { ref, onUnmounted } from 'vue'

export type CallState = 'idle' | 'calling' | 'incoming' | 'active' | 'error'

export interface VoiceCallCallbacks {
    onStateChange?: (state: CallState) => void
    onIncomingCall?: (from: string) => void
    onCallEnded?: () => void
    onError?: (msg: string) => void
    onPeerSpeaking?: (active: boolean) => void
}

const ICE_SERVERS: RTCIceServer[] = [
    { urls: 'stun:stun.l.google.com:19302' },
    { urls: 'stun:stun1.l.google.com:19302' },
]

const WS_BASE = (() => {
    const loc = window.location
    const proto = loc.protocol === 'https:' ? 'wss' : 'ws'
    return `${proto}://${loc.host}/ws`
})()

export function useVoiceCall(callbacks: VoiceCallCallbacks = {}) {
    const callState = ref<CallState>('idle')
    const isMuted = ref(false)
    const callDuration = ref(0)
    const remoteUsername = ref<string | null>(null)
    const peerSpeaking = ref(false)
    const localSpeaking = ref(false)
    const peerConnected = ref(false)
    const errorMessage = ref<string | null>(null)

    let ws: WebSocket | null = null
    let pc: RTCPeerConnection | null = null
    let localStream: MediaStream | null = null
    let remoteAudioEl: HTMLAudioElement | null = null
    let durationTimer: ReturnType<typeof setInterval> | null = null
    let currentChatId: number | null = null

    let audioCtx: AudioContext | null = null
    let localAnalyser: AnalyserNode | null = null
    let localVadTimer: ReturnType<typeof setInterval> | null = null
    let pendingCandidates: RTCIceCandidateInit[] = []
    let pendingOffer;

    function setState(s: CallState) {
        callState.value = s
        callbacks.onStateChange?.(s)
    }

    function setError(msg: string) {
        errorMessage.value = msg
        setState('error')
        callbacks.onError?.(msg)
        setTimeout(() => {
            if (callState.value === 'error') setState('idle')
            errorMessage.value = null
        }, 5000)
    }

    function startDurationTimer() {
        callDuration.value = 0
        durationTimer = setInterval(() => { callDuration.value++ }, 1000)
    }

    function stopDurationTimer() {
        if (durationTimer) { clearInterval(durationTimer); durationTimer = null }
        callDuration.value = 0
    }

    function startLocalVAD(stream: MediaStream) {
        try {
            audioCtx = new AudioContext()
            const source = audioCtx.createMediaStreamSource(stream)
            localAnalyser = audioCtx.createAnalyser()
            localAnalyser.fftSize = 512
            source.connect(localAnalyser)
            const buf = new Uint8Array(localAnalyser.frequencyBinCount)
            localVadTimer = setInterval(() => {
                if (!localAnalyser) return
                localAnalyser.getByteFrequencyData(buf)
                const avg = buf.reduce((a, b) => a + b, 0) / buf.length
                localSpeaking.value = avg > 10
            }, 100)
        } catch { }
    }

    function stopLocalVAD() {
        if (localVadTimer) { clearInterval(localVadTimer); localVadTimer = null }
        localSpeaking.value = false
        audioCtx?.close().catch(() => { })
        audioCtx = null
        localAnalyser = null
    }

    function openSignalSocket(chatId: number): Promise<void> {
        return new Promise((resolve, reject) => {
            const token = localStorage.getItem('access_token') ?? ''
            ws = new WebSocket(`${WS_BASE}/helpdesk/${chatId}/voice/?token=${token}`)

            ws.onopen = () => resolve()

            ws.onerror = () => {
                reject(new Error('Signalling socket failed to open'))
            }

            ws.onclose = (ev) => {
                if (callState.value === 'active' || callState.value === 'calling') {
                    teardown()
                    setError('Call disconnected (network issue)')
                }
            }

            ws.onmessage = (ev) => {
                try {
                    const msg = JSON.parse(ev.data)
                    handleSignal(msg)
                } catch { }
            }
        })
    }

    function send(payload: object) {
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify(payload))
        }
    }

    function addLocalTracks(conn: RTCPeerConnection, stream: MediaStream) {
        const existingTracks = conn.getSenders().map(s => s.track)
        stream.getTracks().forEach(track => {
            if (!existingTracks.includes(track)) {
                conn.addTrack(track, stream)
            }
        })
    }

    async function handleSignal(msg: Record<string, any>) {
        switch (msg.type) {
            case 'call-start':
                if (callState.value !== 'idle') {
                    send({ type: 'call-busy' })
                    return
                }
                remoteUsername.value = msg.from ?? null
                setState('incoming')
                callbacks.onIncomingCall?.(msg.from ?? 'Unknown')
                break

            case 'call-busy':
                setError(`${msg.from} is already in another call.`)
                teardown()
                break

            case 'offer':
                if (callState.value !== 'idle' && callState.value !== 'incoming') {
                    send({ type: 'call-busy' })
                    return
                }
                remoteUsername.value = msg.from ?? null
                pendingOffer = msg.sdp
                setState('incoming')
                callbacks.onIncomingCall?.(remoteUsername.value)
                break

            case 'answer':
                if (!pc) return
                try {
                    await pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp: msg.sdp }))
                    for (const c of pendingCandidates) {
                        await pc.addIceCandidate(new RTCIceCandidate(c)).catch(() => { })
                    }
                    pendingCandidates = []
                } catch (e) {
                    setError('Failed to process answer from peer.')
                }
                break

            case 'ice-candidate':
                if (!msg.candidate) return
                if (pc && pc.remoteDescription) {
                    await pc.addIceCandidate(new RTCIceCandidate(msg.candidate)).catch(() => { })
                } else {
                    pendingCandidates.push(msg.candidate)
                }
                break
            
            case 'peer-present':
            case 'peer-joined':
                peerConnected.value = true
                break

            case 'peer-left':
                peerConnected.value = false
                if (callState.value !== 'idle') {
                    teardown()
                    callbacks.onCallEnded?.()
                }
                break

            case 'call-end':
                if (callState.value !== 'idle') {
                    teardown()
                    callbacks.onCallEnded?.()
                }
                break
        }
    }

    function createPeerConnection() {
        pc = new RTCPeerConnection({ iceServers: ICE_SERVERS })

        pc.onicecandidate = (ev) => {
            if (ev.candidate) {
                send({ type: 'ice-candidate', candidate: ev.candidate.toJSON() })
            }
        }

        pc.ontrack = (ev) => {
            if (!remoteAudioEl) {
                remoteAudioEl = document.createElement('audio')
                remoteAudioEl.autoplay = true
                remoteAudioEl.style.display = 'none'
                document.body.appendChild(remoteAudioEl)
            }
            remoteAudioEl.srcObject = ev.streams[0]

            const track = ev.streams[0].getAudioTracks()[0]
            if (track) {
                try {
                    const ctx = new AudioContext()
                    const src = ctx.createMediaStreamSource(ev.streams[0])
                    const analyzer = ctx.createAnalyser()
                    analyzer.fftSize = 512
                    src.connect(analyzer)
                    const buf = new Uint8Array(analyzer.frequencyBinCount)
                    const vadTimer = setInterval(() => {
                        if (!pc) { clearInterval(vadTimer); ctx.close(); return }
                        analyzer.getByteFrequencyData(buf)
                        const avg = buf.reduce((a, b) => a + b, 0) / buf.length
                        const speaking = avg > 10
                        if (peerSpeaking.value !== speaking) {
                            peerSpeaking.value = speaking
                            callbacks.onPeerSpeaking?.(speaking)
                        }
                    }, 100)
                } catch { }
            }

            setState('active')
            startDurationTimer()
        }

        pc.onconnectionstatechange = () => {
            if (pc?.connectionState === 'failed' || pc?.connectionState === 'disconnected') {
                teardown()
                setError('Peer connection lost.')
            }
        }

        return pc
    }

    async function handleOffer(sdp: string) {
        if (!localStream) return
        const conn = pc || createPeerConnection()
        await conn.setRemoteDescription(new RTCSessionDescription({ type: 'offer', sdp }))

        for (const c of pendingCandidates) {
            await conn.addIceCandidate(new RTCIceCandidate(c)).catch(() => { })
        }
        pendingCandidates = []

        const answer = await conn.createAnswer()
        await conn.setLocalDescription(answer)
        send({ type: 'answer', sdp: answer.sdp })
    }

    async function connect(chatId: number) {
        currentChatId = chatId
        try {
            await openSignalSocket(chatId)
        } catch (e) {
            setError('Could not connect to voice signalling server.')
        }
    }

    async function startCall() {
        if (callState.value !== 'idle' || !currentChatId) return

        try {
            localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        } catch {
            setError('Microphone access denied. Please allow microphone access.')
            return
        }

        setState('calling')
        startLocalVAD(localStream)

        if (!ws || ws.readyState !== WebSocket.OPEN) {
            try { await openSignalSocket(currentChatId) }
            catch { setError('Could not reach signalling server.'); return }
        }

        send({ type: 'call-start' })

        const conn = createPeerConnection()
        addLocalTracks(conn, localStream)

        const offer = await conn.createOffer()
        await conn.setLocalDescription(offer)
        send({ type: 'offer', sdp: offer.sdp })
    }

    async function acceptCall() {
        if (callState.value !== 'incoming') return
        if (!remoteUsername.value) return

        try {
            localStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false })
        } catch {
            setError('Microphone access denied.')
            return
        }

        startLocalVAD(localStream)

        const conn = pc || createPeerConnection()
        addLocalTracks(conn, localStream)

        await handleOffer(pendingOffer)
        pendingOffer = null
        setState('active')
    }

    function declineCall() {
        send({ type: 'call-end' })
        teardown()
    }

    function endCall() {
        send({ type: 'call-end' })
        teardown()
        callbacks.onCallEnded?.()
    }

    function toggleMute() {
        if (!localStream) return
        const enabled = localStream.getAudioTracks()[0]?.enabled ?? false
        localStream.getAudioTracks().forEach(t => { t.enabled = !enabled })
        isMuted.value = enabled
    }

    function disconnect() {
        teardown()
        ws?.close()
        ws = null
    }

    function teardown() {
        stopDurationTimer()
        stopLocalVAD()
        peerSpeaking.value = false
        isMuted.value = false
        pendingCandidates = []

        pc?.close()
        pc = null

        localStream?.getTracks().forEach(t => t.stop())
        localStream = null

        if (remoteAudioEl) {
            remoteAudioEl.srcObject = null
            remoteAudioEl.remove()
            remoteAudioEl = null
        }

        setState('idle')
    }

    onUnmounted(() => {
        disconnect()
    })

    return {
        callState,
        isMuted,
        callDuration,
        remoteUsername,
        peerSpeaking,
        localSpeaking,
        peerConnected,
        errorMessage,

        connect,
        disconnect,
        startCall,
        acceptCall,
        declineCall,
        endCall,
        toggleMute,
    }
}
