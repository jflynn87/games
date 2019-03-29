from django import template
from golf_app.models import Picks, mpScores, Field
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
    if (count -1) % (user_cnt[0].get('user__count')) == 0 or count == 0:
        return True
    else:
        return False

@register.filter
def first_round(pick):
    field = Field.objects.get(tournament__pga_tournament_num='470', playerName=pick)
    wins = mpScores.objects.filter(player=field, round__lte=3, result="Yes").count()
    losses = mpScores.objects.filter(player=field, round__lte=3, result="No").exclude(score="AS").count()
    ties = mpScores.objects.filter(player=field, round__lte=3, score="AS").count()

    return str(wins) + '-' + str(losses) + '-' + str(ties)

@register.filter
def leader(group):
    pass
