"""
Reddit Scraper - Extracts pain signals from targeted subreddits.
Uses Playwright for headless browsing (Reddit API is heavily restricted).
Implements exponential backoff retry logic and randomized delays.
"""

import sqlite3
import re
from datetime import datetime
from typing import Optional
from database import get_db_connection
from utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("reddit_scraper")

# Target subreddits for pain signal detection
TARGET_SUBREDDITS = [
    "entrepreneur", "startups", "smallbusiness", "SaaS", "Accounting",
    "legaladvice", "marketing", "ecommerce", "Trucking", "Construction",
    "Healthcare", "RealEstate", "personalfinance", "freelance",
    "msp", "ITManagers", "restaurantowners"
]

# Pain signal keywords to filter for
PAIN_KEYWORDS = [
    "hate", "broken", "no solution", "nobody solves", "switching from",
    "can't find software for", "we do this manually", "spreadsheet hell",
    "wish someone would build", "doesn't exist", "no tool for",
    "we hired a VA to", "costs too much", "terrible support"
]


def contains_pain_signal(text: str) -> bool:
    """Check if text contains any pain signal keywords."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in PAIN_KEYWORDS)


@safe_scraper_execution("reddit_scraper")
@retry_with_backoff(max_retries=3, base_delay=2.0)
def reddit_scraper() -> list[dict]:
    """
    Scrape Reddit for pain signals using Playwright.
    
    Returns:
        List of dicts with: subreddit, post_title, post_body, comment_text, 
        upvotes, comment_count, url, date_scraped
    """
    logger.info(f"Starting Reddit scraper for {len(TARGET_SUBREDDITS)} subreddits...")
    
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        logger.error("Playwright not installed. Run: pip install playwright && playwright install")
        return []
    
    results = []
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = context.new_page()
            
            for subreddit in TARGET_SUBREDDITS:
                try:
                    logger.info(f"Scraping r/{subreddit}...")
                    
                    # Navigate to subreddit
                    url = f"https://www.reddit.com/r/{subreddit}/hot/"
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    
                    # Wait for posts to load
                    page.wait_for_selector("[data-testid='post-container']", timeout=10000)
                    
                    # Extract posts
                    posts = page.query_selector_all("[data-testid='post-container']")
                    logger.info(f"Found {len(posts)} posts in r/{subreddit}")
                    
                    for post in posts[:10]:  # Limit to top 10 posts per subreddit
                        try:
                            # Extract post title
                            title_elem = post.query_selector("h3")
                            post_title = title_elem.text_content() if title_elem else ""
                            
                            # Extract post body
                            body_elem = post.query_selector("[data-testid='post-body']")
                            post_body = body_elem.text_content() if body_elem else ""
                            
                            # Extract upvotes
                            upvotes_elem = post.query_selector("[data-testid='upvote-button']")
                            upvotes_text = upvotes_elem.text_content() if upvotes_elem else "0"
                            upvotes = parse_number(upvotes_text)
                            
                            # Extract comment count
                            comments_elem = post.query_selector("[data-testid='comment-button']")
                            comments_text = comments_elem.text_content() if comments_elem else "0"
                            comment_count = parse_number(comments_text)
                            
                            # Extract post URL
                            link_elem = post.query_selector("a[href*='/r/']")
                            post_url = link_elem.get_attribute("href") if link_elem else ""
                            if post_url and not post_url.startswith("http"):
                                post_url = f"https://www.reddit.com{post_url}"
                            
                            # Check if post or body contains pain signals
                            if contains_pain_signal(post_title) or contains_pain_signal(post_body):
                                results.append({
                                    "subreddit": subreddit,
                                    "post_title": post_title,
                                    "post_body": post_body,
                                    "comment_text": None,  # Would need to click and load comments
                                    "upvotes": upvotes,
                                    "comment_count": comment_count,
                                    "url": post_url,
                                    "date_scraped": datetime.now(),
                                })
                        
                        except Exception as e:
                            logger.debug(f"Error extracting post from r/{subreddit}: {e}")
                            continue
                    
                    # Apply rate limiting between subreddits
                    randomized_delay(3, 6)
                
                except Exception as e:
                    logger.warning(f"Failed to scrape r/{subreddit}: {e}")
                    continue
            
            browser.close()
    
    except Exception as e:
        logger.error(f"Playwright error: {e}")
        return []
    
    logger.info(f"Reddit scraper completed: {len(results)} pain signals found")
    return results


def parse_number(text: str) -> int:
    """Parse number from text (e.g., '1.2k' -> 1200)."""
    try:
        text = text.strip().lower()
        if 'k' in text:
            return int(float(text.replace('k', '')) * 1000)
        elif 'm' in text:
            return int(float(text.replace('m', '')) * 1000000)
        else:
            return int(''.join(filter(str.isdigit, text)) or 0)
    except:
        return 0


def save_reddit_posts(posts: list[dict]) -> int:
    """Save Reddit posts to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for post in posts:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO reddit_posts 
                (subreddit, post_title, post_body, comment_text, upvotes, comment_count, url, date_scraped)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post.get("subreddit"),
                post.get("post_title"),
                post.get("post_body"),
                post.get("comment_text"),
                post.get("upvotes", 0),
                post.get("comment_count", 0),
                post.get("url"),
                post.get("date_scraped", datetime.now()),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save Reddit post: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(posts)} Reddit posts to database")
    return saved


if __name__ == "__main__":
    posts = reddit_scraper()
    save_reddit_posts(posts)
