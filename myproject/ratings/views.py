"""
Book Rating and Commenting feature.

Originally (Sprint 3) implemented the 4 actions required by the Feature Checklist.
Sprint 4 adds 3 things to make the API more complete against the "REST API Expectations" instructions,
which expects all 4 CRUD verbs

(GET/POST/PUT/DELETE) to be represented, not just GET/POST:

  1. PUT / DELETE for a single rating (update or remove your own rating)
  2. DELETE for a single comment (remove your own comment)
  3. POST responses now return the created row (including its new "id")
     instead of an empty body, so the client can immediately PUT/DELETE it

Endpoints after this update:
  POST   /api/ratings/                    -> create a rating
  PUT    /api/ratings/<rating_id>/        -> update a rating           [NEW]
  DELETE /api/ratings/<rating_id>/        -> delete a rating           [NEW]
  GET    /api/ratings/<book_id>/average/  -> average rating for a book

  POST   /api/comments/                   -> create a comment
  GET    /api/comments/?book_id=<id>      -> list comments for a book [CHANGED — see note below]
  DELETE /api/comments/<comment_id>/      -> delete a comment          [NEW]

IMPORTANT CHANGE — why list_comments moved from a URL path segment to a
query parameter:
  The old URL was GET /api/comments/<book_id>/  (book_id in the path).
  Adding DELETE /api/comments/<comment_id>/ for a single comment would
  reuse that exact same URL shape (comments/<some integer>/), but with
  the integer meaning something different (a comment's own id, not a
  book's id). Django can't tell those apart from the URL alone, so one
  of the two had to move. Filtering by query parameter
  (?book_id=1) is the more standard REST approach anyway — the slide's
  "Uniform Interface" principle is exactly about not overloading the
  same URL shape with two different meanings.

Each view follows the same pattern: validate (if there's incoming data)
-> talk to Supabase -> return a Response with the right status code.
"""

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .serializers import RatingCreateSerializer, RatingUpdateSerializer, CommentCreateSerializer
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

    # CHANGED: return the created row (id, book_id, user_id, stars, created_at) instead of an empty body
    # The client needs the new rating's id if it ever wants to PUT or DELETE it later
    return Response(result.data[0], status=status.HTTP_201_CREATED)

# NEW view. One URL, two HTTP verbs — PUT to update, DELETE to remove
# This is the standard REST pattern: the same address represents "this one specific rating," and the HTTP method says what to do to it.
@api_view(['PUT', 'DELETE'])
def rating_detail(request, rating_id):
    if request.method == 'PUT':
        serializer = RatingUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        result = (
            supabase.table("ratings")
            .update({"stars": serializer.validated_data["stars"]})
            .eq("id", rating_id)
            .execute()
        )

        # Supabase returns an empty list (not an error) if no row matched
        # that id — that's how we detect "not found" here.
        if not result.data:
            return Response(
                {"error": f"No rating found with id {rating_id}."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(result.data[0], status=status.HTTP_200_OK)

    # request.method == 'DELETE'
    result = supabase.table("ratings").delete().eq("id", rating_id).execute()

    if not result.data:
        return Response(
            {"error": f"No rating found with id {rating_id}."},
            status=status.HTTP_404_NOT_FOUND
        )

    # 204 No Content is the standard status for a successful delete —
    # there's nothing left to return, so no response body.
    return Response(status=status.HTTP_204_NO_CONTENT)

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

# CHANGED: this handles BOTH creating a comment (POST) AND listing comments for a book (GET, via ?book_id=)
# Combining them into one view at one URL (/api/comments/) is the standard REST "collection" pattern — same address, different HTTP verb, different action
@api_view(['GET', 'POST'])
def comments_collection(request):
    if request.method == 'POST':
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

        # CHANGED: return the created row instead of an empty body.
        return Response(result.data[0], status=status.HTTP_201_CREATED)

    # request.method == 'GET'
    # CHANGED: book_id now comes from a query parameter (?book_id=1)
    # instead of the URL path — see the module docstring for why.
    book_id = request.query_params.get('book_id')

    if book_id is None:
        return Response(
            {"error": "book_id query parameter is required, e.g. /api/comments/?book_id=1"},
            status=status.HTTP_400_BAD_REQUEST
        )

    result = (
        supabase.table("comments")
        .select("*")
        .eq("book_id", book_id)
        .order("created_at", desc=True)
        .execute()
    )

    return Response(result.data, status=status.HTTP_200_OK)


# NEW view. Deletes one specific comment by its own id.
@api_view(['DELETE'])
def delete_comment(request, comment_id):
    result = supabase.table("comments").delete().eq("id", comment_id).execute()

    if not result.data:
        return Response(
            {"error": f"No comment found with id {comment_id}."},
            status=status.HTTP_404_NOT_FOUND
        )

    return Response(status=status.HTTP_204_NO_CONTENT)