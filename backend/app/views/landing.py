from django.shortcuts import render


def render_landing_page(request):
    return render(request, "app/landing.html")
