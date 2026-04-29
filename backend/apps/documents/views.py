import os
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Document
from .serializers import DocumentSerializer
from .utils import encrypt_file, decrypt_file


class DocumentListCreateView(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        qs = Document.objects.all()
        if self.request.user.role == 'PATIENT':
            qs = qs.filter(uploaded_by=self.request.user)
        return qs

    def perform_create(self, serializer):
        file_obj = self.request.FILES.get('file')
        if not file_obj:
            raise serializers.ValidationError({'file': 'This field is required.'})
        file_bytes = file_obj.read()
        ciphertext, iv = encrypt_file(file_bytes)

        import tempfile
        from django.core.files.base import File
        temp = tempfile.NamedTemporaryFile(delete=False)
        temp.write(ciphertext)
        temp.close()

        document = serializer.save(
            uploaded_by=self.request.user,
            original_filename=file_obj.name,
            encryption_iv=iv,
        )
        with open(temp.name, 'rb') as f:
            document.file.save(file_obj.name, File(f), save=True)
        os.unlink(temp.name)


class DocumentDownloadView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, pk):
        doc = get_object_or_404(Document, pk=pk)
        if request.user.role == 'PATIENT' and doc.uploaded_by != request.user:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        with doc.file.open('rb') as f:
            ciphertext = f.read()
        plaintext = decrypt_file(ciphertext, doc.encryption_iv)

        response = HttpResponse(plaintext, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{doc.original_filename}"'
        return response
