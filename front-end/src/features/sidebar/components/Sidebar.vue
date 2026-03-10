<template>
  <aside class="sidebar">

    <div class="sidebar-brand">
      <span class="brand-mark">⬡</span>
      <span class="brand-name">EVENTLY</span>
    </div>

    <nav class="sidebar-nav">
      <RouterLink
        class="nav-item"
        :class="{ 'nav-item--active': route.name === 'dashboard' }"
        to="/dashboard"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <rect x="3" y="4" width="18" height="18" rx="2"/>
          <line x1="16" y1="2" x2="16" y2="6"/>
          <line x1="8" y1="2" x2="8" y2="6"/>
          <line x1="3" y1="10" x2="21" y2="10"/>
        </svg>
        Events
      </RouterLink>

      <RouterLink
        class="nav-item"
        :class="{ 'nav-item--active': route.name === 'helpdesk' && !route.query.id }"
        to="/helpdesk"
        @click="handleHelpdeskClick"
      >
        <span class="nav-item-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <circle cx="12" cy="12" r="10"/>
            <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
            <line x1="12" y1="17" x2="12.01" y2="17"/>
          </svg>
          <span v-if="helpdeskHasUnread" class="nav-red-dot" />
        </span>
        Helpdesk
      </RouterLink>

      <template v-if="helpdeskStore.history.length">
        <div class="nav-section-label">Recent chats</div>
        <RouterLink
          v-for="c in helpdeskStore.history"
          :key="c.id"
          class="nav-item nav-item--history"
          :class="{ 'nav-item--active': route.query.id === String(c.id) }"
          :to="{ name: 'helpdesk', query: { id: c.id } }"
        >
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
          </svg>
          <span class="nav-history-label">
            <span class="nav-history-id">#{{ c.id }}</span>
            <span class="nav-history-preview">{{ c.last_message?.content ?? 'No messages' }}</span>
          </span>
          <span class="nav-history-status" :class="`nav-history-status--${c.status}`" />
        </RouterLink>
      </template>

      <RouterLink
        v-if="isAgent"
        class="nav-item"
        :class="{ 'nav-item--active': route.name === 'helpdesk-agent' }"
        to="/helpdesk/agent"
        @click="handleAgentClick"
      >
        <span class="nav-item-icon-wrap">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
            <circle cx="9" cy="7" r="4"/>
            <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
            <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
          </svg>
          <span v-if="helpdeskStore.agentQueueHasUnread" class="nav-red-dot" />
        </span>
        Agent panel
      </RouterLink>
    </nav>

    <div class="sidebar-footer">
      <RouterLink class="user-chip" to="/profile" title="Edit profile">
        <div class="user-initial">{{ userInitial }}</div>
        <div class="user-info">
          <span class="user-name">{{ auth.user?.username }}</span>
          <span class="user-role">{{ isAgent ? 'Agent' : 'Member' }}</span>
        </div>
        <svg class="user-edit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
          <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
        </svg>
      </RouterLink>

      <button class="logout-btn" @click="handleLogout" title="Sign out">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        <span>Sign out</span>
      </button>
    </div>

  </aside>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuth } from '@/features/auth/composables/useAuth'
import { useHelpdeskStore } from '@/features/helpdesk/store/helpdesk.store'
import './sidebar.css'

const { auth, handleLogout } = useAuth()
const route         = useRoute()
const helpdeskStore = useHelpdeskStore()

const userInitial = computed(() =>
  (auth.user?.username?.[0] || '?').toUpperCase()
)

const isAgent = computed(() => !!(auth.user as any)?.is_helpdesk_agent)

const helpdeskHasUnread = computed(() => {
  if (!helpdeskStore.chat) return false
  return (helpdeskStore.unreadByChat[helpdeskStore.chat.id] ?? 0) > 0
})

function handleHelpdeskClick() {
  if (helpdeskStore.chat) {
    helpdeskStore.clearUnread(helpdeskStore.chat.id)
  }
}

function handleAgentClick() {
  helpdeskStore.agentQueueHasUnread = false
}

onMounted(async () => {
  await helpdeskStore.loadHistory()
})
</script>