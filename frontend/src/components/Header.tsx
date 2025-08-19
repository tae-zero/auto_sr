'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/domain/auth/store/auth.store';

export default function Header() {
  const { isAuthenticated, isInitialized, user, logout, checkAuthStatus } = useAuthStore();

  // 컴포넌트 마운트 시 인증 상태 확인
  useEffect(() => {
    if (!isInitialized) {
      checkAuthStatus();
    }
  }, [isInitialized, checkAuthStatus]);

  const handleLogout = async () => {
    try {
      await logout();
      // 로그아웃 후 메인 페이지로 이동
      window.location.href = '/';
    } catch (error) {
      console.error('로그아웃 중 오류:', error);
    }
  };

  return (
    <nav className="absolute top-0 left-0 right-0 z-50 bg-transparent">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* 왼쪽 여백 */}
          <div className="flex items-center">
          </div>
          
          {/* 중앙 로고 */}
          <div className="flex-1 flex justify-center">
            <h1 className="text-white text-xl font-medium">정태영의 인생사</h1>
          </div>
          
          {/* 우측 메뉴 */}
          <div className="flex items-center space-x-6">
            {isInitialized && isAuthenticated && user ? (
              <>
                {/* 사용자 이름 표시 */}
                <div className="text-white text-sm font-medium">
                  {(() => {
                    console.log('🔍 User data:', user);
                    console.log('🔍 user.name:', user.name);
                    console.log('🔍 user.username:', user.username);
                    return user.name && user.name !== 'N/A' && user.name.trim() !== '' ? `${user.name}님 환영합니다.` : `${user.username}님 환영합니다.`;
                  })()}
                </div>
                {/* 로그아웃 버튼 */}
                <button
                  onClick={handleLogout}
                  className="text-white hover:text-gray-300 text-sm font-medium bg-red-600 hover:bg-red-700 px-3 py-1 rounded transition-colors duration-200"
                >
                  로그아웃
                </button>
              </>
            ) : (
              <>
                <Link href="/login" className="text-white hover:text-gray-300 text-sm font-medium">
                  LOGIN
                </Link>
                <Link href="/signup" className="text-white hover:text-gray-300 text-sm font-medium">
                  SIGNUP
                </Link>
              </>
            )}

          </div>
        </div>
      </div>
      

    </nav>
  );
}
