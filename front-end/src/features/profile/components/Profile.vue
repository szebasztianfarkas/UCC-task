<template>
  <div class="page-root">
    <AppSidebar />

    <main class="page-main">
      <header class="page-topbar">
        <div>
          <h1 class="page-title">Profile</h1>
          <p class="page-subtitle">Manage your account details</p>
        </div>
      </header>

      <div class="profile-body">
        <section class="card-surface">
          <div class="card-head">
            <div class="icon-box icon-box--md">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                <circle cx="12" cy="7" r="4" />
              </svg>
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
              <textarea v-model="bio.value" rows="3" placeholder="Tell others a little about yourself…"
                :disabled="bio.saving" />
              <span v-if="bio.error" class="field-error">{{ bio.error }}</span>
            </div>
          </div>
          <div class="card-actions">
            <Transition name="fade">
              <span v-if="bio.saved" class="saved-hint">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Saved
              </span>
            </Transition>
            <button class="btn-primary" :disabled="bio.saving || !bioChanged" @click="saveBio">
              <span v-if="!bio.saving">Save bio</span><span v-else class="spinner" />
            </button>
          </div>
        </section>

        <section class="card-surface">
          <div class="card-head">
            <div class="icon-box icon-box--md">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </svg>
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
                <div class="input-readonly">
                  {{ authStore.user?.email || "—" }}
                </div>
              </div>
              <div class="field" :class="{ 'field--error': email.error }">
                <label>New email address</label>
                <input v-model="email.newEmail" type="email" placeholder="you@example.com" :disabled="email.saving"
                  @input="email.error = ''" />
                <span v-if="email.error" class="field-error">{{
                  email.error
                  }}</span>
              </div>
              <div class="card-actions">
                <button class="btn-primary" :disabled="email.saving || !email.newEmail.trim()" @click="initiateEmail">
                  <span v-if="!email.saving">Request change</span><span v-else class="spinner" />
                </button>
              </div>
            </template>

            <template v-else-if="email.step === 'email-sent'">
              <div class="alert alert--success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                  <polyline points="22,6 12,13 2,6" />
                </svg>
                <div>
                  <strong>Check your inbox</strong><br />
                  A confirmation link was sent to
                  <strong>{{ email.newEmail }}</strong>. Click it to apply the change. The link expires in 1 hour.
                </div>
              </div>
              <div class="card-actions">
                <button class="btn-ghost" @click="cancelEmail">
                  Start over
                </button>
              </div>
            </template>

            <template v-else-if="email.step === 'done'">
              <div class="alert alert--success">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Your email has been updated to
                <strong>{{ email.newEmail }}</strong>.
              </div>
              <div class="card-actions">
                <button class="btn-ghost" @click="cancelEmail">
                  Change again
                </button>
              </div>
            </template>
          </div>
        </section>

        <section class="card-surface">
          <div class="card-head">
            <div class="icon-box icon-box--md">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
            </div>
            <div>
              <h2 class="card-title">Password</h2>
              <p class="card-sub">Must be at least 8 characters</p>
            </div>
          </div>
          <div class="card-body">
            <div class="field" :class="{ 'field--error': pwd.errors.old }">
              <label>Current password</label>
              <PasswordInput v-model="pwd.old" placeholder="Enter current password" :disabled="pwd.saving"
                @input="pwd.errors.old = ''" />
              <span v-if="pwd.errors.old" class="field-error">{{
                pwd.errors.old
                }}</span>
            </div>

            <div class="field" :class="{ 'field--error': pwd.errors.new }">
              <label>New password</label>
              <PasswordInput v-model="pwd.new" placeholder="At least 8 characters" autocomplete="new-password"
                :disabled="pwd.saving" @input="pwd.errors.new = ''" />
              <PasswordStrengthMeter :password="pwd.new" />
              <span v-if="pwd.errors.new" class="field-error">{{
                pwd.errors.new
                }}</span>
            </div>

            <div class="field" :class="{ 'field--error': pwd.errors.confirm }">
              <label>Confirm new password</label>
              <input v-model="pwd.confirm" type="password" placeholder="Repeat new password" :disabled="pwd.saving"
                @input="pwd.errors.confirm = ''" />
              <span v-if="pwd.errors.confirm" class="field-error">{{
                pwd.errors.confirm
                }}</span>
            </div>

            <template v-if="hasMfa">
              <div class="mfa-divider"><span>Then confirm with MFA</span></div>
              <OtpInput ref="otpRef" :has-error="!!pwd.errors.totp" :disabled="pwd.saving"
                @update:model-value="pwd.totpCode = $event" />
              <div v-if="pwd.errors.totp" class="alert alert--error">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
                {{ pwd.errors.totp }}
              </div>
            </template>
          </div>
          <div class="card-actions">
            <Transition name="fade">
              <span v-if="pwd.saved" class="saved-hint">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
                Password changed
              </span>
            </Transition>
            <button class="btn-primary" :disabled="pwd.saving" @click="savePassword">
              <span v-if="!pwd.saving">Change password</span><span v-else class="spinner" />
            </button>
          </div>
        </section>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";
import { useAuthStore } from "@/features/auth/store/auth.store";
import AppSidebar from "@/features/sidebar/components/Sidebar.vue";
import PasswordInput from "@/shared/components/PasswordInput.vue";
import PasswordStrengthMeter from "@/shared/components/PasswordStrengthMeter.vue";
import { profileApi } from "../api/profile.api";
import OtpInput from "@/shared/components/OtpInput.vue";
import "./profile.css";

const authStore = useAuthStore();
const route = useRoute();
const otpRef = ref<InstanceType<typeof OtpInput>>();

onMounted(async () => {
  await authStore.fetchMe();
  const emailToken = route.query.email_token as string | undefined;
  if (emailToken) {
    email.step = "confirming-token";
    try {
      await profileApi.confirmEmailWithToken(emailToken);
      email.newEmail = "";
      email.step = "done-token";
      await authStore.fetchMe();
    } catch (e: any) {
      email.step = "idle";
      email.error =
        e?.response?.data?.detail ||
        "The confirmation link is invalid or has expired.";
    }
  }
});

const bio = reactive({
  value: authStore.user?.bio ?? "",
  saving: false,
  saved: false,
  error: "",
});
onMounted(() => {
  if (authStore.user) bio.value = authStore.user.bio;
});
const bioChanged = computed(() => bio.value !== (authStore.user?.bio ?? ""));

async function saveBio() {
  bio.saving = true;
  bio.error = "";
  try {
    const { data } = await profileApi.updateBio(bio.value);
    authStore.user = data;
    bio.saved = true;
    setTimeout(() => {
      bio.saved = false;
    }, 2500);
  } catch (e: any) {
    bio.error = e?.response?.data?.detail || "Failed to save bio.";
  } finally {
    bio.saving = false;
  }
}

type EmailStep =
  | "idle"
  | "email-sent"
  | "done"
  | "confirming-token"
  | "done-token";
const email = reactive({
  step: "idle" as EmailStep,
  newEmail: "",
  requestToken: "",
  saving: false,
  error: "",
});

async function initiateEmail() {
  if (!email.newEmail.trim()) return;
  email.saving = true;
  email.error = "";
  try {
    await profileApi.initiateEmailChange(email.newEmail.trim());
    email.step = "email-sent";
  } catch (e: any) {
    email.error =
      e?.response?.data?.detail || "Failed to initiate email change.";
  } finally {
    email.saving = false;
  }
}

function cancelEmail() {
  Object.assign(email, {
    step: "idle",
    newEmail: "",
    totpCode: "",
    requestToken: "",
    error: "",
  });
}

const hasMfa = computed(() => !!authStore.user?.has_mfa);
const pwd = reactive({
  old: "",
  new: "",
  confirm: "",
  totpCode: "",
  saving: false,
  saved: false,
  errors: { old: "", new: "", confirm: "", totp: "" },
});

async function savePassword() {
  Object.assign(pwd.errors, { old: "", new: "", confirm: "", totp: "" });
  if (!pwd.old) {
    pwd.errors.old = "Enter your current password.";
    return;
  }
  if (pwd.new.length < 8) {
    pwd.errors.new = "Must be at least 8 characters.";
    return;
  }
  if (pwd.new !== pwd.confirm) {
    pwd.errors.confirm = "Passwords do not match.";
    return;
  }
  if (hasMfa.value && pwd.totpCode.length !== 6) {
    pwd.errors.totp = "Enter the 6-digit code from your authenticator app.";
    return;
  }
  pwd.saving = true;
  try {
    await profileApi.changePassword(
      pwd.old,
      pwd.new,
      hasMfa.value ? pwd.totpCode : undefined,
    );
    pwd.old = pwd.new = pwd.confirm = pwd.totpCode = "";
    otpRef.value?.clear();
    pwd.saved = true;
    setTimeout(() => {
      pwd.saved = false;
    }, 2500);
  } catch (e: any) {
    const msg = e?.response?.data?.detail || "Failed to change password.";
    if (
      msg.toLowerCase().includes("authenticator") ||
      msg.toLowerCase().includes("totp")
    )
      pwd.errors.totp = msg;
    else if (msg.toLowerCase().includes("current")) pwd.errors.old = msg;
    else pwd.errors.new = msg;
  } finally {
    pwd.saving = false;
  }
}
</script>
