import requests
import json
import logging
from requests.auth import HTTPBasicAuth
from . import models
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions

logger = logging.getLogger(__name__)

def get_request(url, **kwargs):
    print(kwargs)
    print("GET from {} ".format(url))
    try:
        response = requests.get(url, headers={'Content-Type': 'application/json'}, params=kwargs)
    except:
        # If any error occurs
        print("Network exception occurred")
    status_code = response.status_code
    print("With status {} ".format(status_code))
    json_data = json.loads(response.text)
    return json_data

def post_request(url, json_payload, **kwargs):
    json_obj = json_payload["review"]
    print(kwargs)
    try:
        response = requests.post(url, json=json_obj, params=kwargs)
    except:
        print("Something went wrong")
    print (response)
    return response

def get_dealers_from_cf(url, **kwargs):
    results = []
    json_result = get_request(url)
    if json_result:
        dealers = json_result['entries']
        for dealer in dealers:
            dealer_obj = models.CarDealer(address=dealer["address"], city=dealer["city"], full_name=dealer["full_name"],
                                   id=dealer["id"], lat=dealer["lat"], long=dealer["long"],
                                   short_name=dealer["short_name"],
                                   st=dealer["st"], zip=dealer["zip"])
            results.append(dealer_obj)
            print('-------------------------------------------------------')
    return results

def get_dealer_reviews_by_id_from_cf(url, dealerId):
    results = []
    json_result = get_request(url, dealerId=dealerId)
    if json_result:
        reviews = json_result['entries']
        for review in reviews:
            try:
                review_obj = models.DealerReview(name = review["name"], 
                dealership = review["dealership"], review = review["review"], purchase=review["purchase"],
                purchase_date = review["purchase_date"], car_make = review['car_make'],
                car_model = review['car_model'], car_year= review['car_year'], sentiment= "none")
            except:
                review_obj = models.DealerReview(name = review["name"], 
                dealership = review["dealership"], review = review["review"], purchase=review["purchase"],
                purchase_date = 'none', car_make = 'none',
                car_model = 'none', car_year= 'none', sentiment= "none")
                
            review_obj.sentiment = analyze_review_sentiments(review_obj.review)
            print(review_obj.sentiment)
                    
            results.append(review_obj)

    return results

def analyze_review_sentiments(text):
    api_key = "PyqVnBwo6WMipgLCPtTzqAhGD-nOMSC1_JCfgIokfdw6"
    url = "https://api.au-syd.natural-language-understanding.watson.cloud.ibm.com/instances/937f4277-bc46-444f-8bde-9818b58a8ab7"
    texttoanalyze= text
    version = '2020-08-01'
    authenticator = IAMAuthenticator(api_key)
    natural_language_understanding = NaturalLanguageUnderstandingV1(
    version='2020-08-01',
    authenticator=authenticator
    )
    natural_language_understanding.set_service_url(url)
    response = natural_language_understanding.analyze(
        text=text,
        features= Features(sentiment= SentimentOptions())
    ).get_result()
    print(json.dumps(response))
    sentiment_score = str(response["sentiment"]["document"]["score"])
    sentiment_label = response["sentiment"]["document"]["label"]
    print(sentiment_score)
    print(sentiment_label)
    sentimentresult = sentiment_label
    
    return sentimentresult