# Updated job_scraper.py
import requests
import random
import time
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from config import UNWANTED_PATTERNS, get_headers, get_proxy

def is_excluded(url):
    """Check if URL should be excluded"""
    try:
        domain = urlparse(url).netloc.lower()
        return any(domain.endswith(d) for d in [
            'upwork.com', 'support.upwork.com',
            'www.upwork.com', 'help.upwork.com'
        ])
    except Exception:
        return True

def clean_scraped_content(text):
    """Clean and format scraped content"""
    cleaned = []
    for line in text.split('\n'):
        line = line.strip()
        if not line or any(re.search(p, line) for p in UNWANTED_PATTERNS):
            continue
        cleaned.append(re.sub(r'\s{2,}', ' ', line))
    return '\n'.join(cleaned) if cleaned else 'No description available'

def scrape_job_post(url):
    """Main scraping function with error handling"""
    try:
        # Initialize session with random delay
        time.sleep(random.uniform(1, 4))
        session = requests.Session()
        
        # Configure request parameters
        headers = get_headers()
        proxies = get_proxy()
        
        # Fixed cookie simulation (explicit integers)
        session.cookies.update({
            'session_id': str(random.randint(1000000, 10000000)),  # Explicit integers
            'ak_bmsc': ''.join(random.choices('abcdef0123456789', k=256))
        })

        # Make request with error handling
        try:
            response = session.get(url, headers=headers, proxies=proxies, timeout=25)
            response.raise_for_status()
        except requests.HTTPError as e:
            return {"error": f"HTTP Error {e.response.status_code}: {e.response.reason}"}
        except requests.Timeout:
            return {"error": "Request timed out after 25 seconds"}
        
        # Check for blocking pages
        if any(p in response.text for p in ['Incapsula incident', 'Access Denied', 'cloudflare']):
            return {"error": "Blocked by security system. Use VPN/proxy."}

        # Parse content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract job title
        title = "Job Title Not Found"
        for selector in ['h1[data-test="job-title"]', 'h2.job-title', 'h1']:
            if title_tag := soup.select_one(selector):
                title = title_tag.get_text(strip=True)
                break

        # Extract main content
        main_content = None
        for selector in [
            {'data-test': 'job-description'},
            {'class': 'job-description'},
            'main', 'article'
        ]:
            if content := soup.find('div', selector) or soup.find(selector):
                main_content = content
                break
        
        if not main_content:
            return {"error": "Job description section not found"}

        # Process content sections
        description = []
        links = []
        documents = []
        
        for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol', 'a']):
            try:
                if element.name in ['h2', 'h3']:
                    header = element.get_text(strip=True)
                    if header: description.append(f"\n## {header}")
                elif element.name in ['ul', 'ol']:
                    items = [f"- {li.get_text(strip=True)}" for li in element.find_all('li') if li.get_text(strip=True)]
                    if items: description.append('\n'.join(items))
                elif element.name == 'a':
                    if href := element.get('href', ''):
                        if href.startswith(('http://', 'https://')) and not is_excluded(href):
                            if re.search(r'\.(pdf|docx?|xlsx?)$', href, re.I):
                                documents.append(href)
                            else:
                                links.append(href)
                else:
                    if text := element.get_text(strip=True):
                        description.append(text)
            except Exception:
                continue

        # Process final output
        full_description = clean_scraped_content('\n'.join(description))
        links = list(set(links))
        documents = list(set(documents))

        return {
            "title": title,
            "description": full_description,
            "links": links,
            "documents": documents
        }

    except Exception as e:
        return {"error": f"Scraping failed: {str(e)}"}