from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import Department, Order
from .serializers import DepartmentSerializer, OrderSerializer


class DepartmentListCreateView(generics.ListCreateAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        if self.request.user.role != 'ADMIN':
            raise PermissionDenied('Only administrators can create departments.')
        serializer.save()


class OrderListCreateView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role in ('ADMIN', 'DEPARTMENT'):
            qs = Order.objects.all()
        elif user.role == 'DOCTOR':
            qs = Order.objects.filter(doctor__user=user)
        elif user.role == 'PATIENT':
            qs = Order.objects.filter(patient__user=user)
        else:
            qs = Order.objects.none()
        patient_id = self.request.query_params.get('patient')
        status_filter = self.request.query_params.get('status')
        if patient_id:
            qs = qs.filter(patient_id=patient_id)
        if status_filter:
            qs = qs.filter(status=status_filter.upper())
        return qs

    def perform_create(self, serializer):
        if self.request.user.role != 'DOCTOR':
            raise PermissionDenied('Only doctors can create service orders.')
        from apps.doctors.models import DoctorProfile
        doctor = get_object_or_404(DoctorProfile, user=self.request.user)
        serializer.save(doctor=doctor)


class OrderDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        if user.role in ('ADMIN', 'DEPARTMENT'):
            return Order.objects.all()
        if user.role == 'DOCTOR':
            return Order.objects.filter(doctor__user=user)
        if user.role == 'PATIENT':
            return Order.objects.filter(patient__user=user)
        return Order.objects.none()

    def perform_update(self, serializer):
        if self.request.user.role == 'ADMIN':
            serializer.save()
            return
        if self.request.user.role == 'DOCTOR' and serializer.instance.doctor.user == self.request.user:
            serializer.save()
            return
        raise PermissionDenied('Only administrators and ordering doctors can update service orders.')

    def perform_destroy(self, instance):
        if self.request.user.role == 'ADMIN':
            instance.delete()
            return
        if self.request.user.role == 'DOCTOR' and instance.doctor.user == self.request.user:
            instance.delete()
            return
        raise PermissionDenied('Only administrators and ordering doctors can delete service orders.')


class OrderExecuteView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, pk):
        if request.user.role not in ('ADMIN', 'DEPARTMENT'):
            raise PermissionDenied('Only departments can execute service orders.')
        order = get_object_or_404(Order, pk=pk)
        order.status = request.data.get('status', 'IN_PROGRESS')
        if 'result_notes' in request.data:
            order.result_notes = request.data['result_notes']
        if 'result_file' in request.FILES:
            order.result_file = request.FILES['result_file']
        order.save()
        return Response(OrderSerializer(order).data)
