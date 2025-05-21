from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ..models import Game, Score


# @login_required(login_url="/login/")
def render_leaderboard(request):
    scores = Score.objects.select_related("game__user").order_by("-score_value")[:10]

    return render (
        request,
        "app/leaderboard.html",
        {
            "scores": scores,
        },
    )
