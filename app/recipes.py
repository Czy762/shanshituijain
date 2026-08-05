import json
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
import os

def load_recipes(path: str) -> List[Dict[str, Any]]:
    if not os.path.exists(path):
        # create a sample file if missing
        sample = load_sample_recipes()
        with open(path, "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data

def load_sample_recipes():
    return [
        {
            "id": "r1",
            "name": "番茄炒鸡蛋",
            "ingredients": ["番茄", "鸡蛋", "盐", "油", "葱"],
            "steps": ["打鸡蛋", "炒番茄", "合并炒匀"],
            "cook_time_min": 15,
            "tags": ["家常", "夏季", "暖胃"],
            "nutrition": {"calories": 200, "protein": 10, "fat": 12, "carbs": 10}
        },
        {
            "id": "r2",
            "name": "土豆炖牛肉",
            "ingredients": ["土豆", "牛肉", "生抽", "姜", "油"],
            "steps": ["切块", "炖煮"],
            "cook_time_min": 60,
            "tags": ["家常", "冬季"],
            "nutrition": {"calories": 500, "protein": 30, "fat": 20, "carbs": 40}
        },
        {
            "id": "r3",
            "name": "清爽凉拌黄瓜",
            "ingredients": ["黄瓜", "蒜", "醋", "盐"],
            "steps": ["切片", "拌匀"],
            "cook_time_min": 5,
            "tags": ["夏季", "凉菜"],
            "nutrition": {"calories": 50, "protein": 2, "fat": 1, "carbs": 8}
        },
        {
            "id": "r4",
            "name": "鸡蛋面条",
            "ingredients": ["面条", "鸡蛋", "葱", "盐", "油"],
            "steps": ["煮面", "打蛋拌入"],
            "cook_time_min": 10,
            "tags": ["快手", "夜宵"],
            "nutrition": {"calories": 350, "protein": 15, "fat": 8, "carbs": 50}
        },
        {
            "id": "r5",
            "name": "番茄土豆汤",
            "ingredients": ["番茄", "土豆", "盐", "香菜"],
            "steps": ["切块", "煮汤"],
            "cook_time_min": 20,
            "tags": ["汤", "清淡"],
            "nutrition": {"calories": 120, "protein": 3, "fat": 2, "carbs": 22}
        },
        {
            "id": "r6",
            "name": "蒸鱼（清蒸鲈鱼）",
            "ingredients": ["鱼", "姜", "葱", "酱油"],
            "steps": ["处理鱼", "蒸制"],
            "cook_time_min": 25,
            "tags": ["宴请", "清淡", "海鲜"],
            "nutrition": {"calories": 250, "protein": 40, "fat": 8, "carbs": 0}
        }
    ]

class RecipeIndex:
    def __init__(self, recipes: List[Dict[str, Any]]):
        self.recipes = recipes
        self.id_map = {r["id"]: r for r in recipes}
        self._build_vector_index()

    def _build_vector_index(self):
        docs = []
        for r in self.recipes:
            text = r.get("name", "") + " " + " ".join(r.get("ingredients", [])) + " " + " ".join(r.get("tags", []))
            docs.append(text)
        self.vectorizer = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b")
        self.tfidf = self.vectorizer.fit_transform(docs)

    def search(self, query: str, top_k: int = 5, filter_fn=None):
        if not query:
            # fallback to short list by calories or time
            sims = np.array([1.0]*len(self.recipes))
        else:
            q_vec = self.vectorizer.transform([query])
            sims = linear_kernel(q_vec, self.tfidf).flatten()
        idxs = sims.argsort()[::-1]
        results = []
        for i in idxs:
            r = self.recipes[i]
            if filter_fn and not filter_fn(r):
                continue
            results.append({"score": float(sims[i]), "recipe": r})
            if len(results) >= top_k:
                break
        return results

    def get_by_id(self, rid: str):
        return self.id_map.get(rid)
