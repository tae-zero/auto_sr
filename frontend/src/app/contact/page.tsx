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
            
          </div>

          {/* 주소 */}
          <div className="bg-white rounded-xl shadow-lg p-8 text-center transform hover:scale-105 transition-transform duration-300">
            <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <span className="text-3xl">📍</span>
            </div>
            <h3 className="text-xl font-semibold text-gray-900 mb-4">주소</h3>
            <p className="text-purple-600 font-medium text-lg">
              서울특별시 중랑구 면목동
            </p>
            
          </div>
        </div>

                 {/* 프로필 정보 */}
         <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
           <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">💼 프로필</h2>
           <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
             <div className="text-center">
               <h3 className="text-lg font-semibold text-gray-800 mb-2">이름</h3>
               <p className="text-gray-600">정태영</p>
               <p className="text-gray-600">Jeong Tae-young</p>
               
             </div>
             <div className="text-center">
               <h3 className="text-lg font-semibold text-gray-800 mb-2">직업</h3>
               <p className="text-gray-600">개발자, 데이터 분석가, 기후 전문가</p>
             </div>
             <div className="text-center">
               <h3 className="text-lg font-semibold text-gray-800 mb-2">관심 분야</h3>
               <p className="text-gray-600">ESG, 기상, 기후변화, AI</p>
             </div>
             <div className="text-center">
               <h3 className="text-lg font-semibold text-gray-800 mb-2">좌우명</h3>
               <p className="text-gray-600">&ldquo;안되면 되게하라&rdquo;</p>
               <p className="text-gray-600">&ldquo;하고자 하는 일에 후회하지 않도록 최선을 다하자&rdquo;</p>
             </div>
           </div>
         </div>

         {/* 학력 정보 */}
         <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
           <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">🎓 학력</h2>
           <div className="text-center">
             <h3 className="text-lg font-semibold text-gray-800 mb-2"></h3>
             <p className="text-gray-600 text-lg">2008~2012 해남동초등학교 </p>
             <p className="text-gray-600 text-lg">2013~2015 해남제일중학교 </p>
             <p className="text-gray-600 text-lg">2016~2018 해남고등학교 </p>
             <p className="text-gray-600 text-lg">2019~ 건국대학교 지리학과 학부생 </p>
           </div>
         </div>

         {/* 거주지 정보 */}
         <div className="bg-white rounded-xl shadow-lg p-8 mb-12">
           <h2 className="text-2xl font-bold text-gray-900 mb-6 text-center">🏠 출생</h2>
           <div className="text-center">
             <h3 className="text-lg font-semibold text-gray-800 mb-2"></h3>
             <p className="text-gray-600 text-lg">2000.03.08 전라남도 해남군 출생</p>
             <p className="text-gray-600 text-lg">2022.02~2025.06 서울특별시 광진구 화양동 거주</p>
             <p className="text-gray-600 text-lg">2025.07~ 서울특별시 중랑구 면목동 거주</p>
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
