from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
        ('ADMIN', 'Administrator'),
        ('EMERGENCY', 'Emergency Services'),
        ('DEPARTMENT', 'Department'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='PATIENT')
    phone = models.CharField(max_length=20, blank=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
