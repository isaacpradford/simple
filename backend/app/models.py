from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

class Game(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
    created_at = models.DateTimeField(auto_now_add=True)
    time_elapsed = models.IntegerField(default=1)

class Score(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE, related_name="score")
    score_value = models.DecimalField(max_digits=500, decimal_places=0, default=1)
    increment = models.DecimalField(max_digits=500, decimal_places=0, default=1)
    
    time_increment = models.IntegerField(default=15) # starts the game with incrementing every 15s
    purchased_buttons = models.IntegerField(default=1)
    last_updated = models.DateTimeField(default=timezone.now)

class Number(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="numbers")
    integer = models.DecimalField(max_digits=500, decimal_places=0, default=0)
    quantity = models.DecimalField(max_digits=500, decimal_places=0, default=1)
    last_purchase = models.DateTimeField(auto_now=True)
