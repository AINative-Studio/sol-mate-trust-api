# Sol Mate — Machine-Readable Agent Guide

## Overview

Sol Mate is a trust-based social dApp on Solana. Stake USDC to DM, match, and meet. No-shows get slashed. AI matchmaking powered by AINative.

## Core APIs

**Authentication** — Wallet signature challenge flow → JWT bearer token

**Stakes** — Create USDC stakes for DMs, room entry, or meetups

**Matching** — AI-powered match requests with generated intro messages

**Messaging** — Stake-gated DMs between matched users

**Attestations** — GPS-verified meetup confirmation

**Transfers** — Gift SOL to another user

**Moment NFTs** — Mint commemorative NFTs for confirmed meetups

## API Base
```
https://sol-mate-trust-api-production.up.railway.app
```

## Authentication
JWT via wallet signature. Challenge-response flow.
Header: `Authorization: Bearer <token>`

## Key Endpoints
```
POST /api/v1/auth/wallet/connect   Wallet auth
GET  /api/v1/rooms                 Discover rooms
POST /api/v1/stakes                Create stake
POST /api/v1/matches               Request match
POST /api/v1/messages              Send message
POST /api/v1/attestations          Submit attestation
POST /api/v1/transfers             Gift SOL
POST /api/v1/nfts/mint-moment      Mint Moment NFT
GET  /api/v1/nfts/moments          List Moment NFTs
```

## SDKs
```bash
pip install solmate-stake-sdk
pip install solmate-reputation
pip install x402-solana
```

## Full details: /llms-full.txt
