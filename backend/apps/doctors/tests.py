from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.doctors.models import DoctorProfile, Prescription
from apps.patients.models import PatientProfile

User = get_user_model()


class DoctorProfileTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='doc1', password='pass', role='DOCTOR')
        self.profile = DoctorProfile.objects.create(user=self.user, specialization='Cardiology')

    def test_doctor_creation(self):
        self.assertEqual(self.profile.specialization, 'Cardiology')

    def test_prescription_creation(self):
        patient_user = User.objects.create_user(username='pat1', password='pass', role='PATIENT')
        patient = PatientProfile.objects.create(user=patient_user)
        prescription = Prescription.objects.create(
            patient=patient,
            doctor=self.profile,
            title='Brainworm Rot Treatment',
            content='Administer Type-A vaccine daily.'
        )
        self.assertIn('Brainworm', prescription.title)


class PrescriptionAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.doctor_user = User.objects.create_user(username='doc1', password='pass', role='DOCTOR', is_approved=True)
        self.doctor = DoctorProfile.objects.create(user=self.doctor_user)
        self.patient_user = User.objects.create_user(username='pat1', password='pass', role='PATIENT', is_approved=True)
        self.patient = PatientProfile.objects.create(user=self.patient_user)

    def test_doctor_can_create_prescription(self):
        self.client.force_authenticate(user=self.doctor_user)
        res = self.client.post('/api/v1/doctors/prescriptions/', {
            'patient': self.patient.id,
            'title': 'Rx',
            'content': 'Take two pills',
        })
        self.assertEqual(res.status_code, 201)

    def test_patient_cannot_create_prescription(self):
        self.client.force_authenticate(user=self.patient_user)
        res = self.client.post('/api/v1/doctors/prescriptions/', {
            'patient': self.patient.id,
            'title': 'Rx',
            'content': 'Take two pills',
        })
        self.assertEqual(res.status_code, 403)

    def test_patient_can_read_own_prescriptions(self):
        Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            title='Rx',
            content='Hydrate and rest',
        )
        self.client.force_authenticate(user=self.patient_user)
        res = self.client.get(f'/api/v1/doctors/prescriptions/?patient={self.patient.id}')
        self.assertEqual(res.status_code, 200)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Rx')

    def test_patient_cannot_update_own_prescription(self):
        prescription = Prescription.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            title='Rx',
            content='Hydrate and rest',
        )
        self.client.force_authenticate(user=self.patient_user)
        res = self.client.patch(
            f'/api/v1/doctors/prescriptions/{prescription.id}/',
            {'content': 'Changed by patient'},
        )
        self.assertEqual(res.status_code, 403)
