from django.utils import timezone
from datetime import timedelta

from ..utils.check_digit_limit import check_digit_limit


def update_score(score, update_time):
    now = timezone.now()
    elapsed = (now - score.last_updated).total_seconds()

    if check_digit_limit(score.score_value + score.increment):
        return

    if elapsed >= score.time_increment:
        ticks = int(elapsed // score.time_increment)
        seconds = score.time_increment * ticks

        score.score_value += score.increment * ticks
        
        if (update_time):
            score.last_updated += timedelta(seconds=score.time_increment * ticks)
            game = score.game
            game.time_elapsed += int(seconds)
            game.save()
        score.save()
