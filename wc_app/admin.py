from django.contrib import admin

# Register your models here.


from wc_app.models import Event, Group, Team, Picks
                

class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'year')
    #list_filter = ['tournament',]

class GroupAdmin(admin.ModelAdmin):
    list_display = ['event', 'group']
    list_filter = ['event',]


class TeamAdmin(admin.ModelAdmin):
    list_display = ['group', 'group', 'name']
    list_filter = ['group', 'group' ]


class PicksAdmin(admin.ModelAdmin):
    list_display = ['user', 'team',]
    list_filter = ['team', 'user']

admin.site.register(Event, EventAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Picks, PicksAdmin)
