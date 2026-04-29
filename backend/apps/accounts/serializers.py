from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_approved', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'first_name', 'last_name', 'role', 'phone')

    def create(self, validated_data):
        role = validated_data.get('role', 'PATIENT')
        if role in ('PATIENT', 'DOCTOR'):
            validated_data['is_approved'] = False
        user = User.objects.create_user(**validated_data)
        return user
