from django.contrib import admin

# Register your models here.

from golf_app.models import Season, Tournament, Field, Picks, Group, TotalScore, \
                ScoreDetails, Name, BonusDetails, mpScores, PickMethod, PGAWebScores

class GroupAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'number', 'playerCnt')
    list_filter = ['tournament',]

class FieldAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'playerName']
    list_filter = ['tournament',]

class PicksAdmin(admin.ModelAdmin):


    list_display = ['user', 'playerName']
    list_filter = ['playerName__tournament', 'user' ]


class BonusDetailsAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'user', 'winner_bonus', 'cut_bonus', 'major_bonus']
    list_filter = ['tournament', 'user']

class ScoreDetailsAdmin(admin.ModelAdmin):
    list_display = ['user', 'pick', 'score']
    list_filter = ['pick__playerName__tournament', 'user']

class PickMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'tournament', 'method']
    list_filter = ['user', 'tournament', 'method']




admin.site.register(Tournament)
admin.site.register(Field, FieldAdmin)
admin.site.register(Picks, PicksAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(TotalScore)
admin.site.register(ScoreDetails, ScoreDetailsAdmin)
admin.site.register(Name)
admin.site.register(BonusDetails, BonusDetailsAdmin)
admin.site.register(Season)
admin.site.register(mpScores)
admin.site.register(PickMethod, PickMethodAdmin)
admin.site.register(PGAWebScores)
