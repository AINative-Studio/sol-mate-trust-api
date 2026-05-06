from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional, List, Dict, Any
import uuid

from ..models.persona import Persona
from ..models.user import User
from ..models.reputation import ReputationScore


class MatchmakingService:
    def __init__(self, db: Session):
        self.db = db
        # Preference store backed by ZeroDB in production
        self._prefs: Dict[str, Dict] = {}

    def update_preferences(self, user: User, prefs: Dict[str, Any]) -> dict:
        self._prefs[str(user.id)] = prefs
        # TODO: store in ZeroDB vector store for semantic matching
        return {"status": "preferences_saved", "user_id": str(user.id)}

    def get_suggestions(
        self, user: User, room_id: Optional[UUID] = None, limit: int = 10
    ) -> List[dict]:
        user_prefs = self._prefs.get(str(user.id), {})

        # Get candidate personas (same room or public)
        q = self.db.query(Persona).filter(Persona.is_active == True, Persona.user_id != user.id)
        if room_id:
            q = q.filter(Persona.room_id == room_id)
        candidates = q.limit(100).all()

        suggestions = []
        for persona in candidates:
            score = self._score_compatibility(user, persona, user_prefs)
            if score > 0.3:
                suggestions.append({
                    "persona_id": persona.id,
                    "compatibility_score": round(score, 3),
                    "intro_suggestion": self._generate_intro_text(user, persona),
                    "shared_interests": [],
                    "room_context": str(room_id) if room_id else None,
                })

        suggestions.sort(key=lambda x: x["compatibility_score"], reverse=True)
        return suggestions[:limit]

    def generate_intro(self, user: User, target_persona_id: UUID, context: Optional[str]) -> dict:
        target = self.db.query(Persona).filter(Persona.id == target_persona_id).first()
        if not target:
            from fastapi import HTTPException
            raise HTTPException(404, "Target persona not found")
        intro = self._generate_intro_text(user, target, context)
        return {"intro": intro, "target_persona_id": str(target_persona_id)}

    def apply_vibe_filter(self, user: User, filters: Dict[str, Any]) -> dict:
        # TODO: integrate with ZeroDB semantic search for vibe matching
        return {"status": "filter_applied", "filters": filters}

    def _score_compatibility(self, user: User, persona: Persona, prefs: Dict) -> float:
        score = 0.5  # base

        # Intent mode match
        intent_mode = prefs.get("intent_mode")
        if intent_mode and persona.intent_mode.value == intent_mode:
            score += 0.2

        # Reputation trust score
        rep = self.db.query(ReputationScore).filter(ReputationScore.user_id == persona.user_id).first()
        if rep:
            score += (rep.composite_score / 100) * 0.3

        return min(1.0, score)

    def _generate_intro_text(self, user: User, persona: Persona, context: Optional[str] = None) -> str:
        # TODO: replace with LLM call using user prefs + persona bio
        return f"Hi {persona.display_name}! Looks like we might vibe well together."
