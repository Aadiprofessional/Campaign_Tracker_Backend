from django.http import HttpResponse

def api_root(request):
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Campaign Tracker API</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }
            h1 { color: #2563eb; border-bottom: 2px solid #eee; padding-bottom: 10px; }
            h2 { margin-top: 30px; color: #1e40af; }
            .endpoint { background: #f8fafc; padding: 15px; border-radius: 8px; margin-bottom: 15px; border: 1px solid #e2e8f0; }
            .method { font-weight: bold; color: #fff; padding: 2px 8px; border-radius: 4px; font-size: 0.9em; display: inline-block; min-width: 60px; text-align: center; }
            .get { background-color: #10b981; }
            .post { background-color: #3b82f6; }
            .patch { background-color: #f59e0b; }
            .delete { background-color: #ef4444; }
            code { background: #e2e8f0; padding: 2px 5px; border-radius: 4px; font-family: monospace; }
            pre { background: #1e293b; color: #f8fafc; padding: 15px; border-radius: 8px; overflow-x: auto; }
            .note { background: #fffbeb; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; }
        </style>
    </head>
    <body>
        <h1>Campaign Tracker API</h1>
        <p>Welcome to the Campaign Tracker Backend API. Below are the available endpoints.</p>
        
        <div class="note">
            <strong>Note:</strong> Ensure you have set the Supabase environment variables in your deployment for these endpoints to work.
        </div>

        <h2>Campaign Management</h2>
        
        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/campaigns/</code>
            <p>List all campaigns.</p>
        </div>
        
        <div class="endpoint">
            <span class="method post">POST</span> <code>/api/campaigns/</code>
            <p>Create a new campaign.</p>
            <pre>
curl -X POST https://campaign-tracker-backend-eight.vercel.app/api/campaigns/ \
-H "Content-Type: application/json" \
-d '{
    "name": "Test Campaign",
    "platform": "Google Ads",
    "status": "Active",
    "budget": 1000,
    "start_date": "2023-10-01",
    "end_date": "2023-10-31",
    "goal": "Traffic"
}'</pre>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/campaigns/&lt;id&gt;/</code>
            <p>Retrieve a specific campaign.</p>
        </div>

        <div class="endpoint">
            <span class="method patch">PATCH</span> <code>/api/campaigns/&lt;id&gt;/</code>
            <p>Update a campaign.</p>
        </div>

        <div class="endpoint">
            <span class="method delete">DELETE</span> <code>/api/campaigns/&lt;id&gt;/</code>
            <p>Delete a campaign.</p>
        </div>

        <h2>Dashboard & Analytics</h2>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/dashboard/stats/</code>
            <p>Get aggregated dashboard statistics.</p>
        </div>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/dashboard/performance/</code>
            <p>Get monthly performance metrics for charts.</p>
        </div>

        <h2>Insights</h2>

        <div class="endpoint">
            <span class="method get">GET</span> <code>/api/insights/trends/?query=marketing</code>
            <p>Get trend analysis and related keywords.</p>
        </div>
    </body>
    </html>
    """
    return HttpResponse(html_content)
