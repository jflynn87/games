from django.contrib import admin

# Register your models here.

from golf_app.models import Season, Tournament, Field, Picks, Group, TotalScore, \
                ScoreDetails, Name, BonusDetails, mpScores, PickMethod, PGAWebScores, \
                Golfer, ScoreDict, UserProfile, AccessLog, AuctionPick

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

class GolferAdmin(admin.ModelAdmin):
    list_display = ['golfer_name,',]

class PGAWebScoresAdmin(admin.ModelAdmin):
    list_filter = ['tournament']

class ScoreDictAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'get_season']
    list_filter = ['tournament']
    readonly_fields = ('updated',)

    def get_season(self, obj):
        return obj.tournament.season.season


class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user',]
    


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
admin.site.register(PGAWebScores, PGAWebScoresAdmin)
admin.site.register(Golfer)
admin.site.register(ScoreDict, ScoreDictAdmin)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(AccessLog)
admin.site.register(AuctionPick)
