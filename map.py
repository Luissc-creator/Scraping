import requests
import pandas as pd

# Your Google API key
API_KEY = 'YOUR_GOOGLE_API_KEY'  # Replace with your actual API key

# Function to fetch stores data from Google Places API
def get_stores_data(query, location="California", radius=50000):
    # Base URL for the Google Places API Text Search request
    url = f"https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    # Create the search query
    search_query = f"{query} in {location}"
    
    # Parameters for the API request
    params = {
        'query': search_query,
        'key': API_KEY,
        'radius': radius,  # Set the search radius in meters
    }
    
    # Send GET request to the API
    response = requests.get(url, params=params)
    
    # Parse the response
    if response.status_code == 200:
        results = response.json().get('results', [])
        store_data = []
        
        for store in results:
            name = store.get('name')
            address = store.get('formatted_address', 'N/A')
            phone = store.get('formatted_phone_number', 'N/A')
            website = store.get('website', 'N/A')
            
            store_data.append({
                'Name': name,
                'Address': address,
                'Phone': phone,
                'Website': website
            })
        
        return store_data
    else:
        print(f"Error: {response.status_code}")
        return []

# Example query for antique stores in California
query = "antique stores"
location = "California"
radius = 50000  # Search radius (50km)

# Get the store data
store_data = get_stores_data(query, location, radius)

# Save to Excel if data is available
if store_data:
    df = pd.DataFrame(store_data)
    df.to_excel("antique_stores_google_maps.xlsx", index=False)
    print("Data saved to antique_stores_google_maps.xlsx")
else:
    print("No data found.")
