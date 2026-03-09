<template>
  <div class="dash-root">

    <Sidebar />

    <main class="main">

      <header class="top-bar">
        <div class="top-bar-left">
          <h1 class="page-title">Events</h1>
          <span class="event-count">{{ store.events.length }} event{{ store.events.length !== 1 ? 's' : '' }}</span>
        </div>
        <button class="btn-create" @click="openCreate">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
          New event
        </button>
      </header>

      <div class="filters-bar">
        <div class="search-wrap">
          <svg class="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
          </svg>
          <input
            v-model="search"
            class="search-input"
            type="text"
            placeholder="Search events…"
            @input="onSearchInput"
          />
          <button v-if="search" class="search-clear" @click="search = ''; applyFilters()">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>

        <div class="filter-pills">
          <button class="pill" :class="{ 'pill--active': filters.upcoming }" @click="toggleFilter('upcoming')">
            Upcoming
          </button>
          <button class="pill" :class="{ 'pill--active': filters.attending }" @click="toggleFilter('attending')">
            Attending
          </button>
        </div>
      </div>

      <div v-if="store.loading" class="state-center">
        <div class="big-spinner" />
      </div>

      <div v-else-if="store.error" class="state-center">
        <p class="state-msg state-msg--error">{{ store.error }}</p>
        <button class="btn-ghost" @click="loadEvents">Retry</button>
      </div>

      <div v-else-if="store.events.length === 0" class="state-center">
        <div class="empty-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        </div>
        <p class="state-msg">No events found.</p>
        <button class="btn-ghost" @click="openCreate">Create the first one</button>
      </div>

      <div v-else class="events-grid">
        <EventCard
          v-for="event in store.events"
          :key="event.id"
          :event="event"
          @edit="openEdit"
          @delete="confirmDelete"
          @join="handleJoin"
          @leave="handleLeave"
        />
      </div>
    </main>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="modal.open" class="modal-backdrop" @click.self="closeModal">
          <div class="modal">
            <div class="modal-header">
              <h2>{{ modal.mode === 'create' ? 'New event' : 'Edit event' }}</h2>
              <button class="modal-close" @click="closeModal">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <form @submit.prevent="submitModal" novalidate>
              <div class="field" :class="{ 'field--error': modalErrors.title }">
                <label>Title</label>
                <input v-model="modalForm.title" type="text" placeholder="Event name" @input="delete modalErrors.title" />
                <span v-if="modalErrors.title" class="field-error">{{ modalErrors.title }}</span>
              </div>
              <div class="field" :class="{ 'field--error': modalErrors.occurrence }">
                <label>Date & time</label>
                <input v-model="modalForm.occurrence" type="datetime-local" @input="delete modalErrors.occurrence" />
                <span v-if="modalErrors.occurrence" class="field-error">{{ modalErrors.occurrence }}</span>
              </div>
              <div class="field">
                <label>Description <span class="label-optional">optional</span></label>
                <textarea v-model="modalForm.description" rows="3" placeholder="What's this event about?" />
              </div>
              <div v-if="modalErrors.general" class="alert alert--error">{{ modalErrors.general }}</div>
              <div class="modal-actions">
                <button type="button" class="btn-ghost" @click="closeModal">Cancel</button>
                <button type="submit" class="btn-primary" :disabled="modalLoading">
                  <span v-if="!modalLoading">{{ modal.mode === 'create' ? 'Create' : 'Save changes' }}</span>
                  <span v-else class="spinner" />
                </button>
              </div>
            </form>
          </div>
        </div>
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="modal">
        <div v-if="deleteTarget" class="modal-backdrop" @click.self="deleteTarget = null">
          <div class="modal modal--sm">
            <div class="modal-header">
              <h2>Delete event?</h2>
              <button class="modal-close" @click="deleteTarget = null">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>
            <p class="delete-msg">
              "<strong>{{ deleteTarget?.title }}</strong>" will be permanently removed. This cannot be undone.
            </p>
            <div class="modal-actions">
              <button class="btn-ghost" @click="deleteTarget = null">Cancel</button>
              <button class="btn-danger" :disabled="deleteLoading" @click="executeDelete">
                <span v-if="!deleteLoading">Delete</span>
                <span v-else class="spinner" />
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useEventsStore } from '@/features/event/store/event.store'
import type { Event, EventFilters } from '@/features/event/types/event.types'
import Sidebar from '@/features/sidebar/components/Sidebar.vue'
import EventCard from './EventCard.vue'
import './dashboard.css'

const store = useEventsStore()

const search  = ref('')
const filters = reactive<EventFilters>({ upcoming: false, attending: false })

let searchTimer: ReturnType<typeof setTimeout>

function onSearchInput() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(applyFilters, 350)
}

function toggleFilter(key: 'upcoming' | 'attending') {
  filters[key] = !filters[key]
  applyFilters()
}

function applyFilters() {
  store.fetchEvents({
    search:    search.value || undefined,
    upcoming:  filters.upcoming  || undefined,
    attending: filters.attending || undefined,
  })
}

function loadEvents() {
  store.fetchEvents()
}

onMounted(loadEvents)

const modal = reactive<{ open: boolean; mode: 'create' | 'edit'; eventId: number | null }>({
  open: false, mode: 'create', eventId: null,
})
const modalForm    = reactive({ title: '', occurrence: '', description: '' })
const modalErrors  = reactive<Record<string, string>>({})
const modalLoading = ref(false)

function openCreate() {
  modal.mode = 'create'; modal.eventId = null; modal.open = true
  modalForm.title = ''; modalForm.occurrence = ''; modalForm.description = ''
  Object.keys(modalErrors).forEach(k => delete (modalErrors as any)[k])
}

function openEdit(event: Event) {
  modal.mode = 'edit'; modal.eventId = event.id; modal.open = true
  modalForm.title       = event.title
  modalForm.occurrence  = event.occurrence.slice(0, 16)
  modalForm.description = event.description
  Object.keys(modalErrors).forEach(k => delete (modalErrors as any)[k])
}

function closeModal() { modal.open = false }

async function submitModal() {
  if (!modalForm.title.trim()) { modalErrors.title = 'Title is required.'; return }
  if (!modalForm.occurrence)   { modalErrors.occurrence = 'Date and time are required.'; return }

  const payload = {
    title:       modalForm.title.trim(),
    occurrence:  new Date(modalForm.occurrence).toISOString(),
    description: modalForm.description,
  }

  modalLoading.value = true
  try {
    if (modal.mode === 'create') await store.createEvent(payload)
    else                         await store.updateEvent(modal.eventId!, payload)
    closeModal()
  } catch (e: any) {
    modalErrors.general = e?.response?.data?.detail || 'Something went wrong.'
  } finally {
    modalLoading.value = false
  }
}

const deleteTarget  = ref<Event | null>(null)
const deleteLoading = ref(false)

function confirmDelete(event: Event) { deleteTarget.value = event }

async function executeDelete() {
  if (!deleteTarget.value) return
  deleteLoading.value = true
  try {
    await store.deleteEvent(deleteTarget.value.id)
    deleteTarget.value = null
  } catch {
  } finally {
    deleteLoading.value = false
  }
}

async function handleJoin(event: Event)  { try { await store.joinEvent(event.id)  } catch {} }
async function handleLeave(event: Event) { try { await store.leaveEvent(event.id) } catch {} }
</script>