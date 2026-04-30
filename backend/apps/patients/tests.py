from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from io import StringIO
from apps.patients.models import PatientProfile, HealthReading

User = get_user_model()


class PatientProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='patient1', password='pass', role='PATIENT')
        self.profile = PatientProfile.objects.create(user=self.user, blood_type='O+')

    def test_profile_creation(self):
        self.assertEqual(self.profile.blood_type, 'O+')
        self.assertEqual(str(self.profile), f'Patient: {self.user.username}')

    def test_reading_creation(self):
        reading = HealthReading.objects.create(
            patient=self.profile,
            heart_rate=72,
            blood_pressure_sys=120,
            blood_pressure_dia=80,
        )
        self.assertEqual(reading.heart_rate, 72)


class CSVUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='pat1', password='pass', role='PATIENT', is_approved=True)
        self.profile = PatientProfile.objects.create(user=self.user)
        self.client.force_authenticate(user=self.user)

    def test_csv_upload_creates_readings(self):
        csv_content = (
            "timestamp,heart_rate,blood_pressure_sys,blood_pressure_dia,temperature\n"
            "2024-01-01T00:00:00Z,70,120,80,36.6\n"
            "2024-01-02T00:00:00Z,72,118,78,36.7\n"
        )
        import tempfile
        from django.core.files.base import ContentFile
        temp = tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w')
        temp.write(csv_content)
        temp.close()
        with open(temp.name, 'rb') as f:
            res = self.client.post(f'/api/v1/patients/{self.profile.id}/readings/upload/', {'file': f}, format='multipart')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(HealthReading.objects.filter(patient=self.profile).count(), 2)

    def test_patient_cannot_upload_readings_for_another_patient(self):
        other_user = User.objects.create_user(username='pat2', password='pass', role='PATIENT', is_approved=True)
        other_profile = PatientProfile.objects.create(user=other_user)
        import tempfile
        temp = tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w')
        temp.write("heart_rate\n70\n")
        temp.close()
        with open(temp.name, 'rb') as f:
            res = self.client.post(f'/api/v1/patients/{other_profile.id}/readings/upload/', {'file': f}, format='multipart')
        self.assertEqual(res.status_code, 403)
