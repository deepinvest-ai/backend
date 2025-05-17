from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

import random

# Dummy veri oluşturmak için
DUMMY_NEWS = [
    {"id": 1, "topic": "bitcoin", "title": "Bitcoin All Time High!", "content": "Bitcoin hits an all-time high of $68,000."},
    {"id": 2, "topic": "stocks", "title": "Stocks Rally Up", "content": "The S&P 500 index sees a massive rally."},
    {"id": 3, "topic": "crypto", "title": "Ethereum Upgrade", "content": "Ethereum successfully transitions to Proof of Stake."},
    {"id": 4, "topic": "bitcoin", "title": "Bitcoin Crashes", "content": "Bitcoin drops by 15% in a single day."},
    {"id": 5, "topic": "stocks", "title": "Tech Stocks Soar", "content": "Technology sector sees a major boost."},
]

class NewsViewSet(viewsets.ViewSet):
    """
    News API for fetching financial news.
    """

    @action(detail=False, methods=["get"], url_path="news")
    def get_news(self, request):
        """
        Tüm haberleri getirir veya bir konuya göre filtreler.
        Örnek kullanım:
        - /api/news/
        - /api/news/?topic=bitcoin
        """
        topic = request.query_params.get("topic", None)
        if topic:
            filtered_news = [news for news in DUMMY_NEWS if news["topic"] == topic.lower()]
            return Response({"topic": topic, "news": filtered_news})
        
        return Response({"news": DUMMY_NEWS})
