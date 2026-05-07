"""
SolanaService — submits memo transactions to Solana devnet to record stake
events on-chain. Uses the SPL Memo program so that each stake/refund/slash
produces a real, explorer-visible transaction without requiring a full USDC
token setup.

Graceful degradation: if the keypair file is missing or any RPC call fails,
the methods return None so the rest of the API keeps working normally.
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# SPL Memo program — accepts arbitrary UTF-8 data, no account balance needed
# beyond the tx fee on the fee-payer.
MEMO_PROGRAM_ID_STR = "MemoSq4gqABAXKb96qnH8TysNcWxMyWCqXgDLGmfcHr"


def _load_keypair() -> Optional["Keypair"]:  # noqa: F821
    """Load the Solana keypair from SOLANA_KEYPAIR_PATH env var.

    Returns None if the path is unset or the file does not exist so that
    callers can degrade gracefully.
    """
    try:
        from solders.keypair import Keypair  # type: ignore

        raw_path = os.environ.get("SOLANA_KEYPAIR_PATH", "~/.config/solana/id.json")
        keypair_path = Path(raw_path).expanduser()
        if not keypair_path.exists():
            logger.debug("Solana keypair not found at %s — skipping on-chain memo", keypair_path)
            return None

        key_bytes = json.loads(keypair_path.read_text())
        return Keypair.from_bytes(bytes(key_bytes))
    except Exception as exc:
        logger.warning("Failed to load Solana keypair: %s", exc)
        return None


def _rpc_url() -> str:
    """Return the Solana RPC URL, preferring the config module value."""
    try:
        from ..core.config import settings  # noqa: PLC0415

        return settings.SOLANA_RPC_URL
    except Exception:
        return os.environ.get("SOLANA_RPC_URL", "https://api.devnet.solana.com")


class SolanaService:
    """Submits lightweight SPL Memo transactions to Solana devnet.

    Each public method serialises the event as JSON and embeds it in a
    memo instruction.  The fee-payer is the keypair loaded from
    ``SOLANA_KEYPAIR_PATH``.  All methods return the base-58 transaction
    signature on success, or ``None`` on any error.
    """

    def _submit_memo(self, memo_payload: dict) -> Optional[str]:
        """Core helper: build and send a single memo transaction.

        Returns the tx signature string or None.
        """
        keypair = _load_keypair()
        if keypair is None:
            return None

        try:
            from solana.rpc.api import Client  # type: ignore
            from solana.rpc.types import TxOpts  # type: ignore
            from solders.instruction import AccountMeta, Instruction  # type: ignore
            from solders.message import Message  # type: ignore
            from solders.pubkey import Pubkey  # type: ignore
            from solders.transaction import Transaction  # type: ignore

            client = Client(_rpc_url())
            memo_program_id = Pubkey.from_string(MEMO_PROGRAM_ID_STR)

            # Memo data — JSON-encoded event record
            memo_bytes = json.dumps(memo_payload, separators=(",", ":")).encode("utf-8")

            instruction = Instruction(
                program_id=memo_program_id,
                accounts=[
                    AccountMeta(
                        pubkey=keypair.pubkey(),
                        is_signer=True,
                        is_writable=False,
                    )
                ],
                data=memo_bytes,
            )

            blockhash_resp = client.get_latest_blockhash()
            recent_blockhash = blockhash_resp.value.blockhash

            msg = Message.new_with_blockhash(
                [instruction],
                keypair.pubkey(),
                recent_blockhash,
            )
            tx = Transaction([keypair], msg, recent_blockhash)

            result = client.send_transaction(
                tx,
                opts=TxOpts(skip_preflight=False, preflight_commitment="confirmed"),
            )
            sig = str(result.value)
            logger.info(
                "Solana memo tx submitted | event=%s sig=%s",
                memo_payload.get("event"),
                sig,
            )
            return sig

        except Exception as exc:
            logger.warning(
                "Solana memo tx failed (non-fatal) | event=%s error=%s",
                memo_payload.get("event", "unknown"),
                exc,
            )
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def submit_stake_memo(
        self,
        stake_id: str,
        user_wallet: Optional[str],
        amount_usdc: float,
        stake_type: str,
    ) -> Optional[str]:
        """Record a stake event on-chain.

        Returns the devnet tx signature or None if Solana is unavailable.
        """
        payload = {
            "event": "stake",
            "program": "GihCjDJeAwbNtr826dEAfQFp4GAVBgHWLxDf2sqsQLif",
            "stake_id": str(stake_id),
            "wallet": user_wallet,
            "amount": round(amount_usdc, 6),
            "type": str(stake_type),
        }
        return self._submit_memo(payload)

    def submit_refund_memo(
        self,
        stake_id: str,
        user_wallet: Optional[str],
        amount_usdc: float,
    ) -> Optional[str]:
        """Record a refund event on-chain.

        Returns the devnet tx signature or None if Solana is unavailable.
        """
        payload = {
            "event": "refund",
            "program": "GihCjDJeAwbNtr826dEAfQFp4GAVBgHWLxDf2sqsQLif",
            "stake_id": str(stake_id),
            "wallet": user_wallet,
            "amount": round(amount_usdc, 6),
        }
        return self._submit_memo(payload)

    def submit_slash_memo(
        self,
        stake_id: str,
        user_wallet: Optional[str],
        amount_usdc: float,
        reason: str,
    ) -> Optional[str]:
        """Record a slash event on-chain.

        Returns the devnet tx signature or None if Solana is unavailable.
        """
        payload = {
            "event": "slash",
            "program": "GihCjDJeAwbNtr826dEAfQFp4GAVBgHWLxDf2sqsQLif",
            "stake_id": str(stake_id),
            "wallet": user_wallet,
            "amount": round(amount_usdc, 6),
            "reason": reason,
        }
        return self._submit_memo(payload)
