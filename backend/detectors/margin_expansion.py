"""
Margin Expansion Detector - Identifies high-margin business opportunities.
Queries unified signals table for margin expansion keywords.
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'wie.db')

MARGIN_KEYWORDS = [
    'agency charges', 'consultant', 'hourly rate', 'manual work', 'we outsource',
    'expensive service', 'high margin', 'consulting fee', 'labor intensive',
    'professional services', 'billable hours', 'time and materials'
]

def detect_margin_expansion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    candidates = []
    try:
        signals = c.execute(
            "SELECT * FROM signals WHERE source IN ('hackernews', 'job_postings', 'reddit')"
        ).fetchall()

        for row in signals:
            signal = dict(row)
            text = ' '.join(filter(None, [
                signal['title'] if 'title' in signal.keys() else '',
                signal['description'] if 'description' in signal.keys() else '',
            ])).lower()

            matched = [kw for kw in MARGIN_KEYWORDS if kw in text]
            if len(matched) >= 1:
                candidates.append({
                    'detector_source': 'margin_expansion',
                    'wedge_name': f"[NEEDS REVIEW] {signal['source'].upper()}: {signal['title'][:80]}",
                    'pain_score': 6.0,
                    'spend_potential': 5.0,
                    'growth_rate': 5.0,
                    'expandability': 5.0,
                    'distribution_score': min(10.0, 3.0 + (float(signal.get("score") or 0) / 20.0)),
                    'competition_score': 5.0,
                    'capital_required': 5.0,
                    'regulatory_friction': 5.0,
                    'evidence': json.dumps([{
                        'source': signal['source'],
                        'url': signal['url'] if 'url' in signal.keys() else '',
                        'matched_keywords': matched
                    }]),
                    'entry_segment': 'Unknown — needs manual review',
                    'parent_market': 'Unknown — needs manual review',
                })
    except Exception as e:
        print(f'margin_expansion detector error: {e}')
    finally:
        conn.close()

    print(f'margin_expansion: {len(candidates)} candidates found')
    return candidates

if __name__ == '__main__':
    results = detect_margin_expansion()
    for r in results:
        print(r['wedge_name'][:80])
