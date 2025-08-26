import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { question, sections, top_k } = body;

    // Gateway를 통해 LLM Service 호출
    const gatewayResponse = await fetch(`${process.env.NEXT_PUBLIC_GATEWAY_URL}/api/llm/rag/draft-and-polish`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        sections,
        top_k,
        tone: '공식적/객관적',
        style_guide: 'TCFD 프레임워크 기준, ESG/회계 전문용어 유지'
      })
    });

    const result = await gatewayResponse.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('TCFD 보고서 생성 실패:', error);
    return NextResponse.json(
      { error: 'TCFD 보고서 생성에 실패했습니다.' },
      { status: 500 }
    );
  }
}
