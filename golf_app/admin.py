from django.contrib import admin

# Register your models here.

from golf_app.models import Season, Tournament, Field, Picks, Group, TotalScore, ScoreDetails, Name, BonusDetails

class GroupAdmin(admin.ModelAdmin):
    list_display = ('tournament', 'number', 'playerCnt')
    list_filter = ['tournament',]

class FieldAdmin(admin.ModelAdmin):
    list_display = ['tournament', 'playerName']
    list_filter = ['tournament',]


admin.site.register(Tournament)
admin.site.register(Field, FieldAdmin)
admin.site.register(Picks)
admin.site.register(Group, GroupAdmin)
admin.site.register(TotalScore)
admin.site.register(ScoreDetails)
admin.site.register(Name)
admin.site.register(BonusDetails)
admin.site.register(Season)
