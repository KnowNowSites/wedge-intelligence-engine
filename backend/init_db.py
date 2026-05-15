"""
Initialize SQLite database with all required tables.
Run this once before starting the application.
"""

import sqlite3
import os
from datetime import datetime

def init_database(db_path: str = "wie.db"):
    """Create all required tables in the SQLite database."""
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Users table (for auth)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            openId TEXT UNIQUE NOT NULL,
            name TEXT,
            email TEXT,
            loginMethod TEXT,
            role TEXT DEFAULT 'user' CHECK (role IN ('user', 'admin')),
            createdAt TEXT DEFAULT CURRENT_TIMESTAMP,
            updatedAt TEXT DEFAULT CURRENT_TIMESTAMP,
            lastSignedIn TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Signals table (unified view of all scraped data)
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
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(source, url)
        )
    """)
    
    # Wedge profiles table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wedge_profiles (
            id TEXT PRIMARY KEY,
            wedge_name TEXT NOT NULL,
            wedge_score REAL NOT NULL,
            detector_source TEXT,
            enterprise_value TEXT CHECK (enterprise_value IN ('low', 'medium', 'high', 'very_high')),
            complexity TEXT CHECK (complexity IN ('low', 'medium', 'high')),
            to_10k_mrr_months INTEGER,
            to_100k_mrr_months INTEGER,
            evidence_json TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(wedge_name, detector_source)
        )
    """)
    
    # Watchlist table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id TEXT PRIMARY KEY,
            wedge_id TEXT NOT NULL,
            status TEXT DEFAULT 'watching' CHECK (status IN ('watching', 'investigating', 'building', 'passed')),
            notes TEXT,
            date_added TEXT DEFAULT CURRENT_TIMESTAMP,
            last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wedge_id) REFERENCES wedge_profiles(id)
        )
    """)
    
    # Reddit posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reddit_posts (
            id TEXT PRIMARY KEY,
            subreddit TEXT,
            title TEXT,
            content TEXT,
            score INTEGER,
            url TEXT,
            created_at TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(subreddit, url)
        )
    """)
    
    # Hacker News posts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hn_posts (
            id TEXT PRIMARY KEY,
            hn_id TEXT UNIQUE,
            title TEXT,
            comment_text TEXT,
            score INTEGER,
            author TEXT,
            date_posted TEXT,
            url TEXT,
            thread_type TEXT,
            date_scraped TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # App Store reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_store_reviews (
            id TEXT PRIMARY KEY,
            app_name TEXT,
            rating INTEGER,
            review_text TEXT,
            reviewer_name TEXT,
            review_date TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(app_name, review_text)
        )
    """)
    
    # Play Store reviews table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS play_store_reviews (
            id TEXT PRIMARY KEY,
            app_name TEXT,
            rating INTEGER,
            review_text TEXT,
            reviewer_name TEXT,
            review_date TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(app_name, review_text)
        )
    """)
    
    # Google Trends table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS google_trends (
            id TEXT PRIMARY KEY,
            keyword TEXT,
            trend_score REAL,
            region TEXT,
            category TEXT,
            timestamp TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(keyword, region, timestamp)
        )
    """)
    
    # Product Hunt launches table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS producthunt_launches (
            id TEXT PRIMARY KEY,
            product_name TEXT,
            tagline TEXT,
            url TEXT,
            votes INTEGER,
            created_at TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(product_name, url)
        )
    """)
    
    # Y Combinator companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS yc_companies (
            id TEXT PRIMARY KEY,
            company_name TEXT,
            batch TEXT,
            vertical TEXT,
            description TEXT,
            url TEXT,
            founded_at TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_name, batch)
        )
    """)
    
    # SEC filings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sec_filings (
            id TEXT PRIMARY KEY,
            company_name TEXT,
            filing_type TEXT,
            content TEXT,
            filing_date TEXT,
            url TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_name, filing_type, filing_date)
        )
    """)
    
    # Job postings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS job_postings (
            id TEXT PRIMARY KEY,
            title TEXT,
            company TEXT,
            description TEXT,
            url TEXT,
            posted_date TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company, url)
        )
    """)
    
    # OpenVC companies table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS openvc_companies (
            id TEXT PRIMARY KEY,
            company_name TEXT,
            funding_amount REAL,
            funding_date TEXT,
            vertical TEXT,
            url TEXT,
            scraped_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(company_name, funding_date)
        )
    """)
    
    # Wedge candidates table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wedge_candidates (
            id TEXT PRIMARY KEY,
            wedge_name TEXT NOT NULL,
            detector_source TEXT,
            raw_score REAL,
            pain_score REAL,
            spend_potential REAL,
            growth_rate REAL,
            expandability REAL,
            distribution_score REAL,
            competition_score REAL,
            capital_required REAL,
            regulatory_friction REAL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(wedge_name, detector_source)
        )
    """)
    
    # Scraper metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraper_metadata (
            scraper_name TEXT PRIMARY KEY,
            last_run TEXT,
            last_successful_run TEXT,
            error_count INTEGER DEFAULT 0,
            last_error TEXT,
            results_count INTEGER DEFAULT 0
        )
    """)
    
    # Create indexes for common queries
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_source ON signals(source)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_type ON signals(type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_signals_score ON signals(score DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_wedge_profiles_score ON wedge_profiles(wedge_score DESC)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_wedge_id ON watchlist(wedge_id)")
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized: {db_path}")


if __name__ == "__main__":
    import sys
    db_path = sys.argv[1] if len(sys.argv) > 1 else "wie.db"
    init_database(db_path)
