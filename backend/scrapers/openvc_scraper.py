"""
OpenVC Scraper - Extracts startup funding data as alternative to Crunchbase.
Uses OpenVC and Tracxn public pages (free replacement for Crunchbase).
Identifies verticals with early-stage funding (pre-seed/seed) or no recent funding.
"""

from datetime import datetime
from database import get_db_connection
from utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("openvc_scraper")


@safe_scraper_execution("openvc_scraper")
@retry_with_backoff(max_retries=3, base_delay=2.0)
def openvc_scraper() -> list[dict]:
    """
    Scrape OpenVC for startup funding data.
    
    Returns:
        List of dicts with: company_name, vertical, funding_stage, country, description
    """
    logger.info("Starting OpenVC scraper...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("requests or BeautifulSoup not installed. Run: pip install requests beautifulsoup4")
        return []
    
    results = []
    
    try:
        # OpenVC main page
        url = "https://openvc.app"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find startup listings (structure varies, adjust selectors as needed)
        startup_items = soup.find_all('div', class_='startup-card')
        
        if not startup_items:
            # Try alternative selector
            startup_items = soup.find_all('a', href=lambda x: x and '/startups/' in x)
        
        logger.info(f"Found {len(startup_items)} startup items")
        
        for item in startup_items[:100]:  # Limit to first 100
            try:
                # Extract company name
                name_elem = item.find('h3') or item.find('h2')
                company_name = name_elem.text.strip() if name_elem else ""
                
                # Extract description
                desc_elem = item.find('p', class_='description')
                description = desc_elem.text.strip() if desc_elem else ""
                
                # Extract vertical/industry
                vertical_elem = item.find('span', class_='vertical')
                vertical = vertical_elem.text.strip() if vertical_elem else ""
                
                # Extract funding stage
                stage_elem = item.find('span', class_='stage')
                funding_stage = stage_elem.text.strip() if stage_elem else ""
                
                # Extract country
                country_elem = item.find('span', class_='country')
                country = country_elem.text.strip() if country_elem else ""
                
                if company_name:
                    results.append({
                        "company_name": company_name,
                        "vertical": vertical,
                        "funding_stage": funding_stage,
                        "country": country,
                        "description": description,
                        "source": "openvc",
                    })
            
            except Exception as e:
                logger.debug(f"Error parsing OpenVC startup: {e}")
                continue
        
        # Also try Tracxn as backup source
        try:
            logger.info("Scraping Tracxn for startup data...")
            
            tracxn_url = "https://tracxn.com"
            response = requests.get(tracxn_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            startup_items = soup.find_all('div', class_='startup')[:50]  # Limit to 50
            
            for item in startup_items:
                try:
                    name_elem = item.find('h3')
                    company_name = name_elem.text.strip() if name_elem else ""
                    
                    desc_elem = item.find('p')
                    description = desc_elem.text.strip() if desc_elem else ""
                    
                    if company_name:
                        results.append({
                            "company_name": company_name,
                            "vertical": "",
                            "funding_stage": "",
                            "country": "",
                            "description": description,
                            "source": "tracxn",
                        })
                
                except Exception as e:
                    logger.debug(f"Error parsing Tracxn startup: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Failed to scrape Tracxn: {e}")
        
        randomized_delay(2, 4)
    
    except Exception as e:
        logger.error(f"OpenVC scraper error: {e}")
        return []
    
    logger.info(f"OpenVC scraper completed: {len(results)} companies found")
    return results


def save_openvc_companies(companies: list[dict]) -> int:
    """Save OpenVC companies to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for company in companies:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO openvc_companies 
                (company_name, vertical, funding_stage, country, description, source, date_scraped)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                company.get("company_name"),
                company.get("vertical"),
                company.get("funding_stage"),
                company.get("country"),
                company.get("description"),
                company.get("source", "openvc"),
                datetime.now(),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save OpenVC company: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(companies)} OpenVC companies to database")
    return saved


if __name__ == "__main__":
    companies = openvc_scraper()
    save_openvc_companies(companies)
