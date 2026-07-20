"""
These serializers don't talk to a Django model (we're using Supabase
directly, not Django's ORM) — same pattern as the ratings app. Their
only job is to validate incoming request data before we touch the
database.

Every profile endpoint carries the caller's login email + password,
because the database only grants access to authenticated users (the
anon key alone is denied) — the same reason shoppingcart's get-cart
endpoint takes credentials.
"""

from rest_framework import serializers


class CredentialsSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=128, allow_blank=False)


class UpdateEmailSerializer(CredentialsSerializer):
    new_email = serializers.EmailField()


class UpdatePreferencesSerializer(CredentialsSerializer):
    theme = serializers.CharField(max_length=32, required=False)
    language = serializers.CharField(max_length=16, required=False)
    email_notifications = serializers.BooleanField(required=False)

    def validate(self, data):
        if not any(
            field in data
            for field in ("theme", "language", "email_notifications")
        ):
            raise serializers.ValidationError(
                "Provide at least one of: theme, language, email_notifications."
            )
        return data


class ChangePasswordSerializer(CredentialsSerializer):
    new_password = serializers.CharField(max_length=128, min_length=8)
