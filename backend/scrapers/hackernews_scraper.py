"""
Hacker News Scraper - Extracts problem statements and pain signals.
Uses Hacker News Algolia search API (free, no auth required).
Endpoint: https://hn.algolia.com/api/v1/search
"""

from datetime import datetime
from database import get_db_connection
from utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger
import json
import sqlite3
import os

logger = get_logger("hackernews_scraper")

# Pain signal keywords
PAIN_KEYWORDS = [
    "pain", "problem", "nobody builds", "why isn't there",
    "I wish there was", "frustrating that"
]


@safe_scraper_execution("hackernews_scraper")
@retry_with_backoff(max_retries=3, base_delay=1.0)
def hackernews_scraper() -> list[dict]:
    """
    Scrape Hacker News Algolia API for pain signals and problem statements.
    
    Returns:
        List of dicts with: title, comment_text, score, author, date, url, thread_type
    """
    logger.info("Starting Hacker News scraper...")
    
    try:
        import requests
    except ImportError:
        logger.error("requests not installed. Run: pip install requests")
        return []
    
    results = []
    
    try:
        base_url = "https://hn.algolia.com/api/v1/search"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Search queries for different thread types and pain signals
        search_queries = [
            ("Ask HN: What are you building", "ask_hn_building"),
            ("Ask HN: Who wants to be hired", "ask_hn_hiring"),
            ("pain problem nobody builds", "pain_signal"),
            ("why isn't there frustrating", "pain_signal"),
        ]
        
        for query, thread_type in search_queries:
            try:
                params = {
                    "query": query,
                    "tags": "story",
                    "numericFilters": "created_at_i>%d" % (int(datetime.now().timestamp()) - 7*24*3600),
                    "hitsPerPage": 30,
                }
                
                response = requests.get(base_url, params=params, headers=headers, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for hit in data.get("hits", []):
                    try:
                        hn_id = hit.get("objectID")
                        title = hit.get("title", "")
                        comment_text = hit.get("comment_text", "")
                        score = hit.get("points", 0)
                        author = hit.get("author", "")
                        created_at = hit.get("created_at", "")
                        url = f"https://news.ycombinator.com/item?id={hn_id}"
                        
                        if title or comment_text:
                            results.append({
                                "hn_id": hn_id,
                                "title": title,
                                "comment_text": comment_text,
                                "score": score,
                                "author": author,
                                "date_posted": created_at,
                                "url": url,
                                "thread_type": thread_type,
                            })
                    
                    except Exception as e:
                        logger.debug(f"Error parsing HN result: {e}")
                        continue
                
                randomized_delay(1, 2)
            
            except Exception as e:
                logger.warning(f"Failed to search HN for '{query}': {e}")
                randomized_delay(1, 2)
                continue
    
    except Exception as e:
        logger.error(f"Hacker News scraper error: {e}")
        return []
    
    logger.info(f"Hacker News scraper completed: {len(results)} posts found")
    return results


def save_hn_posts(posts: list[dict]) -> int:
    """Save Hacker News posts to database."""
    try:
        # Use shared wie.db file
        db_path = os.path.join(os.path.dirname(__file__), "..", "..", "wie.db")
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        saved = 0
        for post in posts:
            try:
                # Save to signals table for unified view
                metadata = {
                    "author": post.get("author"),
                    "thread_type": post.get("thread_type")
                }
                cursor.execute("""
                    INSERT OR IGNORE INTO signals 
                    (id, source, type, title, description, score, url, metadata_json, created_at, scraped_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"hn_{post.get('hn_id')}",
                    "hackernews",
                    post.get("thread_type", "general"),
                    post.get("title"),
                    post.get("comment_text", ""),
                    post.get("score", 0),
                    post.get("url"),
                    json.dumps(metadata),
                    post.get("date_posted"),
                    datetime.now().isoformat(),
                ))
                saved += 1
            except Exception as e:
                logger.error(f"Failed to save HN signal: {e}")
        
        conn.commit()
        conn.close()
        logger.info(f"Saved {saved}/{len(posts)} HN signals to database")
        return saved
    except Exception as e:
        logger.error(f"Failed to save HN posts: {e}")
        return 0


if __name__ == "__main__":
    posts = hackernews_scraper()
    save_hn_posts(posts)
