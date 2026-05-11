"""
Pain Signal Detector - Identifies high-volume complaints and negative sentiment.
Queries app_store_reviews, play_store_reviews, reddit_posts, hn_posts.
"""

from datetime import datetime, timedelta
from collections import defaultdict
from backend.database import get_db_connection
from backend.utils import get_logger

logger = get_logger("pain_signal_detector")

# Keywords indicating pain/unmet needs
PAIN_KEYWORDS = [
    "hate", "broken", "no solution", "nobody builds", "why isn't there",
    "I wish there was", "frustrating that", "missing", "can't believe",
    "need to add", "manually", "have to use another app", "switched because",
    "doesn't support", "wish it had"
]


def detect_pain_signals() -> list[dict]:
    """
    Detect pain signals from negative reviews and complaints.
    
    Strategy:
    1. Query 1-2 star app reviews with pain keywords
    2. Query Reddit posts with pain keywords
    3. Query HN posts with pain keywords
    4. Group by software/company name
    5. Calculate pain_score based on frequency and intensity
    6. Generate wedge candidates
    
    Returns:
        List of wedge candidates with pain_score and evidence
    """
    logger.info("Running pain signal detector...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    candidates = []
    pain_signals = defaultdict(lambda: {"count": 0, "evidence": []})
    
    try:
        # Query 1-2 star app store reviews
        cursor.execute("""
            SELECT app_name, review_text, rating, date_scraped
            FROM app_store_reviews
            WHERE rating <= 2 AND review_text IS NOT NULL
            ORDER BY date_scraped DESC
            LIMIT 500
        """)
        
        app_reviews = cursor.fetchall()
        logger.info(f"Found {len(app_reviews)} low-rated App Store reviews")
        
        for app_name, review_text, rating, date_scraped in app_reviews:
            if any(keyword.lower() in review_text.lower() for keyword in PAIN_KEYWORDS):
                pain_signals[app_name]["count"] += 1
                pain_signals[app_name]["evidence"].append({
                    "source": "app_store",
                    "text": review_text[:100],
                    "rating": rating,
                })
        
        # Query 1-2 star play store reviews
        cursor.execute("""
            SELECT app_name, review_text, rating, date_scraped
            FROM play_store_reviews
            WHERE rating <= 2 AND review_text IS NOT NULL
            ORDER BY date_scraped DESC
            LIMIT 500
        """)
        
        play_reviews = cursor.fetchall()
        logger.info(f"Found {len(play_reviews)} low-rated Play Store reviews")
        
        for app_name, review_text, rating, date_scraped in play_reviews:
            if any(keyword.lower() in review_text.lower() for keyword in PAIN_KEYWORDS):
                pain_signals[app_name]["count"] += 1
                pain_signals[app_name]["evidence"].append({
                    "source": "play_store",
                    "text": review_text[:100],
                    "rating": rating,
                })
        
        # Query Reddit posts with pain keywords
        cursor.execute("""
            SELECT subreddit, post_title, post_body, upvotes, date_scraped
            FROM reddit_posts
            WHERE (post_title LIKE ? OR post_body LIKE ?)
            ORDER BY date_scraped DESC
            LIMIT 300
        """, ("%pain%", "%pain%"))
        
        reddit_posts = cursor.fetchall()
        logger.info(f"Found {len(reddit_posts)} Reddit pain signal posts")
        
        for subreddit, post_title, post_body, upvotes, date_scraped in reddit_posts:
            combined_text = f"{post_title} {post_body}".lower()
            if any(keyword.lower() in combined_text for keyword in PAIN_KEYWORDS):
                # Use subreddit as signal source
                signal_key = f"{subreddit}_pain_signal"
                pain_signals[signal_key]["count"] += 1
                pain_signals[signal_key]["evidence"].append({
                    "source": "reddit",
                    "subreddit": subreddit,
                    "text": post_title[:100],
                    "upvotes": upvotes,
                })
        
        # Query HN posts with pain keywords
        cursor.execute("""
            SELECT title, comment_text, score, thread_type, date_scraped
            FROM hn_posts
            WHERE (title LIKE ? OR comment_text LIKE ?)
            ORDER BY date_scraped DESC
            LIMIT 300
        """, ("%pain%", "%pain%"))
        
        hn_posts = cursor.fetchall()
        logger.info(f"Found {len(hn_posts)} Hacker News pain signal posts")
        
        for title, comment_text, score, thread_type, date_scraped in hn_posts:
            combined_text = f"{title} {comment_text}".lower()
            if any(keyword.lower() in combined_text for keyword in PAIN_KEYWORDS):
                signal_key = f"{thread_type}_pain_signal"
                pain_signals[signal_key]["count"] += 1
                pain_signals[signal_key]["evidence"].append({
                    "source": "hackernews",
                    "text": title[:100],
                    "score": score,
                })
        
        # Generate wedge candidates from pain signals
        for signal_name, signal_data in pain_signals.items():
            count = signal_data["count"]
            
            # Only create candidates with 5+ pain signals
            if count >= 5:
                # Calculate pain_score (1-10 scale)
                # More signals = higher score, capped at 10
                pain_score = min(10.0, 3.0 + (count / 10.0))
                
                candidates.append({
                    "detector_name": "pain_signal",
                    "wedge_name": signal_name,
                    "pain_score": pain_score,
                    "pain_signal_count": count,
                    "evidence": signal_data["evidence"][:5],  # Top 5 evidence items
                    "detected_at": datetime.now(),
                })
        
        logger.info(f"Pain signal detector found {len(candidates)} candidates")
    
    except Exception as e:
        logger.error(f"Error in pain signal detector: {e}")
    
    finally:
        conn.close()
    
    return candidates


if __name__ == "__main__":
    candidates = detect_pain_signals()
    for candidate in candidates:
        print(f"Wedge: {candidate['wedge_name']}, Pain Score: {candidate['pain_score']}")
