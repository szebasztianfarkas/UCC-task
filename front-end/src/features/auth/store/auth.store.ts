import { defineStore } from 'pinia'
import { ref, computed, onMounted } from 'vue'
import { authApi } from '../api/auth.api'
import type { AuthUser, LoginCredentials, MfaRequiredResponse, LoginApiResponse } from '../types/auth.types'

function isMfaRequired(data: LoginApiResponse): data is MfaRequiredResponse {
  return (data as MfaRequiredResponse).mfa_required === true
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<AuthUser | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'))
  const mfaToken = ref<string | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  async function login(credentials: LoginCredentials): Promise<{ mfa_required: boolean }> {
    const { data } = await authApi.login(credentials)

    if (isMfaRequired(data)) {
      mfaToken.value = data.mfa_token
      return { mfa_required: true }
    }

    _setTokens(data.access, data.refresh)
    user.value = data.user
    return { mfa_required: false }
  }

  async function verifyMfa(code: string): Promise<void> {
    if (!mfaToken.value) throw new Error('No MFA session in progress.')
    const { data } = await authApi.verifyMfa(code, mfaToken.value)
    mfaToken.value = null
    _setTokens(data.access, data.refresh)
    user.value = data.user
  }

  async function verifyRecovery(code: string): Promise<void> {
    if (!mfaToken.value) throw new Error('No MFA session in progress.')
    const { data } = await authApi.verifyRecovery(code, mfaToken.value)
    mfaToken.value = null
    _setTokens(data.access, data.refresh)
    user.value = data.user
  }

  async function fetchMe(): Promise<void> {
    const { data } = await authApi.me()
    user.value = data
  }

  async function logout(): Promise<void> {
    if (refreshToken.value) {
      await authApi.logout(refreshToken.value).catch(() => {})
    }
    _clearSession()
  }

  function _setTokens(access: string, refresh: string): void {
    token.value = access
    refreshToken.value = refresh
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
  }

  function _clearSession(): void {
    user.value = null
    token.value = null
    refreshToken.value = null
    mfaToken.value = null
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
  }

  return {
    user,
    token,
    isAuthenticated,
    login,
    verifyMfa,
    verifyRecovery,
    fetchMe,
    logout,
  }
})