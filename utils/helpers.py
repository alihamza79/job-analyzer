# Add this to utils/helpers.py
import requests
from bs4 import BeautifulSoup

def scrape_job_post(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        # Custom selector for Upwork job posts
        return soup.find('div', {'class': 'job-description'}).text
    except Exception as e:
        return f"Error scraping job post: {str(e)}"