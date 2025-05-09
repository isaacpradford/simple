from django.utils import timezone
from datetime import timedelta

def update_score_if_needed(score):
    now = timezone.now()
    elapsed = (now - score.last_updated).total_seconds()
    
    if elapsed >= 15:
        ticks = int ( elapsed // 15)
        score.score_value += score.increment * ticks
        score.last_updated += timedelta(seconds=15 * ticks)
        score.save()
        
def update_score_context(request):
    if request.user.is_authenticated and hasattr(request.user, "score"):
        update_score_if_needed(request.user.score)
    return {}