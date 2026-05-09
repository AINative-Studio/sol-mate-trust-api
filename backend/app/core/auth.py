from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import uuid
import httpx

from .config import settings
from .database import get_db
from ..models.user import User

security = HTTPBearer(auto_error=False)

# AINative platform API key prefixes (all supported formats)
AINATIVE_KEY_PREFIXES = ("sk_", "svc_", "agk_", "pa_", "tmp_")


def is_ainative_api_key(token: str) -> bool:
    """Detect AINative platform API keys by prefix and length heuristic."""
    return len(token) < 100 and token.startswith(AINATIVE_KEY_PREFIXES)


async def _validate_ainative_key(api_key: str) -> Optional[dict]:
    """Validate an AINative API key against the platform and return user context."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                f"{settings.AINATIVE_API_URL}/api/v1/auth/me",
                headers={"X-API-Key": api_key},
            )
        if resp.status_code == 200:
            return resp.json()
    except httpx.RequestError:
        pass
    return None


def _get_or_create_platform_user(platform_user: dict, db: Session) -> User:
    """Get or create a Sol Mate user from AINative platform identity."""
    platform_id = str(platform_user.get("id", ""))
    email = platform_user.get("email", "")

    # Look up by a stable platform identifier stored in wallet_address field
    # We use "ainative:{platform_id}" as a synthetic wallet address for platform users
    synthetic_wallet = f"ainative:{platform_id}"

    user = db.query(User).filter(User.wallet_address == synthetic_wallet).first()
    if not user:
        user = User(
            id=uuid.uuid4(),
            wallet_address=synthetic_wallet,
            email=email or None,
            is_active=True,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def create_access_token(user_id: str, wallet_address: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user_id,
        "wallet": wallet_address,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    # --- AINative API key auth (X-API-Key header or Bearer with key prefix) ---
    api_key = request.headers.get("X-API-Key")
    if not api_key and credentials and is_ainative_api_key(credentials.credentials):
        api_key = credentials.credentials

    if api_key and is_ainative_api_key(api_key):
        platform_user = await _validate_ainative_key(api_key)
        if not platform_user:
            raise HTTPException(status_code=401, detail="Invalid AINative API key")
        return _get_or_create_platform_user(platform_user, db)

    # --- Wallet-signature JWT auth (existing flow) ---
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    user = db.query(User).filter(User.id == uuid.UUID(user_id), User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user
