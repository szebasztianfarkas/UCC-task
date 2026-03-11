<template>
  <span class="ws-pill" :class="connected ? 'ws-pill--on' : 'ws-pill--off'" :title="connected ? 'Live' : 'Disconnected'">
    <span class="ws-dot" />
    <slot>{{ connected ? 'Live' : 'Off' }}</slot>
  </span>
</template>

<script setup lang="ts">
defineProps<{ connected: boolean }>()
</script>