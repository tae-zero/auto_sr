'use client';

import { useState } from 'react';
import Image from 'next/image';

interface ClimateScenarioModalProps {
  isOpen: boolean;
  onClose: () => void;
  scenario: 'ssp2.6' | 'ssp8.5';
}

interface ClimateImage {
  key: string;
  title: string;
  filename: string;
  description: string;
}

const ClimateScenarioModal: React.FC<ClimateScenarioModalProps> = ({
  isOpen,
  onClose,
  scenario
}) => {
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  // SSP별 이미지 데이터
  const climateImages: Record<'ssp2.6' | 'ssp8.5', ClimateImage[]> = {
    'ssp2.6': [
      {
        key: '연평균기온',
        title: '연평균기온 변화',
        filename: 'SSP_126_연평균기온.png',
        description: 'SSP 2.6 시나리오에서의 연평균기온 변화 추세'
      },
      {
        key: '평균_최고기온',
        title: '평균 최고기온 변화',
        filename: 'SSP_126_평균_최고기온.png',
        description: 'SSP 2.6 시나리오에서의 평균 최고기온 변화'
      },
      {
        key: '강수량',
        title: '강수량 변화',
        filename: 'SSP_126_강수량.png',
        description: 'SSP 2.6 시나리오에서의 강수량 변화 패턴'
      },
      {
        key: '1일_최대강수량_1',
        title: '1일 최대강수량',
        filename: 'SSP_126_1일_최대강수량_1.png',
        description: 'SSP 2.6 시나리오에서의 1일 최대강수량 변화'
      },
      {
        key: '호우일수_1',
        title: '호우일수 변화',
        filename: 'SSP_126_호우일수_1.png',
        description: 'SSP 2.6 시나리오에서의 호우일수 변화'
      },
      {
        key: '폭염일수_1',
        title: '폭염일수 변화',
        filename: 'SSP_126_폭염일수_1.png',
        description: 'SSP 2.6 시나리오에서의 폭염일수 변화'
      },
      {
        key: '열대야일수_1',
        title: '열대야일수 변화',
        filename: 'SSP_126_열대야일수_1.png',
        description: 'SSP 2.6 시나리오에서의 열대야일수 변화'
      },
      {
        key: '1일_한파일수',
        title: '한파일수 변화',
        filename: 'SSP_126_1일_한파일수.png',
        description: 'SSP 2.6 시나리오에서의 한파일수 변화'
      },
      {
        key: '최대무강수지속기간',
        title: '최대무강수지속기간',
        filename: 'SSP_126_최대무강수지속기간.png',
        description: 'SSP 2.6 시나리오에서의 최대무강수지속기간'
      },
      {
        key: '강수강도',
        title: '강수강도 변화',
        filename: 'SSP_126_강수강도.png',
        description: 'SSP 2.6 시나리오에서의 강수강도 변화'
      }
    ],
    'ssp8.5': [
      {
        key: '연평균기온',
        title: '연평균기온 변화',
        filename: 'SSP_585_연평균기온.png',
        description: 'SSP 8.5 시나리오에서의 연평균기온 변화 추세'
      },
      {
        key: '평균_최고기온',
        title: '평균 최고기온 변화',
        filename: 'SSP_585_평균_최고기온.png',
        description: 'SSP 8.5 시나리오에서의 평균 최고기온 변화'
      },
      {
        key: '강수량',
        title: '강수량 변화',
        filename: 'SSP_585_강수량.png',
        description: 'SSP 8.5 시나리오에서의 강수량 변화 패턴'
      },
      {
        key: '1일_최대강수량',
        title: '1일 최대강수량',
        filename: 'SSP_585_1일_최대강수량.png',
        description: 'SSP 8.5 시나리오에서의 1일 최대강수량 변화'
      },
      {
        key: '호우일수_1',
        title: '호우일수 변화',
        filename: 'SSP_585_호우일수_1.png',
        description: 'SSP 8.5 시나리오에서의 호우일수 변화'
      },
      {
        key: '폭염_일수_1',
        title: '폭염일수 변화',
        filename: 'SSP_585_폭염_일수_1.png',
        description: 'SSP 8.5 시나리오에서의 폭염일수 변화'
      },
      {
        key: '열대야일수_1',
        title: '열대야일수 변화',
        filename: 'SSP_585_열대야일수_1.png',
        description: 'SSP 8.5 시나리오에서의 열대야일수 변화'
      },
      {
        key: '한파일수',
        title: '한파일수 변화',
        filename: 'SSP_585_한파일수.png',
        description: 'SSP 8.5 시나리오에서의 한파일수 변화'
      },
      {
        key: '최대무강수지속기간',
        title: '최대무강수지속기간',
        filename: 'SSP_585_최대무강수지속기간.png',
        description: 'SSP 8.5 시나리오에서의 최대무강수지속기간'
      },
      {
        key: '강수강도',
        title: '강수강도 변화',
        filename: 'SSP_585_강수강도.png',
        description: 'SSP 8.5 시나리오에서의 강수강도 변화'
      }
    ]
  };

  const currentImages = climateImages[scenario];
  const scenarioTitle = scenario === 'ssp2.6' ? 'SSP 2.6 (극저탄소 시나리오)' : 'SSP 8.5 (고탄소 시나리오)';

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-y-auto">
        {/* 헤더 */}
        <div className="flex justify-between items-center p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-800">
            {scenarioTitle} 상세 분석
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl"
          >
            ×
          </button>
        </div>

        {/* 이미지 그리드 */}
        <div className="p-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {currentImages.map((image) => (
              <div
                key={image.key}
                className="bg-gray-50 rounded-lg p-4 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => setSelectedImage(image.filename)}
              >
                <div className="aspect-video bg-white rounded-lg overflow-hidden mb-3">
                  <Image
                    src={`/image_${scenario}/${image.filename}`}
                    alt={image.title}
                    width={300}
                    height={200}
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="font-semibold text-gray-800 mb-2">{image.title}</h3>
                <p className="text-sm text-gray-600">{image.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* 선택된 이미지 모달 */}
        {selectedImage && (
          <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-60 p-4">
            <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
              <div className="flex justify-between items-center p-4 border-b">
                <h3 className="text-xl font-semibold">이미지 상세보기</h3>
                <button
                  onClick={() => setSelectedImage(null)}
                  className="text-gray-500 hover:text-gray-700 text-2xl"
                >
                  ×
                </button>
              </div>
              <div className="p-4">
                <Image
                  src={`/image_${scenario}/${selectedImage}`}
                  alt="상세 이미지"
                  width={800}
                  height={600}
                  className="w-full h-auto rounded-lg"
                />
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ClimateScenarioModal;
