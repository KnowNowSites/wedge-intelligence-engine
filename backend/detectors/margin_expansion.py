"""
Margin Expansion Detector - Identifies high-margin manual service opportunities.
Queries reddit_posts, job_postings, app_store_reviews.
"""

from datetime import datetime
from backend.database import get_db_connection
from backend.utils import get_logger

logger = get_logger("margin_expansion_detector")

HIGH_MARGIN_KEYWORDS = [
    "consultant", "advisor", "freelancer", "contractor", "agency",
    "service provider", "professional services", "outsource"
]


def detect_margin_expansion() -> list[dict]:
    """Detect industries with high prices but manual delivery."""
    logger.info("Running margin expansion detector...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    candidates = []
    
    try:
        # Find job postings for high-margin manual roles
        cursor.execute("""
            SELECT inferred_industry, COUNT(*) as job_count
            FROM job_postings
            WHERE job_title LIKE '%consultant%' OR job_title LIKE '%advisor%'
                OR job_title LIKE '%coordinator%' OR job_title LIKE '%manager%'
            GROUP BY inferred_industry
            HAVING job_count >= 5
            ORDER BY job_count DESC
            LIMIT 50
        """)
        
        manual_industries = cursor.fetchall()
        logger.info(f"Found {len(manual_industries)} industries with manual roles")
        
        for industry, job_count in manual_industries:
            # Calculate margin expansion score
            margin_score = min(10.0, 3.0 + (job_count / 5.0))
            
            candidates.append({
                "detector_name": "margin_expansion",
                "wedge_name": f"{industry}_margin_expansion",
                "industry": industry,
                "margin_score": margin_score,
                "manual_job_count": job_count,
                "signal_type": "high_manual_labor",
                "detected_at": datetime.now(),
            })
        
        logger.info(f"Margin expansion detector found {len(candidates)} candidates")
    
    except Exception as e:
        logger.error(f"Error in margin expansion detector: {e}")
    
    finally:
        conn.close()
    
    return candidates
