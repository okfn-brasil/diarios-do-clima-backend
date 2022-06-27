from rest_framework import serializers
from .models import Alert


class AlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = (
            'id',
            'user',
            'query_string',
            'territory_id',
            'sub_themes',
            'gov_entities',
            'created_at',
            'edited_at',
        )
