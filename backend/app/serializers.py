from django.contrib.auth.models import User
from .models import Score, Number
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Score.objects.create(user=user, score_value=0)  # auto create their score
        Number.objects.create(user=user, integer=1, quantity=1)
        return user


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ["id", "user", "increment", "score_value", "last_updated"]
        extra_kwargs = {"user": {"read_only": True}}


class NumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Number
        fields = ["id", "integer", "quantity", "last_purchase", "user"]
        extra_kwargs = {"user": {"read_only": True}}
