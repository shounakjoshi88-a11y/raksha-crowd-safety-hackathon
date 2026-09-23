"""Faiss cosine gallery. Embeddings must be L2-normalized (insightface normed_embedding is)."""
import json
import numpy as np
import faiss


class Gallery:
    def __init__(self, dim=512):
        self.index = faiss.IndexFlatIP(dim)
        self.names, self.metas = [], []

    def add(self, name, embedding, meta=None):
        v = np.asarray(embedding, dtype=np.float32).reshape(1, -1)
        v /= (np.linalg.norm(v) + 1e-9)
        self.index.add(v)
        self.names.append(name)
        self.metas.append(meta or {})

    def search(self, embedding, thresh=0.40):
        if self.index.ntotal == 0:
            return None, 0.0, None
        v = np.asarray(embedding, dtype=np.float32).reshape(1, -1)
        v /= (np.linalg.norm(v) + 1e-9)
        sims, ids = self.index.search(v, 1)
        sim, idx = float(sims[0][0]), int(ids[0][0])
        if sim < thresh:
            return None, sim, None
        return self.names[idx], sim, self.metas[idx]

    def save(self, prefix):
        faiss.write_index(self.index, prefix + ".faiss")
        with open(prefix + ".json", "w") as f:
            json.dump({"names": self.names, "metas": self.metas}, f)

    @classmethod
    def load(cls, prefix):
        g = cls()
        g.index = faiss.read_index(prefix + ".faiss")
        with open(prefix + ".json") as f:
            d = json.load(f)
        g.names, g.metas = d["names"], d["metas"]
        return g
