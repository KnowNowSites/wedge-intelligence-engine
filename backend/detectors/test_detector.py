"""
Test Detector - Simple detector that generates wedges from HN signals for testing.
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "wie.db"

def generate_test_wedges():
    """Generate test wedges from HN signals."""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    try:
        # Get all HN signals
        cursor.execute("SELECT id, title, score FROM signals WHERE source = 'hackernews' LIMIT 5")
        signals = cursor.fetchall()
        
        print(f"Found {len(signals)} HN signals")
        
        for signal_id, title, score in signals:
            # Create a wedge from each signal
            wedge_name = title[:50].replace(" ", "_").lower()
            wedge_id = f"test_{signal_id}"
            wedge_score = min(10.0, score / 10.0)  # Normalize score
            
            # Insert into wedge_profiles
            cursor.execute("""
                INSERT OR REPLACE INTO wedge_profiles 
                (id, wedge_name, wedge_score, detector_source, enterprise_value, complexity, to_10k_mrr_months, to_100k_mrr_months, evidence_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                wedge_id,
                wedge_name,
                wedge_score,
                "test_detector",
                "medium",
                "medium",
                6,
                12,
                json.dumps({"source_signal": signal_id, "title": title})
            ))
            
            print(f"Created wedge: {wedge_name} (score: {wedge_score})")
        
        conn.commit()
        print(f"✅ Generated {len(signals)} test wedges")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    generate_test_wedges()
