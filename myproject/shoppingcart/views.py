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
            email = data.get('email')
            password = data.get('password')

            
            session = SupabaseDB.auth.sign_in_with_password({

                "email": email,
                "password": password,

            })

            accountID = SupabaseDB.table("Account").select("id").eq("email", email).execute()
            
            if(accountID.data):
                dbDataResponse = SupabaseDB.table('Shopping_Cart').select('cart').eq('customerUUID', value=accountID.data[0]["id"]).execute()
                shoppingCartItems = dbDataResponse.data
            
            else:
                return JsonResponse({"error": f'No shopping cart found for user "{email}".'}, status=404)
            
            shoppingCartString = f"Shopping cart items for {email}:\n\n"
            shoppingCartDictionary = {}

            # Gets all book IDs in the from the cart column in the Shopping_Cart table.
            for item in shoppingCartItems[0]["cart"]:

                dbDataResponse = SupabaseDB.table('Books').select('*').eq('bookID', value=item).execute()
                bookInformation = dbDataResponse.data

                # Stores relevant book data into a dictionary with its respective ID as the key.
                shoppingCartDictionary[item] = {

                    "bookName": bookInformation[0]["bookName"],
                    "bookAuthor": bookInformation[0]["bookAuthor"],
                    "bookDescription": bookInformation[0]["bookDescription"],
                    "bookPrice": bookInformation[0]["price"],
                    "bookISBN13": bookInformation[0]["ISBN13"],
                    "bookPublishDate": bookInformation[0]["publishedDate"],

                }

                # Constructs the string output used when displaying the shopping cart.
                shoppingCartString = shoppingCartString + f"- {shoppingCartDictionary[item]["bookName"]}\n"
                shoppingCartString = shoppingCartString + f"Author: {shoppingCartDictionary[item]["bookAuthor"]}\n"
                shoppingCartString = shoppingCartString + f"Description: {shoppingCartDictionary[item]["bookDescription"]}\n"
                shoppingCartString = shoppingCartString + f"Published: {shoppingCartDictionary[item]["bookPublishDate"]}\n"
                shoppingCartString = shoppingCartString + f"ISBN13: {shoppingCartDictionary[item]["bookISBN13"]}\n"
                shoppingCartString = shoppingCartString + f"Price: ${shoppingCartDictionary[item]["bookPrice"]}\n\n"

            return JsonResponse({"Cart_data": shoppingCartString})

        except Exception as err:

            return JsonResponse({"error": str(err)}, status=500)
        
    return JsonResponse({"error": "Invalid request method"}, status=400)

def cart(req):
    return render(req, 'shoppingcart/shoppingcart.html')

