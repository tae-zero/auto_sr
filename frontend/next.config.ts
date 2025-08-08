import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Vercel에서는 output: 'standalone'이 필요하지 않음
  env: {
    PORT: process.env.PORT || '3000',
  },
  // SWC 비활성화 (Docker 환경에서 문제 해결)
  swcMinify: false,
  // Vercel 최적화 설정
  experimental: {
    optimizePackageImports: ['@vercel/analytics']
  }
};

export default nextConfig;
