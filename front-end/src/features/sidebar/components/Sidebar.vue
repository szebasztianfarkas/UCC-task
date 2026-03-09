<template>
  <aside class="sidebar">

    <div class="sidebar-brand">
      <span class="brand-mark">⬡</span>
      <span class="brand-name">EVENTLY</span>
    </div>

    <nav class="sidebar-nav">
      <RouterLink class="nav-item" :class="{ 'nav-item--active': route.name === 'dashboard' }" to="/dashboard">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="4" width="18" height="18" rx="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
        Events
      </RouterLink>

      <button class="nav-item" disabled title="Coming soon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        Helpdesk
        <span class="nav-badge">Soon</span>
      </button>
    </nav>

    <div class="sidebar-footer">
      <RouterLink class="user-chip" to="/profile" title="Edit profile">
        <div class="user-initial">{{ userInitial }}</div>
        <div class="user-info">
          <span class="user-name">{{ auth.user?.username }}</span>
          <span class="user-role">Member</span>
        </div>
        <svg class="user-edit-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
      </RouterLink>

      <button class="logout-btn" @click="handleLogout" title="Sign out">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        <span>Sign out</span>
      </button>
    </div>

  </aside>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { useAuth } from '@/features/auth/composables/useAuth'
import './sidebar.css'

const { auth, handleLogout } = useAuth()
const route = useRoute()

const userInitial = computed(() =>
  (auth.user?.username?.[0] || '?').toUpperCase()
)
</script>