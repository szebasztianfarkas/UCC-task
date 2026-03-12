<template>
    <Teleport to="body">
        <Transition name="vc-pop">
            <div v-if="callState === 'incoming'" class="vc-incoming-overlay">
                <div class="vc-incoming-card">
                    <div class="vc-ring-anim">
                        <span class="vc-ring vc-ring--1" />
                        <span class="vc-ring vc-ring--2" />
                        <div class="vc-ring-icon">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                                <path
                                    d="M22 16.92v3a2 2 0 0 1-2.18 2A19.8 19.8 0 0 1 3.08 4.18 2 2 0 0 1 5.09 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L9.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 23 16.92z" />
                            </svg>
                        </div>
                    </div>
                    <p class="vc-incoming-who">
                        <strong>{{ remoteUsername }}</strong> is calling…
                    </p>
                    <div class="vc-incoming-btns">
                        <button class="vc-btn-accept" @click="$emit('accept')">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path
                                    d="M22 16.92v3a2 2 0 0 1-2.18 2A19.8 19.8 0 0 1 3.08 4.18 2 2 0 0 1 5.09 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L9.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 23 16.92z" />
                            </svg>
                            Accept
                        </button>
                        <button class="vc-btn-decline" @click="$emit('decline')">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <line x1="18" y1="6" x2="6" y2="18" />
                                <line x1="6" y1="6" x2="18" y2="18" />
                            </svg>
                            Decline
                        </button>
                    </div>
                </div>
            </div>
        </Transition>
    </Teleport>

    <div class="vc-bar" :class="`vc-bar--${callState}`">

        <template v-if="callState === 'idle'">
            <div class="vc-bar-left">
                <div class="vc-bar-icon" :class="peerConnected ? 'vc-bar-icon--idle' : 'vc-bar-icon--waiting'">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                        <path
                            d="M22 16.92v3a2 2 0 0 1-2.18 2A19.8 19.8 0 0 1 3.08 4.18 2 2 0 0 1 5.09 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L9.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 23 16.92z" />
                    </svg>
                </div>
                <div class="vc-bar-presence">
                    <span v-if="peerConnected" class="vc-bar-label">Voice call available</span>
                    <span v-else class="vc-bar-label vc-bar-label--waiting">
                        Waiting for <strong>{{ peerLabel }}</strong> to open the chat…
                    </span>
                    <div class="vc-presence-dots">
                        <span class="vc-presence-dot vc-presence-dot--self" title="You">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                <circle cx="12" cy="7" r="4" />
                            </svg>
                            <span class="vc-presence-online" />
                        </span>
                        <span class="vc-presence-dot"
                            :class="peerConnected ? 'vc-presence-dot--peer-ready' : 'vc-presence-dot--peer-away'"
                            :title="peerConnected ? 'Peer is ready' : 'Peer not connected'">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                                <circle cx="12" cy="7" r="4" />
                            </svg>
                            <span v-if="peerConnected" class="vc-presence-online" />
                            <span v-else class="vc-presence-offline" />
                        </span>
                    </div>
                </div>
            </div>
            <button class="vc-start-btn" :disabled="!peerConnected" @click="$emit('start')">
                Start call
            </button>
        </template>

        <template v-else-if="callState === 'calling'">
            <div class="vc-bar-left">
                <div class="vc-calling-dots">
                    <span /><span /><span />
                </div>
                <span class="vc-bar-label">Calling<span class="vc-ellipsis" /></span>
            </div>
            <button class="vc-end-btn" @click="$emit('end')">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
                Cancel
            </button>
        </template>

        <template v-else-if="callState === 'active'">
            <div class="vc-bar-left">
                <div class="vc-avatar-pair">
                    <div class="vc-avatar" :class="{ 'vc-avatar--speaking': localSpeaking }">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                            <circle cx="12" cy="7" r="4" />
                        </svg>
                    </div>
                    <div class="vc-live-dot-wrap">
                        <span class="vc-live-dot" />
                    </div>
                    <div class="vc-avatar" :class="{ 'vc-avatar--speaking': peerSpeaking }">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                            <circle cx="12" cy="7" r="4" />
                        </svg>
                    </div>
                </div>
                <div class="vc-bar-info">
                    <span class="vc-duration">{{ formattedDuration }}</span>
                    <span class="vc-with">with <strong>{{ remoteUsername }}</strong></span>
                </div>
            </div>

            <div class="vc-controls">
                <button class="vc-ctrl-btn" :class="{ 'vc-ctrl-btn--active': isMuted }"
                    :title="isMuted ? 'Unmute' : 'Mute'" @click="$emit('toggleMute')">
                    <svg v-if="!isMuted" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z" />
                        <path d="M19 10v2a7 7 0 0 1-14 0v-2" />
                        <line x1="12" y1="19" x2="12" y2="23" />
                        <line x1="8" y1="23" x2="16" y2="23" />
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <line x1="1" y1="1" x2="23" y2="23" />
                        <path d="M9 9v3a3 3 0 0 0 5.12 2.12M15 9.34V4a3 3 0 0 0-5.94-.6" />
                        <path d="M17 16.95A7 7 0 0 1 5 12v-2m14 0v2a7 7 0 0 1-.11 1.23" />
                        <line x1="12" y1="19" x2="12" y2="23" />
                        <line x1="8" y1="23" x2="16" y2="23" />
                    </svg>
                </button>

                <button class="vc-end-btn" @click="$emit('end')" title="End call">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path
                            d="M22 16.92v3a2 2 0 0 1-2.18 2A19.8 19.8 0 0 1 3.08 4.18 2 2 0 0 1 5.09 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L9.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 23 16.92z" />
                    </svg>
                    End call
                </button>
            </div>
        </template>

        <template v-else-if="callState === 'error'">
            <div class="vc-bar-left">
                <svg class="vc-error-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                <span class="vc-bar-label vc-bar-label--error">{{ errorMessage }}</span>
            </div>
        </template>

    </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CallState } from '../composables/useVoiceCall'

const props = defineProps<{
    callState: CallState
    isMuted: boolean
    callDuration: number
    remoteUsername: string | null
    peerSpeaking: boolean
    localSpeaking: boolean
    peerConnected: boolean
    peerLabel: string
    errorMessage: string | null
}>()

defineEmits<{
    start: []
    end: []
    accept: []
    decline: []
    toggleMute: []
}>()

const formattedDuration = computed(() => {
    const m = Math.floor(props.callDuration / 60)
    const s = props.callDuration % 60
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})
</script>