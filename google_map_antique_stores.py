import requests
import pandas as pd

API_KEY = 'AIzaSyDE9OEGOb97M0_dYw7EL4Gfdu2vSeCcLW8'  # Replace with your API Key
TEXT_SEARCH_URL = 'https://maps.googleapis.com/maps/api/place/textsearch/json'
DETAILS_URL = 'https://maps.googleapis.com/maps/api/place/details/json'

def fetch_places(query, location, radius=50000):
    """Fetch places based on a query."""
    places = []
    params = {
        'query': query,
        'location': location,
        'radius': radius,
        'key': API_KEY
    }
    response = requests.get(TEXT_SEARCH_URL, params=params)
    data = response.json()
    
    places.extend(data.get('results', []))
    
    # Handle pagination if there are more results
    while 'next_page_token' in data:
        next_page_token = data['next_page_token']
        params['pagetoken'] = next_page_token
        response = requests.get(TEXT_SEARCH_URL, params=params)
        data = response.json()
        places.extend(data.get('results', []))
    
    return places

def fetch_place_details(place_id):
    """Fetch detailed information about a place using its place_id."""
    params = {
        'place_id': place_id,
        'fields': 'name,formatted_address,formatted_phone_number,website,'
                  'address_component',
        'key': API_KEY
    }
    response = requests.get(DETAILS_URL, params=params)
    return response.json().get('result', {})

def extract_address_components(components):
    """Extract city and state from address components."""
    city, state = None, None
    for component in components:
        if 'locality' in component['types']:
            city = component['long_name']
        if 'administrative_area_level_1' in component['types']:
            state = component['short_name']
    return city, state

# Example: Search for antique stores in the US
if __name__ == '__main__':
    location = '39.8283,-98.5795'  # Central point for continental US
    radius = 50000  # 50km radius
    queries = ['antique stores', 'collectibles stores', 'baseball card stores']
    
    results = []
    for query in queries:
        print(f"Fetching results for: {query}")
        places = fetch_places(query, location, radius)
        for place in places:
            place_id = place['place_id']
            details = fetch_place_details(place_id)
            
            # Extract city and state
            city, state = extract_address_components(details.get('address_components', []))
            
            # Append details to results
            results.append({
                'Name': details.get('name', 'N/A'),
                'Phone': details.get('formatted_phone_number', 'N/A'),
                'Address': details.get('formatted_address', 'N/A'),
                'City': city or 'N/A',
                'State': state or 'N/A',
                'Website': details.get('website', 'N/A')
            })

    # Save results to Excel
    df = pd.DataFrame(results)
    df.to_excel("places_results.xlsx", index=False)
    print("Results have been saved to 'places_results.xlsx'")
