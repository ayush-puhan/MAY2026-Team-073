"""Vector Store.

Same shape as embeddings.py: a small abstraction so the rest of the
package doesn't care whether FAISS is installed. Vectors are assumed to
already be normalized (both providers in embeddings.py normalize), so
both backends use plain inner product as the similarity score.

    FaissVectorStore  - primary backend (``faiss.IndexFlatIP``).
    NumpyVectorStore   - dependency-free fallback (linear scan) - fine at
                         this corpus's scale (a handful of documents,
                         low tens of chunks), not intended for a large
                         index.

Persistence is deliberately simple: one file for vectors/index, one
sidecar JSON file for the parallel metadata list.
"""
import json
import os
import pickle
from typing import Protocol


class VectorStore(Protocol):
    name: str

    def add(self, vectors: "list[list[float]]", metadatas: "list[dict]") -> None:
        ...

    def search(self, query_vector: "list[float]", top_k: int) -> "list[tuple[dict, float]]":
        ...

    def save(self, path: str) -> None:
        ...

    def load(self, path: str) -> None:
        ...

    def __len__(self) -> int:
        ...


class NumpyVectorStore:
    """Dependency-free fallback: brute-force cosine/inner-product search."""

    name = "numpy-fallback"

    def __init__(self, dimension: int):
        import numpy as np

        self._np = np
        self.dimension = dimension
        self._vectors = np.zeros((0, dimension), dtype="float32")
        self._metadatas: "list[dict]" = []

    def add(self, vectors, metadatas) -> None:
        np = self._np
        new_vectors = np.array(vectors, dtype="float32")
        self._vectors = new_vectors if len(self) == 0 else np.vstack([self._vectors, new_vectors])
        self._metadatas.extend(metadatas)

    def search(self, query_vector, top_k: int):
        if len(self) == 0:
            return []
        np = self._np
        query = np.array(query_vector, dtype="float32")
        scores = self._vectors @ query
        top_k = min(top_k, len(self))
        top_indices = np.argsort(-scores)[:top_k]
        return [(self._metadatas[i], float(scores[i])) for i in top_indices]

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._np.save(path + ".npy", self._vectors)
        with open(path + ".meta.json", "w", encoding="utf-8") as f:
            json.dump(self._metadatas, f)

    def load(self, path: str) -> None:
        self._vectors = self._np.load(path + ".npy")
        with open(path + ".meta.json", "r", encoding="utf-8") as f:
            self._metadatas = json.load(f)

    def __len__(self) -> int:
        return self._vectors.shape[0]


class FaissVectorStore:
    """Primary backend - FAISS flat inner-product index."""

    name = "faiss"

    def __init__(self, dimension: int):
        import faiss  # optional dep

        self._faiss = faiss
        self.dimension = dimension
        self._index = faiss.IndexFlatIP(dimension)
        self._metadatas: "list[dict]" = []

    def add(self, vectors, metadatas) -> None:
        import numpy as np

        self._index.add(np.array(vectors, dtype="float32"))
        self._metadatas.extend(metadatas)

    def search(self, query_vector, top_k: int):
        if len(self) == 0:
            return []
        import numpy as np

        query = np.array([query_vector], dtype="float32")
        top_k = min(top_k, len(self))
        scores, indices = self._index.search(query, top_k)
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx == -1:
                continue
            results.append((self._metadatas[idx], float(score)))
        return results

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        self._faiss.write_index(self._index, path + ".faiss")
        with open(path + ".meta.pkl", "wb") as f:
            pickle.dump(self._metadatas, f)

    def load(self, path: str) -> None:
        self._index = self._faiss.read_index(path + ".faiss")
        with open(path + ".meta.pkl", "rb") as f:
            self._metadatas = pickle.load(f)

    def __len__(self) -> int:
        return self._index.ntotal


def get_default_vector_store(dimension: int) -> VectorStore:
    """FAISS if installed and loadable, else the NumPy fallback."""
    try:
        return FaissVectorStore(dimension)
    except Exception:
        return NumpyVectorStore(dimension)
