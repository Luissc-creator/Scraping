import requests
from bs4 import BeautifulSoup

def scrape_navbar_categories(url):
    try:
        # Send a GET request to the website
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad HTTP status codes

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the main navigation bar
        nav_menu = soup.select_one('ul.nav_menu.flex')
        if not nav_menu:
            print("Navigation menu not found.")
            return []

        # Recursive function to extract categories and subcategories
        def extract_categories(menu):
            categories = []
            for item in menu.find_all('li', recursive=False):
                link_tag = item.select_one('a')
                category_name = link_tag.get_text(strip=True)
                category_link = link_tag['href']
                sub_menu = item.select_one('ul')
                sub_categories = extract_categories(sub_menu) if sub_menu else []
                categories.append({"name": category_name, "link": category_link, "subcategories": sub_categories})
                
                # If it's an end branch, print the link and extract main content
                if not sub_menu:
                    print(f"End branch link: {category_link}")
                    extract_main_content(category_link, category_name)
            return categories

        def extract_main_content(link, category_name):
            try:
                response = requests.get(link)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                main_content = soup.select_one('div.main.content.wrapper')
                if main_content:
                    content_text = main_content.get_text(strip=True)
                    print(f"Main content from {link}:\n{content_text}")
                    save_content(category_name, content_text)
                else:
                    print(f"No main content found for {link}")
            except requests.exceptions.RequestException as e:
                print(f"An error occurred while fetching the URL {link}: {e}")

        def save_content(category_name, content):
            filename = "./result/" + category_name.replace(" ", "_").replace("/", "_") + ".txt"
            with open(filename, 'w', encoding='utf-8') as file:
                file.write(content)
            print(f"Content saved to {filename}")

        # Extract categories from the navigation menu
        categories = extract_categories(nav_menu)
        return categories

    except requests.exceptions.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
        return []

# URL of the website
url = "https://www.clarisclinic.com/"

# Scrape the categories
categories = scrape_navbar_categories(url)

# Print the categories
import json
print(json.dumps(categories, indent=2))