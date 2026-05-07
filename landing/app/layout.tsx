import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Sol Mate — Skin in the Game Social",
  description:
    "Stake USDC to DM, match, and meet. No-shows get slashed. Harassment gets slashed. AI matchmaking. GPS attestation. Economic accountability replaces swipe culture.",
  keywords: [
    "Solana",
    "dating app",
    "Web3",
    "USDC",
    "stake-to-interact",
    "AI matchmaking",
    "dApp",
    "Seeker",
    "Consensus Miami",
  ],
  openGraph: {
    title: "Sol Mate — Skin in the Game Social",
    description:
      "Stake USDC to DM, match, and meet. Economic accountability replaces swipe culture.",
    siteName: "Sol Mate",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Sol Mate — Skin in the Game Social",
    description:
      "Stake USDC to DM, match, and meet. No-shows get slashed. Genuine connections get rewarded.",
  },
  manifest: "/manifest.json",
};

export const viewport = {
  themeColor: "#7C3AED",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="scroll-smooth">
      <body>{children}</body>
    </html>
  );
}
