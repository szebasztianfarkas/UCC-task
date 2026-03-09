import apiClient from '@/shared/api/client'
import type {
  LoginCredentials,
  LoginApiResponse,
  MfaVerifyResponse,
  AuthUser,
} from '../types/auth.types'
import type { AxiosResponse } from 'axios'

export const authApi = {
  login: (credentials: LoginCredentials): Promise<AxiosResponse<LoginApiResponse>> =>
    apiClient.post('/auth/login/', credentials),

  verifyMfa: (code: string, mfaToken: string): Promise<AxiosResponse<MfaVerifyResponse>> =>
    apiClient.post('/auth/mfa/verify/', { code, mfa_token: mfaToken }),

  verifyRecovery: (recoveryCode: string, mfaToken: string): Promise<AxiosResponse<MfaVerifyResponse>> =>
    apiClient.post('/auth/mfa/recovery/', { code: recoveryCode, mfa_token: mfaToken }),

  refresh: (refreshToken: string): Promise<AxiosResponse<{ access: string }>> =>
    apiClient.post('/auth/token/refresh/', { refresh: refreshToken }),

  logout: (refreshToken: string): Promise<AxiosResponse<void>> =>
    apiClient.post('/auth/logout/', { refresh: refreshToken }),

  requestPasswordReset: (email: string): Promise<AxiosResponse<void>> =>
    apiClient.post('/auth/password/reset/', { email }),

  confirmPasswordReset: (token: string, newPassword: string): Promise<AxiosResponse<void>> =>
    apiClient.post('/auth/password/reset/confirm/', { token, new_password: newPassword }),

  me: (): Promise<AxiosResponse<AuthUser>> =>
    apiClient.get('/auth/me/'),
}