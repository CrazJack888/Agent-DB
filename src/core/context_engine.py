from typing import List
from src.core.models import ContextItem, Context


class ContextEngine:
    @staticmethod
    def merge(memory_items: List[ContextItem], knowledge_items: List[ContextItem], graph_items: List[ContextItem]) -> List[ContextItem]:
        merged = []
        seen = set()
        for item in memory_items + knowledge_items + graph_items:
            key = f"{item.source}:{item.content[:80]}"
            if key not in seen:
                seen.add(key)
                merged.append(item)
        return merged

    @staticmethod
    def rank(items: List[ContextItem]) -> List[ContextItem]:
        return sorted(items, key=lambda x: x.score if x.score is not None else 0.0, reverse=True)

    def build(self, query: str, memory_items: List[ContextItem], knowledge_items: List[ContextItem], graph_items: List[ContextItem]) -> Context:
        merged = self.merge(memory_items, knowledge_items, graph_items)
        ranked = self.rank(merged)
        return Context(query=query, items=ranked)
