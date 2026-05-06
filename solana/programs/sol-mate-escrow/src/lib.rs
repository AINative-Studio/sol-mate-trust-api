use anchor_lang::prelude::*;
use anchor_spl::token::{self, Token, TokenAccount, Transfer};

declare_id!("SoLMateEsCrowXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX");

/// Sol Mate Safety Escrow Program
///
/// Implements stake-to-interact mechanics for social trust:
/// 1. User stakes USDC into a PDA-controlled escrow vault
/// 2. On meetup confirmation, stake is refunded
/// 3. On no-show/harassment, stake is slashed and sent to safety fund
/// 4. Backend authority (Sol Mate API) controls release/slash decisions

#[program]
pub mod sol_mate_escrow {
    use super::*;

    /// Initialize the program-wide authority account.
    /// Called once at deploy by the protocol admin.
    pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
        let authority = &mut ctx.accounts.authority;
        authority.admin = ctx.accounts.admin.key();
        authority.total_staked = 0;
        authority.total_slashed = 0;
        authority.total_refunded = 0;
        authority.bump = ctx.bumps.authority;
        emit!(AuthorityInitialized {
            admin: authority.admin,
        });
        Ok(())
    }

    /// Stake USDC into escrow for a room interaction.
    ///
    /// Creates a StakeVault PDA keyed by (staker, room_id).
    /// Transfers `amount` USDC from staker's ATA to the vault.
    pub fn stake(
        ctx: Context<Stake>,
        room_id: Pubkey,
        amount: u64,
        stake_type: StakeType,
    ) -> Result<()> {
        require!(amount > 0, EscrowError::ZeroStakeAmount);
        require!(
            ctx.accounts.staker_ata.amount >= amount,
            EscrowError::InsufficientBalance
        );

        let vault = &mut ctx.accounts.stake_vault;
        vault.staker = ctx.accounts.staker.key();
        vault.room_id = room_id;
        vault.amount = amount;
        vault.stake_type = stake_type;
        vault.status = StakeStatus::Active;
        vault.created_at = Clock::get()?.unix_timestamp;
        vault.bump = ctx.bumps.stake_vault;

        // Transfer USDC from staker ATA → vault ATA
        let cpi_ctx = CpiContext::new(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.staker_ata.to_account_info(),
                to: ctx.accounts.vault_ata.to_account_info(),
                authority: ctx.accounts.staker.to_account_info(),
            },
        );
        token::transfer(cpi_ctx, amount)?;

        // Update global stats
        let authority = &mut ctx.accounts.authority;
        authority.total_staked = authority.total_staked.checked_add(amount)
            .ok_or(EscrowError::Overflow)?;

        emit!(StakeDeposited {
            staker: vault.staker,
            room_id,
            amount,
            stake_type,
        });
        Ok(())
    }

    /// Refund stake back to user after successful meetup attestation.
    /// Only callable by the backend authority.
    pub fn refund(ctx: Context<Release>) -> Result<()> {
        let vault = &mut ctx.accounts.stake_vault;
        require!(
            vault.status == StakeStatus::Active,
            EscrowError::InvalidStakeStatus
        );

        let amount = vault.amount;
        vault.status = StakeStatus::Refunded;
        vault.resolved_at = Some(Clock::get()?.unix_timestamp);

        // PDA signs transfer: vault ATA → staker ATA
        let seeds: &[&[u8]] = &[
            b"stake_vault",
            vault.staker.as_ref(),
            vault.room_id.as_ref(),
            &[vault.bump],
        ];
        let signer = &[seeds];

        let cpi_ctx = CpiContext::new_with_signer(
            ctx.accounts.token_program.to_account_info(),
            Transfer {
                from: ctx.accounts.vault_ata.to_account_info(),
                to: ctx.accounts.staker_ata.to_account_info(),
                authority: ctx.accounts.stake_vault.to_account_info(),
            },
            signer,
        );
        token::transfer(cpi_ctx, amount)?;

        let authority = &mut ctx.accounts.authority;
        authority.total_refunded = authority.total_refunded.checked_add(amount)
            .ok_or(EscrowError::Overflow)?;

        emit!(StakeRefunded {
            staker: vault.staker,
            room_id: vault.room_id,
            amount,
        });
        Ok(())
    }

    /// Slash stake for no-show, harassment, or fraud.
    /// `slash_bps` is basis points to slash (e.g. 5000 = 50%).
    /// Slashed funds go to safety_fund_ata; remainder returned to staker.
    pub fn slash(
        ctx: Context<Release>,
        slash_bps: u16,
        reason: SlashReason,
    ) -> Result<()> {
        require!(slash_bps <= 10_000, EscrowError::InvalidSlashBps);

        let vault = &mut ctx.accounts.stake_vault;
        require!(
            vault.status == StakeStatus::Active,
            EscrowError::InvalidStakeStatus
        );

        let total = vault.amount;
        let slash_amount = (total as u128)
            .checked_mul(slash_bps as u128)
            .and_then(|v| v.checked_div(10_000))
            .ok_or(EscrowError::Overflow)? as u64;
        let refund_amount = total.checked_sub(slash_amount)
            .ok_or(EscrowError::Overflow)?;

        vault.status = StakeStatus::Slashed;
        vault.resolved_at = Some(Clock::get()?.unix_timestamp);

        let seeds: &[&[u8]] = &[
            b"stake_vault",
            vault.staker.as_ref(),
            vault.room_id.as_ref(),
            &[vault.bump],
        ];
        let signer = &[seeds];

        // Send slashed portion to safety fund
        if slash_amount > 0 {
            let cpi_slash = CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.vault_ata.to_account_info(),
                    to: ctx.accounts.safety_fund_ata.to_account_info(),
                    authority: ctx.accounts.stake_vault.to_account_info(),
                },
                signer,
            );
            token::transfer(cpi_slash, slash_amount)?;
        }

        // Return remainder to staker
        if refund_amount > 0 {
            let cpi_return = CpiContext::new_with_signer(
                ctx.accounts.token_program.to_account_info(),
                Transfer {
                    from: ctx.accounts.vault_ata.to_account_info(),
                    to: ctx.accounts.staker_ata.to_account_info(),
                    authority: ctx.accounts.stake_vault.to_account_info(),
                },
                signer,
            );
            token::transfer(cpi_return, refund_amount)?;
        }

        let authority = &mut ctx.accounts.authority;
        authority.total_slashed = authority.total_slashed.checked_add(slash_amount)
            .ok_or(EscrowError::Overflow)?;

        emit!(StakeSlashed {
            staker: vault.staker,
            room_id: vault.room_id,
            slash_amount,
            refund_amount,
            slash_bps,
            reason,
        });
        Ok(())
    }
}

// ---------------------------------------------------------------------------
// Accounts
// ---------------------------------------------------------------------------

#[derive(Accounts)]
pub struct Initialize<'info> {
    #[account(
        init,
        payer = admin,
        space = 8 + Authority::SPACE,
        seeds = [b"authority"],
        bump
    )]
    pub authority: Account<'info, Authority>,

    #[account(mut)]
    pub admin: Signer<'info>,

    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
#[instruction(room_id: Pubkey, amount: u64)]
pub struct Stake<'info> {
    #[account(
        init,
        payer = staker,
        space = 8 + StakeVault::SPACE,
        seeds = [b"stake_vault", staker.key().as_ref(), room_id.as_ref()],
        bump
    )]
    pub stake_vault: Account<'info, StakeVault>,

    /// USDC vault ATA — owned by stake_vault PDA
    #[account(mut)]
    pub vault_ata: Account<'info, TokenAccount>,

    /// Staker's USDC ATA
    #[account(
        mut,
        constraint = staker_ata.owner == staker.key() @ EscrowError::InvalidTokenAccountOwner
    )]
    pub staker_ata: Account<'info, TokenAccount>,

    #[account(mut, seeds = [b"authority"], bump = authority.bump)]
    pub authority: Account<'info, Authority>,

    #[account(mut)]
    pub staker: Signer<'info>,

    pub token_program: Program<'info, Token>,
    pub system_program: Program<'info, System>,
}

#[derive(Accounts)]
pub struct Release<'info> {
    #[account(
        mut,
        seeds = [b"stake_vault", stake_vault.staker.as_ref(), stake_vault.room_id.as_ref()],
        bump = stake_vault.bump
    )]
    pub stake_vault: Account<'info, StakeVault>,

    #[account(mut)]
    pub vault_ata: Account<'info, TokenAccount>,

    #[account(mut)]
    pub staker_ata: Account<'info, TokenAccount>,

    /// Safety fund ATA (only used in slash; harmless to include in refund)
    #[account(mut)]
    pub safety_fund_ata: Account<'info, TokenAccount>,

    #[account(
        mut,
        seeds = [b"authority"],
        bump = authority.bump,
        constraint = authority.admin == backend_authority.key() @ EscrowError::Unauthorized
    )]
    pub authority: Account<'info, Authority>,

    /// Sol Mate backend keypair — must be the program admin
    pub backend_authority: Signer<'info>,

    pub token_program: Program<'info, Token>,
}

// ---------------------------------------------------------------------------
// State
// ---------------------------------------------------------------------------

#[account]
pub struct Authority {
    pub admin: Pubkey,         // 32
    pub total_staked: u64,     // 8
    pub total_slashed: u64,    // 8
    pub total_refunded: u64,   // 8
    pub bump: u8,              // 1
}

impl Authority {
    pub const SPACE: usize = 32 + 8 + 8 + 8 + 1;
}

#[account]
pub struct StakeVault {
    pub staker: Pubkey,                 // 32
    pub room_id: Pubkey,                // 32
    pub amount: u64,                    // 8
    pub stake_type: StakeType,          // 1
    pub status: StakeStatus,            // 1
    pub created_at: i64,                // 8
    pub resolved_at: Option<i64>,       // 9 (1 + 8)
    pub bump: u8,                       // 1
}

impl StakeVault {
    pub const SPACE: usize = 32 + 32 + 8 + 1 + 1 + 8 + 9 + 1;
}

// ---------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum StakeType {
    RoomEntry,    // Entering a stake-gated room
    MatchRequest, // Initiating a match
    DmUnlock,     // Unlocking DM channel
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum StakeStatus {
    Active,
    Refunded,
    Slashed,
    Disputed,
}

#[derive(AnchorSerialize, AnchorDeserialize, Clone, Copy, PartialEq, Eq)]
pub enum SlashReason {
    NoShow,
    Harassment,
    FalseReport,
    Fraud,
    ContentViolation,
}

// ---------------------------------------------------------------------------
// Events
// ---------------------------------------------------------------------------

#[event]
pub struct AuthorityInitialized {
    pub admin: Pubkey,
}

#[event]
pub struct StakeDeposited {
    pub staker: Pubkey,
    pub room_id: Pubkey,
    pub amount: u64,
    pub stake_type: StakeType,
}

#[event]
pub struct StakeRefunded {
    pub staker: Pubkey,
    pub room_id: Pubkey,
    pub amount: u64,
}

#[event]
pub struct StakeSlashed {
    pub staker: Pubkey,
    pub room_id: Pubkey,
    pub slash_amount: u64,
    pub refund_amount: u64,
    pub slash_bps: u16,
    pub reason: SlashReason,
}

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

#[error_code]
pub enum EscrowError {
    #[msg("Stake amount must be greater than zero")]
    ZeroStakeAmount,
    #[msg("Insufficient USDC balance")]
    InsufficientBalance,
    #[msg("Stake is not in Active status")]
    InvalidStakeStatus,
    #[msg("Slash basis points must be between 0 and 10000")]
    InvalidSlashBps,
    #[msg("Only the backend authority can release or slash stakes")]
    Unauthorized,
    #[msg("Token account owner mismatch")]
    InvalidTokenAccountOwner,
    #[msg("Arithmetic overflow")]
    Overflow,
}
