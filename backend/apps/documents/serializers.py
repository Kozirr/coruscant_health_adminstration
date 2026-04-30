from rest_framework import serializers
from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    uploaded_by_name = serializers.CharField(source='uploaded_by.username', read_only=True)
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ('id', 'uploaded_by', 'uploaded_by_name', 'file', 'download_url', 'original_filename', 'encryption_iv', 'document_type', 'uploaded_at')
        read_only_fields = ('id', 'uploaded_by', 'original_filename', 'encryption_iv', 'uploaded_at')

    def create(self, validated_data):
        validated_data.pop('file', None)
        return super().create(validated_data)

    def get_download_url(self, obj):
        return f'/api/v1/documents/{obj.id}/download/'
