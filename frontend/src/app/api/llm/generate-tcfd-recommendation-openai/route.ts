import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { company_name, recommendation_type, user_input, llm_provider } = body;

    // LLM Service로 직접 호출
    const llmResponse = await fetch(`${process.env.NEXT_PUBLIC_LLM_SERVICE_URL}/tcfd/generate-recommendation`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.LLM_SERVICE_ADMIN_TOKEN || 'supersecret'}`
      },
      body: JSON.stringify({
        company_name,
        recommendation_type,
        user_input,
        llm_provider
      })
    });

    const result = await llmResponse.json();
    return NextResponse.json(result);

  } catch (error) {
    console.error('TCFD 권고사항 문장 생성 실패:', error);
    return NextResponse.json(
      { error: 'TCFD 권고사항 문장 생성에 실패했습니다.' },
      { status: 500 }
    );
  }
}
