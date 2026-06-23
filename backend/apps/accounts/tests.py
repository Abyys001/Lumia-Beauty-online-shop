from django.core.cache import cache
from django.test import TestCase, override_settings
from rest_framework.test import APIClient

from apps.accounts.models import AuthSettings, OtpTemplate, SmsProviderSettings
from apps.accounts.sms import MockSmsProvider, SmsIrProvider, get_sms_provider
from apps.accounts.sms.base import SmsResult


class SmsProviderTests(TestCase):
    def setUp(self):
        SmsProviderSettings.objects.update_or_create(
            pk=1,
            defaults={'provider_mode': SmsProviderSettings.PROVIDER_MOCK, 'is_active': True},
        )

    def test_mock_provider_always_succeeds(self):
        tpl = OtpTemplate.objects.create(name='Test', sms_ir_template_id=1, parameter_name='Code')
        result = MockSmsProvider().send_otp('09123456789', '123456', tpl)
        self.assertTrue(result.success)

    def test_smsir_provider_fails_gracefully_without_key(self):
        tpl = OtpTemplate.objects.create(name='Test', sms_ir_template_id=1, parameter_name='Code')
        SmsProviderSettings.objects.filter(pk=1).update(api_key_encrypted='')
        result = SmsIrProvider().send_otp('09123456789', '123456', tpl)
        self.assertFalse(result.success)

    def test_factory_returns_smsir_when_configured(self):
        SmsProviderSettings.objects.filter(pk=1).update(
            provider_mode=SmsProviderSettings.PROVIDER_SMSIR,
            is_active=True,
        )
        self.assertIsInstance(get_sms_provider(), SmsIrProvider)

    def test_factory_returns_mock_by_default(self):
        SmsProviderSettings.objects.filter(pk=1).update(
            provider_mode=SmsProviderSettings.PROVIDER_MOCK,
        )
        self.assertIsInstance(get_sms_provider(), MockSmsProvider)


class OTPRequestViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        from apps.accounts.models import OtpSettings
        OtpSettings.objects.update_or_create(pk=1, defaults={
            'rate_limit_count': 5,
            'rate_limit_window_seconds': 900,
            'resend_delay_seconds': 0,
        })
        OtpTemplate.objects.get_or_create(
            name='Default',
            defaults={'sms_ir_template_id': 123456, 'parameter_name': 'CODE', 'is_default': True, 'is_active': True},
        )

    def _request_otp(self, phone='09123456789'):
        return self.client.post('/api/auth/otp/request/', {'phone': phone}, format='json')

    def test_fifth_request_succeeds(self):
        for _ in range(4):
            self._request_otp()
        self.assertEqual(self._request_otp().status_code, 200)

    def test_sixth_request_is_rate_limited(self):
        for _ in range(5):
            self._request_otp()
        self.assertEqual(self._request_otp().status_code, 429)

    def test_different_phones_have_independent_limits(self):
        from apps.accounts.models import OtpSettings
        OtpSettings.objects.filter(pk=1).update(rate_limit_count=1)
        self._request_otp('09111111111')
        r1 = self._request_otp('09111111111')
        r2 = self._request_otp('09222222222')
        self.assertEqual(r1.status_code, 429)
        self.assertEqual(r2.status_code, 200)

    @override_settings(DEBUG=True, OTP_DEBUG_CODE=False)
    def test_otp_debug_code_requires_explicit_setting(self):
        response = self._request_otp()
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('debug_code', response.data)

    @override_settings(DEBUG=True, OTP_DEBUG_CODE=True)
    def test_debug_code_exposed_when_enabled(self):
        response = self._request_otp()
        self.assertIn('debug_code', response.data)
        self.assertEqual(len(response.data['debug_code']), 6)
        self.assertTrue(response.data['debug_code'].isdigit())

    def test_invalid_phone_rejected_on_request(self):
        self.assertEqual(self.client.post('/api/auth/otp/request/', {'phone': '12345'}, format='json').status_code, 400)

    def test_phone_with_country_code_normalized(self):
        self.assertEqual(self._request_otp('989123456789').status_code, 200)

    def test_admin_bypass_skips_otp_and_grants_staff(self):
        from apps.accounts.models import User
        AuthSettings.objects.update_or_create(pk=1, defaults={'admin_bypass_phone': '09916122680'})

        response = self._request_otp('09916122680')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertTrue(response.data['user']['is_staff'])
        self.assertNotIn('debug_code', response.data)

        user = User.objects.get(phone='09916122680')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class OTPVerifyViewTests(TestCase):
    def setUp(self):
        cache.clear()
        self.client = APIClient()
        from apps.accounts.models import OtpSettings
        OtpSettings.objects.update_or_create(pk=1, defaults={
            'max_verify_attempts': 5,
            'verify_window_seconds': 900,
            'resend_delay_seconds': 0,
        })
        OtpTemplate.objects.get_or_create(
            name='Default',
            defaults={'sms_ir_template_id': 123456, 'parameter_name': 'CODE', 'is_default': True, 'is_active': True},
        )

    def _request_otp(self, phone='09123456789'):
        with self.settings(OTP_DEBUG_CODE=True, DEBUG=True):
            r = self.client.post('/api/auth/otp/request/', {'phone': phone}, format='json')
        return r.data.get('debug_code')

    def _verify(self, phone, code):
        return self.client.post('/api/auth/otp/verify/', {'phone': phone, 'code': code}, format='json')

    def test_correct_otp_returns_jwt_tokens(self):
        code = self._request_otp()
        response = self._verify('09123456789', code)
        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_wrong_otp_returns_400(self):
        self._request_otp()
        self.assertEqual(self._verify('09123456789', '000000').status_code, 400)

    def test_otp_is_single_use(self):
        code = self._request_otp()
        self._verify('09123456789', code)
        self.assertEqual(self._verify('09123456789', code).status_code, 400)

    def test_otp_verify_is_rate_limited(self):
        from apps.accounts.models import OtpSettings
        OtpSettings.objects.filter(pk=1).update(max_verify_attempts=2, verify_window_seconds=600)
        payload = {'phone': '09123456789', 'code': '000000'}
        self.client.post('/api/auth/otp/verify/', payload, format='json')
        self.client.post('/api/auth/otp/verify/', payload, format='json')
        response = self.client.post('/api/auth/otp/verify/', payload, format='json')
        self.assertEqual(response.status_code, 429)

    def test_fifth_failed_verify_returns_400_not_429(self):
        for _ in range(4):
            self._verify('09123456789', '000000')
        self.assertEqual(self._verify('09123456789', '000000').status_code, 400)

    def test_sixth_failed_verify_returns_429(self):
        for _ in range(5):
            self._verify('09123456789', '000000')
        self.assertEqual(self._verify('09123456789', '000000').status_code, 429)

    def test_user_created_on_first_verify(self):
        from apps.accounts.models import User
        code = self._request_otp()
        self._verify('09123456789', code)
        self.assertTrue(User.objects.filter(phone='09123456789').exists())

    def test_invalid_phone_format_rejected(self):
        self.assertEqual(self._verify('12345', '123456').status_code, 400)
