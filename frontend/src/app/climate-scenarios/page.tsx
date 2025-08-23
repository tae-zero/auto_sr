'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Header } from '@/ui/organisms';
import { apiClient } from '@/shared/lib';
import { useAuthStore } from '@/shared/state/auth.store';

interface ClimateImage {
  id: string;
  title: string;
  filename: string;
  path: string;
  description: string;
}

interface ClimateAnalysisImage {
  id: string;
  title: string;
  filename: string;
  path: string;
  description: string;
  category: string;
}

const ssp26Images: ClimateImage[] = [
  {
    id: 'ssp26-1',
    title: '1일 최대강수량',
    filename: 'SSP_126_1일_최대강수량_1.png',
    path: '/image_ssp2.6/SSP_126_1일_최대강수량_1.png',
    description: 'SSP 2.6 시나리오에서의 1일 최대강수량 변화'
  },
  {
    id: 'ssp26-2',
    title: '호우일수',
    filename: 'SSP_126_호우일수_1.png',
    path: '/image_ssp2.6/SSP_126_호우일수_1.png',
    description: 'SSP 2.6 시나리오에서의 호우일수 변화'
  },
  {
    id: 'ssp26-3',
    title: '1일 한파일수',
    filename: 'SSP_126_1일_한파일수.png',
    path: '/image_ssp2.6/SSP_126_1일_한파일수.png',
    description: 'SSP 2.6 시나리오에서의 1일 한파일수 변화'
  },
  {
    id: 'ssp26-4',
    title: '폭염일수',
    filename: 'SSP_126_폭염일수_1.png',
    path: '/image_ssp2.6/SSP_126_폭염일수_1.png',
    description: 'SSP 2.6 시나리오에서의 폭염일수 변화'
  },
  {
    id: 'ssp26-5',
    title: '강수량',
    filename: 'SSP_126_강수량.png',
    path: '/image_ssp2.6/SSP_126_강수량.png',
    description: 'SSP 2.6 시나리오에서의 강수량 변화'
  },
  {
    id: 'ssp26-6',
    title: '최대무강수지속기간',
    filename: 'SSP_126_최대무강수지속기간.png',
    path: '/image_ssp2.6/SSP_126_최대무강수지속기간.png',
    description: 'SSP 2.6 시나리오에서의 최대무강수지속기간 변화'
  },
  {
    id: 'ssp26-7',
    title: '강수강도',
    filename: 'SSP_126_강수강도.png',
    path: '/image_ssp2.6/SSP_126_강수강도.png',
    description: 'SSP 2.6 시나리오에서의 강수강도 변화'
  },
  {
    id: 'ssp26-8',
    title: '열대야일수',
    filename: 'SSP_126_열대야일수_1.png',
    path: '/image_ssp2.6/SSP_126_열대야일수_1.png',
    description: 'SSP 2.6 시나리오에서의 열대야일수 변화'
  },
  {
    id: 'ssp26-9',
    title: '평균 최고기온',
    filename: 'SSP_126_평균_최고기온.png',
    path: '/image_ssp2.6/SSP_126_평균_최고기온.png',
    description: 'SSP 2.6 시나리오에서의 평균 최고기온 변화'
  },
  {
    id: 'ssp26-10',
    title: '연평균기온',
    filename: 'SSP_126_연평균기온.png',
    path: '/image_ssp2.6/SSP_126_연평균기온.png',
    description: 'SSP 2.6 시나리오에서의 연평균기온 변화'
  }
];

const ssp85Images: ClimateImage[] = [
  {
    id: 'ssp85-1',
    title: '호우일수',
    filename: 'SSP_585_호우일수_1.png',
    path: '/image_ssp8.5/SSP_585_호우일수_1.png',
    description: 'SSP 8.5 시나리오에서의 호우일수 변화'
  },
  {
    id: 'ssp85-2',
    title: '최대무강수지속기간',
    filename: 'SSP_585_최대무강수지속기간.png',
    path: '/image_ssp8.5/SSP_585_최대무강수지속기간.png',
    description: 'SSP 8.5 시나리오에서의 최대무강수지속기간 변화'
  },
  {
    id: 'ssp85-3',
    title: '1일 최대강수량',
    filename: 'SSP_585_1일_최대강수량.png',
    path: '/image_ssp8.5/SSP_585_1일_최대강수량.png',
    description: 'SSP 8.5 시나리오에서의 1일 최대강수량 변화'
  },
  {
    id: 'ssp85-4',
    title: '한파일수',
    filename: 'SSP_585_한파일수.png',
    path: '/image_ssp8.5/SSP_585_한파일수.png',
    description: 'SSP 8.5 시나리오에서의 한파일수 변화'
  },
  {
    id: 'ssp85-5',
    title: '강수강도',
    filename: 'SSP_585_강수강도.png',
    path: '/image_ssp8.5/SSP_585_강수강도.png',
    description: 'SSP 8.5 시나리오에서의 강수강도 변화'
  },
  {
    id: 'ssp85-6',
    title: '폭염일수',
    filename: 'SSP_585_폭염_일수_1.png',
    path: '/image_ssp8.5/SSP_585_폭염_일수_1.png',
    description: 'SSP 8.5 시나리오에서의 폭염일수 변화'
  },
  {
    id: 'ssp85-7',
    title: '열대야일수',
    filename: 'SSP_585_열대야일수_1.png',
    path: '/image_ssp8.5/SSP_585_열대야일수_1.png',
    description: 'SSP 8.5 시나리오에서의 열대야일수 변화'
  },
  {
    id: 'ssp85-8',
    title: '평균 최고기온',
    filename: 'SSP_585_평균_최고기온.png',
    path: '/image_ssp8.5/SSP_585_평균_최고기온.png',
    description: 'SSP 8.5 시나리오에서의 평균 최고기온 변화'
  },
  {
    id: 'ssp85-9',
    title: '강수량',
    filename: 'SSP_585_강수량.png',
    path: '/image_ssp8.5/SSP_585_강수량.png',
    description: 'SSP 8.5 시나리오에서의 강수량 변화'
  },
  {
    id: 'ssp85-10',
    title: '연평균기온',
    filename: 'SSP_585_연평균기온.png',
    path: '/image_ssp8.5/SSP_585_연평균기온.png',
    description: 'SSP 8.5 시나리오에서의 연평균기온 변화'
  }
];

// Climate 분석 이미지들
const climateAnalysisImages: ClimateAnalysisImage[] = [
  {
    id: 'climate-1',
    title: 'Wind, SLP, SST 분석 (2013-2015)',
    filename: 'Wind_SLP_SST_2013-2015.png',
    path: '/climate/Wind_SLP_SST_2013-2015.png',
    description: '2013-2015년간의 바람, 해면기압, 해수면온도 분석 결과',
    category: '기상해양분석'
  },
  {
    id: 'climate-2',
    title: '벡터 예시 1',
    filename: 'vector_example1.png',
    path: '/climate/vector_example1.png',
    description: '벡터 필드 분석 예시 1',
    category: '벡터분석'
  },
  {
    id: 'climate-3',
    title: '벡터 예시 2',
    filename: 'vector_example2.png',
    path: '/climate/vector_example2.png',
    description: '벡터 필드 분석 예시 2',
    category: '벡터분석'
  },
  {
    id: 'climate-4',
    title: '벡터 예시 3',
    filename: 'vector_example3.png',
    path: '/climate/vector_example3.png',
    description: '벡터 필드 분석 예시 3',
    category: '벡터분석'
  },
  {
    id: 'climate-5',
    title: 'T-test 자유도 트렌드',
    filename: 'T-test_dof_trend.png',
    path: '/climate/T-test_dof_trend.png',
    description: 'T-test 자유도 트렌드 분석 결과',
    category: '통계분석'
  },
  {
    id: 'climate-6',
    title: 'T-test 자유도 회귀',
    filename: 'T-test_dof_regression.png',
    path: '/climate/T-test_dof_regression.png',
    description: 'T-test 자유도 회귀 분석 결과',
    category: '통계분석'
  },
  {
    id: 'climate-7',
    title: 'T-test 자유도 상관관계',
    filename: 'T-test_dof_correlation.png',
    path: '/climate/T-test_dof_correlation.png',
    description: 'T-test 자유도 상관관계 분석 결과',
    category: '통계분석'
  },
  {
    id: 'climate-8',
    title: 'T-test 분석',
    filename: 'T-test.png',
    path: '/climate/T-test.png',
    description: 'T-test 통계 분석 결과',
    category: '통계분석'
  },
  {
    id: 'climate-9',
    title: '온도 이상 수직 단면',
    filename: 'Tanom_vertical_cross_section.png',
    path: '/climate/Tanom_vertical_cross_section.png',
    description: '온도 이상의 수직 단면 분석',
    category: '기온분석'
  },
  {
    id: 'climate-10',
    title: 'SST 트렌드 제거 (Cartopy)',
    filename: 'sst_trend_detrend_cartopy.png',
    path: '/climate/sst_trend_detrend_cartopy.png',
    description: 'Cartopy를 사용한 해수면온도 트렌드 제거 분석',
    category: '해수면온도분석'
  },
  {
    id: 'climate-11',
    title: 'SST 히트맵',
    filename: 'sst_heatmap.png',
    path: '/climate/sst_heatmap.png',
    description: '해수면온도 히트맵 분석',
    category: '해수면온도분석'
  },
  {
    id: 'climate-12',
    title: 'SST EOF 시계열',
    filename: 'sst_eof_ts.png',
    path: '/climate/sst_eof_ts.png',
    description: '해수면온도 EOF 시계열 분석',
    category: '해수면온도분석'
  },
  {
    id: 'climate-13',
    title: 'SST EOF 분석',
    filename: 'sst_eof.png',
    path: '/climate/sst_eof.png',
    description: '해수면온도 EOF 분석 결과',
    category: '해수면온도분석'
  },
  {
    id: 'climate-14',
    title: 'SST 상관관계 및 회귀',
    filename: 'sst_corr_reg.png',
    path: '/climate/sst_corr_reg.png',
    description: '해수면온도 상관관계 및 회귀 분석',
    category: '해수면온도분석'
  },
  {
    id: 'climate-15',
    title: 'ONI 시계열',
    filename: 'ONI_timeseries.png',
    path: '/climate/ONI_timeseries.png',
    description: 'Oceanic Niño Index 시계열 분석',
    category: '엘니뇨분석'
  },
  {
    id: 'climate-16',
    title: '고도 이상 PNA',
    filename: 'hgtanom_PNA.png',
    path: '/climate/hgtanom_PNA.png',
    description: 'Pacific-North America 패턴의 고도 이상 분석',
    category: '대기순환분석'
  },
  {
    id: 'climate-17',
    title: 'GPM PCT89 글로벌 맵',
    filename: 'GPM_PCT89_GlobalMap.png',
    path: '/climate/GPM_PCT89_GlobalMap.png',
    description: 'Global Precipitation Mission PCT89 글로벌 맵',
    category: '강수분석'
  },
  {
    id: 'climate-18',
    title: 'DPR Z-profile 샘플',
    filename: 'DPR_Zprofile_sample.png',
    path: '/climate/DPR_Zprofile_sample.png',
    description: 'Dual-frequency Precipitation Radar Z-profile 샘플',
    category: '강수분석'
  },
  {
    id: 'climate-19',
    title: 'AMO-표면온도 상관관계',
    filename: 'Corr_AMO_SurfaceTemp.png',
    path: '/climate/Corr_AMO_SurfaceTemp.png',
    description: 'Atlantic Multidecadal Oscillation과 표면온도 상관관계',
    category: '대기순환분석'
  },
  {
    id: 'climate-20',
    title: 'AMO-300hPa 상관관계',
    filename: 'Corr_AMO_300hPa.png',
    path: '/climate/Corr_AMO_300hPa.png',
    description: 'Atlantic Multidecadal Oscillation과 300hPa 상관관계',
    category: '대기순환분석'
  },
  {
    id: 'climate-21',
    title: '시간 필터 예시',
    filename: 'Code6-2-1_Time_Filter_example.png',
    path: '/climate/Code6-2-1_Time_Filter_example.png',
    description: '시간 필터 적용 예시',
    category: '시계열분석'
  },
  {
    id: 'climate-22',
    title: '산점도 + 히스토그램 예시',
    filename: 'Code6-1-3_Scatter+JHist_example.png',
    path: '/climate/Code6-1-3_Scatter+JHist_example.png',
    description: '산점도와 히스토그램 결합 분석 예시',
    category: '통계분석'
  },
  {
    id: 'climate-23',
    title: '수평 막대 + 바이올린 플롯',
    filename: 'Code6-1-2_barh+Violin_example.png',
    path: '/climate/Code6-1-2_barh+Violin_example.png',
    description: '수평 막대 그래프와 바이올린 플롯 결합 예시',
    category: '통계분석'
  },
  {
    id: 'climate-24',
    title: '수직 막대 그래프',
    filename: 'Code6-1-1_vertical_bar_example.png',
    path: '/climate/Code6-1-1_vertical_bar_example.png',
    description: '수직 막대 그래프 분석 예시',
    category: '통계분석'
  }
];

export default function ClimateScenariosPage() {
  const router = useRouter();
  const [selectedTab, setSelectedTab] = useState<'ssp26' | 'ssp85' | 'climate'>('ssp26');
  const [selectedScenario, setSelectedScenario] = useState<'ssp26' | 'ssp85'>('ssp26');
  const [selectedImage, setSelectedImage] = useState<ClimateImage | ClimateAnalysisImage | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleBack = () => {
    router.push('/tcfd');
  };

  const handleImageClick = (image: ClimateImage) => {
    setSelectedImage(image);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const getCurrentImages = () => {
    if (selectedTab === 'climate') {
      return climateAnalysisImages;
    }
    return selectedScenario === 'ssp26' ? ssp26Images : ssp85Images;
  };

  const currentImages = getCurrentImages();

  // 인증 상태 확인
  useEffect(() => {
    // 클라이언트 사이드에서만 인증 확인
    if (typeof window !== 'undefined') {
      const checkAuth = async () => {
        try {
          // localStorage에서 토큰 확인
          const token = localStorage.getItem('auth_token');
          if (!token) {
            console.log('❌ 인증 토큰이 없습니다');
            router.push('/login');
            return;
          }

          // 토큰 유효성 확인 (API 호출)
          try {
            await apiClient.get('/api/v1/auth/verify');
            console.log('✅ 인증 토큰이 유효합니다');
            setIsAuthenticated(true);
          } catch (error: any) {
            if (error.response?.status === 401) {
              console.log('❌ 인증 토큰이 만료되었습니다');
              // 토큰 갱신 시도
              const refreshed = await useAuthStore.getState().refreshToken();
              if (refreshed) {
                console.log('✅ 토큰이 갱신되었습니다');
                setIsAuthenticated(true);
              } else {
                console.log('❌ 토큰 갱신 실패');
                router.push('/login');
              }
            } else {
              console.log('❌ 인증 확인 중 오류 발생');
              router.push('/login');
            }
          }
        } catch (error) {
          console.error('❌ 인증 확인 실패:', error);
          router.push('/login');
        }
      };

      checkAuth();
    }
  }, [router]);

  // 인증되지 않은 경우 로딩 화면 표시
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header />
        <div className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">인증 확인 중...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 헤더 */}
          <div className="mb-8">
            <button
              onClick={handleBack}
              className="mb-4 flex items-center text-blue-600 hover:text-blue-800 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              TCFD 페이지로 돌아가기
            </button>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">기후 시나리오 분석</h1>
            <p className="text-gray-600">SSP 2.6과 SSP 8.5 시나리오에 따른 기후 변화 예측 이미지</p>
          </div>

          {/* 메인 탭 선택 */}
          <div className="mb-8">
            <div className="flex space-x-1 bg-gray-200 p-1 rounded-lg mb-6">
              <button
                onClick={() => setSelectedTab('ssp26')}
                className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                  selectedTab === 'ssp26'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                SSP 2.6 (낮은 배출 시나리오)
              </button>
              <button
                onClick={() => setSelectedTab('ssp85')}
                className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                  selectedTab === 'ssp85'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                SSP 8.5 (높은 배출 시나리오)
              </button>
              <button
                onClick={() => setSelectedTab('climate')}
                className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                  selectedTab === 'climate'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                Climate 분석
              </button>
            </div>

            {/* SSP 시나리오 하위 탭 (climate 탭이 아닐 때만 표시) */}
            {selectedTab !== 'climate' && (
              <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
                <button
                  onClick={() => setSelectedScenario('ssp26')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    selectedScenario === 'ssp26'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  SSP 2.6
                </button>
                <button
                  onClick={() => setSelectedScenario('ssp85')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    selectedScenario === 'ssp85'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  SSP 8.5
                </button>
              </div>
            )}
          </div>

          {/* 이미지 갤러리 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {currentImages.map((image) => (
              <div
                key={image.id}
                className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleImageClick(image)}
              >
                <div className="aspect-w-16 aspect-h-9 bg-gray-100">
                  <Image
                    src={image.path}
                    alt={image.title}
                    width={640}
                    height={360}
                    className="w-full h-48 object-cover"
                  />
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">{image.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">{image.description}</p>
                  {'category' in image && (
                    <div className="mt-2">
                      <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                        {(image as ClimateAnalysisImage).category}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 이미지 상세 모달 */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">{selectedImage.title}</h2>
                <button
                  onClick={closeModal}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              <div className="mb-4">
                <Image
                  src={selectedImage.path}
                  alt={selectedImage.title}
                  width={1024}
                  height={576}
                  className="w-full h-auto rounded-lg"
                />
              </div>
              
              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-2">설명</h3>
                <p className="text-gray-600">{selectedImage.description}</p>
              </div>
              
              <div className="text-sm text-gray-500">
                <p>파일명: {selectedImage.filename}</p>
                {'category' in selectedImage ? (
                  <p>카테고리: {(selectedImage as ClimateAnalysisImage).category}</p>
                ) : (
                  <p>시나리오: {selectedScenario === 'ssp26' ? 'SSP 2.6' : 'SSP 8.5'}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
