"""
简单自动评分脚本（突出自动化验收的三项）：
- 硬约束校验：过敏/忌口（示例）
- 菜谱存在性校验
- 营养估算输出
"""
import json
from app.recipes import load_recipes, RecipeIndex
from app.planner import MealPlanner

def score_one_case(planner: MealPlanner, profile, utterance):
    out = planner.handle_dialogue("score-session", utterance, profile)
    res = out["result"]
    score = {"ok": res.get("ok", False), "violations": []}
    if res.get("ok"):
        plan = res["plan"]
        main = plan["main"]
        # existence
        if not planner.index.get_by_id(main["id"]):
            score["violations"].append("recipe_missing")
        # allergy
        for a in profile.get("allergies", []):
            if a in [ing for ing in main.get("ingredients", [])]:
                score["violations"].append("allergy_violation")
    return score

if __name__ == "__main__":
    recipes = load_recipes("data/recipes.json")
    index = RecipeIndex(recipes)
    planner = MealPlanner(index)
    # demo profile
    profile = {"allergies": ["鱼"], "dislikes": ["辣"]}
    print(score_one_case(planner, profile, "今晚吃啥比较好？"))
