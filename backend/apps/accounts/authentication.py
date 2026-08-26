from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import AuthenticationFailed

SESSION_EPOCH_CLAIM = 'sess'


class EpochJWTAuthentication(JWTAuthentication):
    """Rejects tokens minted before the user's sessions were last revoked.

    simplejwt has no blacklist table here, so a stolen or shared token could
    otherwise outlive a password reset by up to the refresh lifetime. The epoch
    claim rides along on refreshes (simplejwt copies custom claims), so a single
    counter bump on the user row invalidates the whole outstanding tree.
    """

    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        token_epoch = validated_token.get(SESSION_EPOCH_CLAIM)
        if token_epoch is None or int(token_epoch) != user.session_epoch:
            raise AuthenticationFailed('نشست شما باطل شده است. دوباره وارد شوید.', code='session_revoked')
        return user
