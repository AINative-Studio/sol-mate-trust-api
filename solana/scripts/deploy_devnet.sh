#!/usr/bin/env bash
# Deploy Sol Mate Escrow program to Solana devnet
set -euo pipefail

PROGRAM_NAME="sol_mate_escrow"
CLUSTER="devnet"
WALLET="${SOLANA_KEYPAIR:-$HOME/.config/solana/id.json}"

echo "=== Sol Mate Escrow — Devnet Deploy ==="
echo "Cluster:  $CLUSTER"
echo "Wallet:   $WALLET"

# Confirm toolchain
anchor --version
solana --version
solana config set --url $CLUSTER

# Show wallet balance
echo ""
echo "Wallet balance:"
solana balance "$WALLET" --url $CLUSTER

# Airdrop if balance < 2 SOL
BALANCE=$(solana balance "$WALLET" --url $CLUSTER | awk '{print $1}')
if (( $(echo "$BALANCE < 2" | bc -l) )); then
  echo "Requesting devnet airdrop..."
  solana airdrop 2 "$WALLET" --url $CLUSTER
fi

echo ""
echo "Building program..."
cd "$(dirname "$0")/.."
anchor build

PROGRAM_ID=$(solana address -k "target/deploy/${PROGRAM_NAME}-keypair.json")
echo "Program ID: $PROGRAM_ID"

# Update declare_id! in source
sed -i.bak "s/SoLMateEsCrowXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/$PROGRAM_ID/" \
    "programs/sol-mate-escrow/src/lib.rs"

# Update Anchor.toml
sed -i.bak "s/SoLMateEsCrowXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX/$PROGRAM_ID/" \
    Anchor.toml

# Rebuild with correct ID
anchor build

echo ""
echo "Deploying to devnet..."
anchor deploy --provider.cluster $CLUSTER

echo ""
echo "Uploading IDL..."
anchor idl init --provider.cluster $CLUSTER \
    --filepath "target/idl/sol_mate_escrow.json" \
    "$PROGRAM_ID" || \
anchor idl upgrade --provider.cluster $CLUSTER \
    --filepath "target/idl/sol_mate_escrow.json" \
    "$PROGRAM_ID"

echo ""
echo "=== Deploy complete ==="
echo "Program ID: $PROGRAM_ID"
echo "Explorer:   https://explorer.solana.com/address/$PROGRAM_ID?cluster=devnet"
echo ""
echo "Add this to your backend .env:"
echo "SOLANA_PROGRAM_ID=$PROGRAM_ID"
echo "SOLANA_RPC_URL=https://api.devnet.solana.com"
