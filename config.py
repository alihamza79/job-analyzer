from dotenv import load_dotenv
import os

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

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

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    'Accept-Language': 'en-US,en;q=0.9'
}