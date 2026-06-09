"""
SEC EDGAR Scraper - Extracts regulatory and market signals from filings.
Uses SEC EDGAR Full-Text Search API (free, public, max 10 req/sec).
Endpoint: https://efts.sec.gov/LATEST/search-index?q=...
"""

from datetime import datetime
from database import get_db_connection
from utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("sec_edgar_scraper")

# Keyword clusters to search for market signals
KEYWORD_CLUSTERS = [
    "fragmented market OR no dominant player",
    "manual processes OR legacy systems OR no integrated solution",
    "increased competition from startups OR technology disruption",
    "labor shortage OR difficulty hiring OR workforce constraints",
    "new regulation OR compliance requirements OR regulatory change",
]


@safe_scraper_execution("sec_edgar_scraper")
@retry_with_backoff(max_retries=3, base_delay=1.0)
def sec_edgar_scraper() -> list[dict]:
    """
    Scrape SEC EDGAR for regulatory and market signals in 10-K and 10-Q filings.
    
    Returns:
        List of dicts with: company_name, filing_type, filing_date, industry_sic_code, 
        matched_keyword, excerpt, url
    """
    logger.info(f"Starting SEC EDGAR scraper for {len(KEYWORD_CLUSTERS)} keyword clusters...")
    
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        logger.error("requests or BeautifulSoup not installed. Run: pip install requests beautifulsoup4")
        return []
    
    results = []
    
    try:
        base_url = "https://efts.sec.gov/LATEST/search-index"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        for keyword_cluster in KEYWORD_CLUSTERS:
            try:
                logger.info(f"Searching SEC EDGAR for: {keyword_cluster}")
                
                # Build search query (limit to 10-K and 10-Q)
                query = f"({keyword_cluster}) AND (10-K OR 10-Q)"
                
                params = {
                    "q": query,
                    "count": 50,  # Fetch up to 50 results
                }
                
                response = requests.get(base_url, params=params, headers=headers, timeout=30)
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Parse results (structure varies, this is a simplified approach)
                # SEC EDGAR returns XML, so we parse it accordingly
                filings = soup.find_all('filing')
                
                logger.info(f"Found {len(filings)} filings for: {keyword_cluster}")
                
                for filing in filings[:10]:  # Limit to 10 per keyword cluster
                    try:
                        # Extract filing data
                        company_name_elem = filing.find('company-name')
                        company_name = company_name_elem.text if company_name_elem else ""
                        
                        filing_type_elem = filing.find('form-type')
                        filing_type = filing_type_elem.text if filing_type_elem else ""
                        
                        filing_date_elem = filing.find('filing-date')
                        filing_date = filing_date_elem.text if filing_date_elem else ""
                        
                        sic_code_elem = filing.find('sic-code')
                        sic_code = sic_code_elem.text if sic_code_elem else ""
                        
                        url_elem = filing.find('filing-href')
                        filing_url = url_elem.text if url_elem else ""
                        
                        # Extract excerpt around keyword
                        excerpt_elem = filing.find('snippet')
                        excerpt = excerpt_elem.text if excerpt_elem else ""
                        
                        if company_name and filing_type:
                            results.append({
                                "company_name": company_name,
                                "filing_type": filing_type,
                                "filing_date": filing_date,
                                "industry_sic_code": sic_code,
                                "matched_keyword": keyword_cluster,
                                "excerpt": excerpt[:200],  # Limit to 200 chars
                                "url": filing_url,
                            })
                    
                    except Exception as e:
                        logger.debug(f"Error parsing SEC filing: {e}")
                        continue
                
                # Respect rate limit (max 10 req/sec, so 100ms between requests)
                randomized_delay(0.1, 0.2)
            
            except Exception as e:
                logger.warning(f"Failed to search SEC EDGAR for '{keyword_cluster}': {e}")
                randomized_delay(0.1, 0.2)
                continue
    
    except Exception as e:
        logger.error(f"SEC EDGAR scraper error: {e}")
        return []
    
    logger.info(f"SEC EDGAR scraper completed: {len(results)} filings found")
    return results


def save_sec_filings(filings: list[dict]) -> int:
    """Save SEC filings to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for filing in filings:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO sec_filings 
                (company_name, filing_type, filing_date, industry_sic_code, matched_keyword, excerpt, url, date_scraped)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                filing.get("company_name"),
                filing.get("filing_type"),
                filing.get("filing_date"),
                filing.get("industry_sic_code"),
                filing.get("matched_keyword"),
                filing.get("excerpt"),
                filing.get("url"),
                datetime.now(),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save SEC filing: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(filings)} SEC filings to database")
    return saved


if __name__ == "__main__":
    filings = sec_edgar_scraper()
    save_sec_filings(filings)
