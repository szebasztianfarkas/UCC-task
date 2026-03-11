<template>
  <div class="auth-root page-root">
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
              <p>Access is restricted to authorised personnel.</p>
            </div>
            <form @submit.prevent="submitLogin" novalidate>
              <div class="field" :class="{ 'field--error': errors.username }">
                <label for="username">Username</label>
                <input id="username" v-model="loginForm.username" type="text" autocomplete="username" spellcheck="false"
                  placeholder="username" @input="clearError('username')" />
                <span v-if="errors.username" class="field-error">{{
                  errors.username
                  }}</span>
              </div>
              <div class="field" :class="{ 'field--error': errors.password }">
                <label for="password">
                  Password
                  <button type="button" class="label-action" @click="view = 'reset-request'">
                    Forgot password?
                  </button>
                </label>
                <PasswordInput id="password" v-model="loginForm.password" autocomplete="current-password"
                  @input="clearError('password')" />
                <span v-if="errors.password" class="field-error">{{
                  errors.password
                  }}</span>
              </div>
              <div v-if="errors.general" class="alert alert--error">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                {{ errors.general }}
              </div>
              <button type="submit" class="btn-primary btn-primary--full" :disabled="loading">
                <span v-if="!loading">Continue</span><span v-else class="spinner" />
              </button>
            </form>
          </div>

          <div v-else-if="view === 'mfa'" key="mfa" class="pane">
            <div class="pane-header">
              <h1>Two-factor auth</h1>
              <p>Enter the 6-digit code from your authenticator app.</p>
            </div>
            <form @submit.prevent="submitMfa" novalidate>
              <OtpInput ref="otpRef" :has-error="!!errors.otp" :disabled="loading"
                @update:model-value="otpValue = $event" @complete="onOtpComplete" />
              <div v-if="errors.otp" class="alert alert--error">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                {{ errors.otp }}
              </div>
              <button type="submit" class="btn-primary btn-primary--full" :disabled="loading || otpValue.length < 6">
                <span v-if="!loading">Verify</span><span v-else class="spinner" />
              </button>
              <button type="button" class="btn-ghost" style="width: 100%; margin-top: 8px" @click="view = 'login'">
                ← Back to sign in
              </button>
            </form>
            <div class="mfa-help">
              <p>
                Lost access to your authenticator?
                <button type="button" class="link" @click="view = 'recovery'">
                  Use a recovery code
                </button>
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
                <input id="recovery-code" v-model="recoveryCode" type="text" autocomplete="off" spellcheck="false"
                  placeholder="XXXX-XXXX-XXXX" @input="clearError('recovery')" />
                <span v-if="errors.recovery" class="field-error">{{
                  errors.recovery
                  }}</span>
              </div>
              <button type="submit" class="btn-primary btn-primary--full" :disabled="loading || !recoveryCode">
                <span v-if="!loading">Verify</span><span v-else class="spinner" />
              </button>
              <button type="button" class="btn-ghost" style="width: 100%; margin-top: 8px" @click="view = 'mfa'">
                ← Back to MFA
              </button>
            </form>
          </div>

          <div v-else-if="view === 'reset-request'" key="reset-request" class="pane">
            <div class="pane-header">
              <h1>Reset password</h1>
              <p>
                Enter your email and we'll send reset instructions if an account
                exists.
              </p>
            </div>
            <form @submit.prevent="submitResetRequest" novalidate>
              <div class="field" :class="{ 'field--error': errors.resetEmail }">
                <label for="reset-email">Email address</label>
                <input id="reset-email" v-model="resetEmail" type="email" autocomplete="email"
                  placeholder="you@organisation.com" @input="clearError('resetEmail')" />
                <span v-if="errors.resetEmail" class="field-error">{{
                  errors.resetEmail
                  }}</span>
              </div>
              <button type="submit" class="btn-primary btn-primary--full" :disabled="loading || !resetEmail">
                <span v-if="!loading">Send instructions</span><span v-else class="spinner" />
              </button>
              <button type="button" class="btn-ghost" style="width: 100%; margin-top: 8px" @click="view = 'login'">
                ← Back to sign in
              </button>
            </form>
          </div>

          <div v-else-if="view === 'reset-sent'" key="reset-sent" class="pane pane--centered">
            <div class="success-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M22 2L11 13" />
                <path d="M22 2L15 22 11 13 2 9l20-7z" />
              </svg>
            </div>
            <div class="pane-header">
              <h1>Check your email</h1>
              <p>
                If <strong>{{ resetEmail }}</strong> is associated with an
                account, you'll receive instructions within a few minutes.
              </p>
            </div>
            <button type="button" class="btn-primary" @click="view = 'login'">
              Return to sign in
            </button>
          </div>

          <div v-else-if="view === 'reset-confirm'" key="reset-confirm" class="pane">
            <div class="pane-header">
              <h1>New password</h1>
              <p>Choose a strong password for your account.</p>
            </div>
            <div v-if="errors.resetToken" class="alert alert--error">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              {{ errors.resetToken }}
            </div>
            <form v-if="!errors.resetToken" @submit.prevent="submitResetConfirm" novalidate>
              <div class="field" :class="{ 'field--error': errors.newPassword }">
                <label for="new-password">New password</label>
                <PasswordInput id="new-password" v-model="newPassword" autocomplete="new-password"
                  @input="onNewPasswordInput" />
                <PasswordStrengthMeter ref="strengthRef" :password="newPassword" :show-requirements="true" />
                <span v-if="errors.newPassword" class="field-error">{{
                  errors.newPassword
                  }}</span>
              </div>
              <div class="field" :class="{ 'field--error': errors.confirmPassword }">
                <label for="confirm-password">Confirm password</label>
                <input id="confirm-password" v-model="confirmPassword" type="password" autocomplete="new-password"
                  placeholder="••••••••••••" @input="clearError('confirmPassword')" />
                <span v-if="errors.confirmPassword" class="field-error">{{
                  errors.confirmPassword
                  }}</span>
              </div>
              <button type="submit" class="btn-primary btn-primary--full" :disabled="loading || !canSubmitReset">
                <span v-if="!loading">Set new password</span><span v-else class="spinner" />
              </button>
            </form>
            <button v-if="errors.resetToken" type="button" class="btn-ghost" style="width: 100%"
              @click="view = 'reset-request'">
              Request a new link
            </button>
          </div>

          <div v-else-if="view === 'reset-complete'" key="reset-complete" class="pane pane--centered">
            <div class="success-icon">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <polyline points="20 6 9 17 4 12" />
              </svg>
            </div>
            <div class="pane-header">
              <h1>Password updated</h1>
              <p>
                Your password has been changed. You can now sign in with your
                new credentials.
              </p>
            </div>
            <button type="button" class="btn-primary" @click="view = 'login'">
              Sign in
            </button>
          </div>
        </Transition>
      </div>

      <div class="step-dots" aria-hidden="true">
        <span class="dot" :class="{
          'dot--active': [
            'login',
            'reset-request',
            'reset-sent',
            'reset-confirm',
            'reset-complete',
          ].includes(view),
        }" />
        <span class="dot" :class="{ 'dot--active': view === 'mfa' || view === 'recovery' }" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from "vue";
import { useRouter } from "vue-router";
import { useAuth } from "../composables/useAuth";
import { authApi } from "../api/auth.api";
import type { AuthView, AuthErrors } from "../types/auth.types";
import OtpInput from "@/shared/components/OtpInput.vue";
import PasswordInput from "@/shared/components/PasswordInput.vue";
import PasswordStrengthMeter from "@/shared/components/PasswordStrengthMeter.vue";
import "./auth.css";

const props = defineProps<{ resetToken?: string | null }>();
const { handleLogin, auth } = useAuth();
const router = useRouter();

const view = ref<AuthView>("login");
const loading = ref(false);
const errors = reactive<AuthErrors>({});

const loginForm = reactive({ username: "", password: "" });
const recoveryCode = ref("");
const resetEmail = ref("");
const newPassword = ref("");
const confirmPassword = ref("");
const otpValue = ref("");

const otpRef = ref<InstanceType<typeof OtpInput>>();
const strengthRef = ref<InstanceType<typeof PasswordStrengthMeter>>();

onMounted(() => {
  if (props.resetToken) view.value = "reset-confirm";
});

function clearError(key: keyof AuthErrors) {
  delete errors[key];
  delete errors.general;
}
function setError(key: keyof AuthErrors, msg: string) {
  errors[key] = msg;
}

const canSubmitReset = computed(
  () =>
    (strengthRef.value?.allMet ?? false) &&
    confirmPassword.value === newPassword.value,
);

function onNewPasswordInput() {
  clearError("newPassword");
  clearError("confirmPassword");
}

async function submitLogin() {
  if (!loginForm.username) return setError("username", "Username is required.");
  if (!loginForm.password) return setError("password", "Password is required.");
  loading.value = true;
  try {
    const result = await handleLogin({
      username: loginForm.username,
      password: loginForm.password,
    });
    if (result.mfa_required) view.value = "mfa";
  } catch (e: any) {
    const s = e?.response?.status;
    if (s === 401) setError("general", "Invalid username or password.");
    else if (s === 429)
      setError(
        "general",
        "Too many attempts. Please wait before trying again.",
      );
    else setError("general", "Something went wrong. Please try again.");
  } finally {
    loading.value = false;
  }
}

function onOtpComplete(val: string) {
  otpValue.value = val;
  submitMfa();
}

async function submitMfa() {
  if (otpValue.value.length < 6) return;
  loading.value = true;
  try {
    await auth.verifyMfa(otpValue.value);
    router.push({ name: "dashboard" });
  } catch {
    otpRef.value?.clear();
    otpValue.value = "";
    setError("otp", "Invalid code. Please try again.");
  } finally {
    loading.value = false;
  }
}

async function submitRecovery() {
  if (!recoveryCode.value)
    return setError("recovery", "Recovery code is required.");
  loading.value = true;
  try {
    await auth.verifyRecovery(recoveryCode.value);
    router.push({ name: "dashboard" });
  } catch {
    setError("recovery", "Invalid or already used recovery code.");
  } finally {
    loading.value = false;
  }
}

async function submitResetRequest() {
  if (!resetEmail.value)
    return setError("resetEmail", "Email address is required.");
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(resetEmail.value))
    return setError("resetEmail", "Please enter a valid email address.");
  loading.value = true;
  try {
    await authApi.requestPasswordReset(resetEmail.value);
  } catch {
  } finally {
    loading.value = false;
    view.value = "reset-sent";
  }
}

async function submitResetConfirm() {
  if (!strengthRef.value?.allMet)
    return setError("newPassword", "Please meet all password requirements.");
  if (newPassword.value !== confirmPassword.value)
    return setError("confirmPassword", "Passwords do not match.");
  if (!props.resetToken)
    return setError(
      "resetToken",
      "Reset token is missing. Please use the link from your email.",
    );
  loading.value = true;
  try {
    await authApi.confirmPasswordReset(props.resetToken, newPassword.value);
    view.value = "reset-complete";
    router.replace({ name: "login" });
  } catch (e: any) {
    setError(
      "resetToken",
      e?.response?.data?.detail || "This reset link is invalid or has expired.",
    );
  } finally {
    loading.value = false;
  }
}
</script>
