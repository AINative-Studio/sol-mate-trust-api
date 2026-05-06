# Sol Mate — Trust-Based Social App on Solana

**Sol Mate is a stake-to-interact social app where skin-in-the-game replaces swipe culture.**

Users stake USDC to enter rooms, request matches, and unlock DMs. Genuine meetups release the stake back. No-shows and harassment get slashed. An AI match agent surfaces compatible people. Every safety decision is anchored on Hedera HCS for immutable auditability.

Built for the **EasyA × Consensus Miami Hackathon 2026**.

---

## The Problem

Dating and social apps have zero cost for bad behavior — ghosting, harassment, and fake profiles are free. Reputation scores are siloed and forgettable. There's no skin in the game.

## The Solution

Sol Mate introduces **economic accountability** into social interactions:

- **Stake to interact** — put up USDC to enter a room or DM someone. It comes back if you show up.
- **Slash bad actors** — no-shows lose 50%, harassment loses 100% of their stake.
- **AI matchmaking** — vector-based compatibility scoring finds real chemistry, not just swipes.
- **Meetup attestation** — both parties confirm the meeting via GPS or QR code, triggering stake release and reputation boost.
- **Immutable audit trail** — every safety action is anchored on Hedera HCS.

---

## Features

### Wallet Identity
- Solana Ed25519 wallet auth — challenge/nonce → signature verification (supports Phantom, Solflare)
- JWT session tokens
- Verification levels: wallet → phone → ID → full KYC
- Privacy modes: public / semi-private / private

### Personas
- Multiple personas per wallet (anonymous or named)
- Intent modes: `social`, `dating`, `networking`, `friendship`
- Room-scoped — persona is attached to a specific room

### Rooms
- Types: `lounge`, `topic`, `event`, `private`
- Stake-gated entry: rooms can require USDC stake to join
- Location-aware: GPS coordinates + haversine distance discovery
- Intent-mode filtering: only see rooms that match your vibe

### Stake-to-Interact
- Stake USDC on-chain (Solana Anchor program) to enter a room or initiate a match
- Escrow held in PDA-controlled vault keyed by `(staker, room_id)`
- Three stake types: `room_entry`, `match_request`, `dm_unlock`
- Auto-slash: Celery worker evaluates no-shows hourly

### Safety Escrow (Slashing Policy)
| Violation | Slash % |
|-----------|---------|
| No-show (1st) | 50% |
| No-show (repeat) | 100% |
| Harassment confirmed | 100% |
| False report filed | 25% (reporter slashed) |

- Repeat no-shows (3+) → DM sending suspended
- Stake multiplier: each no-show increases required stake by 0.5×, max 3×

### AI Match Agent
- **Preference memory** — stores interests, personality traits, intent mode, age range
- **Bag-of-words embedding** — 45-term vocabulary, L2-normalised, pure Python (no numpy)
- **5-dimension compatibility scoring:**

| Dimension | Weight |
|-----------|--------|
| Preference similarity | 35% |
| Intent mode match | 20% |
| Reputation trust score | 20% |
| Room context match | 15% |
| Behavioral safety score | 10% |

- **Vibe filter** — exclude reported users, filter by intent mode
- **AI intro generator** — personalized opening message based on shared interests

### Meetup Attestations
- Both parties submit GPS coordinates after meeting
- Proximity verified within 100m (haversine)
- Alternative: BLE token (2-min TTL) or QR code (5-min TTL)
- Confirmed attestation → stake refunded + reputation boosted
- Anchored on Hedera HCS for immutable proof

### Reputation Engine
- 5 dimensions: reliability, safety, response rate, meetup completion, consent confirmation
- Composite score with weighted formula
- Time-based decay: −1 pt/week per dimension for inactivity
- Event-driven updates: meetup completed (+5), no-show (−15), report received (−10), stake slashed (−20)

### Safety & Moderation
- Report categories: harassment, fake profile, underage, spam, no-show, scam
- Auto-actions: underage reports → immediate account deactivation
- Repeat offender detection (3+ reports)
- Bidirectional block system
- Moderation queue with severity levels
- All resolved reports update the offender's reputation

### Matching & Messaging
- Consent-gated: both parties must accept before messages flow
- Stake-gated: DM channel requires active stake
- Match states: `pending` → `accepted` → `active` → `completed` / `expired`
- Interaction policy enforcement: block checks, persona-in-room checks

---

## Architecture

```
backend/app/
  api/          ← FastAPI route handlers (rooms, matches, stakes, safety, reputation…)
  models/       ← SQLAlchemy ORM (User, Persona, Room, Stake, Match, Message, Attestation…)
  schemas/      ← Pydantic v2 request/response schemas
  services/     ← Business logic (24 service classes)
  core/         ← Config, JWT auth, DB pool, domain errors
  tasks/        ← Celery workers (escrow auto-slash, match expiry, reputation decay)

solana/
  programs/sol-mate-escrow/   ← Anchor program (stake/refund/slash)
  tests/                      ← TypeScript integration tests
  scripts/deploy_devnet.sh    ← One-command devnet deploy
```

**Infrastructure primitives** (via Agent-402):
- **Circle USDC** — escrow funding and release
- **Hedera HCS** — immutable audit log for attestations and safety decisions
- **ZeroDB** — vector memory for AI preference matching
- **X402** — HTTP payment protocol for stake transactions

---

## Quick Start

```bash
# Clone and configure
git clone https://github.com/AINative-Studio/sol-mate-trust-api
cd sol-mate-trust-api
cp .env.example .env  # fill in DATABASE_URL, SECRET_KEY, SOLANA_RPC_URL

# Install and run
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
# → API docs at http://localhost:8000/docs
```

### Docker (full stack)

```bash
cd backend
docker-compose up
# Starts: API, Postgres, Redis, Celery worker, Celery beat
```

### Run Demo Seed

```bash
python3 scripts/demo_seed.py --base-url http://localhost:8000
# Seeds 4 users, 3 rooms, a match, messages, attestation, and a harassment report
```

---

## Deploy Solana Program to Devnet

```bash
# Install Solana toolchain
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
cargo install --git https://github.com/coral-xyz/anchor anchor-cli --locked

# Deploy
cd solana
bash scripts/deploy_devnet.sh
```

---

## Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

**182 tests, 87% coverage.**

| Area | Tests | Coverage |
|------|-------|----------|
| Models & Schemas | — | 100% |
| User / Wallet Auth | 25 | 81% |
| Rooms | 9 | 97% |
| Stakes & Escrow | 19 | 93% |
| Matching & Messaging | 15 | 85% |
| Attestations & Reputation | 10 | 85% |
| AI Match Agent | 8 | 91% |
| Safety & Moderation | 23 | 100% |
| Proximity Verification | 16 | 100% |
| Room Discovery | 14 | 97% |
| Preference Memory | 16 | 97% |
| Reputation Decay | 14 | 100% |
| Infra / Health | 11 | 96% |

---

## Hackathon Tracks

| Track | Prize | Our Angle |
|-------|-------|-----------|
| **Solana** | $30k $SKR | On-chain stake/escrow Anchor program; Ed25519 wallet auth |
| **Coinbase + AWS** | $5k + $40k AWS | Circle USDC escrow; X402 stake transactions |

---

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | Postgres connection string |
| `SECRET_KEY` | JWT signing secret |
| `SOLANA_RPC_URL` | Solana RPC (devnet: `https://api.devnet.solana.com`) |
| `SOLANA_PROGRAM_ID` | Deployed escrow program ID |
| `CIRCLE_API_KEY` | Circle USDC API key |
| `HEDERA_ACCOUNT_ID` | Hedera operator account |
| `HEDERA_PRIVATE_KEY` | Hedera operator private key |
| `ZERODB_API_KEY` | ZeroDB vector memory API key |
| `MIN_STAKE_ROOM_ENTRY` | Minimum stake for room entry (default: 1.0 USDC) |
| `MIN_STAKE_MATCH_REQUEST` | Minimum stake for match request (default: 2.0 USDC) |
| `MIN_STAKE_DM_UNLOCK` | Minimum stake for DM unlock (default: 0.5 USDC) |
