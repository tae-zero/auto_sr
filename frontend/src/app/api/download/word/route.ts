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

    const blob = await response.blob();
    
    return new NextResponse(blob, {
      headers: {
        'Content-Type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'Content-Disposition': `attachment; filename="${company_name || 'TCFD'}_보고서_${new Date().toISOString().slice(0, 10)}.docx"`
      }
    });

  } catch (error) {
    console.error('Word 다운로드 API 오류:', error);
    return NextResponse.json(
      { error: 'Word 문서 생성에 실패했습니다.' },
      { status: 500 }
    );
  }
}
