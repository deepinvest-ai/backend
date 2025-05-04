import math
import pandas as pd
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Asset, PriceHistory
from .serializers import AssetSerializer, PriceHistorySerializer
from .indicators import sma, rsi, macd, atr, bollinger, stochastic,ema,cci,obv,adx,mfi,roc,williams_r,ichimoku,vwap,ultimate_oscillator


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer

    @action(detail=True, url_path="sma")
    def sma_view(self, request, pk=None):
        days = int(request.query_params.get("days", 50))
        asset = self.get_object()
        closes = list(asset.prices.order_by("date").values_list("close", flat=True))

        if len(closes) < days:
            return Response(
                {"error": f"{days} günlük SMA için en az {days} kapanış gerekir."},
                status=400,
            )

        value = sma(pd.Series(closes), length=days)
        return Response({"symbol": asset.symbol, "days": days, "sma": value})

    @action(detail=True, url_path="rsi")
    def rsi_view(self, request, pk=None):
        days = int(request.query_params.get("days", 14))
        asset = self.get_object()
        closes = list(asset.prices.order_by("date").values_list("close", flat=True))

        if len(closes) < days + 1:
            return Response(
                {"error": f"{days} günlük RSI için en az {days+1} kapanış gerekir."},
                status=400,
            )

        value = rsi(pd.Series(closes), length=days)
        return Response({"symbol": asset.symbol, "days": days, "rsi": value})

    @action(detail=True, url_path="macd")
    def macd_view(self, request, pk=None):
        asset = self.get_object()
        closes = list(asset.prices.order_by("date").values_list("close", flat=True))

        if len(closes) < 26:
            return Response(
                {"error": "MACD için en az 26 kapanış gerekir."},
                status=400,
            )

        macd_val, signal_val = macd(pd.Series(closes))
        return Response({
            "symbol": asset.symbol,
            "macd": macd_val,
            "signal": signal_val
        })

    @action(detail=True, url_path="risk-management")
    def risk_management_view(self, request, pk=None):
        asset = self.get_object()
        closes = list(asset.prices.order_by("date").values_list("close", flat=True))
        highs = list(asset.prices.order_by("date").values_list("high", flat=True))
        lows = list(asset.prices.order_by("date").values_list("low", flat=True))

        if len(closes) < 14 or len(highs) < 14 or len(lows) < 14:
            return Response(
                {"error": "ATR için en az 14 günlük veri gereklidir."},
                status=400
            )

        atr_value = atr(pd.Series(highs), pd.Series(lows), pd.Series(closes))

        if atr_value is None or pd.isna(atr_value):
            return Response(
                {"error": "ATR değeri hesaplanamadı."},
                status=400
            )

        if atr_value > 10:
            risk = "Yüksek Volatilite"
        elif atr_value > 5:
            risk = "Orta Seviye Risk"
        else:
            risk = "Düşük Risk"

        return Response({
            "symbol": asset.symbol,
            "atr": round(float(atr_value), 4),
            "risk_level": risk
        })

    @action(detail=True, url_path="bollinger")
    def bollinger_view(self, request, pk=None):
        days = int(request.query_params.get("days", 20))
        asset = self.get_object()
        closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))

        if len(closes) < days:
            return Response(
                {"error": f"{days} günlük Bollinger için en az {days} kapanış gerekir."},
                status=400,
            )

        upper, middle, lower = bollinger(pd.Series(closes), length=days)

        return Response({
            "symbol": asset.symbol,
            "days": days,
            "upper": upper,
            "middle": middle,
            "lower": lower
        })

    @action(detail=True, url_path="stochastic")
    def stochastic_view(self, request, pk=None):
        k = int(request.query_params.get("k", 14))
        d = int(request.query_params.get("d", 3))

        asset = self.get_object()
        highs  = list(map(float, asset.prices.order_by("date").values_list("high", flat=True)))
        lows   = list(map(float, asset.prices.order_by("date").values_list("low", flat=True)))
        closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))


        if len(closes) < k + d:
            return Response(
                {"error": f"{k + d} günlük veri gerekli."},
                status=400
            )

        k_val, d_val = stochastic(pd.Series(highs), pd.Series(lows), pd.Series(closes), k, d)

        if k_val is None or d_val is None:
            return Response({"error": "Stochastic hesaplanamadı."}, status=400)

        return Response({
            "symbol": asset.symbol,
            "k": round(float(k_val), 2),
            "d": round(float(d_val), 2)
        })
    @action(detail=True, url_path="ema")
    def ema_view(self, request, pk=None):
     days = int(request.query_params.get("days", 20))
     asset = self.get_object()
     closes = list(asset.prices.order_by("date").values_list("close", flat=True))

     if len(closes) < days:
        return Response(
            {"error": f"{days} günlük EMA için en az {days} kapanış gerekir."},
            status=400,
        )

     value = ema(pd.Series(closes), length=days)
     return Response({
        "symbol": asset.symbol,
        "days": days,
        "ema": value
    })
    @action(detail=True, url_path="cci")
    def cci_view(self, request, pk=None):
     days = int(request.query_params.get("days", 20))
     asset = self.get_object()

     highs = list(map(float, asset.prices.order_by("date").values_list("high", flat=True)))
     lows = list(map(float, asset.prices.order_by("date").values_list("low", flat=True)))
     closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))

     if len(closes) < days or len(highs) < days or len(lows) < days:
        return Response(
            {"error": f"{days} günlük CCI için yeterli veri yok."},
            status=400,
        )

     value = cci(pd.Series(highs), pd.Series(lows), pd.Series(closes), length=days)

     return Response({
        "symbol": asset.symbol,
        "days": days,
        "cci": round(float(value), 2) if value is not None else None
    })
    @action(detail=True, url_path="obv")
    def obv_view(self, request, pk=None):
     asset = self.get_object()

     closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))
     volumes = list(map(float, asset.prices.order_by("date").values_list("volume", flat=True)))

     if len(closes) < 2 or len(volumes) < 2:
        return Response({"error": "OBV hesaplamak için en az 2 günlük veri gerekir."}, status=400)

     value = obv(pd.Series(closes), pd.Series(volumes))

     return Response({
        "symbol": asset.symbol,
        "obv": round(float(value), 2) if value is not None else None
    })
    @action(detail=True, url_path="adx")
    def adx_view(self, request, pk=None):
     days = int(request.query_params.get("days", 14))
     asset = self.get_object()
     highs  = list(asset.prices.order_by("date").values_list("high", flat=True))
     lows   = list(asset.prices.order_by("date").values_list("low", flat=True))
     closes = list(asset.prices.order_by("date").values_list("close", flat=True))

     if len(closes) < days:
        return Response(
            {"error": f"{days} günlük ADX için en az {days} veri gerekir."},
            status=400,
        )

     value = adx(pd.Series(highs, dtype='float64'),
                pd.Series(lows, dtype='float64'),
                pd.Series(closes, dtype='float64'),
                length=days)

     if value is None or pd.isna(value):
        return Response({"error": "ADX hesaplanamadı."}, status=400)

     return Response({
        "symbol": asset.symbol,
        "days": days,
        "adx": round(float(value), 2)
    })
    @action(detail=True, url_path="mfi")
    def mfi_view(self, request, pk=None):
     days = int(request.query_params.get("days", 14))
     asset = self.get_object()

     highs = list(map(float, asset.prices.order_by("date").values_list("high", flat=True)))
     lows = list(map(float, asset.prices.order_by("date").values_list("low", flat=True)))
     closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))
     volumes = list(map(float, asset.prices.order_by("date").values_list("volume", flat=True)))

     if len(closes) < days + 1:
        return Response(
            {"error": f"{days + 1} günlük veri gerekli."},
            status=400
        )

     value = mfi(highs, lows, closes, volumes, length=days)
     if value is None or pd.isna(value):
        return Response({"error": "MFI hesaplanamadı."}, status=400)

     return Response({
        "symbol": asset.symbol,
        "days": days,
        "mfi": round(float(value), 2)
    })
    @action(detail=True, methods=["get"], url_path="roc")
    def roc_view(self, request, pk=None):
     asset = self.get_object()
     days = int(request.query_params.get("days", 12))
     closes = list(asset.prices.order_by("date").values_list("close", flat=True))

     if len(closes) < days + 1:
        return Response({"error": f"{days + 1} günlük veri gerekli."}, status=400)

     value = roc(pd.Series(closes), length=days)

     if value is not None and not pd.isna(value):
        return Response({"symbol": asset.symbol, "days": days, "roc": round(value, 2)})
     else:
        return Response({"error": "ROC hesaplanamadı."}, status=400)
     
    @action(detail=True, url_path="williamsr")
    def williamsr_view(self, request, pk=None):
     days = int(request.query_params.get("days", 14))
     asset = self.get_object()

     highs = list(map(float, asset.prices.order_by("date").values_list("high", flat=True)))
     lows = list(map(float, asset.prices.order_by("date").values_list("low", flat=True)))
     closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))

     if len(closes) < days:
        return Response({"error": f"{days} günlük veri gerekli."}, status=400)

     value = williams_r(highs, lows, closes, length=days)

     if value is not None and not pd.isna(value):
        return Response({
            "symbol": asset.symbol,
            "days": days,
            "williams_%R": round(value, 2)
        })
     else:
        return Response({"error": "Williams %R hesaplanamadı."}, status=400)

    
    @action(detail=True, url_path="ichimoku")
    def ichimoku_view(self, request, pk=None):
        asset = self.get_object()

        highs = list(map(float, asset.prices.order_by("date").values_list("high", flat=True)))
        lows = list(map(float, asset.prices.order_by("date").values_list("low", flat=True)))
        closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))

        if len(closes) < 52:
            return Response({"error": "Ichimoku için en az 52 veri gerekir."}, status=400)

        values = ichimoku(highs, lows, closes)
        if values is None:
            return Response({"error": "Ichimoku hesaplanamadı."}, status=400)

        cleaned_values = {
            k: round(float(v), 2) if v is not None and not math.isnan(v) else None
            for k, v in values.items()
        }

        return Response({
            "symbol": asset.symbol,
            **cleaned_values
        })
    @action(detail=True, url_path="vwap")
    def vwap_view(self, request, pk=None):
     asset = self.get_object()

     highs = list(map(float, asset.prices.order_by("date").values_list("high", flat=True)))
     lows = list(map(float, asset.prices.order_by("date").values_list("low", flat=True)))
     closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))
     volumes = list(map(float, asset.prices.order_by("date").values_list("volume", flat=True)))

     if len(highs) < 1 or len(lows) < 1 or len(closes) < 1 or len(volumes) < 1:
        return Response({"error": "VWAP hesaplamak için yeterli veri yok."}, status=400)

     value = vwap(highs, lows, closes, volumes)

     if value is None or pd.isna(value):
        return Response({"error": "VWAP hesaplanamadı."}, status=400)

     return Response({
        "symbol": asset.symbol,
        "vwap": round(float(value), 2)
    })
    @action(detail=True, url_path="ultimate")
    def ultimate_view(self, request, pk=None):
     asset = self.get_object()

     highs = list(map(float, asset.prices.order_by("date").values_list("high", flat=True)))
     lows = list(map(float, asset.prices.order_by("date").values_list("low", flat=True)))
     closes = list(map(float, asset.prices.order_by("date").values_list("close", flat=True)))

     if len(closes) < 28:
        return Response({"error": "Ultimate Oscillator için en az 28 günlük veri gerekir."}, status=400)

     value = ultimate_oscillator(highs, lows, closes)

     if value is None:
        return Response({"error": "Ultimate Oscillator hesaplanamadı."}, status=400)

     return Response({
        "symbol": asset.symbol,
        "ultimate_oscillator": round(float(value), 2)
    })




 







class PriceHistoryViewSet(viewsets.ModelViewSet):
    queryset = PriceHistory.objects.all()
    serializer_class = PriceHistorySerializer
    filterset_fields = ["asset"]
