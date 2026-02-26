import requests
import os
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CampaignSerializer
from .supabase_client import get_supabase_client
import random
from datetime import timedelta, date, datetime
import uuid

def format_campaign(data):
    if 'budget' in data:
        data['budget'] = float(data['budget'])
    if 'amount_spent' in data:
        data['amount_spent'] = float(data['amount_spent'])
    if 'roi' in data and data['roi'] is not None:
        data['roi'] = float(data['roi'])
    return data

class CampaignViewSet(viewsets.ViewSet):
    def list(self, request):
        supabase = get_supabase_client()
        query = supabase.table('campaigns_campaign').select('*')
        
        if status_param := request.query_params.get('status'):
            query = query.eq('status', status_param)
        if platform_param := request.query_params.get('platform'):
            query = query.eq('platform', platform_param)
        if search_param := request.query_params.get('search'):
            query = query.ilike('name', f'%{search_param}%')
            
        response = query.order('created_at', desc=True).execute()
        return Response([format_campaign(item) for item in response.data])

    def create(self, request):
        serializer = CampaignSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        data = serializer.validated_data
        data['start_date'] = data['start_date'].isoformat()
        data['end_date'] = data['end_date'].isoformat()
        data.setdefault('id', str(uuid.uuid4()))
        data.setdefault('created_at', datetime.now().isoformat())
        
        supabase = get_supabase_client()
        response = supabase.table('campaigns_campaign').insert(data).execute()
        
        if response.data:
            return Response(format_campaign(response.data[0]), status=status.HTTP_201_CREATED)
        return Response({"error": "Failed to create campaign"}, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        supabase = get_supabase_client()
        response = supabase.table('campaigns_campaign').select('*').eq('id', pk).execute()
        return Response(format_campaign(response.data[0])) if response.data else Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        supabase = get_supabase_client()
        response = supabase.table('campaigns_campaign').update(request.data).eq('id', pk).execute()
        return Response(format_campaign(response.data[0])) if response.data else Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        get_supabase_client().table('campaigns_campaign').delete().eq('id', pk).execute()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        supabase = get_supabase_client()
        response = supabase.table('campaigns_campaign').select('*').eq('id', pk).execute()
        
        if not response.data:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        campaign = response.data[0]
        start = datetime.fromisoformat(campaign['start_date']).date() if isinstance(campaign['start_date'], str) else campaign['start_date']
        end = datetime.fromisoformat(campaign['end_date']).date() if isinstance(campaign['end_date'], str) else campaign['end_date']
        end = end or date.today()
            
        data = []
        current = start
        for i in range(1, 11):
            if current > end: break
            impressions = random.randint(1000, 5000)
            data.append({
                "name": f"Week {i}",
                "impressions": impressions,
                "clicks": int(impressions * random.uniform(0.05, 0.15)),
                "conversions": int(impressions * random.uniform(0.05, 0.15) * random.uniform(0.1, 0.3))
            })
            current += timedelta(days=7)
            
        return Response(data)

class DashboardStatsView(APIView):
    def get(self, request):
        supabase = get_supabase_client()
        response = supabase.table('campaigns_campaign').select('status,budget,roi').execute()
        campaigns = response.data
        
        rois = [float(c.get('roi') or 0) for c in campaigns if c.get('roi') is not None]
        
        return Response({
            "total_campaigns": len(campaigns),
            "active_campaigns": sum(1 for c in campaigns if c.get('status') == 'Active'),
            "total_budget": sum(float(c.get('budget', 0) or 0) for c in campaigns),
            "avg_roi": round(sum(rois) / len(rois), 2) if rois else 0
        })

class DashboardPerformanceView(APIView):
    def get(self, request):
        data = []
        for month in ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]:
            impressions = random.randint(3000, 8000)
            data.append({
                "name": month,
                "impressions": impressions,
                "clicks": int(impressions * random.uniform(0.05, 0.15)),
                "conversions": int(impressions * random.uniform(0.05, 0.15) * random.uniform(0.1, 0.3))
            })
        return Response(data)

class InsightsTrendsView(APIView):
    def get(self, request):
        return Response({
            "trend_score": 87,
            "search_volume": "2.4M/month",
            "competition": "Medium",
            "interest_over_time": [{"name": m, "value": v} for m, v in zip(
                ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
                [45, 52, 38, 65, 78, 90, 85, 70, 75, 82, 95, 88]
            )]
        })

class NewsSearchAPIView(APIView):
    def post(self, request):
        url = "https://real-time-news-data.p.rapidapi.com/search"
        
        query = request.data.get('query', 'Football')
        limit = request.data.get('limit', '10')
        time_published = request.data.get('time_published', 'anytime')
        country = request.data.get('country', 'US')
        lang = request.data.get('lang', 'en')
        
        querystring = {
            "query": query,
            "limit": limit,
            "time_published": time_published,
            "country": country,
            "lang": lang
        }
        
        headers = {
            "x-rapidapi-host": os.environ.get("RAPIDAPI_HOST", "real-time-news-data.p.rapidapi.com"),
            "x-rapidapi-key": os.environ.get("RAPIDAPI_KEY")
        }
        
        try:
            response = requests.get(url, headers=headers, params=querystring)
            response.raise_for_status()
            return Response(response.json())
        except requests.RequestException as e:
            return Response(
                {"error": str(e), "details": response.text if 'response' in locals() else "No response"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
