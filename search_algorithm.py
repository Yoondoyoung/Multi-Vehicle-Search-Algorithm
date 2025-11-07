import json
import os
import httpx
from itertools import combinations

# Get the directory where the file is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_PATH = os.path.join(BASE_DIR, 'json', 'listings.json')


def get_listings():
    # Get listings from API if LISTINGS_API_URL is set, otherwise from JSON file.
    api_url = os.getenv('LISTINGS_API_URL')
    
    if api_url:
        # Get listings from API
        try:
            response = httpx.get(api_url, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise Exception(f"Failed to fetch listings from API: {str(e)}")
    else:
        # Load from JSON file
        try:
            with open(JSON_PATH, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise Exception(f"Listings file not found at {JSON_PATH} and LISTINGS_API_URL not set") 

    # {
    #     "id": "abc123", => Spot ID
    #     "length": 10,
    #     "width": 20, => 2 slot
    #     "location_id": "def456", => Building
    #     "price_in_cents": 100,
    # }

def group_listing(listings):
    group_listing = {}
    # Group the listings by location_id
    for listing in listings:
        if listing['location_id'] not in group_listing:
            group_listing[listing['location_id']] = []
        group_listing[listing['location_id']].append({
            'id' : listing['id'],
            'length' : listing['length'],
            'width' : listing['width'],
            'price_in_cents' : listing['price_in_cents']
        })
    
    return group_listing


def expand_cars(cars):
    expand_cars = []
    # Expand the cars into the list
    for car in cars:
        for _ in range(car['quantity']):
            expand_cars.append({
                'length' : car['length'],
                'width' : 10
            })
    
    # Sort the cars by length in descending order
    expand_cars.sort(key=lambda x:x['length'], reverse=True)
    return expand_cars


def fit_in_location(expanded_cars, selected_listings):
    listing_slots = {}
    # Initialize the listing slots for each listing
    for listing in selected_listings:
        slot_num = listing['width'] // 10 # number of slots in the listing
        listing_slots[listing['id']] = {
            'slots' : [
                [] for _ in range(slot_num) # initialize the slots
            ],
            'max_length' : listing['length']
        }
    # Try to fit the cars into the listing slots
    for car in expanded_cars:
        placed = False

        for listing in selected_listings:
            if car['length'] > listing['length']:
                continue

            # Get the listing id and slot information
            listing_id = listing['id']
            slot_info = listing_slots[listing_id]

            for slot_index in range(len(slot_info['slots'])):
                slot = slot_info['slots'][slot_index]
                used_length = sum(slot)
                remaining_length = slot_info['max_length'] - used_length

                # If the remaining length is fit the car, place the car in the slot
                if remaining_length >= car['length']:
                    slot.append(car['length'])
                    placed = True
                    break

            if placed:
                break
            
        if not placed:
            return False
    return True


def find_cheapest_combination(expanded_cars, location_list):
    n = len(location_list) # number of locations
    min_price = float('inf')
    best_combination = None

    for i in range(1, min(n+1, 6)): # number of locations to consider
        for combination in combinations(location_list, i):
            if fit_in_location(expanded_cars, list(combination)):
                total_price = sum(listing['price_in_cents'] for listing in combination)
                if total_price < min_price:
                    min_price = total_price
                    best_combination = list(combination)
    return best_combination, min_price


def search_algorithm(request, listings_data=None):
    # If listings_data is not provided, get listings from API.
    if listings_data is None:
        listings_data = get_listings()
    
    expanded_cars = expand_cars(request)
    grouped_listing = group_listing(listings_data)

    result = []

    for location_id, location_list in grouped_listing.items():
        location_list.sort(key=lambda x:x['price_in_cents'])

        best_combination, min_price = find_cheapest_combination(expanded_cars, location_list)

        if best_combination:
            result.append({
                "location_id": location_id,
                "listing_ids": [listing['id'] for listing in best_combination],
                "total_price_in_cents": min_price
            })
    
    result.sort(key=lambda x: x['total_price_in_cents'])

    return result

