import { NextResponse } from 'next/server';

export async function GET() {
  try {
    // Gateway를 통해 TCFD Service에 연결
    const gatewayUrl = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';
    const response = await fetch(`${gatewayUrl}/api/v1/tcfd/companies`);
    
    if (!response.ok) {
      throw new Error(`Gateway error: ${response.status}`);
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('회사 목록 조회 실패:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: '회사 목록 조회에 실패했습니다',
        details: error instanceof Error ? error.message : '알 수 없는 오류'
      },
      { status: 500 }
    );
  }
}
