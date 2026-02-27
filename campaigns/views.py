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

    @action(detail=True, methods=['get', 'put'], url_path='performance')
    def performance_monthly(self, request, pk=None):
        supabase = get_supabase_client()
        
        if request.method == 'GET':
            # Retrieve monthly performance data
            response = supabase.table('campaigns_monthlyperformance')\
                .select('*')\
                .eq('campaign_id', pk)\
                .order('month')\
                .execute()
            
            return Response(response.data)

        elif request.method == 'PUT':
            # Bulk update/save monthly performance data
            data = request.data
            if not isinstance(data, list):
                return Response(
                    {"error": "Expected a list of monthly performance records"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Prepare data for upsert
            records = []
            for item in data:
                # Calculate ROI: ((Revenue - Spend) / Spend) * 100
                spend = float(item.get('spend', 0))
                revenue = float(item.get('revenue', 0))
                roi = ((revenue - spend) / spend * 100) if spend > 0 else 0.0
                
                record = {
                    'campaign_id': pk,
                    'month': item.get('month'),
                    'impressions': int(item.get('impressions', 0)),
                    'clicks': int(item.get('clicks', 0)),
                    'conversions': int(item.get('conversions', 0)),
                    'spend': spend,
                    'revenue': revenue,
                    'roi': round(roi, 2)
                }
                
                # If id exists, include it for update
                if 'id' in item:
                    record['id'] = item['id']
                    
                records.append(record)
            
            # Upsert data (requires unique constraint on campaign_id, month)
            response = supabase.table('campaigns_monthlyperformance').upsert(records).execute()
            
            if response.data:
                return Response(response.data)
            return Response({"error": "Failed to save performance data"}, status=status.HTTP_400_BAD_REQUEST)

class DashboardStatsView(APIView):
    def get(self, request):
        supabase = get_supabase_client()
        
        # Fetch campaigns
        campaigns_response = supabase.table('campaigns_campaign').select('status,budget').execute()
        campaigns = campaigns_response.data
        
        # Fetch all monthly performance to calculate average ROI
        perf_response = supabase.table('campaigns_monthlyperformance').select('roi').execute()
        perfs = perf_response.data
        
        rois = [float(p.get('roi') or 0) for p in perfs]
        avg_roi = sum(rois) / len(rois) if rois else 0
        
        return Response({
            "total_campaigns": len(campaigns),
            "active_campaigns": sum(1 for c in campaigns if c.get('status') == 'Active'),
            "total_budget": sum(float(c.get('budget', 0) or 0) for c in campaigns),
            "avg_roi": round(avg_roi, 2)
        })

class DashboardPerformanceView(APIView):
    def get(self, request):
        supabase = get_supabase_client()
        
        # Fetch aggregated monthly performance
        # Since we can't do complex aggregation easily via simple Supabase client calls without RPC,
        # we'll fetch all data and aggregate in Python (acceptable for MVP/small scale)
        response = supabase.table('campaigns_monthlyperformance').select('*').execute()
        data = response.data
        
        # Aggregate by month
        aggregated = {}
        for item in data:
            month = item['month']
            # Convert date string YYYY-MM-DD to Month Name (e.g., "Jan") or keep as YYYY-MM
            # For this chart, let's keep it simple or format as needed. 
            # User example showed "2026-02", "2026-03".
            
            if month not in aggregated:
                aggregated[month] = {
                    "name": month,
                    "impressions": 0,
                    "clicks": 0,
                    "conversions": 0,
                    "spend": 0.0,
                    "revenue": 0.0
                }
            
            aggregated[month]["impressions"] += item.get('impressions', 0)
            aggregated[month]["clicks"] += item.get('clicks', 0)
            aggregated[month]["conversions"] += item.get('conversions', 0)
            aggregated[month]["spend"] += float(item.get('spend', 0.0))
            aggregated[month]["revenue"] += float(item.get('revenue', 0.0))
            
        # Convert to list and sort by date
        result = list(aggregated.values())
        result.sort(key=lambda x: x['name'])
        
        return Response(result)

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
