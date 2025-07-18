from rest_framework import serializers
from .models import Queue, Token

class TokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Token
        fields = ['id', 'queue', 'number', 'status', 'created_at', 'updated_at']

class QueueSerializer(serializers.ModelSerializer):
    tokens = TokenSerializer(many=True, read_only=True)
    manager = serializers.PrimaryKeyRelatedField(read_only=True)
    class Meta:
        model = Queue
        fields = ['id', 'name', 'created_at', 'manager', 'tokens'] 