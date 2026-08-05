from typing import Dict, Any, List, Optional
from .recipes import RecipeIndex
from .constraints import violates_allergy, violates_dislike, within_time_limit
import uuid

# Simple in-memory session store (for demo)
_sessions: Dict[str, Dict[str, Any]] = {}

class MealPlanner:
    def __init__(self, index: RecipeIndex):
        self.index = index

    def _filter_fn(self, profile: Dict[str, Any], constraints: Dict[str, Any]):
        allergies = profile.get("allergies", [])
        dislikes = profile.get("dislikes", [])
        time_limit = constraints.get("time_limit_min") if constraints else None
        def fn(recipe):
            if violates_allergy(recipe, allergies):
                return False
            if violates_dislike(recipe, dislikes):
                return False
            if not within_time_limit(recipe, time_limit):
                return False
            return True
        return fn

    def plan_single_meal(self, profile: Dict[str, Any], constraints: Dict[str, Any]):
        # Build query from constraints/preferences
        q_parts = []
        if constraints.get("prefer_main"):
            q_parts.append(constraints["prefer_main"])
        if constraints.get("season"):
            q_parts.append(constraints["season"])
        if profile.get("diet_goal"):
            q_parts.append(profile["diet_goal"])
        query = " ".join(q_parts)
        filter_fn = self._filter_fn(profile, constraints or {})
        results = self.index.search(query, top_k=5, filter_fn=filter_fn)
        if not results:
            return {"ok": False, "reason": "未找到满足硬约束的菜谱"}
        # choose top 1 as main, and try to add a side if available (simple heuristic)
        main = results[0]["recipe"]
        plan = {"id": str(uuid.uuid4()), "main": main}
        # find side with different primary ingredient and short time
        side = None
        for r in results[1:]:
            candidate = r["recipe"]
            if candidate["id"] != main["id"] and candidate.get("cook_time_min", 999) <= max(15, main.get("cook_time_min", 999)):
                side = candidate
                break
        if side:
            plan["side"] = side
        # nutrition aggregation
        plan["nutrition_estimate"] = self._aggregate_nutrition([main] + ([side] if side else []))
        return {"ok": True, "plan": plan}

    def _aggregate_nutrition(self, recipes: List[Dict[str, Any]]):
        agg = {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
        for r in recipes:
            n = r.get("nutrition", {})
            for k in agg:
                agg[k] += n.get(k, 0)
        return agg

    def handle_dialogue(self, session_id: str, user_utterance: str, profile: Optional[Dict[str, Any]] = None):
        # Very simple dialogue manager: accumulate constraints like "不要辣", "半小时内", "两个人" via keyword heuristics
        if session_id not in _sessions:
            _sessions[session_id] = {"history": [], "constraints": {}, "profile": profile or {}}
        s = _sessions[session_id]
        s["history"].append(user_utterance)
        ut = user_utterance.lower()
        # basic parsing heuristics
        if "不要辣" in ut or "不辣" in ut or "别做辣" in ut:
            s["constraints"]["avoid_spicy"] = True
            s["constraints"].setdefault("dislikes", []).append("辣")
        if "半小时" in ut or "30分钟" in ut or "30 分钟" in ut:
            s["constraints"]["time_limit_min"] = 30
        if "两个人" in ut:
            s["constraints"]["servings"] = 2
        if "面" in ut:
            s["constraints"]["prefer_main"] = "面"
        # call planner
        res = self.plan_single_meal(s["profile"], s["constraints"])
        reply = {
            "session_id": session_id,
            "user": user_utterance,
            "constraints": s["constraints"],
            "result": res
        }
        return reply
