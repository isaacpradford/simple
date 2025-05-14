from django.shortcuts import render, redirect, get_object_or_404

from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from decimal import Decimal
from datetime import timedelta

from ..serializers import UserSerializer, ScoreSerializer, NumberSerializer
from ..forms import UserLoginForm, UserRegistrationForm, PurchaseNumberForm
from ..models import Score, Number

def login_view(request):
    if request.user.is_authenticated:
        return redirect("/games/")

    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)

                next_url = request.GET.get("next") or request.POST.get("next")
                return redirect(next_url if next_url else "/games/")
            else:
                form.add_error(None, "Invalid username or password.")

    else:
        form = UserLoginForm()

    return render(request, "registration/login.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("/login")

# Test
# p31s5mikfmgpDxLJuewR
def register_view(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            serializer = UserSerializer(data=form.cleaned_data)
            if serializer.is_valid():
                user = serializer.save()
                login(request, user)  # auto-login after registration
                return redirect("/games/")
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})

