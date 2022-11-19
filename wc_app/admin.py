from django.contrib import admin

# Register your models here.


from wc_app.models import Event, Group, Team, Picks, Stage, AccessLog, TotalScore
                

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')
    #list_filter = ['tournament',]

class StageAdmin(admin.ModelAdmin):
    list_display = ('name',)
    #list_filter = ['tournament',]


class GroupAdmin(admin.ModelAdmin):
    list_display = ['stage', 'group']
    list_filter = ['stage',]


class TeamAdmin(admin.ModelAdmin):
    list_display = ['group', 'group', 'name']
    list_filter = ['group', 'group' ]


class PicksAdmin(admin.ModelAdmin):
    list_display = ['user', 'team',]
    list_filter = ['team', 'user']

class AccessLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'stage', 'count']
    #list_filter = ['team', 'user']

class TotalScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'stage', 'score']
    #list_filter = ['team', 'user']


admin.site.register(Event, EventAdmin)
admin.site.register(Stage, StageAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Picks, PicksAdmin)
admin.site.register(AccessLog, AccessLogAdmin)
admin.site.register(TotalScore, TotalScoreAdmin)

