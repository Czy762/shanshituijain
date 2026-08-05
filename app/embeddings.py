import os
from typing import List, Dict, Any, Optional
import numpy as np

try:
    from sentence_transformers import SentenceTransformer
    import faiss
    _HF_AVAILABLE = True
except Exception:
    _HF_AVAILABLE = False

class SemanticIndex:
    def __init__(self, recipes: List[Dict[str, Any]], model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        if not _HF_AVAILABLE:
            raise RuntimeError("sentence-transformers or faiss not available")
        self.recipes = recipes
        self.ids = [r["id"] for r in recipes]
        self.id_map = {r["id"]: r for r in recipes}
        self.model_name = model_name
        self.model = SentenceTransformer(model_name)
        self._build_index()

    def _build_index(self):
        texts = [r.get("name", "") + " " + " ".join(r.get("ingredients", [])) + " " + " ".join(r.get("tags", [])) for r in self.recipes]
        self.embeddings = self.model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        d = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(d)
        # normalize for cosine similarity
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)

    def search(self, query: str, top_k: int = 5, filter_fn=None):
        q_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        D, I = self.index.search(q_emb, top_k*3)
        results = []
        for idx, score in zip(I[0], D[0]):
            if idx < 0 or idx >= len(self.recipes):
                continue
            r = self.recipes[idx]
            if filter_fn and not filter_fn(r):
                continue
            results.append({"score": float(score), "recipe": r})
            if len(results) >= top_k:
                break
        return results

    def get_by_id(self, rid: str):
        return self.id_map.get(rid)
