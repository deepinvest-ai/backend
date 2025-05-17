from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin,User
from django.db import models
from market.models import Asset


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError("Kullanıcıların bir e-posta adresi olmalı.")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email)
        user.set_password(password)  # Hash'leme burada olur
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None):
        user = self.create_user(username, email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="portfolios")
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

class PortfolioAsset(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="assets")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    average_price = models.DecimalField(max_digits=20, decimal_places=4)

    def __str__(self):
        return f"{self.portfolio.name} - {self.asset.symbol}"    

class TransactionHistory(models.Model):
    ACTION_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="transactions")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    action = models.CharField(max_length=4, choices=ACTION_CHOICES)
    quantity = models.DecimalField(max_digits=20, decimal_places=4)
    price = models.DecimalField(max_digits=20, decimal_places=4)

    def __str__(self):
        return f"{self.user.username} - {self.asset.symbol} - {self.action}"  
    
             
class RecommendationHistory(models.Model):
    RECOMMENDATION_CHOICES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
        ('HOLD', 'Hold'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="recommendations")
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="recommendations")
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    recommendation = models.CharField(max_length=5, choices=RECOMMENDATION_CHOICES)
    confidence = models.DecimalField(max_digits=5, decimal_places=2)  # Örn: 0.87 (yüzde 87 güven)

    def __str__(self):
        return f"{self.user.username} - {self.asset.symbol} - {self.recommendation} ({self.confidence})"

class RiskAnalysis(models.Model):
    RISK_LEVEL_CHOICES = [
        ('Low', 'Düşük'),
        ('Medium', 'Orta'),
        ('High', 'Yüksek'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name="risk_analysis")
    date = models.DateField(auto_now_add=True)
    risk_level = models.CharField(max_length=10, choices=RISK_LEVEL_CHOICES)

    def __str__(self):
        return f"{self.asset.symbol} - {self.risk_level} ({self.date})"        