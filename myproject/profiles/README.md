# Profile Management

Django app for the Profile Management feature. Additive only: no
teammate tables or files are modified beyond one registration line in
`settings.py` (INSTALLED_APPS) and one include in `myproject/urls.py`,
the same way `ratings` and `shoppingcart` are registered.

## Tables used

- `Profiles` (owned by this feature): `id`, `account_uuid -> Account.id`,
  `theme`, `language`, `email_notifications`, `updated_at`
- `Account` (shared, read/update email only): `id` (uuid, same as the
  Supabase Auth user id), `email`

## Why every request carries email + password

The database denies the `anon` role on `Account` and `Profiles`; only
authenticated users have access. So every endpoint signs the caller in
through Supabase Auth first (the same approach as shoppingcart's
`get-cart/` endpoint) and then acts as that user. The account id is
taken from the authenticated session — a caller can never touch another
account's rows by guessing ids.

## Endpoints

All JSON, all under `/api/profile/`. `email` + `password` are the
caller's normal login credentials.

| Method | URL | Body | Success |
|---|---|---|---|
| POST | `/api/profile/` | `{email, password}` | 200 profile row (404 if none yet) |
| POST | `/api/profile/create/` | `{email, password}` | 201 new default row (200 if it already existed) |
| PATCH | `/api/profile/preferences/` | `{email, password}` + any of `theme`, `language`, `email_notifications` | 200 updated row |
| PATCH | `/api/profile/email/` | `{email, password, new_email}` | 200 updated Account row |
| POST | `/api/profile/password/` | `{email, password, new_password}` | 200 password changed (in Supabase Auth) |

Errors: 400 validation, 401 bad credentials, 404 no row, 500 database
error (with the PostgREST code).

## For the signup feature

Call `services.create_profile(client, account_id)` right after signup
(or POST `/api/profile/create/`) to give the new user their default
profile row. It's idempotent — safe to call twice.

## Password changes — how they work

Login verifies passwords through Supabase Auth
(`auth.sign_in_with_password`), and `Account` has no password column, so
`/password/` is **self-service**: it calls
`client.auth.update_user({"password": ...})` on the caller's signed-in
session. Supabase hashes the new password server-side — nothing is ever
stored in plaintext, and the shared `Account` table is untouched. An
admin-style reset by bare account id (no current password) would need
the project's service_role key; not implemented.

## Open team coordination points

1. **Email sync**: `/email/` updates `Account.email` only. The Supabase
   Auth login email stays unchanged (changing it triggers a
   confirmation email), so after an email update the user still signs
   in with the old address until the team decides how to sync them.
2. `myproject/shoppingcart/.env` is committed to git even though `.env`
   is in `.gitignore` — the credentials are in the repo history.
