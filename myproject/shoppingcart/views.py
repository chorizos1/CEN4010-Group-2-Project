from dotenv import load_dotenv
load_dotenv()

import json
import os
from django.http import JsonResponse
from supabase import create_client, Client
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Supabase URL, key, and client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
SupabaseDB = create_client(SUPABASE_URL, SUPABASE_KEY)

@csrf_exempt
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

            SupabaseDB.postgrest.auth(session.session.access_token)

            accountID = SupabaseDB.table("Account").select("id").eq("email", email).execute()
            
            if(accountID.data):
                dbDataResponse = SupabaseDB.table('Shopping_Cart').select('cart').eq('customerUUID', value=accountID.data[0]["id"]).execute()
                shoppingCartItems = dbDataResponse.data
            
            else:
                return JsonResponse({"error": f'No shopping cart found for user "{email}".'}, status=404)

            if(not shoppingCartItems): 

                return JsonResponse({

                    "error": f'No shopping cart found for user "{email}".',
                    "cartRowEmpty": True,

                }, status = 404)

            shoppingCartString = f"Shopping cart items for {email}:\n\n"
            shoppingCartData = []
            totalCartPrice = 0

            # Gets all book IDs in the from the cart column in the Shopping_Cart table.
            for item in shoppingCartItems[0]["cart"]:

                dbDataResponse = SupabaseDB.table('Books').select('*').eq('bookID', value=item).execute()
                bookInformation = dbDataResponse.data

                shoppingCartData.append(

                    {
                        "bookID": bookInformation[0]["bookID"],
                        "bookName": bookInformation[0]["bookName"],
                        "Author": bookInformation[0]["bookAuthor"],
                        "Description": bookInformation[0]["bookDescription"],
                        "Published": bookInformation[0]["publishedDate"],
                        "ISBN13": bookInformation[0]["ISBN13"],
                        "Price": bookInformation[0]["price"],
                    }

                )

                totalCartPrice = totalCartPrice + bookInformation[0]["price"]

            return JsonResponse({

                "Cart_msg": shoppingCartString,
                "Cart_data": shoppingCartData,
                "Total_cart_price": totalCartPrice,

            })

        except Exception as err:

            return JsonResponse({"error": str(err)}, status=500)
        
    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def remove_from_cart(req):

    if(req.method == 'PUT'):

        try:

            data = json.loads(req.body)
            email = data.get('email')
            password = data.get('password')
            bookID = int(data.get('bookID'))

            session = SupabaseDB.auth.sign_in_with_password({
            
                "email": email,
                "password": password,
            
            })

            SupabaseDB.postgrest.auth(session.session.access_token)
            
            accountID = SupabaseDB.table("Account").select("id").eq("email", email).execute()
            shoppingCart = []

            if(accountID.data):
                dbDataResponse = SupabaseDB.table('Shopping_Cart').select('cart').eq('customerUUID', value=accountID.data[0]["id"]).execute()
                shoppingCart = dbDataResponse.data[0]["cart"]
                        
            else:
                return JsonResponse({"error": f'No shopping cart found for user "{email}".'}, status=404)

            shoppingCart.remove(bookID)
            SupabaseDB.table("Shopping_Cart").update({"cart": shoppingCart}).eq("customerUUID", accountID.data[0]["id"]).execute()

            return JsonResponse({"success": True})

        except Exception as err:

            return JsonResponse({"error": str(err)}, status = 500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def removeCart(req):

    if(req.method == 'DELETE'):

        try:

            data = json.loads(req.body)
            email = data.get('email')
            password = data.get('password')

            session = SupabaseDB.auth.sign_in_with_password({
                                
                "email": email,
                "password": password,
                                
            })
                    
            SupabaseDB.postgrest.auth(session.session.access_token)
                                
            accountID = SupabaseDB.table("Account").select("id").eq("email", email).execute()
            
            if(accountID.data):
            
                SupabaseDB.table("Shopping_Cart").delete().eq("customerUUID", accountID.data[0]["id"]).execute()
            
            else:
            
                return JsonResponse({"error": f'No shopping cart found for user "{email}".'}, status=404)
            
            return JsonResponse({"success": True})

        except Exception as err:

            return JsonResponse({"error": str(err)}, status = 500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def createCart(req):

    if(req.method == "POST"):

        try:

            data = json.loads(req.body)
            email = data.get('email')
            password = data.get('password')
            
            session = SupabaseDB.auth.sign_in_with_password({
                                            
                "email": email,
                "password": password,
                                            
            })
                                
            SupabaseDB.postgrest.auth(session.session.access_token)
                                            
            accountID = SupabaseDB.table("Account").select("id").eq("email", email).execute()

            createdCart = SupabaseDB.table("Shopping_Cart").insert({

                "customerUUID": accountID.data[0]["id"],
                "cart": [1, 4, 8],

            }).select().execute()

            if(createdCart.data):

                return JsonResponse({"success": True}, status = 200)

            else:

                return JsonResponse({"error": f'Cart was unable to be created. Try again later.'}, status = 500)

        except Exception as err:

            return JsonResponse({"error": str(err)}, status = 500)

def getAllBooksAvailable(req):

    if(req.method == 'GET'):

        try:
            
            allBooks = SupabaseDB.table("Books").select("*").execute()
            reformattedBooksVar = []

            for bookInfo in allBooks.data:

                reformattedBooksVar.append({

                    "bookID": bookInfo["bookID"],
                    "bookName": bookInfo["bookName"],
                    "bookAuthor": bookInfo["bookAuthor"],

                })

            return JsonResponse({

                "success": True,
                "booksData": reformattedBooksVar,

            }, status = 200)

        except Exception as err:

            return JsonResponse({"error": str(err)}, status = 500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

def addBookToCart(req):

    if(req.method == 'POST'):

        try:

            data = json.loads(req.body)
            email = data.get('email')
            password = data.get('password')
            bookID = data.get('bookID')
                        
            session = SupabaseDB.auth.sign_in_with_password({
                                                        
                "email": email,
                "password": password,
                                                        
            })
                                            
            SupabaseDB.postgrest.auth(session.session.access_token)
                                                        
            accountID = SupabaseDB.table("Account").select("id").eq("email", email).execute()
            shoppingCart = []

            if(accountID.data):
                dbDataResponse = SupabaseDB.table('Shopping_Cart').select('cart').eq('customerUUID', value=accountID.data[0]["id"]).execute()
                shoppingCart = dbDataResponse.data[0]["cart"]
                                    
            else:
                return JsonResponse({"error": f'No shopping cart found for user "{email}".'}, status=404)
            
            shoppingCart.append(bookID)
            SupabaseDB.table("Shopping_Cart").update({"cart": shoppingCart}).eq("customerUUID", accountID.data[0]["id"]).execute()
            
            return JsonResponse({"success": True})

        except Exception as err:

            return JsonResponse({"error": str(err)}, status = 500)

    return JsonResponse({"error": "Invalid request method"}, status=400)

@csrf_exempt
def cart(req):
    return render(req, 'shoppingcart/shoppingcart.html')

