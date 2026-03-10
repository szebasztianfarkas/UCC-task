<template>
  <article class="event-card" :class="{ 'event-card--past': isPast }">

    <div class="card-top">
      <div class="date-badge">
        <span class="date-day">{{ day }}</span>
        <span class="date-month">{{ month }}</span>
      </div>

      <div v-if="event.is_owner" class="card-actions">
        <button class="action-btn" title="Edit event" @click="$emit('edit', event)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
        </button>
        <button class="action-btn action-btn--danger" title="Delete event" @click="$emit('delete', event)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
        </button>
      </div>
    </div>

    <h3 class="card-title">{{ event.title }}</h3>
    <p v-if="event.description" class="card-desc">{{ event.description }}</p>

    <div class="card-meta">
      <span class="meta-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
        {{ time }}
      </span>
      <span class="meta-item">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
        {{ event.created_by.username }}
      </span>
    </div>

    <div class="card-footer">
      <div class="attendees">
        <div
          v-for="(a, i) in visibleAttendees"
          :key="a.id"
          class="attendee-bubble"
          :style="{ zIndex: visibleAttendees.length - i }"
          :title="a.username"
        >{{ a.username[0].toUpperCase() }}</div>
        <span v-if="overflowCount > 0" class="attendee-overflow">+{{ overflowCount }}</span>
        <span class="attendee-label">
          {{ event.attendee_count === 0 ? 'No attendees yet' : `${event.attendee_count} attending` }}
        </span>
      </div>

      <template v-if="!event.is_owner">
        <button v-if="!event.is_attending" class="btn-join" :disabled="isPast" @click="$emit('join', event)">
          Join
        </button>
        <button v-else class="btn-leave" @click="$emit('leave', event)">Leave</button>
      </template>

      <span v-if="event.is_owner" class="owner-badge">Your event</span>
    </div>

  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { Event } from '@/features/event/types/event.types'
import './eventcard.css'

const props = defineProps<{ event: Event }>()
defineEmits<{
  edit:   [event: Event]
  delete: [event: Event]
  join:   [event: Event]
  leave:  [event: Event]
}>()

const date  = computed(() => new Date(props.event.occurrence))
const day   = computed(() => date.value.getDate())
const month = computed(() => date.value.toLocaleString('default', { month: 'short' }).toUpperCase())
const time  = computed(() => date.value.toLocaleString('default', {
  hour: 'numeric', minute: '2-digit', hour12: true, weekday: 'short',
}))
const isPast = computed(() => date.value < new Date())

const MAX_BUBBLES      = 4
const visibleAttendees = computed(() => props.event.attendees.slice(0, MAX_BUBBLES))
const overflowCount    = computed(() => Math.max(0, props.event.attendee_count - MAX_BUBBLES))
</script>