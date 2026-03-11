export type MessageRole = 'user' | 'bot' | 'agent' | 'system'
export type ChatStatus = 'open' | 'waiting' | 'agent_open' | 'resolved' | 'locked'

export interface Sender {
  id: number
  username: string
}

export interface HelpdeskMessage {
  id: number
  role: MessageRole
  sender: Sender | null
  content: string | null
  created_at: string
}

export interface HelpdeskChatSummary {
  id: number
  status: ChatStatus
  user_username: string
  agent_username: string | null
  created_at: string
  updated_at: string
  last_message: { role: MessageRole; content: string } | null
}

export interface HelpdeskChat extends HelpdeskChatSummary {
  messages: HelpdeskMessage[]
}