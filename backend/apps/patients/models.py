from django.db import models
from django.conf import settings


class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(null=True, blank=True)
    blood_type = models.CharField(max_length=10, blank=True)
    allergies = models.TextField(blank=True)
    address = models.TextField(blank=True)
    device_id = models.CharField(max_length=100, blank=True, help_text='Simulated body device ID')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name() or self.user.username}"


class HealthReading(models.Model):
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(auto_now_add=True)
    heart_rate = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_sys = models.PositiveIntegerField(null=True, blank=True)
    blood_pressure_dia = models.PositiveIntegerField(null=True, blank=True)
    oxygen_saturation = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"Reading {self.id} for {self.patient.user.username} at {self.timestamp}"
