"""
Y Combinator Scraper - Generates realistic YC company data for testing.
Uses known YC company names and verticals to create diverse signals.
"""

from datetime import datetime
from database import get_db_connection
from utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("yc_scraper")

# Real YC companies across different batches and verticals
YC_COMPANIES = [
    {"name": "Stripe", "batch": "S10", "vertical": "Fintech", "description": "Online payment processing platform"},
    {"name": "Airbnb", "batch": "S09", "vertical": "Travel", "description": "Peer-to-peer accommodation marketplace"},
    {"name": "Dropbox", "batch": "S07", "vertical": "Cloud Storage", "description": "File hosting and synchronization"},
    {"name": "Twitch", "batch": "S11", "vertical": "Gaming", "description": "Live streaming platform for gamers"},
    {"name": "Instacart", "batch": "S12", "vertical": "Logistics", "description": "Grocery delivery service"},
    {"name": "Brex", "batch": "S14", "vertical": "Fintech", "description": "Corporate credit card and financial services"},
    {"name": "Guidepoint", "batch": "S13", "vertical": "Enterprise", "description": "Expert network platform"},
    {"name": "Notion", "batch": "S16", "vertical": "Productivity", "description": "All-in-one workspace for notes and databases"},
    {"name": "Figma", "batch": "S15", "vertical": "Design", "description": "Collaborative design and prototyping tool"},
    {"name": "Canva", "batch": "S13", "vertical": "Design", "description": "Graphic design platform for non-designers"},
    {"name": "Slack", "batch": "S11", "vertical": "Communication", "description": "Team messaging and collaboration platform"},
    {"name": "Uber", "batch": "S09", "vertical": "Transportation", "description": "Ride-sharing and delivery platform"},
    {"name": "Doordash", "batch": "S13", "vertical": "Food Delivery", "description": "On-demand food delivery"},
    {"name": "Amplitude", "batch": "S12", "vertical": "Analytics", "description": "Product analytics platform"},
    {"name": "Plaid", "batch": "S13", "vertical": "Fintech", "description": "Financial data connectivity API"},
    {"name": "Gusto", "batch": "S12", "vertical": "HR", "description": "Payroll and HR software"},
    {"name": "Mixpanel", "batch": "S09", "vertical": "Analytics", "description": "Mobile analytics platform"},
    {"name": "Zendesk", "batch": "S08", "vertical": "Customer Support", "description": "Customer service software"},
    {"name": "Segment", "batch": "S14", "vertical": "Data", "description": "Customer data platform"},
    {"name": "Intercom", "batch": "S11", "vertical": "Communication", "description": "Customer communication platform"},
]


@safe_scraper_execution("yc_scraper")
@retry_with_backoff(max_retries=3, base_delay=2.0)
def yc_scraper() -> list[dict]:
    """
    Generate realistic Y Combinator company data for testing.
    
    Returns:
        List of dicts with: company_name, batch, description, vertical, status, url
    """
    logger.info("Starting Y Combinator scraper...")
    
    results = []
    
    try:
        for company in YC_COMPANIES:
            results.append({
                "company_name": company["name"],
                "batch": company["batch"],
                "description": company["description"],
                "vertical": company["vertical"],
                "status": "active",
                "url": f"https://www.ycombinator.com/companies/{company['name'].lower()}",
            })
        
        randomized_delay(1, 2)
    
    except Exception as e:
        logger.error(f"Y Combinator scraper error: {e}")
        return []
    
    logger.info(f"Y Combinator scraper completed: {len(results)} companies found")
    return results


def save_yc_companies(companies: list[dict]) -> int:
    """Save Y Combinator companies to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for company in companies:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO yc_companies 
                (company_name, batch, description, vertical, status, url, date_scraped)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company.get("company_name"),
                company.get("batch"),
                company.get("description"),
                company.get("vertical"),
                company.get("status"),
                company.get("url"),
                datetime.now(),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save YC company: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(companies)} YC companies to database")
    return saved


if __name__ == "__main__":
    companies = yc_scraper()
    save_yc_companies(companies)
