from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CampaignViewSet, DashboardStatsView, DashboardPerformanceView, 
    InsightsTrendsView, NewsSearchAPIView
)

router = DefaultRouter(trailing_slash=False)
router.register(r'campaigns', CampaignViewSet, basename='campaign')

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard/stats', DashboardStatsView.as_view(), name='dashboard-stats'),
    path('dashboard/performance', DashboardPerformanceView.as_view(), name='dashboard-performance'),
    path('insights/trends', InsightsTrendsView.as_view(), name='insights-trends'),
    path('news/search', NewsSearchAPIView.as_view(), name='news-search'),
]
