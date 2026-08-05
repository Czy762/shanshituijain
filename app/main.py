from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
from .recipes import RecipeIndex, load_recipes
from .planner import MealPlanner
from .schemas import UserProfile, PlanRequest, DialogueRequest

app = FastAPI(title="Personalized Meal Planning Agent")

# Load sample recipes at startup (scripts/build_index.py will generate if you replace data)
RECIPES_PATH = "data/recipes.json"
recipes = load_recipes(RECIPES_PATH)
index = RecipeIndex(recipes)
planner = MealPlanner(index)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/plan")
def plan(req: PlanRequest):
    profile: UserProfile = req.profile
    constraints = req.constraints or {}
    try:
        result = planner.plan_single_meal(profile.dict(), constraints)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/dialogue")
def dialogue(req: DialogueRequest):
    # simple session state kept in memory per session id (for demo only)
    return planner.handle_dialogue(req.session_id, req.user_utterance, req.profile.dict() if req.profile else None)

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
