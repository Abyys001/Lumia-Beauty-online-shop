from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.accounts.models import OtpTemplate


@dataclass
class SmsResult:
    success: bool
    provider_response: dict
    message_id: str | None = None
    error: str | None = None

    @property
    def as_bool(self) -> bool:
        return self.success


class SmsProvider:
    def send_otp(self, phone: str, code: str, template: 'OtpTemplate | None') -> SmsResult:
        raise NotImplementedError

    def test_connection(self) -> SmsResult:
        raise NotImplementedError

    def get_credit(self) -> float | None:
        raise NotImplementedError
