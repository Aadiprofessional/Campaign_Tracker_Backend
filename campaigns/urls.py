from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CampaignViewSet, DashboardStatsView, DashboardPerformanceView, 
    InsightsTrendsView, NewsSearchAPIView
)

# Router for endpoints without trailing slashes (e.g., /api/campaigns)
router_no_slash = DefaultRouter(trailing_slash=False)
router_no_slash.register(r'campaigns', CampaignViewSet, basename='campaign')

# Router for endpoints with trailing slashes (e.g., /api/campaigns/)
# This ensures compatibility with frontend requests that might include slashes
router_slash = DefaultRouter(trailing_slash=True)
router_slash.register(r'campaigns', CampaignViewSet, basename='campaign_slash')

urlpatterns = [
    path('', include(router_no_slash.urls)),
    path('', include(router_slash.urls)),
    
    # Use re_path to support both with and without trailing slash for manual endpoints
    re_path(r'^dashboard/stats/?$', DashboardStatsView.as_view(), name='dashboard-stats'),
    re_path(r'^dashboard/performance/?$', DashboardPerformanceView.as_view(), name='dashboard-performance'),
    re_path(r'^insights/trends/?$', InsightsTrendsView.as_view(), name='insights-trends'),
    re_path(r'^news/search/?$', NewsSearchAPIView.as_view(), name='news-search'),
]
