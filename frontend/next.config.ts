import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    serverActions: {},
  },
  images: {
    domains: ['localhost', '127.0.0.1'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
    NEXT_PUBLIC_BASE_URL: process.env.NEXT_PUBLIC_BASE_URL || 'http://localhost:3000',
  },
};

export default nextConfig;
