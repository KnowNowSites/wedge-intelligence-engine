#!/usr/bin/env python3
"""
Run all 7 real detectors for WIE and complete the pipeline.
Re-runs are idempotent: existing candidates and profiles are updated in-place.
"""
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from detectors.pain_signal import detect_pain_signals
from detectors.incumbent_weakness import detect_incumbent_weakness
from detectors.emerging_category import detect_emerging_category
from detectors.distribution_gap import detect_distribution_gap
from detectors.regulation_change import detect_regulation_change
from detectors.margin_expansion import detect_margin_expansion
from detectors.geographic_wedge import detect_geographic_wedge
from database import get_db_connection
from utils import get_logger
from wedge_profile_generator import generate_wedge_profiles

logger = get_logger("run_detectors")


def save_candidates(detector_name, candidates):
    """Save detector candidates to wedge_candidates table.
    Uses INSERT OR REPLACE so re-runs update scores rather than erroring
    on the UNIQUE(detector_source, wedge_name) constraint.
    """
    if not candidates:
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()
    saved = 0

    try:
        for candidate in candidates:
            cursor.execute("""
                INSERT OR REPLACE INTO wedge_candidates (
                    detector_source, wedge_name, pain_score, spend_potential,
                    growth_rate, expandability, distribution_score, competition_score,
                    capital_required, regulatory_friction, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                candidate.get("detector_source", detector_name),
                candidate.get("wedge_name", "unknown"),
                candidate.get("pain_score", 0.0),
                candidate.get("spend_potential", 0.0),
                candidate.get("growth_rate", 0.0),
                candidate.get("expandability", 0.0),
                candidate.get("distribution_score", 0.0),
                candidate.get("competition_score", 0.0),
                candidate.get("capital_required", 0.0),
                candidate.get("regulatory_friction", 0.0),
            ))
            saved += 1

        conn.commit()
        logger.info(f"Saved/updated {saved} candidates from {detector_name}")
    except Exception as e:
        logger.error(f"Error saving candidates from {detector_name}: {e}")
    finally:
        conn.close()

    return saved


def run_all():
    print("[1/7] Running pain signal detector...")
    candidates = detect_pain_signals()
    save_candidates("pain_signal", candidates)

    print("[2/7] Running incumbent weakness detector...")
    candidates = detect_incumbent_weakness()
    save_candidates("incumbent_weakness", candidates)

    print("[3/7] Running emerging category detector...")
    candidates = detect_emerging_category()
    save_candidates("emerging_category", candidates)

    print("[4/7] Running distribution gap detector...")
    candidates = detect_distribution_gap()
    save_candidates("distribution_gap", candidates)

    print("[5/7] Running regulation change detector...")
    candidates = detect_regulation_change()
    save_candidates("regulation_change", candidates)

    print("[6/7] Running margin expansion detector...")
    candidates = detect_margin_expansion()
    save_candidates("margin_expansion", candidates)

    print("[7/7] Running geographic wedge detector...")
    candidates = detect_geographic_wedge()
    save_candidates("geographic_wedge", candidates)

    print("\nGenerating wedge profiles from candidates...")
    profiles_generated = generate_wedge_profiles()
    print(f"Generated/updated {profiles_generated} wedge profiles")

    print("\nAll detectors and profile generation complete.")


if __name__ == '__main__':
    run_all()
