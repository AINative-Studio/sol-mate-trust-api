# Contributing to Sol Mate

Sol Mate is open source under the MIT license. We welcome contributions to the core protocol, SDKs, and tooling.

## What We're Building

Sol Mate introduces **economic accountability** to social interactions on Solana. The reusable primitives we're extracting:

| Package | Description | Status |
|---------|-------------|--------|
| `solmate-stake-sdk` | Stake-gated access control for Solana dApps | Planned |
| `solmate-reputation` | On-chain reputation decay + HCS audit trail | Planned |
| `x402-solana` | x402 FastAPI middleware bridging Solana + Coinbase Base | Planned |

## Getting Started

```bash
git clone https://github.com/AINative-Studio/sol-mate-trust-api
cd sol-mate-trust-api/backend
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest tests/ -v
```

## Project Structure

```
backend/          FastAPI backend (Python)
  app/
    api/          HTTP route handlers
    services/     Business logic
    models/       SQLAlchemy ORM models
    tasks/        Celery beat tasks
solana/           Anchor escrow program (Rust)
  programs/
    sol-mate-escrow/src/lib.rs
scripts/          Demo seed + deployment scripts
docs/             Postman collection
```

## How to Contribute

1. Fork the repo and create a branch: `feature/your-feature` or `fix/issue-number`
2. Write tests — we maintain 94%+ coverage
3. Open a PR referencing the issue: `Closes #N`
4. All PRs require passing CI

## Areas We Need Help

- **Solana program tests** — TypeScript Anchor tests in `solana/tests/`
- **Mobile SDK** — React Native wallet integration
- **x402 TypeScript client** — browser-side payment flow
- **ZeroDB memory tuning** — improve AI matchmaking accuracy

## Code of Conduct

Be constructive. This project exists to make social interactions safer — hold that standard in how you collaborate too.

## License

MIT — see [LICENSE](LICENSE).
