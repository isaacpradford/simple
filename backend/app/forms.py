from django import forms
from django.shortcuts import get_object_or_404
from decimal import Decimal
from .models import Number, Game

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .utils.check_digit_limit import check_digit_limit


class UserLoginForm(forms.Form):
    username = forms.CharField(max_length=150, min_length=5, widget=forms.TextInput(attrs={
        "class": "form-control",
        "id": "usernameInput",
        "placeholder": "Enter your username",
        "aria-describedBy": "emailHelp"
    }))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "id": "passwordInput",
        "placeholder": "Enter your password"
    }))
        

class UserRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, min_length=5, widget=forms.TextInput(attrs={
        "class": "form-control",
        "id": "usernameInput",
        "placeholder": "Enter your username",
        "aria-describedBy": "emailHelp"
    }))
    password = forms.CharField(min_length=8, widget=forms.PasswordInput(attrs={
        "class": "form-control",
        "id": "passwordInput",
        "placeholder": "Enter your password"
    }))
    
class PurchaseNumberForm(forms.Form):
    def __init__(self, *args, game_id=None, **kwargs):
        self.game = get_object_or_404(Game, id=game_id)
        self.score = self.game.score
        super().__init__(*args, **kwargs)
        self.next_integer = self.calculate_next_integer()
        self.next_integer_cost = self.calculate_next_integer_cost()
        
    def calculate_next_integer(self):
        game_numbers = self.game.numbers.all()
        
        if game_numbers.exists():
            largest_number = max(n.integer for n in game_numbers)
            
            num_string = format(int(largest_number * 2))
            if len(num_string) >= 500:
                return "Infinity"
            
            return "{:,}".format(int(largest_number * 2))
    
    def calculate_next_integer_cost(self):
        game_numbers = self.game.numbers.all()
        if game_numbers.exists():
            largest_number = max(n.integer for n in game_numbers)
            num_string = format(int(largest_number * 2))

            if len(num_string) >= 500:
                return "&infin;"
            
            return "{:,}".format(int(largest_number * 2 * 100))
        
    def clean(self):
        cleaned_data = super().clean()
        total_cost = self.next_integer * 2
        
        if check_digit_limit(total_cost):
            raise forms.ValidationError("This number is too large to store.")
        if self.score.score_value < total_cost:   
            raise forms.ValidationError("Not enough points to purchase new number.")

        cleaned_data["total_cost"] = total_cost
        cleaned_data["next_integer"] = self.next_integer
        return cleaned_data    