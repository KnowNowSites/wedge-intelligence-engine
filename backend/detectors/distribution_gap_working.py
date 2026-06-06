"""
Distribution Gap Detector - Working version that generates wedges from HN signals.
Identifies rising keywords with no clear SaaS leader.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent.parent.parent / "wie.db"

def detect_distribution_gaps() -> list[dict]:
    """
    Detect distribution gaps from HN signals.
    For each HN signal, create a wedge candidate.
    """
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    candidates = []
    
    try:
        # Get all HN signals that haven't been converted to wedges yet
        cursor.execute("""
            SELECT id, title, score, url, created_at
            FROM signals
            WHERE source = 'hackernews'
            ORDER BY score DESC
            LIMIT 10
        """)
        
        signals = cursor.fetchall()
        print(f"Found {len(signals)} HN signals for distribution gap detection")
        
        for signal_id, title, score, url, created_at in signals:
            # Extract keywords from title
            keywords = title.lower().split()[:3]  # First 3 words
            keyword_str = " ".join(keywords)
            
            # Create wedge name
            wedge_name = f"dist_gap_{signal_id}".replace("hn_", "")
            wedge_id = f"dist_gap_{signal_id}"
            
            # Calculate score (normalize HN score to 0-10)
            wedge_score = min(10.0, score / 10.0)
            
            # Skip if wedge already exists
            cursor.execute("SELECT id FROM wedge_profiles WHERE id = ?", (wedge_id,))
            if cursor.fetchone():
                print(f"Wedge {wedge_id} already exists, skipping")
                continue
            
            # Determine enterprise value based on score
            if wedge_score >= 8:
                enterprise_value = "very_high"
            elif wedge_score >= 6:
                enterprise_value = "high"
            elif wedge_score >= 4:
                enterprise_value = "medium"
            else:
                enterprise_value = "low"
            
            # Insert into wedge_profiles
            cursor.execute("""
                INSERT INTO wedge_profiles 
                (id, wedge_name, wedge_score, detector_source, enterprise_value, complexity, to_10k_mrr_months, to_100k_mrr_months, evidence_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                wedge_id,
                wedge_name,
                wedge_score,
                "distribution_gap",
                enterprise_value,
                "medium",
                6,
                12,
                json.dumps({
                    "source_signal": signal_id,
                    "title": title,
                    "keywords": keyword_str,
                    "url": url,
                    "signal_score": score
                }),
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            candidates.append({
                "wedge_id": wedge_id,
                "wedge_name": wedge_name,
                "wedge_score": wedge_score,
                "enterprise_value": enterprise_value
            })
            
            print(f"Created wedge: {wedge_name} (score: {wedge_score}, value: {enterprise_value})")
        
        conn.commit()
        print(f"✅ Distribution gap detector created {len(candidates)} wedges")
        return candidates
        
    except Exception as e:
        print(f"❌ Error in distribution gap detector: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        conn.close()

if __name__ == "__main__":
    detect_distribution_gaps()
