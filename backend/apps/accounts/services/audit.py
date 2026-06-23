from apps.accounts.models import AuthAuditLog


class AuthAuditService:
    @staticmethod
    def log(action: str, phone: str = '', user=None, ip_address=None, metadata=None):
        AuthAuditLog.objects.create(
            action=action,
            phone=phone or '',
            user=user,
            ip_address=ip_address,
            metadata=metadata or {},
        )
