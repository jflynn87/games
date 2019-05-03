from django.contrib import admin
from port_app.models import CCY, Position, Portfolio, MarketData

# Register your models here.


admin.site.register(CCY)
admin.site.register(Portfolio)
admin.site.register(Position)
admin.site.register(MarketData)
