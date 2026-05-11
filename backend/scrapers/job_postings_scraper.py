"""
Job Postings Scraper - Detects industries scaling manually via job postings.
Uses Indeed RSS feeds and RemoteOK (no auth required).
Signals high volume of manual job titles = industry scaling manually instead of via software.
"""

from datetime import datetime
from backend.database import get_db_connection
from backend.utils import safe_scraper_execution, retry_with_backoff, randomized_delay, get_logger

logger = get_logger("job_postings_scraper")

# Keywords indicating manual processes
MANUAL_KEYWORDS = [
    "operations coordinator", "data entry specialist", "manual reporting",
    "excel specialist", "billing coordinator", "field operations",
    "dispatch coordinator", "workflow manager"
]

# Industries to monitor
INDUSTRIES_TO_MONITOR = [
    "roofing", "construction", "plumbing", "hvac", "landscaping",
    "accounting", "bookkeeping", "legal", "healthcare", "logistics",
    "transportation", "real estate", "property management"
]


@safe_scraper_execution("job_postings_scraper")
@retry_with_backoff(max_retries=3, base_delay=2.0)
def job_postings_scraper() -> list[dict]:
    """
    Scrape job postings for manual process signals.
    
    Returns:
        List of dicts with: job_title, company_name, inferred_industry, 
        posting_date, job_description_snippet, source_url
    """
    logger.info(f"Starting Job Postings scraper for {len(INDUSTRIES_TO_MONITOR)} industries...")
    
    try:
        import requests
        import feedparser
    except ImportError:
        logger.error("requests or feedparser not installed. Run: pip install requests feedparser")
        return []
    
    results = []
    
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        # Scrape Indeed RSS feeds for each industry
        for industry in INDUSTRIES_TO_MONITOR:
            try:
                logger.info(f"Scraping Indeed jobs for: {industry}")
                
                # Indeed RSS feed URL
                rss_url = f"https://www.indeed.com/rss?q={industry}+jobs&l=&sort=date"
                
                response = requests.get(rss_url, headers=headers, timeout=30)
                response.raise_for_status()
                
                feed = feedparser.parse(response.content)
                entries = feed.get('entries', [])
                
                logger.info(f"Found {len(entries)} job postings for {industry}")
                
                for entry in entries[:20]:  # Limit to 20 per industry
                    try:
                        # Extract job data
                        job_title = entry.get('title', '')
                        summary = entry.get('summary', '')
                        published = entry.get('published', '')
                        link = entry.get('link', '')
                        
                        # Extract company name from summary (usually first line)
                        company_name = ""
                        if summary:
                            lines = summary.split('<br />')
                            if lines:
                                company_name = lines[0].strip()
                        
                        # Check if job title contains manual keywords
                        job_title_lower = job_title.lower()
                        has_manual_signal = any(
                            keyword.lower() in job_title_lower 
                            for keyword in MANUAL_KEYWORDS
                        )
                        
                        if has_manual_signal:
                            results.append({
                                "job_title": job_title,
                                "company_name": company_name,
                                "inferred_industry": industry,
                                "posting_date": published,
                                "job_description_snippet": summary[:200],  # First 200 chars
                                "source_url": link,
                            })
                    
                    except Exception as e:
                        logger.debug(f"Error parsing job posting: {e}")
                        continue
                
                randomized_delay(2, 4)
            
            except Exception as e:
                logger.warning(f"Failed to scrape Indeed for {industry}: {e}")
                randomized_delay(2, 4)
                continue
        
        # Also try RemoteOK (alternative source)
        try:
            logger.info("Scraping RemoteOK for manual job titles...")
            
            remoteok_url = "https://remoteok.com/api"
            response = requests.get(remoteok_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            jobs = response.json()
            
            for job in jobs[:50]:  # Limit to 50 jobs
                try:
                    job_title = job.get('title', '')
                    company = job.get('company', '')
                    description = job.get('description', '')
                    url = job.get('url', '')
                    
                    # Check for manual keywords
                    job_title_lower = job_title.lower()
                    has_manual_signal = any(
                        keyword.lower() in job_title_lower 
                        for keyword in MANUAL_KEYWORDS
                    )
                    
                    if has_manual_signal:
                        results.append({
                            "job_title": job_title,
                            "company_name": company,
                            "inferred_industry": "remote",
                            "posting_date": datetime.now(),
                            "job_description_snippet": description[:200],
                            "source_url": url,
                        })
                
                except Exception as e:
                    logger.debug(f"Error parsing RemoteOK job: {e}")
                    continue
        
        except Exception as e:
            logger.warning(f"Failed to scrape RemoteOK: {e}")
    
    except Exception as e:
        logger.error(f"Job Postings scraper error: {e}")
        return []
    
    logger.info(f"Job Postings scraper completed: {len(results)} postings found")
    return results


def save_job_postings(postings: list[dict]) -> int:
    """Save job postings to database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    saved = 0
    for posting in postings:
        try:
            cursor.execute("""
                INSERT OR IGNORE INTO job_postings 
                (job_title, company_name, inferred_industry, posting_date, job_description_snippet, source_url, date_scraped)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                posting.get("job_title"),
                posting.get("company_name"),
                posting.get("inferred_industry"),
                posting.get("posting_date"),
                posting.get("job_description_snippet"),
                posting.get("source_url"),
                datetime.now(),
            ))
            saved += 1
        except Exception as e:
            logger.error(f"Failed to save job posting: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(postings)} job postings to database")
    return saved


if __name__ == "__main__":
    postings = job_postings_scraper()
    save_job_postings(postings)
