from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

def update_score(score):
    now = timezone.now()
    elapsed = (now - score.last_updated).total_seconds()
    
    if elapsed >= score.time_increment:
        ticks = int(elapsed // score.time_increment)
        seconds = score.time_increment * ticks
        
        score.score_value += score.increment * ticks
        score.last_updated += timedelta(seconds=score.time_increment * ticks)
        score.save()

        game = score.game
        game.time_elapsed += int(seconds)
        game.save()
        