from django.db import models
from django.conf import settings


class Department(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    ORDER_TYPES = [
        ('CT_SCAN', 'CT Scan'),
        ('PET_SCAN', 'PET Scan'),
        ('MRI', 'MRI'),
        ('BLOODWORK', 'Bloodwork'),
        ('X_RAY', 'X-Ray'),
        ('ULTRASOUND', 'Ultrasound'),
        ('OTHER', 'Other'),
    ]
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]
    patient = models.ForeignKey('patients.PatientProfile', on_delete=models.CASCADE, related_name='orders')
    doctor = models.ForeignKey('doctors.DoctorProfile', on_delete=models.CASCADE, related_name='orders')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    notes = models.TextField(blank=True)
    result_notes = models.TextField(blank=True)
    result_file = models.FileField(upload_to='order_results/%Y/%m/%d/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.order_type} for {self.patient.user.username}"
