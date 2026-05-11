"""
Play Store Scraper - Extracts 1-2 star reviews with unmet need signals.
Uses google-play-scraper library for Google Play Store.
"""

from datetime import datetime
from backend.database import get_db_connection
from backend.utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("play_store_scraper")

UNMET_NEED_KEYWORDS = [
    "wish it had", "missing", "can't believe there's no",
    "need to add", "manually", "have to use another app for",
    "switched because", "doesn't support"
]

# Popular apps to scrape reviews from (by category)
APPS_TO_SCRAPE = [
    # Finance
    ("com.intuit.mint", "Finance"),
    ("com.quicken.quickenmobile", "Finance"),
    # Business
    ("com.asana.app", "Business"),
    ("com.monday", "Business"),
    # Productivity
    ("com.todoist", "Productivity"),
    ("com.evernote", "Productivity"),
    # Healthcare
    ("com.teladoc.teladoc", "Healthcare"),
    ("com.myfitnesspal.android", "Healthcare"),
    # Construction
    ("com.buildr.app", "Construction"),
    # Real Estate
    ("com.zillow.android", "Real Estate"),
]


def contains_unmet_need(text: str) -> bool:
    """Check if review text contains unmet need signals."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword.lower() in text_lower for keyword in UNMET_NEED_KEYWORDS)


@safe_scraper_execution("play_store_scraper")
@retry_with_backoff(max_retries=3, base_delay=2.0)
def play_store_scraper() -> list[dict]:
    """
    Scrape Google Play Store for 1-2 star reviews with unmet needs.
    
    Returns:
        List of dicts with: app_name, rating, review_text, review_date, app_category
    """
    logger.info(f"Starting Play Store scraper for {len(APPS_TO_SCRAPE)} apps...")
    
    try:
        from google_play_scraper import app, reviews
    except ImportError:
        logger.error("google-play-scraper not installed. Run: pip install google-play-scraper")
        return []
    
    results = []
    
    try:
        for app_id, category in APPS_TO_SCRAPE:
            try:
                logger.info(f"Scraping Play Store app: {app_id} ({category})")
                
                # Fetch app info
                try:
                    app_info = app(app_id, lang='en', country='us')
                    app_name = app_info.get('title', app_id)
                except Exception as e:
                    logger.debug(f"Could not fetch app info for {app_id}: {e}")
                    app_name = app_id
                
                # Fetch reviews (1-2 star only)
                try:
                    review_list, _ = reviews(
                        app_id,
                        lang='en',
                        country='us',
                        sort='newest',
                        count=50,  # Fetch 50 reviews per app
                        filter_score_with=1  # Filter for 1-star reviews
                    )
                    
                    for review in review_list:
                        if review.get('score', 0) <= 2 and contains_unmet_need(review.get('reviewText', '')):
                            results.append({
                                "app_name": app_name,
                                "rating": review.get('score', 1),
                                "review_text": review.get('reviewText'),
                                "review_date": review.get('reviewCreatedVersion'),
                                "app_category": category,
                            })
                    
                    # Also fetch 2-star reviews
                    review_list_2, _ = reviews(
                        app_id,
                        lang='en',
                        country='us',
                        sort='newest',
                        count=50,
                        filter_score_with=2  # Filter for 2-star reviews
                    )
                    
                    for review in review_list_2:
                        if contains_unmet_need(review.get('reviewText', '')):
                            results.append({
                                "app_name": app_name,
                                "rating": review.get('score', 2),
                                "review_text": review.get('reviewText'),
                                "review_date": review.get('reviewCreatedVersion'),
                                "app_category": category,
                            })
                
                except Exception as e:
                    logger.warning(f"Could not fetch reviews for {app_id}: {e}")
                
                randomized_delay(2, 4)
            
            except Exception as e:
                logger.warning(f"Failed to scrape Play Store app {app_id}: {e}")
                randomized_delay(2, 4)
                continue
    
    except Exception as e:
        logger.error(f"Play Store scraper error: {e}")
        return []
    
    logger.info(f"Play Store scraper completed: {len(results)} reviews found")
    return results


def save_play_store_reviews(reviews: list[dict]) -> int:
    """Save Play Store reviews to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for review in reviews:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO play_store_reviews 
                (app_name, rating, review_text, review_date, app_category, date_scraped)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                review.get("app_name"),
                review.get("rating", 1),
                review.get("review_text"),
                review.get("review_date"),
                review.get("app_category"),
                datetime.now(),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save Play Store review: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(reviews)} Play Store reviews to database")
    return saved


if __name__ == "__main__":
    reviews = play_store_scraper()
    save_play_store_reviews(reviews)
