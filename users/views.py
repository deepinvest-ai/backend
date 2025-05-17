from rest_framework import viewsets, permissions,generics
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from market.models import Asset,PriceHistory
from rest_framework.generics import ListAPIView
from market.indicators import *
from market.models import Asset,PriceHistory
from .models import Portfolio, PortfolioAsset,TransactionHistory,RecommendationHistory
from .serializers import PortfolioSerializer, PortfolioAssetSerializer,TransactionHistorySerializer,RecommendationHistorySerializer
from django.http import JsonResponse
import random
from datetime import datetime ,timedelta

from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

class PortfolioViewSet(viewsets.ModelViewSet):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"])
    def add_asset(self, request, pk=None):
        portfolio = self.get_object()
        asset_id = request.data.get("asset_id")
        quantity = request.data.get("quantity")
        average_price = request.data.get("average_price")

        if not all([asset_id, quantity, average_price]):
            return Response({"error": "Tüm alanlar zorunludur."}, status=400)

        existing = PortfolioAsset.objects.filter(portfolio=portfolio, asset_id=asset_id).first()
        if existing:
            return Response({"error": "Bu varlık zaten portföyde mevcut."}, status=400)

        asset_obj = PortfolioAsset.objects.create(
            portfolio=portfolio,
            asset_id=asset_id,
            quantity=quantity,
            average_price=average_price
        )
        return Response(PortfolioAssetSerializer(asset_obj).data)
    
class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        return Response({
            'token': token.key,
            'user_id': token.user_id,
            'email': token.user.email,
            'username': token.user.username
        })



class PortfolioAssetViewSet(viewsets.ModelViewSet):
    queryset = PortfolioAsset.objects.all()
    serializer_class = PortfolioAssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(portfolio__user=self.request.user)

class TransactionHistoryViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return TransactionHistory.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class AIRecommendationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        portfolio_id = request.data.get("portfolio_id")
        asset_id = request.data.get("asset_id")

        if not all([portfolio_id, asset_id]):
            return Response({"error": "portfolio_id ve asset_id zorunludur."}, status=400)

        try:
            portfolio = Portfolio.objects.get(id=portfolio_id, user=request.user)
            asset = Asset.objects.get(id=asset_id)
        except Portfolio.DoesNotExist:
            return Response({"error": "Portföy bulunamadı veya erişim yetkiniz yok."}, status=404)
        except Asset.DoesNotExist:
            return Response({"error": "Varlık bulunamadı."}, status=404)

        # Dummy öneri üretimi
        recommendation = random.choice(["BUY", "SELL", "HOLD"])
        confidence = round(random.uniform(0.6, 0.99), 2)

        record = RecommendationHistory.objects.create(
            user=request.user,
            portfolio=portfolio,
            asset=asset,
            recommendation=recommendation,
            confidence=confidence,
            date=datetime.now().date()
        )

        return Response(RecommendationHistorySerializer(record).data, status=201)        

class RecommendationHistoryListView(generics.ListAPIView):
    serializer_class = RecommendationHistorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RecommendationHistory.objects.filter(user=self.request.user).order_by("-date")   


class AIRecommendationHistoryView(ListAPIView):
    serializer_class = RecommendationHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return RecommendationHistory.objects.filter(user=self.request.user).order_by('-date')
    

class AIAnalysisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        asset_id = request.query_params.get("asset_id")
        if not asset_id:
            return Response({"error": "asset_id parametresi gerekli."}, status=400)

        try:
            asset = Asset.objects.get(id=asset_id)
        except Asset.DoesNotExist:
            return Response({"error": "Varlık bulunamadı."}, status=404)

        prices = PriceHistory.objects.filter(asset=asset).order_by("-date")[:60]
        if prices.count() < 30:
            return Response({"error": "Yeterli tarihsel veri yok."}, status=400)

        prices = list(prices)[::-1]  # En eski → en yeni

        closes = [p.close for p in prices]
        highs = [p.high for p in prices]
        lows = [p.low for p in prices]
        volumes = [p.volume for p in prices]

        closes_series = pd.Series(closes)
        highs_series = pd.Series(highs)
        lows_series = pd.Series(lows)
        volumes_series = pd.Series(volumes)

        # İndikatörleri hesapla
        rsi_val = rsi(closes)
        macd_val, _ = macd(closes)
        obv_val = obv(closes_series, volumes_series)
        adx_val = adx(highs_series, lows_series, closes_series)
        ema_val = ema(closes_series)
        sma_val = sma(closes_series)
        cci_val = cci(highs, lows, closes)
        atr_val = atr(highs_series, lows_series, closes_series)
        stoch_k, stoch_d = stochastic(highs, lows, closes)
        bb_upper, bb_middle, bb_lower = bollinger(closes_series)
        mfi_val = mfi(highs, lows, closes, volumes)
        roc_val = roc(closes_series)
        willr_val = williams_r(highs, lows, closes)
        ichimoku_vals = ichimoku(highs, lows, closes)
        vwap_val = vwap(highs, lows, closes, volumes)
        uo_val = ultimate_oscillator(highs, lows, closes)

        result = {
            "asset_id": asset.id,
            "symbol": asset.symbol,
            "indicators": {
                "rsi": round(rsi_val, 2) if rsi_val is not None else None,
                "macd": round(macd_val, 2) if macd_val is not None else None,
                "obv": round(obv_val, 2) if obv_val is not None else None,
                "adx": round(adx_val, 2) if adx_val is not None else None,
                "ema": round(ema_val, 2) if ema_val is not None else None,
                "sma": round(sma_val, 2) if sma_val is not None else None,
                "cci": round(cci_val, 2) if cci_val is not None else None,
                "atr": round(atr_val, 2) if atr_val is not None else None,
                "stochastic_k": round(stoch_k, 2) if stoch_k is not None else None,
                "stochastic_d": round(stoch_d, 2) if stoch_d is not None else None,
                "bollinger_upper": round(bb_upper, 2) if bb_upper is not None else None,
                "bollinger_middle": round(bb_middle, 2) if bb_middle is not None else None,
                "bollinger_lower": round(bb_lower, 2) if bb_lower is not None else None,
                "mfi": round(mfi_val, 2) if mfi_val is not None else None,
                "roc": round(roc_val, 2) if roc_val is not None else None,
                "williams_r": round(willr_val, 2) if willr_val is not None else None,
                "vwap": round(vwap_val, 2) if vwap_val is not None else None,
                "ultimate_oscillator": round(uo_val, 2) if uo_val is not None else None,
                "ichimoku": ichimoku_vals  # zaten sözlük, içi boş olabilir
            },
            "recommendation": random.choice(["BUY", "SELL", "HOLD"])
        }

        return Response(result)

    

def generate_fake_price_history(request):
    try:
        asset = Asset.objects.get(id=1)  # Örnek olarak id=1
        for i in range(60):
            date = datetime.now() - timedelta(days=i)
            PriceHistory.objects.create(
                asset=asset,
                date=date,
                open=random.uniform(100, 150),
                high=random.uniform(150, 160),
                low=random.uniform(90, 100),
                close=random.uniform(100, 150),
                volume=random.randint(1000, 5000)
            )
        return JsonResponse({"status": "success", "message": "Veriler basariyla olusturuldu."})
    except Asset.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Asset bulunamadi."})
