from django.utils import timezone
from datetime import timedelta

def update_score(score):
    now = timezone.now()
    elapsed = (now - score.last_updated).total_seconds()

    if elapsed >= score.time_increment:
        ticks = int(elapsed // score.time_increment)
        score.score_value += score.increment * ticks
        score.last_updated += timedelta(seconds=score.time_increment * ticks)
        score.save()
            