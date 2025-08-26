import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { question, sections, top_k } = body;

    // OpenAI RAG 서비스로 직접 호출
    const llmResponse = await fetch(`${process.env.NEXT_PUBLIC_LLM_SERVICE_URL}/rag/draft-and-polish?service=openai`, {
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

    const result = await llmResponse.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('OpenAI RAG 초안 생성 실패:', error);
    return NextResponse.json(
      { error: 'OpenAI RAG 초안 생성에 실패했습니다.' },
      { status: 500 }
    );
  }
}
