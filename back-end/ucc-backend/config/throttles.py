from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class LoginRateThrottle(AnonRateThrottle):
    """10 login attempts per minute per IP — limits credential stuffing."""
    scope = 'login'


class PasswordResetThrottle(AnonRateThrottle):
    """5 reset requests per minute per IP — limits email flooding."""
    scope = 'password_reset'


class MFAThrottle(AnonRateThrottle):
    """10 MFA attempts per minute per IP — limits TOTP brute-force."""
    scope = 'mfa'