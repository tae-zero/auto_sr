import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Docker 배포를 위한 standalone 출력
  output: 'standalone',
  
  env: {
    PORT: process.env.PORT || '3000',
  },
  
  // SWC 비활성화 (Docker 환경에서 문제 해결)
  swcMinify: false,
  
  // Vercel 최적화 설정
  experimental: {
    optimizePackageImports: ['@vercel/analytics']
  },
  
  // Docker 환경 최적화
  poweredByHeader: false,
  compress: true,
  
  // 이미지 최적화 설정
  images: {
    unoptimized: true
  }
};

export default nextConfig;
