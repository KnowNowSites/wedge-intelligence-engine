"""
Geographic Wedge Detector - Identifies geographic expansion opportunities.
Queries yc_companies, producthunt_launches, openvc_companies.
"""

from datetime import datetime
from collections import defaultdict
from backend.database import get_db_connection
from backend.utils import get_logger

logger = get_logger("geographic_wedge_detector")

UNDERSERVED_REGIONS = ["MENA", "SEA", "LATAM", "Africa", "Eastern Europe"]
DOMINANT_REGIONS = ["US", "EU", "Western Europe"]


def detect_geographic_wedges() -> list[dict]:
    """Detect geographic expansion opportunities."""
    logger.info("Running geographic wedge detector...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    candidates = []
    
    try:
        # Find verticals with strong US/EU presence but no MENA/SEA/LATAM equivalent
        cursor.execute("""
            SELECT vertical, country, COUNT(*) as company_count
            FROM yc_companies
            WHERE vertical IS NOT NULL AND country IS NOT NULL
            GROUP BY vertical, country
            ORDER BY company_count DESC
        """)
        
        vertical_by_country = defaultdict(lambda: defaultdict(int))
        
        for vertical, country, company_count in cursor.fetchall():
            vertical_by_country[vertical][country] = company_count
        
        logger.info(f"Found {len(vertical_by_country)} verticals across countries")
        
        for vertical, country_counts in vertical_by_country.items():
            # Check if vertical has strong US/EU presence
            us_eu_presence = sum(
                count for country, count in country_counts.items()
                if country in DOMINANT_REGIONS
            )
            
            # Check if vertical has weak MENA/SEA/LATAM presence
            underserved_presence = sum(
                count for country, count in country_counts.items()
                if country in UNDERSERVED_REGIONS
            )
            
            # If strong in US/EU but weak elsewhere, it's a geographic wedge
            if us_eu_presence >= 3 and underserved_presence == 0:
                geographic_score = min(10.0, 4.0 + (us_eu_presence / 3.0))
                
                candidates.append({
                    "detector_name": "geographic_wedge",
                    "wedge_name": f"{vertical}_geographic",
                    "vertical": vertical,
                    "geographic_score": geographic_score,
                    "dominant_region_presence": us_eu_presence,
                    "underserved_regions": UNDERSERVED_REGIONS,
                    "detected_at": datetime.now(),
                })
        
        logger.info(f"Geographic wedge detector found {len(candidates)} candidates")
    
    except Exception as e:
        logger.error(f"Error in geographic wedge detector: {e}")
    
    finally:
        conn.close()
    
    return candidates
