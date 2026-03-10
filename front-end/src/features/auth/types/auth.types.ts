export type AuthView = 'login' | 'mfa' | 'recovery' | 'reset-request' | 'reset-sent' | 'reset-confirm' | 'reset-complete'

export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthUser {
  id: number
  username: string
  email: string
  bio: string
  has_mfa: boolean
  is_helpdesk_agent: boolean
}

export interface LoginResponse {
  access: string
  refresh: string
  user: AuthUser
}

export interface MfaRequiredResponse {
  mfa_required: true
  mfa_token: string
}

export interface MfaVerifyResponse {
  access: string
  refresh: string
  user: AuthUser
}

export type LoginApiResponse = LoginResponse | MfaRequiredResponse

export interface AuthErrors {
  username?: string
  password?: string
  otp?: string
  recovery?: string
  resetEmail?: string
  newPassword?: string
  confirmPassword?: string
  resetToken?: string
  general?: string
}