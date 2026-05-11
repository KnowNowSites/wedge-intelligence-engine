"""
Y Combinator Scraper - Extracts company data and analyzes market signals.
Uses BeautifulSoup for static content scraping from ycombinator.com/companies.
"""

from datetime import datetime
from backend.database import get_db_connection
from backend.utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("yc_scraper")


@safe_scraper_execution("yc_scraper")
@retry_with_backoff(max_retries=3, base_delay=2.0)
def yc_scraper() -> list[dict]:
    """
    Scrape Y Combinator companies from ycombinator.com/companies.
    
    Returns:
        List of dicts with: company_name, batch, description, vertical, status, url
    """
    logger.info("Starting Y Combinator scraper...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("requests or BeautifulSoup not installed. Run: pip install requests beautifulsoup4")
        return []
    
    results = []
    
    try:
        # Fetch YC companies page
        url = "https://www.ycombinator.com/companies"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find company listings (structure may vary, adjust selectors as needed)
        company_items = soup.find_all('div', class_='company-card')
        
        if not company_items:
            # Try alternative selector
            company_items = soup.find_all('a', href=lambda x: x and '/companies/' in x)
        
        logger.info(f"Found {len(company_items)} company items")
        
        for item in company_items[:100]:  # Limit to first 100 for performance
            try:
                # Extract company name
                name_elem = item.find('h2') or item.find('h3')
                company_name = name_elem.text.strip() if name_elem else ""
                
                # Extract description
                desc_elem = item.find('p', class_='description')
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Extract batch (e.g., S24, W24)
                batch_elem = item.find('span', class_='batch')
                batch = batch_elem.text.strip() if batch_elem else ""
                
                # Extract vertical/category
                vertical_elem = item.find('span', class_='vertical')
                vertical = vertical_elem.text.strip() if vertical_elem else ""
                
                # Extract status (active/acquired/dead)
                status_elem = item.find('span', class_='status')
                status = status_elem.text.strip() if status_elem else "active"
                
                # Extract URL
                link_elem = item.find('a', href=True)
                company_url = link_elem.get('href', '') if link_elem else ""
                if company_url and not company_url.startswith('http'):
                    company_url = f"https://www.ycombinator.com{company_url}"
                
                if company_name:
                    results.append({
                        "company_name": company_name,
                        "batch": batch,
                        "description": description,
                        "vertical": vertical,
                        "status": status,
                        "url": company_url,
                    })
            
            except Exception as e:
                logger.debug(f"Error parsing YC company: {e}")
                continue
        
        randomized_delay(2, 4)
    
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
