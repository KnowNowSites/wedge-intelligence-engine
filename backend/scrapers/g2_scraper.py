"""
G2 Reviews Scraper - TODO STUB

This scraper is marked as TODO because:
- G2 has aggressive bot protection (CloudFlare, rate limiting)
- Scraping G2 violates their Terms of Service
- G2 actively blocks and bans scraping IPs
- Alternative: Use app store reviews which are free and more accessible

If you need G2 data, consider:
1. Using G2's official API (requires approval and fees)
2. Using app store reviews instead (recommended)
3. Manual research for specific categories
"""

from utils import get_logger

logger = get_logger("g2_scraper")


def g2_scraper() -> list[dict]:
    """
    TODO: Implement G2 reviews scraper.
    
    Blocked: Aggressive bot protection and ToS restrictions.
    Alternative: Use app_store_scraper.py instead.
    """
    logger.warning("G2 scraper not implemented (aggressive bot protection)")
    return []
