"""
solmate-stake-sdk — Stake-gated access control for Solana dApps

Any Solana dApp can require a USDC stake before a DM, room entry, or action.
Extracted from Sol Mate Trust API.

Install: pip install solmate-stake-sdk

Features:
  - Stake lifecycle: create → active → refund/slash
  - Three stake types: dm_unlock, room_entry, meetup_request
  - Solana SPL Memo on-chain recording
  - Circle USDC escrow (graceful stub when unconfigured)
  - Per-type minimum USDC amounts
  - Repeat offender multiplier (each no-show raises required stake 0.5×)
"""

from .stake import StakeType, StakeStatus, StakeRecord, StakeGate
from .slashing import SlashingPolicy, SlashReason

__version__ = "0.1.0"
__all__ = [
    "StakeType",
    "StakeStatus",
    "StakeRecord",
    "StakeGate",
    "SlashingPolicy",
    "SlashReason",
]
