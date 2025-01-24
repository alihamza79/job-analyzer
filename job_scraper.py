# job_scraper.py

import requests
import re
from bs4 import BeautifulSoup
from config import UNWANTED_PATTERNS, HEADERS

def clean_scraped_content(description_sections):
    clean_lines = []
    for line in description_sections:
        if not line.strip() or 'Upwork' in line:
            continue
            
        if not any(re.search(pattern, line) for pattern in UNWANTED_PATTERNS):
            clean_line = re.sub(r'Close the tooltip.*?\.\s*', '', line)
            clean_line = re.sub(r'\s{2,}', ' ', clean_line).strip()
            if clean_line and len(clean_line) > 30:
                clean_lines.append(clean_line)
    return clean_lines

def scrape_job_post(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find('h1').get_text(strip=True) if soup.find('h1') else "Job Title Not Found"
        
        main_content = soup.find('div', {'role': 'main'}) or \
                     soup.find('main') or \
                     soup.find('div', class_=lambda x: x and 'description' in x.lower()) or \
                     soup.find('article')
        
        description_sections = []
        if main_content:
            for element in main_content.find_all(['h2', 'h3', 'p', 'ul', 'ol']):
                if element.name in ['h2', 'h3']:
                    description_sections.append(f"\n## {element.get_text(strip=True)}")
                elif element.name in ['ul', 'ol']:
                    items = [f"- {li.get_text(strip=True)}" for li in element.find_all('li')]
                    description_sections.append('\n'.join(items))
                else:
                    text = element.get_text(strip=True)
                    if text and len(text) > 30:
                        description_sections.append(text)

        cleaned_description = clean_scraped_content(description_sections)
        return f"JOB TITLE: {title}\n\nDESCRIPTION:\n" + '\n'.join(cleaned_description) + "\n\n"
    
    except Exception as e:
        return f"Job post scraping error: {str(e)}"