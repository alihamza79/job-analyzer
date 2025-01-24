# File: job_scraper.py
# Enhanced Job Scraper for Upwork Job Analyzer Pro with Accurate Link Extraction

from dotenv import load_dotenv
import os
import random
import requests
import re
import time
from bs4 import BeautifulSoup
from config import UNWANTED_PATTERNS, get_headers
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Define User Agents for headers
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'
]

# List of domains to exclude (Upwork's own domains)
EXCLUDED_DOMAINS = [
    'upwork.com',
    'support.upwork.com',
    'www.upwork.com',
    'help.upwork.com'
]

def get_headers():
    """Return headers with a random User-Agent."""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept-Language': 'en-US,en;q=0.9'
    }

def is_excluded(url):
    """Check if the URL's domain is in the excluded list."""
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        for excluded in EXCLUDED_DOMAINS:
            if domain.endswith(excluded):
                return True
        return False
    except Exception:
        return False  # In case of parsing error, exclude the URL

def clean_scraped_content(description_sections):
    """
    Clean the scraped description sections by removing unwanted patterns
    and ensuring the text is relevant and of sufficient length.
    """
    clean_lines = []
    for line in description_sections:
        if not line.strip() or 'Upwork' in line:
            continue

        # Remove lines matching any unwanted patterns
        if not any(re.search(pattern, line, re.IGNORECASE) for pattern in UNWANTED_PATTERNS):
            # Remove tooltips and excessive whitespace
            clean_line = re.sub(r'Close the tooltip.*?\.\s*', '', line)
            clean_line = re.sub(r'\s{2,}', ' ', clean_line).strip()
            if clean_line and len(clean_line) > 30:
                clean_lines.append(clean_line)
    return clean_lines

def extract_links(text):
    """
    Extract all absolute URLs from the given text and return them as a list.
    Ensures that URLs are captured accurately without trailing punctuation.
    """
    # Regex pattern to match absolute URLs without trailing punctuation
    url_pattern = re.compile(
        r'https?://[^\s\'"<>]+(?<![\.,\-])', re.IGNORECASE
    )
    return url_pattern.findall(text)

def scrape_job_post(url):
    """
    Scrape the job post from the given Upwork URL, separating
    the job description from any embedded links or documents.

    Returns:
        dict: {
            "title": str,
            "description": str,
            "links": list of str,
            "documents": list of str (if any)
        }
    """
    try:
        # Add a small random delay to mimic human behavior
        time.sleep(random.uniform(0.5, 1.5))

        # Get fresh headers with a random User-Agent
        headers = get_headers()

        # Send GET request to the job URL
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()  # Raise HTTPError for bad responses

        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the job title
        title_tag = soup.find('h4')
        title = title_tag.get_text(strip=True) if title_tag else "Job Title Not Found"

        # Identify the main content area of the job post
        main_content = soup.find('div', {'role': 'main'}) or \
                       soup.find('main') or \
                       soup.find('div', class_=lambda x: x and 'description' in x.lower()) or \
                       soup.find('article')

        description_sections = []
        extracted_links = []
        extracted_documents = []

        if main_content:
            # Iterate through relevant HTML elements to extract text and links
            for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'a']):
                if element.name in ['h2', 'h3']:
                    header_text = element.get_text(strip=True)
                    if header_text:
                        description_sections.append(f"\n## {header_text}")
                elif element.name in ['ul', 'ol']:
                    # Extract list items
                    items = [f"- {li.get_text(strip=True)}" for li in element.find_all('li')]
                    description_sections.append('\n'.join(items))
                elif element.name == 'a':
                    # Extract href links
                    href = element.get('href')
                    if href and (href.startswith('http://') or href.startswith('https://')):
                        if not is_excluded(href):
                            # Categorize the link
                            if re.match(r'.*\.(pdf|doc|docx|xls|xlsx)$', href, re.IGNORECASE):
                                extracted_documents.append(href)
                            else:
                                extracted_links.append(href)
                else:
                    # Extract paragraph or other text
                    text = element.get_text(strip=True)
                    if text and len(text) > 30:
                        description_sections.append(text)

        # Combine all description sections into a single text
        combined_description = '\n'.join(description_sections)

        # Extract links from the combined description
        links_in_description = extract_links(combined_description)
        # Filter out excluded domains in the description links as well
        links_in_description = [link for link in links_in_description if not is_excluded(link)]
        extracted_links.extend(links_in_description)

        # Remove all URLs from the description to keep it clean
        clean_description = re.sub(r'http\S+', '', combined_description)

        # Split the clean description into lines for further cleaning
        description_lines = clean_description.split('\n')

        # Clean the description lines using the existing cleaning function
        cleaned_description = clean_scraped_content(description_lines)

        # Remove duplicate links and ensure exact URLs
        unique_links = list(set([link.rstrip('.,-)') for link in extracted_links]))
        unique_documents = list(set([doc.rstrip('.,-)') for doc in extracted_documents]))

        # **Print Extracted Links and Documents for Verification**
        print("===== Extracted Links =====")
        for link in unique_links:
            print(link)
        print("===== Extracted Documents =====")
        for doc in unique_documents:
            print(doc)
        print("============================\n")

        return {
            "title": title,
            "description": '\n'.join(cleaned_description),
            "links": unique_links,
            "documents": unique_documents
        }

    except requests.HTTPError as http_err:
        print(f"HTTP error occurred: {str(http_err)}")  # Print HTTP errors
        return {"error": f"HTTP error occurred: {str(http_err)}"}
    except Exception as e:
        print(f"Job post scraping error: {str(e)}")  # Print general errors
        return {"error": f"Job post scraping error: {str(e)}"}

# Optional: If you want to test the scraper independently, you can add the following code.
# Remove or comment out this section when integrating with the main application.

if __name__ == "__main__":
    test_url = input("Enter Upwork Job Posting URL for testing: ").strip()
    result = scrape_job_post(test_url)
    if "error" in result:
        print(result["error"])
    else:
        print("===== Scraping Result =====")
        print(f"Title: {result['title']}")
        print(f"Description:\n{result['description']}\n")
        print("Links:")
        for link in result['links']:
            print(f"- {link}")
        print("Documents:")
        for doc in result['documents']:
            print(f"- {doc}")
        print("==========================")
