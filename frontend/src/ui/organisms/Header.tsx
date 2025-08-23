'use client';

import { useEffect } from 'react';
import Link from 'next/link';
import { useAuthStore } from '@/shared/state/auth.store';

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
    <nav className="absolute top-0 left-0 right-0 z-50 w-full">
      <div className="w-full h-16 bg-white shadow-md flex justify-between items-center px-4 sm:px-6 lg:px-8">
        {/* 왼쪽 여백 */}
        <div className="flex items-center">
        </div>
        
        {/* 중앙 로고 - 초록색 박스 */}
        <div className="absolute left-1/2 transform -translate-x-1/2">
          <div className="bg-green-500 px-6 py-2 rounded-lg shadow-sm">
            <h1 className="text-white text-xl font-bold">TAEZERO</h1>
          </div>
        </div>
        
        {/* 우측 메뉴 - 회색 박스 */}
        <div className="flex items-center space-x-4">
          {isInitialized && isAuthenticated && user ? (
            <>
              {/* 사용자 이름 표시 */}
              <div className="bg-gray-200 px-4 py-2 rounded-lg">
                <span className="text-black text-sm font-medium">
                  {(() => {
                    console.log('🔍 User data:', user);
                    console.log('🔍 user.name:', user.name);
                    console.log('🔍 user.username:', user.username);
                    return user.name && user.name !== 'N/A' && user.name.trim() !== '' ? `${user.name}님 환영합니다.` : `${user.username}님 환영합니다.`;
                  })()}
                </span>
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
              <div className="bg-gray-200 px-4 py-2 rounded-lg">
                <Link href="/login" className="text-black hover:text-gray-600 text-sm font-medium">
                  LOGIN
                </Link>
              </div>
              <div className="bg-gray-200 px-4 py-2 rounded-lg">
                <Link href="/signup" className="text-black hover:text-gray-600 text-sm font-medium">
                  SIGNUP
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
