'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';

// 재무정보 타입 정의 (Frontend용)
interface FinancialData {
  revenue: number;
  total_assets: number;
  total_liabilities: number;
  total_equity: number;
  operating_income?: number;
  net_income?: number;
  fiscal_year: string;
  company_id: string;
}

export default function TcfdSrPage() {
  const [activeTab, setActiveTab] = useState(1);
  const [financialData, setFinancialData] = useState<FinancialData | null>(null);
  const [isLoadingFinancial, setIsLoadingFinancial] = useState(false);
  const [financialError, setFinancialError] = useState<string | null>(null);
  const [showFinancialAnalysis, setShowFinancialAnalysis] = useState(false);

  // 재무정보 로드 함수 - Gateway를 통해 TCFD Service 호출
  const loadFinancialData = async () => {
    setIsLoadingFinancial(true);
    setFinancialError(null);
    
    try {
      // Gateway를 통해 TCFD Service의 재무정보 API 호출
      const response = await fetch('/api/financial-data', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('재무정보를 불러오는데 실패했습니다.');
      }

      const data = await response.json();
      setFinancialData(data);
    } catch (error) {
      console.error('재무정보 로드 오류:', error);
      setFinancialError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.');
    } finally {
      setIsLoadingFinancial(false);
    }
  };

  // 재무정보 저장 함수 - Gateway를 통해 TCFD Service 호출
  const saveFinancialData = async (data: Partial<FinancialData>) => {
    try {
      const response = await fetch('/api/financial-data', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error('재무정보 저장에 실패했습니다.');
      }

      // 저장 후 데이터 다시 로드
      await loadFinancialData();
      return true;
    } catch (error) {
      console.error('재무정보 저장 오류:', error);
      setFinancialError(error instanceof Error ? error.message : '알 수 없는 오류가 발생했습니다.');
      return false;
    }
  };

  // 재무지표 분석 표시
  const handleFinancialAnalysis = () => {
    if (financialData) {
      setShowFinancialAnalysis(true);
    }
  };

  // 재무정보 탭이 활성화될 때 데이터 로드
  useEffect(() => {
    if (activeTab === 2) {
      loadFinancialData();
    }
  }, [activeTab]);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 네비게이션 */}
      <nav className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <Link href="/" className="text-gray-600 hover:text-gray-900">
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </Link>
              <h1 className="ml-4 text-xl font-semibold text-gray-900">TCFD 기준 SR 작성</h1>
            </div>
            <div className="flex items-center space-x-4">
              <Link href="/login" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                LOGIN
              </Link>
              <Link href="/signup" className="text-gray-600 hover:text-gray-900 text-sm font-medium">
                SIGNUP
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* 메인 컨텐츠 */}
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* 헤더 섹션 */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 mb-8 text-white">
          <h1 className="text-3xl font-bold mb-4">TCFD 기준 지속가능보고서 작성</h1>
          <p className="text-blue-100 text-lg">
            AI와 함께 기후 관련 재무정보공개 태스크포스(TCFD) 기준으로 SR을 작성해보세요
          </p>
        </div>

        {/* 탭 네비게이션 */}
        <div className="bg-white rounded-xl shadow-sm border mb-8 overflow-x-auto">
          <div className="flex min-w-max">
            {[
              { number: 1, name: '회사정보' },
              { number: 2, name: '재무정보' },
              { number: 3, name: 'TCFD 프레임워크' },
              { number: 4, name: '기후시나리오' },
              { number: 5, name: 'AI보고서 초안' }
            ].map((tab) => (
              <button
                key={tab.number}
                onClick={() => setActiveTab(tab.number)}
                className={`px-6 py-4 text-center font-medium transition-colors rounded-t-xl whitespace-nowrap ${
                  activeTab === tab.number
                    ? 'text-blue-600 border-b-2 border-blue-600 bg-blue-50'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                }`}
              >
                {tab.name}
              </button>
            ))}
          </div>
        </div>

        {/* 탭 컨텐츠 */}
        <div className="bg-white rounded-xl shadow-sm border p-8">
          {activeTab === 1 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">회사정보</h3>
                <p className="text-gray-600 mb-6">
                  TCFD 기준으로 SR을 작성하기 위한 기본 회사 정보를 입력하세요.
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">회사명 *</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="회사명을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">업종 *</label>
                  <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option value="">업종을 선택하세요</option>
                    <option value="manufacturing">제조업</option>
                    <option value="finance">금융업</option>
                    <option value="energy">에너지업</option>
                    <option value="technology">기술업</option>
                    <option value="retail">소매업</option>
                    <option value="other">기타</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">설립연도</label>
                  <input
                    type="number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="예: 1990"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">직원 수</label>
                  <select className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <option value="">직원 수를 선택하세요</option>
                    <option value="1-50">1-50명</option>
                    <option value="51-200">51-200명</option>
                    <option value="201-1000">201-1000명</option>
                    <option value="1001-5000">1001-5000명</option>
                    <option value="5000+">5000명 이상</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">대표자명</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="대표자명을 입력하세요"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">주소</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="회사 주소를 입력하세요"
                  />
                </div>
              </div>

              <div className="pt-4">
                <button 
                  onClick={() => setActiveTab(2)}
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  다음 단계 →
                </button>
              </div>
            </div>
          )}

          {activeTab === 2 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">재무정보</h3>
                <p className="text-gray-600 mb-6">
                  기후 관련 위험과 기회가 재무에 미치는 영향을 분석하기 위한 재무 정보를 입력하세요.
                </p>
              </div>

              {/* Railway DB 연동 상태 표시 */}
              <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${isLoadingFinancial ? 'bg-yellow-500 animate-pulse' : financialData ? 'bg-green-500' : 'bg-gray-400'}`}></div>
                    <span className="text-sm text-blue-700">
                      {isLoadingFinancial ? '데이터 로딩 중...' : financialData ? 'TCFD Service 연결됨' : '서비스 연결 대기 중'}
                    </span>
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={loadFinancialData}
                      disabled={isLoadingFinancial}
                      className="px-3 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      새로고침
                    </button>
                    {financialData && (
                      <span className="px-2 py-1 text-xs bg-green-100 text-green-800 rounded">
                        {financialData.fiscal_year}년 데이터
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* 오류 메시지 */}
              {financialError && (
                <div className="bg-red-50 p-4 rounded-lg border border-red-200">
                  <div className="flex items-center space-x-2">
                    <svg className="w-5 h-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                    </svg>
                    <span className="text-red-700 text-sm">{financialError}</span>
                  </div>
                </div>
              )}
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">매출액 (백만원) *</label>
                  <input
                    type="number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="연간 매출액을 입력하세요"
                    value={financialData?.revenue || ''}
                    onChange={(e) => setFinancialData(prev => prev ? {...prev, revenue: Number(e.target.value)} : null)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">자산총액 (백만원) *</label>
                  <input
                    type="number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="자산총액을 입력하세요"
                    value={financialData?.total_assets || ''}
                    onChange={(e) => setFinancialData(prev => prev ? {...prev, total_assets: Number(e.target.value)} : null)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">부채총액 (백만원) *</label>
                  <input
                    type="number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="부채총액을 입력하세요"
                    value={financialData?.total_liabilities || ''}
                    onChange={(e) => setFinancialData(prev => prev ? {...prev, total_liabilities: Number(e.target.value)} : null)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">자본총액 (백만원) *</label>
                  <input
                    type="number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="자본총액을 입력하세요"
                    value={financialData?.total_equity || ''}
                    onChange={(e) => setFinancialData(prev => prev ? {...prev, total_equity: Number(e.target.value)} : null)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">영업이익 (백만원)</label>
                  <input
                    type="number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="영업이익을 입력하세요"
                    value={financialData?.operating_income || ''}
                    onChange={(e) => setFinancialData(prev => prev ? {...prev, operating_income: Number(e.target.value)} : null)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">당기순이익 (백만원)</label>
                  <input
                    type="number"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="당기순이익을 입력하세요"
                    value={financialData?.net_income || ''}
                    onChange={(e) => setFinancialData(prev => prev ? {...prev, net_income: Number(e.target.value)} : null)}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">회계연도</label>
                  <input
                    type="text"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="예: 2024"
                    value={financialData?.fiscal_year || ''}
                    onChange={(e) => setFinancialData(prev => prev ? {...prev, fiscal_year: e.target.value} : null)}
                  />
                </div>
              </div>

              {/* 재무정보 저장/업데이트 버튼 */}
              <div className="bg-gray-50 p-4 rounded-lg border border-gray-200">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600">
                    TCFD Service를 통해 Railway DB에 재무정보를 저장하거나 업데이트할 수 있습니다.
                  </div>
                  <div className="flex space-x-2">
                    <button
                      onClick={() => financialData && saveFinancialData(financialData)}
                      disabled={!financialData || isLoadingFinancial}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {financialData ? '업데이트' : '저장'}
                    </button>
                    <button
                      onClick={() => setFinancialData(null)}
                      className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600"
                    >
                      초기화
                    </button>
                  </div>
                </div>
              </div>

              {/* 재무지표 분석 섹션 */}
              {financialData && (
                <div className="bg-gradient-to-r from-purple-50 to-blue-50 p-6 rounded-lg border border-purple-200">
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="text-lg font-semibold text-purple-900">재무지표 분석</h4>
                    <button
                      onClick={handleFinancialAnalysis}
                      className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                    >
                      {showFinancialAnalysis ? '분석 숨기기' : '재무지표 분석'}
                    </button>
                  </div>
                  
                  {showFinancialAnalysis && (
                    <div className="space-y-4">
                      {/* 기본 재무지표 */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-white p-3 rounded-lg border border-purple-200">
                          <div className="text-xs text-purple-600 font-medium">부채비율</div>
                          <div className="text-lg font-bold text-purple-900">
                            {((financialData.total_liabilities / financialData.total_equity) * 100).toFixed(1)}%
                          </div>
                        </div>
                        <div className="bg-white p-3 rounded-lg border border-purple-200">
                          <div className="text-xs text-purple-600 font-medium">자기자본비율</div>
                          <div className="text-lg font-bold text-purple-900">
                            {((financialData.total_equity / financialData.total_assets) * 100).toFixed(1)}%
                          </div>
                        </div>
                        {financialData.operating_income && (
                          <div className="bg-white p-3 rounded-lg border border-purple-200">
                            <div className="text-xs text-purple-600 font-medium">영업이익률</div>
                            <div className="text-lg font-bold text-purple-900">
                              {((financialData.operating_income / financialData.revenue) * 100).toFixed(1)}%
                            </div>
                          </div>
                        )}
                        {financialData.net_income && (
                          <div className="bg-white p-3 rounded-lg border border-purple-200">
                            <div className="text-xs text-purple-600 font-medium">순이익률</div>
                            <div className="text-lg font-bold text-purple-900">
                              {((financialData.net_income / financialData.revenue) * 100).toFixed(1)}%
                            </div>
                          </div>
                        )}
                      </div>

                      {/* TCFD 관점에서의 재무 위험 */}
                      <div className="bg-white p-4 rounded-lg border border-purple-200">
                        <h5 className="font-semibold text-purple-900 mb-3">TCFD 관점에서의 재무 위험</h5>
                        <div className="space-y-2 text-sm text-gray-700">
                          <div className="flex items-start space-x-2">
                            <div className="w-2 h-2 bg-red-400 rounded-full mt-2 flex-shrink-0"></div>
                            <span>기후 변화로 인한 매출 감소 위험: {financialData.revenue > 100000 ? '높음' : '보통'}</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <div className="w-2 h-2 bg-yellow-400 rounded-full mt-2 flex-shrink-0"></div>
                            <span>자산 가치 하락 위험: {financialData.total_assets > 500000 ? '높음' : '보통'}</span>
                          </div>
                          <div className="flex items-start space-x-2">
                            <div className="w-2 h-2 bg-green-400 rounded-full mt-2 flex-shrink-0"></div>
                            <span>재무 안정성: {financialData.total_equity / financialData.total_assets > 0.5 ? '양호' : '주의 필요'}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              <div className="pt-4 flex justify-between">
                <button 
                  onClick={() => setActiveTab(1)}
                  className="bg-gray-500 text-white px-8 py-3 rounded-lg hover:bg-gray-600 transition-colors font-medium"
                >
                  ← 이전 단계
                </button>
                <button 
                  onClick={() => setActiveTab(3)}
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  다음 단계 →
                </button>
              </div>
            </div>
          )}

          {activeTab === 3 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">TCFD 프레임워크</h3>
                <p className="text-gray-600 mb-6">
                  TCFD의 4개 핵심 영역에 대한 정보를 입력하세요.
                </p>
              </div>
              
              <div className="space-y-6">
                <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
                  <h4 className="font-semibold text-blue-900 mb-3 text-lg">거버넌스 (Governance)</h4>
                  <p className="text-blue-700 mb-4">기후 관련 위험과 기회에 대한 감독 역할과 책임</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-blue-800 mb-2">감사위원회 역할</label>
                      <textarea
                        className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={3}
                        placeholder="감사위원회의 기후 관련 위험 감독 역할을 설명하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-blue-800 mb-2">경영진 책임</label>
                      <textarea
                        className="w-full px-3 py-2 border border-blue-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        rows={3}
                        placeholder="경영진의 기후 관련 위험 관리 책임을 설명하세요"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-green-50 p-6 rounded-lg border border-green-200">
                  <h4 className="font-semibold text-green-900 mb-3 text-lg">전략 (Strategy)</h4>
                  <p className="text-green-700 mb-4">기후 관련 위험과 기회가 비즈니스에 미치는 영향</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-2">기후 시나리오 분석</label>
                      <textarea
                        className="w-full px-3 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        rows={3}
                        placeholder="기후 시나리오 분석 결과를 설명하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-green-800 mb-2">비즈니스 영향</label>
                      <textarea
                        className="w-full px-3 py-2 border border-green-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                        rows={3}
                        placeholder="기후 변화가 비즈니스에 미치는 영향을 설명하세요"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-purple-50 p-6 rounded-lg border border-purple-200">
                  <h4 className="font-semibold text-purple-900 mb-3 text-lg">위험 관리 (Risk Management)</h4>
                  <p className="text-purple-700 mb-4">기후 관련 위험 식별, 평가 및 관리</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-purple-800 mb-2">위험 식별</label>
                      <textarea
                        className="w-full px-3 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        rows={3}
                        placeholder="식별된 기후 관련 위험을 설명하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-purple-800 mb-2">위험 평가</label>
                      <textarea
                        className="w-full px-3 py-2 border border-purple-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                        rows={3}
                        placeholder="위험 평가 방법과 결과를 설명하세요"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-orange-50 p-6 rounded-lg border border-orange-200">
                  <h4 className="font-semibold text-orange-900 mb-3 text-lg">지표 및 목표 (Metrics & Targets)</h4>
                  <p className="text-orange-700 mb-4">기후 관련 위험과 기회를 평가하기 위한 지표</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-orange-800 mb-2">주요 지표</label>
                      <textarea
                        className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        rows={3}
                        placeholder="사용하는 주요 기후 관련 지표를 설명하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-orange-800 mb-2">목표 설정</label>
                      <textarea
                        className="w-full px-3 py-2 border border-orange-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                        rows={3}
                        placeholder="설정한 기후 관련 목표를 설명하세요"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 flex justify-between">
                <button 
                  onClick={() => setActiveTab(2)}
                  className="bg-gray-500 text-white px-8 py-3 rounded-lg hover:bg-gray-600 transition-colors font-medium"
                >
                  ← 이전 단계
                </button>
                <button 
                  onClick={() => setActiveTab(4)}
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  다음 단계 →
                </button>
              </div>
            </div>
          )}

          {activeTab === 4 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">기후시나리오</h3>
                <p className="text-gray-600 mb-6">
                  다양한 기후 시나리오에 따른 위험과 기회를 분석하세요.
                </p>
              </div>
              
              <div className="space-y-6">
                <div className="bg-red-50 p-6 rounded-lg border border-red-200">
                  <h4 className="font-semibold text-red-900 mb-3 text-lg">2°C 시나리오</h4>
                  <p className="text-red-700 mb-4">지구 평균 기온 상승을 2°C 이하로 제한하는 시나리오</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-red-800 mb-2">위험 요소</label>
                      <textarea
                        className="w-full px-3 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        rows={3}
                        placeholder="2°C 시나리오에서 예상되는 위험 요소를 설명하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-red-800 mb-2">기회 요소</label>
                      <textarea
                        className="w-full px-3 py-2 border border-red-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                        rows={3}
                        placeholder="2°C 시나리오에서 예상되는 기회 요소를 설명하세요"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-yellow-50 p-6 rounded-lg border border-yellow-200">
                  <h4 className="font-semibold text-yellow-900 mb-3 text-lg">4°C 시나리오</h4>
                  <p className="text-yellow-700 mb-4">현재 정책이 지속될 경우 예상되는 시나리오</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-yellow-800 mb-2">위험 요소</label>
                      <textarea
                        className="w-full px-3 py-2 border border-yellow-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                        rows={3}
                        placeholder="4°C 시나리오에서 예상되는 위험 요소를 설명하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-yellow-800 mb-2">기회 요소</label>
                      <textarea
                        className="w-full px-3 py-2 border border-yellow-300 rounded-lg focus:ring-2 focus:ring-yellow-500 focus:border-transparent"
                        rows={3}
                        placeholder="4°C 시나리오에서 예상되는 기회 요소를 설명하세요"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-indigo-50 p-6 rounded-lg border border-indigo-200">
                  <h4 className="font-semibold text-indigo-900 mb-3 text-lg">물리적 위험</h4>
                  <p className="text-indigo-700 mb-4">기후 변화로 인한 직접적인 물리적 위험</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-indigo-800 mb-2">급격한 기후 변화</label>
                      <textarea
                        className="w-full px-3 py-2 border border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        rows={3}
                        placeholder="급격한 기후 변화로 인한 위험을 설명하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-indigo-800 mb-2">점진적 기후 변화</label>
                      <textarea
                        className="w-full px-3 py-2 border border-indigo-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        rows={3}
                        placeholder="점진적 기후 변화로 인한 위험을 설명하세요"
                      />
                    </div>
                  </div>
                </div>

                <div className="bg-teal-50 p-6 rounded-lg border border-teal-200">
                  <h4 className="font-semibold text-teal-900 mb-3 text-lg">전환 위험</h4>
                  <p className="text-teal-700 mb-4">저탄소 경제로의 전환 과정에서 발생하는 위험</p>
                  <div className="space-y-3">
                    <div>
                      <label className="block text-sm font-medium text-teal-800 mb-2">정책 위험</label>
                      <textarea
                        className="w-full px-3 py-2 border border-teal-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                        rows={3}
                        placeholder="정책 변화로 인한 위험을 설명하세요"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-teal-800 mb-2">기술 위험</label>
                      <textarea
                        className="w-full px-3 py-2 border border-teal-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
                        rows={3}
                        placeholder="기술 변화로 인한 위험을 설명하세요"
                      />
                    </div>
                  </div>
                </div>
              </div>

              <div className="pt-4 flex justify-between">
                <button 
                  onClick={() => setActiveTab(3)}
                  className="bg-gray-500 text-white px-8 py-3 rounded-lg hover:bg-gray-600 transition-colors font-medium"
                >
                  ← 이전 단계
                </button>
                <button 
                  onClick={() => setActiveTab(5)}
                  className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium"
                >
                  다음 단계 →
                </button>
              </div>
            </div>
          )}

          {activeTab === 5 && (
            <div className="space-y-6">
              <div>
                <h3 className="text-2xl font-semibold text-gray-900 mb-4">AI보고서 초안</h3>
                <p className="text-gray-600 mb-6">
                  AI가 입력된 정보를 바탕으로 TCFD 기준 SR 초안을 생성합니다.
                </p>
              </div>
              
              <div className="bg-gray-50 p-6 rounded-lg border border-gray-200">
                <div className="flex items-center space-x-3 mb-4">
                  <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                  <span className="text-sm text-gray-600">AI 분석 준비 완료</span>
                </div>
                <textarea
                  className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="AI가 생성한 TCFD 기준 SR 초안이 여기에 표시됩니다..."
                  readOnly
                />
              </div>

              <div className="flex space-x-4 pt-4">
                <button className="bg-blue-600 text-white px-8 py-3 rounded-lg hover:bg-blue-700 transition-colors font-medium">
                  AI 분석 시작
                </button>
                <button className="bg-gray-500 text-white px-8 py-3 rounded-lg hover:bg-gray-600 transition-colors font-medium">
                  초기화
                </button>
                <button className="bg-green-600 text-white px-8 py-3 rounded-lg hover:bg-green-700 transition-colors font-medium">
                  SR 다운로드
                </button>
                <button className="bg-purple-600 text-white px-8 py-3 rounded-lg hover:bg-purple-700 transition-colors font-medium">
                  PDF 변환
                </button>
              </div>

              <div className="pt-4">
                <button 
                  onClick={() => setActiveTab(4)}
                  className="bg-gray-500 text-white px-8 py-3 rounded-lg hover:bg-gray-600 transition-colors font-medium"
                >
                  ← 이전 단계
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
