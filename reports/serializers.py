from rest_framework import serializers
from .models import (
    Report,
    Quotation,
)


class ReportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Report
        fields = (
            'id',
            'title',
            'description',
            'file',
            'is_public',
            'created_at',
        )


class QuotationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quotation
        fields = (
            'id',
            'name',
            'email',
            'message',
            'created_at',
        )

        read_only_fields = (
            'id',
            'created_at',
        )
