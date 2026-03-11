<template>
  <div class="otp-row">
    <input
      v-for="(_, i) in 6"
      :key="i"
      :ref="(el) => { inputs[i] = el as HTMLInputElement }"
      :value="digits[i]"
      class="otp-box"
      type="text"
      inputmode="numeric"
      maxlength="1"
      pattern="[0-9]"
      autocomplete="off"
      :class="{ 'otp-box--error': hasError }"
      :disabled="disabled"
      @input="onInput(i, $event as InputEvent)"
      @keydown="onKeydown(i, $event as KeyboardEvent)"
      @paste.prevent="onPaste($event as ClipboardEvent)"
    />
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, nextTick } from 'vue'

const props = withDefaults(defineProps<{
  hasError?: boolean
  disabled?: boolean
}>(), {
  hasError: false,
  disabled: false,
})

const emit = defineEmits<{
  'update:modelValue': [value: string]
  complete:           [value: string]
}>()

const digits = reactive<string[]>(['', '', '', '', '', ''])
const inputs = ref<HTMLInputElement[]>([])

const value = () => digits.join('')

function onInput(i: number, e: InputEvent) {
  const raw = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  digits[i] = raw.slice(-1)
  emit('update:modelValue', value())
  if (raw && i < 5) nextTick(() => inputs.value[i + 1]?.focus())
  if (value().length === 6) emit('complete', value())
}

function onKeydown(i: number, e: KeyboardEvent) {
  if (e.key === 'Backspace' && !digits[i] && i > 0) nextTick(() => inputs.value[i - 1]?.focus())
  if (e.key === 'ArrowLeft'  && i > 0) inputs.value[i - 1]?.focus()
  if (e.key === 'ArrowRight' && i < 5) inputs.value[i + 1]?.focus()
}

function onPaste(e: ClipboardEvent) {
  const text = (e.clipboardData?.getData('text') || '').replace(/\D/g, '').slice(0, 6)
  text.split('').forEach((ch, i) => { digits[i] = ch })
  emit('update:modelValue', value())
  nextTick(() => inputs.value[Math.min(text.length, 5)]?.focus())
  if (text.length === 6) emit('complete', text)
}

function clear() {
  digits.fill('')
  emit('update:modelValue', '')
  nextTick(() => inputs.value[0]?.focus())
}

defineExpose({ clear })
</script>