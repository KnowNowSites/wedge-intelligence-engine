"""
Wedge Scoring Engine - Implements the wedge score formula and profile generation.
"""

from typing import Optional
from backend.utils import get_logger

logger = get_logger("scoring")


def calculate_wedge_score(wedge: dict) -> dict:
    """
    Calculate wedge score using the multi-factor formula.
    
    All inputs are floats from 1.0 to 10.0
    Higher = better for numerator fields
    Higher = worse for denominator fields
    
    Args:
        wedge: Dict with scoring dimensions
        
    Returns:
        Dict with wedge_score, speed_to_mrr estimates, EV ceiling, complexity
    """
    try:
        # Extract scoring dimensions (defaults to 5.0 if missing)
        pain_score = float(wedge.get("pain_score", 5.0))
        spend_potential = float(wedge.get("spend_potential", 5.0))
        growth_rate = float(wedge.get("growth_rate", 5.0))
        expandability = float(wedge.get("expandability", 5.0))
        distribution_score = float(wedge.get("distribution_score", 5.0))
        
        competition_score = float(wedge.get("competition_score", 5.0))
        capital_required = float(wedge.get("capital_required", 5.0))
        regulatory_friction = float(wedge.get("regulatory_friction", 5.0))
        
        # Calculate numerator and denominator
        numerator = (
            pain_score
            * spend_potential
            * growth_rate
            * expandability
            * distribution_score
        )
        
        denominator = (
            competition_score
            * capital_required
            * regulatory_friction
        )
        
        # Avoid division by zero
        if denominator == 0:
            denominator = 1.0
        
        base_score = round(numerator / denominator, 3)
        
        return {
            "wedge_score": base_score,
            "speed_to_10k_mrr_months": estimate_mrr_timeline(wedge, target=10000),
            "speed_to_100k_mrr_months": estimate_mrr_timeline(wedge, target=100000),
            "enterprise_value_ceiling": classify_ev(wedge),
            "operational_complexity": classify_complexity(wedge),
        }
    except Exception as e:
        logger.error(f"Error calculating wedge score: {e}")
        return {
            "wedge_score": 0.0,
            "speed_to_10k_mrr_months": None,
            "speed_to_100k_mrr_months": None,
            "enterprise_value_ceiling": "unknown",
            "operational_complexity": "unknown",
        }


def estimate_mrr_timeline(wedge: dict, target: int = 10000) -> Optional[int]:
    """
    Estimate months to reach target MRR.
    
    Uses heuristics based on:
    - Capital required (lower = faster)
    - Growth rate (higher = faster)
    - Distribution score (higher = faster)
    - Complexity (higher = slower)
    
    Args:
        wedge: Wedge candidate dict
        target: Target MRR in dollars (10000 or 100000)
        
    Returns:
        Estimated months to reach target, or None if unknown
    """
    try:
        capital_required = float(wedge.get("capital_required", 5.0))
        growth_rate = float(wedge.get("growth_rate", 5.0))
        distribution_score = float(wedge.get("distribution_score", 5.0))
        complexity = float(wedge.get("operational_complexity", 5.0))
        
        # Base timeline: 6-24 months depending on factors
        # Lower capital = faster (1-6 months)
        # Higher growth = faster (reduce by 2-4 months)
        # Higher distribution = faster (reduce by 1-3 months)
        # Higher complexity = slower (add 2-4 months)
        
        base_months = 12  # Default 12 months
        
        # Adjust for capital
        if capital_required < 3:
            base_months -= 4
        elif capital_required < 5:
            base_months -= 2
        elif capital_required > 7:
            base_months += 2
        
        # Adjust for growth
        if growth_rate > 7:
            base_months -= 3
        elif growth_rate > 5:
            base_months -= 1
        
        # Adjust for distribution
        if distribution_score > 7:
            base_months -= 2
        elif distribution_score > 5:
            base_months -= 1
        
        # Adjust for complexity
        if complexity > 7:
            base_months += 3
        elif complexity > 5:
            base_months += 1
        
        # Scale for target MRR
        if target == 100000:
            base_months += 6  # Takes longer to reach 100k
        
        return max(3, min(36, base_months))  # Clamp to 3-36 months
    except Exception as e:
        logger.error(f"Error estimating MRR timeline: {e}")
        return None


def classify_ev(wedge: dict) -> str:
    """
    Classify enterprise value ceiling.
    
    Args:
        wedge: Wedge candidate dict
        
    Returns:
        One of: "low", "medium", "high", "very_high"
    """
    try:
        expandability = float(wedge.get("expandability", 5.0))
        spend_potential = float(wedge.get("spend_potential", 5.0))
        market_size = float(wedge.get("market_size", 5.0))
        
        # Calculate EV score
        ev_score = (expandability + spend_potential + market_size) / 3
        
        if ev_score >= 8:
            return "very_high"
        elif ev_score >= 6:
            return "high"
        elif ev_score >= 4:
            return "medium"
        else:
            return "low"
    except Exception as e:
        logger.error(f"Error classifying EV: {e}")
        return "unknown"


def classify_complexity(wedge: dict) -> str:
    """
    Classify operational complexity.
    
    Args:
        wedge: Wedge candidate dict
        
    Returns:
        One of: "low", "medium", "high"
    """
    try:
        regulatory_friction = float(wedge.get("regulatory_friction", 5.0))
        capital_required = float(wedge.get("capital_required", 5.0))
        competition_score = float(wedge.get("competition_score", 5.0))
        
        # Calculate complexity score
        complexity_score = (regulatory_friction + capital_required + competition_score) / 3
        
        if complexity_score >= 7:
            return "high"
        elif complexity_score >= 4:
            return "medium"
        else:
            return "low"
    except Exception as e:
        logger.error(f"Error classifying complexity: {e}")
        return "unknown"


def apply_rejection_filters(wedge: dict) -> tuple[bool, list[str]]:
    """
    Apply 5 rejection filters to determine if wedge should be profiled.
    
    A wedge is rejected if 2 or more filters match.
    
    Args:
        wedge: Wedge candidate dict
        
    Returns:
        Tuple of (should_profile: bool, rejection_flags: list[str])
    """
    rejection_flags = []
    
    # Filter 1: Dominated by GAFAM with no vertical escape route
    if wedge.get("dominated_by_gafam") and not wedge.get("vertical_escape_route"):
        rejection_flags.append("dominated_by_gafam_no_escape")
    
    # Filter 2: Capital required > $500k
    capital_required = wedge.get("capital_required_dollars", 0)
    if capital_required > 500000:
        rejection_flags.append("capital_required_exceeds_500k")
    
    # Filter 3: No distribution channel identified
    if not wedge.get("distribution_channels") or len(wedge.get("distribution_channels", [])) == 0:
        rejection_flags.append("no_distribution_channel")
    
    # Filter 4: 3+ funded startups targeting identical entry segment
    funded_competitors = wedge.get("funded_competitors_count", 0)
    if funded_competitors >= 3:
        rejection_flags.append("3_plus_funded_competitors")
    
    # Filter 5: Regulatory barrier requires government license before first dollar
    if wedge.get("requires_government_license"):
        rejection_flags.append("requires_government_license")
    
    # Reject if 2 or more filters match
    should_profile = len(rejection_flags) < 2
    
    return should_profile, rejection_flags


if __name__ == "__main__":
    # Test scoring
    test_wedge = {
        "pain_score": 8.0,
        "spend_potential": 7.0,
        "growth_rate": 6.5,
        "expandability": 7.5,
        "distribution_score": 6.0,
        "competition_score": 4.0,
        "capital_required": 3.0,
        "regulatory_friction": 2.0,
    }
    
    result = calculate_wedge_score(test_wedge)
    print(f"Wedge Score: {result['wedge_score']}")
    print(f"Speed to $10k MRR: {result['speed_to_10k_mrr_months']} months")
    print(f"Speed to $100k MRR: {result['speed_to_100k_mrr_months']} months")
    print(f"EV Ceiling: {result['enterprise_value_ceiling']}")
    print(f"Complexity: {result['operational_complexity']}")
