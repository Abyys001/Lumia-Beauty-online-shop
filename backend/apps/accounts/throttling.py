from django.conf import settings
from rest_framework.throttling import ScopedRateThrottle


class OtpScopedThrottle(ScopedRateThrottle):
    scope = 'otp'

    def allow_request(self, request, view):
        if getattr(settings, 'OTP_DISABLE_RATE_LIMIT', False):
            return True
        return super().allow_request(request, view)
