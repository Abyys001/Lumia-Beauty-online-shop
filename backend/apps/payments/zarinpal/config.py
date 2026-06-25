import os

from django.conf import settings as django_settings

from apps.accounts.utils.encryption import decrypt_value, encrypt_value

from ..models import ZarinpalSettings


class ZarinpalConfigService:
    @staticmethod
    def get_settings() -> ZarinpalSettings:
        return ZarinpalSettings.get_settings()

    @staticmethod
    def resolve_merchant_id() -> str:
        db = ZarinpalConfigService.get_settings()
        if db.merchant_id:
            return db.merchant_id
        return os.environ.get('ZARINPAL_MERCHANT_ID', '') or getattr(
            django_settings, 'ZARINPAL_MERCHANT_ID', ''
        )

    @staticmethod
    def resolve_is_sandbox() -> bool:
        db = ZarinpalConfigService.get_settings()
        if db.merchant_id or db.is_sandbox is not None:
            return db.is_sandbox
        return getattr(django_settings, 'ZARINPAL_SANDBOX', True)

    @staticmethod
    def resolve_is_mock() -> bool:
        db = ZarinpalConfigService.get_settings()
        env_mock = os.environ.get('ZARINPAL_MOCK', '')
        if env_mock:
            return env_mock.lower() in ('true', '1', 'yes')
        if db.merchant_id:
            return db.is_mock
        return getattr(django_settings, 'ZARINPAL_MOCK', True)

    @staticmethod
    def resolve_callback_url() -> str:
        db = ZarinpalConfigService.get_settings()
        if db.callback_url:
            return db.callback_url
        return os.environ.get('ZARINPAL_CALLBACK_URL', '') or getattr(
            django_settings, 'ZARINPAL_CALLBACK_URL',
            'http://localhost/api/payments/zarinpal/verify/',
        )

    @staticmethod
    def resolve_currency() -> str:
        db = ZarinpalConfigService.get_settings()
        return db.currency or ZarinpalSettings.CURRENCY_IRR

    @staticmethod
    def resolve_client_id() -> str:
        db = ZarinpalConfigService.get_settings()
        if db.client_id:
            return db.client_id
        return os.environ.get('ZARINPAL_CLIENT_ID', '') or getattr(
            django_settings, 'ZARINPAL_CLIENT_ID', ''
        )

    @staticmethod
    def resolve_client_secret() -> str:
        db = ZarinpalConfigService.get_settings()
        if db.client_secret_encrypted:
            decrypted = decrypt_value(db.client_secret_encrypted)
            if decrypted:
                return decrypted
        return os.environ.get('ZARINPAL_CLIENT_SECRET', '') or getattr(
            django_settings, 'ZARINPAL_CLIENT_SECRET', ''
        )

    @staticmethod
    def resolve_terminal_id() -> str:
        db = ZarinpalConfigService.get_settings()
        if db.terminal_id:
            return db.terminal_id
        return os.environ.get('ZARINPAL_TERMINAL_ID', '') or getattr(
            django_settings, 'ZARINPAL_TERMINAL_ID', ''
        )

    @staticmethod
    def resolve_max_retries() -> int:
        db = ZarinpalConfigService.get_settings()
        return db.max_retry_attempts or 3

    @staticmethod
    def resolve_enable_logging() -> bool:
        db = ZarinpalConfigService.get_settings()
        return db.enable_api_logging

    @staticmethod
    def resolve_auto_reconcile() -> bool:
        db = ZarinpalConfigService.get_settings()
        return db.auto_reconcile

    @staticmethod
    def store_tokens(access_token: str, refresh_token: str, expires_at) -> None:
        db = ZarinpalConfigService.get_settings()
        db.access_token_encrypted = encrypt_value(access_token)
        if refresh_token:
            db.refresh_token_encrypted = encrypt_value(refresh_token)
        db.token_expires_at = expires_at
        db.save(update_fields=[
            'access_token_encrypted', 'refresh_token_encrypted', 'token_expires_at', 'updated_at',
        ])

    @staticmethod
    def get_stored_access_token() -> str:
        db = ZarinpalConfigService.get_settings()
        return decrypt_value(db.access_token_encrypted)

    @staticmethod
    def get_stored_refresh_token() -> str:
        db = ZarinpalConfigService.get_settings()
        return decrypt_value(db.refresh_token_encrypted)

    @staticmethod
    def get_token_expires_at():
        db = ZarinpalConfigService.get_settings()
        return db.token_expires_at

    @staticmethod
    def rest_base_url() -> str:
        if ZarinpalConfigService.resolve_is_sandbox():
            return 'https://sandbox.zarinpal.com/pg/v4/payment'
        return 'https://payment.zarinpal.com/pg/v4/payment'

    @staticmethod
    def gateway_url() -> str:
        if ZarinpalConfigService.resolve_is_sandbox():
            return 'https://sandbox.zarinpal.com/pg/StartPay/'
        return 'https://payment.zarinpal.com/pg/StartPay/'

    @staticmethod
    def graphql_url() -> str:
        return 'https://next.zarinpal.com/api/v4/graphql/'

    @staticmethod
    def oauth_token_url() -> str:
        return 'https://next.zarinpal.com/api/oauth/token'
