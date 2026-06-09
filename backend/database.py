"""
SQLite database schema and initialization for WIE.
All tables are created with proper indexes and constraints.
"""

import sqlite3
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).parent.parent / "wie.db"


def get_db_connection():
    """Get a connection to the SQLite database."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the SQLite database with all required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Reddit posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subreddit TEXT NOT NULL,
            post_title TEXT NOT NULL,
            post_body TEXT,
            comment_text TEXT,
            upvotes INTEGER DEFAULT 0,
            comment_count INTEGER DEFAULT 0,
            url TEXT UNIQUE,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(subreddit, post_title, comment_text)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_subreddit ON reddit_posts(subreddit)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_reddit_date ON reddit_posts(date_scraped)")

    # Hacker News posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hn_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hn_id INTEGER UNIQUE,
            title TEXT NOT NULL,
            comment_text TEXT,
            score INTEGER DEFAULT 0,
            author TEXT,
            date_posted TIMESTAMP,
            url TEXT,
            thread_type TEXT,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hn_date ON hn_posts(date_posted)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_hn_type ON hn_posts(thread_type)")

    # App Store reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_store_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            platform TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review_text TEXT,
            review_date TIMESTAMP,
            app_category TEXT,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(app_name, platform, review_text)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_appstore_rating ON app_store_reviews(rating)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_appstore_category ON app_store_reviews(app_category)")

    # Play Store reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS play_store_reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_name TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review_text TEXT,
            review_date TIMESTAMP,
            app_category TEXT,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(app_name, review_text)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_playstore_rating ON play_store_reviews(rating)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_playstore_category ON play_store_reviews(app_category)")

    # Google Trends table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS google_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT NOT NULL,
            trend_score REAL NOT NULL,
            is_breakout BOOLEAN DEFAULT 0,
            category TEXT,
            date_pulled TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(keyword, category, date_pulled)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trends_keyword ON google_trends(keyword)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_trends_breakout ON google_trends(is_breakout)")

    # Product Hunt launches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS producthunt_launches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            tagline TEXT,
            upvotes INTEGER DEFAULT 0,
            comments INTEGER DEFAULT 0,
            category_tags TEXT,
            launch_date TIMESTAMP,
            url TEXT UNIQUE,
            hunter_username TEXT,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ph_upvotes ON producthunt_launches(upvotes)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_ph_launch_date ON producthunt_launches(launch_date)")

    # Y Combinator companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yc_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            batch TEXT,
            description TEXT,
            vertical TEXT,
            status TEXT,
            url TEXT UNIQUE,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_name, batch)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_yc_vertical ON yc_companies(vertical)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_yc_batch ON yc_companies(batch)")

    # SEC EDGAR filings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sec_filings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            filing_type TEXT,
            filing_date TIMESTAMP,
            industry_sic_code TEXT,
            matched_keyword TEXT,
            excerpt TEXT,
            url TEXT,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_name, filing_type, filing_date, matched_keyword)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sec_company ON sec_filings(company_name)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sec_keyword ON sec_filings(matched_keyword)")

    # Job postings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company_name TEXT,
            inferred_industry TEXT,
            posting_date TIMESTAMP,
            job_description_snippet TEXT,
            source_url TEXT UNIQUE,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_industry ON job_postings(inferred_industry)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_jobs_title ON job_postings(job_title)")

    # OpenVC companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS openvc_companies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT NOT NULL,
            vertical TEXT,
            funding_stage TEXT,
            country TEXT,
            description TEXT,
            source TEXT,
            date_scraped TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_name, vertical, country)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_openvc_vertical ON openvc_companies(vertical)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_openvc_stage ON openvc_companies(funding_stage)")

    # Signals table (unified view of all scraped signals)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS signals (
            id TEXT PRIMARY KEY,
            source TEXT NOT NULL,
            type TEXT NOT NULL,
            title TEXT,
            description TEXT,
            score REAL DEFAULT 0,
            url TEXT,
            metadata_json TEXT,
            created_at TEXT,
            scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_date ON signals(scraped_at)")

    # Wedge candidates table (output from detectors)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wedge_candidates (
            id TEXT PRIMARY KEY,
            detector_source TEXT NOT NULL,
            wedge_name TEXT NOT NULL,
            pain_score REAL DEFAULT 5.0,
            spend_potential REAL DEFAULT 5.0,
            growth_rate REAL DEFAULT 5.0,
            expandability REAL DEFAULT 5.0,
            distribution_score REAL DEFAULT 5.0,
            competition_score REAL DEFAULT 5.0,
            capital_required REAL DEFAULT 5.0,
            regulatory_friction REAL DEFAULT 5.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(detector_source, wedge_name)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wedge_detector ON wedge_candidates(detector_source)")

    # Wedge profiles table (final profiles for scores > 15.0)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wedge_profiles (
            id TEXT PRIMARY KEY,
            wedge_name TEXT NOT NULL,
            wedge_score REAL NOT NULL,
            detector_source TEXT,
            enterprise_value TEXT,
            complexity TEXT,
            to_10k_mrr_months INTEGER,
            to_100k_mrr_months INTEGER,
            evidence_json TEXT,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profile_score ON wedge_profiles(wedge_score)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profile_detector ON wedge_profiles(detector_source)")

    # Watchlist table (user-saved wedges)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wedge_profile_id INTEGER NOT NULL,
            user_notes TEXT,
            status TEXT DEFAULT 'Researching',
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wedge_profile_id) REFERENCES wedge_profiles(id),
            UNIQUE(wedge_profile_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_status ON watchlist(status)")

    # Scraper metadata table (track last run times)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraper_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scraper_name TEXT UNIQUE NOT NULL,
            last_run TIMESTAMP,
            last_successful_run TIMESTAMP,
            error_count INTEGER DEFAULT 0,
            last_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")


if __name__ == "__main__":
    init_database()
