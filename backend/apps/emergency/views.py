from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from apps.patients.models import PatientProfile
from apps.core.permissions import IsAdmin, IsEmergency
from .models import EmergencyPatient
from .serializers import EmergencyPatientSerializer


class EmergencyPatientListCreateView(generics.ListCreateAPIView):
    queryset = EmergencyPatient.objects.all()
    serializer_class = EmergencyPatientSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(input_by=self.request.user)


class EmergencyPatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = EmergencyPatient.objects.all()
    serializer_class = EmergencyPatientSerializer
    permission_classes = (permissions.IsAuthenticated,)


class ConvertEmergencyPatientView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, pk):
        emergency = get_object_or_404(EmergencyPatient, pk=pk)
        if emergency.converted_to_patient:
            return Response({'detail': 'Already converted.'}, status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username=f"emerg_{emergency.id}_{emergency.last_name.lower()}",
            first_name=emergency.first_name,
            last_name=emergency.last_name,
            role='PATIENT',
            password='changeme123'
        )
        PatientProfile.objects.create(user=user)
        emergency.converted_to_patient = True
        emergency.save()
        return Response({'detail': 'Converted to patient.', 'user_id': user.id}, status=status.HTTP_201_CREATED)
