"""
Y Combinator Scraper - Fetches YC company mentions from HN Algolia API.
Uses https://hn.algolia.com/api/v1/search - no authentication required.
"""

import hashlib
import requests
import sqlite3
import os
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("yc_scraper")

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'wie.db')


def make_signal_id(source: str, title: str, url: str = "") -> str:
    """Generate a deterministic 20-char hex id for a signal.
    Same source+title+url always produces the same id, so INSERT OR IGNORE
    correctly deduplicates on re-runs.
    """
    raw = f"{source}:{title}:{url}"
    return hashlib.md5(raw.encode()).hexdigest()[:20]


def yc_scraper() -> list[dict]:
    """
    Fetch Y Combinator company mentions from HN Algolia API.

    Returns:
        List of dicts with signal data
    """
    logger.info("Starting Y Combinator scraper from HN Algolia API...")

    results = []

    try:
        url = "https://hn.algolia.com/api/v1/search?query=YC+W24+OR+YC+S24+OR+YC+W25+OR+YC+S25&tags=story&hitsPerPage=100"

        response = requests.get(url, timeout=15)
        response.raise_for_status()

        hits = response.json().get('hits', [])
        logger.info(f"Found {len(hits)} YC-related posts from HN Algolia")

        for h in hits:
            try:
                title = h.get('title', '')
                story_text = h.get('story_text') or h.get('comment_text', '')
                url_val = h.get('url', '')
                score = h.get('points', 0)

                if title:
                    results.append({
                        'source': 'yc',
                        'type': 'company_launch',
                        'title': title,
                        'description': story_text,
                        'url': url_val,
                        'score': score,
                    })
            except Exception as e:
                logger.debug(f"Error parsing YC post: {e}")
                continue

        time.sleep(1)

    except Exception as e:
        logger.error(f"Y Combinator scraper error: {e}")
        return []

    logger.info(f"Y Combinator scraper completed: {len(results)} posts found")
    return results


def save_yc_signals(signals: list[dict]) -> int:
    """Save YC signals to signals table with deterministic ids for deduplication."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    saved = 0
    for signal in signals:
        try:
            title = signal.get('title', '')
            url = signal.get('url', '')
            signal_id = make_signal_id('yc', title, url)

            cursor.execute("""
                INSERT OR IGNORE INTO signals
                (id, source, type, title, description, url, score, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                signal_id,
                signal.get('source'),
                signal.get('type'),
                title,
                signal.get('description'),
                url,
                signal.get('score'),
            ))
            if cursor.rowcount > 0:
                saved += 1
        except Exception as e:
            logger.error(f"Failed to save YC signal: {e}")

    conn.commit()
    conn.close()
    logger.info(f"Saved {saved}/{len(signals)} YC signals to database (rest were duplicates)")
    return saved


if __name__ == "__main__":
    signals = yc_scraper()
    save_yc_signals(signals)
