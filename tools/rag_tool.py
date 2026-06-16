from typing import List, Dict, Any, Optional
from config.settings import Settings


class RAGRetrieverTool:
    """基于ChromaDB的RAG检索工具，支持文档索引和语义检索。"""

    def __init__(self, settings: Optional[Settings] = None):
        self.settings = settings or Settings()
        self._client = None
        self._collection = None
        self._embedding_model = None
        self._ready = False

    def _init_once(self):
        if self._ready:
            return True
        try:
            import chromadb
            from sentence_transformers import SentenceTransformer
            self._client = chromadb.PersistentClient(path=self.settings.chroma_persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.settings.chroma_collection,
                metadata={"hnsw:space": "cosine"}
            )
            self._embedding_model = SentenceTransformer(self.settings.embedding_model)
            self._ready = True
            return True
        except Exception as e:
            print(f"RAG init failed: {e}")
            return False

    def _embed(self, texts: List[str]) -> List[List[float]]:
        return self._embedding_model.encode(texts).tolist()

    def index_documents(self, documents: List[Dict[str, str]]) -> int:
        if not self._init_once():
            return 0
        ids = [doc["id"] for doc in documents]
        contents = [doc["content"] for doc in documents]
        metadatas = [doc.get("metadata", {}) for doc in documents]
        embeddings = self._embed(contents)

        batch_size = 100
        for i in range(0, len(ids), batch_size):
            self._collection.upsert(
                ids=ids[i:i+batch_size],
                documents=contents[i:i+batch_size],
                embeddings=embeddings[i:i+batch_size],
                metadatas=metadatas[i:i+batch_size],
            )
        return len(ids)

    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if not self._init_once():
            return []
        q_emb = self._embed([query])
        results = self._collection.query(
            query_embeddings=q_emb,
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )
        docs = []
        for i in range(len(results["ids"][0])):
            docs.append({
                "id": results["ids"][0][i],
                "content": results["documents"][0][i],
                "metadata": results["metadatas"][0][i],
                "score": 1 - results["distances"][0][i],
            })
        return docs

    def build_context(self, query: str, top_k: int = 5) -> str:
        results = self.search(query, top_k)
        if not results:
            return "[知识库中未找到相关信息]"
        parts = []
        for i, r in enumerate(results):
            source = r["metadata"].get("source", "unknown")
            parts.append(f"[来源{i+1}: {source} | 相关度: {r['score']:.3f}]\n{r['content']}")
        return "\n\n---\n\n".join(parts)

    def stats(self) -> Dict[str, int]:
        if not self._init_once():
            return {"collection": self.settings.chroma_collection, "count": 0}
        return {"collection": self.settings.chroma_collection, "count": self._collection.count()}
