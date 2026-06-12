from dotenv import load_dotenv
load_dotenv()

import json
import os
from django.http import JsonResponse
from supabase import create_client, Client
from django.shortcuts import render

# Supabase URL, key, and client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SupabaseDB = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create your views here.
def get_cart_view(req):

    if(req.method == 'POST'):

        try:

            data = json.loads(req.body)
            username = data.get('username')

            accountID = SupabaseDB.table("Account").select("id").eq("username", username).execute()

            if(not accountID.data): print("empty")
            
            if(accountID.data):
                dbDataResponse = SupabaseDB.table('Shopping_Cart').select('cart').eq('customerID', value=accountID.data[0]["id"]).execute()
                shoppingCartItems = dbDataResponse.data
            
            else:
                print("hi")
                return JsonResponse({"error": f'No shopping cart found for user "{username}".'}, status=404)
            
            shoppingCartString = f"Shopping cart items for {username}:\n"

            for item in shoppingCartItems[0]["cart"]:
                shoppingCartString = shoppingCartString + f"- {item}\n"

            print(shoppingCartString)
            return JsonResponse({"Cart_data": shoppingCartString})

        except Exception as err:

            return JsonResponse({"error": str(err)}, status=500)
        
    return JsonResponse({"error": "Invalid request method"}, status=400)

def cart(req):
    return render(req, 'shoppingcart/shoppingcart.html')

