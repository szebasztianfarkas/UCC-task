<template>
  <div class="agent-root">
    <AppSidebar />

    <div class="agent-layout">
      <aside class="agent-queue">
        <div class="agent-panel" ref="panelEl">

          <div class="agent-queue-section" :style="{ flexBasis: queuePct + '%' }">
            <div class="agent-queue-header">
              <h2 class="agent-queue-title">
                Queue
                <span v-if="totalUnread > 0" class="agent-total-badge">{{ totalUnread }}</span>
              </h2>
              <div class="agent-queue-header-right">
                <WsPill :connected="store.isConnected" />
                <button class="agent-refresh-btn" @click="loadQueue" :disabled="queueLoading" title="Refresh">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                    :class="{ spinning: queueLoading }">
                    <polyline points="23 4 23 10 17 10" />
                    <path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10" />
                  </svg>
                </button>
              </div>
            </div>

            <div v-if="queueLoading && !queue.length" class="agent-queue-empty">
              <div class="hd-spinner" />
            </div>
            <div v-else-if="!queue.length" class="agent-queue-empty">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                <polyline points="20 6 9 17 4 12" />
              </svg>
              <p>All clear</p>
            </div>
            <div v-else class="agent-queue-list">
              <button v-for="c in queue" :key="c.id" class="agent-queue-item" :class="{
                'agent-queue-item--active': activeChat?.id === c.id,
                [`agent-queue-item--${c.status}`]: true,
              }" @click="openChat(c.id)">
                <div class="aqi-top">
                  <span class="aqi-user">{{ c.user_username }}</span>
                  <div class="aqi-right">
                    <span v-if="store.agentUnreadByChat[c.id]" class="aqi-unread-badge">
                      {{ store.agentUnreadByChat[c.id] > 9 ? "9+" : store.agentUnreadByChat[c.id] }}
                    </span>
                    <span class="aqi-status-dot" :class="`aqi-dot--${c.status}`" />
                  </div>
                </div>
                <p v-if="c.last_message" class="aqi-preview">{{ c.last_message.content }}</p>
                <span class="aqi-time">{{ timeAgo(c.updated_at) }}</span>
              </button>
            </div>
          </div>

          <div class="agent-panel-divider" :class="{ 'agent-panel-divider--dragging': dragging }"
            @mousedown.prevent="startDrag">
            <div class="agent-panel-divider-grip">
              <span /><span /><span />
            </div>
          </div>

          <div class="agent-history-section" :style="{ flexBasis: historyPct + '%' }">
            <div class="agent-history-header">
              <span class="agent-history-title">History</span>
              <input v-model="historySearch" class="agent-history-search" placeholder="Search…"
                @input="debouncedSearch" />
            </div>

            <div v-if="historyLoading" class="agent-history-loading">
              <div class="hd-spinner" />
            </div>
            <div v-else-if="!historyItems.length" class="agent-history-empty">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <p>{{ historySearch ? 'No results' : 'No closed chats yet' }}</p>
            </div>
            <div v-else class="agent-history-list">
              <button v-for="c in historyItems" :key="c.id" class="agent-history-item"
                :class="{ 'agent-history-item--active': activeChat?.id === c.id }" @click="openChat(c.id)">
                <div class="ahi-top">
                  <span class="ahi-user">{{ c.user_username }}</span>
                  <span class="ahi-status" :class="`ahi-status--${c.status}`">{{ c.status }}</span>
                </div>
                <p v-if="c.last_message" class="ahi-preview">{{ c.last_message.content }}</p>
                <span class="ahi-agent">
                  {{ c.agent_username ? `Agent: ${c.agent_username}` : 'Unassigned' }}
                  · {{ timeAgo(c.updated_at) }}
                </span>
              </button>
            </div>

            <div v-if="historyPages > 1" class="agent-history-pagination">
              <button class="agent-history-page-btn" :disabled="historyPage <= 1" @click="changePage(historyPage - 1)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="10" height="10">
                  <polyline points="15 18 9 12 15 6" />
                </svg>
              </button>
              <span class="agent-history-page-info">{{ historyPage }} / {{ historyPages }}</span>
              <button class="agent-history-page-btn" :disabled="historyPage >= historyPages"
                @click="changePage(historyPage + 1)">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="10" height="10">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </button>
            </div>
          </div>

        </div>
      </aside>

      <main class="agent-chat">
        <div v-if="!activeChat && !chatLoading" class="agent-empty">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
          <p>Select a chat from the queue or history</p>
        </div>

        <div v-else-if="chatLoading" class="agent-empty">
          <div class="hd-spinner" />
        </div>

        <template v-else-if="activeChat">
          <div class="agent-chat-header">
            <div class="agent-chat-user">
              <div class="acu-initial">{{ activeChat.user_username[0].toUpperCase() }}</div>
              <div>
                <p class="acu-name">{{ activeChat.user_username }}</p>
                <p class="acu-meta">
                  Chat #{{ activeChat.id }} · {{ formatDate(activeChat.created_at) }}
                  <span v-if="store.isConnected && isActiveChatLive" class="acu-live-dot" title="Live connection" />
                </p>
              </div>
            </div>
            <div class="agent-chat-actions">
              <span class="hd-status-badge" :class="`hd-status-badge--${activeChat.status}`">
                {{ statusLabel(activeChat.status) }}
              </span>
              <button v-if="activeChat.status === 'waiting'" class="btn-primary btn-sm" @click="assign"
                :disabled="assigning">
                <span v-if="!assigning">Take chat</span>
                <span v-else class="spinner" />
              </button>
              <button v-if="activeChat.status === 'agent_open'" class="btn-danger btn-sm" @click="resolveChat"
                :disabled="resolving">
                <span v-if="!resolving">Close chat</span>
                <span v-else class="spinner" />
              </button>
            </div>
          </div>

          <div class="agent-messages" ref="agentMsgList">
            <template v-for="msg in activeChat.messages" :key="msg.id">
              <MessageBubble :msg="msg" :is-history="true" />
            </template>
            <div v-if="sending" class="hd-bubble hd-bubble--bot hd-bubble--typing">
              <div class="hd-bubble-body">
                <span class="typing-dot" /><span class="typing-dot" /><span class="typing-dot" />
              </div>
            </div>
          </div>

          <VoiceCallBar v-if="activeChat.status === 'agent_open'" :call-state="voice.callState.value"
            :is-muted="voice.isMuted.value" :call-duration="voice.callDuration.value"
            :remote-username="voice.remoteUsername.value" :peer-speaking="voice.peerSpeaking.value"
            :local-speaking="voice.localSpeaking.value" :peer-connected="voice.peerConnected.value"
            peer-label="the user" :error-message="voice.errorMessage.value" @start="voice.startCall()"
            @end="voice.endCall()" @accept="voice.acceptCall()" @decline="voice.declineCall()"
            @toggle-mute="voice.toggleMute()" />

          <div v-if="activeChat.status === 'agent_open'" class="hd-input-bar">
            <div class="hd-input-row">
              <textarea v-model="agentDraft" class="hd-input" placeholder="Reply to user…" rows="1" :disabled="sending"
                @keydown.enter.exact.prevent="agentSend" @input="autoResize" ref="agentInputEl" />
              <button class="hd-send-btn" :disabled="sending || !agentDraft.trim()" @click="agentSend">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              </button>
            </div>
          </div>

          <div v-else-if="activeChat.status === 'waiting'" class="notice-bar notice-bar--warning">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10" />
              <polyline points="12 6 12 12 16 14" />
            </svg>
            Click "Take chat" to assign yourself and start replying.
          </div>
        </template>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, onUnmounted, watch } from 'vue'
import { helpdeskApi } from '../api/helpdesk.api'
import { useHelpdeskStore } from '../store/helpdesk.store'
import { useVoiceCall } from '../composables/useVoiceCall'
import type { HelpdeskChat, HelpdeskChatSummary, HelpdeskMessage, ChatStatus } from '../types/helpdesk.types'
import AppSidebar from '@/features/sidebar/components/Sidebar.vue'
import WsPill from '@/shared/components/WsPill.vue'
import MessageBubble from './MessageBubble.vue'
import VoiceCallBar from './VoiceCallBar.vue'
import './agent.css'
import './voicecall.css'

const store = useHelpdeskStore()

const queue = ref<HelpdeskChatSummary[]>([])
const activeChat = ref<HelpdeskChat | null>(null)
const queueLoading = ref(false)
const chatLoading = ref(false)
const assigning = ref(false)
const resolving = ref(false)
const sending = ref(false)
const agentDraft = ref('')
const agentMsgList = ref<HTMLElement | null>(null)
const agentInputEl = ref<HTMLTextAreaElement | null>(null)

const isActiveChatLive = computed(() =>
  !!activeChat.value && ['waiting', 'agent_open'].includes(activeChat.value.status)
)

const panelEl = ref<HTMLElement | null>(null)
const queuePct = ref(55)
const historyPct = computed(() => 100 - queuePct.value)
const dragging = ref(false)

function startDrag(e: MouseEvent) {
  dragging.value = true
  const startY = e.clientY
  const startPct = queuePct.value
  const panel = panelEl.value
  if (!panel) return

  function onMove(ev: MouseEvent) {
    const totalH = panel.getBoundingClientRect().height
    const deltaPct = ((ev.clientY - startY) / totalH) * 100
    queuePct.value = Math.min(85, Math.max(15, startPct + deltaPct))
  }
  function onUp() {
    dragging.value = false
    window.removeEventListener('mousemove', onMove)
    window.removeEventListener('mouseup', onUp)
  }
  window.addEventListener('mousemove', onMove)
  window.addEventListener('mouseup', onUp)
}

const historyItems = ref<HelpdeskChatSummary[]>([])
const historyPage = ref(1)
const historyPages = ref(1)
const historyLoading = ref(false)
const historySearch = ref('')
let searchDebounce: ReturnType<typeof setTimeout> | null = null

async function loadHistory(page = 1) {
  historyLoading.value = true
  try {
    const { data } = await helpdeskApi.agentHistory(page, historySearch.value)
    historyItems.value = data.results
    historyPage.value = data.page
    historyPages.value = data.pages
  } catch { } finally {
    historyLoading.value = false
  }
}

function debouncedSearch() {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => loadHistory(1), 320)
}

function changePage(p: number) { loadHistory(p) }

const totalUnread = computed(() =>
  Object.values(store.agentUnreadByChat).reduce((s, n) => s + n, 0)
)

const seenIdsByChatId = new Map<number, Set<number>>()

function _seenFor(chatId: number): Set<number> {
  if (!seenIdsByChatId.has(chatId)) seenIdsByChatId.set(chatId, new Set())
  return seenIdsByChatId.get(chatId)!
}

function handleAgentMessage(msg: HelpdeskMessage) {
  const chatId = msg.chat_id
  if (!chatId) return

  const seen = _seenFor(chatId)
  if (seen.has(msg.id)) return
  seen.add(msg.id)

  if (activeChat.value?.id === chatId) {
    const tempIndex = activeChat.value.messages.findIndex(m => m.id < 0)
    if (tempIndex !== -1) {
      const tempMsg = activeChat.value.messages[tempIndex]
      if (tempMsg.content === msg.content && msg.role === 'agent') {
        activeChat.value.messages.splice(tempIndex, 1, msg)
        return
      }
    }
    activeChat.value.messages.push(msg)
    store.clearAgentUnread(chatId)
  } else {
    if (msg.role === 'user') {
      store.agentUnreadByChat[chatId] = (store.agentUnreadByChat[chatId] ?? 0) + 1
      store.agentQueueHasUnread = true
    }
  }

  const qItem = queue.value.find(c => c.id === chatId)
  if (qItem && msg.content) {
    qItem.last_message = { role: msg.role, content: msg.content }
  }
}

function handleAgentStatusChange(newStatus: ChatStatus, chatId: number) {
  const qItem = queue.value.find(c => c.id === chatId)
  if (qItem) qItem.status = newStatus

  if (activeChat.value?.id === chatId) {
    activeChat.value.status = newStatus
    if (newStatus === 'agent_open') {
      helpdeskApi.getChat(chatId).then(({ data }) => {
        if (activeChat.value?.id === chatId) activeChat.value.agent_username = data.agent_username
      }).catch(() => { })
    }
  }

  if (newStatus === 'resolved' || newStatus === 'locked') {
    queue.value = queue.value.filter(c => c.id !== chatId)
    seenIdsByChatId.delete(chatId)
    loadHistory(historyPage.value)
  }
}

const voice = useVoiceCall()

watch(
  () => ({ chatId: activeChat.value?.id, status: activeChat.value?.status }),
  async ({ chatId, status }) => {
    voice.disconnect()
    if (status === 'agent_open' && chatId) {
      await voice.connect(chatId)
    }
  },
)

watch(
  () => activeChat.value?.messages.length,
  async () => {
    await nextTick();
    scrollMsgs();
  },
);

let queuePollTimer: ReturnType<typeof setInterval>

onMounted(async () => {
  store.setAgentCallbacks(handleAgentMessage, handleAgentStatusChange)
  store.connectAgentSocket()
  await Promise.all([loadQueue(), loadHistory()])
  queuePollTimer = setInterval(loadQueue, 30_000)
})

onUnmounted(() => {
  clearInterval(queuePollTimer)
  store.setAgentCallbacks(null, null)
  voice.disconnect()
  if (searchDebounce) clearTimeout(searchDebounce)
})

async function loadQueue() {
  queueLoading.value = true
  try {
    const { data } = await helpdeskApi.agentQueue()
    queue.value = data
    store.refreshAgentRooms()
  } finally {
    queueLoading.value = false
  }
}

async function openChat(id: number) {
  store.clearAgentUnread(id)
  chatLoading.value = true
  try {
    const { data } = await helpdeskApi.getChat(id)
    activeChat.value = data
    const seen = _seenFor(id)
    seen.clear()
    data.messages.forEach((m: HelpdeskMessage) => seen.add(m.id))
    helpdeskApi.markRead(id).catch(() => { })
  } finally {
    chatLoading.value = false
  }
}

async function assign() {
  if (!activeChat.value) return
  assigning.value = true
  try {
    const { data } = await helpdeskApi.agentAssign(activeChat.value.id)
    const seen = _seenFor(data.id)
    data.messages.forEach((m: HelpdeskMessage) => seen.add(m.id))
    activeChat.value = data
    await loadQueue()
  } finally {
    assigning.value = false
  }
}

async function resolveChat() {
  if (!activeChat.value) return
  resolving.value = true
  try {
    await helpdeskApi.agentResolve(activeChat.value.id)
    const sys: HelpdeskMessage = {
      id: Date.now(), role: 'system', sender: null,
      content: 'Chat resolved by agent.',
      created_at: new Date().toISOString(),
      chat_id: activeChat.value.id,
    }
    _seenFor(activeChat.value.id).add(sys.id)
    activeChat.value.messages.push(sys)
    activeChat.value.status = 'resolved'
    queue.value = queue.value.filter(c => c.id !== activeChat.value!.id)
    voice.disconnect()
    loadHistory(historyPage.value)
  } finally {
    resolving.value = false
  }
}

async function agentSend() {
  if (!activeChat.value || !agentDraft.value.trim()) return
  sending.value = true
  const text = agentDraft.value.trim()
  agentDraft.value = ''
  if (agentInputEl.value) agentInputEl.value.style.height = 'auto'

  const tempId = -Date.now()
  const tempMsg: HelpdeskMessage = {
    id: tempId,
    role: 'agent',
    sender: null,
    content: text,
    chat_id: activeChat.value.id,
    created_at: new Date().toISOString(),
  }
  activeChat.value.messages.push(tempMsg)

  try {
    const { data } = await helpdeskApi.sendMessage(activeChat.value.id, text)
    const seen = _seenFor(activeChat.value.id)
    const tempIndex = activeChat.value.messages.findIndex(m => m.id === tempId)
    if (tempIndex !== -1) {
      activeChat.value.messages.splice(tempIndex, 1, ...data)
    } else {
      data.forEach((m: HelpdeskMessage) => {
        if (!seen.has(m.id)) activeChat.value!.messages.push(m)
      })
    }
    data.forEach((m: HelpdeskMessage) => seen.add(m.id))
  } catch {
    const idx = activeChat.value.messages.findIndex(m => m.id === tempId)
    if (idx !== -1) activeChat.value.messages.splice(idx, 1)
  } finally {
    sending.value = false
  }
}

function scrollMsgs() {
  const el = agentMsgList.value;
  if (!el) return;

  el.scrollTo({
    top: el.scrollHeight,
    behavior: "smooth",
  });
}

function autoResize(e: Event) {
  const el = e.target as HTMLTextAreaElement
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 140) + 'px'
}
function statusLabel(s: string) {
  return ({
    open: 'Open', waiting: 'Waiting', agent_open: 'With agent',
    resolved: 'Resolved', locked: 'Locked'
  } as Record<string, string>)[s] ?? s
}
function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString([], { day: 'numeric', month: 'short', year: 'numeric' })
}
function timeAgo(iso: string) {
  const m = Math.floor((Date.now() - new Date(iso).getTime()) / 60000)
  if (m < 1) return 'just now'
  if (m < 60) return `${m}m ago`
  const h = Math.floor(m / 60)
  if (h < 24) return `${h}h ago`
  return `${Math.floor(h / 24)}d ago`
}
</script>