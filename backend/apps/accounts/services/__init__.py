"""Account domain services."""

__all__ = ['AuthAuditService', 'OtpService', 'SmsConfigService', 'issue_tokens']


def __getattr__(name: str):
    if name == 'AuthAuditService':
        from .audit import AuthAuditService
        return AuthAuditService
    if name == 'OtpService':
        from .otp_service import OtpService
        return OtpService
    if name == 'SmsConfigService':
        from .sms_config import SmsConfigService
        return SmsConfigService
    if name == 'issue_tokens':
        from .tokens import issue_tokens
        return issue_tokens
    raise AttributeError(name)
