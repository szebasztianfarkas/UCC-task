import { ref } from 'vue'
import type { HelpdeskMessage, ChatStatus } from '../types/helpdesk.types'

export interface AgentSocketCallbacks {
    onMessage: (msg: HelpdeskMessage) => void
    onStatusChange: (status: ChatStatus, chatId: number) => void
}

const WS_BASE = (() => {
    const loc = window.location
    const proto = loc.protocol === 'https:' ? 'wss' : 'ws'
    return `${proto}://${loc.host}/ws`
})()

export function useAgentSocket(callbacks: AgentSocketCallbacks) {
    const isConnected = ref(false)

    let ws: WebSocket | null = null
    let reconnectTimer: ReturnType<typeof setTimeout> | null = null
    let intentionallyClosed = false

    function connect() {
        intentionallyClosed = false
        _open()
    }

    function disconnect() {
        intentionallyClosed = true
        if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
        ws?.close()
        ws = null
        isConnected.value = false
    }

    function refreshRooms() {
        if (ws?.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'refresh_rooms' }))
        }
    }

    function _open() {
        if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
            ws.close()
        }

        const token = localStorage.getItem('access_token') ?? ''
        ws = new WebSocket(`${WS_BASE}/helpdesk/agent/?token=${token}`)

        ws.onopen = () => {
            isConnected.value = true
        }

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data)
                if (data.type === 'message') {
                    callbacks.onMessage(data.message as HelpdeskMessage)
                } else if (data.type === 'status_change') {
                    callbacks.onStatusChange(data.status as ChatStatus, data.chat_id as number)
                }
            } catch { }
        }

        ws.onclose = (event) => {
            isConnected.value = false
            if (intentionallyClosed || event.code === 4001 || event.code === 4003) return
            reconnectTimer = setTimeout(_open, 3000)
        }

        ws.onerror = () => {
            ws?.close()
        }
    }

    return { isConnected, connect, disconnect, refreshRooms }
}