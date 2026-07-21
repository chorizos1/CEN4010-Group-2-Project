import os
from supabase import create_client, Client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set as environment variables. "
        "Check that your .env file exists and is being loaded."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
