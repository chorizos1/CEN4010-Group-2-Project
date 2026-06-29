from dotenv import load_dotenv
load_dotenv()

import os
from django.http import JsonResponse
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