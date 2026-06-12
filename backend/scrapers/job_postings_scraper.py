"""
Job Postings Scraper - Detects industries scaling manually via job postings.
Uses RemoteOK free JSON API (no authentication required).
Signals high volume of manual job titles = industry scaling manually instead of via software.
"""

import hashlib
import re
import sqlite3
import os
import time
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("job_postings_scraper")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'wie.db')


def get_db_connection():
    return sqlite3.connect(DB_PATH)


def make_signal_id(source: str, title: str, url: str = "") -> str:
    """Generate a deterministic 20-char hex id for a signal.
    Same source+title+url always produces the same id, so INSERT OR IGNORE
    correctly deduplicates on re-runs.
    """
    raw = f"{source}:{title}:{url}"
    return hashlib.md5(raw.encode()).hexdigest()[:20]


def job_postings_scraper() -> list[dict]:
    """
    Scrape job postings from RemoteOK API for market signals.

    Returns:
        List of dicts with: job_title, company_name, inferred_industry,
        posting_date, job_description_snippet, source_url
    """
    logger.info("Starting Job Postings scraper from RemoteOK...")

    try:
        import requests
    except ImportError:
        logger.error("requests not installed. Run: pip install requests")
        return []

    results = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        api_url = "https://remoteok.com/api"

        logger.info("Fetching jobs from RemoteOK API...")
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()

        jobs_data = response.json()
        logger.info(f"Found {len(jobs_data)} items from RemoteOK")

        for job in jobs_data[1:]:  # Skip first item (metadata)
            try:
                job_title = job.get("position", "")
                company_name = job.get("company", "")
                job_slug = job.get("slug", "")
                job_url = f"https://remoteok.com/{job_slug}" if job_slug else ""

                description = job.get("description", "")
                clean_desc = re.sub('<[^<]+?>', '', description)
                snippet = clean_desc[:200] if clean_desc else ""

                tags = job.get("tags", [])
                inferred_industry = tags[0] if tags else "Unknown"

                if job_title and company_name:
                    results.append({
                        "job_title": job_title,
                        "company_name": company_name,
                        "inferred_industry": inferred_industry,
                        "posting_date": job.get("date", datetime.now().isoformat()),
                        "job_description_snippet": snippet,
                        "source_url": job_url,
                    })

            except Exception as e:
                logger.debug(f"Error parsing RemoteOK job: {e}")
                continue

        time.sleep(1)

    except Exception as e:
        logger.error(f"Job Postings scraper error: {e}")
        return []

    logger.info(f"Job Postings scraper completed: {len(results)} jobs found")
    return results


def save_job_postings(postings: list[dict]) -> int:
    """Save job postings to signals table with deterministic ids for deduplication."""
    conn = get_db_connection()
    cursor = conn.cursor()

    saved = 0
    for posting in postings:
        try:
            title = posting.get("job_title", "")
            url = posting.get("source_url", "")
            signal_id = make_signal_id('job_postings', title, url)

            cursor.execute("""
                INSERT OR IGNORE INTO signals
                (id, source, type, title, description, url, score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                signal_id,
                'job_postings',
                'job_posting',
                title,
                posting.get("job_description_snippet"),
                url,
                0,
            ))
            if cursor.rowcount > 0:
                saved += 1
        except Exception as e:
            logger.error(f"Failed to save job posting: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(postings)} job postings to signals table (rest were duplicates)")
    return saved


if __name__ == "__main__":
    postings = job_postings_scraper()
    save_job_postings(postings)
