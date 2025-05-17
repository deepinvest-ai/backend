"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as authtoken_views


from market.views import AssetViewSet, PriceHistoryViewSet
from market.news import NewsViewSet  # ← Eklenen satır

from users.views import PortfolioViewSet, CustomAuthToken,PortfolioAssetViewSet,TransactionHistoryViewSet,AIRecommendationView,RecommendationHistoryListView,AIRecommendationHistoryView,AIAnalysisView
from users.views import generate_fake_price_history

# Router tanımlaması
router = routers.DefaultRouter()
router.register(r"assets", AssetViewSet)         # /api/assets/
router.register(r"prices", PriceHistoryViewSet)  # /api/prices/
router.register(r"news", NewsViewSet, basename="news")  # /api/news/
router.register(r"portfolios", PortfolioViewSet, basename="portfolio")
router.register(r"portfolio-assets", PortfolioAssetViewSet, basename="portfolioasset")
router.register(r"transactions", TransactionHistoryViewSet, basename="transaction")

# URL pattern
urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),  # API rotaları
    path("api/token/login/", CustomAuthToken.as_view(), name="token-login"),
    path("api/ai/recommend/", AIRecommendationView.as_view(), name="ai-recommend"),
    path("api/ai/recommend/history/", RecommendationHistoryListView.as_view(), name="recommendation-history"),
    path("api/ai/recommend/history/", AIRecommendationHistoryView.as_view(), name="ai-recommendation-history"),
    path("api/ai/analysis/", AIAnalysisView.as_view(), name="ai-analysis"),
    path("api/generate-fake-data/", generate_fake_price_history),


]
