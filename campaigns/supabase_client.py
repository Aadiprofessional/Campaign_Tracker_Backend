import os
from supabase import create_client, Client

def get_supabase_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    # Prefer service role key for backend operations to bypass RLS if needed, 
    # or use anon key if RLS policies are set up for public access.
    # Given the user provided both and this is a backend, service role is often safer for admin tasks,
    # but for a user-facing app, we might want to be careful. 
    # However, the user said "use that to save to the tables", implying backend authority.
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_ANON_KEY")
    
    if not url or not key:
        raise ValueError("Supabase URL and Key must be set in environment variables.")
        
    return create_client(url, key)
