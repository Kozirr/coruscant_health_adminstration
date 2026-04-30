from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.orders.models import Department, Order
from apps.patients.models import PatientProfile
from apps.doctors.models import DoctorProfile

User = get_user_model()


class OrderTests(TestCase):
    def setUp(self):
        self.patient_user = User.objects.create_user(username='pat1', password='pass', role='PATIENT')
        self.patient = PatientProfile.objects.create(user=self.patient_user)
        self.doctor_user = User.objects.create_user(username='doc1', password='pass', role='DOCTOR')
        self.doctor = DoctorProfile.objects.create(user=self.doctor_user)
        self.dept = Department.objects.create(name='Radiology')

    def test_order_creation(self):
        order = Order.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.dept,
            order_type='CT_SCAN',
            status='PENDING'
        )
        self.assertEqual(order.status, 'PENDING')
        self.assertEqual(str(order), 'CT_SCAN for pat1')


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class OrderExecuteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient_user = User.objects.create_user(username='pat1', password='pass', role='PATIENT')
        self.patient = PatientProfile.objects.create(user=self.patient_user)
        self.doctor_user = User.objects.create_user(username='doc1', password='pass', role='DOCTOR')
        self.doctor = DoctorProfile.objects.create(user=self.doctor_user)
        self.dept = Department.objects.create(name='Radiology')
        self.order = Order.objects.create(
            patient=self.patient,
            doctor=self.doctor,
            department=self.dept,
            order_type='CT_SCAN',
            status='IN_PROGRESS'
        )
        self.dept_user = User.objects.create_user(username='dept1', password='pass', role='DEPARTMENT', is_approved=True)

    def test_department_can_execute_order_with_file(self):
        self.client.force_authenticate(user=self.dept_user)
        import tempfile
        temp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w')
        temp.write('scan results')
        temp.close()
        with open(temp.name, 'rb') as f:
            res = self.client.patch(
                f'/api/v1/orders/{self.order.id}/execute/',
                {'status': 'COMPLETED', 'result_notes': 'All clear', 'result_file': f},
                format='multipart'
            )
        self.assertEqual(res.status_code, 200)
        self.order.refresh_from_db()
        self.assertEqual(self.order.status, 'COMPLETED')
        self.assertEqual(self.order.result_notes, 'All clear')
        self.assertTrue(self.order.result_file)

    def test_order_filter_by_status(self):
        self.client.force_authenticate(user=self.doctor_user)
        Order.objects.create(patient=self.patient, doctor=self.doctor, department=self.dept, order_type='MRI', status='PENDING')
        res = self.client.get('/api/v1/orders/?status=PENDING')
        self.assertEqual(res.status_code, 200)
        results = res.data.get('results', res.data)
        self.assertEqual(len(results), 1)

    def test_patient_cannot_execute_order(self):
        self.client.force_authenticate(user=self.patient_user)
        res = self.client.patch(
            f'/api/v1/orders/{self.order.id}/execute/',
            {'status': 'COMPLETED'},
        )
        self.assertEqual(res.status_code, 403)

    def test_patient_cannot_update_order_directly(self):
        self.client.force_authenticate(user=self.patient_user)
        res = self.client.patch(
            f'/api/v1/orders/{self.order.id}/',
            {'status': 'COMPLETED'},
        )
        self.assertEqual(res.status_code, 403)
