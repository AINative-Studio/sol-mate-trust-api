# Solana Seeker dApp Store — Submission Guide

Sol Mate target device: **Solana Seeker** (Android, Web3 phone, $450)  
Official dApp Store 2.0 — 150k+ users, 100+ listed dApps, on-chain NFT registry.

---

## What Is Seeker dApp Store 2.0?

Unlike Apple App Store or Google Play, Seeker dApp Store lists apps as **on-chain NFTs** on Solana mainnet. Every app = an App NFT. Every release = a Release NFT. Discoverability happens on-chain.

- Publishing CLI: `solana-mobile/dapp-publishing` (GitHub)
- Official docs: `docs.solanamobile.com`
- Review time: 2–5 business days

---

## Prerequisites

- [ ] Solana mainnet wallet with ~0.1 SOL (for minting NFT metadata)
- [ ] `@solana-mobile/dapp-publishing` CLI installed
- [ ] `solana-cli` installed and configured for mainnet
- [ ] Android APK or hosted PWA/web app URL
- [ ] Publisher Portal account (KYC required)

---

## Step 1: Publisher Portal KYC

1. Go to `publisher.solanamobile.com`
2. Create a Publisher account
3. Complete identity verification (KYC) — required before any submission
4. Fund your publisher wallet with SOL for NFT minting fees

---

## Step 2: Prepare `config.yaml`

This is the app manifest. Place at `seeker/config.yaml` in this repo:

```yaml
# seeker/config.yaml
publisher:
  name: "AINative Studio"
  website: "https://ainative.studio"
  contact: "hello@ainative.studio"

release:
  catalog_entry:
    name: "Sol Mate"
    tagline: "Stake USDC to DM, match, and meet."
    description: |
      Sol Mate is a stake-to-interact social app where economic accountability
      replaces swipe culture. Stake USDC to enter rooms, request matches, and
      unlock DMs. Genuine meetups release your stake. No-shows get slashed.
      AI matchmaking. GPS attestation. Hedera HCS audit trail.
    
    short_description: "Stake-to-interact social app. Skin in the game replaces swipe culture."
    
    icon: "./assets/icon.png"           # 512x512 PNG
    screenshots:
      - "./assets/screenshot_1.png"     # 1080x2340 portrait
      - "./assets/screenshot_2.png"
      - "./assets/screenshot_3.png"
    
    android:
      package_name: "studio.ainative.solmate"
      minimum_sdk: 26
    
    categories:
      - "Social"
      - "Lifestyle"
    
    website_url: "https://sol-mate-trust-api-production.up.railway.app"
    contact_email: "hello@ainative.studio"

  android:
    apk_url: ""  # Fill in: direct link to APK or hosted PWA manifest
```

---

## Step 3: Create `seeker/` Asset Directory

```
seeker/
  config.yaml
  assets/
    icon.png              # 512x512 PNG, no rounded corners (Seeker applies them)
    screenshot_1.png      # Match discovery screen
    screenshot_2.png      # Stake-to-connect flow
    screenshot_3.png      # GPS meetup attestation
    feature_graphic.png   # 1024x500 banner (optional)
```

---

## Step 4: Install Publishing CLI

```bash
npm install -g @solana-mobile/dapp-publishing
```

Or use via npx:
```bash
npx @solana-mobile/dapp-publishing --help
```

---

## Step 5: Mint App NFT (Publisher NFT)

This is the one-time on-chain registration of your publisher identity.

```bash
npx @solana-mobile/dapp-publishing create publisher \
  --keypair ~/.config/solana/id.json \
  --url mainnet-beta
```

Save the **Publisher NFT mint address** — you'll need it for all releases.

---

## Step 6: Create App NFT

```bash
npx @solana-mobile/dapp-publishing create app \
  --keypair ~/.config/solana/id.json \
  --url mainnet-beta
```

This mints the App NFT on Solana mainnet. Outputs an **App NFT mint address**.

---

## Step 7: Mint Release NFT

```bash
npx @solana-mobile/dapp-publishing create release \
  --keypair ~/.config/solana/id.json \
  --url mainnet-beta \
  --config seeker/config.yaml
```

Each version update requires a new Release NFT.

---

## Step 8: Submit for Review

```bash
npx @solana-mobile/dapp-publishing publish submit \
  --keypair ~/.config/solana/id.json \
  --url mainnet-beta
```

Then go to `publisher.solanamobile.com/dashboard` to track review status.

---

## Step 9: Post-Approval

After 2–5 business days, your app appears in the Seeker dApp Store 2.0 on-device.  
Users can install directly from their Seeker phone.

---

## Alternative: Android Sideload (for Hackathon Demo)

For the EasyA hackathon demo, judges with a Seeker phone can sideload the APK directly:

```bash
# Enable "Unknown sources" in Seeker settings → Security → Install unknown apps
adb install sol-mate.apk

# Or share via direct URL:
# https://sol-mate-trust-api-production.up.railway.app/download/sol-mate.apk
```

Or access the dApp as a **Progressive Web App**:

1. Open `https://sol-mate-trust-api-production.up.railway.app` in Seeker browser
2. Tap the 3-dot menu → "Add to Home Screen"
3. App icon appears on Seeker home screen — no install required

---

## PWA Implementation Checklist

To make Sol Mate fully installable as a PWA on Seeker:

- [ ] Add `public/manifest.json` with `display: "standalone"`
- [ ] Add `public/service-worker.js` for offline caching
- [ ] Add `<link rel="manifest">` to `app/layout.tsx`
- [ ] 512x512 app icon at `public/icon-512.png`
- [ ] HTTPS (already satisfied by Railway deployment)

---

## Resources

- Publishing CLI: `github.com/solana-mobile/dapp-publishing`
- Official docs: `docs.solanamobile.com/dapp-publishing/overview`
- Publisher Portal: `publisher.solanamobile.com`
- Seeker Discord: `discord.gg/solana-mobile`
