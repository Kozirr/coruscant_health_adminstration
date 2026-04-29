from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)

    class Meta:
        model = Document
        fields = ('id', 'uploaded_by', 'uploaded_by_name', 'file', 'original_filename', 'encryption_iv', 'document_type', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_by', 'original_filename', 'encryption_iv', 'uploaded_at')
