import json
from app.recipes import load_recipes, RecipeIndex
import sys

if __name__ == "__main__":
    path = "data/recipes.json"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    print("Loading recipes from", path)
    recs = load_recipes(path)
    idx = RecipeIndex(recs)
    print(f"Built index with {len(recs)} recipes.")
    # no separate file required as TF-IDF is in-memory; If needed we can persist vectorizer via joblib.
