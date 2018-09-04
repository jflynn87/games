from django.contrib import admin

# Register your models here.

from golf_app.models import Tournament, Field, Picks, Group, TotalScore, ScoreDetails, Name

admin.site.register(Tournament)
admin.site.register(Field)
admin.site.register(Picks)
admin.site.register(Group)
admin.site.register(TotalScore)
admin.site.register(ScoreDetails)
admin.site.register(Name)
