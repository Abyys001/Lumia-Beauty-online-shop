import logging
from datetime import timedelta

from django.utils import timezone

from .client import ZarinpalHttpClient
from .config import ZarinpalConfigService

logger = logging.getLogger(__name__)


class ZarinpalGraphQLClient:
    @classmethod
    def _graphql_request(cls, query: str, variables: dict | None = None) -> dict:
        token = cls.ensure_access_token()
        if not token:
            return {'errors': [{'message': 'OAuth token unavailable'}]}
        headers = {'Authorization': f'Bearer {token}'}
        return ZarinpalHttpClient.post_json(
            ZarinpalConfigService.graphql_url(),
            {'query': query, 'variables': variables or {}},
            headers=headers,
        )

    @classmethod
    def ensure_access_token(cls) -> str:
        expires_at = ZarinpalConfigService.get_token_expires_at()
        token = ZarinpalConfigService.get_stored_access_token()
        if token and expires_at and expires_at > timezone.now() + timedelta(minutes=5):
            return token
        return cls._refresh_access_token()

    @classmethod
    def _refresh_access_token(cls) -> str:
        refresh_token = ZarinpalConfigService.get_stored_refresh_token()
        client_id = ZarinpalConfigService.resolve_client_id()
        client_secret = ZarinpalConfigService.resolve_client_secret()

        if not all([refresh_token, client_id, client_secret]):
            return ''

        payload = {
            'grant_type': 'refresh_token',
            'client_id': client_id,
            'client_secret': client_secret,
            'refresh_token': refresh_token,
        }
        try:
            result = ZarinpalHttpClient.post_json(
                ZarinpalConfigService.oauth_token_url(),
                payload,
            )
        except Exception as exc:
            logger.warning('Zarinpal OAuth refresh failed: %s', exc)
            return ''

        access_token = result.get('access_token', '')
        new_refresh = result.get('refresh_token', refresh_token)
        expires_in = result.get('expires_in', 1296000)
        if access_token:
            expires_at = timezone.now() + timedelta(seconds=int(expires_in))
            ZarinpalConfigService.store_tokens(access_token, new_refresh, expires_at)
        return access_token

    @classmethod
    def store_oauth_tokens(cls, access_token: str, refresh_token: str, expires_in: int) -> None:
        expires_at = timezone.now() + timedelta(seconds=int(expires_in))
        ZarinpalConfigService.store_tokens(access_token, refresh_token, expires_at)

    @classmethod
    def list_sessions(cls, terminal_id: str | None = None) -> dict:
        tid = terminal_id or ZarinpalConfigService.resolve_terminal_id()
        query = """
        query Sessions($terminal_id: ID!) {
          Session(terminal_id: $terminal_id) {
            id status amount description created_at card_pan ref_id
          }
        }
        """
        return cls._graphql_request(query, {'terminal_id': tid})

    @classmethod
    def list_reconciliations(cls, terminal_id: str | None = None, status_filter: str | None = None) -> dict:
        tid = terminal_id or ZarinpalConfigService.resolve_terminal_id()
        query = """
        query Reconciles($terminal_id: ID!, $filter: ReconciliationStatusEnum) {
          resource: Reconciliation(terminal_id: $terminal_id, filter: $filter) {
            id status amount payable_at reference_id reconciled_at
          }
        }
        """
        variables = {'terminal_id': tid}
        if status_filter:
            variables['filter'] = status_filter
        return cls._graphql_request(query, variables)

    @classmethod
    def add_refund(
        cls,
        session_id: str,
        amount: int,
        description: str = '',
        method: str = 'CARD',
        reason: str = 'CUSTOMER_REQUEST',
    ) -> dict:
        query = """
        mutation AddRefund(
          $session_id: ID!,
          $amount: BigInteger!,
          $description: String,
          $method: InstantPayoutActionTypeEnum,
          $reason: RefundReasonEnum
        ) {
          resource: AddRefund(
            session_id: $session_id,
            amount: $amount,
            description: $description,
            method: $method,
            reason: $reason
          ) {
            id amount terminal_id
            timeline { refund_amount refund_time refund_status }
          }
        }
        """
        variables = {
            'session_id': session_id,
            'amount': amount,
            'description': description,
            'method': method,
            'reason': reason,
        }
        return cls._graphql_request(query, variables)
