from dotenv import load_dotenv
load_dotenv()

import os
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from supabase import create_client

# supabase url, key, client

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SupabaseDB = create_client(SUPABASE_URL, SUPABASE_KEY)


def get_book_details(req, book_id):
    try:
        response = SupabaseDB.table("Books").select("*").eq("bookID", book_id).execute()

        if not response.data:
            return JsonResponse({"error": "Book not found"}, status=404)

        return JsonResponse(response.data[0])

    except Exception as err:
        return JsonResponse({"error": str(err)}, status=500)

@csrf_exempt
def create_book(req):
    if req.method != "POST":
        return JsonResponse({"error": "Please use a POST request."}, status=405)

    try:
        book_data = json.loads(req.body)
        required_fields = [
                "ISBN13",
                "bookName",
                "bookDescription",
                "price",
                "bookAuthor",
                "genre",
                "publisher",
                "publishedDate",
                "copiesSold",
        ]

        missing_fields = [
            field for field in required_fields
            if field not in book_data
        ]

        if missing_fields:
            return JsonResponse({"error": "Missing required fields","missingFields": missing_fields,},status=400)

        response = (SupabaseDB.table("Books").insert(book_data).execute())

        return JsonResponse({"message": "Book created!", "book": response.data[0] if response.data else book_data,}, status=201,)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    except Exception as err:
        return JsonResponse({"error": str(err)}, status=500)

@csrf_exempt
def create_author(req):
    if req.method != "POST":
        return JsonResponse({"error": "Please use a POST request."}, status=405)

    try:
        author_data = json.loads(req.body)
        required_fields = [
                "firstName",
                "lastName",
                "biography",
                "publisher",
        ]

        missing_fields = [
            field for field in required_fields
            if field not in author_data
        ]

        if missing_fields:
            return JsonResponse({"error": "Missing required fields","missingFields": missing_fields,},status=400)

        response = (SupabaseDB.table("Authors").insert(author_data).execute())

        return JsonResponse({"message": "Author created!", "author": response.data[0] if response.data else author_data,}, status=201,)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON data"}, status=400)

    except Exception as err:
        return JsonResponse({"error": str(err)}, status=500)