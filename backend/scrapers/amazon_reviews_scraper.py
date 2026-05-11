"""
Amazon Reviews Scraper - TODO STUB

This scraper is marked as TODO because:
- Amazon aggressively blocks scrapers and requires residential proxies
- Residential proxies are expensive ($10-50+ per GB)
- Amazon reviews are less reliable than app store reviews for B2B signals
- Alternative: Use app store reviews which are free and more relevant

If you need Amazon reviews, consider:
1. Using a paid proxy service (e.g., Bright Data, Oxylabs)
2. Using Amazon Product Advertising API (requires approval and fees)
3. Focusing on app store reviews instead (recommended)
"""

from backend.utils import get_logger

logger = get_logger("amazon_reviews_scraper")


def amazon_reviews_scraper() -> list[dict]:
    """
    TODO: Implement Amazon reviews scraper.
    
    Blocked: Requires expensive residential proxies.
    Alternative: Use app_store_scraper.py instead.
    """
    logger.warning("Amazon Reviews scraper not implemented (requires paid proxies)")
    return []
