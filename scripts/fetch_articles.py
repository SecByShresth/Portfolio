#!/usr/bin/env python3
"""
Fetch latest articles from Medium and Dev.to RSS feeds
and save them to data/articles.json
"""

import json
import os
import feedparser
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration
MEDIUM_RSS = "https://medium.com/feed/@shresthpaul133"
DEVTO_RSS = "https://dev.to/feed/secbyshresth"
OUTPUT_FILE = "data/articles.json"
MAX_ARTICLES = 20

def clean_html(html_text):
    """Remove HTML tags and clean text"""
    if not html_text:
        return ""
    soup = BeautifulSoup(html_text, 'html.parser')
    text = soup.get_text()
    # Clean up whitespace
    text = ' '.join(text.split())
    # Truncate to reasonable length for excerpt
    if len(text) > 200:
        text = text[:197] + "..."
    return text

def parse_date(entry):
    """Parse RSS date to timestamp for sorting"""
    try:
        # feedparser already parses the date into a time struct
        if hasattr(entry, 'published_parsed') and entry.published_parsed:
            return datetime(*entry.published_parsed[:6])
        elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
            return datetime(*entry.updated_parsed[:6])
        else:
            return datetime.min
    except Exception as e:
        print(f"⚠ Date parsing warning: {e}")
        return datetime.min

def fetch_medium_articles():
    """Fetch articles from Medium RSS feed"""
    articles = []
    try:
        feed = feedparser.parse(MEDIUM_RSS)
        for entry in feed.entries[:MAX_ARTICLES]:
            # Get content or summary
            content = entry.get('content', [{}])[0].get('value', '') or entry.get('summary', '')
            
            # Get published date
            pub_date = parse_date(entry)
            
            article = {
                'title': entry.title,
                'url': entry.link,
                'platform': 'medium',
                'excerpt': clean_html(content),
                'published': pub_date.isoformat() if pub_date != datetime.min else '',
                'updated_at': datetime.now().isoformat(),
                '_sort_date': pub_date  # For sorting only
            }
            articles.append(article)
        print(f"✓ Fetched {len(articles)} articles from Medium")
    except Exception as e:
        print(f"✗ Error fetching Medium articles: {e}")
    return articles

def fetch_devto_articles():
    """Fetch articles from Dev.to RSS feed"""
    articles = []
    try:
        feed = feedparser.parse(DEVTO_RSS)
        for entry in feed.entries[:MAX_ARTICLES]:
            # Get description or content
            content = entry.get('description', '') or entry.get('summary', '')
            
            # Get published date
            pub_date = parse_date(entry)
            
            article = {
                'title': entry.title,
                'url': entry.link,
                'platform': 'devto',
                'excerpt': clean_html(content),
                'published': pub_date.isoformat() if pub_date != datetime.min else '',
                'updated_at': datetime.now().isoformat(),
                '_sort_date': pub_date  # For sorting only
            }
            articles.append(article)
        print(f"✓ Fetched {len(articles)} articles from Dev.to")
    except Exception as e:
        print(f"✗ Error fetching Dev.to articles: {e}")
    return articles

def main():
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    
    print("📥 Fetching articles from Medium and Dev.to...")
    
    # Fetch articles from both platforms
    medium_articles = fetch_medium_articles()
    devto_articles = fetch_devto_articles()
    
    # Combine and sort by published date (newest first)
    all_articles = medium_articles + devto_articles
    
    # Sort by published date using the _sort_date field
    all_articles.sort(key=lambda x: x.get('_sort_date', datetime.min), reverse=True)
    
    # Remove the temporary _sort_date field before saving
    for article in all_articles:
        article.pop('_sort_date', None)
    
    print(f"✓ Sorted articles by date")
    
    # Save to JSON file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_articles, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Saved {len(all_articles)} total articles to {OUTPUT_FILE}")
    print(f"  - Medium: {len(medium_articles)} articles")
    print(f"  - Dev.to: {len(devto_articles)} articles")

if __name__ == "__main__":
    main()
