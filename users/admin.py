from django.contrib import admin
from .models import User, Portfolio, PortfolioAsset, TransactionHistory, RecommendationHistory, RiskAnalysis

admin.site.register(User)
admin.site.register(Portfolio)
admin.site.register(PortfolioAsset)
admin.site.register(TransactionHistory)
admin.site.register(RecommendationHistory)
admin.site.register(RiskAnalysis)
