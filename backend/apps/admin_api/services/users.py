"""Who may do what to whom in the user-management screen.

Staff can look after customers; only a superuser can touch another admin or
hand out admin rights. Every rule below fails closed with a Persian message the
dashboard can show verbatim.
"""

from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.accounts.models import AuthAuditLog, User, is_admin_phone
from apps.admin_api.services import audit_actor


def assert_can_manage(actor: User, target: User) -> None:
    """Staff may manage customers; admins may only be managed by a superuser."""
    if actor.is_superuser:
        return
    if target.is_staff or target.is_superuser:
        raise PermissionDenied('برای مدیریت حساب‌های ادمین باید مدیر ارشد باشید.')


def assert_not_self(actor: User, target: User, message: str) -> None:
    if actor.pk == target.pk:
        raise ValidationError({'detail': message})


def assert_superuser_remains(target: User, *, losing_superuser: bool) -> None:
    """Never let the store lock itself out of its own dashboard."""
    if not losing_superuser or not target.is_superuser:
        return
    others = User.objects.filter(is_superuser=True, is_active=True).exclude(pk=target.pk).count()
    if others == 0:
        raise ValidationError({'detail': 'این تنها مدیر ارشد فعال است و نمی‌توان دسترسی او را برداشت.'})


def assert_role_change_sticks(target: User, *, is_staff: bool, is_superuser: bool) -> None:
    """A phone on the admin list is re-promoted at every login — say so up front."""
    if (target.is_staff and not is_staff) or (target.is_superuser and not is_superuser):
        if is_admin_phone(target.phone):
            raise ValidationError({'detail': (
                'این شماره در فهرست شماره‌های ادمین است و در ورود بعدی دوباره ادمین می‌شود. '
                'ابتدا آن را از «تنظیمات ← احراز هویت» حذف کنید.'
            )})


def log_role_change(actor: User, target: User, before: dict, after: dict, ip=None) -> None:
    audit_actor(
        AuthAuditLog.ACTION_ROLE_CHANGED, actor, target, ip,
        extra={'before': before, 'after': after},
    )
