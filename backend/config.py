"""
Configuration loader for WIE.
Reads environment variables and provides defaults.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)


class Config:
    """Configuration class for WIE."""
    
    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(Path(__file__).parent.parent / "wie.db"))
    
    # Reddit scraper
    REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
    REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")
    REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
    
    # Product Hunt scraper
    PRODUCTHUNT_API_TOKEN = os.getenv("PRODUCTHUNT_API_TOKEN", "")
    
    # Google Trends (no auth required, uses pytrends)
    GOOGLE_TRENDS_ENABLED = os.getenv("GOOGLE_TRENDS_ENABLED", "true").lower() == "true"
    
    # App Store scrapers
    APP_STORE_ENABLED = os.getenv("APP_STORE_ENABLED", "true").lower() == "true"
    PLAY_STORE_ENABLED = os.getenv("PLAY_STORE_ENABLED", "true").lower() == "true"
    
    # Scheduler
    SCHEDULER_ENABLED = os.getenv("SCHEDULER_ENABLED", "true").lower() == "true"
    
    # Scraper intervals (in hours)
    REDDIT_INTERVAL = int(os.getenv("REDDIT_INTERVAL", "24"))
    GOOGLE_TRENDS_INTERVAL = int(os.getenv("GOOGLE_TRENDS_INTERVAL", "48"))
    APP_STORE_INTERVAL = int(os.getenv("APP_STORE_INTERVAL", "48"))
    PLAY_STORE_INTERVAL = int(os.getenv("PLAY_STORE_INTERVAL", "48"))
    PRODUCTHUNT_INTERVAL = int(os.getenv("PRODUCTHUNT_INTERVAL", "24"))
    YC_INTERVAL = int(os.getenv("YC_INTERVAL", "72"))
    SEC_EDGAR_INTERVAL = int(os.getenv("SEC_EDGAR_INTERVAL", "72"))
    HACKERNEWS_INTERVAL = int(os.getenv("HACKERNEWS_INTERVAL", "24"))
    JOB_POSTINGS_INTERVAL = int(os.getenv("JOB_POSTINGS_INTERVAL", "48"))
    OPENVC_INTERVAL = int(os.getenv("OPENVC_INTERVAL", "72"))
    
    # Wedge scoring threshold
    WEDGE_SCORE_THRESHOLD = float(os.getenv("WEDGE_SCORE_THRESHOLD", "15.0"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate critical configuration."""
        missing = []
        
        # Check for API keys if scrapers are enabled
        if cls.REDDIT_INTERVAL > 0 and not all([
            cls.REDDIT_USERNAME,
            cls.REDDIT_PASSWORD,
            cls.REDDIT_CLIENT_ID,
            cls.REDDIT_CLIENT_SECRET,
        ]):
            missing.append("Reddit credentials (REDDIT_USERNAME, REDDIT_PASSWORD, REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET)")
        
        if cls.PRODUCTHUNT_INTERVAL > 0 and not cls.PRODUCTHUNT_API_TOKEN:
            missing.append("Product Hunt API token (PRODUCTHUNT_API_TOKEN)")
        
        if missing:
            print("⚠️  Missing configuration:")
            for item in missing:
                print(f"   - {item}")
            return False
        
        return True


# Example .env template
ENV_TEMPLATE = """
# Database
DATABASE_PATH=./wie.db

# Reddit Scraper (get from reddit.com/prefs/apps)
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret

# Product Hunt Scraper (get from producthunt.com/v2/oauth/applications)
PRODUCTHUNT_API_TOKEN=your_token

# Scraper intervals (hours)
REDDIT_INTERVAL=24
GOOGLE_TRENDS_INTERVAL=48
APP_STORE_INTERVAL=48
PLAY_STORE_INTERVAL=48
PRODUCTHUNT_INTERVAL=24
YC_INTERVAL=72
SEC_EDGAR_INTERVAL=72
HACKERNEWS_INTERVAL=24
JOB_POSTINGS_INTERVAL=48
OPENVC_INTERVAL=72

# Wedge scoring
WEDGE_SCORE_THRESHOLD=15.0

# Logging
LOG_LEVEL=INFO

# Feature flags
SCHEDULER_ENABLED=true
GOOGLE_TRENDS_ENABLED=true
APP_STORE_ENABLED=true
PLAY_STORE_ENABLED=true
"""


def create_env_template():
    """Create a .env.example file for users."""
    example_path = Path(__file__).parent.parent / ".env.example"
    if not example_path.exists():
        example_path.write_text(ENV_TEMPLATE)
        print(f"Created {example_path}")
