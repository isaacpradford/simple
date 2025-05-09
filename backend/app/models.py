from django.db import models
from django.contrib.auth.models import User


class Score(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="score")
    score_value = models.DecimalField(max_digits=500, decimal_places=0, default=0)
    increment = models.DecimalField(max_digits=500, decimal_places=0, default=1)
    time_stamp = models.DateTimeField(auto_now=True)


class Number(models.Model):
    integer = models.DecimalField(max_digits=500, decimal_places=0, default=0)
    quantity = models.DecimalField(max_digits=500, decimal_places=0, default=0)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="numbers")
    last_purchase = models.DateTimeField(auto_now=True)
