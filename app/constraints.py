from typing import Dict, Any, List

def violates_allergy(recipe: Dict[str, Any], allergies: List[str]) -> bool:
    if not allergies:
        return False
    ing = [i.lower() for i in recipe.get("ingredients", [])]
    for a in allergies:
        if a.lower() in ing:
            return True
    return False

def violates_dislike(recipe: Dict[str, Any], dislikes: List[str]) -> bool:
    if not dislikes:
        return False
    ing = [i.lower() for i in recipe.get("ingredients", [])]
    for d in dislikes:
        if d.lower() in ing:
            return True
    return False

def within_time_limit(recipe: Dict[str, Any], time_limit_min: int) -> bool:
    if not time_limit_min:
        return True
    return recipe.get("cook_time_min", 9999) <= time_limit_min
