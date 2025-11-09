from fuzzywuzzy import fuzz
from typing import List, Tuple

def find_closest_symptom(input_symptom: str, symptom_list: List[str], threshold: int = 80) -> Tuple[str, int]:
    """
    Find the closest matching symptom from the list using fuzzy string matching.
    
    Args:
        input_symptom (str): The symptom entered by the user
        symptom_list (List[str]): List of valid symptoms
        threshold (int): Minimum similarity score to consider a match
        
    Returns:
        Tuple[str, int]: Closest matching symptom and its similarity score
    """
    best_match = None
    best_ratio = 0
    
    input_symptom = input_symptom.lower().strip()
    
    for symptom in symptom_list:
        ratio = fuzz.ratio(input_symptom, symptom.lower())
        if ratio > best_ratio:
            best_ratio = ratio
            best_match = symptom
    
    if best_ratio >= threshold:
        return best_match, best_ratio
    return None, best_ratio