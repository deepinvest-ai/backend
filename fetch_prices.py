from decimal import Decimal
import pandas as pd              # ← eksik import
import pytz
import yfinance as yf
from django.utils import timezone
from market.models import Asset, PriceHistory

local_tz = pytz.timezone("UTC")

# 1) Varlığı al / oluştur
asset, _ = Asset.objects.get_or_create(
    symbol="AAPL",
    defaults={"name": "Apple Inc.", "asset_type": "ST"},
)

# 2) Son 5 günlük veriyi çek
data = yf.download("AAPL", period="5d", interval="1d")

# ‘Ticker’ seviyesini at:  yfinance 0.2.x MultiIndex dönebiliyor
if isinstance(data.columns, pd.MultiIndex):
    data.columns = data.columns.droplevel(0)

# 3) Veriyi PriceHistory tablosuna yaz
for dt in data.index:
    PriceHistory.objects.update_or_create(
        asset=asset,
        date=timezone.make_aware(dt, local_tz),
        defaults={
            "open":   Decimal(str(float(data.loc[dt, "Open"]))),
            "high":   Decimal(str(float(data.loc[dt, "High"]))),
            "low":    Decimal(str(float(data.loc[dt, "Low"]))),
            "close":  Decimal(str(float(data.loc[dt, "Close"]))),
            "volume": int(data.loc[dt, "Volume"]),
        },
    )

print("✓ AAPL fiyat verisi eklendi.")
