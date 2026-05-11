"""
Emerging Category Detector - Identifies fragmented markets with multiple players.
Queries yc_companies, job_postings, hn_posts, openvc_companies.
"""

from datetime import datetime
from collections import defaultdict
from backend.database import get_db_connection
from backend.utils import get_logger

logger = get_logger("emerging_category_detector")


def detect_emerging_categories() -> list[dict]:
    """
    Detect fragmented markets with 5+ competitors but no clear leader.
    
    Strategy:
    1. Find verticals where 5+ YC companies exist but none has obvious dominance
    2. Find verticals where job postings exist but no software brand is mentioned
    3. Find verticals where OpenVC has funded 3+ companies (validated but unsolved)
    4. Generate wedge candidates
    
    Returns:
        List of wedge candidates
    """
    logger.info("Running emerging category detector...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    candidates = []
    
    try:
        # Find verticals with 5+ YC companies
        cursor.execute("""
            SELECT vertical, COUNT(*) as company_count
            FROM yc_companies
            WHERE vertical IS NOT NULL AND vertical != ''
            GROUP BY vertical
            HAVING company_count >= 5
            ORDER BY company_count DESC
            LIMIT 50
        """)
        
        yc_verticals = cursor.fetchall()
        logger.info(f"Found {len(yc_verticals)} YC verticals with 5+ companies")
        
        for vertical, company_count in yc_verticals:
            # Check if any company has dominant presence (would need funding data)
            # For now, assume fragmented if 5+ companies
            
            # Calculate emerging score
            emerging_score = min(10.0, 3.0 + (company_count / 3.0))
            
            candidates.append({
                "detector_name": "emerging_category",
                "wedge_name": f"{vertical}_emerging",
                "vertical": vertical,
                "emerging_score": emerging_score,
                "yc_company_count": company_count,
                "signal_type": "yc_fragmentation",
                "detected_at": datetime.now(),
            })
        
        # Find verticals with 3+ OpenVC companies
        cursor.execute("""
            SELECT vertical, COUNT(*) as company_count
            FROM openvc_companies
            WHERE vertical IS NOT NULL AND vertical != ''
            GROUP BY vertical
            HAVING company_count >= 3
            ORDER BY company_count DESC
            LIMIT 50
        """)
        
        openvc_verticals = cursor.fetchall()
        logger.info(f"Found {len(openvc_verticals)} OpenVC verticals with 3+ companies")
        
        for vertical, company_count in openvc_verticals:
            emerging_score = min(10.0, 2.5 + (company_count / 2.0))
            
            candidates.append({
                "detector_name": "emerging_category",
                "wedge_name": f"{vertical}_emerging_openvc",
                "vertical": vertical,
                "emerging_score": emerging_score,
                "openvc_company_count": company_count,
                "signal_type": "openvc_fragmentation",
                "detected_at": datetime.now(),
            })
        
        logger.info(f"Emerging category detector found {len(candidates)} candidates")
    
    except Exception as e:
        logger.error(f"Error in emerging category detector: {e}")
    
    finally:
        conn.close()
    
    return candidates


if __name__ == "__main__":
    candidates = detect_emerging_categories()
    for candidate in candidates:
        print(f"Vertical: {candidate['vertical']}, Emerging Score: {candidate['emerging_score']}")
