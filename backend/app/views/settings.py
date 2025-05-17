from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

@login_required(login_url="/login/")
def render_settings(request):
    return render(request, "app/settings.html")


@login_required(login_url="/login/")
def deactivate_account(request):
    user = request.user
    user.is_active = False
    user.save()
    logout(request)
    return redirect("/login/")