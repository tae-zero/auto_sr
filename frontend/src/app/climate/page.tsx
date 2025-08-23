'use client';

import Image from 'next/image';
import { useState } from 'react';

interface ImageData {
  src: string;
  title: string;
  description: string;
}

const climateImages: ImageData[] = [
  {
    src: '/climate/ONI_timeseries.png',
    title: 'ONI Time Series',
    description: 'Oceanic Niño Index 시계열 데이터'
  },
  {
    src: '/climate/vector_example1.png',
    title: 'Vector Example 1',
    description: '벡터 데이터 시각화 예시 1'
  },
  {
    src: '/climate/vector_example2.png',
    title: 'Vector Example 2',
    description: '벡터 데이터 시각화 예시 2'
  },
  {
    src: '/climate/vector_example3.png',
    title: 'Vector Example 3',
    description: '벡터 데이터 시각화 예시 3'
  },
  {
    src: '/climate/Corr_AMO_300hPa.png',
    title: 'AMO Correlation',
    description: 'AMO와 300hPa 상관관계 분석'
  },
  {
    src: '/climate/DPR_Zprofile_sample.png',
    title: 'DPR Z-Profile',
    description: 'DPR Z 프로파일 샘플 데이터'
  },
  {
    src: '/climate/Tanom_vertical_cross_section.png',
    title: 'Temperature Anomaly',
    description: '온도 이상 수직 단면도'
  },
  {
    src: '/climate/5.png',
    title: 'Climate Chart',
    description: '기후 데이터 차트'
  },
  {
    src: '/climate/GPM_PCT89_GlobalMap.png',
    title: 'GPM Global Map',
    description: 'GPM PCT89 글로벌 맵'
  }
];

export default function ClimatePage() {
  const [selectedImage, setSelectedImage] = useState<ImageData | null>(null);

  return (
    <div className="min-h-screen bg-gray-100 py-12 px-4 sm:px-6 lg:px-8">
      {/* 헤더 */}
      <div className="max-w-7xl mx-auto text-center mb-12">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          기후 데이터 갤러리
        </h1>
        <p className="text-lg text-gray-600">
          기후 변화와 관련된 다양한 데이터 시각화 자료들을 확인하세요
        </p>
      </div>

      {/* 이미지 그리드 */}
      <div className="max-w-7xl mx-auto">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {climateImages.map((image, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow duration-300 cursor-pointer"
              onClick={() => setSelectedImage(image)}
            >
              <div className="relative h-48 sm:h-64">
                <Image
                  src={image.src}
                  alt={image.title}
                  fill
                  style={{ objectFit: 'cover' }}
                  sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
                />
              </div>
              <div className="p-4">
                <h3 className="text-lg font-semibold text-gray-900 mb-1">
                  {image.title}
                </h3>
                <p className="text-sm text-gray-600">{image.description}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 모달 */}
      {selectedImage && (
        <div
          className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <div className="max-w-4xl w-full bg-white rounded-lg overflow-hidden">
            <div className="relative h-[80vh]">
              <Image
                src={selectedImage.src}
                alt={selectedImage.title}
                fill
                style={{ objectFit: 'contain' }}
                sizes="100vw"
              />
            </div>
            <div className="p-4 bg-white">
              <h3 className="text-xl font-semibold text-gray-900 mb-2">
                {selectedImage.title}
              </h3>
              <p className="text-gray-600">{selectedImage.description}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
