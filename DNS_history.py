from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import markdownify
import traceback

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
    Scrape all questions from a given category page.
    """
    try:
        driver.get(category_url)
        
        # Wait for question elements to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'question'))
        )
        
        questions = []
        question_elements = driver.find_elements(By.CLASS_NAME, 'question')
        for element in question_elements:
            anchor = element.find_element(By.TAG_NAME, 'a')
            href = anchor.get_attribute('href')
            question_text = anchor.text.strip()
            questions.append({
                "Question": question_text,
                "URL": href
            })
        return questions
    except Exception as e:
        print(f"Error while fetching questions for category URL: {category_url}")
        print(traceback.format_exc())
        return []

def scrape_question_content(question_url):
    """
    Scrape the content of a single question page, format it as Markdown.
    """
    try:
        driver.get(question_url)
        
        # Wait for the main content area to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'article'))
        )
        
        # Get page source and parse with BeautifulSoup
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Locate the main content area
        main_content = soup.find('article', class_='detail selfcare-detail')
        if not main_content:
            return {
                "QuestionTitle": "Unknown",
                "ContentMarkdown": "Content not found"
            }

        # Extract the main question heading
        question_heading = main_content.find('h2')
        question_title = question_heading.get_text(strip=True) if question_heading else "No title found"

        # Extract all subcomponents within the article
        all_content_html = ""
        for component in main_content.find_all('div', recursive=False):
            all_content_html += str(component)

        # Convert the HTML content to Markdown
        content_markdown = markdownify.markdownify(all_content_html, heading_style="ATX")

        # Append additional elements like links and images
        for img in main_content.find_all('img'):
            src = img.get('src', '')
            alt = img.get('alt', 'Image')
            content_markdown += f"\n![{alt}]({src})"

        for link in main_content.find_all('a', href=True):
            href = link['href']
            text = link.get_text(strip=True)
            content_markdown += f"\n[Link: {text}]({href})"

        for video in main_content.find_all('video', src=True):
            src = video['src']
            content_markdown += f"\n[Video: {src}]"

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
            category_url = category["URL"]
            print(f"Scraping category: {category_name} ({category_url})")

            # Get all questions in the category
            questions = get_questions(category_url)
            for question in questions:
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
        print("Error occurred while scraping data:")
        print(traceback.format_exc())
    return all_data

# Run the scraper
if __name__ == "__main__":
    try:
        scraped_data = scrape_all_data()

        # Print results to the console
        for entry in scraped_data:
            print(f"Category: {entry['Category']}")
            print(f"Question: {entry['Question']}")
            print(f"URL: {entry['URL']}")
            print(f"Content:\n{entry['Content']}")
            print("-" * 80)

    finally:
        driver.quit()
