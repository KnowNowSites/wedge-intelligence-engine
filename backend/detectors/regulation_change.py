"""
Regulation Change Detector - Identifies regulation-driven opportunities.
Queries unified signals table for regulation keywords.
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'wie.db')

REGULATION_KEYWORDS = [
    'regulation', 'compliance', 'new law', 'mandate', 'required by',
    'gdpr', 'hipaa', 'sec', 'ftc', 'deadline', 'regulatory',
    'legal requirement', 'must comply', 'enforcement'
]

def detect_regulation_change():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    candidates = []
    try:
        signals = c.execute(
            "SELECT * FROM signals WHERE source IN ('sec_edgar', 'hackernews')"
        ).fetchall()

        for signal in signals:
            text = ' '.join(filter(None, [
                signal['title'] if 'title' in signal.keys() else '',
                signal['description'] if 'description' in signal.keys() else '',
            ])).lower()

            matched = [kw for kw in REGULATION_KEYWORDS if kw in text]
            if len(matched) >= 1:
                candidates.append({
                    'detector_source': 'regulation_change',
                    'wedge_name': f"[NEEDS REVIEW] {signal['source'].upper()}: {signal['title'][:80]}",
                    'pain_score': 7.0,
                    'spend_potential': 8.0,
                    'growth_rate': 5.0,
                    'expandability': 6.0,
                    'distribution_score': 6.0,
                    'competition_score': 4.0,
                    'capital_required': 6.0,
                    'regulatory_friction': 8.0,
                    'evidence': json.dumps([{
                        'source': signal['source'],
                        'url': signal['url'] if 'url' in signal.keys() else '',
                        'matched_keywords': matched
                    }]),
                    'entry_segment': 'Unknown — needs manual review',
                    'parent_market': 'Unknown — needs manual review',
                })
    except Exception as e:
        print(f'regulation_change detector error: {e}')
    finally:
        conn.close()

    print(f'regulation_change: {len(candidates)} candidates found')
    return candidates

if __name__ == '__main__':
    results = detect_regulation_change()
    for r in results:
        print(r['wedge_name'][:80])
