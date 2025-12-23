import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: 'export',
  images: {
    unoptimized: true,
  },
  // Set basePath for GitHub Pages (repo name)
  // Uncomment and adjust if deploying to a repository subdirectory
  // basePath: '/ha-discover',
};

export default nextConfig;
