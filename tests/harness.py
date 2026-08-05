"""
自动测试 harness:
- 加载对话用例 JSON（和你提供的 file）
- 对每个用例按轮次调用 /dialogue 路由（这里直接调用 planner）
- 输出简单的评分/日志（是否使用库中菜谱，是否违反过敏/忌口）
"""
import json
import sys
from app.recipes import load_recipes, RecipeIndex
from app.planner import MealPlanner

RECIPES_PATH = "data/recipes.json"
DIALOG_FILE = "data/对话用例.json"

def load_dialogs(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def main(dialog_path=DIALOG_FILE):
    recipes = load_recipes(RECIPES_PATH)
    index = RecipeIndex(recipes)
    planner = MealPlanner(index)
    dialogs = load_dialogs(dialog_path)
    report = []
    for d in dialogs:
        sid = f"case-{d.get('id')}"
        # aggregate profile as blank for now; harness can be extended to use health profiles
        profile = {}
        for turn_idx, user in enumerate(d.get("user_messages", []), start=1):
            utterance = user
            out = planner.handle_dialogue(sid, utterance, profile)
            ok = out["result"].get("ok", False)
            plan = out["result"].get("plan", {})
            # validate existence
            violations = []
            if ok:
                main = plan.get("main", {}).get("id")
                if not index.get_by_id(main):
                    violations.append("主菜不在菜谱库中")
            report.append({
                "case_id": d.get("id"),
                "turn": turn_idx,
                "utterance": utterance,
                "ok": ok,
                "violations": violations,
                "plan_summary": plan.get("main", {}).get("name") if ok else None
            })
    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv)>1 else DIALOG_FILE
    main(path)
