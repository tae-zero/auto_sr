import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { company_name, draft, polished } = body;

    // TCFD Report Service로 요청 전달
    const response = await fetch(`${process.env.NEXT_PUBLIC_GATEWAY_URL}/api/v1/tcfdreport/download/word`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        company_name,
        draft,
        polished
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // 스트림을 그대로 전달 (blob으로 읽지 않음)
    const stream = response.body;
    if (!stream) {
      throw new Error('응답 스트림이 없습니다.');
    }

    // 헤더 복사 (특히 Content-Disposition)
    const headers = new Headers();
    headers.set('Content-Type', response.headers.get('content-type') || 'application/vnd.openxmlformats-officedocument.wordprocessingml.document');
    
    const contentDisposition = response.headers.get('content-disposition');
    if (contentDisposition) {
      headers.set('Content-Disposition', contentDisposition);
    } else {
      // fallback filename
      headers.set('Content-Disposition', `attachment; filename="${company_name || 'TCFD'}_보고서_${new Date().toISOString().slice(0, 10)}.docx"`);
    }

    // 스트림을 그대로 전달
    return new NextResponse(stream, { headers });

  } catch (error) {
    console.error('Word 다운로드 API 오류:', error);
    return NextResponse.json(
      { error: 'Word 문서 생성에 실패했습니다.' },
      { status: 500 }
    );
  }
}
