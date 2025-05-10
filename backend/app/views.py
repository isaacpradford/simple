from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from django.db import transaction
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from .serializers import UserSerializer, ScoreSerializer, NumberSerializer
from .forms import UserLoginForm, UserRegistrationForm, PurchaseNumberForm
from .models import Score, Number


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


# Form to purchase a new number
@login_required(login_url="/login/")
@transaction.atomic  # ensures all functions finish or don't run at all
def render_home(request):
    form = PurchaseNumberForm(request.POST or None, user=request.user)
    numbers = request.user.numbers.order_by("-integer")

    if request.method == "POST" and form.is_valid():
        next_integer = form.cleaned_data["next_integer"]
        total_cost = form.cleaned_data["total_cost"]

        # Deduct score
        score = request.user.score
        score.score_value -= total_cost
        score.save()

        # Add or update the Number
        number, created = Number.objects.get_or_create(
            user=request.user, integer=next_integer, defaults={"quantity": 1}
        )
        if not created:
            number.quantity += 1
            number.save()

        score.increment = sum(n.integer * n.quantity for n in numbers)
        score.save()

        return redirect("/")

    return render(
        request,
        "app/home.html",
        {
            "form": form,
            "numbers": numbers,
            "last_updated": request.user.score.last_updated,
        },
    )


# Form to update a number
@login_required(login_url="/login/")
@transaction.atomic
def increase_quantity(request, number_id, amount):
    number = get_object_or_404(Number, id=number_id, user=request.user)
    cost = number.integer * amount * 2  # Cost of any number is twice it's own size
    score = request.user.score

    if score.score_value >= cost:
        score.score_value -= cost
        score.save()

        number.quantity += amount
        number.save()

        numbers = request.user.numbers.all()
        score.increment = sum(n.integer * n.quantity for n in numbers)
        score.save()
    # else:
    # raise ValidationError("Not enough points to purchase new number.")

    return redirect("/")


@login_required(login_url="/login/")
@transaction.atomic
def decrease_quantity(request, number_id, amount):
    number = get_object_or_404(Number, id=number_id, user=request.user)
    cost = number.integer * amount * 2  # The cost of any number is twice it's own size
    score = request.user.score

    if number.quantity - amount >= 0:
        score.score_value += cost
        score.save()

        number.quantity -= amount
        number.save()

        numbers = request.user.numbers.all()
        score.increment = sum(n.integer * n.quantity for n in numbers)
        score.save()

    return redirect("/")


class CreateUser(generics.CreateAPIView):
    queryset = User.objects.all()  # Look at the existing users
    serializer_class = UserSerializer
    permission_classes = [AllowAny]  # Allow anyone to create a new user


# score is auto-created when user is created
class ListScore(generics.ListAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Score.objects.filter(user=self.request.user)


class RetrieveScore(generics.ListAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.score


class UpdateScore(generics.UpdateAPIView):
    serializer_class = ScoreSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Score.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        score_value = request.data.get("score_value")
        increment = request.data.get("increment")

        try:
            instance.score_value = score_value
            instance.increment = increment
            instance.save()
        except ValueError:
            return Response(
                {"error": "score_value is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CreateNumber(generics.ListCreateAPIView):
    serializer_class = NumberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Number.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        user = self.request.user

        if serializer.is_valid():
            serializer.save(user=user)

            # Update the score with the new data passed in
            new_score = self.request.data.get("new_score")
            new_increment = self.request.data.get("new_increment")

            score = Score.objects.get(user=user)
            score.increment = new_increment
            score.score_value = new_score

            score.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateNumber(generics.UpdateAPIView):
    serializer_class = NumberSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):  # Get all the numbers of one user
        return Number.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)

        if serializer.is_valid():
            # Update the score with the new data passed in
            new_score = self.request.data.get("new_score")
            new_increment = self.request.data.get("new_increment")
            score = Score.objects.get(user=self.request.user)

            score.increment = new_increment
            score.score_value = new_score

            score.save()
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListNumbers(generics.ListAPIView):
    serializer_class = NumberSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Number.objects.filter(user=self.request.user)


class DeleteNumber(generics.DestroyAPIView):
    serializer_class = NumberSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "pk"

    def get_queryset(self):
        return Number.objects.filter(user=self.request.user)

    # For overriding default destroy function
    # def destroy(self, request, *args, **kwargs):
    # instance = self.get_object()
    # self.perform_destroy(instance)
    # return Response({"message": "Number deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
