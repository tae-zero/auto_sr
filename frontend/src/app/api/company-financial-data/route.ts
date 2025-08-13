import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const companyName = searchParams.get('company_name');
    
    if (!companyName) {
      return NextResponse.json(
        { success: false, error: '회사명이 필요합니다' },
        { status: 400 }
      );
    }

    // Gateway를 통해 TCFD Service에 연결
    const gatewayUrl = process.env.NEXT_PUBLIC_GATEWAY_URL || 'http://localhost:8080';
    const response = await fetch(`${gatewayUrl}/api/v1/tcfd/company-financial-data?company_name=${encodeURIComponent(companyName)}`);
    
    if (!response.ok) {
      throw new Error(`Gateway error: ${response.status}`);
    }
    
    const data = await response.json();
    
    return NextResponse.json(data);
  } catch (error) {
    console.error('회사별 재무정보 조회 실패:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: '회사별 재무정보 조회에 실패했습니다',
        details: error instanceof Error ? error.message : '알 수 없는 오류'
      },
      { status: 500 }
    );
  }
}
