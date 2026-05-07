const README = `# Sol Mate

Stake USDC to DM, match, and meet. No-shows get slashed on Solana.

Built for the **EasyA × Consensus Miami Hackathon 2026** by AINative Studio.

## How It Works

1. Connect your Phantom or Solflare wallet
2. Stake USDC to send a DM, enter a room, or propose a meetup
3. Both parties confirm via GPS attestation
4. No-show → stake slashed. Show up → stake returned + reputation boost
5. After a confirmed meetup, mint a Moment NFT

## API

Base URL: https://sol-mate-trust-api-production.up.railway.app
Docs: https://sol-mate-trust-api-production.up.railway.app/docs

## Open Source

- \`pip install solmate-stake-sdk\` — StakeGate, SlashingPolicy
- \`pip install solmate-reputation\` — ReputationEngine, Hedera HCS
- \`pip install solmate-x402\` — Coinbase x402 USDC payments

## Agent Discovery

- /llms.txt — LLM summary
- /llms-full.txt — Full manifest
- /agents.md — Agent guide
- /agent.json — Machine-readable capabilities
- /openapi.json — OpenAPI spec
`

export async function GET() {
  return new Response(README, {
    headers: { 'Content-Type': 'text/markdown; charset=utf-8' },
  })
}
