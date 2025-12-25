import os
import json
import time
import requests
import pandas as pd
from dotenv import load_dotenv

#load .env file which has api key and host information
load_dotenv(".env")
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST")

#scraping 3 most populous cities in the US for data
CITIES = ["New York, NY", "Los Angeles, CA", "Chicago, IL"]

#function when rate limited/request fails
def requestWithRetry(url, headers, params, maxRetries=3):
    for attempt in range(maxRetries):
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                return response
            elif response.status_code == 429:  #rate limited
                print(f"rate limited :( waiting {2**attempt} sec...")
                time.sleep(2 ** attempt) #exponential backoff (2^attempt secs)
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}. Retrying...")
            time.sleep(2 ** attempt)
    return None

#validate the data and filer out outliers
def validateListing(listing):
    if not listing.get("price") or not listing.get("bedrooms"):
        return False
    try:
        price = float(listing["price"])
        if isinstance(price, str):
            price = float(price.replace("$", "").replace(",", "").strip()) #clean price string just in case
        else:
            price = float(price)
        if price < 500 or price > 20000: #keep reasonable listings only
            return False
    except Exception:
        return False
    return True

#main scraping function
def scrapeDataForCity(city, maxPages=5): #only need 5 pages worth of daya
    url = f"https://{RAPIDAPI_HOST}/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": RAPIDAPI_HOST
    }
    allListings = []
    os.makedirs("data/raw", exist_ok=True) #ensure directory exists

    for page in range(1, maxPages + 1):
        params = {
            "location": city,
            "status": "forRent",
            "page": str(page),
            "output": "json"
        }
        resp = requestWithRetry(url, headers, params) #fetch listing
        if not resp:
            print(f"Failed to fetch page {page} for {city}")
            break
        data = resp.json()
        results = data.get("results", [])
        if not results:
            break
        
        #extract relevant fields into a dictionary
        for item in results:
            listing = {
                "address": item.get("streetAddress"), #string, full
                "city": item.get("city"), #string,full
                "state": item.get("state"), #abbreviation
                "zip_code": item.get("zipcode"), 
                "price": item.get("price"), #no $, just numbers
                "bedrooms": item.get("bedrooms"), #decimal number for some reason
                "bathrooms": item.get("bathrooms"), #same here
                "square_feet": item.get("livingArea"), #living area -> total sq feet
                "listing_date": item.get("daysOnZillow"),  #days active, not exact date
                "latitude": item.get("latitude"),
                "longitude": item.get("longitude"),
                "url": f"https://www.zillow.com/homedetails/{item.get('zpid')}_zpid/"
            }
            if validateListing(listing): #validate before adding
                allListings.append(listing)

        print(f"{city}: Page {page} -> {len(results)} listings fetched")

        time.sleep(1)  #limit b/w requests is 1 s

    return allListings

if __name__ == "__main__":
    totalListings = []
    os.makedirs("data/raw", exist_ok=True) #make directory if it doesnt already exist

    for city in CITIES: #loop thru cities
        print(f"Scraping {city}...")
        cityData = scrapeDataForCity(city)
        totalListings.extend(cityData)
        pd.DataFrame(cityData).to_csv( #save individual city data
            f"data/raw/{city.replace(',','').replace(' ','_').lower()}_raw.csv",
            index=False
        )
        print(f"Saved {len(cityData)} listings for {city}.")

    #save combined dataset
    df = pd.DataFrame(totalListings)
    df.to_csv("data/raw/all_rentals_raw.csv", index=False)
    print(f"Done! Total collected: {len(df)} listings :)")