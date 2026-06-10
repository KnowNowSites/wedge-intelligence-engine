"""
SEC EDGAR Scraper - Fetches market signals from SEC filings.
Uses https://efts.sec.gov/LATEST/search-index - no authentication required.
"""

import requests
import sqlite3
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sec_edgar_scraper")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'wie.db')

KEYWORDS = ["fragmented market", "manual processes", "legacy systems", "labor shortage", "no dominant player"]


def scrape_sec() -> int:
    """
    Scrape SEC EDGAR for market signals based on keywords.
    
    Returns:
        Number of signals saved
    """
    logger.info("Starting SEC EDGAR scraper...")
    
    headers = {"User-Agent": "WIE Research Tool research@example.com"}
    conn = sqlite3.connect(DB_PATH)
    saved = 0
    
    for kw in KEYWORDS:
        try:
            url = f"https://efts.sec.gov/LATEST/search-index?q=%22{kw.replace(' ','+')}%22&forms=10-K&dateRange=custom&startdt=2023-01-01&enddt=2025-12-31"
            logger.info(f"Searching for: {kw}")
            
            r = requests.get(url, headers=headers, timeout=15)
            hits = r.json().get('hits', {}).get('hits', [])
            logger.info(f"Found {len(hits)} filings for: {kw}")
            
            for h in hits[:10]:
                try:
                    src = h.get('_source', {})
                    entity_name = src.get('entity_name', '')
                    period = src.get('period_of_report', '')
                    
                    if entity_name:
                        conn.execute("""
                            INSERT OR IGNORE INTO signals 
                            (source, type, title, description, url, score, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                        """, (
                            'sec_edgar',
                            'filing',
                            entity_name,
                            f"Keyword: {kw} | Period: {period}",
                            src.get('file_date', ''),
                            5,
                        ))
                        saved += 1
                except Exception as e:
                    logger.debug(f"Error parsing SEC filing: {e}")
                    continue
            
            time.sleep(3)
        
        except Exception as e:
            logger.error(f"SEC error for '{kw}': {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"SEC scraper: {saved} signals saved")
    return saved


if __name__ == '__main__':
    scrape_sec()
