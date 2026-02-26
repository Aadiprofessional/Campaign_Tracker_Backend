# Campaign Tracker Backend

Django backend for the Campaign Tracker application, providing REST API endpoints for campaign management and performance analytics.

## Setup

### Prerequisites
- Python 3.9+
- Supabase account

### Installation

1. **Clone and Install**
   ```bash
   git clone <repository-url>
   cd Campaign_python_backend
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   Copy `.env.example` to `.env` and configure your Supabase credentials:
   ```bash
   cp .env.example .env
   ```

## Database Setup

This project uses Supabase (PostgreSQL). Run the SQL script provided in `schema.sql` in your Supabase SQL Editor to create the necessary tables.

```sql
-- Example table creation
CREATE TABLE campaigns_campaign (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    platform VARCHAR(50) NOT NULL,
    status VARCHAR(50) DEFAULT 'Draft',
    budget FLOAT NOT NULL,
    amount_spent FLOAT DEFAULT 0.0,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    target_audience TEXT,
    goal VARCHAR(50) NOT NULL,
    roi FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Running the Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`.

## Deployment

The project is configured for deployment on Vercel or any Docker-compatible platform.

### Docker
```bash
docker build -t campaign-backend .
docker run -p 8080:8080 campaign-backend
```

### Vercel
1. Push to GitHub.
2. Import project in Vercel.
3. Set environment variables (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`).
4. Deploy.

## API Usage

### Endpoints
- `GET /api/campaigns/` - List all campaigns
- `POST /api/campaigns/` - Create a new campaign
- `GET /api/campaigns/<id>/` - Retrieve campaign details
- `PATCH /api/campaigns/<id>/` - Update campaign
- `DELETE /api/campaigns/<id>/` - Delete campaign
- `GET /api/dashboard/performance/` - Get performance metrics
- `GET /api/insights/trends/?query=<term>` - Get trend analysis

### Example Request
```bash
curl -X POST http://localhost:8000/api/campaigns/ \
-H "Content-Type: application/json" \
-d '{
    "name": "Test Campaign",
    "platform": "Google Ads",
    "status": "Active",
    "budget": 1000,
    "start_date": "2023-10-01",
    "end_date": "2023-10-31",
    "goal": "Traffic"
}'
```
