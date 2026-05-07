from pydantic_settings import BaseSettings
from typing import List, Optional
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Sol Mate Trust API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    ENVIRONMENT: str = "development"

    # Database
    DATABASE_URL: str = "postgresql://solmate:solmate@localhost:5432/solmate"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10

    # Auth
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Solana
    SOLANA_RPC_URL: str = "https://api.devnet.solana.com"
    SOLANA_NETWORK: str = "devnet"
    SOLANA_PROGRAM_ID: str = "GihCjDJeAwbNtr826dEAfQFp4GAVBgHWLxDf2sqsQLif"
    SOLANA_KEYPAIR_PATH: str = "~/.config/solana/id.json"

    # Circle (USDC payments / escrow)
    CIRCLE_API_KEY: Optional[str] = None
    CIRCLE_WALLET_SET_ID: Optional[str] = None
    CIRCLE_BASE_URL: str = "https://api-sandbox.circle.com"

    # Hedera (HCS anchoring + reputation)
    HEDERA_ACCOUNT_ID: Optional[str] = None
    HEDERA_PRIVATE_KEY: Optional[str] = None
    HEDERA_NETWORK: str = "testnet"

    # ZeroDB (memory + vectors)
    ZERODB_API_URL: str = "https://api.ainative.studio"
    ZERODB_PROJECT_ID: Optional[str] = None
    ZERODB_USERNAME: Optional[str] = None
    ZERODB_PASSWORD: Optional[str] = None

    # AI / LLM
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None

    # Coinbase x402 payment protocol (Base)
    X402_ENABLED: bool = False
    COINBASE_PAYMENT_ADDRESS: str = ""

    # Safety
    MIN_STAKE_DM_USDC: float = 1.0
    MIN_STAKE_MEETUP_USDC: float = 5.0
    MIN_STAKE_ROOM_USDC: float = 0.5
    SLASH_AMOUNT_NO_SHOW: float = 5.0

    # CORS
    ALLOWED_ORIGINS: List[str] = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
