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

    # --- Legacy individual tables (kept for backwards compat, scrapers now write to signals) ---

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

    # --- Active tables ---

    # Unified signals table (all scrapers write here)
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

    # Wedge candidates (detector output)
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

    # Wedge profiles (final scored profiles > 30.0)
    # UNIQUE(wedge_name, detector_source) prevents duplicate profiles on re-runs
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
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(wedge_name, detector_source)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profile_score ON wedge_profiles(wedge_score)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_profile_detector ON wedge_profiles(detector_source)")

    # Watchlist (user-saved wedges)
    # NOTE: column is wedge_id (not wedge_profile_id) - matches api_server.py
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wedge_id TEXT NOT NULL,
            user_notes TEXT,
            status TEXT DEFAULT 'Researching',
            date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (wedge_id) REFERENCES wedge_profiles(id),
            UNIQUE(wedge_id)
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_watchlist_status ON watchlist(status)")

    # Scraper metadata (run tracking)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS scraper_metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scraper_name TEXT UNIQUE NOT NULL,
            last_run TIMESTAMP,
            last_successful_run TIMESTAMP,
            error_count INTEGER DEFAULT 0,
            results_count INTEGER DEFAULT 0,
            last_error TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    # --- Migrations for existing databases ---
    # Safe to run on any DB state; each is wrapped in try/except
    _run_migrations(cursor, conn)

    conn.close()
    print(f"Database initialized at {DB_PATH}")


def _run_migrations(cursor, conn):
    """Apply schema migrations for databases initialized before this version."""

    # Migration 1: add results_count to scraper_metadata if missing
    try:
        cursor.execute("ALTER TABLE scraper_metadata ADD COLUMN results_count INTEGER DEFAULT 0")
        conn.commit()
    except Exception:
        pass  # Column already exists

    # Migration 2: rename wedge_profile_id -> wedge_id in watchlist if old schema exists
    # SQLite supports RENAME COLUMN since 3.25.0 (2018) - safe on all modern systems
    try:
        cursor.execute("ALTER TABLE watchlist RENAME COLUMN wedge_profile_id TO wedge_id")
        conn.commit()
    except Exception:
        pass  # Column already renamed or doesn't exist

    # Migration 3: add UNIQUE constraint to wedge_profiles
    # Can't add constraints to existing tables in SQLite; recreate only if needed
    try:
        cursor.execute("SELECT wedge_name, detector_source FROM wedge_profiles LIMIT 1")
        # Table exists — check if UNIQUE constraint is present by inspecting indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='wedge_profiles' AND name='idx_profile_unique_wedge'")
        if not cursor.fetchone():
            # No unique index yet — add it (won't enforce retroactively but prevents future dupes)
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_profile_unique_wedge ON wedge_profiles(wedge_name, detector_source)")
            conn.commit()
    except Exception:
        pass


if __name__ == "__main__":
    init_database()
