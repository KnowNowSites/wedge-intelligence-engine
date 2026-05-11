"""
WIE Wedge Detection Modules.
Each detector queries the database and outputs scored wedge candidates.
"""

from .pain_signal import detect_pain_signals
from .incumbent_weakness import detect_incumbent_weakness
from .emerging_category import detect_emerging_categories
from .distribution_gap import detect_distribution_gaps
from .regulation_change import detect_regulation_changes
from .margin_expansion import detect_margin_expansion
from .geographic_wedge import detect_geographic_wedges

__all__ = [
    "detect_pain_signals",
    "detect_incumbent_weakness",
    "detect_emerging_categories",
    "detect_distribution_gaps",
    "detect_regulation_changes",
    "detect_margin_expansion",
    "detect_geographic_wedges",
]
