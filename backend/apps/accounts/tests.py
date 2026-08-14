from django.core.cache import cache
from django.test import TestCase
from rest_framework.test import APIClient
from unittest.mock import patch
import os

from apps.accounts.models import AuthSettings, OtpTemplate, SmsProviderProfile, SmsProviderSettings, User
from apps.accounts.services.sms_config import SmsConfigService
from apps.accounts.services.sms_sync import sync_default_template_for_mode
from apps.accounts.sms import IranPayamakProvider, MockSmsProvider, SmsIrProvider, get_sms_provider
from apps.accounts.sms.iranpayamak import IranPayamakApiResult
from apps.accounts.sms.iranpayamak_utils import format_mobile_for_iranpayamak, validate_iran_mobile_for_iranpayamak
from apps.accounts.sms.smsir_utils import (
    format_mobile_for_smsir,
    map_smsir_status,
    normalize_verify_parameters,
    to_ascii_digits,
    validate_iran_mobile_for_smsir,
)
from apps.accounts.utils.encryption import encrypt_value


class SmsProviderTests(TestCase):
    def setUp(self):
        SmsProviderSettings.objects.update_or_create(
            pk=1,
            defaults={'provider_mode': SmsProviderSettings.PROVIDER_MOCK, 'is_active': True},
        )
        SmsProviderProfile.ensure_profiles()
        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_MOCK)
        SmsProviderProfile.ensure_profiles()
        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_MOCK)

    def _activate_smsir(self, **kwargs):
        profile = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_SMSIR)
        for k, v in kwargs.items():
            setattr(profile, k, v)
        profile.save()
        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_SMSIR)
        return profile

    def _activate_iranpayamak(self, **kwargs):
        profile = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_IRANPAYAMAK)
        for k, v in kwargs.items():
            setattr(profile, k, v)
        profile.save()
        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_IRANPAYAMAK)
        return profile

    def test_mock_provider_always_succeeds(self):
        tpl = OtpTemplate.objects.create(name='Test', sms_ir_template_id=1, parameter_name='Code')
        result = MockSmsProvider().send_otp('09123456789', '123456', tpl)
        self.assertTrue(result.success)

    def test_smsir_provider_fails_gracefully_without_key(self):
        tpl = OtpTemplate.objects.create(name='Test', sms_ir_template_id=1, parameter_name='Code')
        self._activate_smsir(api_key_encrypted='')
        result = SmsIrProvider().send_otp('09123456789', '123456', tpl)
        self.assertFalse(result.success)

    def test_factory_returns_smsir_when_configured(self):
        self._activate_smsir()
        self.assertIsInstance(get_sms_provider(), SmsIrProvider)

    def test_factory_returns_iranpayamak_when_configured(self):
        self._activate_iranpayamak(
            line_number='50002178584000',
            api_key_encrypted=encrypt_value('test-key'),
        )
        self.assertIsInstance(get_sms_provider(), IranPayamakProvider)

    @patch('apps.accounts.sms.iranpayamak.IranPayamakClient.send_pattern')
    def test_iranpayamak_send_otp_success(self, mock_send):
        mock_send.return_value = (
            IranPayamakApiResult(success=True, status='success', data=12345, http_status=201),
            {'code': 'PAT1', 'recipient': '09123456789'},
        )
        self._activate_iranpayamak(
            line_number='50002178584000',
            api_key_encrypted=encrypt_value('test-key'),
            base_url='https://api.iranpayamak.com',
        )
        tpl = OtpTemplate.objects.create(
            name='IP Test',
            pattern_code='PAT1',
            parameter_name='CODE',
        )
        result = IranPayamakProvider().send_otp('09123456789', '123456', tpl)
        self.assertTrue(result.success)
        self.assertEqual(result.message_id, '12345')

    def test_iranpayamak_send_otp_requires_pattern_code(self):
        self._activate_iranpayamak(
            line_number='50002178584000',
            api_key_encrypted=encrypt_value('test-key'),
        )
        tpl = OtpTemplate.objects.create(name='No Pattern', parameter_name='CODE')
        result = IranPayamakProvider().send_otp('09123456789', '123456', tpl)
        self.assertFalse(result.success)
        self.assertIn('Pattern', result.error or '')

    def test_iranpayamak_mobile_validation(self):
        formatted, error = validate_iran_mobile_for_iranpayamak('09123456789')
        self.assertEqual(formatted, '09123456789')
        self.assertEqual(error, '')
        self.assertEqual(format_mobile_for_iranpayamak('9123456789'), '09123456789')

    @patch.dict(os.environ, {'SMS_PROVIDER': 'iranpayamak'}, clear=False)
    def test_resolve_provider_mode_iranpayamak(self):
        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_MOCK)
        SmsConfigService.bootstrap_from_env()
        self.assertEqual(SmsConfigService.resolve_provider_mode(), SmsProviderProfile.PROVIDER_IRANPAYAMAK)

    @patch.dict(os.environ, {'SMS_PROVIDER': 'mock'}, clear=False)
    def test_factory_returns_mock_by_default(self):
        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_MOCK)
        self.assertIsInstance(get_sms_provider(), MockSmsProvider)

    def test_format_mobile_for_smsir(self):
        self.assertEqual(format_mobile_for_smsir('09123456789'), '9123456789')
        self.assertEqual(format_mobile_for_smsir('989123456789'), '9123456789')
        self.assertEqual(format_mobile_for_smsir('+989123456789'), '9123456789')
        self.assertEqual(format_mobile_for_smsir('۰۹۱۲۳۴۵۶۷۸۹'), '9123456789')

    def test_to_ascii_digits_on_otp_code(self):
        self.assertEqual(to_ascii_digits('۱۲۳۴۵۶'), '123456')

    def test_validate_iran_mobile_rejects_invalid(self):
        formatted, error = validate_iran_mobile_for_smsir('9812345678')
        self.assertEqual(formatted, '')
        self.assertIn('نادرست', error)

    def test_normalize_verify_parameters_ascii(self):
        params = normalize_verify_parameters([{'name': 'Code', 'value': '۱۲۳۴۵'}])
        self.assertEqual(params[0]['value'], '12345')

    def test_map_smsir_status_104(self):
        msg = map_smsir_status(104, '')
        self.assertIn('موبایل', msg)

    def test_resolve_api_key_uses_sandbox_key_when_sandbox(self):
        profile = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_SMSIR)
        profile.api_key_encrypted = encrypt_value('prod-key')
        profile.sandbox_api_key_encrypted = encrypt_value('sandbox-key')
        profile.is_sandbox = True
        profile.save()
        self.assertEqual(SmsConfigService.resolve_api_key(profile=profile), 'sandbox-key')
        self.assertEqual(SmsConfigService.resolve_api_key(profile=profile, sandbox=False), 'prod-key')

    def test_resolve_api_key_falls_back_to_production_in_sandbox_mode(self):
        profile = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_SMSIR)
        profile.api_key_encrypted = encrypt_value('shared-key')
        profile.sandbox_api_key_encrypted = ''
        profile.is_sandbox = True
        profile.save()
        self.assertEqual(SmsConfigService.resolve_api_key(profile=profile), 'shared-key')

    def test_sync_default_template_for_production(self):
        sync_default_template_for_mode(False)
        tpl = OtpTemplate.objects.get(is_default=True)
        self.assertEqual(tpl.sms_ir_template_id, 394212)

    def test_sync_default_template_for_sandbox(self):
        sync_default_template_for_mode(True)
        tpl = OtpTemplate.objects.get(is_default=True)
        self.assertEqual(tpl.sms_ir_template_id, 123456)
        self.assertEqual(tpl.parameter_name, 'Code')

    def test_profiles_store_keys_separately(self):
        smsir = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_SMSIR)
        smsir.api_key_encrypted = encrypt_value('smsir-key')
        smsir.save()
        iranpayamak = SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_IRANPAYAMAK)
        iranpayamak.api_key_encrypted = encrypt_value('ip-key')
        iranpayamak.save()

        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_IRANPAYAMAK)
        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_SMSIR)

        smsir.refresh_from_db()
        iranpayamak.refresh_from_db()
        self.assertEqual(SmsConfigService.resolve_api_key(profile=smsir, sandbox=False), 'smsir-key')
        self.assertEqual(SmsConfigService.resolve_iranpayamak_api_key(profile=iranpayamak), 'ip-key')

    def test_activate_only_one_profile(self):
        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_SMSIR)
        self.assertTrue(SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_SMSIR).is_active)
        self.assertFalse(SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_IRANPAYAMAK).is_active)
        self.assertFalse(SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_MOCK).is_active)

        SmsProviderProfile.activate(SmsProviderProfile.PROVIDER_IRANPAYAMAK)
        self.assertFalse(SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_SMSIR).is_active)
        self.assertTrue(SmsProviderProfile.get_profile(SmsProviderProfile.PROVIDER_IRANPAYAMAK).is_active)


class RegisterViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_register_creates_user_and_returns_tokens(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'secret123'},
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

    def test_register_rejects_short_password(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': '123'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)

    def test_register_rejects_invalid_phone(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '12345', 'password': 'secret123'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)

    def test_register_normalizes_country_code(self):
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '989123456789', 'password': 'secret123'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['phone'], '09123456789')

    def test_register_existing_user_with_password_rejected(self):
        User.objects.create_user(phone='09123456789', password='secret123')
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'newpass'},
            format='json',
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn('phone', response.data)

    def test_register_sets_password_for_passwordless_user(self):
        user = User.objects.create_user(phone='09123456789')
        self.assertFalse(user.has_usable_password())
        response = self.client.post(
            '/api/auth/register/',
            {'phone': '09123456789', 'password': 'secret123'},
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        user.refresh_from_db()
        self.assertTrue(user.check_password('secret123'))


@patch.dict(os.environ, {'SMS_PROVIDER': 'mock'}, clear=False)
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



