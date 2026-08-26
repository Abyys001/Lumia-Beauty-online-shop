from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APIClient

from apps.accounts.models import AuthSettings, TrustedDevice, User


class RememberDeviceTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        AuthSettings.get_settings()

    def _register(self, phone='09120000001', remember=True):
        return self.client.post(reverse('register'), {
            'phone': phone, 'password': 'secret', 'first_name': 'مریم', 'last_name': 'رضایی',
            'remember_device': remember,
        }, format='json')

    def test_register_remembers_the_device_by_default(self):
        res = self._register()
        self.assertEqual(res.status_code, 201)
        self.assertIsNotNone(res.data['device'])
        self.assertEqual(TrustedDevice.objects.count(), 1)

    def test_register_can_opt_out(self):
        res = self._register(remember=False)
        self.assertIsNone(res.data['device'])
        self.assertEqual(TrustedDevice.objects.count(), 0)

    def test_login_remembers_the_device(self):
        self._register(remember=False)
        res = self.client.post(reverse('login'), {
            'phone': '09120000001', 'password': 'secret', 'remember_device': True,
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertIsNotNone(res.data['device'])

    def test_device_login_returns_a_working_session_without_a_password(self):
        device = self._register().data['device']
        res = self.client.post(reverse('device-login'), {
            'device_id': device['id'], 'device_token': device['token'],
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['user']['phone'], '09120000001')

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {res.data["access"]}')
        self.assertEqual(self.client.get(reverse('user-profile')).status_code, 200)

    def test_device_token_rotates_on_every_auto_login(self):
        device = self._register().data['device']
        first = self.client.post(reverse('device-login'), {
            'device_id': device['id'], 'device_token': device['token'],
        }, format='json').data['device']
        self.assertNotEqual(first['token'], device['token'])
        self.assertEqual(first['id'], device['id'])

        second = self.client.post(reverse('device-login'), {
            'device_id': first['id'], 'device_token': first['token'],
        }, format='json')
        self.assertEqual(second.status_code, 200)

    def test_replaying_a_spent_token_kills_the_device(self):
        device = self._register().data['device']
        self.client.post(reverse('device-login'), {
            'device_id': device['id'], 'device_token': device['token'],
        }, format='json')

        replay = self.client.post(reverse('device-login'), {
            'device_id': device['id'], 'device_token': device['token'],
        }, format='json')
        self.assertEqual(replay.status_code, 401)
        self.assertIsNotNone(TrustedDevice.objects.get(id=device['id']).revoked_at)

    def test_expired_device_is_refused(self):
        device = self._register().data['device']
        TrustedDevice.objects.filter(id=device['id']).update(
            expires_at=timezone.now() - timezone.timedelta(days=1),
        )
        res = self.client.post(reverse('device-login'), {
            'device_id': device['id'], 'device_token': device['token'],
        }, format='json')
        self.assertEqual(res.status_code, 401)

    def test_deactivated_user_cannot_auto_login(self):
        device = self._register().data['device']
        User.objects.filter(phone='09120000001').update(is_active=False)
        res = self.client.post(reverse('device-login'), {
            'device_id': device['id'], 'device_token': device['token'],
        }, format='json')
        self.assertEqual(res.status_code, 401)


class SessionEpochTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user('09120000002', 'secret')

    def _login(self):
        return self.client.post(reverse('login'), {
            'phone': '09120000002', 'password': 'secret', 'remember_device': False,
        }, format='json').data

    def test_revoking_sessions_invalidates_an_outstanding_access_token(self):
        tokens = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        self.assertEqual(self.client.get(reverse('user-profile')).status_code, 200)

        self.user.revoke_sessions()
        self.assertEqual(self.client.get(reverse('user-profile')).status_code, 401)

    def test_revoking_sessions_closes_the_refresh_endpoint(self):
        tokens = self._login()
        self.user.revoke_sessions()
        refreshed = self.client.post(reverse('token-refresh'), {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(refreshed.status_code, 401)

    def test_deactivated_user_cannot_refresh(self):
        tokens = self._login()
        User.objects.filter(pk=self.user.pk).update(is_active=False)
        refreshed = self.client.post(reverse('token-refresh'), {'refresh': tokens['refresh']}, format='json')
        self.assertEqual(refreshed.status_code, 401)

    def test_refresh_keeps_working_while_the_epoch_is_unchanged(self):
        tokens = self._login()
        refreshed = self.client.post(reverse('token-refresh'), {'refresh': tokens['refresh']}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {refreshed.data["access"]}')
        self.assertEqual(self.client.get(reverse('user-profile')).status_code, 200)

    def test_changing_own_password_hands_back_a_usable_session(self):
        tokens = self._login()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        res = self.client.post(reverse('user-password'), {
            'new_password': 'newsecret', 'confirm_password': 'newsecret',
        }, format='json')
        self.assertEqual(res.status_code, 200)

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        self.assertEqual(self.client.get(reverse('user-profile')).status_code, 401)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {res.data["access"]}')
        self.assertEqual(self.client.get(reverse('user-profile')).status_code, 200)
