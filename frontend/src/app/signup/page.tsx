'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import axios from 'axios';

export default function SignupPage() {
  const router = useRouter();

  // Form state management
  const [formData, setFormData] = useState({
    user_id: '',
    name: '',
    email: '',
    phone: '',
    gender: '',
    birthdate: '',
    address: ''
  });

  // Form input handler
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Signup form submission
  const handleSignup = (e: React.FormEvent) => {
    e.preventDefault();
    
    // 입력된 데이터를 JSON 형태로 alert에 표시
    const signupData = {
      "회원가입 정보": {
        "사용자 ID": formData.user_id,
        "이름": formData.name,
        "이메일": formData.email,
        "전화번호": formData.phone,
        "성별": formData.gender,
        "생년월일": formData.birthdate,
        "주소": formData.address
      }
    };
    
    // JSON을 보기 좋게 포맷팅하여 alert에 표시
    alert(JSON.stringify(signupData, null, 2));
    
    // TODO: Send signup data to backend
    axios.post('http://localhost:8080/signup', formData)
      .then(response => {
        console.log('Signup successful:', response.data);
        alert('회원가입이 완료되었습니다!');
        router.push('/login');
      })
      .catch(error => {
        console.error('Signup failed:', error);
        alert('회원가입에 실패했습니다.');
      });
  };

  // Go back to login page
  const handleBackToLogin = () => {
    router.push('/login');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-3xl shadow-2xl px-8 py-12">
          {/* Signup Title */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 tracking-tight">
              Sign Up
            </h1>
            <p className="text-gray-600 mt-2">회원가입을 진행해주세요</p>
          </div>

          {/* Signup Form */}
          <form onSubmit={handleSignup} className="space-y-6">
            {/* User ID Input */}
            <div className="relative">
              <input
                type="text"
                name="user_id"
                value={formData.user_id}
                onChange={handleInputChange}
                placeholder="User ID"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Name Input */}
            <div className="relative">
              <input
                type="text"
                name="name"
                value={formData.name}
                onChange={handleInputChange}
                placeholder="이름"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Email Input */}
            <div className="relative">
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleInputChange}
                placeholder="이메일"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Phone Input */}
            <div className="relative">
              <input
                type="tel"
                name="phone"
                value={formData.phone}
                onChange={handleInputChange}
                placeholder="전화번호 (예: 010-1234-5678)"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Gender Select */}
            <div className="relative">
              <select
                name="gender"
                value={formData.gender}
                onChange={handleInputChange}
                className="w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              >
                <option value="">성별을 선택하세요</option>
                <option value="male">남성</option>
                <option value="female">여성</option>
                <option value="other">기타</option>
              </select>
            </div>

            {/* Birthdate Input */}
            <div className="relative">
              <input
                type="date"
                name="birthdate"
                value={formData.birthdate}
                onChange={handleInputChange}
                className="w-full px-4 py-3 text-gray-800 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Address Input */}
            <div className="relative">
              <input
                type="text"
                name="address"
                value={formData.address}
                onChange={handleInputChange}
                placeholder="주소"
                className="w-full px-4 py-3 text-gray-800 placeholder-gray-400 bg-gray-50 border border-gray-200 rounded-xl focus:border-blue-500 focus:outline-none transition-all duration-300"
                required
              />
            </div>

            {/* Buttons */}
            <div className="space-y-4 pt-4">
              {/* Sign Up Button */}
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 rounded-xl hover:bg-blue-700 transition-all duration-200 font-medium text-lg shadow-sm"
              >
                회원가입
              </button>

              {/* Back to Login Button */}
              <button
                type="button"
                onClick={handleBackToLogin}
                className="w-full bg-white border-2 border-gray-300 text-gray-800 py-3 rounded-xl hover:bg-gray-50 hover:border-gray-400 transition-all duration-200 font-medium text-lg shadow-sm"
              >
                로그인으로 돌아가기
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
