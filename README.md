# Campaign Tracker Backend

This is the Django backend for the Campaign Tracker application. It provides REST API endpoints for managing marketing campaigns, visualizing performance data, and retrieving trend insights.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Local Setup](#local-setup)
- [Database Setup](#database-setup)
- [Running Locally](#running-locally)
- [Deployment](#deployment)
- [Testing](#testing)

## Prerequisites
- Python 3.9+
- pip (Python package manager)
- Supabase account (for PostgreSQL database)

## Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Campaign_python_backend
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**
   Create a `.env` file in the root directory based on `.env.example`.
   
   ```bash
   cp .env.example .env
   ```
   
   Fill in your Supabase credentials in `.env`:
   ```properties
   # Supabase Configuration
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_ANON_KEY=your-anon-key
   SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

   # Django Configuration
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   ALLOWED_HOSTS=*
   ```

## Database Setup

This project uses Supabase (PostgreSQL) as the database. The backend connects directly to Supabase tables using the `supabase-py` client for CRUD operations.

1. **Create Tables**
   Run the SQL script provided in `schema.sql` in your Supabase SQL Editor to create the necessary tables.

   ```sql
   -- Create Campaign Table
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

2. **Disable RLS (Optional/Development)**
   For rapid development, you can disable Row Level Security (RLS) or add policies to allow read/write access.
   *Note: In production, ensure you have proper RLS policies.*

## Running Locally

1. **Start the Django development server**
   ```bash
   python manage.py runserver
   ```
   The backend will run at `http://localhost:8000`.

2. **Running the Frontend (Next.js)**
   Navigate to your frontend directory and start the server:
   ```bash
   cd ../path-to-frontend
   npm run dev
   ```
   The frontend typically runs at `http://localhost:3000`.

   *Note: Ensure `CORS_ALLOWED_ORIGINS` in `config/settings.py` includes your frontend URL if you encounter CORS issues.*

## Deployment

### Vercel (Recommended)

This backend is configured for deployment on **Vercel**.

1. **Push to GitHub**
   Ensure your code is pushed to a GitHub repository.

2. **Import to Vercel**
   - Go to Vercel Dashboard -> Add New -> Project.
   - Select your GitHub repository.
   - Vercel should automatically detect the Django project via `vercel.json`.

3. **Configure Environment Variables on Vercel**
   Add the following environment variables in the Vercel Project Settings:
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SECRET_KEY`
   - `DEBUG` (Set to `False` for production)
   - `ALLOWED_HOSTS` (Set to `.vercel.app`)

4. **Deploy**
   Click "Deploy". Vercel will build and start your application.

### Google Cloud Run (Alternative)

This project includes a `Dockerfile` for containerized deployment on GCP Cloud Run.

1. **Build the Docker image**
   ```bash
   docker build -t campaign-backend .
   ```

2. **Run locally (optional)**
   ```bash
   docker run -p 8080:8080 --env-file .env campaign-backend
   ```

3. **Deploy to Cloud Run**
   - Push the image to Google Container Registry (GCR) or Artifact Registry.
   - Create a Cloud Run service using the image.
   - Set the required environment variables (`SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`).


## Testing

### UI Flow to Test CRUD
You can test the API endpoints using `curl` or Postman.

1. **Create a Campaign**
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

2. **List Campaigns**
   ```bash
   curl http://localhost:8000/api/campaigns/
   ```

3. **Get Campaign Details**
   Copy the `id` from the list response and use it:
   ```bash
   curl http://localhost:8000/api/campaigns/<CAMPAIGN_ID>/
   ```

4. **Update Campaign**
   ```bash
   curl -X PATCH http://localhost:8000/api/campaigns/<CAMPAIGN_ID>/ \
   -H "Content-Type: application/json" \
   -d '{"status": "Paused"}'
   ```

5. **Delete Campaign**
   ```bash
   curl -X DELETE http://localhost:8000/api/campaigns/<CAMPAIGN_ID>/
   ```

### Report/Visualization Page Path
- **Endpoint:** `/api/dashboard/performance/`
- **Description:** Returns monthly performance metrics (impressions, clicks, conversions) for charting.
- **Frontend Path:** Typically displayed on the main dashboard (`/dashboard`).

### Third-Party API Feature Path
- **Endpoint:** `/api/insights/trends/?query=marketing`
- **Description:** Fetches trend analysis and related keywords.
- **Frontend Path:** Accessed via the Insights or Trends section (`/insights`).
