<template>
  <div v-if="password" class="strength-meter">
    <div class="strength-bars">
      <span
        v-for="i in 4"
        :key="i"
        class="strength-bar"
        :class="{ [`strength-bar--${level}`]: i <= score }"
      />
    </div>
    <span class="strength-label" :class="`strength-label--${level}`">{{ label }}</span>
  </div>

  <ul v-if="password && showRequirements" class="requirements">
    <li
      v-for="req in requirements"
      :key="req.label"
      :class="{ 'req--met': req.met }"
    >
      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
        <polyline v-if="req.met" points="20 6 9 17 4 12"/>
        <line v-else x1="12" y1="5" x2="12" y2="19"/>
      </svg>
      {{ req.label }}
    </li>
  </ul>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  password:         string
  showRequirements?: boolean
}>(), {
  showRequirements: false,
})

interface Requirement { label: string; met: boolean }

const requirements = computed<Requirement[]>(() => [
  { label: 'At least 8 characters',        met: props.password.length >= 8 },
  { label: 'One uppercase letter (A–Z)',    met: /[A-Z]/.test(props.password) },
  { label: 'One lowercase letter (a–z)',    met: /[a-z]/.test(props.password) },
  { label: 'One number (0–9)',              met: /\d/.test(props.password) },
  { label: 'One special character (!@#…)',  met: /[^A-Za-z0-9]/.test(props.password) },
])

const score = computed(() => requirements.value.filter(r => r.met).length)

const level = computed(() => {
  if (score.value <= 1) return 'weak'
  if (score.value === 2) return 'fair'
  if (score.value === 3) return 'good'
  return 'strong'
})

const label = computed(() => ({ weak: 'Weak', fair: 'Fair', good: 'Good', strong: 'Strong' }[level.value]))

const allMet = computed(() => requirements.value.every(r => r.met))
defineExpose({ allMet, score, level })
</script>