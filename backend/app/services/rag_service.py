import json
import os
import re
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class SimpleRAGService:
    """轻量级RAG实现，无需下载嵌入模型。

    使用关键词匹配 + TF-IDF 风格的简单评分。
    """

    def __init__(self):
        self.data_file = os.path.join(settings.CHROMA_PATH, "documents.json")
        self.documents: list[dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    self.documents = json.load(f)
            except Exception:
                self.documents = []
        else:
            self.documents = []

    def _save(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, "w", encoding="utf-8") as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)

    async def search(self, query: str, top_k: int = 5, threshold: float = 0.2) -> list[dict]:
        return self.search_sync(query, top_k, threshold)

    def search_sync(self, query: str, top_k: int = 5, threshold: float = 0.2) -> list[dict]:
        if not self.documents:
            return []

        query_lower = query.lower()
        query_words = set(re.findall(r'[一-鿿]+|[a-zA-Z0-9]+', query_lower))

        scored = []
        for doc in self.documents:
            content = doc.get("content", "")
            content_lower = content.lower()

            # 计算关键词匹配分数
            score = 0
            for word in query_words:
                if word in content_lower:
                    score += 1
                # 部分匹配
                if len(word) > 2:
                    for i in range(len(word) - 1):
                        if word[i:i + 2] in content_lower:
                            score += 0.3

            # 标题额外加分
            title = doc.get("metadata", {}).get("title", "")
            for word in query_words:
                if word in title.lower():
                    score += 2

            # 归一化
            if query_words:
                score = score / len(query_words)

            if score >= threshold:
                scored.append({
                    "id": doc["id"],
                    "content": content,
                    "metadata": doc.get("metadata", {}),
                    "similarity": round(min(score / 5, 1.0), 4),
                })

        scored.sort(key=lambda x: x["similarity"], reverse=True)
        return scored[:top_k]

    def add_document(self, doc_id: str, content: str, metadata: dict = None):
        # 检查是否已存在
        for i, doc in enumerate(self.documents):
            if doc["id"] == doc_id:
                self.documents[i] = {"id": doc_id, "content": content, "metadata": metadata or {}}
                self._save()
                return
        self.documents.append({"id": doc_id, "content": content, "metadata": metadata or {}})
        self._save()

    def delete_document(self, doc_id: str):
        self.documents = [d for d in self.documents if d["id"] != doc_id]
        self._save()

    def count(self) -> int:
        return len(self.documents)


# 全局实例
_rag_instance: Optional[SimpleRAGService] = None


def get_rag() -> SimpleRAGService:
    global _rag_instance
    if _rag_instance is None:
        _rag_instance = SimpleRAGService()
    return _rag_instance


# 向后兼容别名
RAGService = SimpleRAGService
