"""
Distribution Gap Detector - Identifies rising keywords with no clear SaaS leader.
Queries google_trends, producthunt_launches, hn_posts.
"""

from datetime import datetime
from backend.database import get_db_connection
from backend.utils import get_logger

logger = get_logger("distribution_gap_detector")


def detect_distribution_gaps() -> list[dict]:
    """Detect distribution opportunities where demand exists but supply does not."""
    logger.info("Running distribution gap detector...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    candidates = []
    
    try:
        # Find rising Google Trends with high trend_score but low Product Hunt presence
        cursor.execute("""
            SELECT keyword, trend_score, is_breakout
            FROM google_trends
            WHERE is_breakout = 1 AND trend_score > 70
            ORDER BY trend_score DESC
            LIMIT 100
        """)
        
        rising_keywords = cursor.fetchall()
        logger.info(f"Found {len(rising_keywords)} rising keywords")
        
        for keyword, trend_score, is_breakout in rising_keywords:
            # Check if keyword appears in Product Hunt launches
            cursor.execute("""
                SELECT COUNT(*) FROM producthunt_launches
                WHERE category_tags LIKE ? OR tagline LIKE ?
            """, (f"%{keyword}%", f"%{keyword}%"))
            
            ph_count = cursor.fetchone()[0]
            
            # If rising but few Product Hunt launches, it's a distribution gap
            if ph_count < 3:
                distribution_score = min(10.0, (trend_score / 10.0))
                
                candidates.append({
                    "detector_name": "distribution_gap",
                    "wedge_name": f"{keyword}_distribution_gap",
                    "keyword": keyword,
                    "distribution_score": distribution_score,
                    "trend_score": trend_score,
                    "producthunt_presence": ph_count,
                    "detected_at": datetime.now(),
                })
        
        logger.info(f"Distribution gap detector found {len(candidates)} candidates")
    
    except Exception as e:
        logger.error(f"Error in distribution gap detector: {e}")
    
    finally:
        conn.close()
    
    return candidates
