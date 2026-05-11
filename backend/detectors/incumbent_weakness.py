"""
Incumbent Weakness Detector - Identifies weak incumbents with complaint patterns.
Queries app_store_reviews, play_store_reviews, reddit_posts, hn_posts.
"""

from datetime import datetime
from collections import defaultdict
from backend.database import get_db_connection
from backend.utils import get_logger

logger = get_logger("incumbent_weakness_detector")


def detect_incumbent_weakness() -> list[dict]:
    """
    Detect weak incumbents mentioned 10+ times with negative sentiment.
    
    Strategy:
    1. Group 1-2 star reviews by app name
    2. Flag any app mentioned 10+ times with negative sentiment
    3. Extract specific failure patterns (price, UX, missing feature, etc.)
    4. Generate wedge candidates
    
    Returns:
        List of wedge candidates
    """
    logger.info("Running incumbent weakness detector...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    candidates = []
    
    try:
        # Find apps with 10+ low-rated reviews
        cursor.execute("""
            SELECT app_name, COUNT(*) as complaint_count, AVG(rating) as avg_rating
            FROM (
                SELECT app_name, rating FROM app_store_reviews WHERE rating <= 2
                UNION ALL
                SELECT app_name, rating FROM play_store_reviews WHERE rating <= 2
            )
            GROUP BY app_name
            HAVING complaint_count >= 10
            ORDER BY complaint_count DESC
            LIMIT 50
        """)
        
        weak_incumbents = cursor.fetchall()
        logger.info(f"Found {len(weak_incumbents)} weak incumbents")
        
        for app_name, complaint_count, avg_rating in weak_incumbents:
            # Extract failure patterns
            cursor.execute("""
                SELECT review_text FROM app_store_reviews
                WHERE app_name = ? AND rating <= 2
                LIMIT 10
            """, (app_name,))
            
            reviews = cursor.fetchall()
            failure_patterns = extract_failure_patterns([r[0] for r in reviews])
            
            # Calculate weakness score
            weakness_score = min(10.0, 4.0 + (complaint_count / 5.0))
            
            candidates.append({
                "detector_name": "incumbent_weakness",
                "wedge_name": f"{app_name}_weakness",
                "incumbent_name": app_name,
                "weakness_score": weakness_score,
                "complaint_count": complaint_count,
                "avg_rating": avg_rating,
                "failure_patterns": failure_patterns,
                "detected_at": datetime.now(),
            })
        
        logger.info(f"Incumbent weakness detector found {len(candidates)} candidates")
    
    except Exception as e:
        logger.error(f"Error in incumbent weakness detector: {e}")
    
    finally:
        conn.close()
    
    return candidates


def extract_failure_patterns(reviews: list[str]) -> list[str]:
    """Extract common failure patterns from reviews."""
    patterns = {
        "price": 0,
        "ux": 0,
        "missing_feature": 0,
        "performance": 0,
        "support": 0,
    }
    
    price_keywords = ["expensive", "cost", "price", "too much"]
    ux_keywords = ["confusing", "hard to use", "unintuitive", "ugly"]
    feature_keywords = ["missing", "doesn't have", "no support for"]
    perf_keywords = ["slow", "crashes", "buggy", "freezes"]
    support_keywords = ["support", "help", "customer service"]
    
    for review in reviews:
        review_lower = review.lower()
        for keyword in price_keywords:
            if keyword in review_lower:
                patterns["price"] += 1
        for keyword in ux_keywords:
            if keyword in review_lower:
                patterns["ux"] += 1
        for keyword in feature_keywords:
            if keyword in review_lower:
                patterns["missing_feature"] += 1
        for keyword in perf_keywords:
            if keyword in review_lower:
                patterns["performance"] += 1
        for keyword in support_keywords:
            if keyword in review_lower:
                patterns["support"] += 1
    
    # Return top 3 patterns
    sorted_patterns = sorted(patterns.items(), key=lambda x: x[1], reverse=True)
    return [p[0] for p in sorted_patterns[:3] if p[1] > 0]


if __name__ == "__main__":
    candidates = detect_incumbent_weakness()
    for candidate in candidates:
        print(f"Incumbent: {candidate['incumbent_name']}, Weakness Score: {candidate['weakness_score']}")
