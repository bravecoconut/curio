# app/stages/stage_1/search_for_trending_piece/search_topic.py

"""Discover candidate post topics by scraping daily facts from an external source."""

from ddgs import DDGS
from ddgs.exceptions import DDGSException

from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[0]

import sqlite3

from ddgs import DDGS
from ddgs.exceptions import DDGSException

import requests

import json

from datetime import datetime

from bs4 import BeautifulSoup


def search_for_topics():
    """Scrape topics from the source site and write a dated JSON snapshot."""

    error = {'error': None}


    target_url = "https://www.thefactsite.com/daily-facts/"
    
    # Use browser-like headers to reduce the chance of HTTP blocking.
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    all_extracted_topics = []
    
    try:
        response = requests.get(target_url, headers=headers, timeout=15)
        
        if response.status_code != 200:
            print(f"Connection dropped. Server returned an error code: {response.status_code}")
            return []
            
        # Parse the HTML response into a navigable document tree.
        import re
        soup = BeautifulSoup(response.content, "html.parser")

        # Collect fact paragraphs tagged with generated CSS class names.
        for p in soup.find_all("p"):
            headline_text = p.get_text(strip=True)
            classes = p.get('class', [])
            
            # Fact blocks use classes matching the pattern gb-text-<8 hex chars>.
            has_random_class = any(re.match(r'^gb-text-[a-f0-9]{8}$', c) for c in classes)

            if has_random_class and len(headline_text) > 30:
                # Exclude site boilerplate, attribution, and footer copy.
                ignore_phrases = [
                    "Learn something about everything",
                    "Luke Ward is the owner",
                    "The facts on this page",
                    "If you notice anything",
                    "The Fact Site is the number one source"
                ]
                
                if any(phrase in headline_text for phrase in ignore_phrases):
                    continue
                
                topic_data = {
                    "topic": headline_text,
                }
                all_extracted_topics.append(topic_data)
            
    except Exception as e:
        print(f"Web scraper connection sequence crashed: {e}")
        error['error'] = e 
        return error

    # Resolve the topic archive path under the project data directory.
    output_file = PROJECT_ROOT / "data" / "json" / "latest_topics.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    current_date = datetime.now().strftime("%Y-%m-%d")
    
    existing_data = {}
    if output_file.exists() and output_file.stat().st_size > 0:
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                loaded_content = json.load(f)
                if isinstance(loaded_content, dict):
                    existing_data = loaded_content
        except json.JSONDecodeError:
            error['error'] = e 
            return error

    # Index scraped topics by collection date for downstream lookup.
    existing_data[current_date] = all_extracted_topics
    
    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(existing_data, file, indent=4, ensure_ascii=False)
        
    return all_extracted_topics 

if __name__ == "__main__":
    search_for_topics()


