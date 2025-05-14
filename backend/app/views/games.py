from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from ..serializers import GameSerializer
from ..models import Game

@login_required(login_url="/login/")
@transaction.atomic
def render_games_page(request):
    games = request.user.games.all()

    return render(
        request, 
        "app/games.html",
        {
            "games": games,
        }
    )
    
@login_required(login_url="/login/")
@transaction.atomic
@require_POST
def new_game(request):
    serializer = GameSerializer(data = request.POST, context={"request": request})
    if serializer.is_valid():
        game = serializer.save()
        return redirect("play_game", game.id)
    
    return redirect("render_games_page")