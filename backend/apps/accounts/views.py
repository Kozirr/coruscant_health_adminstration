from rest_framework import generics, permissions, status, serializers
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from apps.core.permissions import IsAdmin
from .serializers import RegisterSerializer, UserSerializer

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        if user.role in ('PATIENT', 'DOCTOR') and not user.is_approved:
            raise serializers.ValidationError(
                {'detail': 'Your account is pending administrator approval.'}
            )
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserApproveView(APIView):
    permission_classes = (IsAdmin,)

    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        user.is_approved = True
        user.save()
        if user.role == 'PATIENT':
            from apps.patients.models import PatientProfile
            PatientProfile.objects.get_or_create(user=user)
        elif user.role == 'DOCTOR':
            from apps.doctors.models import DoctorProfile
            DoctorProfile.objects.get_or_create(user=user)
        return Response({'message': f'User {user.username} approved.'})


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Registration successful.'
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdmin,)

    def get_queryset(self):
        qs = super().get_queryset()
        role = self.request.query_params.get('role')
        if role:
            qs = qs.filter(role=role.upper())
        return qs
