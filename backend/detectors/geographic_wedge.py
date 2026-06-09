"""
Geographic Wedge Detector - Identifies geographic expansion opportunities.
Queries unified signals table for geographic keywords.
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'wie.db')

GEOGRAPHIC_KEYWORDS = [
    'only in us', 'not available in', 'no equivalent in', 'international version',
    'global expansion', 'localization', 'regional', 'country specific',
    'us only', 'europe needs', 'asia market', 'latin america'
]

def detect_geographic_wedge():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    candidates = []
    try:
        signals = c.execute(
            "SELECT * FROM signals WHERE source IN ('hackernews', 'producthunt')"
        ).fetchall()

        for signal in signals:
            text = ' '.join(filter(None, [
                signal['title'] if 'title' in signal.keys() else '',
                signal['description'] if 'description' in signal.keys() else '',
            ])).lower()

            matched = [kw for kw in GEOGRAPHIC_KEYWORDS if kw in text]
            if len(matched) >= 1:
                candidates.append({
                    'detector_source': 'geographic_wedge',
                    'wedge_name': f"[NEEDS REVIEW] {signal['source'].upper()}: {signal['title'][:80]}",
                    'pain_score': 5.0,
                    'spend_potential': 6.0,
                    'growth_rate': 7.0,
                    'expandability': 8.0,
                    'distribution_score': 5.0,
                    'competition_score': 4.0,
                    'capital_required': 4.0,
                    'regulatory_friction': 3.0,
                    'evidence': json.dumps([{
                        'source': signal['source'],
                        'url': signal['url'] if 'url' in signal.keys() else '',
                        'matched_keywords': matched
                    }]),
                    'entry_segment': 'Unknown — needs manual review',
                    'parent_market': 'Unknown — needs manual review',
                })
    except Exception as e:
        print(f'geographic_wedge detector error: {e}')
    finally:
        conn.close()

    print(f'geographic_wedge: {len(candidates)} candidates found')
    return candidates

if __name__ == '__main__':
    results = detect_geographic_wedge()
    for r in results:
        print(r['wedge_name'][:80])
