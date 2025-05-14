from django import forms
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Number, Game

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta:
        model = User
        fields = ["username", "password"]
        

class UserRegistrationForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)
    class Meta: 
        model = User
        fields = ["username", "password"]

class PurchaseNumberForm(forms.Form):
    def __init__(self, *args, game_id=None, **kwargs):
        self.game = get_object_or_404(Game, id=game_id)
        self.score = self.game.score
        super().__init__(*args, **kwargs)
        self.next_integer = self.calculate_next_integer()
        
    def calculate_next_integer(self):
        game_numbers = self.game.numbers.all()
        if game_numbers.exists():
            largest_number = max(n.integer for n in game_numbers)
            return largest_number * 2
        
    def clean(self):
        cleaned_data = super().clean()
        total_cost = self.next_integer * 2
        
        if self.score.score_value < total_cost:   
            raise forms.ValidationError("Not enough points to purchase new number.")

        cleaned_data["total_cost"] = total_cost
        cleaned_data["next_integer"] = self.next_integer
        return cleaned_data
        
    class Meta:
        model = Number
        fields = ("integer")
        
    