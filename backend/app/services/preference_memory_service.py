"""
Preference Memory Service — stores and retrieves user preferences,
computes bag-of-words keyword embeddings, and provides cosine similarity.
No external API needed: pure Python + numpy for hackathon use.
"""
from __future__ import annotations

import math
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models.match_agent import UserPreferences


# Shared vocabulary of keywords that span interests + personality_traits.
# Intentionally broad so ad-hoc terms still produce non-zero overlap.
_VOCAB: list[str] = [
    # interests
    "music", "travel", "hiking", "cooking", "gaming", "art", "sports",
    "fitness", "reading", "photography", "yoga", "dancing", "coffee",
    "tech", "science", "nature", "movies", "anime", "food", "fashion",
    "startup", "crypto", "blockchain", "defi", "solana",
    # personality traits
    "adventurous", "creative", "ambitious", "empathetic", "humorous",
    "introverted", "extroverted", "caring", "intellectual", "spiritual",
    "optimistic", "spontaneous", "reliable", "passionate", "laid_back",
    "social", "independent", "romantic", "playful", "serious",
]
_VOCAB_INDEX: dict[str, int] = {w: i for i, w in enumerate(_VOCAB)}


def _normalise(vec: list[float]) -> list[float]:
    mag = math.sqrt(sum(x * x for x in vec))
    if mag == 0.0:
        return vec
    return [x / mag for x in vec]


class PreferenceMemoryService:
    def __init__(self, db: Session):
        self.db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def store(self, user_id: UUID, prefs: dict) -> UserPreferences:
        """Upsert user preferences and recompute the embedding vector."""
        embedding = self.compute_embedding(prefs)

        existing = self.db.query(UserPreferences).filter(
            UserPreferences.user_id == user_id
        ).first()

        if existing:
            existing.intent_mode = prefs.get("intent_mode", existing.intent_mode)
            age = prefs.get("age_range", {})
            if age:
                existing.age_range_min = age.get("min", existing.age_range_min)
                existing.age_range_max = age.get("max", existing.age_range_max)
            if "interests" in prefs:
                existing.interests = prefs["interests"]
            if "dealbreakers" in prefs:
                existing.dealbreakers = prefs["dealbreakers"]
            if "location_range_km" in prefs:
                existing.location_range_km = prefs["location_range_km"]
            if "personality_traits" in prefs:
                existing.personality_traits = prefs["personality_traits"]
            existing.embedding_vector = embedding
            self.db.commit()
            self.db.refresh(existing)
            return existing

        age = prefs.get("age_range", {})
        record = UserPreferences(
            user_id=user_id,
            intent_mode=prefs.get("intent_mode"),
            age_range_min=age.get("min") if age else None,
            age_range_max=age.get("max") if age else None,
            interests=prefs.get("interests"),
            dealbreakers=prefs.get("dealbreakers"),
            location_range_km=prefs.get("location_range_km"),
            personality_traits=prefs.get("personality_traits"),
            embedding_vector=embedding,
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get(self, user_id: UUID) -> Optional[UserPreferences]:
        return (
            self.db.query(UserPreferences)
            .filter(UserPreferences.user_id == user_id)
            .first()
        )

    def compute_embedding(self, prefs: dict) -> list[float]:
        """
        Build a normalised bag-of-words vector from interests + personality_traits.
        Terms outside the fixed vocabulary are ignored (hackathon simplification).
        """
        vec = [0.0] * len(_VOCAB)

        for term in prefs.get("interests", []) or []:
            key = term.lower().replace(" ", "_")
            if key in _VOCAB_INDEX:
                vec[_VOCAB_INDEX[key]] += 1.0

        for term in prefs.get("personality_traits", []) or []:
            key = term.lower().replace(" ", "_")
            if key in _VOCAB_INDEX:
                vec[_VOCAB_INDEX[key]] += 1.0

        return _normalise(vec)

    @staticmethod
    def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
        """Return cosine similarity in [0, 1] between two pre-normalised vectors."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        # Clamp to [0, 1] — vectors are normalised so magnitude is ~1
        return max(0.0, min(1.0, dot))
