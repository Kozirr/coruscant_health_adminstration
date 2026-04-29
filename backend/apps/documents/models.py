from django.db import models
from django.conf import settings


class Document(models.Model):
    DOC_TYPES = [
        ('IDENTITY', 'Identity'),
        ('MEDICAL_RECORD', 'Medical Record'),
        ('RESULT', 'Result'),
        ('PRESCRIPTION', 'Prescription'),
        ('OTHER', 'Other'),
    ]
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='encrypted_docs/%Y/%m/%d/')
    original_filename = models.CharField(max_length=255)
    encryption_iv = models.CharField(max_length=24)
    document_type = models.CharField(max_length=20, choices=DOC_TYPES, default='OTHER')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"Document {self.original_filename} by {self.uploaded_by.username}"
