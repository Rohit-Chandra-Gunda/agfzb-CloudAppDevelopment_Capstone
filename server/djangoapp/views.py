from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel, CarMake, CarDealer, DealerReview
from .restapis import *
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)

def about(request):
    context = {}
    if request.method == "GET":
        return render(request, 'djangoapp/about.html', context)


def contact(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/contact.html', context)

def login_request(request):
    context = {}
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/djangoapp/')
        else:
           return render(request, 'djangoapp/user_login.html', context)
    else:
        return render(request, 'djangoapp/user_login.html', context)

def logout_request(request):
    logout(request)
    return redirect('/djangoapp/')

def registration_request(request):
    context = {}
    if request.method == 'GET':
        return render(request, 'djangoapp/registration.html', context)
    elif request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.debug("{} is new user".format(username))
        if not user_exist:
            user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name,
                                            password=password)
            login(request, user)
            return redirect("/djangoapp/")
        else:
            return render(request, 'djangoapp/registration.html', context)

def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://au-syd.functions.appdomain.cloud/api/v1/web/e3e4bac1-45ac-4161-a0dd-42f3422594a9/dealership-package/get-dealership"
        dealerships = get_dealers_from_cf(url)
        context["dealerships"] = dealerships
        print(dealerships)
        return render(request, 'djangoapp/index.html', context)

def get_dealer_details(request, id):
    if request.method == "GET":
        context = {}
        dealer_url = "https://au-syd.functions.appdomain.cloud/api/v1/web/e3e4bac1-45ac-4161-a0dd-42f3422594a9/dealership-package/get-dealership"
        dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
        context["dealer"] = dealer
        
        review_url = "https://au-syd.functions.appdomain.cloud/api/v1/web/e3e4bac1-45ac-4161-a0dd-42f3422594a9/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(review_url, id=id)
        context["reviews"] = reviews

        return render(request, 'djangoapp/dealer_details.html', context)

def add_review(request, id):
    context = {}
    dealer_url = "https://au-syd.functions.appdomain.cloud/api/v1/web/e3e4bac1-45ac-4161-a0dd-42f3422594a9/dealership-package/get-dealership"
    dealer = get_dealer_by_id_from_cf(dealer_url, id=id)
    context["dealer"] = dealer
    
    if request.method == 'GET':
        cars = CarModel.objects.filter(dealerid = id)
        context["cars"] = cars
        print(cars)
        return render(request, 'djangoapp/add_review.html', context)
    elif request.method == 'POST':
        if request.user.is_authenticated:
            username = request.user.username
            print(request.POST)
            payload = dict()
            car_name = request.POST["car"]
            print("Car name!")
            print(car_name)
            car = CarModel.objects.get(name = car_name)
            payload["time"] = datetime.utcnow().isoformat()
            payload["name"] = username
            payload["dealership"] = id
            payload["id"] = id
            payload["review"] = request.POST["content"]
            payload["purchase"] = False
            if "purchasecheck" in request.POST:
                if request.POST["purchasecheck"] == 'on':
                    payload["purchase"] = True
            payload["purchase_date"] = request.POST["purchasedate"]
            payload["car_make"] = car.carmake.name
            payload["car_model"] = car.cartype
            payload["car_year"] = car.year.year

            new_payload = {}
            new_payload["review"] = payload
            review_post_url =  "https://au-syd.functions.appdomain.cloud/api/v1/web/e3e4bac1-45ac-4161-a0dd-42f3422594a9/dealership-package/post-review"
            post_request(review_post_url, new_payload, id=id)

        return redirect("djangoapp:dealer_details", id=id)