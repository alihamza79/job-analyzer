import os
import random
from dotenv import load_dotenv

load_dotenv()

# Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# User Agents List
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0'
]

PROXY_SERVERS = [
    # Add proxies in format: 'http://user:pass@host:port'
]

def get_headers():
    """Return rotating headers with browser-like characteristics"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://www.upwork.com/',
        'DNT': str(random.randint(0, 1)),
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Pragma': 'no-cache',
        'Cache-Control': 'no-cache'
    }

def get_proxy():
    """Return random proxy configuration"""
    if PROXY_SERVERS:
        proxy = random.choice(PROXY_SERVERS)
        return {'http': proxy, 'https': proxy}
    return None

UNWANTED_PATTERNS = [
    r'\$[\d,.]+',
    r'Proposals:.*',
    r'Interviewing:\d+',
    r'Invites sent:\d+',
    r'Last viewed by client:.*',
    r'How it works',
    r'About Upwork',
    r'Find the best freelance jobs',
    r'Explore Upwork opportunities',
    r'total spent',
    r'\d+ hires',
    r'Posted On:',
    r'^-\s[A-Z][a-z]+[A-Z]',
    r'Remote Job',
    r'Ongoing projectProject Type',
    r'Activity on this job'
]