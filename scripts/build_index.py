import json
from app.recipes import load_recipes, RecipeIndex

# Try to build semantic index using embeddings if available
try:
    from app.embeddings import SemanticIndex
    HAVE_SEMANTIC = True
except Exception:
    HAVE_SEMANTIC = False

import sys

if __name__ == "__main__":
    path = "data/recipes.json"
    if len(sys.argv) > 1:
        path = sys.argv[1]
    print("Loading recipes from", path)
    recs = load_recipes(path)
    if HAVE_SEMANTIC:
        print("Building semantic FAISS index (this may use a model and take time)...")
        idx = SemanticIndex(recs)
        print("Built semantic index with", len(recs), "recipes.")
    else:
        idx = RecipeIndex(recs)
        print(f"Built TF-IDF index with {len(recs)} recipes.")
