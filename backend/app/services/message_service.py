from sqlalchemy.orm import Session
from uuid import UUID
import uuid

from ..models.message import Message
from ..models.match import Match, MatchStatus, ConsentState
from ..models.persona import Persona
from ..models.stake import Stake, StakeStatus
from ..models.user import User
from ..schemas.message import MessageCreate, MessageThread
from ..core.errors import MessagingBlockedError, ConsentRequiredError


class MessageService:
    def __init__(self, db: Session):
        self.db = db

    def send(self, user: User, payload: MessageCreate) -> Message:
        match = self.db.query(Match).filter(Match.id == payload.match_id).first()
        if not match:
            raise MessagingBlockedError("Match not found")

        # Enforce messaging rules
        self._check_consent(match)
        self._check_persona_validity(user, match)
        self._check_stake_if_required(payload)
        self._check_not_blocked(user.id, match)

        msg = Message(
            id=uuid.uuid4(),
            match_id=payload.match_id,
            sender_persona_id=self._get_sender_persona_id(user, match),
            type=payload.type,
            content=payload.content,
            stake_id=payload.stake_id,
        )
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def get_thread(self, user: User, match_id: UUID, skip: int = 0, limit: int = 50) -> MessageThread:
        match = self.db.query(Match).filter(Match.id == match_id).first()
        if not match:
            raise MessagingBlockedError("Match not found")
        self._check_persona_validity(user, match)

        messages = (
            self.db.query(Message)
            .filter(Message.match_id == match_id)
            .order_by(Message.created_at.asc())
            .offset(skip).limit(limit).all()
        )
        return MessageThread(messages=messages, total=len(messages), match_id=match_id)

    def _check_consent(self, match: Match):
        if match.consent_state != ConsentState.GRANTED:
            raise ConsentRequiredError()
        if match.status != MatchStatus.ACCEPTED:
            raise MessagingBlockedError("Match not accepted")

    def _check_persona_validity(self, user: User, match: Match):
        persona_ids = [
            p.id for p in self.db.query(Persona.id).filter(Persona.user_id == user.id).all()
        ]
        if match.requester_persona_id not in persona_ids and match.target_persona_id not in persona_ids:
            raise MessagingBlockedError("Not a participant in this match")

    def _check_stake_if_required(self, payload: MessageCreate):
        if payload.stake_id:
            stake = self.db.query(Stake).filter(Stake.id == payload.stake_id).first()
            if not stake or stake.status != StakeStatus.ACTIVE:
                raise MessagingBlockedError("Required stake is not active")

    def _check_not_blocked(self, user_id: UUID, match: Match):
        from ..models.block import Block
        requester = self.db.query(Persona).filter(Persona.id == match.requester_persona_id).first()
        target = self.db.query(Persona).filter(Persona.id == match.target_persona_id).first()
        if not requester or not target:
            return
        block = self.db.query(Block).filter(
            ((Block.blocker_id == requester.user_id) & (Block.blocked_id == target.user_id)) |
            ((Block.blocker_id == target.user_id) & (Block.blocked_id == requester.user_id))
        ).first()
        if block:
            raise MessagingBlockedError("User has been blocked")

    def _get_sender_persona_id(self, user: User, match: Match):
        persona = self.db.query(Persona).filter(
            Persona.user_id == user.id,
            Persona.id.in_([match.requester_persona_id, match.target_persona_id])
        ).first()
        return persona.id if persona else None
