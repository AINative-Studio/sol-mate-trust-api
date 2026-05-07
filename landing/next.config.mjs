/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "standalone",
  trailingSlash: true,
  skipTrailingSlashRedirect: true,
  images: {
    unoptimized: true,
  },
  async redirects() {
    return [
      {
        source: "/ai-plugin.json",
        destination: "/.well-known/ai-plugin.json",
        permanent: true,
      },
      {
        source: "/AGENTS.md",
        destination: "/agents.md",
        permanent: true,
      },
    ];
  },
};

export default nextConfig;
