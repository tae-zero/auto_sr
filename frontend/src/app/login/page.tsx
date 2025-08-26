'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/shared/state';
import { Header } from '@/ui/organisms';
import axios, { AxiosError } from 'axios';
import { authAPI } from '@/shared/lib';

// URL 유효성 검사 함수


export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isInitialized, checkAuthStatus } = useAuthStore();

  // Form state management
  const [formData, setFormData] = useState({
    auth_id: '',
    auth_pw: ''
  });

  // Check authentication status on component mount
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  // Redirect authenticated users to main page
  useEffect(() => {
    if (isAuthenticated && isInitialized) {
      router.push('/');
    }
  }, [isAuthenticated, isInitialized, router]);

  // Form input handler
  const handleInputChange = (userData: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = userData.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Login form submission
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const response = await authAPI.login(formData);
      console.log('Login response:', response.data);
      
      if (!response.data.success) {
        alert(`❌ ${response.data.message || '로그인에 실패했습니다.'}`);
        return;
      }

      const { token, name = 'N/A', email = 'N/A', company_id = 'N/A' } = response.data;
      
      if (!token) {
        console.error('No token in response');
        alert('❌ 토큰이 없습니다.');
        return;
      }
      
      // 토큰과 사용자 정보를 auth store에 저장
      const userData = {
        username: formData.auth_id,
        email: email,
        name: name,
        company_id: company_id
      };
      
      // auth store의 login 함수 호출하여 사용자 정보와 토큰 저장
      useAuthStore.getState().login(formData.auth_id, userData, token);
      
      alert(`✅ 로그인 성공\n\n이름: ${name}\n이메일: ${email}\n회사 ID: ${company_id}`);
      // 로그인 성공 후 메인페이지로 이동
      router.push('/');
    } catch (error) {
      console.error('Login failed:', error);
      
      if (axios.isAxiosError(error)) {
        const axiosError = error as AxiosError<{ message?: string; detail?: string }>;
        if (axiosError.response?.data) {
          alert(`❌ 로그인 실패: ${axiosError.response.data.message || axiosError.response.data.detail || '알 수 없는 오류'}`);
        } else {
          alert('❌ 로그인에 실패했습니다. 서버 연결을 확인해주세요.');
        }
      } else {
        alert('❌ 로그인에 실패했습니다. 서버 연결을 확인해주세요.');
      }
    }
  };

  // Show loading while checking authentication status
  if (!isInitialized) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  // Show login screen for unauthenticated users
  if (!isAuthenticated && isInitialized) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200">
        <Header />
        <div className="flex items-center justify-center min-h-screen pt-16">
          <div className="w-full max-w-6xl mx-4">
            <div className="bg-white rounded-3xl shadow-2xl overflow-hidden">
              <div className="flex">
                {/* Left Side - Background Image */}
                <div className="hidden lg:block lg:w-1/2 relative">
                  <div 
                    className="h-full w-full bg-cover bg-center bg-no-repeat"
                    style={{
                      backgroundImage: 'url(/markus-spiske-GnxktpZHjcM-unsplash.jpg)'
                    }}
                  >
                    {/* Dark overlay for better text readability */}
                    <div className="absolute inset-0 bg-black bg-opacity-30"></div>
                    {/* Optional text overlay */}
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center text-white">
                        <h2 className="text-4xl font-bold mb-4">Welcome Back</h2>
                        <p className="text-xl opacity-90">Sign in to continue your journey</p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Right Side - Login Form */}
                <div className="w-full lg:w-1/2 p-8 lg:p-12">
                  {/* Login Title */}
                  <div className="text-center mb-12">
                    <h1 className="text-5xl font-bold text-gray-900 tracking-tight">
                      Login
                    </h1>
                  </div>

                  {/* Login Form */}
                  <div className="space-y-8">
                    {/* Auth ID Input */}
                    <div className="relative">
                      <input
                        type="text"
                        name="auth_id"
                        value={formData.auth_id}
                        onChange={handleInputChange}
                        placeholder="인증 ID"
                        className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                        required
                      />
                    </div>

                    {/* Auth Password Input */}
                    <div className="relative">
                      <input
                        type="password"
                        name="auth_pw"
                        value={formData.auth_pw}
                        onChange={handleInputChange}
                        placeholder="인증 비밀번호"
                        className="w-full px-0 py-4 text-lg text-gray-800 placeholder-gray-400 bg-transparent border-0 border-b-2 border-gray-200 focus:border-blue-500 focus:outline-none transition-all duration-300"
                        required
                      />
                    </div>

                    {/* Find ID/Password Links */}
                    <div className="text-center py-6">
                      <div className="text-sm text-gray-500 space-x-1">
                        <a href="/find-id" className="hover:text-blue-600 transition-colors duration-200">
                          Find ID
                        </a>
                        <span className="mx-3 text-gray-300">|</span>
                        <a href="/find-password" className="hover:text-blue-600 transition-colors duration-200">
                          Find Password
                        </a>
                      </div>
                    </div>
                    
                    {/* Login Button */}
                    <button
                      type="submit"
                      onClick={handleLogin}
                      className="w-full bg-blue-600 text-white py-4 rounded-2xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm"
                    >
                      Login
                    </button>

                    {/* Sign Up Button */}
                    <button
                      type="button"
                      onClick={() => {
                        router.push('/signup');
                      }}
                      className="w-full bg-white border-2 border-gray-300 text-gray-800 py-4 rounded-2xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-medium text-lg shadow-sm"
                    >
                      Sign Up
                    </button>
                    

                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
}