'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Header from '@/components/Header';

export default function Home() {
  const [stars, setStars] = useState<Array<{left: string, top: string, delay: string, duration: string}>>([]);

  const portfolioItems = [
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20 18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H1c-.6 0-1 .4-1 1s.4 1 1 1h22c.6 0 1-.4 1-1s-.4-1-1-1h-3zM4 6h16v10H4V6z"/>
        </svg>
      ),
      title: "who am i?",
      description: "나는 태영이야"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "재무대시보드",
      description: "유가증권시장 내역을 나랑 살펴볼래? ㅋㅋ"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
      ),
      title: "esg 공시 챗봇",
      description: "esg 공시가 헷갈려?"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "지구가 아파한대!!",
      description: "우리나라가 어떻게 변해가는지 알아볼까?"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "TCFD 기준으로 SR작성해볼까?",
      description: "SR을 ai와 함께 작성해보기"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "나한테 사진 찍힐래?",
      description: "사진찍는거 좋아하는데 내 필름으로 들어올래?"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "GRI",
      description: "GRI 기준으로 지속가능성 보고서 작성해볼까?"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "Materiality",
      description: "Materiality 분석으로 핵심 이슈를 파악해볼까?"
    }
  ];

  // 별들 생성 (클라이언트에서만 실행)
  useEffect(() => {
    const newStars = Array.from({ length: 50 }, () => ({
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      delay: `${Math.random() * 3}s`,
      duration: `${2 + Math.random() * 2}s`
    }));
    setStars(newStars);
  }, []);

  return (
    <div className="min-h-screen bg-white">
      {/* 네비게이션 */}
      <Header />

      {/* 히어로 섹션 - 밤하늘 배경 */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* 배경 그라데이션 */}
        <div className="absolute inset-0 bg-gradient-to-b from-teal-900 via-teal-800 to-teal-700"></div>
        
        {/* 별들 */}
        <div className="absolute inset-0">
          {stars.map((star, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-white rounded-full animate-pulse"
              style={{
                left: star.left,
                top: star.top,
                animationDelay: star.delay,
                animationDuration: star.duration
              }}
            ></div>
          ))}
        </div>
        
        {/* 달 */}
        <div className="absolute top-20 left-20 w-16 h-16 bg-white rounded-full opacity-80">
          <div className="absolute top-2 left-2 w-12 h-12 bg-teal-900 rounded-full"></div>
        </div>
        
        {/* 산들 */}
        <div className="absolute bottom-0 left-0 right-0">
          <div className="relative h-64">
            {/* 첫 번째 산 */}
            <div className="absolute bottom-0 left-0 w-0 h-0 border-l-[200px] border-r-[200px] border-b-[120px] border-l-transparent border-r-transparent border-b-gray-300"></div>
            {/* 두 번째 산 */}
            <div className="absolute bottom-0 left-1/4 w-0 h-0 border-l-[150px] border-r-[150px] border-b-[100px] border-l-transparent border-r-transparent border-b-gray-400"></div>
            {/* 세 번째 산 */}
            <div className="absolute bottom-0 right-1/4 w-0 h-0 border-l-[180px] border-r-[180px] border-b-[110px] border-l-transparent border-r-transparent border-b-gray-300"></div>
            {/* 네 번째 산 */}
            <div className="absolute bottom-0 right-0 w-0 h-0 border-l-[160px] border-r-[160px] border-b-[90px] border-l-transparent border-r-transparent border-b-gray-400"></div>
          </div>
        </div>
        
        {/* 새들 */}
        <div className="absolute top-1/3 right-1/4">
          {[...Array(3)].map((_, i) => (
            <div
              key={i}
              className="absolute text-white opacity-80 animate-bounce"
              style={{
                left: `${i * 20}px`,
                top: `${i * 10}px`,
                animationDelay: `${i * 0.5}s`
              }}
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                <path d="M12 2L9 9H2l5.5 4L5 20l7-5 7 5-2.5-7L22 9h-7l-3-7z"/>
              </svg>
            </div>
          ))}
        </div>
        
        {/* 텍스트 오버레이 */}
        <div className="relative z-10 text-center text-white px-4">
          <h1 className="text-5xl md:text-7xl font-bold mb-6 leading-tight">
          안되면 되게하라<br />
            하고자 하는 일에 후회하지 않도록 최선을 다하자
          </h1>

        </div>
      </section>

      {/* 포트폴리오 섹션 */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
              I am a positive person.
            </h2>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {portfolioItems.map((item, index) => (
              <div key={index} className="bg-gray-100 rounded-lg p-8 shadow-lg transform hover:scale-105 transition-transform duration-300">
                <div className="text-center mb-6">
                  <div className="text-gray-600 mb-4">
                    {item.icon}
                  </div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-4">
                    {item.title}
                  </h3>
                </div>
                <p className="text-gray-600 text-sm leading-relaxed mb-6">
                  {item.description}
                </p>
                                 <div className="text-center">
                   {item.title === "TCFD 기준으로 SR작성해볼까?" ? (
                     <Link href="/tcfd">
                       <button 
                         className="border-2 border-blue-400 text-blue-600 hover:bg-blue-400 hover:text-white px-6 py-2 rounded-lg transition-colors duration-200 font-medium"
                       >
                         MORE
                       </button>
                     </Link>
                   ) : item.title === "who am i?" ? (
                     <Link href="/contact">
                       <button 
                         className="border-2 border-blue-400 text-blue-600 hover:bg-blue-400 hover:text-white px-6 py-2 rounded-lg transition-transform duration-200 font-medium"
                       >
                         MORE
                       </button>
                     </Link>
                   ) : item.title === "지구가 아파한대!!" ? (
                     <Link href="/climate-scenarios">
                       <button 
                         className="border-2 border-green-400 text-green-600 hover:bg-green-400 hover:text-white px-6 py-2 rounded-lg transition-colors duration-200 font-medium"
                       >
                         MORE
                       </button>
                     </Link>
                   ) : item.title === "재무대시보드" ? (
                     <button 
                       onClick={() => window.open('https://finance-dashboard-git-main-jeongtaeyeongs-projects.vercel.app', '_blank')}
                       className="border-2 border-blue-400 text-blue-600 hover:bg-blue-400 hover:text-white px-6 py-2 rounded-lg transition-colors duration-200 font-medium"
                     >
                       MORE
                     </button>
                   ) : (
                     <button className="border-2 border-blue-400 text-blue-600 hover:bg-blue-400 hover:text-white px-6 py-2 rounded-lg transition-colors duration-200 font-medium">
                       MORE
                     </button>
                   )}
                 </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      

      {/* 푸터 */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">정태영의 인생사</h3>
              <p className="text-gray-400">
                정태영의 꿈과 희망이 가득찬 이곳
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">서비스</h4>
              <ul className="space-y-2 text-gray-400">
                <li><Link href="/login" className="hover:text-white">로그인</Link></li>
                <li><Link href="/signup" className="hover:text-white">회원가입</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-4">연락처</h4>
              <ul className="space-y-2 text-gray-400">
                <li>jty000308@naver.com</li>
                <li>010-3880-8322</li>
                <li>서울특별시</li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 Portfolio. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}
