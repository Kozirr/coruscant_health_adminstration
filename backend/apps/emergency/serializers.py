from rest_framework import serializers
from .models import EmergencyPatient


class EmergencyPatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyPatient
        fields = '__all__'
        read_only_fields = ('id', 'arrival_time')
