from django.shortcuts import render, get_object_or_404

from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from decimal import Decimal

from ..serializers import UserSerializer, ScoreSerializer, NumberSerializer
from ..forms import PurchaseNumberForm
from ..models import Game, Score, Number

from ..utils.update_score import update_score
from ..utils.calculate_time_cost import calculate_time_cost

# render the game page
@login_required(login_url="/login/")
@transaction.atomic  # ensures all functions finish or don't run at all
def render_game(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    
    score = game.score
    numbers = game.numbers.order_by("-integer")
    
    update_score(score)
    
    form = PurchaseNumberForm(request.POST or None, game_id=game_id)
    
    buttons = [10**i for i in range(score.purchased_buttons)]
    next_button = max(n for n in buttons) * 10
    next_button_cost = next_button * 10
    time_increment = score.time_increment
    next_second_cost = calculate_time_cost(time_increment)


    return render(
        request,
        "app/game.html",
        {
            "game_id": game.id,
            "form": form,
            "numbers": numbers,
            "buttons": buttons,
            "next_button": next_button,
            "next_button_cost": next_button_cost,
            "time_increment": time_increment,
            "next_second_cost": next_second_cost,
            "last_updated": score.last_updated,
        },
    )

@login_required
@require_POST
@transaction.atomic
def purchase_number(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)

    update_score(score)
    
    user_numbers = game.numbers.all()
    next_number = max(n.integer for n in user_numbers) * 2
    cost = next_number * 2
    score = game.score

    if score.score_value < cost:
        return JsonResponse(
            {"success": False, "message": "Not enough points!"}, status=400
        )
    else:
        score.score_value -= cost
        score.increment += next_number
        score.save()

        number = Number.objects.create(user=request.user, integer=next_number)
        number.save()

        return JsonResponse(
            {
                "success": True,
                "message": "+" + str(next_number),
                "new_score": str(score.score_value),
                "new_increment": str(score.increment),
                "new_number": str(number.integer),
                "time_increment": score.time_increment,
                "number_id": number.id,
                "next_purchase": str(cost),
            }
        )


@login_required(login_url="/login/")
@require_POST
@transaction.atomic
def increase_quantity(request, game_id, number_id, amount):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    number = get_object_or_404(Number, id=number_id, user=request.user)
    score = game.score
    
    update_score(score)
    
    cost = (
        number.integer * amount
    )  # The cost of increasing number quantity is 1x it's size

    if score.score_value >= cost:
        score.score_value -= cost
        score.save()

        number.quantity += amount
        number.save()

        numbers = game.numbers.all()
        score.increment = sum(n.integer * n.quantity for n in numbers)
        score.save()

        return JsonResponse(
            {
                "success": True,
                "message": "+" + str(amount),
                "new_quantity": number.quantity,
                "new_score": str(score.score_value),
                "new_increment": str(
                    score.increment
                ),  # Return strings so that Javascript doesn't ruin big numbers
                "time_increment": score.time_increment,
            }
        )

    return JsonResponse({"success": False, "message": "Not enough points!"}, status=400)


@login_required(login_url="/login/")
@transaction.atomic
def decrease_quantity(request, game_id, number_id, amount):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    score = game.score
    
    update_score(score)
    
    number = get_object_or_404(Number, id=number_id, user=request.user)
    cost = (
        number.integer * amount
    )  # The cost of increasing number quantity is 1x it's size

    if number.quantity - amount >= 0:
        score.score_value += cost
        score.save()

        number.quantity -= amount
        number.save()

        numbers = game.numbers.all()
        score.increment = sum(n.integer * n.quantity for n in numbers)
        score.save()

        return JsonResponse(
            {
                "success": True,
                "message": "-" + str(amount),
                "new_quantity": number.quantity,
                "new_score": str(score.score_value),
                "new_increment": str(score.increment),
                "time_increment": score.time_increment,
            }
        )
    else:
        return JsonResponse({"success": False, "message": "Need more!"}, status=400)


@login_required(login_url="/login/")
@transaction.atomic
def purchase_button(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    score = game.score
    
    update_score(score)
    
    current_buttons = score.purchased_buttons

    cost = Decimal(10) ** (current_buttons + 1)
    
    if score.score_value < cost:
        return JsonResponse({"success": False, "message": "Not enough points!"})

    score.score_value -= cost
    score.purchased_buttons += 1
    score.save()

    return JsonResponse(
        {
            "success": True,
            "new_score": str(score.score_value),
            "new_button_amount": 10**score.purchased_buttons,
            "message": f"Unlocked +/- {10 ** score.purchased_buttons}",
        }
    )


@login_required(login_url="/login/")
@transaction.atomic
def purchase_time(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)

    score = game.score
    update_score(score)
    
    current_timer = score.time_increment
    cost = calculate_time_cost(current_timer)
    next_timer_cost = calculate_time_cost(current_timer - 1)

    print(cost)

    if current_timer == 5:
        return JsonResponse(
            {
                "success": False,
                "message": "Can't go any smaller!",
            }
        )

    if score.score_value >= cost:
        score.time_increment -= 1
        score.score_value -= cost
        score.save()
        

        return JsonResponse(
            {
                "success": True,
                "message": "-1 second",
                "new_score": str(score.score_value),
                "new_timer": str(score.time_increment),
                "new_timer_cost": str(next_timer_cost),
            }
        )

    else:
        return JsonResponse(
            {
                "success": False,
                "message": "Need more points!",
            }
        )


# Get the estimated score
@login_required(login_url="/login/")
def get_predicted_score(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)

    score = game.score
    update_score(score)
    
    elapsed = (timezone.now() - score.last_updated).total_seconds()
    increments = elapsed // score.time_increment
    predicted_score = score.score_value + score.increment * Decimal(increments)

    return JsonResponse(
        {
            "score": str(predicted_score),
            "increment": str(score.increment),
            "last_updated": score.last_updated.isoformat(),
            "time_increment": score.time_increment,
        }
    )
