import apiClient from '@/shared/api/client'

export const profileApi = {
  getMe: () =>
    apiClient.get('/users/me/'),

  updateBio: (bio: string) =>
    apiClient.patch('/users/me/', { bio }),

  changePassword: (old_password: string, new_password: string, totp_code?: string) =>
    apiClient.post('/users/me/change-password/', {
      old_password,
      new_password,
      ...(totp_code ? { totp_code } : {}),
    }),

  initiateEmailChange: (new_email: string) =>
    apiClient.post('/users/me/email/initiate/', { new_email }),

  confirmEmailWithTotp: (request_token: string, totp_code: string) =>
    apiClient.post('/users/me/email/confirm/', { request_token, totp_code }),

  confirmEmailWithToken: (email_token: string) =>
    apiClient.post('/users/me/email/confirm/', { email_token }),
}