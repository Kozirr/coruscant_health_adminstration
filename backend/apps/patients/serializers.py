from rest_framework import serializers
from .models import PatientProfile, HealthReading


class HealthReadingSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthReading
        fields = '__all__'
        read_only_fields = ('id', 'timestamp')


class PatientProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    readings = HealthReadingSerializer(many=True, read_only=True)

    class Meta:
        model = PatientProfile
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')
