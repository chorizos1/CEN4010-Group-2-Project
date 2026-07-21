"""
Profile Management feature.

Endpoints (all under /api/profile/):

  1. POST  /api/profile/              -> get the caller's profile
  2. POST  /api/profile/create/      -> create the default profile row (signup)
  3. PATCH /api/profile/preferences/ -> update theme/language/email_notifications
  4. PATCH /api/profile/email/       -> update Account.email
  5. POST  /api/profile/password/    -> change the caller's password (Supabase Auth)

Each view follows the same pattern as the ratings app:
  1. Validate the incoming data with a serializer.
  2. Talk to Supabase — but signed in as the caller, because the
     database denies the anon role on Account and Profiles.
  3. Return a DRF Response with the right HTTP status code.

Reads use POST (not GET) because the caller's credentials travel in the
request body, like shoppingcart's get-cart endpoint.
"""

from postgrest.exceptions import APIError
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from supabase_auth.errors import AuthApiError

from . import services
from .serializers import (
    ChangePasswordSerializer,
    CredentialsSerializer,
    UpdateEmailSerializer,
    UpdatePreferencesSerializer,
)
from .supabase_client import signed_in_client


def _authenticate(serializer_class, request):
    """
    Validate the request body and sign the caller in.

    Returns (validated_data, client, account_id, error_response);
    error_response is None on success, otherwise a ready-to-return
    Response and the other values are None.
    """
    serializer = serializer_class(data=request.data)
    if not serializer.is_valid():
        return None, None, None, Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

    validated = serializer.validated_data
    try:
        client, account_id = signed_in_client(
            validated["email"], validated["password"]
        )
    except AuthApiError as err:
        return None, None, None, Response(
            {"error": f"Authentication failed: {err.message}"},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return validated, client, account_id, None


def _database_error(err):
    return Response(
        {"error": f"Database error: {err.message}", "code": err.code},
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@api_view(['POST'])
def get_profile_view(request):
    _, client, account_id, error = _authenticate(CredentialsSerializer, request)
    if error:
        return error

    try:
        profile = services.get_profile(client, account_id)
    except APIError as err:
        return _database_error(err)

    if profile is None:
        return Response(
            {"error": "No profile exists for this account yet. "
                      "POST /api/profile/create/ to create one."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(profile, status=status.HTTP_200_OK)


@api_view(['POST'])
def create_profile_view(request):
    _, client, account_id, error = _authenticate(CredentialsSerializer, request)
    if error:
        return error

    try:
        profile, created = services.create_profile(client, account_id)
    except APIError as err:
        return _database_error(err)

    if created:
        return Response(profile, status=status.HTTP_201_CREATED)
    return Response(
        {"message": "Profile already exists.", "profile": profile},
        status=status.HTTP_200_OK,
    )


@api_view(['PATCH'])
def update_preferences_view(request):
    validated, client, account_id, error = _authenticate(
        UpdatePreferencesSerializer, request
    )
    if error:
        return error

    try:
        profile = services.update_preferences(client, account_id, validated)
    except APIError as err:
        return _database_error(err)

    if profile is None:
        return Response(
            {"error": "No profile exists for this account yet. "
                      "POST /api/profile/create/ to create one."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(profile, status=status.HTTP_200_OK)


@api_view(['PATCH'])
def update_email_view(request):
    validated, client, account_id, error = _authenticate(
        UpdateEmailSerializer, request
    )
    if error:
        return error

    try:
        account = services.update_email(client, account_id, validated["new_email"])
    except APIError as err:
        return _database_error(err)

    if account is None:
        return Response(
            {"error": "No Account row matched this user."},
            status=status.HTTP_404_NOT_FOUND,
        )
    return Response(account, status=status.HTTP_200_OK)


@api_view(['POST'])
def change_password_view(request):
    validated, client, account_id, error = _authenticate(
        ChangePasswordSerializer, request
    )
    if error:
        return error

    try:
        services.change_password(client, account_id, validated["new_password"])
    except AuthApiError as err:
        # e.g. the new password matches the old one, or is below
        # Supabase's configured minimum strength.
        return Response(
            {"error": f"Password change rejected: {err.message}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"message": "Password updated. Use the new password on your "
                    "next sign-in."},
        status=status.HTTP_200_OK,
    )
