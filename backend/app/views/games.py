from django.db import transaction
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from ..serializers import GameSerializer
from ..models import Game
from ..utils.update_score import update_score

@login_required(login_url="/login/")
@transaction.atomic
def render_games_page(request):
    games = request.user.games.order_by("id")

    for game in games:
        update_score(game.score, True)

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
    
    return redirect("/games/")


@login_required(login_url="/login/")
@require_POST
def delete_game(request, game_id):
    obj = Game.objects.get(id=game_id)
    obj.delete()
    
    return redirect("/games/")