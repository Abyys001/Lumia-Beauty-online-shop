import hashlib
import logging
import secrets
import string
from dataclasses import dataclass
from datetime import timedelta

from django.conf import settings as django_settings
from django.core.cache import cache
from django.utils import timezone

from apps.accounts.models import (
    AuthAuditLog,
    OtpRequest,
    SmsLog,
    User,
)
from apps.accounts.services.audit import AuthAuditService
from apps.accounts.services.sms_config import SmsConfigService
from apps.accounts.services.tokens import issue_tokens
from apps.accounts.sms.mock import log_sms_attempt

logger = logging.getLogger('accounts.otp')


def _get_sms_provider():
    from apps.accounts.sms import get_sms_provider
    return get_sms_provider()


@dataclass
class OtpRequestResult:
    success: bool
    detail: str = ''
    bypass_tokens: dict | None = None
    user: User | None = None
    debug_code: str = ''
    status_code: int = 200


@dataclass
class OtpVerifyResult:
    success: bool
    detail: str = ''
    tokens: dict | None = None
    user: User | None = None
    created: bool = False
    status_code: int = 200


def _mask_phone(phone: str) -> str:
    if len(phone) >= 7:
        return f'{phone[:4]}****{phone[-3:]}'
    return phone


def _hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def _otp_cache_key(phone: str) -> str:
    return f'otp:{phone}'


def _otp_rate_key(phone: str) -> str:
    return f'otp_rate:{phone}'


def _otp_verify_rate_key(phone: str) -> str:
    return f'otp_verify_rate:{phone}'


def _otp_ip_rate_key(ip: str) -> str:
    return f'otp_ip_rate:{ip}'


def _check_rate_limit(key: str, limit: int, timeout: int) -> bool:
    if cache.add(key, 1, timeout=timeout):
        return True
    try:
        count = cache.incr(key)
    except ValueError:
        cache.set(key, 1, timeout=timeout)
        return True
    return count <= limit


class OtpService:
    @staticmethod
    def generate_code(length: int) -> str:
        length = max(4, min(8, length))
        return ''.join(secrets.choice(string.digits) for _ in range(length))

    @staticmethod
    def request_otp(phone: str, ip_address=None, user_agent: str = '') -> OtpRequestResult:
        auth_settings = SmsConfigService.get_auth_settings()
        if not auth_settings.otp_login_enabled:
            AuthAuditService.log(AuthAuditLog.ACTION_LOGIN_BLOCKED, phone=phone, ip_address=ip_address)
            return OtpRequestResult(False, 'ورود با OTP غیرفعال است', status_code=403)

        bypass_phone = SmsConfigService.resolve_admin_bypass_phone()
        if bypass_phone and phone == bypass_phone:
            user, _ = User.objects.get_or_create(phone=phone)
            if not user.is_staff or not user.is_superuser:
                user.is_staff = True
                user.is_superuser = True
                user.save(update_fields=['is_staff', 'is_superuser'])
            tokens = issue_tokens(user)
            AuthAuditService.log(
                AuthAuditLog.ACTION_LOGIN_SUCCESS,
                phone=phone,
                user=user,
                ip_address=ip_address,
                metadata={'bypass': True},
            )
            logger.info('Admin bypass login | phone=%s', _mask_phone(phone))
            return OtpRequestResult(
                True,
                bypass_tokens=tokens,
                user=user,
            )

        otp_settings = SmsConfigService.get_otp_settings()

        if ip_address and not _check_rate_limit(
            _otp_ip_rate_key(ip_address),
            otp_settings.ip_rate_limit_count,
            otp_settings.ip_rate_limit_window_seconds,
        ):
            AuthAuditService.log(AuthAuditLog.ACTION_LOGIN_BLOCKED, phone=phone, ip_address=ip_address, metadata={'reason': 'ip_rate_limit'})
            return OtpRequestResult(False, 'تعداد درخواست‌ها بیش از حد مجاز است. لطفاً چند دقیقه صبر کنید.', status_code=429)

        if not _check_rate_limit(
            _otp_rate_key(phone),
            otp_settings.rate_limit_count,
            otp_settings.rate_limit_window_seconds,
        ):
            AuthAuditService.log(AuthAuditLog.ACTION_LOGIN_BLOCKED, phone=phone, ip_address=ip_address, metadata={'reason': 'phone_rate_limit'})
            return OtpRequestResult(False, 'تعداد درخواست‌ها بیش از حد مجاز است. لطفاً چند دقیقه صبر کنید.', status_code=429)

        last_request = OtpRequest.objects.filter(phone=phone, status=OtpRequest.STATUS_PENDING).order_by('-created_at').first()
        if last_request:
            elapsed = (timezone.now() - last_request.created_at).total_seconds()
            if elapsed < otp_settings.resend_delay_seconds:
                wait = int(otp_settings.resend_delay_seconds - elapsed)
                return OtpRequestResult(False, f'لطفاً {wait} ثانیه دیگر تلاش کنید.', status_code=429)

        template = SmsConfigService.get_default_template()
        code = OtpService.generate_code(otp_settings.otp_length)
        expires_at = timezone.now() + timedelta(seconds=otp_settings.expiry_seconds)

        cache.set(_otp_cache_key(phone), code, timeout=otp_settings.expiry_seconds)

        otp_req = OtpRequest.objects.create(
            phone=phone,
            code_hash=_hash_code(code),
            ip_address=ip_address,
            user_agent=user_agent or '',
            status=OtpRequest.STATUS_PENDING,
            template=template,
            expires_at=expires_at,
        )

        provider = _get_sms_provider()
        provider_name = 'smsir' if provider.__class__.__name__ == 'SmsIrProvider' else 'mock'
        result = provider.send_otp(phone, code, template)

        log_status = SmsLog.STATUS_SENT if result.success else SmsLog.STATUS_FAILED
        if provider_name == 'mock':
            log_status = SmsLog.STATUS_SIMULATED

        log_sms_attempt(
            phone=phone,
            provider=provider_name,
            status=log_status,
            request_data={
                'mobile': phone,
                'templateId': template.sms_ir_template_id if template else None,
            },
            response_data=result.provider_response,
            template=template,
            message_id=result.message_id or '',
            error_message=result.error or '',
            ip_address=ip_address,
        )

        AuthAuditService.log(
            AuthAuditLog.ACTION_OTP_REQUESTED,
            phone=phone,
            ip_address=ip_address,
            metadata={'otp_request_id': str(otp_req.id), 'provider': provider_name},
        )

        debug_code = ''
        if django_settings.DEBUG and getattr(django_settings, 'OTP_DEBUG_CODE', False):
            debug_code = code

        if not result.success and not django_settings.DEBUG:
            return OtpRequestResult(False, 'خطا در ارسال پیامک', status_code=503)

        logger.info('OTP requested | phone=%s | provider=%s', _mask_phone(phone), provider_name)
        return OtpRequestResult(True, 'کد تأیید ارسال شد', debug_code=debug_code)

    @staticmethod
    def verify_otp(phone: str, code: str, ip_address=None) -> OtpVerifyResult:
        otp_settings = SmsConfigService.get_otp_settings()

        if not _check_rate_limit(
            _otp_verify_rate_key(phone),
            otp_settings.max_verify_attempts,
            otp_settings.verify_window_seconds,
        ):
            AuthAuditService.log(
                AuthAuditLog.ACTION_LOGIN_BLOCKED,
                phone=phone,
                ip_address=ip_address,
                metadata={'reason': 'verify_rate_limit'},
            )
            return OtpVerifyResult(False, 'تعداد تلاش‌ها بیش از حد مجاز است. لطفاً چند دقیقه صبر کنید.', status_code=429)

        stored = cache.get(_otp_cache_key(phone))
        pending = OtpRequest.objects.filter(phone=phone, status=OtpRequest.STATUS_PENDING).order_by('-created_at').first()

        valid = stored and stored == code
        if not valid and pending and pending.code_hash == _hash_code(code) and pending.expires_at >= timezone.now():
            valid = True

        if not valid:
            if pending:
                pending.attempts += 1
                if pending.attempts >= otp_settings.max_verify_attempts:
                    pending.status = OtpRequest.STATUS_FAILED
                pending.save(update_fields=['attempts', 'status'])
            AuthAuditService.log(AuthAuditLog.ACTION_OTP_FAILED, phone=phone, ip_address=ip_address)
            logger.warning('OTP verify failed | phone=%s', _mask_phone(phone))
            return OtpVerifyResult(False, 'کد تأیید نامعتبر یا منقضی شده است', status_code=400)

        cache.delete(_otp_cache_key(phone))
        if pending:
            pending.status = OtpRequest.STATUS_VERIFIED
            pending.verified_at = timezone.now()
            pending.save(update_fields=['status', 'verified_at'])

        user, created = User.objects.get_or_create(phone=phone)
        tokens = issue_tokens(user)
        AuthAuditService.log(
            AuthAuditLog.ACTION_OTP_VERIFIED,
            phone=phone,
            user=user,
            ip_address=ip_address,
        )
        AuthAuditService.log(
            AuthAuditLog.ACTION_LOGIN_SUCCESS,
            phone=phone,
            user=user,
            ip_address=ip_address,
        )
        logger.info('OTP verified | phone=%s | new_user=%s', _mask_phone(phone), created)
        return OtpVerifyResult(True, tokens=tokens, user=user, created=created)
