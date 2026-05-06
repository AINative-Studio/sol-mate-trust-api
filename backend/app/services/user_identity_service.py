from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import secrets
import uuid

from ..models.user import User
from ..schemas.user import UserOnboard, UserResponse, UserUpdate, WalletAuthChallenge, WalletAuthToken
from ..core.auth import create_access_token
from ..core.errors import UserNotFoundError


# In-memory nonce store (replace with Redis in production)
_nonce_store: dict = {}


class UserIdentityService:
    def __init__(self, db: Session):
        self.db = db

    def create_challenge(self, wallet_address: str) -> WalletAuthChallenge:
        nonce = secrets.token_hex(32)
        expires_at = datetime.utcnow() + timedelta(minutes=5)
        _nonce_store[wallet_address] = {"nonce": nonce, "expires_at": expires_at}
        return WalletAuthChallenge(nonce=nonce, expires_at=expires_at)

    def onboard(self, payload: UserOnboard) -> WalletAuthToken:
        # Verify nonce
        stored = _nonce_store.get(payload.wallet_address)
        if not stored or stored["nonce"] != payload.nonce:
            from fastapi import HTTPException
            raise HTTPException(status_code=401, detail="Invalid or expired nonce")
        if stored["expires_at"] < datetime.utcnow():
            raise HTTPException(status_code=401, detail="Nonce expired")

        # TODO: verify Solana signature (payload.signature)
        # solana.verify_signature(payload.wallet_address, payload.nonce, payload.signature)

        # Upsert user
        user = self.db.query(User).filter(User.wallet_address == payload.wallet_address).first()
        if not user:
            user = User(
                id=uuid.uuid4(),
                wallet_address=payload.wallet_address,
                email=payload.email,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)

        # Clear nonce
        _nonce_store.pop(payload.wallet_address, None)

        token = create_access_token(str(user.id), user.wallet_address)
        return WalletAuthToken(access_token=token, user=UserResponse.model_validate(user))

    def update_user(self, user: User, payload: UserUpdate) -> User:
        if payload.email is not None:
            user.email = payload.email
        if payload.privacy_mode is not None:
            user.privacy_mode = payload.privacy_mode
        user.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(user)
        return user
