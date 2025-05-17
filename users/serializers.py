from rest_framework import serializers
from .models import Portfolio, PortfolioAsset,TransactionHistory,RecommendationHistory
from market.models import Asset

class AssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Asset
        fields = ['id', 'symbol', 'name', 'asset_type']

class PortfolioAssetSerializer(serializers.ModelSerializer):
    asset = AssetSerializer(read_only=True)

    class Meta:
        model = PortfolioAsset
        fields = ['id', 'asset', 'quantity', 'average_price']

class PortfolioSerializer(serializers.ModelSerializer):
    assets = PortfolioAssetSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'created_at', 'assets']

class TransactionHistorySerializer(serializers.ModelSerializer):
    asset = serializers.PrimaryKeyRelatedField(queryset=Asset.objects.all())

    class Meta:
        model = TransactionHistory
        fields = ['id', 'asset', 'portfolio', 'action', 'quantity', 'price', 'date']

class RecommendationHistorySerializer(serializers.ModelSerializer):
    asset = serializers.SerializerMethodField()

    class Meta:
        model = RecommendationHistory
        fields = ['id', 'portfolio', 'asset', 'recommendation', 'confidence', 'date']

    def get_asset(self, obj):
        return {
            "id": obj.asset.id,
            "symbol": obj.asset.symbol,
            "name": obj.asset.name,
            "asset_type": obj.asset.asset_type
        }    
