import { defineStore } from 'pinia'
import { ref } from 'vue'
import { eventsApi } from '../api/event.api'
import type { Event, CreateEventPayload, UpdateEventPayload, EventFilters } from '../types/event.types'

export const useEventsStore = defineStore('events', () => {
  const events = ref<Event[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  function _replaceEvent(updated: Event) {
    const idx = events.value.findIndex(e => e.id === updated.id)
    if (idx !== -1) events.value[idx] = updated
  }

  async function fetchEvents(filters: EventFilters = {}) {
    loading.value = true
    error.value = null
    try {
      const res = await eventsApi.list(filters)
      events.value = res.data
    } catch (e: any) {
      error.value = e?.response?.data?.detail || 'Failed to load events.'
    } finally {
      loading.value = false
    }
  }

  async function createEvent(payload: CreateEventPayload): Promise<Event> {
    const res = await eventsApi.create(payload)
    events.value.unshift(res.data)
    return res.data
  }

  async function updateEvent(id: number, payload: UpdateEventPayload): Promise<Event> {
    const res = await eventsApi.update(id, payload)
    _replaceEvent(res.data)
    return res.data
  }

  async function deleteEvent(id: number) {
    await eventsApi.delete(id)
    events.value = events.value.filter(e => e.id !== id)
  }

  async function joinEvent(id: number) {
    const res = await eventsApi.join(id)
    _replaceEvent(res.data)
  }

  async function leaveEvent(id: number) {
    const res = await eventsApi.leave(id)
    _replaceEvent(res.data)
  }

  return {
    events, loading, error,
    fetchEvents, createEvent, updateEvent, deleteEvent, joinEvent, leaveEvent,
  }
})