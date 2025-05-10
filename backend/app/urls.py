from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path("", views.render_home, name="home"),
    path("numbers/<int:number_id>/increase/<int:amount>/", views.increase_quantity, name="increase_quantity"),
    path("numbers/<int:number_id>/decrease/<int:amount>/", views.decrease_quantity, name="decrease_quantity"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register_view, name="register"),
    
    # path("score/read/", views.ListScore.as_view(), name="read-score"),
    # path("score/update/<int:pk>/", views.UpdateScore.as_view(), name="update-score"),
    
    # path("number/read/", views.ListNumbers.as_view(), name="read-numbers"),
    # path("number/create/", views.CreateNumber.as_view(), name="create-number"),
    # path("number/update/<int:pk>/", views.UpdateNumber.as_view(), name="update-number"),
    # path("number/delete/<int:pk>/", views.DeleteNumber.as_view(), name="delete-number")
]