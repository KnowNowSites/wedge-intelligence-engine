"""
Scheduler - APScheduler-based background job runner.
Runs each scraper on its defined cadence, then re-runs all detectors and scoring.
"""

import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from backend.config import Config
from backend.utils import get_logger
from backend.database import get_db_connection

logger = get_logger("scheduler")

scheduler = BackgroundScheduler()

# Scraper configurations (name, interval_hours, import_path)
SCRAPERS = [
    ("reddit", 24, "backend.scrapers.reddit_scraper", "reddit_scraper"),
    ("google_trends", 48, "backend.scrapers.google_trends_scraper", "google_trends_scraper"),
    ("app_store", 48, "backend.scrapers.app_store_scraper", "app_store_scraper"),
    ("play_store", 48, "backend.scrapers.play_store_scraper", "play_store_scraper"),
    ("producthunt", 24, "backend.scrapers.producthunt_scraper", "producthunt_scraper"),
    ("yc", 72, "backend.scrapers.yc_scraper", "yc_scraper"),
    ("sec_edgar", 72, "backend.scrapers.sec_edgar_scraper", "sec_edgar_scraper"),
    ("hackernews", 24, "backend.scrapers.hackernews_scraper", "hackernews_scraper"),
    ("job_postings", 48, "backend.scrapers.job_postings_scraper", "job_postings_scraper"),
    ("openvc", 72, "backend.scrapers.openvc_scraper", "openvc_scraper"),
]


def update_scraper_metadata(scraper_name: str, success: bool = True, error: str = None, results_count: int = 0):
    """Update last run time and error count for a scraper."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if success:
            cursor.execute("""
                INSERT INTO scraper_metadata (scraper_name, last_run, last_successful_run, error_count, last_error, results_count)
                VALUES (?, ?, ?, 0, NULL, ?)
                ON CONFLICT(scraper_name) DO UPDATE SET
                    last_run = ?,
                    last_successful_run = ?,
                    error_count = 0,
                    last_error = NULL,
                    results_count = ?
            """, (scraper_name, datetime.now(), datetime.now(), results_count, 
                  datetime.now(), datetime.now(), results_count))
        else:
            cursor.execute("""
                INSERT INTO scraper_metadata (scraper_name, last_run, error_count, last_error)
                VALUES (?, ?, 1, ?)
                ON CONFLICT(scraper_name) DO UPDATE SET
                    last_run = ?,
                    error_count = error_count + 1,
                    last_error = ?
            """, (scraper_name, datetime.now(), error, datetime.now(), error))
        
        conn.commit()
    except Exception as e:
        logger.error(f"Failed to update scraper metadata for {scraper_name}: {e}")
    finally:
        conn.close()


def run_scraper(scraper_name: str, import_path: str, func_name: str):
    """Run a single scraper and update metadata."""
    logger.info(f"[Scheduler] Starting scraper: {scraper_name}")
    
    try:
        # Dynamically import and run scraper
        module = __import__(import_path, fromlist=[func_name])
        scraper_func = getattr(module, func_name)
        
        # Run scraper
        results = scraper_func()
        results_count = len(results) if results else 0
        
        logger.info(f"[Scheduler] Scraper {scraper_name} completed: {results_count} results")
        update_scraper_metadata(scraper_name, success=True, results_count=results_count)
        
        # After each scraper, re-run detectors and scoring
        run_all_detectors()
        run_profile_generator()
        
    except Exception as e:
        logger.error(f"[Scheduler] Scraper {scraper_name} failed: {e}")
        update_scraper_metadata(scraper_name, success=False, error=str(e))


def run_all_detectors():
    """Run all wedge detectors and update candidates table."""
    logger.info("[Scheduler] Running all wedge detectors...")
    
    detectors = [
        ("pain_signal", "backend.detectors.pain_signal", "detect_pain_signals"),
        ("incumbent_weakness", "backend.detectors.incumbent_weakness", "detect_incumbent_weakness"),
        ("emerging_category", "backend.detectors.emerging_category", "detect_emerging_categories"),
        ("distribution_gap", "backend.detectors.distribution_gap", "detect_distribution_gaps"),
        ("regulation_change", "backend.detectors.regulation_change", "detect_regulation_changes"),
        ("margin_expansion", "backend.detectors.margin_expansion", "detect_margin_expansion"),
        ("geographic_wedge", "backend.detectors.geographic_wedge", "detect_geographic_wedges"),
    ]
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    for detector_name, import_path, func_name in detectors:
        try:
            logger.info(f"[Scheduler] Running detector: {detector_name}")
            
            # Dynamically import and run detector
            module = __import__(import_path, fromlist=[func_name])
            detector_func = getattr(module, func_name)
            
            # Run detector
            candidates = detector_func()
            logger.info(f"[Scheduler] Detector {detector_name} returned {len(candidates)} candidates")
            
            # Save candidates to database
            for candidate in candidates:
                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO wedge_candidates 
                        (detector_name, wedge_name, pain_score, spend_potential, growth_rate, 
                         expandability, distribution_score, competition_score, capital_required, 
                         regulatory_friction, detected_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        candidate.get("detector_name"),
                        candidate.get("wedge_name"),
                        candidate.get("pain_score", 5.0),
                        candidate.get("spend_potential", 5.0),
                        candidate.get("growth_rate", 5.0),
                        candidate.get("expandability", 5.0),
                        candidate.get("distribution_score", 5.0),
                        candidate.get("competition_score", 5.0),
                        candidate.get("capital_required", 5.0),
                        candidate.get("regulatory_friction", 5.0),
                        datetime.now(),
                    ))
                except Exception as e:
                    logger.debug(f"Error saving candidate: {e}")
            
            conn.commit()
        
        except Exception as e:
            logger.error(f"[Scheduler] Detector {detector_name} failed: {e}")
            continue
    
    conn.close()
    logger.info("[Scheduler] All detectors completed")


def run_profile_generator():
    """Run wedge profile generator."""
    logger.info("[Scheduler] Running wedge profile generator...")
    
    try:
        from backend.wedge_profile_generator import generate_wedge_profiles
        
        profiles_generated = generate_wedge_profiles()
        logger.info(f"[Scheduler] Generated {profiles_generated} wedge profiles")
    
    except Exception as e:
        logger.error(f"[Scheduler] Profile generator failed: {e}")


def schedule_scraper(scraper_name: str, interval_hours: int, import_path: str, func_name: str):
    """Schedule a scraper to run at regular intervals."""
    if interval_hours <= 0:
        logger.info(f"[Scheduler] Scraper {scraper_name} disabled (interval <= 0)")
        return
    
    def job():
        run_scraper(scraper_name, import_path, func_name)
    
    scheduler.add_job(
        job,
        trigger=IntervalTrigger(hours=interval_hours),
        id=f"scraper_{scraper_name}",
        name=f"Scraper: {scraper_name}",
        replace_existing=True,
    )
    logger.info(f"[Scheduler] Scheduled {scraper_name} to run every {interval_hours} hours")


def start_scheduler():
    """Start the APScheduler background scheduler."""
    if not Config.SCHEDULER_ENABLED:
        logger.info("[Scheduler] Scheduler disabled in configuration")
        return False
    
    try:
        # Schedule all scrapers
        for scraper_name, interval_hours, import_path, func_name in SCRAPERS:
            schedule_scraper(scraper_name, interval_hours, import_path, func_name)
        
        # Schedule periodic profile generation (every 6 hours)
        scheduler.add_job(
            run_profile_generator,
            trigger=IntervalTrigger(hours=6),
            id="profile_generator",
            name="Profile Generator",
            replace_existing=True,
        )
        
        # Start the scheduler
        scheduler.start()
        logger.info("[Scheduler] Scheduler started successfully")
        return True
    
    except Exception as e:
        logger.error(f"[Scheduler] Failed to start scheduler: {e}")
        return False


def stop_scheduler():
    """Stop the APScheduler background scheduler."""
    try:
        scheduler.shutdown()
        logger.info("[Scheduler] Scheduler stopped")
    except Exception as e:
        logger.error(f"[Scheduler] Failed to stop scheduler: {e}")


def get_scheduler_status() -> dict:
    """Get current scheduler status."""
    try:
        jobs = scheduler.get_jobs()
        return {
            "running": scheduler.running,
            "job_count": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                }
                for job in jobs
            ],
        }
    except Exception as e:
        logger.error(f"Error getting scheduler status: {e}")
        return {"running": False, "job_count": 0, "jobs": []}


if __name__ == "__main__":
    start_scheduler()
    
    # Keep running
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        stop_scheduler()
