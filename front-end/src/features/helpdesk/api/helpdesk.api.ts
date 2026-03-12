import apiClient from '@/shared/api/client'
import type { AxiosResponse } from 'axios'
import type { HelpdeskChat, HelpdeskChatSummary, HelpdeskMessage, AgentHistoryPage } from '../types/helpdesk.types'

export const helpdeskApi = {
  listMyClosed: (): Promise<AxiosResponse<HelpdeskChatSummary[]>> => apiClient.get('/helpdesk/my/'),
  getActiveChat: (): Promise<AxiosResponse<HelpdeskChat>> => apiClient.get('/helpdesk/my/active/'),
  createChat: (): Promise<AxiosResponse<HelpdeskChat>> => apiClient.post('/helpdesk/my/'),
  getChat: (id: number): Promise<AxiosResponse<HelpdeskChat>> => apiClient.get(`/helpdesk/${id}/`),
  sendMessage: (id: number, text: string): Promise<AxiosResponse<HelpdeskMessage[]>> => apiClient.post(`/helpdesk/${id}/`, { text }),
  resolve: (id: number): Promise<AxiosResponse<HelpdeskChat>> => apiClient.post(`/helpdesk/${id}/resolve/`),
  requestAgent: (id: number): Promise<AxiosResponse<HelpdeskMessage[]>> => apiClient.post(`/helpdesk/${id}/request-agent/`),
  agentQueue: (): Promise<AxiosResponse<HelpdeskChatSummary[]>> => apiClient.get('/helpdesk/agent/queue/'),
  agentAssign: (id: number): Promise<AxiosResponse<HelpdeskChat>> => apiClient.post(`/helpdesk/agent/${id}/assign/`),
  agentResolve: (id: number): Promise<AxiosResponse<HelpdeskChat>> => apiClient.post(`/helpdesk/agent/${id}/resolve/`),
  agentHistory: (page = 1, search = ''): Promise<AxiosResponse<AgentHistoryPage>> => apiClient.get('/helpdesk/agent/history/', { params: { page, search: search || undefined } }),
  getUnreadCounts: (): Promise<AxiosResponse<Record<number, number>>> => apiClient.get('/helpdesk/unread-counts/'),
  markRead: (id: number): Promise<AxiosResponse<void>> => apiClient.post(`/helpdesk/${id}/read/`),
}