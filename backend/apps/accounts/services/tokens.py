from datetime import timedelta

from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.models import AuthSettings


def issue_tokens(user):
    auth_settings = AuthSettings.get_settings()
    refresh = RefreshToken.for_user(user)
    refresh.set_exp(
        lifetime=timedelta(days=auth_settings.refresh_token_lifetime_days),
    )
    access = refresh.access_token
    access.set_exp(
        lifetime=timedelta(minutes=auth_settings.access_token_lifetime_minutes),
    )
    return {
        'access': str(access),
        'refresh': str(refresh),
    }
