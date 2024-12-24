from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import requests
import traceback

# Initialize Selenium WebDriver
driver = webdriver.Chrome()  # Ensure ChromeDriver is installed and in PATH

# Clearbit API Key
CLEARBIT_API_KEY = "your_clearbit_api_key"

def scrape_google_maps(search_query, location, max_results=50000):
    """
    Scrape veterinary businesses across the US using Google Maps.
    """
    base_url = f"https://www.google.com/maps/search/{search_query.replace(' ', '+')}+in+{location.replace(' ', '+')}"
    driver.get(base_url)
    business_data = []
    scraped_count = 0

    while scraped_count < max_results:
        try:
            # Wait for business listings to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'Nv2PK'))
            )

            # Find all business listing elements
            businesses = driver.find_elements(By.CLASS_NAME, 'Nv2PK')
            for business in businesses:
                try:
                    # Scroll the business element into view
                    driver.execute_script("arguments[0].scrollIntoView(true);", business)
                    time.sleep(1)

                    # Click on the business to load detailed information
                    business.click()
                    time.sleep(3)  # Wait for the side panel to load

                    # Extract details from the side panel
                    name = driver.find_element(By.CLASS_NAME, 'DUwDvf').text
                    address = (
                        driver.find_element(By.XPATH, "//button[contains(@data-item-id, 'address')]").text
                        if driver.find_elements(By.XPATH, "//button[contains(@data-item-id, 'address')]")
                        else "N/A"
                    )
                    phone = driver.find_element(By.XPATH, "//button[contains(@data-tooltip, 'Copy phone number')]").text
                       
                    website = (
                        driver.find_element(By.CLASS_NAME, "bm892c").get_attribute('href')
                        if driver.find_elements(By.CLASS_NAME, "bm892c").get_attribute('href')
                        else "N/A"
                    )

                    # Add the extracted information to the data list
                    business_data.append({
                        "Business Name": name,
                        "Address": address,
                        "Phone Number": phone,
                        "Website": website
                    })

                    scraped_count += 1
                    if scraped_count >= max_results:
                        break
                except Exception as e:
                    print("Error extracting business details:", e)

            # Scroll down to load more results
            driver.execute_script("window.scrollBy(0, 1000);")
            time.sleep(2)

            # Check if "Next" button exists to load additional pages
            next_button = driver.find_elements(By.ID, 'ppdPk-Ej1Yeb-LgbsSe-tJiF1e')
            if next_button:
                next_button[0].click()
                time.sleep(5)
            else:
                break

        except Exception as e:
            print("Error during scrolling/pagination:", e)
            break

    return business_data


def enrich_with_clearbit(business_data):
    """
    Enrich business data with owner details using Clearbit API.
    """
    enriched_data = []
    for business in business_data:
        domain = business.get("Website")
        if domain and domain != "N/A":
            try:
                response = requests.get(
                    f"https://company.clearbit.com/v2/companies/find?domain={domain}",
                    headers={"Authorization": f"Bearer {CLEARBIT_API_KEY}"}
                )
                if response.status_code == 200:
                    data = response.json()
                    enriched_data.append({
                        **business,
                        "Owner Name": data.get('person', {}).get('name', {}).get('fullName', "N/A"),
                        "Owner Title": data.get('person', {}).get('title', "N/A"),
                        "Revenue": data.get('metrics', {}).get('annualRevenue', "N/A"),
                        "Employees": data.get('metrics', {}).get('employees', "N/A"),
                        "LinkedIn Profile": data.get('person', {}).get('linkedin', "N/A")
                    })
                else:
                    enriched_data.append({
                        **business,
                        "Owner Name": "Not Found",
                        "Owner Title": "Not Found",
                        "Revenue": "Not Found",
                        "Employees": "Not Found",
                        "LinkedIn Profile": "Not Found"
                    })
            except Exception as e:
                print(f"Error enriching data for {domain}: {e}")
                enriched_data.append(business)
        else:
            enriched_data.append(business)
    return enriched_data


def save_to_excel(data, filename="veterinary_businesses_us.xlsx"):
    """
    Save the scraped and enriched data into an Excel file.
    """
    try:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print("Error saving to Excel:", e)


def main():
    # Search query and location
    search_query = "veterinary clinics"
    location = "United States"

    # Step 1: Scrape Google Maps
    print("Scraping Google Maps...")
    business_data = scrape_google_maps(search_query, location)

    # Step 2: Enrich data with Clearbit API
    print("Enriching data with Clearbit...")
    enriched_data = enrich_with_clearbit(business_data)

    # Step 3: Save results to Excel
    print("Saving data to Excel...")
    save_to_excel(enriched_data, filename="veterinary_businesses_us.xlsx")


if __name__ == "__main__":
    try:
        main()
    finally:
        driver.quit()
