from rest_framework import serializers
from .models import Asset, PriceHistory

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Asset
        fields = "__all__"
class PriceHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = PriceHistory
        fields = "__all__"