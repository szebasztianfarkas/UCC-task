"""
Management command to set up or reset MFA for a user.

Usage:
  python manage.py setup_mfa <username>
  python manage.py setup_mfa <username> --reset      # removes existing device first
  python manage.py setup_mfa <username> --codes 12   # generate 12 recovery codes (default: 8)
"""
import secrets
import pyotp

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model

from apps.auth.models import MFADevice, MFARecoveryCode

User = get_user_model()

DEFAULT_RECOVERY_CODES = 8


class Command(BaseCommand):
    help = 'Set up MFA (TOTP) for a user and generate recovery codes.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='Username to enable MFA for')
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Remove any existing MFA device before setting up a new one',
        )
        parser.add_argument(
            '--codes',
            type=int,
            default=DEFAULT_RECOVERY_CODES,
            metavar='N',
            help=f'Number of recovery codes to generate (default: {DEFAULT_RECOVERY_CODES})',
        )

    def handle(self, *args, **options):
        username = options['username']
        do_reset = options['reset']
        num_codes = options['codes']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f'User "{username}" does not exist.')

        if not user.is_active:
            raise CommandError(f'User "{username}" is inactive.')

        existing = MFADevice.objects.filter(user=user).first()

        if existing and not do_reset:
            raise CommandError(
                f'User "{username}" already has an MFA device. '
                f'Run with --reset to replace it.'
            )

        if existing and do_reset:
            existing.delete()
            self.stdout.write(self.style.WARNING(f'  Removed existing MFA device for "{username}".'))

        secret = pyotp.random_base32()
        device = MFADevice.objects.create(user=user, secret=secret, is_active=True)

        codes = []
        for _ in range(num_codes):
            code = secrets.token_hex(6).upper()
            MFARecoveryCode.objects.create(device=device, code=code)
            codes.append(code)

        totp = pyotp.TOTP(secret)
        otp_uri = totp.provisioning_uri(
            name=user.email or username,
            issuer_name='Evently',
        )

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'✓ MFA enabled for "{username}"'))
        self.stdout.write('')

        self.stdout.write(self.style.HTTP_INFO('  ── Authenticator setup ─────────────────────────'))
        self.stdout.write(f'  Secret (enter manually): {self.style.SUCCESS(secret)}')
        self.stdout.write('')
        self.stdout.write(f'  OTP URI (paste into a QR code generator to scan):')
        self.stdout.write(f'  {otp_uri}')
        self.stdout.write('')

        self.stdout.write(self.style.HTTP_INFO('  ── Recovery codes ──────────────────────────────'))
        self.stdout.write(self.style.WARNING('  Store these somewhere safe — each can only be used once.'))
        self.stdout.write('')
        for code in codes:
            self.stdout.write(f'    {code}')
        self.stdout.write('')