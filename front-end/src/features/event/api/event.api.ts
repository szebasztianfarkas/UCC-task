import apiClient from '@/shared/api/client'
import type { AxiosResponse } from 'axios'
import type { Event, CreateEventPayload, UpdateEventPayload, EventFilters } from '../types/event.types'

export const eventsApi = {
  list: (filters: EventFilters = {}): Promise<AxiosResponse<Event[]>> => {
    const params: Record<string, string> = {}
    if (filters.search)   params.search   = filters.search
    if (filters.upcoming) params.upcoming  = 'true'
    if (filters.attending) params.attending = 'true'
    return apiClient.get('/events/', { params })
  },

  get: (id: number): Promise<AxiosResponse<Event>> =>
    apiClient.get(`/events/${id}/`),

  create: (payload: CreateEventPayload): Promise<AxiosResponse<Event>> =>
    apiClient.post('/events/', payload),

  update: (id: number, payload: UpdateEventPayload): Promise<AxiosResponse<Event>> =>
    apiClient.patch(`/events/${id}/`, payload),

  delete: (id: number): Promise<AxiosResponse<void>> =>
    apiClient.delete(`/events/${id}/`),

  join: (id: number): Promise<AxiosResponse<Event>> =>
    apiClient.post(`/events/${id}/join/`),

  leave: (id: number): Promise<AxiosResponse<Event>> =>
    apiClient.post(`/events/${id}/leave/`),
}