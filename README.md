# Sol Mate Trust API

**Social trust backend for stake-to-interact, AI matchmaking, meetup attestations, and safety escrow on Solana.**

Built for the EasyA × Consensus Miami Hackathon 2026.

## Architecture

Sol Mate is a **new domain layer** on top of Agent-402 infrastructure primitives (ZeroDB, Hedera HCS, Circle USDC, X402).

```
backend/app/
  api/          ← FastAPI route handlers
  models/       ← SQLAlchemy ORM models
  schemas/      ← Pydantic request/response schemas
  services/     ← Business logic
  core/         ← Config, auth, DB, errors
```

## Sprint Plan

| Sprint | Scope | Acceptance |
|--------|-------|------------|
| 1 | User, Persona, Room | Wallet auth → persona → room join |
| 2 | Stake, Escrow | Stake USDC → DM or meetup |
| 3 | Match, Message | Consent + stake gated messaging |
| 4 | Attestation, Reputation | Meetup proof updates escrow + score |
| 5 | AI Match Agent | AI suggests compatible matches |
| 6 | Safety, Audit | Reports/disputes replayable on HCS |

## Quick Start

```bash
cp .env.example .env
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Run Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```
