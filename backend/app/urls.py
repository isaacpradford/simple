from django.urls import path
from django.contrib.auth.views import LoginView
from .views import gameplay, authentication, games

urlpatterns = [
    path("login/", authentication.login_view, name="login"),
    path("logout/", authentication.logout_view, name="logout"),
    path("register/", authentication.register_view, name="register"),
    
    path("games/", games.render_games_page, name="games" ),
    path("games/new_game/", games.new_game, name="new_game"),
    path("games/<int:game_id>/", gameplay.render_game, name="play_game"),

    # path("", gameplay.render_game, name="home"),
    path("game/<int:game_id>/numbers/purchase_number/", gameplay.purchase_number, name="purchase_number"),
    path("game/<int:game_id>/numbers/<int:number_id>/increase/<int:amount>/", gameplay.increase_quantity, name="increase_quantity"),
    path("game/<int:game_id>/numbers/<int:number_id>/decrease/<int:amount>/", gameplay.decrease_quantity, name="decrease_quantity"),
    
    path("game/<int:game_id>/button/purchase_button/", gameplay.purchase_button, name="purchase_button"),
    path("game/<int:game_id>/timer/purchase_time/", gameplay.purchase_time, name="purchase_time"),
    path("game/<int:game_id>/predicted_score/", gameplay.get_predicted_score, name="predicted_score")
    
    # path("score/read/", views.ListScore.as_view(), name="read-score"),
    # path("score/update/<int:pk>/", views.UpdateScore.as_view(), name="update-score"),
    
    # path("number/read/", views.ListNumbers.as_view(), name="read-numbers"),
    # path("number/create/", views.CreateNumber.as_view(), name="create-number"),
    # path("number/update/<int:pk>/", views.UpdateNumber.as_view(), name="update-number"),
    # path("number/delete/<int:pk>/", views.DeleteNumber.as_view(), name="delete-number")
]