"""
Wedge Profile Generator - Auto-generates full JSON profiles for high-scoring wedges.
Applies 5 rejection filters before storing results.
"""

import json
from datetime import datetime
from backend.database import get_db_connection
from backend.scoring import calculate_wedge_score, apply_rejection_filters
from backend.utils import get_logger

logger = get_logger("wedge_profile_generator")

WEDGE_SCORE_THRESHOLD = 15.0


def generate_wedge_profiles() -> int:
    """
    Generate full JSON profiles for all wedges scoring > 15.0.
    
    Process:
    1. Query wedge_candidates table
    2. Calculate wedge_score for each candidate
    3. Filter candidates scoring > 15.0
    4. Apply 5 rejection filters
    5. Generate full profile JSON
    6. Store in wedge_profiles table
    
    Returns:
        Number of profiles generated
    """
    logger.info(f"Starting wedge profile generator (threshold: {WEDGE_SCORE_THRESHOLD})...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    profiles_generated = 0
    
    try:
        # Query all candidates from detectors
        cursor.execute("""
            SELECT id, detector_name, wedge_name, pain_score, spend_potential, 
                   growth_rate, expandability, distribution_score, competition_score,
                   capital_required, regulatory_friction
            FROM wedge_candidates
            WHERE profile_generated = 0
            ORDER BY pain_score DESC
            LIMIT 1000
        """)
        
        candidates = cursor.fetchall()
        logger.info(f"Found {len(candidates)} candidates to evaluate")
        
        for candidate in candidates:
            try:
                candidate_id, detector_name, wedge_name, pain_score, spend_potential, \
                growth_rate, expandability, distribution_score, competition_score, \
                capital_required, regulatory_friction = candidate
                
                # Build scoring dict
                wedge_data = {
                    "pain_score": pain_score or 5.0,
                    "spend_potential": spend_potential or 5.0,
                    "growth_rate": growth_rate or 5.0,
                    "expandability": expandability or 5.0,
                    "distribution_score": distribution_score or 5.0,
                    "competition_score": competition_score or 5.0,
                    "capital_required": capital_required or 5.0,
                    "regulatory_friction": regulatory_friction or 5.0,
                }
                
                # Calculate wedge score
                score_result = calculate_wedge_score(wedge_data)
                wedge_score = score_result.get("wedge_score", 0.0)
                
                # Check if score exceeds threshold
                if wedge_score < WEDGE_SCORE_THRESHOLD:
                    continue
                
                # Apply rejection filters
                should_profile, rejection_flags = apply_rejection_filters(wedge_data)
                
                if not should_profile:
                    logger.info(f"Wedge {wedge_name} rejected: {rejection_flags}")
                    continue
                
                # Generate full profile
                profile = {
                    "wedge_name": wedge_name,
                    "detector_source": detector_name,
                    "wedge_score": wedge_score,
                    "scoring": {
                        "pain_score": wedge_data["pain_score"],
                        "spend_potential": wedge_data["spend_potential"],
                        "growth_rate": wedge_data["growth_rate"],
                        "expandability": wedge_data["expandability"],
                        "distribution_score": wedge_data["distribution_score"],
                        "competition_score": wedge_data["competition_score"],
                        "capital_required": wedge_data["capital_required"],
                        "regulatory_friction": wedge_data["regulatory_friction"],
                    },
                    "mrr_timeline": {
                        "to_10k_mrr_months": score_result.get("speed_to_10k_mrr_months"),
                        "to_100k_mrr_months": score_result.get("speed_to_100k_mrr_months"),
                    },
                    "enterprise_value": score_result.get("enterprise_value_ceiling"),
                    "complexity": score_result.get("operational_complexity"),
                    "generated_at": datetime.now().isoformat(),
                }
                
                # Store profile in database
                profile_json = json.dumps(profile)
                
                cursor.execute("""
                    INSERT INTO wedge_profiles (wedge_name, detector_source, wedge_score, profile_json, generated_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (wedge_name, detector_name, wedge_score, profile_json, datetime.now()))
                
                # Mark candidate as profiled
                cursor.execute("""
                    UPDATE wedge_candidates
                    SET profile_generated = 1, profile_generated_at = ?
                    WHERE id = ?
                """, (datetime.now(), candidate_id))
                
                profiles_generated += 1
                logger.info(f"Generated profile for {wedge_name} (score: {wedge_score:.2f})")
            
            except Exception as e:
                logger.error(f"Error generating profile for candidate {candidate_id}: {e}")
                continue
        
        conn.commit()
        logger.info(f"Wedge profile generator completed: {profiles_generated} profiles generated")
    
    except Exception as e:
        logger.error(f"Error in wedge profile generator: {e}")
    
    finally:
        conn.close()
    
    return profiles_generated


def get_top_wedges(limit: int = 20) -> list[dict]:
    """
    Get top wedges by score.
    
    Args:
        limit: Number of top wedges to return
        
    Returns:
        List of wedge profiles
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT wedge_name, wedge_score, profile_json, generated_at
            FROM wedge_profiles
            ORDER BY wedge_score DESC
            LIMIT ?
        """, (limit,))
        
        results = []
        for wedge_name, wedge_score, profile_json, generated_at in cursor.fetchall():
            try:
                profile = json.loads(profile_json)
                profile["wedge_score"] = wedge_score
                profile["generated_at"] = generated_at
                results.append(profile)
            except json.JSONDecodeError:
                logger.warning(f"Failed to parse profile JSON for {wedge_name}")
                continue
        
        return results
    
    except Exception as e:
        logger.error(f"Error fetching top wedges: {e}")
        return []
    
    finally:
        conn.close()


if __name__ == "__main__":
    profiles_generated = generate_wedge_profiles()
    print(f"Generated {profiles_generated} wedge profiles")
    
    top_wedges = get_top_wedges(10)
    print(f"\nTop 10 Wedges:")
    for wedge in top_wedges:
        print(f"  {wedge['wedge_name']}: {wedge['wedge_score']:.2f}")
