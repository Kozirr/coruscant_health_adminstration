from io import StringIO
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from rest_framework.test import APIClient

User = get_user_model()


class UserModelTests(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='testuser', password='testpass123', role='PATIENT')
        self.assertEqual(user.role, 'PATIENT')
        self.assertTrue(user.check_password('testpass123'))

    def test_create_doctor(self):
        user = User.objects.create_user(username='doc1', password='pass', role='DOCTOR')
        self.assertEqual(user.role, 'DOCTOR')


class HealthOfficialCommandTests(TestCase):
    def test_command_with_two_args(self):
        out = StringIO()
        err = StringIO()
        call_command('health_official', 'John', 'Doe', stdout=out, stderr=err)
        self.assertIn('Coruscant Health Official: John Doe', out.getvalue())

    def test_command_with_no_args(self):
        out = StringIO()
        err = StringIO()
        call_command('health_official', stdout=out, stderr=err)
        self.assertIn('Usage', err.getvalue())

    def test_command_with_one_arg(self):
        out = StringIO()
        err = StringIO()
        call_command('health_official', 'John', stdout=out, stderr=err)
        self.assertIn('Usage', err.getvalue())


class ApprovalWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(username='admin1', password='pass', role='ADMIN')
        self.admin.is_approved = True
        self.admin.save()

    def test_register_patient_sets_pending(self):
        res = self.client.post('/api/v1/auth/register/', {
            'username': 'patient1',
            'password': 'testpass123',
            'email': 'p@example.com',
            'first_name': 'Pat',
            'last_name': 'One',
            'role': 'PATIENT',
        })
        self.assertEqual(res.status_code, 201)
        self.assertFalse(res.data['user']['is_approved'])

    def test_register_admin_is_approved(self):
        res = self.client.post('/api/v1/auth/register/', {
            'username': 'admin2',
            'password': 'testpass123',
            'email': 'a@example.com',
            'first_name': 'Ad',
            'last_name': 'Min',
            'role': 'ADMIN',
        })
        self.assertEqual(res.status_code, 201)
        self.assertTrue(res.data['user']['is_approved'])

    def test_unapproved_patient_cannot_login(self):
        User.objects.create_user(username='unapproved', password='pass', role='PATIENT', is_approved=False)
        res = self.client.post('/api/v1/auth/login/', {'username': 'unapproved', 'password': 'pass'})
        self.assertEqual(res.status_code, 400)
        self.assertIn('pending', str(res.data).lower())

    def test_admin_can_approve_user(self):
        pending = User.objects.create_user(username='pending1', password='pass', role='PATIENT', is_approved=False)
        self.client.force_authenticate(user=self.admin)
        res = self.client.post(f'/api/v1/auth/users/{pending.id}/approve/')
        self.assertEqual(res.status_code, 200)
        pending.refresh_from_db()
        self.assertTrue(pending.is_approved)

    def test_non_admin_cannot_list_users(self):
        patient = User.objects.create_user(username='pat1', password='pass', role='PATIENT', is_approved=True)
        self.client.force_authenticate(user=patient)
        res = self.client.get('/api/v1/auth/users/')
        self.assertEqual(res.status_code, 403)
