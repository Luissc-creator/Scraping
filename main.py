import pandas as pd
import random
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from fake_useragent import UserAgent
import undetected_chromedriver as uc
import re

# Function to read Excel file with product URLs
def read_product_urls(file_path):
    df = pd.read_excel(file_path)
    return df['Product URLs'].tolist()

# Function to initialize undetected ChromeDriver
def initialize_driver():
    ua = UserAgent()
    try:
        user_agent = ua.random  # Random user-agent
        print(f"Using User-Agent: {user_agent}")
    except:
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.6778.140 Safari/537.36"
        print("Fallback User-Agent:", user_agent)

    options = uc.ChromeOptions()
    options.add_argument(f"user-agent={user_agent}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-proxy-server")
    options.add_argument("--proxy-server='direct://'")
    options.add_argument("--proxy-bypass-list=*")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--no-sandbox")
    # options.add_argument("--headless=new")  # Optional for headless mode

    # Initialize the driver
    driver = uc.Chrome(options=options)
    return driver

# Function to handle "Press & Hold" CAPTCHA
def press_and_hold(driver):
    try:
        captcha_container = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.px-captcha-container"))
        )
        print("Detected CAPTCHA container.")
        press_hold_element = captcha_container.find_element(By.CSS_SELECTOR, "div#px-captcha")
        print("Interacting with 'Press & Hold' element...")
        actions = ActionChains(driver)
        actions.click_and_hold(press_hold_element).perform()
        time.sleep(10)  # Hold for 5 seconds
        actions.release().perform()
        print("'Press & Hold' interaction complete.")
    except Exception as e:
        print("No 'Press & Hold' element detected or issue interacting:", e)

def scrape_product_info(url, driver):
    driver.get(url)
    time.sleep(3)  # Wait for the page to load
    press_and_hold(driver)
    time.sleep(10)
    product_info_list = []

    try:
        # Click the menu button to reveal category menu
        menu_button = driver.find_element(By.CSS_SELECTOR, "button#menu-button-pdp-size-selector")
        menu_button.click()
        time.sleep(2)
        press_and_hold(driver)
        # Get category buttons
        category_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid=size-conversion-chip]")

        for category_index, category_button in enumerate(category_buttons):
            # Re-locate the category button after each iteration due to DOM changes
            category_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid=size-conversion-chip]")
            category_button = category_buttons[category_index]
            category_button.click()
            time.sleep(2)  # Wait for sizes to load

            # Get size buttons
            size_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid=size-selector-button]")

            for size_index, size_button in enumerate(size_buttons):
                # Re-locate the size button after each iteration due to DOM changes
                size_buttons = driver.find_elements(By.CSS_SELECTOR, "button[data-testid=size-selector-button]")
                size_button = size_buttons[size_index]

                # Extract size name
                size_name = size_button.find_element(By.CSS_SELECTOR, "span > span").text

                # Click the size button
                size_button.click()
                time.sleep(2)  # Wait for the details to load

                # Extract product name
                product_name = driver.find_element(By.CSS_SELECTOR, "h1[data-component=primary-product-title]").text

                # Extract price
                price = driver.find_element(By.CSS_SELECTOR, "h2[data-testid=trade-box-buy-amount]").text

                # Extract SKU
                raw_sku = driver.execute_script("return document.querySelector('title').textContent")
                sku_match = re.search(r"(\b\w{6,}-\w{3,}\b)", raw_sku)
                sku = sku_match.group(1) if sku_match else "N/A"

                # Append information to the list
                product_info = {
                    "name": product_name,
                    "sku": sku,
                    "size": size_name,
                    "price": price
                }
                product_info_list.append(product_info)

                # Log product info to the console
                print(product_info)
                # Return to size selection
                menu_button = driver.find_element(By.CSS_SELECTOR, "button#menu-button-pdp-size-selector")
                menu_button.click()
                time.sleep(2)

            # Return to category selection
            menu_button = driver.find_element(By.CSS_SELECTOR, "button#menu-button-pdp-size-selector")
            menu_button.click()
            time.sleep(2)

    except Exception as e:
        print(f"Error scraping {url}: {e}")

    return product_info_list


# Main function to run the scraper
def run_scraper(excel_file):
    product_urls = read_product_urls(excel_file)
    driver = initialize_driver()
    all_scraped_data = []

    try:
        for url in product_urls:
            print(f"Scraping {url}...")
            product_data = scrape_product_info(url, driver)
            all_scraped_data.extend(product_data)
            print(f"Completed scraping {url}.")
    finally:
        driver.quit()

    # Save scraped data to Excel
    df = pd.DataFrame(all_scraped_data)
    df.to_excel("scraped_product_info.xlsx", index=False)
    print("Scraping completed and saved to 'scraped_product_info.xlsx'.")

# Run the scraper
if __name__ == "__main__":
    run_scraper("product_urls.xlsx")
