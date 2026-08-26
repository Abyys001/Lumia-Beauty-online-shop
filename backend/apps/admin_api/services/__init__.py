from apps.accounts.services.audit import AuthAuditService


def audit_actor(action: str, actor, target, ip=None, extra: dict | None = None) -> None:
    """Audit an admin acting on someone else's account — both sides recorded."""
    AuthAuditService.log(
        action,
        phone=target.phone,
        user=target,
        ip_address=ip,
        metadata={'by': str(actor.pk), 'by_phone': actor.phone, **(extra or {})},
    )
