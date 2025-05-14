from django.contrib.auth.models import User
from .models import Score, Number, Game
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = Game
        fields = ["id","user", "created_at"]
        read_only_fields = ["user"]
        
    def create(self, validated_data):
        user = self.context['request'].user
        game = Game.objects.create(user=user, **validated_data)
        Score.objects.create(game=game, score_value=1)  # auto create their score
        Number.objects.create(game=game, integer=1, quantity=1)
        return game


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = ["id", "user", "score_value", "increment", "time_increment", "purchased_buttons", "last_updated"]
        extra_kwargs = {"user": {"read_only": True}}


class NumberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Number
        fields = ["id", "integer", "quantity", "last_purchase", "user"]
        extra_kwargs = {"user": {"read_only": True}}
