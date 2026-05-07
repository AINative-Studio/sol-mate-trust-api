const GITHUB_URL = "https://github.com/AINative-Studio/sol-mate-trust-api";

const PACKAGES = [
  {
    name: "solmate-stake-sdk",
    registries: "PyPI + npm",
    desc: "Stake-gated access control for any Solana dApp. Require USDC escrow before DMs, room entry, or any action.",
    status: "planned",
  },
  {
    name: "solmate-reputation",
    registries: "PyPI",
    desc: "On-chain reputation decay with Hedera HCS anchoring. Portable trust scoring for Web3 social apps.",
    status: "planned",
  },
  {
    name: "x402-solana",
    registries: "PyPI",
    desc: "FastAPI middleware bridging Solana stake mechanics with Coinbase x402 HTTP payments on Base. Novel cross-chain primitive.",
    status: "planned",
  },
];

const CONTRIBUTIONS = [
  {
    icon: "🏗️",
    title: "Anchor Escrow Program",
    desc: 'Open-source PDA escrow keyed by (staker, room_id). Reusable for any stake-gated Solana app. Program ID: GihCjDJeAwbNtr826dEAfQFp4GAVBgHWLxDf2sqsQLif',
  },
  {
    icon: "🔐",
    title: "x402 × Solana Bridge",
    desc: "First-of-kind FastAPI middleware connecting Solana wallet auth with Coinbase x402 HTTP payment proofs on Base USDC.",
  },
  {
    icon: "🧠",
    title: "Pure-Python Preference Embeddings",
    desc: "45-term bag-of-words vocabulary, L2-normalised, zero numpy dependency. Embeddable preference memory for resource-constrained environments.",
  },
  {
    icon: "📋",
    title: "HCS Safety Audit Pattern",
    desc: "Reusable pattern for anchoring moderation decisions on Hedera HCS — immutable, verifiable, and GDPR-compatible.",
  },
];

export default function OpenSource() {
  return (
    <section id="open-source" className="py-24 px-6 bg-brand-dark/50">
      <div className="max-w-6xl mx-auto">
        <div className="text-center mb-16">
          <div className="inline-block text-sm font-medium text-green-400 bg-green-500/10 border border-green-500/20 px-4 py-1.5 rounded-full mb-4">
            Open Source
          </div>
          <h2 className="text-4xl md:text-5xl font-black tracking-tight">
            Built for the ecosystem.{" "}
            <span className="text-gradient">Free to fork.</span>
          </h2>
          <p className="mt-4 text-white/50 max-w-xl mx-auto text-lg">
            Sol Mate is MIT licensed. The primitives we built — stake gating,
            reputation decay, x402 bridging — are being extracted as standalone
            packages.
          </p>
        </div>

        {/* Ecosystem contributions */}
        <div className="grid md:grid-cols-2 gap-5 mb-12">
          {CONTRIBUTIONS.map((c) => (
            <div
              key={c.title}
              className="p-6 rounded-2xl border-gradient bg-brand-card"
            >
              <div className="text-3xl mb-3">{c.icon}</div>
              <h3 className="font-bold mb-2">{c.title}</h3>
              <p className="text-white/50 text-sm leading-relaxed">{c.desc}</p>
            </div>
          ))}
        </div>

        {/* Planned packages */}
        <h3 className="text-sm font-semibold text-white/40 uppercase tracking-widest mb-4">
          Planned Packages (post-hackathon)
        </h3>
        <div className="grid md:grid-cols-3 gap-5 mb-12">
          {PACKAGES.map((pkg) => (
            <div
              key={pkg.name}
              className="p-5 rounded-xl bg-brand-card border border-brand-border"
            >
              <div className="flex items-start justify-between mb-2">
                <code className="text-sm font-mono text-violet-300">
                  {pkg.name}
                </code>
                <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-500/15 text-yellow-400 border border-yellow-500/25">
                  {pkg.status}
                </span>
              </div>
              <div className="text-xs text-white/40 mb-3">{pkg.registries}</div>
              <p className="text-white/55 text-sm leading-relaxed">{pkg.desc}</p>
            </div>
          ))}
        </div>

        {/* GitHub CTA */}
        <div className="text-center">
          <a
            href={GITHUB_URL}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-8 py-4 rounded-full border border-brand-violet/50 text-white font-semibold text-lg hover:border-brand-violet hover:glow-violet transition-all"
          >
            <svg
              className="w-5 h-5"
              fill="currentColor"
              viewBox="0 0 24 24"
            >
              <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z" />
            </svg>
            View on GitHub
          </a>
          <p className="mt-3 text-white/35 text-sm">
            MIT License · 324 tests · 94% coverage
          </p>
        </div>
      </div>
    </section>
  );
}
