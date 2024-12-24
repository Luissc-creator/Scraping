
import requests
from bs4 import BeautifulSoup
import markdownify
import pandas as pd
from playwright.sync_api import sync_playwright

def scrape_page(url):
    # Render dynamic content using Playwright
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        content = page.content()  # Get full HTML after rendering
        browser.close()

    soup = BeautifulSoup(content, 'html.parser')
    
    # Extract category (e.g., from breadcrumb or meta tag)
    category = soup.find('meta', {'name': 'category'})['content'] if soup.find('meta', {'name': 'category'}) else 'Unknown'

    # Extract question (e.g., main heading)
    question = soup.find('h1').get_text(strip=True) if soup.find('h1') else 'No Question Found'

    # Extract content and convert to markdown
    content_section = soup.find('main') or soup.find('body')  # Adjust selector as needed
    content_markdown = markdownify.markdownify(str(content_section), heading_style="ATX")
    
    # Include links, images, and videos
    for img in soup.find_all('img'):
        content_markdown += f"\n![{img.get('alt', 'Image')}]({img.get('src')})"
    for link in soup.find_all('a'):
        content_markdown += f"\n[Link: {link.get_text(strip=True)}]({link.get('href')})"
    for video in soup.find_all('video'):
        content_markdown += f"\n[Video: {video.get('src')}]"

    return {
        "URL": url,
        "Category": category,
        "Question": question,
        "Content": content_markdown
    }

def scrape_site(start_url):
    # List to store data
    data = []

    # TODO: Write logic to crawl the entire site (e.g., sitemap or URL extraction)
    # Example: Extract links from a main page
    response = requests.get(start_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True) if 'support' in a['href']]  # Adjust filter logic

    for link in links:
        try:
            page_data = scrape_page(link)
            data.append(page_data)
        except Exception as e:
            print(f"Error scraping {link}: {e}")

    return data

# Scrape and save to Google Sheet
start_url = "https://www.examplebank.com/support"
scraped_data = scrape_site(start_url)

# Convert to DataFrame and save
df = pd.DataFrame(scraped_data)
df.to_csv("support_data.csv", index=False)  # For local CSV
# TODO: Use Google Sheets API to upload df directly to a Google Sheet
