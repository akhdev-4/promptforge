import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Emit a minimal standalone server bundle for small production images.
  output: "standalone",
  poweredByHeader: false,
  reactStrictMode: true,
};

export default nextConfig;
