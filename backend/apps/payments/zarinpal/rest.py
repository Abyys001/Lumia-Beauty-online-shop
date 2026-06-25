from .client import ZarinpalHttpClient
from .config import ZarinpalConfigService
from .errors import parse_api_response


class ZarinpalRestClient:
    @classmethod
    def _merchant_id(cls) -> str:
        return ZarinpalConfigService.resolve_merchant_id()

    @classmethod
    def request_payment(
        cls,
        amount: int,
        description: str,
        callback_url: str | None = None,
        metadata: dict | None = None,
        currency: str | None = None,
    ) -> tuple[bool, dict, str, int | None]:
        url = f'{ZarinpalConfigService.rest_base_url()}/request.json'
        payload = {
            'merchant_id': cls._merchant_id(),
            'amount': amount,
            'description': description,
            'callback_url': callback_url or ZarinpalConfigService.resolve_callback_url(),
            'currency': currency or ZarinpalConfigService.resolve_currency(),
        }
        if metadata:
            payload['metadata'] = metadata
        result = ZarinpalHttpClient.post_json(url, payload)
        return parse_api_response(result)

    @classmethod
    def verify_payment(cls, amount: int, authority: str) -> tuple[bool, dict, str, int | None]:
        url = f'{ZarinpalConfigService.rest_base_url()}/verify.json'
        payload = {
            'merchant_id': cls._merchant_id(),
            'amount': amount,
            'authority': authority,
        }
        result = ZarinpalHttpClient.post_json(url, payload)
        return parse_api_response(result)

    @classmethod
    def reverse_payment(cls, authority: str) -> tuple[bool, dict, str, int | None]:
        url = f'{ZarinpalConfigService.rest_base_url()}/reverse.json'
        payload = {
            'merchant_id': cls._merchant_id(),
            'authority': authority,
        }
        result = ZarinpalHttpClient.post_json(url, payload)
        return parse_api_response(result)

    @classmethod
    def inquiry(cls, authority: str) -> tuple[bool, dict, str, int | None]:
        url = f'{ZarinpalConfigService.rest_base_url()}/inquiry.json'
        payload = {
            'merchant_id': cls._merchant_id(),
            'authority': authority,
        }
        result = ZarinpalHttpClient.post_json(url, payload)
        return parse_api_response(result)

    @classmethod
    def unverified(cls) -> tuple[bool, dict, str, int | None]:
        url = f'{ZarinpalConfigService.rest_base_url()}/unVerified.json'
        payload = {'merchant_id': cls._merchant_id()}
        result = ZarinpalHttpClient.post_json(url, payload)
        return parse_api_response(result)

    @classmethod
    def fee_calculation(cls, amount: int, currency: str | None = None) -> tuple[bool, dict, str, int | None]:
        url = f'{ZarinpalConfigService.rest_base_url()}/feeCalculation.json'
        payload = {
            'merchant_id': cls._merchant_id(),
            'amount': amount,
            'currency': currency or ZarinpalConfigService.resolve_currency(),
        }
        result = ZarinpalHttpClient.post_json(url, payload)
        return parse_api_response(result)

    @classmethod
    def get_redirect_url(cls, authority: str) -> str:
        return f'{ZarinpalConfigService.gateway_url()}{authority}'
