from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from .models import Monitor


class MonitorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Monitor
        fields = ['id', 'timeout', 'alert_email', 'status', 'expires_at', 'last_heartbeat', 'created_at']
        read_only_fields = fields


class MonitorCreateSerializer(serializers.ModelSerializer):
    id = serializers.CharField(max_length=100, validators=[])

    class Meta:
        model = Monitor
        fields = ['id', 'timeout', 'alert_email']

    def validate_id(self, value):
        if Monitor.objects.filter(id=value).exists():
            raise serializers.ValidationError(f"A monitor with ID '{value}' already exists.")
        return value

    def validate_timeout(self, value):
        if value <= 0:
            raise serializers.ValidationError("Timeout must be a positive number of seconds.")
        return value

    def create(self, validated_data):
        validated_data['expires_at'] = timezone.now() + timedelta(seconds=validated_data['timeout'])
        return super().create(validated_data)
