'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Header } from '@/ui/organisms';

export default function Home() {
  const portfolioItems = [
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M20 18c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v10c0 1.1.9 2 2 2H1c-.6 0-1 .4-1 1s.4 1 1 1h22c.6 0 1-.4 1-1s-.4-1-1-1h-3zM4 6h16v10H4V6z"/>
        </svg>
      ),
      title: "who am i?",
      description: "자기소개"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "재무대시보드",
      description: "유가증권시장 대시보드"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
        </svg>
      ),
      title: "ESG 공시 챗봇",
      description: "GRI, TCFD, KSSB, IFRS 기준 공시 챗봇"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "Climate",
      description: "Climate gallery"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "TCFD SR",
      description: "AI"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "My Gallery",
      description: "My Photo Gallery"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "GRI",
      description: "GRI INDEX"
    },
    {
      icon: (
        <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 24 24">
          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
        </svg>
      ),
      title: "Materiality",
      description: "Materiality INDEX"
    }
  ];

  return (
    <div className="min-h-screen bg-white">
      {/* 네비게이션 */}
      <Header />

      {/* 히어로 섹션 - 자연 풍경 이미지 배경 */}
      <section className="relative h-screen flex items-center justify-center overflow-hidden">
        {/* 배경 이미지 */}
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: 'url(/bailey-zindel-NRQV-hBF10M-unsplash.jpg)'
          }}
        ></div>
        
        {/* 어두운 오버레이로 텍스트 가독성 향상 */}
        <div className="absolute inset-0 bg-black bg-opacity-40"></div>
        
                 {/* 텍스트 오버레이 */}
         <div className="relative z-10 text-center text-white px-4 flex items-center justify-center h-full">
           <h1 className="text-4xl md:text-6xl font-bold leading-tight drop-shadow-lg">
             TAEZERO
           </h1>
         </div>
      </section>

      {/* 포트폴리오 섹션 */}
      <section className="py-20 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                     <div className="text-center mb-16 flex flex-col items-center justify-center">
             <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4 text-center leading-relaxed">
               자연으로 돌아가라<br/>
               하고자 하는 일에 후회하지 않도록 최선을 다하자
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
                <p className="text-gray-600 text-sm leading-relaxed mb-6 text-center">
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
                   ) : item.title === "WHO AM I" ? (
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
                   ) : item.title === "Materiality" ? (
                     <Link href="/materiality">
                       <button 
                         onClick={() => {
                           console.log('=== Materiality MORE 버튼 클릭됨 ===');
                           console.log('현재 페이지:', window.location.href);
                           console.log('이동할 페이지: /materiality');
                         }}
                         className="border-2 border-blue-400 text-blue-600 hover:bg-blue-400 hover:text-white px-6 py-2 rounded-lg transition-colors duration-200 font-medium"
                       >
                         MORE
                       </button>
                     </Link>
                   ) : item.title === "나한테 사진 찍힐래?" ? (
                      <Link href="/photo-gallery">
                        <button 
                          className="border-2 border-purple-400 text-purple-600 hover:bg-purple-400 hover:text-white px-6 py-2 rounded-lg transition-colors duration-200 font-medium"
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
              <h3 className="text-xl font-bold mb-4">TAEZERO</h3>
              <p className="text-gray-400">
                TAEZERO PORTFOLIO
              </p>
            </div>
            <div>
              <h4 className="font-semibold mb-4">로그인</h4>
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
