import { defineStore } from 'pinia'
import { ref, reactive } from 'vue'
import { helpdeskApi } from '../api/helpdesk.api'
import { useHelpdeskSocket } from '../composables/useHelpdeskSocket'
import type { HelpdeskChat, HelpdeskChatSummary, HelpdeskMessage, ChatStatus } from '../types/helpdesk.types'

export const useHelpdeskStore = defineStore('helpdesk', () => {

  const chat = ref<HelpdeskChat | null>(null)
  const history = ref<HelpdeskChatSummary[]>([])
  const loading = ref(false)
  const sending = ref(false)
  const error = ref<string | null>(null)

  const unreadByChat = reactive<Record<number, number>>({})

  const agentQueueHasUnread = ref(false)

  const seenMessageIds = new Set<number>()

  const { isConnected, connect, disconnect } = useHelpdeskSocket({

    onMessage(msg: HelpdeskMessage) {
      if (!chat.value) return
      if (seenMessageIds.has(msg.id)) return
      seenMessageIds.add(msg.id)
      chat.value.messages.push(msg)

      const isIncoming = msg.role === 'agent' || (msg.role === 'bot' && msg.content !== null)
      if (isIncoming) {
        unreadByChat[chat.value.id] = (unreadByChat[chat.value.id] ?? 0) + 1
      }
    },

    onStatusChange(newStatus: ChatStatus, chatId: number) {
      if (!chat.value || chat.value.id !== chatId) return
      chat.value.status = newStatus
      if (newStatus === 'agent_open') _refreshMeta(chatId)
      if (newStatus === 'resolved' || newStatus === 'locked') {
        disconnect()
        loadHistory()
      }
    },
  })


  async function _refreshMeta(chatId: number) {
    try {
      const { data } = await helpdeskApi.getChat(chatId)
      if (chat.value?.id === chatId) {
        chat.value.agent_username = data.agent_username
        chat.value.status = data.status
      }
    } catch { }
  }

  function _seedSeen(msgs: HelpdeskMessage[]) {
    msgs.forEach(m => seenMessageIds.add(m.id))
  }

  function _resetSocket() {
    disconnect()
    seenMessageIds.clear()
  }


  function clearUnread(chatId: number) {
    delete unreadByChat[chatId]
  }

  async function loadActiveOrById(id?: number) {
    loading.value = true
    error.value = null
    _resetSocket()

    try {
      if (id) {
        const { data } = await helpdeskApi.getChat(id)
        chat.value = data
        _seedSeen(data.messages)
      } else {
        try {
          const { data } = await helpdeskApi.getActiveChat()
          chat.value = data
          _seedSeen(data.messages)
          if (!['resolved', 'locked'].includes(data.status)) connect(data.id)
        } catch (e: any) {
          if (e?.response?.status === 204) chat.value = null
          else throw e
        }
      }
    } catch {
      error.value = 'Failed to load chat.'
    } finally {
      loading.value = false
    }
  }

  async function loadHistory() {
    try {
      const { data } = await helpdeskApi.listMyClosed()
      history.value = data
    } catch { }
  }

  async function createChat(): Promise<HelpdeskChat | null> {
    loading.value = true
    error.value = null
    _resetSocket()

    try {
      const { data } = await helpdeskApi.createChat()
      chat.value = data
      _seedSeen(data.messages)
      connect(data.id)
      return data
    } catch {
      error.value = 'Failed to create chat.'
      return null
    } finally {
      loading.value = false
    }
  }

  async function sendMessage(text: string): Promise<HelpdeskMessage[] | null> {
    if (!chat.value) return null
    sending.value = true
    try {
      const { data } = await helpdeskApi.sendMessage(chat.value.id, text)
      data.forEach(m => seenMessageIds.add(m.id))
      chat.value.messages.push(...data)

      if (data.some(m => m.role === 'system')) {
        const { data: fresh } = await helpdeskApi.getChat(chat.value.id)
        chat.value.status = fresh.status
        chat.value.agent_username = fresh.agent_username
      }
      return data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || 'Failed to send.'
      return null
    } finally {
      sending.value = false
    }
  }

  async function resolve(): Promise<boolean> {
    if (!chat.value) return false
    try {
      const { data } = await helpdeskApi.resolve(chat.value.id)
      chat.value.status = data.status
      const sys: HelpdeskMessage = {
        id: Date.now(), role: 'system', sender: null,
        content: 'Chat resolved.', created_at: new Date().toISOString(),
      }
      seenMessageIds.add(sys.id)
      chat.value.messages.push(sys)
      disconnect()
      await loadHistory()
      return true
    } catch { return false }
  }

  async function requestAgent(): Promise<boolean> {
    if (!chat.value) return false
    try {
      const { data: msgs } = await helpdeskApi.requestAgent(chat.value.id)
      msgs.forEach(m => seenMessageIds.add(m.id))
      chat.value.messages.push(...msgs)
      const { data: fresh } = await helpdeskApi.getChat(chat.value.id)
      chat.value.status = fresh.status
      return true
    } catch { return false }
  }

  return {
    chat, history, loading, sending, error, isConnected,
    unreadByChat, agentQueueHasUnread,
    clearUnread,
    loadActiveOrById, loadHistory, createChat,
    sendMessage, resolve, requestAgent,
  }
})