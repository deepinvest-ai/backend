from django.db import models

class Asset(models.Model):
    STOCK  = "ST"
    CRYPTO = "CR"
    TYPE_CHOICES = [(STOCK, "Stock"), (CRYPTO, "Crypto")]

    symbol      = models.CharField(max_length=10, unique=True)
    name        = models.CharField(max_length=100)
    asset_type  = models.CharField(max_length=2, choices=TYPE_CHOICES)

    def __str__(self):
        return self.symbol

class PriceHistory(models.Model):
    asset   = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="prices")
    date    = models.DateTimeField()
    open    = models.DecimalField(max_digits=15, decimal_places=4)
    high    = models.DecimalField(max_digits=15, decimal_places=4)
    low     = models.DecimalField(max_digits=15, decimal_places=4)
    close   = models.DecimalField(max_digits=15, decimal_places=4)
    volume  = models.BigIntegerField()

    class Meta:
        unique_together = ("asset", "date")
        ordering = ["-date"]
