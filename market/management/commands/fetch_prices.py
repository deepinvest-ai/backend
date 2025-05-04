from decimal import Decimal
import pandas as pd
import yfinance as yf
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from market.models import Asset, PriceHistory


class Command(BaseCommand):
    help = "Belirtilen sembol için yfinance'tan fiyat verisi çeker (varsayılan: 90gün/1gün)."

    def add_arguments(self, parser):
        parser.add_argument("--symbol", required=True, help="Örn: AAPL, BTC-USD")
        parser.add_argument("--period", default="90d", help="yfinance period (30d, 1y, vb.)")
        parser.add_argument("--interval", default="1d", help="1d, 1h, 5m vb.")

    def handle(self, *args, **opts):
        symbol = opts["symbol"].upper()
        period = opts["period"]
        interval = opts["interval"]

        self.stdout.write(f"⏳  {symbol} {period}/{interval} verisi çekiliyor…")

        # auto_adjust=False ile eski davranışı koru
        data = yf.download(symbol, period=period, interval=interval, auto_adjust=False)
        if data.empty:
            raise CommandError("Veri bulunamadı; sembol hatalı olabilir.")

        # Debug için sütun isimlerini göster
        self.stdout.write(f"Sütun isimleri: {data.columns.tolist()}")

        # Çoklu seviye varsa düzleştir
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.droplevel(1)  # Sembol seviyesini kaldır

        asset, _ = Asset.objects.get_or_create(
            symbol=symbol,
            defaults={"name": symbol, "asset_type": "ST"},
        )

        added, updated = 0, 0
        for dt, row in data.iterrows():
            try:
                obj, created = PriceHistory.objects.update_or_create(
                    asset=asset,
                    date=timezone.make_aware(dt),
                    defaults={
                        "open": Decimal(str(float(row["Open"]))),
                        "high": Decimal(str(float(row["High"]))),
                        "low": Decimal(str(float(row["Low"]))),
                        "close": Decimal(str(float(row["Close"]))),
                        "volume": int(row["Volume"]),
                    },
                )
                if created:
                    added += 1
                else:
                    updated += 1
            except KeyError as e:
                self.stdout.write(self.style.ERROR(f"Hata: {e}"))
                self.stdout.write(f"Satır verisi: {row}")
                raise

        self.stdout.write(self.style.SUCCESS(
            f"✓ {symbol}: {added} yeni, {updated} güncellenen kayıt"
        ))
