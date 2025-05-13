from django import forms
from decimal import Decimal
from .models import Number

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
    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.next_integer = self.calculate_next_integer()
        
    def calculate_next_integer(self):
        user_numbers = self.user.numbers.all()
        if user_numbers.exists():
            largest_number = max(n.integer for n in user_numbers)
            return largest_number * 2
        
    def clean(self):
        cleaned_data = super().clean()
        # quantity = cleaned_data.get("quantity")
        total_cost = self.next_integer * 2
        
        if self.user.score.score_value < total_cost:   
            raise forms.ValidationError("Not enough points to purchase new number.")

        cleaned_data["total_cost"] = total_cost
        cleaned_data["next_integer"] = self.next_integer
        return cleaned_data
        
    class Meta:
        model = Number
        fields = ("integer")
        
        
class PurchaseButtonForm(forms.Form):
    def __init__(self, * args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.next_button = self.user.score.purchased_buttons + 1
        
    # def 