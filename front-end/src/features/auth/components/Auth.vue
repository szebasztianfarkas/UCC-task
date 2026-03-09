<template>
  <div class="auth-root">
    <div class="grid-bg" aria-hidden="true">
      <div class="grid-lines" />
      <div class="orb orb-1" />
      <div class="orb orb-2" />
    </div>

    <div class="auth-shell">
      <div class="brand">
        <span class="brand-mark">⬡</span>
        <span class="brand-name">EVENTLY</span>
      </div>

      <div class="card" :class="`card--${view}`">

        <Transition name="slide" mode="out-in">
          <div v-if="view === 'login'" key="login" class="pane">
            <div class="pane-header">
              <h1>Sign in</h1>
            </div>

            <form @submit.prevent="submitLogin" novalidate>
              <div class="field" :class="{ 'field--error': errors.username }">
                <label for="username">Username</label>
                <input
                  id="username"
                  v-model="loginForm.username"
                  type="text"
                  autocomplete="username"
                  spellcheck="false"
                  placeholder="you@organisation.com"
                  @input="clearError('username')"
                />
                <span v-if="errors.username" class="field-error">{{ errors.username }}</span>
              </div>

              <div class="field" :class="{ 'field--error': errors.password }">
                <label for="password">
                  Password
                  <button type="button" class="label-action" @click="view = 'reset-request'">
                    Forgot password?
                  </button>
                </label>
                <div class="input-group">
                  <input
                    id="password"
                    v-model="loginForm.password"
                    :type="showPassword ? 'text' : 'password'"
                    autocomplete="current-password"
                    placeholder="••••••••••••"
                    @input="clearError('password')"
                  />
                  <button
                    type="button"
                    class="input-toggle"
                    :aria-label="showPassword ? 'Hide password' : 'Show password'"
                    @click="showPassword = !showPassword"
                  >
                    <svg v-if="!showPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/>
                      <circle cx="12" cy="12" r="3"/>
                    </svg>
                    <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                      <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                      <line x1="1" y1="1" x2="23" y2="23"/>
                    </svg>
                  </button>
                </div>
                <span v-if="errors.password" class="field-error">{{ errors.password }}</span>
              </div>

              <div v-if="errors.general" class="alert alert--error">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {{ errors.general }}
              </div>

              <button type="submit" class="btn-primary" :disabled="loading">
                <span v-if="!loading">Continue</span>
                <span v-else class="spinner" />
              </button>
            </form>
          </div>

          <div v-else-if="view === 'mfa'" key="mfa" class="pane">
            <div class="pane-header">
              <h1>Two-factor auth</h1>
              <p>Enter the 6-digit code from your authenticator app.</p>
            </div>

            <form @submit.prevent="submitMfa" novalidate>
              <div class="otp-row">
                <input
                  v-for="(_, i) in 6"
                  :key="i"
                  :ref="(el) => { otpRefs[i] = el as HTMLInputElement }"
                  v-model="otpDigits[i]"
                  class="otp-box"
                  type="text"
                  inputmode="numeric"
                  maxlength="1"
                  pattern="[0-9]"
                  :class="{ 'otp-box--error': errors.otp }"
                  @input="onOtpInput(i, $event as InputEvent)"
                  @keydown="onOtpKeydown(i, $event as KeyboardEvent)"
                  @paste.prevent="onOtpPaste($event as ClipboardEvent)"
                />
              </div>

              <div v-if="errors.otp" class="alert alert--error">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                {{ errors.otp }}
              </div>

              <button type="submit" class="btn-primary" :disabled="loading || otpValue.length < 6">
                <span v-if="!loading">Verify</span>
                <span v-else class="spinner" />
              </button>

              <button type="button" class="btn-ghost" @click="view = 'login'">
                ← Back to sign in
              </button>
            </form>

            <div class="mfa-help">
              <p>
                Lost access to your authenticator?
                <button type="button" class="link" @click="view = 'recovery'">Use a recovery code</button>
              </p>
            </div>
          </div>

          <div v-else-if="view === 'recovery'" key="recovery" class="pane">
            <div class="pane-header">
              <h1>Recovery code</h1>
              <p>Enter one of your saved recovery codes.</p>
            </div>

            <form @submit.prevent="submitRecovery" novalidate>
              <div class="field" :class="{ 'field--error': errors.recovery }">
                <label for="recovery-code">Recovery code</label>
                <input
                  id="recovery-code"
                  v-model="recoveryCode"
                  type="text"
                  autocomplete="off"
                  spellcheck="false"
                  placeholder="XXXX-XXXX-XXXX"
                  @input="clearError('recovery')"
                />
                <span v-if="errors.recovery" class="field-error">{{ errors.recovery }}</span>
              </div>

              <button type="submit" class="btn-primary" :disabled="loading || !recoveryCode">
                <span v-if="!loading">Verify</span>
                <span v-else class="spinner" />
              </button>

              <button type="button" class="btn-ghost" @click="view = 'mfa'">
                ← Back to MFA
              </button>
            </form>
          </div>

          <div v-else-if="view === 'reset-request'" key="reset-request" class="pane">
            <div class="pane-header">
              <h1>Reset password</h1>
              <p>Enter your email and we'll send reset instructions if an account exists.</p>
            </div>

            <form @submit.prevent="submitResetRequest" novalidate>
              <div class="field" :class="{ 'field--error': errors.resetEmail }">
                <label for="reset-email">Email address</label>
                <input
                  id="reset-email"
                  v-model="resetEmail"
                  type="email"
                  autocomplete="email"
                  placeholder="you@organisation.com"
                  @input="clearError('resetEmail')"
                />
                <span v-if="errors.resetEmail" class="field-error">{{ errors.resetEmail }}</span>
              </div>

              <button type="submit" class="btn-primary" :disabled="loading || !resetEmail">
                <span v-if="!loading">Send instructions</span>
                <span v-else class="spinner" />
              </button>

              <button type="button" class="btn-ghost" @click="view = 'login'">
                ← Back to sign in
              </button>
            </form>
          </div>

          <div v-else-if="view === 'reset-sent'" key="reset-sent" class="pane pane--centered">
            <div class="success-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 2L11 13"/>
                <path d="M22 2L15 22 11 13 2 9l20-7z"/>
              </svg>
            </div>
            <div class="pane-header">
              <h1>Check your email</h1>
              <p>
                If <strong>{{ resetEmail }}</strong> is associated with an account,
                you'll receive instructions within a few minutes.
              </p>
            </div>
            <button type="button" class="btn-primary" @click="view = 'login'">
              Return to sign in
            </button>
          </div>
          
        </Transition>
      </div>

      <div class="step-dots" aria-hidden="true">
        <span
          class="dot"
          :class="{ 'dot--active': view === 'login' || view === 'reset-request' || view === 'reset-sent' }"
        />
        <span
          class="dot"
          :class="{ 'dot--active': view === 'mfa' || view === 'recovery' }"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { authApi } from '../api/auth.api'
import type { AuthView, AuthErrors } from '../types/auth.types'
import './Auth.css'

const { handleLogin, auth } = useAuth()
const router = useRouter()

const view = ref<AuthView>('login')
const loading = ref<boolean>(false)
const showPassword = ref<boolean>(false)
const errors = reactive<AuthErrors>({})

const loginForm = reactive({ username: '', password: '' })
const otpDigits = reactive<string[]>(['', '', '', '', '', ''])
const otpRefs = ref<HTMLInputElement[]>([])
const recoveryCode = ref<string>('')
const resetEmail = ref<string>('')

const otpValue = computed<string>(() => otpDigits.join(''))

function clearError(key: keyof AuthErrors) {
  delete errors[key]
  delete errors.general
}

function setError(key: keyof AuthErrors, msg: string) {
  errors[key] = msg
}

async function submitLogin() {
  if (!loginForm.username) return setError('username', 'Username is required.')
  if (!loginForm.password) return setError('password', 'Password is required.')

  loading.value = true
  try {
    const result = await handleLogin({ username: loginForm.username, password: loginForm.password })
    if (result.mfa_required) {
      view.value = 'mfa'
    }
  } catch (e: any) {
    const status = e?.response?.status
    if (status === 401) setError('general', 'Invalid username or password.')
    else if (status === 429) setError('general', 'Too many attempts. Please wait before trying again.')
    else setError('general', 'Something went wrong. Please try again.')
  } finally {
    loading.value = false
  }
}

function onOtpInput(i: number, e: InputEvent) {
  const val = (e.target as HTMLInputElement).value.replace(/\D/g, '')
  otpDigits[i] = val.slice(-1)
  clearError('otp')
  if (val && i < 5) nextTick(() => otpRefs.value[i + 1]?.focus())
  if (otpValue.value.length === 6) submitMfa()
}

function onOtpKeydown(i: number, e: KeyboardEvent) {
  if (e.key === 'Backspace' && !otpDigits[i] && i > 0) {
    nextTick(() => otpRefs.value[i - 1]?.focus())
  }
  if (e.key === 'ArrowLeft' && i > 0) otpRefs.value[i - 1]?.focus()
  if (e.key === 'ArrowRight' && i < 5) otpRefs.value[i + 1]?.focus()
}

function onOtpPaste(e: ClipboardEvent) {
  const text = (e.clipboardData?.getData('text') || '').replace(/\D/g, '').slice(0, 6)
  text.split('').forEach((ch, i) => { otpDigits[i] = ch })
  nextTick(() => otpRefs.value[Math.min(text.length, 5)]?.focus())
  if (text.length === 6) submitMfa()
}

async function submitMfa() {
  if (otpValue.value.length < 6) return
  loading.value = true
  try {
    await auth.verifyMfa(otpValue.value)
    router.push({ name: 'dashboard' })
  } catch (e: any) {
    otpDigits.fill('')
    nextTick(() => otpRefs.value[0]?.focus())
    setError('otp', 'Invalid code. Please try again.')
  } finally {
    loading.value = false
  }
}

async function submitRecovery() {
  if (!recoveryCode.value) return setError('recovery', 'Recovery code is required.')
  loading.value = true
  try {
    await auth.verifyRecovery(recoveryCode.value)
    router.push({ name: 'dashboard' })
  } catch (e: any) {
    setError('recovery', 'Invalid or already used recovery code.')
  } finally {
    loading.value = false
  }
}

async function submitResetRequest() {
  if (!resetEmail.value) return setError('resetEmail', 'Email address is required.')
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(resetEmail.value)) {
    return setError('resetEmail', 'Please enter a valid email address.')
  }
  loading.value = true
  try {
    await authApi.requestPasswordReset(resetEmail.value)
  } catch {
  } finally {
    loading.value = false
    view.value = 'reset-sent'
  }
}
</script>