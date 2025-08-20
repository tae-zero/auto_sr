'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/ui/organisms';

interface ClimateImage {
  id: string;
  title: string;
  filename: string;
  path: string;
  description: string;
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

export default function ClimateScenariosPage() {
  const router = useRouter();
  const [selectedScenario, setSelectedScenario] = useState<'ssp26' | 'ssp85'>('ssp26');
  const [selectedImage, setSelectedImage] = useState<ClimateImage | null>(null);

  const handleBack = () => {
    router.push('/tcfd');
  };

  const handleImageClick = (image: ClimateImage) => {
    setSelectedImage(image);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const currentImages = selectedScenario === 'ssp26' ? ssp26Images : ssp85Images;

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

          {/* 시나리오 선택 탭 */}
          <div className="mb-8">
            <div className="flex space-x-1 bg-gray-200 p-1 rounded-lg">
              <button
                onClick={() => setSelectedScenario('ssp26')}
                className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                  selectedScenario === 'ssp26'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                SSP 2.6 (낮은 배출 시나리오)
              </button>
              <button
                onClick={() => setSelectedScenario('ssp85')}
                className={`flex-1 py-3 px-6 rounded-md font-medium transition-colors ${
                  selectedScenario === 'ssp85'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                SSP 8.5 (높은 배출 시나리오)
              </button>
            </div>
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
                  <img
                    src={image.path}
                    alt={image.title}
                    className="w-full h-48 object-cover"
                  />
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">{image.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">{image.description}</p>
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
                <img
                  src={selectedImage.path}
                  alt={selectedImage.title}
                  className="w-full h-auto rounded-lg"
                />
              </div>
              
              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-2">설명</h3>
                <p className="text-gray-600">{selectedImage.description}</p>
              </div>
              
              <div className="text-sm text-gray-500">
                <p>파일명: {selectedImage.filename}</p>
                <p>시나리오: {selectedScenario === 'ssp26' ? 'SSP 2.6' : 'SSP 8.5'}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
