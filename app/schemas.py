from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class UserProfile(BaseModel):
    id: Optional[str]
    name: Optional[str]
    age: Optional[int]
    sex: Optional[str]
    height_cm: Optional[float]
    weight_kg: Optional[float]
    bmi: Optional[float]
    diagnoses: Optional[List[str]] = []
    allergies: Optional[List[str]] = []
    dislikes: Optional[List[str]] = []
    diet_goal: Optional[str] = None  # e.g., "loss", "maintain", "muscle"
    extra: Optional[Dict[str, Any]] = {}

class PlanRequest(BaseModel):
    profile: UserProfile
    constraints: Optional[Dict[str, Any]] = None

class DialogueRequest(BaseModel):
    session_id: str
    user_utterance: str
    profile: Optional[UserProfile] = None
