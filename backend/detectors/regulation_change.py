"""
Regulation Change Detector - Identifies regulation-triggered wedges.
Queries sec_filings, reddit_posts, hn_posts.
"""

from datetime import datetime
from collections import defaultdict
from backend.database import get_db_connection
from backend.utils import get_logger

logger = get_logger("regulation_change_detector")

REGULATION_KEYWORDS = [
    "regulation", "compliance", "regulatory", "law", "legislation",
    "requirement", "mandate", "rule", "policy", "government"
]


def detect_regulation_changes() -> list[dict]:
    """Detect regulation-triggered wedges from SEC filings and discussions."""
    logger.info("Running regulation change detector...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    candidates = []
    regulation_signals = defaultdict(lambda: {"count": 0, "sources": set()})
    
    try:
        # Find SEC filings mentioning regulations
        cursor.execute("""
            SELECT company_name, industry_sic_code, matched_keyword, excerpt
            FROM sec_filings
            WHERE matched_keyword LIKE '%regulation%' OR matched_keyword LIKE '%compliance%'
            LIMIT 200
        """)
        
        sec_filings = cursor.fetchall()
        logger.info(f"Found {len(sec_filings)} SEC filings with regulation mentions")
        
        for company_name, sic_code, matched_keyword, excerpt in sec_filings:
            # Use SIC code as industry signal
            if sic_code:
                regulation_signals[sic_code]["count"] += 1
                regulation_signals[sic_code]["sources"].add("sec_filings")
        
        # Find Reddit discussions about regulations
        cursor.execute("""
            SELECT subreddit, post_title, post_body
            FROM reddit_posts
            WHERE post_title LIKE '%regulation%' OR post_title LIKE '%compliance%'
                OR post_body LIKE '%regulation%' OR post_body LIKE '%compliance%'
            LIMIT 200
        """)
        
        reddit_posts = cursor.fetchall()
        logger.info(f"Found {len(reddit_posts)} Reddit posts about regulations")
        
        for subreddit, post_title, post_body in reddit_posts:
            regulation_signals[subreddit]["count"] += 1
            regulation_signals[subreddit]["sources"].add("reddit")
        
        # Find HN discussions about regulations
        cursor.execute("""
            SELECT title, comment_text
            FROM hn_posts
            WHERE title LIKE '%regulation%' OR title LIKE '%compliance%'
                OR comment_text LIKE '%regulation%' OR comment_text LIKE '%compliance%'
            LIMIT 200
        """)
        
        hn_posts = cursor.fetchall()
        logger.info(f"Found {len(hn_posts)} HN posts about regulations")
        
        for title, comment_text in hn_posts:
            # Extract category from title
            category = title.split()[0] if title else "unknown"
            regulation_signals[category]["count"] += 1
            regulation_signals[category]["sources"].add("hackernews")
        
        # Generate wedge candidates
        for signal_name, signal_data in regulation_signals.items():
            count = signal_data["count"]
            source_count = len(signal_data["sources"])
            
            # Only create candidates with 3+ mentions across 2+ sources
            if count >= 3 and source_count >= 2:
                # Higher score if mentioned in multiple sources
                regulation_score = min(10.0, 3.0 + (count / 3.0) + (source_count * 0.5))
                
                candidates.append({
                    "detector_name": "regulation_change",
                    "wedge_name": f"{signal_name}_regulation",
                    "category": signal_name,
                    "regulation_score": regulation_score,
                    "mention_count": count,
                    "source_count": source_count,
                    "sources": list(signal_data["sources"]),
                    "detected_at": datetime.now(),
                })
        
        logger.info(f"Regulation change detector found {len(candidates)} candidates")
    
    except Exception as e:
        logger.error(f"Error in regulation change detector: {e}")
    
    finally:
        conn.close()
    
    return candidates
