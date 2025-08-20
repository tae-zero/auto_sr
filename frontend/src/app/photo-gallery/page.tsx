'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Header } from '@/ui/organisms';

interface PhotoImage {
  id: string;
  filename: string;
  path: string;
}

const photoCategories = {
  '동해안': [
    { id: 'dh-1', filename: 'IMG_1652.JPG', path: '/동해안/IMG_1652.JPG' },
    { id: 'dh-2', filename: 'IMG_1656.JPG', path: '/동해안/IMG_1656.JPG' },
    { id: 'dh-3', filename: 'IMG_1657.JPG', path: '/동해안/IMG_1657.JPG' },
    { id: 'dh-4', filename: 'IMG_1659.JPG', path: '/동해안/IMG_1659.JPG' },
    { id: 'dh-5', filename: 'IMG_1670.JPG', path: '/동해안/IMG_1670.JPG' },
    { id: 'dh-6', filename: 'IMG_1674.JPG', path: '/동해안/IMG_1674.JPG' },
    { id: 'dh-7', filename: 'IMG_1683.JPG', path: '/동해안/IMG_1683.JPG' }
  ],
  '수락산': [
    { id: 'sr-1', filename: '2-8.jpg', path: '/수락산/2-8.jpg' },
    { id: 'sr-2', filename: '2-3.jpg', path: '/수락산/2-3.jpg' },
    { id: 'sr-3', filename: '1-23.JPG', path: '/수락산/1-23.JPG' },
    { id: 'sr-4', filename: '1-22.JPG', path: '/수락산/1-22.JPG' },
    { id: 'sr-5', filename: '1-20.JPG', path: '/수락산/1-20.JPG' },
    { id: 'sr-6', filename: '1-19.JPG', path: '/수락산/1-19.JPG' },
    { id: 'sr-7', filename: '1-18.JPG', path: '/수락산/1-18.JPG' },
    { id: 'sr-8', filename: '1-12.JPG', path: '/수락산/1-12.JPG' },
    { id: 'sr-9', filename: '1-6.JPG', path: '/수락산/1-6.JPG' },
    { id: 'sr-10', filename: '1-2.JPG', path: '/수락산/1-2.JPG' },
    { id: 'sr-11', filename: '1-1.JPG', path: '/수락산/1-1.JPG' }
  ],
  '아차산': [
    { id: 'ac-1', filename: 'KakaoTalk_20231007_211015122_20.jpg', path: '/아차산/KakaoTalk_20231007_211015122_20.jpg' },
    { id: 'ac-2', filename: 'KakaoTalk_20231007_211015122_24.jpg', path: '/아차산/KakaoTalk_20231007_211015122_24.jpg' },
    { id: 'ac-3', filename: 'KakaoTalk_20231007_211015122_13.jpg', path: '/아차산/KakaoTalk_20231007_211015122_13.jpg' },
    { id: 'ac-4', filename: 'KakaoTalk_20231007_211015122_07.jpg', path: '/아차산/KakaoTalk_20231007_211015122_07.jpg' },
    { id: 'ac-5', filename: 'KakaoTalk_20231007_211111336_16.jpg', path: '/아차산/KakaoTalk_20231007_211111336_16.jpg' },
    { id: 'ac-6', filename: 'KakaoTalk_20231007_211111336_11.jpg', path: '/아차산/KakaoTalk_20231007_211111336_11.jpg' },
    { id: 'ac-7', filename: 'KakaoTalk_20231007_211111336_07.jpg', path: '/아차산/KakaoTalk_20231007_211111336_07.jpg' },
    { id: 'ac-8', filename: '등산에 의한 침식.jpg', path: '/아차산/등산에 의한 침식.jpg' },
    { id: 'ac-9', filename: '핵석.jpg', path: '/아차산/핵석.jpg' }
  ],
  '우항리': [
    { id: 'wh-1', filename: 'IMG_8406.JPG', path: '/우항리/IMG_8406.JPG' },
    { id: 'wh-2', filename: 'IMG_8390.JPG', path: '/우항리/IMG_8390.JPG' },
    { id: 'wh-3', filename: 'IMG_8382.JPG', path: '/우항리/IMG_8382.JPG' },
    { id: 'wh-4', filename: 'IMG_8374.JPG', path: '/우항리/IMG_8374.JPG' },
    { id: 'wh-5', filename: 'IMG_8368.JPG', path: '/우항리/IMG_8368.JPG' },
    { id: 'wh-6', filename: 'IMG_8352.JPG', path: '/우항리/IMG_8352.JPG' }
  ],
  '일본': [
    { id: 'jp-1', filename: 'IMG_8932.JPG', path: '/일본/IMG_8932.JPG' },
    { id: 'jp-2', filename: 'IMG_8918.JPG', path: '/일본/IMG_8918.JPG' },
    { id: 'jp-3', filename: 'IMG_8836.JPG', path: '/일본/IMG_8836.JPG' },
    { id: 'jp-4', filename: 'IMG_8830.JPG', path: '/일본/IMG_8830.JPG' },
    { id: 'jp-5', filename: 'IMG_8824.JPG', path: '/일본/IMG_8824.JPG' },
    { id: 'jp-6', filename: 'IMG_8819.JPG', path: '/일본/IMG_8819.JPG' },
    { id: 'jp-7', filename: 'IMG_8815.JPG', path: '/일본/IMG_8815.JPG' },
    { id: 'jp-8', filename: 'IMG_8813.JPG', path: '/일본/IMG_8813.JPG' },
    { id: 'jp-9', filename: 'IMG_8807.JPG', path: '/일본/IMG_8807.JPG' },
    { id: 'jp-10', filename: 'IMG_8803.JPG', path: '/일본/IMG_8803.JPG' },
    { id: 'jp-11', filename: 'IMG_8770.JPG', path: '/일본/IMG_8770.JPG' },
    { id: 'jp-12', filename: 'IMG_8704.JPG', path: '/일본/IMG_8704.JPG' },
    { id: 'jp-13', filename: 'IMG_8692.JPG', path: '/일본/IMG_8692.JPG' },
    { id: 'jp-14', filename: 'IMG_8641.JPG', path: '/일본/IMG_8641.JPG' },
    { id: 'jp-15', filename: 'IMG_8636.JPG', path: '/일본/IMG_8636.JPG' }
  ],
  '제주도': [
    { id: 'jj-1', filename: 'IMG_1230.JPG', path: '/제주도/IMG_1230.JPG' },
    { id: 'jj-2', filename: 'IMG_1237.JPG', path: '/제주도/IMG_1237.JPG' },
    { id: 'jj-3', filename: 'IMG_1245.JPG', path: '/제주도/IMG_1245.JPG' },
    { id: 'jj-4', filename: 'IMG_1249.JPG', path: '/제주도/IMG_1249.JPG' },
    { id: 'jj-5', filename: 'IMG_1250.JPG', path: '/제주도/IMG_1250.JPG' },
    { id: 'jj-6', filename: 'IMG_1251.JPG', path: '/제주도/IMG_1251.JPG' },
    { id: 'jj-7', filename: 'IMG_1293.JPG', path: '/제주도/IMG_1293.JPG' },
    { id: 'jj-8', filename: 'IMG_1309.JPG', path: '/제주도/IMG_1309.JPG' },
    { id: 'jj-9', filename: 'IMG_1317.JPG', path: '/제주도/IMG_1317.JPG' }
  ]
};

export default function PhotoGalleryPage() {
  const router = useRouter();
  const [selectedCategory, setSelectedCategory] = useState<string>('동해안');
  const [selectedImage, setSelectedImage] = useState<PhotoImage | null>(null);

  const handleBack = () => {
    router.push('/');
  };

  const handleImageClick = (image: PhotoImage) => {
    setSelectedImage(image);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const currentImages = photoCategories[selectedCategory as keyof typeof photoCategories] || [];

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
              메인 페이지로 돌아가기
            </button>
            
            <h1 className="text-3xl font-bold text-gray-900 mb-2">📸 정태영의 사진 갤러리</h1>
            <p className="text-gray-600">여러 지역에서 찍은 아름다운 순간들을 담았습니다</p>
          </div>

          {/* 카테고리 선택 탭 */}
          <div className="mb-8">
            <div className="flex flex-wrap gap-2">
              {Object.keys(photoCategories).map((category) => (
                <button
                  key={category}
                  onClick={() => setSelectedCategory(category)}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    selectedCategory === category
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'bg-white text-gray-600 hover:bg-gray-100 border border-gray-200'
                  }`}
                >
                  {category}
                </button>
              ))}
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
                    alt={`${selectedCategory} 사진`}
                    className="w-full h-48 object-cover"
                  />
                </div>
                <div className="p-4">
                  <p className="text-sm text-gray-500 text-center">설명: 나중에</p>
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
                <h2 className="text-2xl font-bold text-gray-900">{selectedCategory}</h2>
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
                  alt={`${selectedCategory} 사진`}
                  className="w-full h-auto rounded-lg"
                />
              </div>
              
              <div className="text-sm text-gray-500">
                <p>설명: 나중에</p>
                <p>카테고리: {selectedCategory}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
