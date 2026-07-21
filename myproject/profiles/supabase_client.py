"""
Supabase access for the Profile Management app.

Mirrors ratings/supabase_client.py (credentials come from environment
variables), but adds a per-request *signed-in* client: the database
denies the anon role on Account and Profiles, so every profile
operation first signs the caller in with Supabase Auth — the same
approach shoppingcart/views.py uses before querying.
"""

import os

from dotenv import load_dotenv
from supabase import Client, create_client

# settings.py already calls load_dotenv(); calling it again here is a
# harmless no-op when the variables are set, and makes this module work
# on its own (it searches for a .env from this folder upward).
load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "SUPABASE_URL and SUPABASE_KEY must be set as environment variables. "
        "Check that your .env file exists and is being loaded."
    )


def signed_in_client(email, password):
    """
    Create a fresh client and sign the caller in through Supabase Auth.

    Returns (client, account_id) where account_id is the authenticated
    user's UUID — the same value as Account.id in the database. Raises
    AuthApiError on bad credentials.

    A fresh client per request (instead of a shared module-level one)
    keeps one caller's session from leaking into another's request.
    """
    client: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    session = client.auth.sign_in_with_password(
        {"email": email, "password": password}
    )
    return client, session.user.id
