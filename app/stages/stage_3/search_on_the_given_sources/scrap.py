"""Scrape and extract readable article text from research source URLs."""

import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# Hostnames that serve client-rendered pages with no usable static HTML.
JS_ONLY_DOMAINS = {"msn.com", "www.msn.com"}


def search_for_sources(sources):
    """Fetch page content from each source URL and return consolidated research text."""
    error = {'error': None}

    try:

        hrefs = []

        research_data = ""

        for item in sources:
            href = item.get('href', item.get('url', None))
            body_text = item.get('body', '')
            if body_text:
                research_data += f"{body_text}\n\n"
                
            if href:
                hrefs.append(href)

        for href in hrefs:
            try:
                # Skip hosts that cannot be scraped with a plain HTTP client.
                domain = urlparse(href).netloc.lower()
                if domain in JS_ONLY_DOMAINS:
                    print(f"SKIPPED: {domain} is a JavaScript-only site, cannot scrape with requests.")
                    continue

                headers = {
                    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Connection": "keep-alive"
                }
                    
                with requests.Session() as session:
                    response = session.get(href, headers=headers, timeout=15)
                    
                    if response.status_code == 403:
                        print(f"ACCESS DENIED: {href} blocked the request (403). Skipping.")
                        continue
                    elif response.status_code != 200:
                        print(f"HTTP ERROR: {href} returned status {response.status_code}. Skipping.")
                        continue

                    soup = BeautifulSoup(response.content, "html.parser")
                    
                    # Strip navigation, chrome, and non-article markup before extraction.
                    for noise_tag in soup.find_all(["script", "style", "nav", "header", "footer", "aside"]):
                        noise_tag.decompose()

                    # Detect JavaScript-rendered pages that return an empty body.
                    body = soup.find("body")
                    body_text = body.get_text(strip=True) if body else ""
                    if len(body_text) < 100:
                        print(f"SKIPPED: {href} appears to be JavaScript-rendered (empty body).")
                        continue

                    # Try common CSS class patterns used by article containers.
                    article_container = None
                    container_classes = [
                        "article-body", "articlebody", "articlebodycontent",
                        "article-content", "article_content", "articleContent",
                        "story-body", "storybody", "story-content", "storytext",
                        "post-content", "postcontent", "post-body",
                        "entry-content", "content-body", "main-content",
                        "field-item", "node-content"
                    ]
                    
                    for cls in container_classes:
                        article_container = soup.find("div", class_=lambda c: c and cls in c)
                        if article_container:
                            break
                    
                    # Prefer paragraph tags inside the identified article container.
                    if article_container:
                        p_tags = article_container.find_all("p")
                    else:
                        # Fall back to semantic <article> markup when class selectors fail.
                        article_tag = soup.find("article")
                        if article_tag:
                            p_tags = article_tag.find_all("p")
                        else:
                            # Last resort: select the parent element with the most substantive paragraphs.
                            all_p = soup.find_all("p")
                            parent_scores = {}
                            for p in all_p:
                                text = p.get_text().strip()
                                if len(text) > 50 and p.parent:
                                    parent_id = id(p.parent)
                                    if parent_id not in parent_scores:
                                        parent_scores[parent_id] = {"element": p.parent, "count": 0}
                                    parent_scores[parent_id]["count"] += 1
                            
                            if parent_scores:
                                best_parent = max(parent_scores.values(), key=lambda x: x["count"])
                                p_tags = best_parent["element"].find_all("p")
                            else:
                                p_tags = all_p
                    
                    cleaned_text_blocks = []
                    for p in p_tags:
                        text_fragment = p.get_text().strip()
                        
                        # Drop short fragments and common subscription or legal boilerplate.
                        if len(text_fragment) > 35:
                            lower_text = text_fragment.lower()
                            if any(kw in lower_text for kw in ["subscription", "sign in", "sign up", "newsletter", "cookie", "copyright"]):
                                continue
                            cleaned_text_blocks.append(text_fragment)
                    
                    # Some sites store body copy in div/span elements instead of paragraphs.
                    if not cleaned_text_blocks:
                        fallback_selectors = ["excerpt", "summary", "description", "content-text", "teaser"]
                        for sel in fallback_selectors:
                            divs = soup.find_all(["div", "span"], class_=lambda c: c and sel in c)
                            for div in divs:
                                text = div.get_text().strip()
                                if len(text) > 50:
                                    cleaned_text_blocks.append(text)
                    
                    # Join extracted blocks with blank lines for readable downstream input.
                    clean_story_text = "\n\n".join(cleaned_text_blocks)
                    
                    if not clean_story_text:
                        print(f"PARSING FAILURE: No extractable text from {href}. Skipping.")
                        continue
                        
                    research_data += f"{clean_story_text}\n\n"

            except Exception as e:
                print(f"SCRAPING ERROR on {href}: {e}. Skipping.")
                continue
            
        return research_data

    except Exception as e:
        print(f"scrapping error: {e}")
        error['error'] = e 
        return error