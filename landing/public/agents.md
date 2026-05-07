# Sol Mate — Agent Interaction Guide

## What Sol Mate Is

Sol Mate is a trust-based social dApp on Solana. Users stake USDC to send DMs, enter rooms, and confirm meetups. No-shows are automatically slashed. AI matchmaking is powered by AINative embeddings and ZeroDB semantic search.

Built for the EasyA × Consensus Miami Hackathon 2026 by AINative Studio.

## API Base

```
https://sol-mate-trust-api-production.up.railway.app
```

Interactive docs: `https://sol-mate-trust-api-production.up.railway.app/docs`

## Authentication (for agents)

Sol Mate uses wallet-signature JWT authentication:

1. `POST /api/v1/auth/wallet/connect` with `{ "wallet_address": "<address>" }` → returns `challenge`
2. Sign the challenge with the wallet private key
3. `POST /api/v1/auth/wallet/connect` with `{ "wallet_address", "signature", "challenge" }` → returns `access_token`
4. Include `Authorization: Bearer <access_token>` on all subsequent requests

## Actions Available to Agents

| Action | Method | Path |
|--------|--------|------|
| Discover rooms | GET | /api/v1/rooms |
| Create a stake | POST | /api/v1/stakes |
| Request a match | POST | /api/v1/matches |
| Send a message | POST | /api/v1/messages |
| Submit meetup attestation | POST | /api/v1/attestations |
| Gift SOL to a user | POST | /api/v1/transfers |
| Mint a Moment NFT | POST | /api/v1/nfts/mint-moment |
| List my Moment NFTs | GET | /api/v1/nfts/moments |

## Open Source SDKs

```bash
pip install solmate-stake-sdk    # StakeGate, SlashingPolicy
pip install solmate-reputation   # ReputationEngine, Hedera HCS anchoring
pip install x402-solana          # Coinbase x402 USDC payment middleware
```

## Full Reference

- Full API manifest: /llms-full.txt
- OpenAPI spec: /openapi.json
- SDK details: /sdks.txt
