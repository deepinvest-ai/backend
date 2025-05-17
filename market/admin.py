from django.contrib import admin
from .models import Asset, PriceHistory

admin.site.register(Asset)
admin.site.register(PriceHistory)
