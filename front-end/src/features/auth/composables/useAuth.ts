import { useAuthStore } from '../store/auth.store'
import { useRouter } from 'vue-router'
import type { LoginCredentials } from '../types/auth.types'

export function useAuth() {
  const auth = useAuthStore()
  const router = useRouter()

  async function handleLogin(credentials: LoginCredentials): Promise<{ mfa_required: boolean }> {
    const result = await auth.login(credentials)

    if (!result.mfa_required) {
      await router.push({ name: 'dashboard' })
    }
    return result
  }

  async function handleLogout(): Promise<void> {
    await auth.logout()
    await router.push({ name: 'login' })
  }

  return { auth, handleLogin, handleLogout }
}