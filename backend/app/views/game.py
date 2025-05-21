from django.shortcuts import render, redirect, get_object_or_404

from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from decimal import Decimal

from ..forms import PurchaseNumberForm
from ..models import Game, Score, Number

from ..utils.update_score import update_score
from ..utils.calculate_time_cost import calculate_time_cost
from ..utils.check_digit_limit import check_digit_limit


# render the game page
@login_required(login_url="/login/")
@transaction.atomic  # ensures all functions finish or don't run at all
def render_game(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)

    score = game.score
    numbers = game.numbers.order_by("-integer")

    for index, num in enumerate(numbers):
        num.integer = "{:,}".format(int(num.integer))

    update_score(score, True)

    form = PurchaseNumberForm(request.POST or None, game_id=game_id)

    # +/- buttons
    buttons = [10**i for i in range(score.purchased_buttons)]
    next_button = max(n for n in buttons) * 10
    next_button_cost = next_button * 10

    time_increment = score.time_increment
    next_second_cost = calculate_time_cost(time_increment)

    return render(
        request,
        "app/game.html",
        {
            "game": game,
            "form": form,
            "score": score,
            "numbers": numbers,
            "buttons": buttons,
            "next_button": next_button,
            "next_button_cost": next_button_cost,
            "time_increment": time_increment,
            "next_second_cost": "{:,}".format(int(next_second_cost)),
            "last_updated": score.last_updated,
        },
    )


@login_required(login_url="/login/")
@require_POST
@transaction.atomic
def click_main_button(request, game_id):
    score = get_object_or_404(Score, game=game_id)
    update_score(score, False) # Don't update score before clicking button, as this resets the scores timer date to now, which will make 15s increment never hit if they're pressing the button

    new_score = score.score_value + score.increment
    score.score_value = new_score

    if check_digit_limit(new_score):
         return JsonResponse(
            {
                "new_score": "Infinity",
                "success": True,
                "message": "+Infinity",
            }
        )
    else:
        score.save()

    return JsonResponse(
        {
            "new_score": "{:,}".format(int(new_score)),
            "success": True,
            "message": "+" + "{:,}".format(int(score.increment)),
        }
    )


@login_required(login_url="/login/")
@require_POST
@transaction.atomic
def purchase_number(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    score = game.score

    update_score(score, False)

    user_numbers = game.numbers.all()
    new_number = max(n.integer for n in user_numbers) * 2
    cost = new_number * 100

    next_number = new_number * 2 
    next_cost = next_number * 100 # Unlocking a number costs 100x it's size
    
    # Check if they're going to break the db with too big of numbers first
    if check_digit_limit(next_number) or check_digit_limit(next_cost):
        return JsonResponse(
            {
                "success": True,
                "message": "You won!",
                "new_score": "Infinity",
                "new_increment": "Infinity",
                "new_number": "Infinity",
                "next_number": "Infinity",
                "next_number_cost": "Infinity",
            },
        )

    if score.score_value < cost:
        return JsonResponse(
            {"success": False, "message": "Not enough points!"}, status=400
        )
    else:
        score.score_value -= cost
        score.increment += new_number
        score.save()

        number = Number.objects.create(game=game, integer=new_number)
        number.save()

        return JsonResponse(
            {
                "success": True,
                "message": "+" + "{:,}".format(int(new_number)),
                "new_score": "{:,}".format(int(score.score_value)),
                "new_increment": "{:,}".format(int(score.increment)),
                "new_number": "{:,}".format(int(number.integer)),
                "next_number": "{:,}".format(int(next_number)),
                "next_number_cost": "{:,}".format(int(next_cost)),
                "time_increment": score.time_increment,
                "number_id": number.id,
            }
        )

@login_required(login_url="/login/")
@require_POST
@transaction.atomic
def increase_quantity(request, game_id, number_id, amount):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    number = get_object_or_404(Number, id=number_id, game=game_id)
    score = game.score

    update_score(score, False)

    cost = ( number.integer * amount * 10 )  # The cost of increasing number quantity is 1x it's size
    
    # Make sure increment doesn't get too big that it breaks the db
    if check_digit_limit(score.increment + (number.integer * amount)):
        return JsonResponse(
            {
                "success": True,
                "message": "Can't go any higher!",
                "new_quantity": number.quantity,
                "new_score": "{:,}".format(int(score.score_value)),
                "new_increment": "{:,}".format(int(score.increment)),
                "time_increment": score.time_increment,
            }
        )

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
                "new_quantity": "{:,}".format(int(number.quantity)),
                "new_score": "{:,}".format(int(score.score_value)),
                "new_increment": "{:,}".format(int(score.increment)),  # Return formatted strings so that Javascript doesn't ruin big numbers
                "time_increment": score.time_increment,
            }
        )

    return JsonResponse({"success": False, "message": "Not enough points!"}, status=400)


@login_required(login_url="/login/")
@transaction.atomic
def decrease_quantity(request, game_id, number_id, amount):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    score = game.score

    update_score(score, False)

    number = get_object_or_404(Number, id=number_id, game=game_id)
    cost = ( number.integer * amount * 10 )  # The cost of increasing number quantity is 10x it's size
    
    if check_digit_limit(score.score_value + cost):
         return JsonResponse(
            {
                "success": True,
                "message": "Too many points!",
                "new_quantity": "{:,}".format(int(number.quantity)),
                "new_score": "{:,}".format(int(score.score_value)),
                "new_increment": "{:,}".format(int(score.increment)),
                "time_increment": score.time_increment,
            }
        )

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
                "message": "-" + "{:,}".format(int(amount)),
                "new_quantity": "{:,}".format(int(number.quantity)),
                "new_score": "{:,}".format(int(score.score_value)),
                "new_increment": "{:,}".format(int(score.increment)),
                "time_increment": score.time_increment,
            }
        )
    else:
        return JsonResponse({"success": False, "message": "No more!"}, status=400)


@login_required(login_url="/login/")
@transaction.atomic
def purchase_button(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)
    score = game.score
    update_score(score, False)

    current_buttons = score.purchased_buttons

    if current_buttons >= 3:
        return JsonResponse({"success": False, "message": "No more buttons!"})

    cost = Decimal(10) ** (current_buttons + 1)

    if score.score_value < cost:
        return JsonResponse({"success": False, "message": "Not enough points!"})

    score.score_value -= cost
    score.purchased_buttons += 1
    score.save()
    
    formatted_val = "{:,}".format(10**(score.purchased_buttons - 1))

    # return redirect(to="/games/" + str(game_id))

    return JsonResponse(
        {
            "success": True,
            "new_score": "{:,}".format(int(score.score_value)),
            "new_button_amount": "{:,}".format(10**score.purchased_buttons),
            "message": f"Unlocked +/- {formatted_val}",
        }
    )


@login_required(login_url="/login/")
@transaction.atomic
def purchase_time(request, game_id):
    game = get_object_or_404(Game, id=game_id, user=request.user)

    score = game.score
    update_score(score, False)

    current_timer = score.time_increment
    cost = calculate_time_cost(current_timer)
    next_timer_cost = calculate_time_cost(current_timer - 1)

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
                "new_score": "{:,}".format(int(score.score_value)),
                "new_timer": str(score.time_increment),
                "new_timer_cost": "{:,}".format(int(next_timer_cost)),
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
    update_score(score, True)

    elapsed = (timezone.now() - score.last_updated).total_seconds()
    increments = elapsed // score.time_increment
    predicted_score = game.score.score_value + game.score.increment * Decimal(increments)
    
    if check_digit_limit(predicted_score):
        return JsonResponse(
            {
                "score": "Infinity",
                "increment": "Infinity",
                "last_updated": score.last_updated.isoformat(),
                "time_increment": score.time_increment,
            }
        )

    return JsonResponse(
        {
            "score": "{:,}".format(int(predicted_score)),
            "increment": "{:,}".format(int(score.increment)),
            "last_updated": score.last_updated.isoformat(),
            "time_increment": score.time_increment,
        }
    )
