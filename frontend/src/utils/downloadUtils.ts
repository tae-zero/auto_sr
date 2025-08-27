

export interface DownloadContent {
  title: string;
  draft: string;
  polished: string;
  companyName?: string;
  timestamp?: string;
}

/**
 * 서버 API를 통해 Word 문서 다운로드
 */
export const downloadAsWordFromServer = async (content: DownloadContent): Promise<void> => {
  try {
    const response = await fetch('/api/download/word', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_name: content.companyName,
        draft: content.draft,
        polished: content.polished
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${content.title}_TCFD_보고서.docx`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Word 다운로드 실패:', error);
    throw new Error('Word 문서 다운로드에 실패했습니다.');
  }
};

/**
 * 서버 API를 통해 PDF 다운로드
 */
export const downloadAsPDFFromServer = async (content: DownloadContent): Promise<void> => {
  try {
    const response = await fetch('/api/download/pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_name: content.companyName,
        draft: content.draft,
        polished: content.polished
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `${content.title}_TCFD_보고서.pdf`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error('PDF 다운로드 실패:', error);
    throw new Error('PDF 다운로드에 실패했습니다.');
  }
};

/**
 * 텍스트를 Word 문서 형식으로 변환
 */
export const formatTextForWord = (text: string): string => {
  // 특수 문자 처리 및 줄바꿈 유지
  return text
    .replace(/\n/g, '\n\n') // 줄바꿈을 더 명확하게
    .replace(/\s+/g, ' ') // 연속된 공백 정리
    .trim();
};

/**
 * 텍스트를 PDF 형식으로 변환
 */
export const formatTextForPDF = (text: string): string => {
  // PDF에서 잘 보이도록 텍스트 정리
  return text
    .replace(/\n{3,}/g, '\n\n') // 3개 이상의 연속된 줄바꿈을 2개로
    .replace(/\s+/g, ' ') // 연속된 공백 정리
    .trim();
};
