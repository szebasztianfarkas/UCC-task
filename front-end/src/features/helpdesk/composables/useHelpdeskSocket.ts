import { ref, type Ref } from 'vue'
import type { HelpdeskMessage, ChatStatus } from '../types/helpdesk.types'

export interface SocketCallbacks {
  onMessage:      (msg: HelpdeskMessage) => void
  onStatusChange: (status: ChatStatus, chatId: number) => void
}

export interface HelpdeskSocket {
  isConnected: Ref<boolean>
  connect:     (chatId: number) => void
  disconnect:  () => void
}

const WS_BASE = (() => {
  const loc = window.location
  const proto = loc.protocol === 'https:' ? 'wss' : 'ws'
  return `${proto}://${loc.host}/ws`
})()

export function useHelpdeskSocket(callbacks: SocketCallbacks): HelpdeskSocket {
  const isConnected = ref(false)
  let ws:            WebSocket | null = null
  let reconnectTimer: ReturnType<typeof setTimeout> | null = null
  let currentChatId:  number | null = null
  let intentionallyClosed = false

  function connect(chatId: number) {
    intentionallyClosed = false
    currentChatId = chatId
    _open(chatId)
  }

  function disconnect() {
    intentionallyClosed = true
    currentChatId = null
    if (reconnectTimer) { clearTimeout(reconnectTimer); reconnectTimer = null }
    ws?.close()
    ws = null
    isConnected.value = false
  }

  function _open(chatId: number) {
    if (ws && (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING)) {
      ws.close()
    }

    const token = localStorage.getItem('access_token') ?? ''
    ws = new WebSocket(`${WS_BASE}/helpdesk/${chatId}/?token=${token}`)

    ws.onopen = () => {
      isConnected.value = true
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'chat_message') {
          callbacks.onMessage(data.message as HelpdeskMessage)
        } else if (data.type === 'status_change') {
          callbacks.onStatusChange(data.status as ChatStatus, data.chat_id as number)
        }
      } catch {  }
    }

    ws.onclose = (event) => {
      isConnected.value = false
      if (intentionallyClosed || event.code === 4001 || event.code === 4003) return
      if (currentChatId !== null) {
        reconnectTimer = setTimeout(() => _open(currentChatId!), 3000)
      }
    }

    ws.onerror = () => {
      ws?.close()
    }
  }

  return { isConnected, connect, disconnect }
}