from sqlalchemy.orm import Session
from typing import List
from uuid import UUID
from datetime import datetime
import uuid

from ..models.stake import Stake, StakeStatus, StakeType
from ..models.user import User
from ..schemas.stake import StakeCreate
from ..core.config import settings
from ..core.errors import StakeNotFoundError, InsufficientStakeError


class StakeService:
    def __init__(self, db: Session):
        self.db = db

    MIN_AMOUNTS = {
        StakeType.DM: lambda: settings.MIN_STAKE_DM_USDC,
        StakeType.JOIN_ROOM: lambda: settings.MIN_STAKE_ROOM_USDC,
        StakeType.REQUEST_MEETUP: lambda: settings.MIN_STAKE_MEETUP_USDC,
        StakeType.CONFIRM_MEETUP: lambda: settings.MIN_STAKE_MEETUP_USDC,
        StakeType.UNLOCK_PHOTO: lambda: 0.5,
    }

    def create(self, user: User, payload: StakeCreate) -> Stake:
        min_amt = self.MIN_AMOUNTS.get(payload.stake_type, lambda: 0.0)()
        if payload.amount_usdc < min_amt:
            raise InsufficientStakeError(min_amt, payload.amount_usdc)

        stake = Stake(
            id=uuid.uuid4(),
            user_id=user.id,
            stake_type=payload.stake_type,
            amount_usdc=payload.amount_usdc,
            room_id=payload.room_id,
            target_user_id=payload.target_user_id,
            tx_hash=payload.tx_hash,
            status=StakeStatus.ACTIVE,
        )
        self.db.add(stake)
        self.db.commit()
        self.db.refresh(stake)
        return stake

    def get_user_stakes(self, user_id: UUID) -> List[Stake]:
        return self.db.query(Stake).filter(Stake.user_id == user_id).all()

    def get_or_404(self, stake_id: UUID, user: User) -> Stake:
        s = self.db.query(Stake).filter(Stake.id == stake_id, Stake.user_id == user.id).first()
        if not s:
            raise StakeNotFoundError()
        return s

    def refund(self, user: User, stake_id: UUID) -> Stake:
        stake = self.get_or_404(stake_id, user)
        if stake.status not in (StakeStatus.ACTIVE, StakeStatus.PENDING):
            from fastapi import HTTPException
            raise HTTPException(400, "Stake cannot be refunded in its current state")
        stake.status = StakeStatus.REFUNDED
        stake.resolved_at = datetime.utcnow()
        # TODO: trigger Circle USDC refund
        self.db.commit()
        self.db.refresh(stake)
        return stake

    def slash(self, user: User, stake_id: UUID, reason: str) -> Stake:
        stake = self.db.query(Stake).filter(Stake.id == stake_id).first()
        if not stake:
            raise StakeNotFoundError()
        stake.status = StakeStatus.SLASHED
        stake.slash_reason = reason
        stake.resolved_at = datetime.utcnow()
        # TODO: trigger slashing policy + reputation event
        self.db.commit()
        self.db.refresh(stake)
        return stake
