from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.emergency.models import EmergencyPatient
from apps.patients.models import PatientProfile

User = get_user_model()


class EmergencyPatientTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='emer1', password='pass', role='EMERGENCY')

    def test_emergency_creation(self):
        ep = EmergencyPatient.objects.create(
            first_name='Han',
            last_name='Solo',
            condition_notes='Fever and fatigue',
            input_by=self.user
        )
        self.assertFalse(ep.converted_to_patient)
        self.assertEqual(str(ep), 'Emergency: Han Solo')


class EmergencyConvertTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.emer_user = User.objects.create_user(username='emer1', password='pass', role='EMERGENCY', is_approved=True)
        self.client.force_authenticate(user=self.emer_user)

    def test_emergency_convert_creates_patient_profile(self):
        ep = EmergencyPatient.objects.create(
            first_name='Leia',
            last_name='Organa',
            condition_notes='High fever',
            input_by=self.emer_user
        )
        res = self.client.post(f'/api/v1/emergency/{ep.id}/convert/')
        self.assertEqual(res.status_code, 201)
        self.assertTrue(User.objects.filter(username__startswith='leia_organa').exists() or User.objects.filter(first_name='Leia').exists())
        ep.refresh_from_db()
        self.assertTrue(ep.converted_to_patient)
