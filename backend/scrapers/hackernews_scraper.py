"""
Hacker News Scraper - Extracts problem statements and pain signals.
Uses Hacker News Algolia search API (free, no auth required).
Endpoint: https://hn.algolia.com/api/v1/search
"""

from datetime import datetime
from backend.database import get_db_connection
from backend.utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

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
                logger.info(f"Searching HN for: {query}")
                
                params = {
                    "query": query,
                    "tags": "story,comment",
                    "numericFilters": "created_at_i>0",  # All time
                    "hitsPerPage": 50,
                }
                
                response = requests.get(base_url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                hits = data.get('hits', [])
                
                logger.info(f"Found {len(hits)} results for: {query}")
                
                for hit in hits[:20]:  # Limit to 20 per query
                    try:
                        # Extract data
                        title = hit.get('title', hit.get('story_title', ''))
                        comment_text = hit.get('comment_text', '')
                        score = hit.get('points', 0)
                        author = hit.get('author', '')
                        hn_id = hit.get('objectID', '')
                        created_at = hit.get('created_at', '')
                        url = hit.get('url', '')
                        
                        # Build HN URL if not present
                        if not url and hn_id:
                            if hit.get('type') == 'comment':
                                url = f"https://news.ycombinator.com/item?id={hn_id}"
                            else:
                                url = f"https://news.ycombinator.com/item?id={hn_id}"
                        
                        # Check if contains pain signals
                        text_to_check = f"{title} {comment_text}".lower()
                        has_pain_signal = any(keyword.lower() in text_to_check for keyword in PAIN_KEYWORDS)
                        
                        if title or (comment_text and has_pain_signal):
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
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for post in posts:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO hn_posts 
                (hn_id, title, comment_text, score, author, date_posted, url, thread_type, date_scraped)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.get("hn_id"),
                post.get("title"),
                post.get("comment_text"),
                post.get("score", 0),
                post.get("author"),
                post.get("date_posted"),
                post.get("url"),
                post.get("thread_type"),
                datetime.now(),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save HN post: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(posts)} HN posts to database")
    return saved


if __name__ == "__main__":
    posts = hackernews_scraper()
    save_hn_posts(posts)
