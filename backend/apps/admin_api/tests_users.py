from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import AuthSettings, TrustedDevice, User
from apps.accounts.services.devices import trust_device


class AdminUserManagementTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.owner = User.objects.create_superuser('09150000001', 'secret')
        self.staff = User.objects.create_user('09150000002', 'secret', is_staff=True)
        self.customer = User.objects.create_user('09150000003', 'secret')

    def as_(self, user):
        self.client.force_authenticate(user)
        return self.client

    # ── creating ─────────────────────────────────────────────────────────────

    def test_staff_can_create_a_customer(self):
        res = self.as_(self.staff).post('/api/admin/users/', {
            'phone': '09150000010', 'password': 'secret', 'first_name': 'سارا',
        }, format='json')
        self.assertEqual(res.status_code, 201)
        self.assertTrue(User.objects.get(phone='09150000010').check_password('secret'))

    def test_staff_cannot_create_an_admin(self):
        res = self.as_(self.staff).post('/api/admin/users/', {
            'phone': '09150000011', 'password': 'secret', 'is_staff': True,
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertFalse(User.objects.filter(phone='09150000011').exists())

    def test_duplicate_phone_is_rejected_with_a_field_error(self):
        res = self.as_(self.owner).post('/api/admin/users/', {
            'phone': '09150000003', 'password': 'secret',
        }, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertIn('phone', res.data)

    # ── passwords ────────────────────────────────────────────────────────────

    def test_staff_can_reset_a_customer_password(self):
        res = self.as_(self.staff).post(
            f'/api/admin/users/{self.customer.id}/set-password/',
            {'password': 'brandnew'}, format='json')
        self.assertEqual(res.status_code, 200)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.check_password('brandnew'))

    def test_password_reset_signs_the_customer_out_everywhere(self):
        trust_device(self.customer)
        before = self.customer.session_epoch
        self.as_(self.staff).post(
            f'/api/admin/users/{self.customer.id}/set-password/',
            {'password': 'brandnew'}, format='json')
        self.customer.refresh_from_db()
        self.assertEqual(self.customer.session_epoch, before + 1)
        self.assertEqual(self.customer.trusted_devices.filter(revoked_at__isnull=True).count(), 0)

    def test_staff_cannot_reset_another_admins_password(self):
        other_admin = User.objects.create_user('09150000004', 'secret', is_staff=True)
        res = self.as_(self.staff).post(
            f'/api/admin/users/{other_admin.id}/set-password/',
            {'password': 'brandnew'}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_superuser_can_reset_an_admins_password(self):
        res = self.as_(self.owner).post(
            f'/api/admin/users/{self.staff.id}/set-password/',
            {'password': 'brandnew'}, format='json')
        self.assertEqual(res.status_code, 200)

    def test_short_password_is_rejected(self):
        res = self.as_(self.owner).post(
            f'/api/admin/users/{self.customer.id}/set-password/',
            {'password': 'ab'}, format='json')
        self.assertEqual(res.status_code, 400)

    # ── roles ────────────────────────────────────────────────────────────────

    def test_superuser_can_promote_a_customer_to_admin(self):
        res = self.as_(self.owner).post(
            f'/api/admin/users/{self.customer.id}/roles/',
            {'is_staff': True}, format='json')
        self.assertEqual(res.status_code, 200)
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_staff)
        self.assertFalse(self.customer.is_superuser)

    def test_granting_superuser_also_grants_staff(self):
        self.as_(self.owner).post(
            f'/api/admin/users/{self.customer.id}/roles/',
            {'is_superuser': True}, format='json')
        self.customer.refresh_from_db()
        self.assertTrue(self.customer.is_staff and self.customer.is_superuser)

    def test_staff_cannot_promote_anyone(self):
        res = self.as_(self.staff).post(
            f'/api/admin/users/{self.customer.id}/roles/',
            {'is_staff': True}, format='json')
        self.assertEqual(res.status_code, 403)

    def test_a_plain_patch_cannot_mint_an_admin(self):
        self.as_(self.staff).patch(
            f'/api/admin/users/{self.customer.id}/',
            {'is_staff': True, 'is_superuser': True}, format='json')
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_staff)

    def test_cannot_demote_yourself(self):
        second = User.objects.create_superuser('09150000005', 'secret')
        res = self.as_(self.owner).post(
            f'/api/admin/users/{self.owner.id}/roles/',
            {'is_superuser': False}, format='json')
        self.assertEqual(res.status_code, 400)
        self.assertTrue(second.is_superuser)

    def test_cannot_remove_the_last_superuser(self):
        second = User.objects.create_superuser('09150000005', 'secret')
        res = self.as_(second).post(
            f'/api/admin/users/{self.owner.id}/roles/',
            {'is_superuser': False}, format='json')
        self.assertEqual(res.status_code, 200)

        third = User.objects.create_superuser('09150000006', 'secret')
        User.objects.filter(pk=third.pk).update(is_superuser=False)
        res = self.as_(self.staff)  # staff can't, so use the remaining superuser
        self.client.force_authenticate(second)
        res = self.client.post(
            f'/api/admin/users/{second.id}/roles/', {'is_superuser': False}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_demoting_an_admin_invalidates_their_dashboard_session(self):
        before = self.staff.session_epoch
        self.as_(self.owner).post(
            f'/api/admin/users/{self.staff.id}/roles/', {'is_staff': False}, format='json')
        self.staff.refresh_from_db()
        self.assertEqual(self.staff.session_epoch, before + 1)

    # ── activation, sessions, devices ────────────────────────────────────────

    def test_deactivating_revokes_sessions(self):
        before = self.customer.session_epoch
        res = self.as_(self.staff).patch(
            f'/api/admin/users/{self.customer.id}/', {'is_active': False}, format='json')
        self.assertEqual(res.status_code, 200)
        self.customer.refresh_from_db()
        self.assertFalse(self.customer.is_active)
        self.assertEqual(self.customer.session_epoch, before + 1)

    def test_cannot_deactivate_yourself(self):
        res = self.as_(self.owner).patch(
            f'/api/admin/users/{self.owner.id}/', {'is_active': False}, format='json')
        self.assertEqual(res.status_code, 400)

    def test_revoke_sessions_endpoint_drops_remembered_devices(self):
        trust_device(self.customer)
        res = self.as_(self.staff).post(
            f'/api/admin/users/{self.customer.id}/revoke-sessions/', {}, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(TrustedDevice.objects.filter(revoked_at__isnull=True).count(), 0)

    def test_single_device_can_be_revoked(self):
        kept = trust_device(self.customer)['device']
        dropped = trust_device(self.customer)['device']
        res = self.as_(self.staff).delete(
            f'/api/admin/users/{self.customer.id}/devices/{dropped.id}/')
        self.assertEqual(res.status_code, 204)
        self.assertIsNone(TrustedDevice.objects.get(id=kept.id).revoked_at)
        self.assertIsNotNone(TrustedDevice.objects.get(id=dropped.id).revoked_at)

    # ── deletion ─────────────────────────────────────────────────────────────

    def test_staff_cannot_delete(self):
        res = self.as_(self.staff).delete(f'/api/admin/users/{self.customer.id}/')
        self.assertEqual(res.status_code, 400)
        self.assertTrue(User.objects.filter(pk=self.customer.pk).exists())

    def test_superuser_can_delete_a_customer_without_orders(self):
        res = self.as_(self.owner).delete(f'/api/admin/users/{self.customer.id}/')
        self.assertEqual(res.status_code, 204)
        self.assertFalse(User.objects.filter(pk=self.customer.pk).exists())

    def test_cannot_delete_yourself(self):
        User.objects.create_superuser('09150000005', 'secret')
        res = self.as_(self.owner).delete(f'/api/admin/users/{self.owner.id}/')
        self.assertEqual(res.status_code, 400)

    # ── privilege escalation via settings ────────────────────────────────────

    def test_staff_cannot_add_themselves_to_the_admin_phone_list(self):
        before = AuthSettings.get_settings().admin_phones
        res = self.as_(self.staff).patch('/api/admin/auth/settings/', {
            'admin_phones': ['09150000002'],
        }, format='json')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data['admin_phones'], before)

    def test_superuser_can_edit_the_admin_phone_list(self):
        res = self.as_(self.owner).patch('/api/admin/auth/settings/', {
            'admin_phones': ['09150000002'],
        }, format='json')
        self.assertEqual(res.data['admin_phones'], ['09150000002'])
