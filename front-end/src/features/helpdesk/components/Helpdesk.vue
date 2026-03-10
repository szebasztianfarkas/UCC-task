<template>
  <div class="hd-root">
    <AppSidebar />

    <main class="hd-main">

      <div v-if="store.loading" class="hd-state">
        <div class="hd-spinner" />
      </div>

      <template v-else-if="isHistory && store.chat">
        <header class="hd-header">
          <div class="hd-header-left">
            <button class="hd-back-btn" @click="goNew">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 18 9 12 15 6"/>
              </svg>
            </button>
            <div class="hd-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div>
              <h1 class="hd-title">Chat #{{ store.chat.id }}</h1>
              <p class="hd-sub">{{ formatDate(store.chat.created_at) }}</p>
            </div>
          </div>
          <span class="hd-status-badge" :class="`hd-status-badge--${store.chat.status}`">
            {{ statusLabel(store.chat.status) }}
          </span>
        </header>
        <div class="hd-messages" ref="messageList">
          <MessageBubble v-for="msg in store.chat.messages" :key="msg.id" :msg="msg" :is-history="true" />
        </div>
        <div class="hd-locked-bar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2a5 5 0 0 1 5 5v3H7V7a5 5 0 0 1 5-5z"/>
            <rect x="3" y="10" width="18" height="12" rx="2"/>
          </svg>
          This conversation is archived.
          <button class="hd-link-btn" @click="goNew">Start a new chat →</button>
        </div>
      </template>

      <template v-else-if="!store.chat && !store.loading">
        <header class="hd-header">
          <div class="hd-header-left">
            <div class="hd-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div><h1 class="hd-title">Helpdesk</h1><p class="hd-sub">We're here to help</p></div>
          </div>
        </header>
        <div class="hd-state">
          <div class="hd-empty-card">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
            <p>Have a question about Evently?</p>
            <span>Our bot answers common questions instantly. If it can't help, a support agent will take over.</span>
            <button class="btn-primary" @click="startChat">Start a chat</button>
          </div>
        </div>
      </template>

      <template v-else-if="store.chat">
        <header class="hd-header">
          <div class="hd-header-left">
            <div class="hd-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10"/>
                <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
                <line x1="12" y1="17" x2="12.01" y2="17"/>
              </svg>
            </div>
            <div>
              <h1 class="hd-title">
                Helpdesk
              </h1>
              <p class="hd-sub" v-if="store.chat.agent_username">
                <span class="hd-agent-online-dot" />
                Agent: <strong>{{ store.chat.agent_username }}</strong>
              </p>
              <p class="hd-sub" v-else>Ask anything about Evently</p>
            </div>
          </div>
          <div class="hd-header-right">
            <span class="ws-pill" :class="store.isConnected ? 'ws-pill--on' : 'ws-pill--off'"
              :title="store.isConnected ? 'Live connection' : 'Reconnecting…'">
              <span class="ws-dot" />{{ store.isConnected ? 'Live' : 'Off' }}
            </span>
            <span class="hd-status-badge" :class="`hd-status-badge--${store.chat.status}`">
              {{ statusLabel(store.chat.status) }}
            </span>
          </div>
        </header>

        <div class="hd-messages" ref="messageList">
          <div class="hd-welcome">
            <p>Hi <strong>{{ authStore.user?.username }}</strong> 👋 — what can I help you with?</p>
            <p class="hd-welcome-sub">Ask about events, your account, MFA, or anything else about Evently.</p>
          </div>

          <template v-for="(msg, idx) in store.chat.messages" :key="msg.id">
            <MessageBubble
              :msg="msg"
              :show-resolution="shouldShowResolution(idx)"
              :resolving="resolving"
              @resolve="handleResolve"
              @request-agent="handleRequestAgent"
            />
          </template>

          <div v-if="store.sending" class="hd-bubble hd-bubble--bot hd-bubble--typing">
            <div class="hd-bubble-body">
              <span class="typing-dot"/><span class="typing-dot"/><span class="typing-dot"/>
            </div>
          </div>

          <div ref="scrollAnchor" />
        </div>

        <div v-if="store.chat.status === 'waiting'" class="hd-notice hd-notice--waiting">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>
          </svg>
          Waiting for a helpdesk agent to join — you can keep adding context below.
        </div>

        <div v-else-if="store.chat.status === 'resolved' || store.chat.status === 'locked'" class="hd-locked-bar">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M12 2a5 5 0 0 1 5 5v3H7V7a5 5 0 0 1 5-5z"/>
            <rect x="3" y="10" width="18" height="12" rx="2"/>
          </svg>
          This chat is closed.
          <button class="hd-link-btn" @click="goNew">Start a new chat →</button>
        </div>

        <div
          v-if="store.chat.status !== 'resolved' && store.chat.status !== 'locked'"
          class="hd-input-bar"
        >
          <textarea
            v-model="draft"
            class="hd-input"
            :placeholder="inputPlaceholder"
            rows="1"
            :disabled="store.sending"
            @keydown.enter.exact.prevent="submit"
            @input="autoResize"
            ref="inputEl"
          />
          <button class="hd-send-btn" :disabled="store.sending || !draft.trim()" @click="submit">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="22" y1="2" x2="11" y2="13"/>
              <polygon points="22 2 15 22 11 13 2 9 22 2"/>
            </svg>
          </button>
        </div>
      </template>

    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useHelpdeskStore } from '../store/helpdesk.store'
import { useAuthStore } from '@/features/auth/store/auth.store'
import AppSidebar from '@/features/sidebar/components/Sidebar.vue'
import MessageBubble from './MessageBubble.vue'
import './helpdesk.css'

const store     = useHelpdeskStore()
const authStore = useAuthStore()
const route     = useRoute()
const router    = useRouter()

const draft        = ref('')
const messageList  = ref<HTMLElement | null>(null)
const scrollAnchor = ref<HTMLElement | null>(null)
const inputEl      = ref<HTMLTextAreaElement | null>(null)
const resolving    = ref(false)

const historyId = computed(() => route.query.id ? Number(route.query.id) : null)
const isHistory = computed(() => !!historyId.value)

const unreadCount = computed(() =>
  store.chat ? (store.unreadByChat[store.chat.id] ?? 0) : 0
)

const inputPlaceholder = computed(() => {
  if (!store.chat) return 'Type your message…'
  if (store.chat.status === 'waiting') return 'Add more context while you wait…'
  if (store.chat.status === 'agent_open') return 'Reply to agent…'
  return 'Type your message…'
})

onMounted(async () => {
  if (historyId.value) {
    await store.loadActiveOrById(historyId.value)
  } else {
    await store.loadActiveOrById()
    if (store.chat) store.clearUnread(store.chat.id)
  }
  await nextTick()
  scrollToBottom()
})

onUnmounted(() => {})

watch(() => route.query.id, async (newId) => {
  if (newId) {
    await store.loadActiveOrById(Number(newId))
  } else {
    await store.loadActiveOrById()
    if (store.chat) store.clearUnread(store.chat.id)
  }
  await nextTick(); scrollToBottom()
})

watch(() => store.chat?.messages.length, async () => {
  await nextTick()
  scrollToBottom()
  if (store.chat && !isHistory.value) store.clearUnread(store.chat.id)
})

watch(unreadCount, (n) => {
  document.title = n > 0 ? `(${n}) Helpdesk – Evently` : 'Helpdesk – Evently'
})

onUnmounted(() => { document.title = 'Evently' })

function scrollToBottom() {
  scrollAnchor.value?.scrollIntoView({ behavior: 'smooth', block: 'end' })
}

function autoResize(e: Event) {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}

function statusLabel(s: string) {
  return ({ open: 'Open', waiting: 'Waiting', agent_open: 'With agent',
            resolved: 'Resolved', locked: 'Locked' } as Record<string, string>)[s] ?? s
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' })
}

function shouldShowResolution(idx: number): boolean {
  if (!store.chat) return false
  if (['resolved', 'locked', 'agent_open', 'waiting'].includes(store.chat.status)) return false
  if (store.sending || resolving.value) return false
  const msgs = store.chat.messages
  const msg  = msgs[idx]
  if (msg.role !== 'bot' || msg.content === null) return false
  for (let i = idx + 1; i < msgs.length; i++) {
    if (msgs[i].role === 'bot' && msgs[i].content !== null) return false
    if (msgs[i].role === 'user') return false
  }
  return true
}

async function startChat() {
  const c = await store.createChat()
  if (c) router.replace({ name: 'helpdesk' })
}

function goNew() {
  router.push({ name: 'helpdesk' })
}

async function submit() {
  const text = draft.value.trim()
  if (!text || store.sending) return
  draft.value = ''
  if (inputEl.value) inputEl.value.style.height = 'auto'
  await store.sendMessage(text)
}

async function handleResolve() {
  resolving.value = true
  await store.resolve()
  resolving.value = false
}

async function handleRequestAgent() {
  resolving.value = true
  await store.requestAgent()
  resolving.value = false
}
</script>