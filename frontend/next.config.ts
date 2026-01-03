import path from "node:path";
import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "export",
  images: {
    unoptimized: true,
  },
  // Set basePath for GitHub Pages (repo name)
  //basePath: '/hadiscover',
  turbopack: {
    root: path.resolve(__dirname),
  },
};

export default nextConfig;
