from django import template
from golf_app.models import Picks
from django.db.models import Count

register = template.Library()

@register.filter
def model_name(obj):
    return obj._meta.verbose_name

@register.filter
def currency(dollars):
    dollars = int(dollars)
    return '$' + str(dollars)

@register.filter
def line_break(count):
    user_cnt = Picks.objects.filter(playerName__tournament__current=True).values('playerName__tournament').annotate(Count('user', distinct=True))
    if count % (user_cnt[0].get('user__count')+1) == 0 or count == 1:
        return True
    else:
        return False
