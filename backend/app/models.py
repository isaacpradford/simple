from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# class Game(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="games")
#     created_at = models.DateTimeField(auto_now_add=True)
    

class Score(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="score")
    score_value = models.DecimalField(max_digits=500, decimal_places=0, default=1)
    increment = models.DecimalField(max_digits=500, decimal_places=0, default=1)
    
    time_increment = models.IntegerField(default=15) # starts the user every 30s
    purchased_buttons = models.IntegerField(default=1)
    last_updated = models.DateTimeField(default=timezone.now)

class Number(models.Model):
    integer = models.DecimalField(max_digits=500, decimal_places=0, default=0)
    quantity = models.DecimalField(max_digits=500, decimal_places=0, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="numbers")
    last_purchase = models.DateTimeField(auto_now=True)
