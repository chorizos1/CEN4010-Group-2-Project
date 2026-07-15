"""
These serializers don't talk to a Django model (we're using Supabase
directly, not Django's ORM). Their only job is to validate incoming
request data: check required fields are present and the right type
before we ever send anything to the database.
"""

from rest_framework import serializers


class RatingCreateSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    stars = serializers.IntegerField(min_value=1, max_value=5)

# NEW: separate serializer for updates (PUT)
# Only `stars` can be changed — book_id and user_id identify WHICH rating you're looking at (via the URL), not something you'd change after the fact.
class RatingUpdateSerializer(serializers.Serializer):
    stars = serializers.IntegerField(min_value=1, max_value=5)

class CommentCreateSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    text = serializers.CharField(max_length=2000, allow_blank=False)
