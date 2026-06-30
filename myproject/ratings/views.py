"""
Book Rating and Commenting feature.

Implements the 4 endpoints required by the feature checklist:
  1. POST /api/ratings/                 -> create a rating
  2. POST /api/comments/                -> create a comment
  3. GET  /api/comments/<book_id>/      -> list comments for a book
  4. GET  /api/ratings/<book_id>/average/ -> average rating for a book

Each view follows the same pattern:
  1. Validate the incoming data with a serializer.
  2. Talk to Supabase using the shared client.
  3. Return a DRF Response with the right HTTP status code.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import RatingCreateSerializer, CommentCreateSerializer
from .supabase_client import supabase


@api_view(['POST'])
def create_rating(request):
    serializer = RatingCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data

    result = supabase.table("ratings").insert({
        "book_id": validated["book_id"],
        "user_id": validated["user_id"],
        "stars": validated["stars"],
    }).execute()

    if not result.data:
        return Response(
            {"error": "Failed to create rating."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(status=status.HTTP_201_CREATED)


@api_view(['POST'])
def create_comment(request):
    serializer = CommentCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    validated = serializer.validated_data

    result = supabase.table("comments").insert({
        "book_id": validated["book_id"],
        "user_id": validated["user_id"],
        "text": validated["text"],
    }).execute()

    if not result.data:
        return Response(
            {"error": "Failed to create comment."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return Response(status=status.HTTP_201_CREATED)


@api_view(['GET'])
def list_comments(request, book_id):
    result = (
        supabase.table("comments")
        .select("*")
        .eq("book_id", book_id)
        .order("created_at", desc=True)
        .execute()
    )

    return Response(result.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def average_rating(request, book_id):
    result = (
        supabase.table("ratings")
        .select("stars")
        .eq("book_id", book_id)
        .execute()
    )

    ratings = result.data

    if not ratings:
        return Response(
            {"book_id": book_id, "average_rating": None, "rating_count": 0},
            status=status.HTTP_200_OK
        )

    stars_list = [r["stars"] for r in ratings]
    average = round(sum(stars_list) / len(stars_list), 2)

    return Response(
        {"book_id": book_id, "average_rating": average, "rating_count": len(stars_list)},
        status=status.HTTP_200_OK
    )
