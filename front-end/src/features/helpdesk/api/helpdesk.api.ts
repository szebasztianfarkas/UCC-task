import apiClient from '@/shared/api/client'
import type { AxiosResponse } from 'axios'
import type { HelpdeskChat, HelpdeskChatSummary, HelpdeskMessage } from '../types/helpdesk.types'

export const helpdeskApi = {
  listMyClosed:   (): Promise<AxiosResponse<HelpdeskChatSummary[]>> => apiClient.get('/helpdesk/my/'),
  getActiveChat:  (): Promise<AxiosResponse<HelpdeskChat>>          => apiClient.get('/helpdesk/my/active/'),
  createChat:     (): Promise<AxiosResponse<HelpdeskChat>>          => apiClient.post('/helpdesk/my/'),
  getChat:        (id: number): Promise<AxiosResponse<HelpdeskChat>>=> apiClient.get(`/helpdesk/${id}/`),
  sendMessage:    (id: number, text: string): Promise<AxiosResponse<HelpdeskMessage[]>> => apiClient.post(`/helpdesk/${id}/`, { text }),
  resolve:        (id: number): Promise<AxiosResponse<HelpdeskChat>>=> apiClient.post(`/helpdesk/${id}/resolve/`),
  requestAgent:   (id: number): Promise<AxiosResponse<HelpdeskMessage[]>> => apiClient.post(`/helpdesk/${id}/request-agent/`),
  agentQueue:     (): Promise<AxiosResponse<HelpdeskChatSummary[]>> => apiClient.get('/helpdesk/agent/queue/'),
  agentAssign:    (id: number): Promise<AxiosResponse<HelpdeskChat>>=> apiClient.post(`/helpdesk/agent/${id}/assign/`),
  agentResolve:   (id: number): Promise<AxiosResponse<HelpdeskChat>>=> apiClient.post(`/helpdesk/agent/${id}/resolve/`),
}