from django.contrib import admin

# Register your models here.

from golf_app.models import Season, Tournament, Field, Picks, Group, TotalScore, ScoreDetails, Name, BonusDetails

class GroupAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'number', 'playerCnt')
    list_filter = ['tournament',]

class FieldAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'playerName']
    list_filter = ['tournament',]

class PicksAdmin(admin.ModelAdmin):
    list_display = ['user', 'playerName']
    list_filter = ['user']



admin.site.register(Tournament)
admin.site.register(Field, FieldAdmin)
admin.site.register(Picks, PicksAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(TotalScore)
admin.site.register(ScoreDetails)
admin.site.register(Name)
admin.site.register(BonusDetails)
admin.site.register(Season)
