from django.contrib import admin
from fb_app.models import Week, Games, Picks, Player, League, Teams, MikeScore, WeekScore

# Register your models here.

admin.site.register(Week)
admin.site.register(Games)
admin.site.register(Picks)
admin.site.register(Player)
admin.site.register(League)
admin.site.register(Teams)
admin.site.register(MikeScore)
admin.site.register(WeekScore)
