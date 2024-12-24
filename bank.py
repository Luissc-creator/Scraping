from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import markdownify
import traceback
import time
import pandas as pd

# Initialize WebDriver
driver = webdriver.Chrome()  # Ensure chromedriver is installed and on PATH

base_url = "https://www.belfius.be"

def get_categories():
    """
    Scrape all categories from the main support page.
    """
    try:
        driver.get(base_url + "/webapps/fr/selfcare/belfius/")
        
        # Wait for categories to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'linkType01'))
        )
        
        categories = []
        links = driver.find_elements(By.CLASS_NAME, 'linkType01')
        for link in links:
            href = link.get_attribute('href')
            category_name = link.text.strip()
            if href:
                categories.append({
                    "Category": category_name,
                    "URL": href
                })
        return categories
    except Exception as e:
        print("Error while fetching categories:")
        print(traceback.format_exc())
        return []

def get_questions(category_url):
    """
    Scrape all questions from a given category page, handling both normal list and section case types.
    """
    try:
        driver.get(category_url)
        
        # Wait for the body element to load to ensure the page is fully loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'body > div.height-100.display-flex-column.ng-scope > div.selfcare.grid.flex-auto.ng-scope > div > h2'))
        )
        
        questions = []

        # Parse the page source with BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

# Case 1: Normal list type
        try:
            normal_questions = driver.find_elements(By.CSS_SELECTOR, 
                "body > div.height-100.display-flex-column.ng-scope > div.selfcare.grid.flex-auto.ng-scope > div > div > a")
            if normal_questions:
                print(f"Normal question list detected for {category_url}")
                for element in normal_questions:
                    try:
                        href = element.get_attribute('href')
                        question_text = element.text.strip()
                        questions.append({
                            "Question": question_text,
                            "URL": f"{base_url}{href}" if href.startswith("/") else href
                        })
                    except Exception as e:
                        print(f"Error processing normal question element: {element}")
                        print(traceback.format_exc())
        except Exception as e:
            print(f"Error detecting normal questions for {category_url}:")
            print(traceback.format_exc())

        # Case 2: Section list type
        if not questions:  # Only check for section type if no normal questions found
            try:
                section_questions = driver.find_elements(By.CSS_SELECTOR, 
                    "div.height-100.display-flex-column.ng-scope > div.selfcare.grid.flex-auto.ng-scope > div > section.subject.ng-scope > ul > li > a")
                if section_questions:
                    print(f"Section question list detected for {category_url}")
                    for element in section_questions:
                        try:
                            href = element.get_attribute('href')
                            question_text = element.text.strip()
                            questions.append({
                                "Question": question_text,
                                "URL": f"{base_url}{href}" if href.startswith("/") else href
                            })
                        except Exception as e:
                            print(f"Error processing section question element: {element}")
                            print(traceback.format_exc())
            except Exception as e:
                print(f"Error detecting section questions for {category_url}:")
                print(traceback.format_exc())

        # If no questions found, log and return empty
        if not questions:
            print(f"No questions found for {category_url}. Check the page structure.")
        
        return questions
    except Exception as e:
        print(f"Error while fetching questions for category URL: {category_url}")
        print(traceback.format_exc())
        return []


def scrape_question_content(question_url):
    """
    Scrape the content of a single question page as Markdown, placing videos, images, and links in the correct positions.
    """
    try:
        driver.get(question_url)
        
        # Wait for the specific element to load
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "body > div.height-100.display-flex-column.ng-scope > div.selfcare.grid.flex-auto.ng-scope > article"))
        )
        time.sleep(5)
        
        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Locate the main content area using the provided selector
        main_content = soup.select_one("body > div.height-100.display-flex-column.ng-scope > div.selfcare.grid.flex-auto.ng-scope > article")
        if not main_content:
            return {
                "QuestionTitle": "Unknown",
                "ContentMarkdown": "Content not found"
            }

        # Extract the main question heading
        question_heading = main_content.find('h2')
        question_title = question_heading.get_text(strip=True) if question_heading else "No title found"

        # Process videos
        video_divs = main_content.find_all('div', class_='videos')
        for video_div in video_divs:
            try:
                iframe = video_div.find('iframe')
                if iframe and iframe.has_attr('src'):
                    video_src = iframe['src']
                    video_div.insert_before(soup.new_string(f"[Video: {video_src}]\n"))
            except Exception as e:
                print(f"Error processing iframe in video div: {video_div}")
                print(traceback.format_exc())

        # Process images
        images = main_content.find_all('img')
        for img in images:
            try:
                src = img.get('src', '')
                alt = img.get('alt', 'Image')
                img.insert_before(soup.new_string(f"![{alt}]({src})\n"))
            except Exception as e:
                print(f"Error processing image: {img}")
                print(traceback.format_exc())

        # Process links
        links = main_content.find_all('a', href=True)
        for link in links:
            try:
                href = link['href']
                text = link.get_text(strip=True)
                link.insert_before(soup.new_string(f"[Link: {text}]({href})\n"))
            except Exception as e:
                print(f"Error processing link: {link}")
                print(traceback.format_exc())

        # Convert the updated HTML content to Markdown
        content_markdown = markdownify.markdownify(str(main_content), heading_style="ATX")

        return {
            "QuestionTitle": question_title,
            "ContentMarkdown": content_markdown
        }
    except Exception as e:
        print(f"Error while scraping content for question URL: {question_url}")
        print(traceback.format_exc())
        return {
            "QuestionTitle": "Unknown",
            "ContentMarkdown": "Error occurred while fetching content"
        }


def scrape_all_data():
    """
    Scrape all categories, questions, and their content.
    """
    all_data = []
    try:
        # Get all categories
        categories = get_categories()
        for category in categories:
            category_name = category["Category"]
            # if category_name != "Fraude":  # Optional filter for "Fraude" category
            #     continue
            category_url = category["URL"]
            print(f"Scraping category: {category_name} ({category_url})")

            # Get all questions in the category
            questions = get_questions(category_url)
            for question in questions:
                try:
                    question_text = question["Question"]
                    question_url = question["URL"]
                    print(f"  Scraping question: {question_text} ({question_url})")
                    
                    # Scrape question content
                    content = scrape_question_content(question_url)
                    
                    all_data.append({
                        "Category": category_name,
                        "Question": question_text,
                        "URL": question_url,
                        "Content": content["ContentMarkdown"]
                    })
                except Exception as e:
                    print(f"Error while scraping question: {question_text}")
                    print(traceback.format_exc())
    except Exception as e:
        print("Error occurred while scraping data:")
        print(traceback.format_exc())
    return all_data

def save_to_excel(data, filename="scraped_data.xlsx"):
    """
    Save the scraped data into an Excel file.
    """
    try:
        df = pd.DataFrame(data)
        df.to_excel(filename, index=False)
        print(f"Data successfully saved to {filename}")
    except Exception as e:
        print("Error while saving data to Excel:")
        print(traceback.format_exc())

# Run the scraper
if __name__ == "__main__":
    try:
        scraped_data = scrape_all_data()

        # Save results to Excel
        save_to_excel(scraped_data, filename="scraped_data.xlsx")
    finally:
        driver.quit()
