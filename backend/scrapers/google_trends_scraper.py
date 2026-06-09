"""
Google Trends Scraper - Extracts rising keywords and breakout trends.
Uses pytrends library with conservative rate limiting (5+ second delays).
"""

from datetime import datetime
from database import get_db_connection
from utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("google_trends_scraper")

# Seed categories to monitor for B2B/vertical SaaS opportunities
SEED_CATEGORIES = [
    "B2B software", "vertical SaaS", "fintech", "healthcare tech",
    "logistics tech", "construction tech", "legal tech", "proptech",
    "HR tech", "field service software", "supply chain tools"
]


@safe_scraper_execution("google_trends_scraper")
@retry_with_backoff(max_retries=3, base_delay=5.0)
def google_trends_scraper() -> list[dict]:
    """
    Scrape Google Trends for rising keywords using pytrends.
    
    Returns:
        List of dicts with: keyword, trend_score, is_breakout, category, date_pulled
    """
    logger.info(f"Starting Google Trends scraper for {len(SEED_CATEGORIES)} categories...")
    
    try:
        from pytrends.request import TrendReq
    except ImportError:
        logger.error("pytrends not installed. Run: pip install pytrends")
        return []
    
    results = []
    
    try:
        # Initialize pytrends with conservative settings
        pytrends = TrendReq(hl='en-US', tz=360, retries=3, backoff_factor=0.1)
        
        for category in SEED_CATEGORIES:
            try:
                logger.info(f"Fetching trends for: {category}")
                
                # Get trending searches (rising queries)
                trending_df = pytrends.trending_searches(pn='united_states')
                
                if trending_df is not None and not trending_df.empty:
                    for idx, row in trending_df.iterrows():
                        keyword = row[0]
                        
                        # Assign trend score based on position (1-100)
                        trend_score = max(1, 100 - (idx * 5))
                        
                        results.append({
                            "keyword": keyword,
                            "trend_score": trend_score,
                            "is_breakout": idx < 5,  # Top 5 are breakout
                            "category": category,
                            "date_pulled": datetime.now(),
                        })
                
                # Get related topics for the category
                try:
                    pytrends.build_payload([category], timeframe='today 1m')
                    related_queries = pytrends.related_queries()
                    
                    if related_queries and category in related_queries:
                        rising = related_queries[category].get('rising', [])
                        
                        if rising is not None and not rising.empty:
                            for idx, row in rising.iterrows():
                                keyword = row.get('query', '')
                                trend_score = int(row.get('value', 50))
                                
                                results.append({
                                    "keyword": keyword,
                                    "trend_score": trend_score,
                                    "is_breakout": trend_score > 75,
                                    "category": category,
                                    "date_pulled": datetime.now(),
                                })
                
                except Exception as e:
                    logger.debug(f"Could not fetch related queries for {category}: {e}")
                
                # Apply conservative rate limiting (5-8 seconds between API calls)
                randomized_delay(5, 8)
            
            except Exception as e:
                logger.warning(f"Failed to fetch trends for {category}: {e}")
                randomized_delay(5, 8)
                continue
    
    except Exception as e:
        logger.error(f"Google Trends error: {e}")
        return []
    
    logger.info(f"Google Trends scraper completed: {len(results)} trends found")
    return results


def save_google_trends(trends: list[dict]) -> int:
    """Save Google Trends to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for trend in trends:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO google_trends 
                (keyword, trend_score, is_breakout, category, date_pulled)
                VALUES (?, ?, ?, ?, ?)
            """, (
                trend.get("keyword"),
                trend.get("trend_score", 50),
                trend.get("is_breakout", False),
                trend.get("category"),
                trend.get("date_pulled", datetime.now()),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save trend: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(trends)} trends to database")
    return saved


if __name__ == "__main__":
    trends = google_trends_scraper()
    save_google_trends(trends)
