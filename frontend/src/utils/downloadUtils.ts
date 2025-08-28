

export interface DownloadContent {
  title: string;
  draft: string;
  polished: string;
  companyName?: string;
  timestamp?: string;
}

/**
 * axios를 사용한 안정적인 파일 다운로드 (권장)
 */
export const downloadFileWithAxios = async (url: string, payload: any, fallbackName: string): Promise<void> => {
  try {
    // axios를 동적으로 import (필요시에만)
    const axios = (await import('axios')).default;
    
    const res = await axios.post(url, payload, { 
      responseType: 'blob',
      timeout: 60000 // 60초 타임아웃
    });

    // 에러 응답(예: 400/500)이 blob(JSON)로 오는 경우 처리
    if (res.status !== 200) {
      const text = await res.data.text?.().catch(() => '');
      throw new Error(text || `HTTP ${res.status}`);
    }

    // 파일명 추출
    const cd = (res.headers['content-disposition'] || '') as string;
    const m = /filename\*?=(?:UTF-8''|")?([^"]+)/i.exec(cd);
    const encoded = (m?.[1] || fallbackName).trim();
    const filename = decodeURIComponent(encoded);

    // 다운로드
    const blob = new Blob([res.data]);
    const urlObj = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = urlObj;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(urlObj);
  } catch (error) {
    console.error('Axios 다운로드 실패:', error);
    throw error;
  }
};

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
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    // 파일명 추출
    const contentDisposition = response.headers.get('content-disposition') || '';
    const filenameMatch = /filename\*?=(?:UTF-8''|")?([^"]+)/i.exec(contentDisposition);
    const encodedFilename = (filenameMatch?.[1] || `${content.title}_TCFD_보고서.docx`).trim();
    const filename = decodeURIComponent(encodedFilename);

    // Blob으로 변환하여 다운로드
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
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
      const errorText = await response.text();
      throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
    }

    // 파일명 추출
    const contentDisposition = response.headers.get('content-disposition') || '';
    const filenameMatch = /filename\*?=(?:UTF-8''|")?([^"]+)/i.exec(contentDisposition);
    const encodedFilename = (filenameMatch?.[1] || `${content.title}_TCFD_보고서.pdf`).trim();
    const filename = decodeURIComponent(encodedFilename);

    // Blob으로 변환하여 다운로드
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
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
