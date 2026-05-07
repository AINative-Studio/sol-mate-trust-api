# Sol Mate — Trust-Based Social App on Solana

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-324%20passing-brightgreen)](backend/tests/)
[![Coverage](https://img.shields.io/badge/coverage-94%25-brightgreen)](backend/)
[![Deployed](https://img.shields.io/badge/API-live%20on%20Railway-blue)](https://sol-mate-trust-api-production.up.railway.app/health)

> **Submission description (≤300 chars):** Sol Mate — stake USDC to DM, match, and meet. No-shows and harassment get slashed on Solana. AI matchmaking, GPS attestation, HCS audit trail, and Coinbase x402 payments. Skin in the game replaces swipe culture.

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

## Solana Program — Live on Devnet

**Program ID:** `GihCjDJeAwbNtr826dEAfQFp4GAVBgHWLxDf2sqsQLif`

**Deploy tx:** [`2UtFRJPh...`](https://explorer.solana.com/tx/2UtFRJPhLfn2BHn2A7PMo3CzYKSfyhHo5iV4FjUu96ArbporeDPJ6oUsQKXE4abF8q7JGr2iHD4LWcsjA2dJN5gJ?cluster=devnet)

The Anchor escrow program is deployed and verified on Solana devnet. Every stake, refund, and slash from the API submits a transaction to this program and returns an Explorer link.

```bash
# Re-deploy (if needed)
cd solana
anchor deploy --provider.cluster devnet
```

---

## Open Source Strategy

Sol Mate is MIT licensed and built to be reused. The three primitives at its core are being extracted as standalone packages for the Solana/Web3 ecosystem:

| Package | What it does | Planned registry |
|---------|-------------|-----------------|
| **`solmate-stake-sdk`** | Stake-gated access control — any Solana dApp can require a USDC stake before a DM, room entry, or action | PyPI + npm |
| **`solmate-reputation`** | On-chain reputation decay with Hedera HCS audit anchoring — portable trust scoring for social dApps | PyPI |
| **`x402-solana`** | FastAPI middleware bridging Solana stake mechanics with Coinbase x402 HTTP payments on Base — novel cross-chain primitive | PyPI |

These packages are planned for extraction post-hackathon. The full protocol design and interfaces are already implemented in this repo — see `backend/app/services/solana_service.py`, `backend/app/services/social_reputation_service.py`, and `backend/app/middleware/x402_payment.py`.

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get involved.

---

## Tests

```bash
cd backend
pytest tests/ -v --cov=app --cov-report=term-missing
```

**324 tests, 94% coverage.**

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
| **Coinbase + AWS** | $10k + $80k AWS | Coinbase x402 payment middleware on Base; Circle USDC escrow |

---

## Integrations

### Coinbase x402 — HTTP Payment Protocol (Base)

Sol Mate implements the [x402 HTTP payment protocol](https://x402.org) on Base mainnet for DM unlock staking. This qualifies for the **Agentic track** ($10K + $80K AWS).

**How it works:**

```
Client → POST /api/v1/stakes (stake_type=dm, no payment)
Server → 402 Payment Required + payment requirements (Base USDC)
Client → pays 0.5 USDC on Base via Coinbase facilitator
Client → POST /api/v1/stakes (X-Payment: <proof>)
Server → verifies proof via https://x402.org/facilitator/verify
Server → 201 Created (stake unlocked)
```

**Payment details:**
- Network: Base mainnet
- Asset: USDC (`0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`)
- Amount: 0.5 USDC (500,000 micro-units, 6 decimals)
- Facilitator: Coinbase public facilitator (`https://x402.org/facilitator`)

**Enable in `.env`:**

```env
X402_ENABLED=true
COINBASE_PAYMENT_ADDRESS=0xYourBaseWalletAddress
```

**Disabled by default** — all existing tests pass without any x402 configuration. When the facilitator is unreachable, requests are allowed through (graceful degradation).

**Implementation:**
- Middleware: `backend/app/middleware/x402_payment.py`
- Dependency: `require_x402_payment` (called inline for `stake_type=dm` only)
- Package: `x402[fastapi]==2.9.0`

---

## Running Locally — API Keys Setup

Sol Mate is designed to run without external API keys in development. All third-party integrations (Circle, Hedera, ZeroDB) **gracefully no-op** when credentials are missing — the API still starts and all tests pass.

### Minimum setup (no external services)

```bash
cp .env.example .env
```

Edit `.env` with just these two required values:

```env
# Required — always
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/solmate
SECRET_KEY=any-random-string-at-least-32-chars

# Optional — app starts fine without these
```

That's it. Wallet auth, rooms, matching, AI scoring, and all 198 tests work without any third-party keys.

---

### Optional integrations

Each integration below adds a real capability. Skip any you don't need.

#### Solana (on-chain stake/escrow)
Get a devnet keypair at https://solana.com/developers

```env
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_PROGRAM_ID=<from: cd solana && bash scripts/deploy_devnet.sh>
```

#### Circle USDC (real money movement)
Sign up at https://developer.circle.com — use the sandbox for free testing.

```env
CIRCLE_API_KEY=TEST_API_KEY:...          # from circle.com/developers
CIRCLE_ENVIRONMENT=sandbox               # or "production"
CIRCLE_ESCROW_WALLET_ID=<wallet-id>      # your Circle escrow wallet
CIRCLE_SAFETY_FUND_WALLET_ID=<wallet-id> # your Circle safety fund wallet
```

> Without these, stake create/refund/slash still work — Circle calls log a debug message and return a `stub` result.

#### Hedera HCS (immutable audit trail)
Sign up at https://portal.hedera.com — testnet accounts are free.

```env
HEDERA_ACCOUNT_ID=0.0.XXXXXX
HEDERA_PRIVATE_KEY=302e...               # ED25519 private key from portal
HEDERA_TOPIC_ID=0.0.XXXXXX              # create via: hedera topic create
HEDERA_NETWORK=testnet                  # or "mainnet"
```

> Without these, attestation anchoring and safety audit calls are silently skipped. The `hcs_message_id` field stays null on attestations.

#### ZeroDB (vector memory for AI matching)
Get a free API key at https://ainative.studio

```env
ZERODB_API_KEY=<your-key>
ZERODB_PROJECT_ID=<your-project-id>
ZERODB_API_URL=https://api.ainative.studio  # default
```

> Without these, preference embeddings are stored only in Postgres (the built-in bag-of-words scoring still works). Semantic search across all users won't be available.

#### OpenAI (enhanced intro generation)
```env
OPENAI_API_KEY=sk-...
```

> Without this, the AI intro generator uses the built-in template engine.

---

### Full `.env` reference

```env
# ── Required ──────────────────────────────────────────────────────────────────
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/solmate
SECRET_KEY=change-me-to-a-long-random-secret

# ── Solana ────────────────────────────────────────────────────────────────────
SOLANA_RPC_URL=https://api.devnet.solana.com
SOLANA_PROGRAM_ID=

# ── Circle USDC ───────────────────────────────────────────────────────────────
CIRCLE_API_KEY=
CIRCLE_ENVIRONMENT=sandbox
CIRCLE_ESCROW_WALLET_ID=
CIRCLE_SAFETY_FUND_WALLET_ID=

# ── Hedera HCS ────────────────────────────────────────────────────────────────
HEDERA_ACCOUNT_ID=
HEDERA_PRIVATE_KEY=
HEDERA_TOPIC_ID=
HEDERA_NETWORK=testnet

# ── ZeroDB ────────────────────────────────────────────────────────────────────
ZERODB_API_KEY=
ZERODB_PROJECT_ID=
ZERODB_API_URL=https://api.ainative.studio

# ── OpenAI (optional) ─────────────────────────────────────────────────────────
OPENAI_API_KEY=

# ── Stake thresholds (USDC) ───────────────────────────────────────────────────
MIN_STAKE_ROOM_USDC=1.0
MIN_STAKE_MEETUP_USDC=2.0
MIN_STAKE_DM_USDC=0.5

# ── Celery / Redis (for background workers) ───────────────────────────────────
REDIS_URL=redis://localhost:6379/0
```

---

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | **Yes** | Postgres connection string |
| `SECRET_KEY` | **Yes** | JWT signing secret (32+ chars) |
| `SOLANA_RPC_URL` | No | Solana RPC endpoint |
| `SOLANA_PROGRAM_ID` | No | Deployed escrow program address |
| `CIRCLE_API_KEY` | No | Circle USDC API key (sandbox or prod) |
| `CIRCLE_ENVIRONMENT` | No | `sandbox` or `production` (default: sandbox) |
| `CIRCLE_ESCROW_WALLET_ID` | No | Circle wallet ID for escrow holds |
| `CIRCLE_SAFETY_FUND_WALLET_ID` | No | Circle wallet ID for slashed funds |
| `HEDERA_ACCOUNT_ID` | No | Hedera operator account (e.g. `0.0.12345`) |
| `HEDERA_PRIVATE_KEY` | No | Hedera ED25519 private key |
| `HEDERA_TOPIC_ID` | No | HCS topic ID for audit logs |
| `HEDERA_NETWORK` | No | `testnet` or `mainnet` (default: testnet) |
| `ZERODB_API_KEY` | No | ZeroDB vector memory API key |
| `ZERODB_PROJECT_ID` | No | ZeroDB project identifier |
| `ZERODB_API_URL` | No | ZeroDB base URL (default: `https://api.ainative.studio`) |
| `OPENAI_API_KEY` | No | OpenAI key for enhanced intro generation |
| `REDIS_URL` | No | Redis URL for Celery workers (default: `redis://localhost:6379/0`) |
| `MIN_STAKE_ROOM_USDC` | No | Min USDC stake for room entry (default: 1.0) |
| `MIN_STAKE_MEETUP_USDC` | No | Min USDC stake for meetup request (default: 2.0) |
| `MIN_STAKE_DM_USDC` | No | Min USDC stake to unlock DMs (default: 0.5) |
| `X402_ENABLED` | No | Enable Coinbase x402 payment gate on DM unlock (default: false) |
| `COINBASE_PAYMENT_ADDRESS` | No | Base wallet address to receive x402 USDC payments |
