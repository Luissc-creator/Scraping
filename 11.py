import pandas as pd
from scrapingbee import ScrapingBeeClient
from bs4 import BeautifulSoup
import re

# Function to read Excel file with product URLs
def read_product_urls(file_path):
    df = pd.read_excel(file_path)
    return df['Product URLs'].tolist()

# Function to scrape product information using ScrapingBeeClient
def scrape_product_info_with_scrapingbee(api_key, url):
    client = ScrapingBeeClient(api_key=api_key)
    response = client.get(url)

    if response.status_code == 200:
        return response.content.decode("utf-8")  # Return the HTML content
    else:
        print(f"Failed to fetch the data for {url}. Status Code: {response.status_code}")
        return None

# Function to extract product details from the HTML response
def extract_product_details(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    
    try:
        # Extract menu button
        menu_button = soup.select_one("button#menu-button-pdp-size-selector")
        if menu_button:
            print("Menu button found and clicked (simulated).")

        # Extract product name and SKU
        product_name = soup.select_one("h1[data-component=primary-product-title]").text.strip()
        title_text = soup.select_one("title").text
        sku_match = re.search(r"(\b\w{6,}-\w{3,}\b)", title_text)
        sku = sku_match.group(1) if sku_match else "N/A"

        # Initialize product information list
        product_info_list = []

        # Extract category buttons
        category_buttons = soup.select("button[data-testid=size-conversion-chip]")
        for category_button in category_buttons:
            category_name = category_button.text.strip()
            print(f"Processing category: {category_name}")

            # Simulate clicking the category button (using ScrapingBee, no dynamic interaction is needed)

            # Extract size buttons within the category
            size_buttons = soup.select("button[data-testid=size-selector-button]")
            for size_button in size_buttons:
                size_name = size_button.select_one("span > span").text.strip()

                # Extract price
                price = soup.select_one("h2[data-testid=trade-box-buy-amount]").text.strip()

                product_info = {
                    "name": product_name,
                    "sku": sku,
                    "size": size_name,
                    "price": price
                }
                product_info_list.append(product_info)

                # Log product info
                print(product_info)

        return product_info_list

    except Exception as e:
        print(f"Error extracting product details: {e}")
        return []

# Main function to run the scraper
def run_scraper(api_key, excel_file):
    product_urls = read_product_urls(excel_file)
    all_scraped_data = []

    for url in product_urls:
        print(f"Scraping {url}...")
        html_content = scrape_product_info_with_scrapingbee(api_key, url)
        if html_content:
            product_data = extract_product_details(html_content)
            all_scraped_data.extend(product_data)

    # Save scraped data to Excel
    df = pd.DataFrame(all_scraped_data)
    df.to_excel("scraped_product_info.xlsx", index=False)
    print("Scraping completed and saved to 'scraped_product_info.xlsx'.")

if __name__ == "__main__":
    API_KEY = "YKW5C2TZZNWTZOD4PR6NIOLMK1DO6LSYGKX86421QTLYJFEZ5L0H81AO4AXH34XD2NCADZMTLXYGJIEI"  # Replace with your ScrapingBee API key
    run_scraper(API_KEY, "product_urls.xlsx")
