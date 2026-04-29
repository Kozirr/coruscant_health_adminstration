from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.documents.utils import encrypt_file, decrypt_file
from apps.documents.models import Document

User = get_user_model()


class EncryptionTests(TestCase):
    def test_encrypt_decrypt_roundtrip(self):
        original = b"Galactic Republic Health Data"
        ciphertext, iv = encrypt_file(original)
        decrypted = decrypt_file(ciphertext, iv)
        self.assertEqual(original, decrypted)


@override_settings(DEFAULT_FILE_STORAGE='django.core.files.storage.FileSystemStorage')
class DocumentAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.patient = User.objects.create_user(username='pat1', password='pass', role='PATIENT', is_approved=True)
        self.other = User.objects.create_user(username='other1', password='pass', role='PATIENT', is_approved=True)

    def test_patient_can_upload_document(self):
        self.client.force_authenticate(user=self.patient)
        import tempfile
        temp = tempfile.NamedTemporaryFile(suffix='.txt', delete=False, mode='w')
        temp.write('health record')
        temp.close()
        with open(temp.name, 'rb') as f:
            res = self.client.post('/api/v1/documents/', {'file': f, 'document_type': 'MEDICAL_RECORD'}, format='multipart')
        self.assertEqual(res.status_code, 201)
        self.assertEqual(Document.objects.filter(uploaded_by=self.patient).count(), 1)

    def test_download_decrypts_correctly(self):
        from django.core.files.base import ContentFile
        from django.core.files.uploadedfile import SimpleUploadedFile
        plaintext = b"secret medical data"
        ciphertext, iv = encrypt_file(plaintext)
        doc = Document.objects.create(
            uploaded_by=self.patient,
            original_filename='test.txt',
            encryption_iv=iv,
            document_type='MEDICAL_RECORD',
        )
        doc.file.save('test.txt', ContentFile(ciphertext))
        self.client.force_authenticate(user=self.patient)
        res = self.client.get(f'/api/v1/documents/{doc.id}/download/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, plaintext)

    def test_patient_cannot_see_others_documents(self):
        from django.core.files.base import ContentFile
        ciphertext, iv = encrypt_file(b'data')
        doc = Document.objects.create(
            uploaded_by=self.other,
            original_filename='other.txt',
            encryption_iv=iv,
            document_type='OTHER',
        )
        doc.file.save('other.txt', ContentFile(ciphertext))
        self.client.force_authenticate(user=self.patient)
        res = self.client.get('/api/v1/documents/')
        self.assertEqual(res.status_code, 200)
        results = res.data.get('results', res.data)
        ids = [d['id'] for d in results]
        self.assertNotIn(doc.id, ids)
