"""
WIE Wedge Detection Modules.
Each detector queries the database and outputs scored wedge candidates.
"""

from .pain_signal import detect_pain_signals
from .incumbent_weakness import detect_incumbent_weakness
from .emerging_category import detect_emerging_category
from .distribution_gap import detect_distribution_gap
from .regulation_change import detect_regulation_change
from .margin_expansion import detect_margin_expansion
from .geographic_wedge import detect_geographic_wedge

__all__ = [
    "detect_pain_signals",
    "detect_incumbent_weakness",
    "detect_emerging_category",
    "detect_distribution_gap",
    "detect_regulation_change",
    "detect_margin_expansion",
    "detect_geographic_wedge",
]
