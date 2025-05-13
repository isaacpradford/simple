from django.shortcuts import render, redirect, get_object_or_404

from django.db import transaction
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils import timezone

from decimal import Decimal
from datetime import timedelta

from .serializers import UserSerializer, ScoreSerializer, NumberSerializer
from .forms import UserLoginForm, UserRegistrationForm, PurchaseNumberForm
from .models import Score, Number


def update_score_if_needed(request):
    if request.user.is_authenticated and hasattr(request.user, "score"):
        score = request.user.score
        now = timezone.now()
        elapsed = (now - score.last_updated).total_seconds()

        if elapsed >= score.time_increment:
            ticks = int(elapsed // score.time_increment)
            score.score_value += score.increment * ticks
            score.last_updated += timedelta(seconds=score.time_increment * ticks)
            score.save()
            
def calculate_next_second_cost(current_timer):
    new_timer = current_timer - 1
    new_cost = ((15 - new_timer)) ** (15 - new_timer)
    return new_cost


def login_view(request):
    if request.user.is_authenticated:
        return redirect("/")

    if request.method == "POST":
        form = UserLoginForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(request=request, username=username, password=password)
            if user is not None:
                login(request, user)

                next_url = request.GET.get("next") or request.POST.get("next")
                return redirect(next_url if next_url else "/")
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
                return redirect("/")
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})


# render the home page
@login_required(login_url="/login/")
@transaction.atomic  # ensures all functions finish or don't run at all
def render_home(request):
    form = PurchaseNumberForm(request.POST or None, user=request.user)
    numbers = request.user.numbers.order_by("-integer")
    buttons = [10**i for i in range(request.user.score.purchased_buttons)]
    next_button = max(n for n in buttons) * 10
    next_button_cost = next_button * 10
    time_increment = request.user.score.time_increment
    next_second_cost = calculate_next_second_cost(time_increment)

    update_score_if_needed(request)

    return render(
        request,
        "app/home.html",
        {
            "form": form,
            "numbers": numbers,
            "buttons": buttons,
            "next_button": next_button,
            "next_button_cost": next_button_cost,
            "time_increment": time_increment,
            "next_second_cost": next_second_cost,
            "last_updated": request.user.score.last_updated,
        },
    )


@login_required
@require_POST
@transaction.atomic
def purchase_number(request):
    update_score_if_needed(request)
    user_numbers = request.user.numbers.all()
    next_number = max(n.integer for n in user_numbers) * 2
    cost = next_number * 2
    score = request.user.score

    if request.user.score.score_value < cost:
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
def increase_quantity(request, number_id, amount):
    update_score_if_needed(request)
    number = get_object_or_404(Number, id=number_id, user=request.user)
    cost = (
        number.integer * amount
    )  # The cost of increasing number quantity is 1x it's size
    score = request.user.score

    if score.score_value >= cost:
        score.score_value -= cost
        score.save()

        number.quantity += amount
        number.save()

        numbers = request.user.numbers.all()
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
def decrease_quantity(request, number_id, amount):
    update_score_if_needed(request)
    number = get_object_or_404(Number, id=number_id, user=request.user)
    cost = (
        number.integer * amount
    )  # The cost of increasing number quantity is 1x it's size
    score = request.user.score

    if number.quantity - amount >= 0:
        score.score_value += cost
        score.save()

        number.quantity -= amount
        number.save()

        numbers = request.user.numbers.all()
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
def purchase_button(request):
    score = request.user.score
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
def purchase_time(request):
    score = request.user.score
    current_timer = score.time_increment
    cost = calculate_next_second_cost(current_timer)
    next_timer_cost = calculate_next_second_cost(current_timer - 1)

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
def get_predicted_score(request):
    update_score_if_needed(request)
    score = request.user.score
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
