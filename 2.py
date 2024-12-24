# import the required library

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

options = webdriver.ChromeOptions()

# options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)

def scrape_stores(query):
  query = query.replace(" ", "+")
  url = f"https://www.google.com/search?q={query}"
  print(f"Loading URL: {url}")
  # visit your target site
  driver.get("https://www.google.com/maps/@28.5822018,-143.0517018,3z?entry=ttu&g_ep=EgoyMDI0MTIwMS4xIKXMDSoASAFQAw%3D%3D")
  
  try:
        # Wait for an element to load, this signals the page has finished rendering
        print("sdfsfsdfsdfsdffsd")
        WebDriverWait(driver, 30).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'S8ee5')]"))
        )
        
        print(f"Page loaded successfully.")
        # print(driver.page_source)

  except Exception as e:
        print(f"Error while loading page: {str(e)}")
#   print(driver.page_source);
#   more_info_buttons = driver.find_elements(By.XPATH, "//div[contains(text(), '更多地点')]")
#   if more_info_buttons:
#     # Click the first "More Information" button found
#     more_info_buttons[0].click()

#   # extract all the product containers
#   products = driver.find_elements(By.CSS_SELECTOR, ".product")

#   # extract the elements into a dictionary using the CSS selector
#   product_data = {
#       "Url": driver.find_element(
#           By.CSS_SELECTOR, ".woocommerce-LoopProduct-link"
#       ).get_attribute("href"),
#       "Name": driver.find_element(By.CSS_SELECTOR, ".product-name").text,
#       "Price": driver.find_element(By.CSS_SELECTOR, ".price").text,
#   }

#   # print the extracted data
#   print(product_data)


queries = ["antique stores in US", "collectibles shops in US", "baseball card shops in US"]

for query in queries:
  scrape_stores(query)
# # release the resources allocated by Selenium and shut down the browser
driver.quit()
