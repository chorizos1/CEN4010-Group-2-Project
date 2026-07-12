from django.http import HttpResponse
from django.shortcuts import render
import supabase

def homepage(req):
    # return HttpResponse("Hello World!")
    return render(req, 'home.html')

def aboutpage(req):
    # return HttpResponse("About page.")
    return render(req, 'about.html')

def shoppingcart(req):
    return render(req, 'shoppingcart.html')
