import json
from collections import defaultdict

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from postgrest.exceptions import APIError

from .supabase_client import supabase

TOP_SELLERS_LIMIT = 10


def books_by_genre(request):
    genre = request.GET.get("genre")
    if not genre:
        return JsonResponse(
            {"error": "Missing required query parameter: genre"}, status=400
        )
    response = (
        supabase.table("Books")
        .select("*")
        .ilike("genre", genre)
        .order("copiesSold", desc=True)
        .execute()
    )
    return JsonResponse(response.data or [], safe=False)


def top_sellers(request):
    response = (
        supabase.table("Books")
        .select("*")
        .order("copiesSold", desc=True)
        .limit(TOP_SELLERS_LIMIT)
        .execute()
    )
    return JsonResponse(response.data or [], safe=False)


def books_by_min_rating(request):
    rating = request.GET.get("rating")
    if not rating:
        return JsonResponse(
            {"error": "Missing required query parameter: rating"}, status=400
        )
    try:
        min_rating = float(rating)
    except ValueError:
        return JsonResponse(
            {"error": f"Invalid rating: {rating!r} is not a number"}, status=400
        )

    try:
        ratings_rows = (
            supabase.table("ratings").select("book_id, stars").execute().data or []
        )
    except APIError as e:
        if e.code == "PGRST205":
            return JsonResponse([], safe=False)
        raise

    buckets = defaultdict(list)
    for r in ratings_rows:
        buckets[r["book_id"]].append(r["stars"])

    averages = {
        bid: round(sum(stars) / len(stars), 2) for bid, stars in buckets.items()
    }
    qualifying_ids = [bid for bid, avg in averages.items() if avg >= min_rating]

    if not qualifying_ids:
        return JsonResponse([], safe=False)

    books = (
        supabase.table("Books")
        .select("*")
        .in_("bookID", qualifying_ids)
        .execute()
        .data
        or []
    )
    for book in books:
        book["averageRating"] = averages.get(book["bookID"])
    books.sort(key=lambda b: b["averageRating"], reverse=True)

    return JsonResponse(books, safe=False)


@csrf_exempt
@require_http_methods(["PATCH"])
def apply_discount(request):
    try:
        payload = json.loads(request.body or b"{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Request body must be valid JSON"}, status=400)

    publisher = payload.get("publisher")
    discount = payload.get("discount")
    if not publisher:
        return JsonResponse({"error": "Missing required field: publisher"}, status=400)
    if discount is None:
        return JsonResponse({"error": "Missing required field: discount"}, status=400)
    try:
        discount = float(discount)
    except (TypeError, ValueError):
        return JsonResponse({"error": "'discount' must be a number"}, status=400)
    if not 0 <= discount <= 100:
        return JsonResponse(
            {"error": "'discount' must be between 0 and 100"}, status=400
        )

    books = (
        supabase.table("Books")
        .select("bookID, price")
        .eq("publisher", publisher)
        .execute()
        .data
        or []
    )

    multiplier = 1 - discount / 100
    for book in books:
        new_price = round(float(book["price"]) * multiplier, 2)
        supabase.table("Books").update({"price": new_price}).eq(
            "bookID", book["bookID"]
        ).execute()

    return JsonResponse({}, status=200)
