<template>
  <div v-if="msg.role === 'system'" class="hd-system-notice">
    {{ msg.content }}
  </div>

  <div v-else-if="msg.role === 'user'" class="hd-bubble hd-bubble--user">
    <div class="hd-bubble-body">
      <p class="hd-bubble-text">{{ msg.content }}</p>
    </div>
    <span class="hd-bubble-time">{{ formatTime(msg.created_at) }}</span>
  </div>

  <div v-else-if="msg.role === 'bot'" class="hd-bubble hd-bubble--bot">
    <div class="hd-bubble-avatar hd-bubble-avatar--bot">
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <circle cx="12" cy="12" r="10" />
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
      </svg>
    </div>
    <div class="hd-bubble-col">
      <div class="hd-bubble-body">
        <template v-if="msg.content">
          <p class="hd-bubble-text">{{ msg.content }}</p>
        </template>
        <template v-else>
          <p class="hd-bubble-text hd-bubble-text--null">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            I don't have an answer for that yet.
          </p>
        </template>
      </div>
      <span class="hd-bubble-time">{{ formatTime(msg.created_at) }}</span>

      <div v-if="showResolution && !isHistory" class="hd-resolution">
        <span class="hd-resolution-label">Did this solve your issue?</span>
        <div class="hd-resolution-btns">
          <button class="hd-res-btn hd-res-btn--yes" :disabled="resolving" @click="$emit('resolve')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            Yes
          </button>
          <button class="hd-res-btn hd-res-btn--no" :disabled="resolving" @click="$emit('request-agent')">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            No — talk to an agent
          </button>
        </div>
      </div>
    </div>
  </div>

  <div v-else-if="msg.role === 'agent'" class="hd-bubble hd-bubble--agent">
    <div class="hd-bubble-avatar hd-bubble-avatar--agent">
      {{ (msg.sender?.username?.[0] || "A").toUpperCase() }}
    </div>
    <div class="hd-bubble-col">
      <span class="hd-agent-name">{{ msg.sender?.username ?? "Agent" }}</span>
      <div class="hd-bubble-body">
        <p class="hd-bubble-text">{{ msg.content }}</p>
      </div>
      <span class="hd-bubble-time">{{ formatTime(msg.created_at) }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HelpdeskMessage } from "../types/helpdesk.types";

defineProps<{
  msg: HelpdeskMessage;
  showResolution?: boolean;
  isHistory?: boolean;
  resolving?: boolean;
}>();
defineEmits<{ resolve: []; "request-agent": [] }>();

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
}
</script>
