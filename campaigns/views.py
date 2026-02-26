from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import CampaignSerializer
from .supabase_client import get_supabase_client
import random
from datetime import timedelta, date, datetime
import uuid

# Helper to format Supabase response to match Serializer/Frontend expectations
def format_campaign(data):
    # Ensure numeric fields are floats
    if 'budget' in data:
        data['budget'] = float(data['budget'])
    if 'amount_spent' in data:
        data['amount_spent'] = float(data['amount_spent'])
    if 'roi' in data and data['roi'] is not None:
        data['roi'] = float(data['roi'])
    return data

class CampaignViewSet(viewsets.ViewSet):
    # We use ViewSet instead of ModelViewSet because we aren't using Django ORM
    
    def list(self, request):
        supabase = get_supabase_client()
        query = supabase.table('campaigns_campaign').select('*')
        
        # Apply filters
        status_param = request.query_params.get('status')
        platform_param = request.query_params.get('platform')
        search_param = request.query_params.get('search')
        
        if status_param:
            query = query.eq('status', status_param)
        if platform_param:
            query = query.eq('platform', platform_param)
        if search_param:
            query = query.ilike('name', f'%{search_param}%')
            
        # Execute query
        response = query.order('created_at', desc=True).execute()
        
        # Supabase returns data in response.data
        data = [format_campaign(item) for item in response.data]
        return Response(data)

    def create(self, request):
        serializer = CampaignSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            # Convert dates to strings for JSON serialization
            data['start_date'] = data['start_date'].isoformat()
            data['end_date'] = data['end_date'].isoformat()
            
            # Generate UUID if not present
            if 'id' not in data:
                data['id'] = str(uuid.uuid4())
            
            # Add created_at if not present
            if 'created_at' not in data:
                data['created_at'] = datetime.now().isoformat()
            
            supabase = get_supabase_client()
            # Insert returns the created object
            response = supabase.table('campaigns_campaign').insert(data).execute()
            
            if response.data:
                return Response(format_campaign(response.data[0]), status=status.HTTP_201_CREATED)
            return Response({"error": "Failed to create campaign"}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def retrieve(self, request, pk=None):
        supabase = get_supabase_client()
        response = supabase.table('campaigns_campaign').select('*').eq('id', pk).execute()
        
        if response.data:
            return Response(format_campaign(response.data[0]))
        return Response(status=status.HTTP_404_NOT_FOUND)

    def update(self, request, pk=None):
        # Partial update support
        supabase = get_supabase_client()
        
        # We can validate using serializer partial=True
        # But since we don't have an instance to pass to serializer, we just validate the data structure
        # Serializer expect an instance for update, so we might skip full serializer validation 
        # or use a workaround. For now, let's just send the data to Supabase.
        # Ideally: Fetch existing -> Deserialize -> Update -> Validate -> Serialize -> Send
        
        data = request.data.copy()
        
        response = supabase.table('campaigns_campaign').update(data).eq('id', pk).execute()
        
        if response.data:
            return Response(format_campaign(response.data[0]))
        return Response(status=status.HTTP_404_NOT_FOUND)

    def partial_update(self, request, pk=None):
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        supabase = get_supabase_client()
        supabase.table('campaigns_campaign').delete().eq('id', pk).execute()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def performance(self, request, pk=None):
        # Retrieve campaign to get dates
        supabase = get_supabase_client()
        response = supabase.table('campaigns_campaign').select('*').eq('id', pk).execute()
        
        if not response.data:
            return Response(status=status.HTTP_404_NOT_FOUND)
            
        campaign = response.data[0]
        start_date_str = campaign['start_date']
        end_date_str = campaign['end_date']
        
        # Parse dates
        start = datetime.fromisoformat(start_date_str).date() if isinstance(start_date_str, str) else start_date_str
        end = datetime.fromisoformat(end_date_str).date() if isinstance(end_date_str, str) else end_date_str
        if not end:
            end = date.today()
            
        # Mock performance data
        data = []
        current = start
        week_num = 1
        # Limit loop to avoid infinite if dates are weird
        while current <= end and week_num <= 10:
            impressions = random.randint(1000, 5000)
            clicks = int(impressions * random.uniform(0.05, 0.15))
            conversions = int(clicks * random.uniform(0.1, 0.3))
            
            data.append({
                "name": f"Week {week_num}",
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions
            })
            current += timedelta(days=7)
            week_num += 1
            
        return Response(data)

class DashboardStatsView(APIView):
    def get(self, request):
        supabase = get_supabase_client()
        
        # Fetch all campaigns to calculate stats (naive approach for MVP)
        # For production, use Supabase .count() or RPCs
        response = supabase.table('campaigns_campaign').select('status,budget,roi').execute()
        campaigns = response.data
        
        total_campaigns = len(campaigns)
        active_campaigns = sum(1 for c in campaigns if c.get('status') == 'Active')
        total_budget = sum(float(c.get('budget', 0) or 0) for c in campaigns)
        
        rois = [float(c.get('roi') or 0) for c in campaigns if c.get('roi') is not None]
        avg_roi = sum(rois) / len(rois) if rois else 0
        
        return Response({
            "total_campaigns": total_campaigns,
            "active_campaigns": active_campaigns,
            "total_budget": total_budget,
            "avg_roi": round(avg_roi, 2)
        })

class DashboardPerformanceView(APIView):
    def get(self, request):
        # Mock monthly performance data
        months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
        data = []
        for month in months:
            impressions = random.randint(3000, 8000)
            clicks = int(impressions * random.uniform(0.05, 0.15))
            conversions = int(clicks * random.uniform(0.1, 0.3))
            data.append({
                "name": month,
                "impressions": impressions,
                "clicks": clicks,
                "conversions": conversions
            })
        return Response(data)

class InsightsTrendsView(APIView):
    def get(self, request):
        query = request.query_params.get('query', 'digital marketing')
        # Mock response mimicking Google Trends/Market analysis
        return Response({
            "trend_score": 87,
            "search_volume": "2.4M/month",
            "competition": "Medium",
            "interest_over_time": [
                { "name": "Jan", "value": 45 },
                { "name": "Feb", "value": 52 },
                { "name": "Mar", "value": 38 },
                { "name": "Apr", "value": 65 },
                { "name": "May", "value": 78 },
                { "name": "Jun", "value": 90 },
                { "name": "Jul", "value": 85 },
                { "name": "Aug", "value": 70 },
                { "name": "Sep", "value": 75 },
                { "name": "Oct", "value": 82 },
                { "name": "Nov", "value": 95 },
                { "name": "Dec", "value": 88 }
            ],
            "related_keywords": [
                { "name": f"{query} trends", "volume": 8500 },
                { "name": f"ai in {query}", "volume": 7200 },
                { "name": "marketing strategies", "volume": 5400 }
            ],
            "trending_topics": [
                {
                    "id": 1,
                    "name": "AI Content Generation",
                    "category": "Technology",
                    "score": 92,
                    "volume": "1.2M"
                },
                {
                    "id": 2,
                    "name": "Short-form Video",
                    "category": "Social Media",
                    "score": 88,
                    "volume": "950K"
                }
            ]
        })
