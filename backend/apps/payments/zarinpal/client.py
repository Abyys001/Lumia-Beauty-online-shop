import logging
import time

import requests

from .config import ZarinpalConfigService

logger = logging.getLogger(__name__)


class ZarinpalHttpClient:
    DEFAULT_TIMEOUT = 15

    @classmethod
    def post_json(cls, url: str, payload: dict, headers: dict | None = None) -> dict:
        max_retries = ZarinpalConfigService.resolve_max_retries()
        merged_headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
        if headers:
            merged_headers.update(headers)

        last_exc = None
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    url,
                    json=payload,
                    headers=merged_headers,
                    timeout=cls.DEFAULT_TIMEOUT,
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                last_exc = exc
                if ZarinpalConfigService.resolve_enable_logging():
                    logger.warning(
                        'Zarinpal request failed (attempt %s/%s): %s %s',
                        attempt + 1, max_retries, url, exc,
                    )
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)

        if last_exc:
            raise last_exc
        return {}
