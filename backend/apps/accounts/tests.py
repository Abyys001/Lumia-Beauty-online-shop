from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import AuthSettings, User


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'secret123', 'first_name': 'سارا', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['phone'], '09123456789')
        user = User.objects.get(phone='09123456789')
        self.assertTrue(user.check_password('secret123'))

    def test_register_with_names(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'secret123', 'first_name': 'سارا', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(phone='09123456789')
        self.assertEqual(user.first_name, 'سارا')
        self.assertEqual(user.last_name, 'احمدی')

    def test_register_requires_names(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'secret123'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.data)
        self.assertIn('last_name', response.data)

    def test_register_rejects_blank_names(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'secret123', 'first_name': '  ', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('first_name', response.data)

    def test_register_rejects_short_password(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': '123', 'first_name': 'سارا', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_register_rejects_invalid_phone(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '12345', 'password': 'secret123', 'first_name': 'سارا', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)

    def test_register_normalizes_country_code(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '989123456789', 'password': 'secret123', 'first_name': 'سارا', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['phone'], '09123456789')

    def test_register_existing_user_with_password_rejected(self):
        User.objects.create_user(phone='09123456789', password='secret123')
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'newpass', 'first_name': 'سارا', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)

    def test_register_sets_password_for_passwordless_user(self):
        user = User.objects.create_user(phone='09123456789')
        self.assertFalse(user.has_usable_password())
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'secret123', 'first_name': 'سارا', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        user.refresh_from_db()
        self.assertTrue(user.check_password('secret123'))


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(phone='09123456789', password='secret123')

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            '/api/auth/login/',
            {'phone': '09123456789', 'password': 'secret123'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_with_wrong_password(self):
        response = self.client.post(
            '/api/auth/login/',
            {'phone': '09123456789', 'password': 'wrongpass'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('detail', response.data)

    def test_login_unknown_phone(self):
        response = self.client.post(
            '/api/auth/login/',
            {'phone': '09111111111', 'password': 'secret123'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)

    def test_login_normalizes_phone(self):
        response = self.client.post(
            '/api/auth/login/',
            {'phone': '989123456789', 'password': 'secret123'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)

    def test_login_admin_bypass_grants_staff(self):
        AuthSettings.objects.update_or_create(pk=1, defaults={'admin_bypass_phone': '09916122680'})
        response = self.client.post(
            '/api/auth/login/',
            {'phone': '09916122680', 'password': 'anything'},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['user']['is_staff'])
        user = User.objects.get(phone='09916122680')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class AdminPhoneTests(TestCase):
    """Registering with a configured admin phone must grant staff + superuser."""

    def setUp(self):
        self.client = APIClient()

    @override_settings(ADMIN_PHONES=['09916122680', '09332279699', '09166099383'])
    def test_register_admin_phone_grants_staff(self):
        for phone in ['09916122680', '09332279699', '09166099383']:
            with self.subTest(phone=phone):
                response = self.client.post(
                    '/api/auth/register/',
                    {'phone': phone, 'password': 'secret123', 'first_name': 'سارا', 'last_name': 'احمدی'},
                    format='json',
                )
                self.assertEqual(response.status_code, 201)
                self.assertTrue(response.data['user']['is_staff'])
                user = User.objects.get(phone=phone)
                self.assertTrue(user.is_superuser)

    @override_settings(ADMIN_PHONES=['09166099383'])
    def test_register_over_seeded_placeholder_row(self):
        """The boot-time placeholder row (no password set) must not block sign-up."""
        User.objects.create(phone='09166099383', is_staff=True, is_superuser=True)
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09166099383', 'password': 'secret123', 'first_name': 'مینا', 'last_name': 'قراچه'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(phone='09166099383')
        self.assertTrue(user.check_password('secret123'))
        self.assertTrue(user.is_staff)

    @override_settings(ADMIN_PHONES=['09166099383'])
    def test_register_normal_phone_stays_customer(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'secret123', 'first_name': 'سارا', 'last_name': 'احمدی'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertFalse(User.objects.get(phone='09123456789').is_staff)

    @override_settings(ADMIN_PHONES=['09332279699'], ADMIN_BYPASS_PHONE='')
    def test_admin_phone_still_needs_password_on_login(self):
        User.objects.create_user(phone='09332279699', password='secret123')
        response = self.client.post(
            '/api/auth/login/',
            {'phone': '09332279699', 'password': 'wrong'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
