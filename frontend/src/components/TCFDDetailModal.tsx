'use client';

import { TCFDStandardData } from '@/app/tcfd/page';

interface TCFDDetailModalProps {
  isOpen: boolean;
  onClose: () => void;
  category: string;
  title: string;
  description: string;
  disclosures: TCFDStandardData[];
  color: string;
  bgColor: string;
}

export default function TCFDDetailModal({
  isOpen,
  onClose,
  category,
  title,
  description,
  disclosures,
  color,
  bgColor
}: TCFDDetailModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        {/* 헤더 */}
        <div className={`${bgColor} p-6 rounded-t-lg`}>
          <div className="flex justify-between items-start">
            <div>
              <h2 className={`text-2xl font-bold ${color} mb-2`}>{title}</h2>
              <p className={`${color} text-lg`}>{description}</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
            >
              ×
            </button>
          </div>
        </div>

        {/* 컨텐츠 */}
        <div className="p-6">
          <div className="space-y-6">
            {disclosures.map((disclosure, index) => (
              <div key={`${disclosure.category}-${disclosure.disclosure_id}-${index}`} 
                   className="border border-gray-200 rounded-lg p-6 shadow-sm">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-xl font-semibold text-gray-800">
                    {disclosure.disclosure_id}
                  </h3>
                  <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
                    {category}
                  </span>
                </div>
                
                <div className="space-y-4">
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">공개 요약</h4>
                    <p className="text-gray-600 leading-relaxed">
                      {disclosure.disclosure_summary}
                    </p>
                  </div>
                  
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">공개 상세</h4>
                    <p className="text-gray-600 leading-relaxed">
                      {disclosure.disclosure_detail}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* 푸터 */}
        <div className="bg-gray-50 px-6 py-4 rounded-b-lg">
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-600">
              총 {disclosures.length}개의 공개 요구사항
            </p>
            <button
              onClick={onClose}
              className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              닫기
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
