from django.db import models
from django.conf import settings


class EmergencyPatient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    condition_notes = models.TextField(blank=True)
    arrival_time = models.DateTimeField(auto_now_add=True)
    input_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    converted_to_patient = models.BooleanField(default=False)

    class Meta:
        ordering = ['-arrival_time']

    def __str__(self):
        return f"Emergency: {self.first_name} {self.last_name}"
