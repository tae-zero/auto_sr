'use client';

import Link from 'next/link';

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-16">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* 헤더 */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            📞 연락처 정보
          </h1>
          <p className="text-xl text-gray-600">
            정태영과 연락하실 수 있는 방법들입니다
          </p>
        </div>

        {/* 연락처 카드들 */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-12">
          {/* 이메일 */}
          <div className="bg-white rounded-xl shadow-lg p-8 text-center transform hover:scale-105 transition-transform duration-300">
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-3xl">📧</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">이메일</h3>
            <p className="text-blue-600 font-medium text-lg break-all">
              jty000308@naver.com
            </p>
            <a 
              href="mailto:jty000308@naver.com" 
              className="inline-block mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              메일 보내기
            </a>
          </div>

          {/* 전화번호 */}
          <div className="bg-white rounded-xl shadow-lg p-8 text-center transform hover:scale-105 transition-transform duration-300">
            <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-3xl">📱</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">전화번호</h3>
            <p className="text-green-600 font-medium text-lg">
              010-3880-8322
            </p>
            <a 
              href="tel:010-3880-8322" 
              className="inline-block mt-4 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
            >
              전화 걸기
            </a>
          </div>

          {/* 주소 */}
          <div className="bg-white rounded-xl shadow-lg p-8 text-center transform hover:scale-105 transition-transform duration-300">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-3xl">📍</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">주소</h3>
            <p className="text-purple-600 font-medium text-lg">
              서울특별시
            </p>
            <button 
              className="inline-block mt-4 px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
              onClick={() => alert('서울특별시에 위치하고 있습니다!')}
            >
              위치 확인
            </button>
          </div>
        </div>

        {/* 추가 정보 */}
        <div className="bg-white rounded-xl shadow-lg p-8 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">💼 프로필</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">이름</h3>
              <p className="text-gray-600">정태영</p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">직업</h3>
              <p className="text-gray-600">개발자</p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">관심 분야</h3>
              <p className="text-gray-600">TCFD, ESG, 지속가능성</p>
            </div>
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-800 mb-2">좌우명</h3>
              <p className="text-gray-600">"안되면 되게하라"</p>
            </div>
          </div>
        </div>

        {/* 돌아가기 버튼 */}
        <div className="text-center">
          <Link 
            href="/"
            className="inline-flex items-center px-8 py-3 bg-gray-800 text-white rounded-lg hover:bg-gray-900 transition-colors text-lg font-medium"
          >
            <span className="mr-2">←</span>
            메인으로 돌아가기
          </Link>
        </div>
      </div>
    </div>
  );
}
