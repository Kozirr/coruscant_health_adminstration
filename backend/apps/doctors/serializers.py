from rest_framework import serializers
from .models import DoctorProfile, Prescription


class PrescriptionSerializer(serializers.ModelSerializer):
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)

    class Meta:
        model = Prescription
        fields = '__all__'
        read_only_fields = ('id', 'doctor', 'created_at', 'updated_at')


class DoctorProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    prescriptions = PrescriptionSerializer(many=True, read_only=True)

    class Meta:
        model = DoctorProfile
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
