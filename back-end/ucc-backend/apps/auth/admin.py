from django.contrib import admin
from apps.auth.models import MFADevice, MFARecoveryCode, PasswordResetToken, PendingMFAToken

admin.site.register(MFADevice)
admin.site.register(MFARecoveryCode)
admin.site.register(PasswordResetToken)
admin.site.register(PendingMFAToken)