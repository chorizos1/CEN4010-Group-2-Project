"""
Profile Management service functions.

Each function takes an already-authenticated Supabase client plus the
account UUID it acts on, so the database logic stays separate from the
HTTP layer (views.py) and can be reused by other features — e.g. a
signup flow calling create_profile().

Table facts (verified against the live schema):

  Account:  id (uuid, same value as the Supabase Auth user id), email
  Profiles: id, account_uuid -> Account.id, theme, language,
            email_notifications, updated_at

Passwords are NOT stored in Account: login verifies through Supabase
Auth (see shoppingcart/views.py), which hashes them server-side.
"""

from datetime import datetime, timezone

DEFAULT_PREFERENCES = {
    "theme": "light",
    "language": "en",
    "email_notifications": True,
}

PREFERENCE_FIELDS = ("theme", "language", "email_notifications")


def _now():
    return datetime.now(timezone.utc).isoformat()


def get_profile(client, account_id):
    """Return the Profiles row for this account, or None if none exists."""
    result = (
        client.table("Profiles")
        .select("*")
        .eq("account_uuid", account_id)
        .execute()
    )
    return result.data[0] if result.data else None


def create_profile(client, account_id):
    """
    Create the default Profiles row for a new account (meant to be
    called on signup). Returns (row, created); created is False when a
    row already existed, so calling this twice is safe.
    """
    existing = get_profile(client, account_id)
    if existing:
        return existing, False

    result = (
        client.table("Profiles")
        .insert({
            "account_uuid": account_id,
            "updated_at": _now(),
            **DEFAULT_PREFERENCES,
        })
        .execute()
    )
    return (result.data[0] if result.data else None), True


def update_preferences(client, account_id, prefs):
    """
    Update any subset of theme / language / email_notifications on the
    caller's Profiles row. Returns the updated row, or None if the
    account has no Profiles row yet.
    """
    changes = {
        field: prefs[field]
        for field in PREFERENCE_FIELDS
        if field in prefs and prefs[field] is not None
    }
    changes["updated_at"] = _now()

    result = (
        client.table("Profiles")
        .update(changes)
        .eq("account_uuid", account_id)
        .execute()
    )
    return result.data[0] if result.data else None


def update_email(client, account_id, new_email):
    """
    Update Account.email for this account. Returns the updated row, or
    None if no Account row matched.

    NOTE: this changes only the Account table, not the Supabase Auth
    login email — the caller still signs in with their old email until
    the team decides how to keep the two in sync (changing the auth
    email sends a confirmation email to the user).
    """
    result = (
        client.table("Account")
        .update({"email": new_email})
        .eq("id", account_id)
        .execute()
    )
    return result.data[0] if result.data else None


def change_password(client, account_id, new_password):
    """
    Change the caller's password through Supabase Auth (self-service).

    Login verifies passwords via auth.sign_in_with_password (see
    shoppingcart/views.py), so the change goes through the same system:
    update_user() on the caller's already-signed-in session. Supabase
    hashes the new password server-side — it is never stored (or seen)
    in plaintext, and the shared Account table is untouched (it has no
    password column). An admin-style reset by bare account_id would
    instead need the service_role key.
    """
    result = client.auth.update_user({"password": new_password})
    return result.user.id if result.user else account_id
