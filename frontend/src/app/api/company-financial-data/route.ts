import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const companyName = searchParams.get('company_name');
    
    if (!companyName) {
      return NextResponse.json(
        { 
          success: false, 
          error: '회사명이 필요합니다' 
        },
        { status: 400 }
      );
    }
    
    // Gateway를 통해 TCFD Service의 회사별 재무정보 API 호출
    const gatewayUrl = process.env.GATEWAY_URL || 'http://localhost:8080';
    const response = await fetch(`${gatewayUrl}/api/v1/tcfd/financial-data/company/${encodeURIComponent(companyName)}`);
    
    if (!response.ok) {
      throw new Error(`TCFD Service error: ${response.status}`);
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
