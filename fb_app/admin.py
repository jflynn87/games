from django.contrib import admin
from fb_app.models import Week, Games, Picks, Player, League, Teams, MikeScore, \
    WeekScore, Season

# Register your models here.

class PicksAdmin(admin.ModelAdmin):
    list_display = ['week', 'player', 'pick_num', 'team']
    list_filter = ['week', 'player']

class GamesAdmin(admin.ModelAdmin):
    list_display = ['week', 'home', 'away']
    list_filter = ['week__season', 'week']

class WeekScoreAdmin(admin.ModelAdmin):
    list_display = ['week', 'player', 'score']
    list_filter = ['week', 'player']

class WeekAdmin(admin.ModelAdmin):
    list_display = ['season', 'week', 'game_cnt']
    list_filter = ['season', 'week']

admin.site.register(Week, WeekAdmin)
admin.site.register(Games, GamesAdmin)
admin.site.register(Picks, PicksAdmin)
admin.site.register(Player)
admin.site.register(League)
admin.site.register(Teams)
admin.site.register(MikeScore)
admin.site.register(WeekScore, WeekScoreAdmin)
admin.site.register(Season)
