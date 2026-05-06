import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { SolMateEscrow } from "../target/types/sol_mate_escrow";
import {
  createMint,
  createAssociatedTokenAccount,
  mintTo,
  getAccount,
  TOKEN_PROGRAM_ID,
} from "@solana/spl-token";
import { assert } from "chai";

describe("sol-mate-escrow", () => {
  const provider = anchor.AnchorProvider.env();
  anchor.setProvider(provider);
  const program = anchor.workspace.SolMateEscrow as Program<SolMateEscrow>;

  let usdcMint: anchor.web3.PublicKey;
  let staker: anchor.web3.Keypair;
  let stakerAta: anchor.web3.PublicKey;
  let safetyFundAta: anchor.web3.PublicKey;
  let authorityPda: anchor.web3.PublicKey;
  let authorityBump: number;
  const roomId = anchor.web3.Keypair.generate().publicKey;
  const STAKE_AMOUNT = 5_000_000; // 5 USDC (6 decimals)

  before(async () => {
    staker = anchor.web3.Keypair.generate();

    // Airdrop SOL to staker
    await provider.connection.confirmTransaction(
      await provider.connection.requestAirdrop(staker.publicKey, 2e9)
    );

    // Create USDC-like mint (6 decimals)
    usdcMint = await createMint(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      provider.wallet.publicKey,
      null,
      6
    );

    // Create ATAs
    stakerAta = await createAssociatedTokenAccount(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      staker.publicKey
    );
    safetyFundAta = await createAssociatedTokenAccount(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      provider.wallet.publicKey
    );

    // Mint tokens to staker
    await mintTo(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      stakerAta,
      provider.wallet.publicKey,
      10_000_000 // 10 USDC
    );

    // Derive authority PDA
    [authorityPda, authorityBump] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("authority")],
      program.programId
    );
  });

  it("initializes the authority account", async () => {
    await program.methods
      .initialize()
      .accounts({
        authority: authorityPda,
        admin: provider.wallet.publicKey,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .rpc();

    const auth = await program.account.authority.fetch(authorityPda);
    assert.ok(auth.admin.equals(provider.wallet.publicKey));
    assert.equal(auth.totalStaked.toNumber(), 0);
  });

  it("stakes USDC into escrow vault", async () => {
    const [vaultPda] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake_vault"), staker.publicKey.toBuffer(), roomId.toBuffer()],
      program.programId
    );

    const vaultAta = await createAssociatedTokenAccount(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      vaultPda,
      true // allowOwnerOffCurve — PDA owns the ATA
    );

    await program.methods
      .stake(roomId, new anchor.BN(STAKE_AMOUNT), { roomEntry: {} })
      .accounts({
        stakeVault: vaultPda,
        vaultAta,
        stakerAta,
        authority: authorityPda,
        staker: staker.publicKey,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([staker])
      .rpc();

    const vault = await program.account.stakeVault.fetch(vaultPda);
    assert.ok(vault.staker.equals(staker.publicKey));
    assert.equal(vault.amount.toNumber(), STAKE_AMOUNT);
    assert.deepEqual(vault.status, { active: {} });

    const vaultBalance = await getAccount(provider.connection, vaultAta);
    assert.equal(Number(vaultBalance.amount), STAKE_AMOUNT);

    const auth = await program.account.authority.fetch(authorityPda);
    assert.equal(auth.totalStaked.toNumber(), STAKE_AMOUNT);
  });

  it("refunds stake after meetup attestation", async () => {
    const [vaultPda] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake_vault"), staker.publicKey.toBuffer(), roomId.toBuffer()],
      program.programId
    );

    const vaultAta = await createAssociatedTokenAccount(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      vaultPda,
      true
    );

    const balanceBefore = await getAccount(provider.connection, stakerAta);

    await program.methods
      .refund()
      .accounts({
        stakeVault: vaultPda,
        vaultAta,
        stakerAta,
        safetyFundAta,
        authority: authorityPda,
        backendAuthority: provider.wallet.publicKey,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .rpc();

    const vault = await program.account.stakeVault.fetch(vaultPda);
    assert.deepEqual(vault.status, { refunded: {} });

    const balanceAfter = await getAccount(provider.connection, stakerAta);
    assert.equal(
      Number(balanceAfter.amount) - Number(balanceBefore.amount),
      STAKE_AMOUNT
    );

    const auth = await program.account.authority.fetch(authorityPda);
    assert.equal(auth.totalRefunded.toNumber(), STAKE_AMOUNT);
  });

  it("slashes 50% for no-show, returns remainder to staker", async () => {
    // Create a fresh staker + room for this test
    const slashStaker = anchor.web3.Keypair.generate();
    await provider.connection.confirmTransaction(
      await provider.connection.requestAirdrop(slashStaker.publicKey, 2e9)
    );
    const slashRoomId = anchor.web3.Keypair.generate().publicKey;

    const slashStakerAta = await createAssociatedTokenAccount(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      slashStaker.publicKey
    );
    await mintTo(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      slashStakerAta,
      provider.wallet.publicKey,
      10_000_000
    );

    const [vaultPda] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake_vault"), slashStaker.publicKey.toBuffer(), slashRoomId.toBuffer()],
      program.programId
    );

    const vaultAta = await createAssociatedTokenAccount(
      provider.connection,
      (provider.wallet as anchor.Wallet).payer,
      usdcMint,
      vaultPda,
      true
    );

    // Stake
    await program.methods
      .stake(slashRoomId, new anchor.BN(STAKE_AMOUNT), { matchRequest: {} })
      .accounts({
        stakeVault: vaultPda,
        vaultAta,
        stakerAta: slashStakerAta,
        authority: authorityPda,
        staker: slashStaker.publicKey,
        tokenProgram: TOKEN_PROGRAM_ID,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([slashStaker])
      .rpc();

    const stakerBalBefore = await getAccount(provider.connection, slashStakerAta);
    const fundBalBefore = await getAccount(provider.connection, safetyFundAta);

    // Slash 50%
    await program.methods
      .slash(5000, { noShow: {} })
      .accounts({
        stakeVault: vaultPda,
        vaultAta,
        stakerAta: slashStakerAta,
        safetyFundAta,
        authority: authorityPda,
        backendAuthority: provider.wallet.publicKey,
        tokenProgram: TOKEN_PROGRAM_ID,
      })
      .rpc();

    const vault = await program.account.stakeVault.fetch(vaultPda);
    assert.deepEqual(vault.status, { slashed: {} });

    const stakerBalAfter = await getAccount(provider.connection, slashStakerAta);
    const fundBalAfter = await getAccount(provider.connection, safetyFundAta);

    // Staker gets back 50%
    assert.equal(
      Number(stakerBalAfter.amount) - Number(stakerBalBefore.amount),
      STAKE_AMOUNT / 2
    );
    // Safety fund receives 50%
    assert.equal(
      Number(fundBalAfter.amount) - Number(fundBalBefore.amount),
      STAKE_AMOUNT / 2
    );
  });

  it("rejects slash from unauthorized signer", async () => {
    const unauthorized = anchor.web3.Keypair.generate();
    const fakeRoomId = anchor.web3.Keypair.generate().publicKey;
    const [vaultPda] = anchor.web3.PublicKey.findProgramAddressSync(
      [Buffer.from("stake_vault"), staker.publicKey.toBuffer(), fakeRoomId.toBuffer()],
      program.programId
    );

    try {
      await program.methods
        .slash(10000, { fraud: {} })
        .accounts({
          stakeVault: vaultPda,
          vaultAta: stakerAta, // wrong but irrelevant — should fail on authority check
          stakerAta,
          safetyFundAta,
          authority: authorityPda,
          backendAuthority: unauthorized.publicKey,
          tokenProgram: TOKEN_PROGRAM_ID,
        })
        .signers([unauthorized])
        .rpc();
      assert.fail("Expected unauthorized error");
    } catch (err: any) {
      assert.include(err.message, "Unauthorized");
    }
  });
});
