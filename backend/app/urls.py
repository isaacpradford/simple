from django.urls import path
from django.contrib.auth.views import LoginView
from .views import landing, authentication, game, games, settings, leaderboard

urlpatterns = [
    path("", landing.render_landing_page, name="landing"),
    
    path("login/", authentication.login_view, name="login"),
    path("logout/", authentication.logout_view, name="logout"),
    path("register/", authentication.register_view, name="register"),
    
    path("settings/", settings.render_settings, name="settings"),
    
    path("games/", games.render_games_page, name="games" ),
    path("games/new_game/", games.new_game, name="new_game"),
    path("games/<int:game_id>/", game.render_game, name="play_game"),

    path("game/<int:game_id>/numbers/purchase_number/", game.purchase_number, name="purchase_number"),
    path("game/<int:game_id>/numbers/<int:number_id>/increase/<int:amount>/", game.increase_quantity, name="increase_quantity"),
    path("game/<int:game_id>/numbers/<int:number_id>/decrease/<int:amount>/", game.decrease_quantity, name="decrease_quantity"),
    
    path("game/<int:game_id>/button/purchase_button/", game.purchase_button, name="purchase_button"),
    path("game/<int:game_id>/timer/purchase_time/", game.purchase_time, name="purchase_time"),
    path("game/<int:game_id>/predicted_score/", game.get_predicted_score, name="predicted_score"),
    
    path("leaderboard/", leaderboard.render_leaderboard, name="leaderboard")
]