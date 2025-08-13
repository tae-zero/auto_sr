import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Docker 배포를 위한 standalone 출력 제거 (SWC 문제 해결)
  // output: 'standalone',
  
  env: {
    PORT: process.env.PORT || '3000',
    NEXT_PUBLIC_GATEWAY_URL: 'http://localhost:8080',
    NEXT_PUBLIC_TCFD_SERVICE_URL: 'http://localhost:8005',
    NEXT_PUBLIC_AUTH_SERVICE_URL: 'http://localhost:8008',
    NEXT_PUBLIC_API_URL: 'http://localhost:8080/api',
  },
  
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
