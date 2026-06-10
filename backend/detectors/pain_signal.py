"""
Pain Signal Detector - Identifies high-volume complaints and negative sentiment.
Queries unified signals table for pain keywords.
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'wie.db')

PAIN_KEYWORDS = [
    'hate', 'broken', 'no solution', 'nobody solves', 'switching from',
    "can't find software", 'we do this manually', 'spreadsheet hell',
    'wish someone would build', "doesn't exist", 'no tool for',
    'we hired a VA', 'costs too much', 'terrible support',
    'painful', 'frustrating', 'nightmare', 'manual process',
    'no software', 'no platform', 'missing feature', 'wish it had',
    'ask hn', 'building', 'problem', 'need', 'help'
]

def detect_pain_signals():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    candidates = []
    try:
        signals = c.execute(
            "SELECT * FROM signals WHERE source IN ('hackernews', 'reddit', 'app_store', 'play_store')"
        ).fetchall()

        for row in signals:
            signal = dict(row)
            text = ' '.join(filter(None, [
                signal['title'] if 'title' in signal.keys() else '',
                signal['description'] if 'description' in signal.keys() else '',
            ])).lower()

            matched = [kw for kw in PAIN_KEYWORDS if kw in text]
            if len(matched) >= 1 or 'ask hn' in text:
                pain_score = min(10.0, 2.0 + len(matched) * 1.5)
                raw_score = float(signal.get('score') or 0)
                distribution_score = min(10.0, 3.0 + (raw_score / 20.0))
                
                candidates.append({
                    'detector_source': 'pain_signal',
                    'wedge_name': signal['title'][:100] if 'title' in signal.keys() else 'Unknown',
                    'pain_score': pain_score,
                    'spend_potential': 5.0,
                    'growth_rate': 5.0,
                    'expandability': 5.0,
                    'distribution_score': distribution_score,
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
        print(f'pain_signal detector error: {e}')
    finally:
        conn.close()

    print(f'pain_signal: {len(candidates)} candidates found')
    return candidates

if __name__ == '__main__':
    results = detect_pain_signals()
    for r in results:
        print(r['wedge_name'], '| score input:', r['pain_score'])
