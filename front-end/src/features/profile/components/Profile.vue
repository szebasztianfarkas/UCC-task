<template>
  <div class="profile-root">
    <AppSidebar />

    <main class="profile-main">
      <header class="profile-header">
        <div>
          <h1 class="profile-title">Profile</h1>
          <p class="profile-subtitle">Manage your account details</p>
        </div>
      </header>

      <div class="profile-body">

        <section class="card">
          <div class="card-head">
            <div class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>
            </div>
            <div>
              <h2 class="card-title">Profile info</h2>
              <p class="card-sub">Your public username and bio</p>
            </div>
          </div>

          <div class="card-body">
            <div class="field">
              <label>Username</label>
              <div class="input-readonly">
                {{ authStore.user?.username }}
                <span class="readonly-badge">Read only</span>
              </div>
            </div>

            <div class="field">
              <label>Bio <span class="label-opt">optional</span></label>
              <textarea
                v-model="bio.value"
                rows="3"
                placeholder="Tell others a little about yourself…"
                :disabled="bio.saving"
              />
              <span v-if="bio.error" class="field-error">{{ bio.error }}</span>
            </div>
          </div>

          <div class="card-actions">
            <transition name="fade">
              <span v-if="bio.saved" class="saved-hint">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                Saved
              </span>
            </transition>
            <button class="btn-primary" :disabled="bio.saving || !bioChanged" @click="saveBio">
              <span v-if="!bio.saving">Save bio</span>
              <span v-else class="spinner" />
            </button>
          </div>
        </section>

        <section class="card">
          <div class="card-head">
            <div class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
            </div>
            <div>
              <h2 class="card-title">Email address</h2>
              <p class="card-sub">Changes require verification</p>
            </div>
          </div>

          <div class="card-body">

            <template v-if="email.step === 'idle'">
              <div class="field">
                <label>Current email</label>
                <div class="input-readonly">{{ authStore.user?.email || '—' }}</div>
              </div>
              <div class="field" :class="{ 'field--error': email.error }">
                <label>New email address</label>
                <input
                  v-model="email.newEmail"
                  type="email"
                  autocomplete="email"
                  placeholder="you@example.com"
                  :disabled="email.saving"
                  @input="email.error = ''"
                />
                <span v-if="email.error" class="field-error">{{ email.error }}</span>
              </div>
              <div class="card-actions">
                <button class="btn-primary" :disabled="email.saving || !email.newEmail.trim()" @click="initiateEmail">
                  <span v-if="!email.saving">Request change</span>
                  <span v-else class="spinner" />
                </button>
              </div>
            </template>

            <template v-else-if="email.step === 'email-sent'">
              <div class="confirm-banner confirm-banner--success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/></svg>
                <div>
                  <strong>Check your inbox</strong><br/>
                  A confirmation link was sent to <strong>{{ email.newEmail }}</strong>.
                  Click it to apply the change. The link expires in 1 hour.
                </div>
              </div>
              <div class="card-actions">
                <button class="btn-ghost" @click="cancelEmail">Start over</button>
              </div>
            </template>

            <template v-else-if="email.step === 'done'">
              <div class="confirm-banner confirm-banner--success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                Your email has been updated to <strong>{{ email.newEmail }}</strong>.
              </div>
              <div class="card-actions">
                <button class="btn-ghost" @click="cancelEmail">Change again</button>
              </div>
            </template>

          </div>
        </section>

        <section class="card">
          <div class="card-head">
            <div class="card-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></svg>
            </div>
            <div>
              <h2 class="card-title">Password</h2>
              <p class="card-sub">Must be at least 8 characters</p>
            </div>
          </div>

          <div class="card-body">
            <div class="field" :class="{ 'field--error': pwd.errors.old }">
              <label>Current password</label>
              <div class="input-wrap">
                <input
                  v-model="pwd.old"
                  :type="pwd.showOld ? 'text' : 'password'"
                  placeholder="Enter current password"
                  :disabled="pwd.saving"
                  @input="pwd.errors.old = ''"
                />
                <button class="toggle-visibility" type="button" @click="pwd.showOld = !pwd.showOld">
                  <svg v-if="!pwd.showOld" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
              <span v-if="pwd.errors.old" class="field-error">{{ pwd.errors.old }}</span>
            </div>

            <div class="field" :class="{ 'field--error': pwd.errors.new }">
              <label>New password</label>
              <div class="input-wrap">
                <input
                  v-model="pwd.new"
                  :type="pwd.showNew ? 'text' : 'password'"
                  placeholder="At least 8 characters"
                  :disabled="pwd.saving"
                  @input="pwd.errors.new = ''"
                />
                <button class="toggle-visibility" type="button" @click="pwd.showNew = !pwd.showNew">
                  <svg v-if="!pwd.showNew" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                  <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
                </button>
              </div>
              <span v-if="pwd.errors.new" class="field-error">{{ pwd.errors.new }}</span>
            </div>

            <div class="field" :class="{ 'field--error': pwd.errors.confirm }">
              <label>Confirm new password</label>
              <input
                v-model="pwd.confirm"
                :type="pwd.showNew ? 'text' : 'password'"
                placeholder="Repeat new password"
                :disabled="pwd.saving"
                @input="pwd.errors.confirm = ''"
              />
              <span v-if="pwd.errors.confirm" class="field-error">{{ pwd.errors.confirm }}</span>
            </div>

            <template v-if="hasMfa">
              <div class="mfa-divider">
                <span>Then confirm with MFA</span>
              </div>
              <div class="field" :class="{ 'field--error': pwd.errors.totp }">
                <label>Authenticator code</label>
                <input
                  v-model="pwd.totpCode"
                  type="text"
                  inputmode="numeric"
                  maxlength="6"
                  placeholder="000000"
                  class="input-otp"
                  :disabled="pwd.saving"
                  @input="pwd.errors.totp = ''"
                />
                <span v-if="pwd.errors.totp" class="field-error">{{ pwd.errors.totp }}</span>
              </div>
            </template>

            <div v-if="pwd.new" class="strength-wrap">
              <div class="strength-bars">
                <span
                  v-for="i in 4" :key="i"
                  class="strength-bar"
                  :class="{ [`strength-bar--${strengthLabel}`]: i <= strengthScore }"
                />
              </div>
              <span class="strength-label" :class="`strength-text--${strengthLabel}`">{{ strengthLabel }}</span>
            </div>
          </div>

          <div class="card-actions">
            <transition name="fade">
              <span v-if="pwd.saved" class="saved-hint">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="20 6 9 17 4 12"/></svg>
                Password changed
              </span>
            </transition>
            <button class="btn-primary" :disabled="pwd.saving || !pwdReady" @click="savePassword">
              <span v-if="!pwd.saving">Change password</span>
              <span v-else class="spinner" />
            </button>
          </div>
        </section>

      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/features/auth/store/auth.store'
import AppSidebar from '@/features/sidebar/components/Sidebar.vue'
import { profileApi } from '../api/profile.api'
import './profile.css'

const authStore = useAuthStore()
const route     = useRoute()

onMounted(async () => {
  await authStore.fetchMe()

  const emailToken = route.query.email_token as string | undefined
  if (emailToken) {
    email.step = 'confirming-token'
    try {
      await profileApi.confirmEmailWithToken(emailToken)
      email.newEmail = ''
      email.step = 'done-token'
      await authStore.fetchMe()
    } catch (e: any) {
      email.step = 'idle'
      email.error = e?.response?.data?.detail || 'The confirmation link is invalid or has expired.'
    }
  }
})

const bio = reactive({
  value:  authStore.user?.bio ?? '',
  saving: false,
  saved:  false,
  error:  '',
})

computed(() => authStore.user?.bio).value
onMounted(() => { if (authStore.user) bio.value = authStore.user.bio })

const bioChanged = computed(() => bio.value !== (authStore.user?.bio ?? ''))

async function saveBio() {
  bio.saving = true
  bio.error  = ''
  try {
    const { data } = await profileApi.updateBio(bio.value)
    authStore.user = data
    bio.saved = true
    setTimeout(() => { bio.saved = false }, 2500)
  } catch (e: any) {
    bio.error = e?.response?.data?.detail || 'Failed to save bio.'
  } finally {
    bio.saving = false
  }
}

type EmailStep = 'idle' | 'email-sent' | 'done' | 'confirming-token' | 'done-token'

const email = reactive({
  step:         'idle' as EmailStep,
  newEmail:     '',
  totpCode:     '',
  requestToken: '',
  saving:       false,
  error:        '',
})

async function initiateEmail() {
  if (!email.newEmail.trim()) return
  email.saving = true
  email.error  = ''
  try {
    await profileApi.initiateEmailChange(email.newEmail.trim())
    email.step = 'email-sent'
  } catch (e: any) {
    email.error = e?.response?.data?.detail || 'Failed to initiate email change.'
  } finally {
    email.saving = false
  }
}

function cancelEmail() {
  email.step         = 'idle'
  email.newEmail     = ''
  email.requestToken = ''
  email.error        = ''
}

const hasMfa = computed(() => !!authStore.user?.has_mfa)

const pwd = reactive({
  old: '', new: '', confirm: '', totpCode: '',
  showOld: false, showNew: false,
  saving: false, saved: false,
  errors: { old: '', new: '', confirm: '', totp: '' },
})

const strengthScore = computed((): number => {
  const p = pwd.new
  if (!p) return 0
  let score = 0
  if (p.length >= 8)            score++
  if (/[A-Z]/.test(p))          score++
  if (/[0-9]/.test(p))          score++
  if (/[^A-Za-z0-9]/.test(p))   score++
  return score
})

const strengthLabel = computed((): string => {
  return ['', 'weak', 'fair', 'good', 'strong'][strengthScore.value] || ''
})

const pwdReady = computed(() =>
  pwd.old &&
  pwd.new.length >= 8 &&
  pwd.new === pwd.confirm &&
  (!hasMfa.value || pwd.totpCode.length === 6)
)

async function savePassword() {
  pwd.errors.old = pwd.errors.new = pwd.errors.confirm = pwd.errors.totp = ''

  if (!pwd.old)                { pwd.errors.old = 'Enter your current password.'; return }
  if (pwd.new.length < 8)      { pwd.errors.new = 'Must be at least 8 characters.'; return }
  if (pwd.new !== pwd.confirm) { pwd.errors.confirm = 'Passwords do not match.'; return }
  if (hasMfa.value && pwd.totpCode.length !== 6) {
    pwd.errors.totp = 'Enter the 6-digit code from your authenticator app.'
    return
  }

  pwd.saving = true
  try {
    await profileApi.changePassword(
      pwd.old,
      pwd.new,
      hasMfa.value ? pwd.totpCode : undefined,
    )
    pwd.old = pwd.new = pwd.confirm = pwd.totpCode = ''
    pwd.saved = true
    setTimeout(() => { pwd.saved = false }, 2500)
  } catch (e: any) {
    const msg = e?.response?.data?.detail || 'Failed to change password.'
    if (msg.toLowerCase().includes('authenticator') || msg.toLowerCase().includes('totp')) {
      pwd.errors.totp = msg
    } else if (msg.toLowerCase().includes('current')) {
      pwd.errors.old = msg
    } else {
      pwd.errors.new = msg
    }
  } finally {
    pwd.saving = false
  }
}
</script>