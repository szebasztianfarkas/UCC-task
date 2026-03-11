<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="open" class="modal-backdrop" @click.self="$emit('close')">
        <div class="modal" :class="size === 'sm' ? 'modal--sm' : ''">
          <div class="modal-header">
            <h2>{{ title }}</h2>
            <button class="btn-icon" :aria-label="'Close ' + title" @click="$emit('close')">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <slot />
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
defineProps<{
  open:   boolean
  title:  string
  size?:  'sm' | 'md'
}>()

defineEmits<{ close: [] }>()
</script>