from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from supabase import create_client
import json
import os

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def homepage(req):
    # return HttpResponse("Hello World!")
    return render(req, 'home.html')

def aboutpage(req):
    # return HttpResponse("About page.")
    return render(req, 'about.html')

@csrf_exempt
def create_wishlist(req):
    if req.method == "POST":
        try:
            data = json.loads(req.body)

            user_uuid = data.get("userUUID")
            wishlist_name = data.get("wishlistName")

            if not user_uuid or not wishlist_name:
                return JsonResponse(
                    {"error": "userUUID and wishlistName are required"},
                    status=400
                )

            response = supabase.table("Wishlists").insert({
                "userUUID": user_uuid,
                "wishlistName": wishlist_name
            }).execute()

            return JsonResponse({
                "message": "Wishlist created successfully",
                "data": response.data
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

@csrf_exempt
def add_book_to_wishlist(req):
    if req.method == "POST":
        try:
            data = json.loads(req.body)

            wishlist_id = data.get("wishlistID")
            book_id = data.get("bookID")

            if not wishlist_id or not book_id:
                return JsonResponse(
                    {"error": "wishlistID and bookID are required"},
                    status=400
                )

            response = supabase.table("Wishlist_Books").insert({
                "wishlistID": wishlist_id,
                "bookID": book_id
            }).execute()

            return JsonResponse({
                "message": "Book added to wishlist successfully",
                "data": response.data
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON format"}, status=400)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

def get_wishlist_books(req, wishlist_id):
    if req.method != "GET":
        return JsonResponse({"error": "Only GET requests are allowed"}, status=405)

    try:
        wishlist_books = supabase.table("Wishlist_Books").select("*").eq("wishlistID", wishlist_id).execute()

        book_ids = [item["bookID"] for item in wishlist_books.data]

        if not book_ids:
            return JsonResponse({"message": "No books found in this wishlist", "data": []}, status=200)

        books = supabase.table("Books").select("*").in_("bookID", book_ids).execute()

        return JsonResponse({"wishlistID": wishlist_id, "books": books.data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def remove_book_from_wishlist(req, wishlist_id, book_id):
    if req.method != "DELETE":
        return JsonResponse({"error": "Only DELETE requests are allowed"}, status=405)

    try:
        response = supabase.table("Wishlist_Books") \
            .delete() \
            .eq("wishlistID", wishlist_id) \
            .eq("bookID", book_id) \
            .execute()

        return JsonResponse({"message": "Book removed from wishlist successfully", "data": response.data}, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def shoppingcart(req):
    return render(req, 'shoppingcart.html')

