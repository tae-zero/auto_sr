'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { Header } from '@/ui/organisms';
import { apiClient } from '@/shared/lib';
import { useAuthStore } from '@/shared/state/auth.store';

interface ClimateImage {
  id: string;
  title: string;
  filename: string;
  path: string;
  description: string;
}

interface ClimateAnalysisImage {
  id: string;
  title: string;
  filename: string;
  path: string;
  description: string;
  category: string;
}

const ssp26Images: ClimateImage[] = [
  {
    id: 'ssp26-1',
    title: '1일 최대강수량',
    filename: 'SSP_126_1일_최대강수량_1.png',
    path: '/image_ssp2.6/SSP_126_1일_최대강수량_1.png',
    description: 'SSP 2.6 시나리오에서의 1일 최대강수량 변화'
  },
  {
    id: 'ssp26-2',
    title: '호우일수',
    filename: 'SSP_126_호우일수_1.png',
    path: '/image_ssp2.6/SSP_126_호우일수_1.png',
    description: 'SSP 2.6 시나리오에서의 호우일수 변화'
  },
  {
    id: 'ssp26-3',
    title: '1일 한파일수',
    filename: 'SSP_126_1일_한파일수.png',
    path: '/image_ssp2.6/SSP_126_1일_한파일수.png',
    description: 'SSP 2.6 시나리오에서의 1일 한파일수 변화'
  },
  {
    id: 'ssp26-4',
    title: '폭염일수',
    filename: 'SSP_126_폭염일수_1.png',
    path: '/image_ssp2.6/SSP_126_폭염일수_1.png',
    description: 'SSP 2.6 시나리오에서의 폭염일수 변화'
  },
  {
    id: 'ssp26-5',
    title: '강수량',
    filename: 'SSP_126_강수량.png',
    path: '/image_ssp2.6/SSP_126_강수량.png',
    description: 'SSP 2.6 시나리오에서의 강수량 변화'
  },
  {
    id: 'ssp26-6',
    title: '최대무강수지속기간',
    filename: 'SSP_126_최대무강수지속기간.png',
    path: '/image_ssp2.6/SSP_126_최대무강수지속기간.png',
    description: 'SSP 2.6 시나리오에서의 최대무강수지속기간 변화'
  },
  {
    id: 'ssp26-7',
    title: '강수강도',
    filename: 'SSP_126_강수강도.png',
    path: '/image_ssp2.6/SSP_126_강수강도.png',
    description: 'SSP 2.6 시나리오에서의 강수강도 변화'
  },
  {
    id: 'ssp26-8',
    title: '열대야일수',
    filename: 'SSP_126_열대야일수_1.png',
    path: '/image_ssp2.6/SSP_126_열대야일수_1.png',
    description: 'SSP 2.6 시나리오에서의 열대야일수 변화'
  },
  {
    id: 'ssp26-9',
    title: '평균 최고기온',
    filename: 'SSP_126_평균_최고기온.png',
    path: '/image_ssp2.6/SSP_126_평균_최고기온.png',
    description: 'SSP 2.6 시나리오에서의 평균 최고기온 변화'
  },
  {
    id: 'ssp26-10',
    title: '연평균기온',
    filename: 'SSP_126_연평균기온.png',
    path: '/image_ssp2.6/SSP_126_연평균기온.png',
    description: 'SSP 2.6 시나리오에서의 연평균기온 변화'
  }
];

const ssp85Images: ClimateImage[] = [
  {
    id: 'ssp85-1',
    title: '호우일수',
    filename: 'SSP_585_호우일수_1.png',
    path: '/image_ssp8.5/SSP_585_호우일수_1.png',
    description: 'SSP 8.5 시나리오에서의 호우일수 변화'
  },
  {
    id: 'ssp85-2',
    title: '최대무강수지속기간',
    filename: 'SSP_585_최대무강수지속기간.png',
    path: '/image_ssp8.5/SSP_585_최대무강수지속기간.png',
    description: 'SSP 8.5 시나리오에서의 최대무강수지속기간 변화'
  },
  {
    id: 'ssp85-3',
    title: '1일 최대강수량',
    filename: 'SSP_585_1일_최대강수량.png',
    path: '/image_ssp8.5/SSP_585_1일_최대강수량.png',
    description: 'SSP 8.5 시나리오에서의 1일 최대강수량 변화'
  },
  {
    id: 'ssp85-4',
    title: '한파일수',
    filename: 'SSP_585_한파일수.png',
    path: '/image_ssp8.5/SSP_585_한파일수.png',
    description: 'SSP 8.5 시나리오에서의 한파일수 변화'
  },
  {
    id: 'ssp85-5',
    title: '강수강도',
    filename: 'SSP_585_강수강도.png',
    path: '/image_ssp8.5/SSP_585_강수강도.png',
    description: 'SSP 8.5 시나리오에서의 강수강도 변화'
  },
  {
    id: 'ssp85-6',
    title: '폭염일수',
    filename: 'SSP_585_폭염_일수_1.png',
    path: '/image_ssp8.5/SSP_585_폭염_일수_1.png',
    description: 'SSP 8.5 시나리오에서의 폭염일수 변화'
  },
  {
    id: 'ssp85-7',
    title: '열대야일수',
    filename: 'SSP_585_열대야일수_1.png',
    path: '/image_ssp8.5/SSP_585_열대야일수_1.png',
    description: 'SSP 8.5 시나리오에서의 열대야일수 변화'
  },
  {
    id: 'ssp85-8',
    title: '평균 최고기온',
    filename: 'SSP_585_평균_최고기온.png',
    path: '/image_ssp8.5/SSP_585_평균_최고기온.png',
    description: 'SSP 8.5 시나리오에서의 평균 최고기온 변화'
  },
  {
    id: 'ssp85-9',
    title: '강수량',
    filename: 'SSP_585_강수량.png',
    path: '/image_ssp8.5/SSP_585_강수량.png',
    description: 'SSP 8.5 시나리오에서의 강수량 변화'
  },
  {
    id: 'ssp85-10',
    title: '연평균기온',
    filename: 'SSP_585_연평균기온.png',
    path: '/image_ssp8.5/SSP_585_연평균기온.png',
    description: 'SSP 8.5 시나리오에서의 연평균기온 변화'
  }
];

// Climate 분석 이미지들
const climateAnalysisImages: ClimateAnalysisImage[] = [
  {
    id: 'climate-1',
    title: 'Wind, SLP, SST 분석 (2013-2015)',
    filename: 'Wind_SLP_SST_2013-2015.png',
    path: '/climate/Wind_SLP_SST_2013-2015.png',
    description: '2013-2015년간의 바람, 해면기압, 해수면온도 분석 결과',
    category: '기상해양분석'
  },
  {
    id: 'climate-2',
    title: '벡터 예시 1',
    filename: 'vector_example1.png',
    path: '/climate/vector_example1.png',
    description: '벡터 필드 분석 예시 1',
    category: '벡터분석'
  },
  {
    id: 'climate-3',
    title: '벡터 예시 2',
    filename: 'vector_example2.png',
    path: '/climate/vector_example2.png',
    description: '벡터 필드 분석 예시 2',
    category: '벡터분석'
  },
  {
    id: 'climate-4',
    title: '벡터 예시 3',
    filename: 'vector_example3.png',
    path: '/climate/vector_example3.png',
    description: '벡터 필드 분석 예시 3',
    category: '벡터분석'
  },
  {
    id: 'climate-5',
    title: 'T-test 자유도 트렌드',
    filename: 'T-test_dof_trend.png',
    path: '/climate/T-test_dof_trend.png',
    description: 'T-test 자유도 트렌드 분석 결과',
    category: '통계분석'
  },
  {
    id: 'climate-6',
    title: 'T-test 자유도 회귀',
    filename: 'T-test_dof_regression.png',
    path: '/climate/T-test_dof_regression.png',
    description: 'T-test 자유도 회귀 분석 결과',
    category: '통계분석'
  },
  {
    id: 'climate-7',
    title: 'T-test 자유도 상관관계',
    filename: 'T-test_dof_correlation.png',
    path: '/climate/T-test_dof_correlation.png',
    description: 'T-test 자유도 상관관계 분석 결과',
    category: '통계분석'
  },
  {
    id: 'climate-8',
    title: 'T-test 분석',
    filename: 'T-test.png',
    path: '/climate/T-test.png',
    description: 'T-test 통계 분석 결과',
    category: '통계분석'
  },
  {
    id: 'climate-9',
    title: '온도 이상 수직 단면',
    filename: 'Tanom_vertical_cross_section.png',
    path: '/climate/Tanom_vertical_cross_section.png',
    description: '온도 이상의 수직 단면 분석',
    category: '기온분석'
  },
  {
    id: 'climate-10',
    title: 'SST 트렌드 제거 (Cartopy)',
    filename: 'sst_trend_detrend_cartopy.png',
    path: '/climate/sst_trend_detrend_cartopy.png',
    description: 'Cartopy를 사용한 해수면온도 트렌드 제거 분석',
    category: '해수면온도분석'
  },
  {
    id: 'climate-11',
    title: 'SST 히트맵',
    filename: 'sst_heatmap.png',
    path: '/climate/sst_heatmap.png',
    description: '해수면온도 히트맵 분석',
    category: '해수면온도분석'
  },
  {
    id: 'climate-12',
    title: 'SST EOF 시계열',
    filename: 'sst_eof_ts.png',
    path: '/climate/sst_eof_ts.png',
    description: '해수면온도 EOF 시계열 분석',
    category: '해수면온도분석'
  },
  {
    id: 'climate-13',
    title: 'SST EOF 분석',
    filename: 'sst_eof.png',
    path: '/climate/sst_eof.png',
    description: '해수면온도 EOF 분석 결과',
    category: '해수면온도분석'
  },
  {
    id: 'climate-14',
    title: 'SST 상관관계 및 회귀',
    filename: 'sst_corr_reg.png',
    path: '/climate/sst_corr_reg.png',
    description: '해수면온도 상관관계 및 회귀 분석',
    category: '해수면온도분석'
  },
  {
    id: 'climate-15',
    title: 'ONI 시계열',
    filename: 'ONI_timeseries.png',
    path: '/climate/ONI_timeseries.png',
    description: 'Oceanic Niño Index 시계열 분석',
    category: '엘니뇨분석'
  },
  {
    id: 'climate-16',
    title: '고도 이상 PNA',
    filename: 'hgtanom_PNA.png',
    path: '/climate/hgtanom_PNA.png',
    description: 'Pacific-North America 패턴의 고도 이상 분석',
    category: '대기순환분석'
  },
  {
    id: 'climate-17',
    title: 'GPM PCT89 글로벌 맵',
    filename: 'GPM_PCT89_GlobalMap.png',
    path: '/climate/GPM_PCT89_GlobalMap.png',
    description: 'Global Precipitation Mission PCT89 글로벌 맵',
    category: '강수분석'
  },
  {
    id: 'climate-18',
    title: 'DPR Z-profile 샘플',
    filename: 'DPR_Zprofile_sample.png',
    path: '/climate/DPR_Zprofile_sample.png',
    description: 'Dual-frequency Precipitation Radar Z-profile 샘플',
    category: '강수분석'
  },
  {
    id: 'climate-19',
    title: 'AMO-표면온도 상관관계',
    filename: 'Corr_AMO_SurfaceTemp.png',
    path: '/climate/Corr_AMO_SurfaceTemp.png',
    description: 'Atlantic Multidecadal Oscillation과 표면온도 상관관계',
    category: '대기순환분석'
  },
  {
    id: 'climate-20',
    title: 'AMO-300hPa 상관관계',
    filename: 'Corr_AMO_300hPa.png',
    path: '/climate/Corr_AMO_300hPa.png',
    description: 'Atlantic Multidecadal Oscillation과 300hPa 상관관계',
    category: '대기순환분석'
  },
  {
    id: 'climate-21',
    title: '시간 필터 예시',
    filename: 'Code6-2-1_Time_Filter_example.png',
    path: '/climate/Code6-2-1_Time_Filter_example.png',
    description: '시간 필터 적용 예시',
    category: '시계열분석'
  },
  {
    id: 'climate-22',
    title: '산점도 + 히스토그램 예시',
    filename: 'Code6-1-3_Scatter+JHist_example.png',
    path: '/climate/Code6-1-3_Scatter+JHist_example.png',
    description: '산점도와 히스토그램 결합 분석 예시',
    category: '통계분석'
  },
  {
    id: 'climate-23',
    title: '수평 막대 + 바이올린 플롯',
    filename: 'Code6-1-2_barh+Violin_example.png',
    path: '/climate/Code6-1-2_barh+Violin_example.png',
    description: '수평 막대 그래프와 바이올린 플롯 결합 예시',
    category: '통계분석'
  },
  {
    id: 'climate-24',
    title: '수직 막대 그래프',
    filename: 'Code6-1-1_vertical_bar_example.png',
    path: '/climate/Code6-1-1_vertical_bar_example.png',
    description: '수직 막대 그래프 분석 예시',
    category: '통계분석'
  }
];

// HL만도 기후시나리오 이미지들
const hlMandoImages: ClimateAnalysisImage[] = [
  // SSP126 2026-2030년
  {
    id: 'hlmando-ssp126-1',
    title: 'HL만도 - SSP126 연강수량 (2026-2030)',
    filename: 'SSP126_화성시_연강수량_2026_2030.png',
    path: '/HL만도/SSP126_화성시_연강수량_2026_2030.png',
    description: 'HL만도 화성시 SSP126 시나리오 연강수량 예측 (2026-2030)',
    category: 'HL만도-SSP126'
  },
  {
    id: 'hlmando-ssp126-2',
    title: 'HL만도 - SSP126 호우일수 (2026-2030)',
    filename: 'SSP126_화성시_호우일수_2026_2030.png',
    path: '/HL만도/SSP126_화성시_호우일수_2026_2030.png',
    description: 'HL만도 화성시 SSP126 시나리오 호우일수 예측 (2026-2030)',
    category: 'HL만도-SSP126'
  },
  {
    id: 'hlmando-ssp126-3',
    title: 'HL만도 - SSP126 폭염일수 (2026-2030)',
    filename: 'SSP126_화성시_폭염일수_2026_2030.png',
    path: '/HL만도/SSP126_화성시_폭염일수_2026_2030.png',
    description: 'HL만도 화성시 SSP126 시나리오 폭염일수 예측 (2026-2030)',
    category: 'HL만도-SSP126'
  },
  {
    id: 'hlmando-ssp126-4',
    title: 'HL만도 - SSP126 열대야일수 (2026-2030)',
    filename: 'SSP126_화성시_열대야일수_2026_2030.png',
    path: '/HL만도/SSP126_화성시_열대야일수_2026_2030.png',
    description: 'HL만도 화성시 SSP126 시나리오 열대야일수 예측 (2026-2030)',
    category: 'HL만도-SSP126'
  },
  {
    id: 'hlmando-ssp126-5',
    title: 'HL만도 - SSP126 연평균기온 (2026-2030)',
    filename: 'SSP126_화성시_연평균기온_2026_2030.png',
    path: '/HL만도/SSP126_화성시_연평균기온_2026_2030.png',
    description: 'HL만도 화성시 SSP126 시나리오 연평균기온 예측 (2026-2030)',
    category: 'HL만도-SSP126'
  },
  // SSP585 2026-2030년
  {
    id: 'hlmando-ssp585-1',
    title: 'HL만도 - SSP585 연강수량 (2026-2030)',
    filename: 'SSP585_화성시_연강수량_2026_2030.png',
    path: '/HL만도/SSP585_화성시_연강수량_2026_2030.png',
    description: 'HL만도 화성시 SSP585 시나리오 연강수량 예측 (2026-2030)',
    category: 'HL만도-SSP585'
  },
  {
    id: 'hlmando-ssp585-2',
    title: 'HL만도 - SSP585 호우일수 (2026-2030)',
    filename: 'SSP585_화성시_호우일수_2026_2030.png',
    path: '/HL만도/SSP585_화성시_호우일수_2026_2030.png',
    description: 'HL만도 화성시 SSP585 시나리오 호우일수 예측 (2026-2030)',
    category: 'HL만도-SSP585'
  },
  {
    id: 'hlmando-ssp585-3',
    title: 'HL만도 - SSP585 폭염일수 (2026-2030)',
    filename: 'SSP585_화성시_폭염일수_2026_2030.png',
    path: '/HL만도/SSP585_화성시_폭염일수_2026_2030.png',
    description: 'HL만도 화성시 SSP585 시나리오 폭염일수 예측 (2026-2030)',
    category: 'HL만도-SSP585'
  },
  {
    id: 'hlmando-ssp585-4',
    title: 'HL만도 - SSP585 열대야일수 (2026-2030)',
    filename: 'SSP585_화성시_열대야일수_2026_2030.png',
    path: '/HL만도/SSP585_화성시_열대야일수_2026_2030.png',
    description: 'HL만도 화성시 SSP585 시나리오 열대야일수 예측 (2026-2030)',
    category: 'HL만도-SSP585'
  },
  {
    id: 'hlmando-ssp585-5',
    title: 'HL만도 - SSP585 연평균기온 (2026-2030)',
    filename: 'SSP585_화성시_연평균기온_2026_2030.png',
    path: '/HL만도/SSP585_화성시_연평균기온_2026_2030.png',
    description: 'HL만도 화성시 SSP585 시나리오 연평균기온 예측 (2026-2030)',
    category: 'HL만도-SSP585'
  }
];

// 한온시스템 기후시나리오 이미지들
const hanonSystemImages: ClimateAnalysisImage[] = [
  // SSP126 2026-2030년
  {
    id: 'hanon-ssp126-1',
    title: '한온시스템 - SSP126 연강수량 (2026-2030)',
    filename: 'SSP126_강남구_연강수량_2026_2030.png',
    path: '/한온시스템/SSP126_강남구_연강수량_2026_2030.png',
    description: '한온시스템 강남구 SSP126 시나리오 연강수량 예측 (2026-2030)',
    category: '한온시스템-SSP126'
  },
  {
    id: 'hanon-ssp126-2',
    title: '한온시스템 - SSP126 호우일수 (2026-2030)',
    filename: 'SSP126_강남구_호우일수_2026_2030.png',
    path: '/한온시스템/SSP126_강남구_호우일수_2026_2030.png',
    description: '한온시스템 강남구 SSP126 시나리오 호우일수 예측 (2026-2030)',
    category: '한온시스템-SSP126'
  },
  {
    id: 'hanon-ssp126-3',
    title: '한온시스템 - SSP126 폭염일수 (2026-2030)',
    filename: 'SSP126_강남구_폭염일수_2026_2030.png',
    path: '/한온시스템/SSP126_강남구_폭염일수_2026_2030.png',
    description: '한온시스템 강남구 SSP126 시나리오 폭염일수 예측 (2026-2030)',
    category: '한온시스템-SSP126'
  },
  {
    id: 'hanon-ssp126-4',
    title: '한온시스템 - SSP126 열대야일수 (2026-2030)',
    filename: 'SSP126_강남구_열대야일수_2026_2030.png',
    path: '/한온시스템/SSP126_강남구_열대야일수_2026_2030.png',
    description: '한온시스템 강남구 SSP126 시나리오 열대야일수 예측 (2026-2030)',
    category: '한온시스템-SSP126'
  },
  {
    id: 'hanon-ssp126-5',
    title: '한온시스템 - SSP126 연평균기온 (2026-2030)',
    filename: 'SSP126_강남구_연평균기온_2026_2030.png',
    path: '/한온시스템/SSP126_강남구_연평균기온_2026_2030.png',
    description: '한온시스템 강남구 SSP126 시나리오 연평균기온 예측 (2026-2030)',
    category: '한온시스템-SSP126'
  },
  // SSP585 2026-2030년
  {
    id: 'hanon-ssp585-1',
    title: '한온시스템 - SSP585 연강수량 (2026-2030)',
    filename: 'SSP585_강남구_연강수량_2026_2030.png',
    path: '/한온시스템/SSP585_강남구_연강수량_2026_2030.png',
    description: '한온시스템 강남구 SSP585 시나리오 연강수량 예측 (2026-2030)',
    category: '한온시스템-SSP585'
  },
  {
    id: 'hanon-ssp585-2',
    title: '한온시스템 - SSP585 호우일수 (2026-2030)',
    filename: 'SSP585_강남구_호우일수_2026_2030.png',
    path: '/한온시스템/SSP585_강남구_호우일수_2026_2030.png',
    description: '한온시스템 강남구 SSP585 시나리오 호우일수 예측 (2026-2030)',
    category: '한온시스템-SSP585'
  },
  {
    id: 'hanon-ssp585-3',
    title: '한온시스템 - SSP585 폭염일수 (2026-2030)',
    filename: 'SSP585_강남구_폭염일수_2026_2030.png',
    path: '/한온시스템/SSP585_강남구_폭염일수_2026_2030.png',
    description: '한온시스템 강남구 SSP585 시나리오 폭염일수 예측 (2026-2030)',
    category: '한온시스템-SSP585'
  },
  {
    id: 'hanon-ssp585-4',
    title: '한온시스템 - SSP585 열대야일수 (2026-2030)',
    filename: 'SSP585_강남구_열대야일수_2026_2030.png',
    path: '/한온시스템/SSP585_강남구_열대야일수_2026_2030.png',
    description: '한온시스템 강남구 SSP585 시나리오 열대야일수 예측 (2026-2030)',
    category: '한온시스템-SSP585'
  },
  {
    id: 'hanon-ssp585-5',
    title: '한온시스템 - SSP585 연평균기온 (2026-2030)',
    filename: 'SSP585_강남구_연평균기온_2026_2030.png',
    path: '/한온시스템/SSP585_강남구_연평균기온_2026_2030.png',
    description: '한온시스템 강남구 SSP585 시나리오 연평균기온 예측 (2026-2030)',
    category: '한온시스템-SSP585'
  }
];

// 현대모비스 기후시나리오 이미지들
const hyundaiMobisImages: ClimateAnalysisImage[] = [
  // SSP126 2026-2030년
  {
    id: 'mobis-ssp126-1',
    title: '현대모비스 - SSP126 연강수량 (2026-2030)',
    filename: 'SSP126_포항시_연강수량_2026_2030.png',
    path: '/현대모비스/SSP126_포항시_연강수량_2026_2030.png',
    description: '현대모비스 포항시 SSP126 시나리오 연강수량 예측 (2026-2030)',
    category: '현대모비스-SSP126'
  },
  {
    id: 'mobis-ssp126-2',
    title: '현대모비스 - SSP126 호우일수 (2026-2030)',
    filename: 'SSP126_포항시_호우일수_2026_2030.png',
    path: '/현대모비스/SSP126_포항시_호우일수_2026_2030.png',
    description: '현대모비스 포항시 SSP126 시나리오 호우일수 예측 (2026-2030)',
    category: '현대모비스-SSP126'
  },
  {
    id: 'mobis-ssp126-3',
    title: '현대모비스 - SSP126 폭염일수 (2026-2030)',
    filename: 'SSP126_포항시_폭염일수_2026_2030.png',
    path: '/현대모비스/SSP126_포항시_폭염일수_2026_2030.png',
    description: '현대모비스 포항시 SSP126 시나리오 폭염일수 예측 (2026-2030)',
    category: '현대모비스-SSP126'
  },
  {
    id: 'mobis-ssp126-4',
    title: '현대모비스 - SSP126 열대야일수 (2026-2030)',
    filename: 'SSP126_포항시_열대야일수_2026_2030.png',
    path: '/현대모비스/SSP126_포항시_열대야일수_2026_2030.png',
    description: '현대모비스 포항시 SSP126 시나리오 열대야일수 예측 (2026-2030)',
    category: '현대모비스-SSP126'
  },
  {
    id: 'mobis-ssp126-5',
    title: '현대모비스 - SSP126 연평균기온 (2026-2030)',
    filename: 'SSP126_포항시_연평균기온_2026_2030.png',
    path: '/현대모비스/SSP126_포항시_연평균기온_2026_2030.png',
    description: '현대모비스 포항시 SSP126 시나리오 연평균기온 예측 (2026-2030)',
    category: '현대모비스-SSP126'
  },
  // SSP585 2026-2030년
  {
    id: 'mobis-ssp585-1',
    title: '현대모비스 - SSP585 연강수량 (2026-2030)',
    filename: 'SSP585_포항시_연강수량_2026_2030.png',
    path: '/현대모비스/SSP585_포항시_연강수량_2026_2030.png',
    description: '현대모비스 포항시 SSP585 시나리오 연강수량 예측 (2026-2030)',
    category: '현대모비스-SSP585'
  },
  {
    id: 'mobis-ssp585-2',
    title: '현대모비스 - SSP585 호우일수 (2026-2030)',
    filename: 'SSP585_포항시_호우일수_2026_2030.png',
    path: '/현대모비스/SSP585_포항시_호우일수_2026_2030.png',
    description: '현대모비스 포항시 SSP585 시나리오 호우일수 예측 (2026-2030)',
    category: '현대모비스-SSP585'
  },
  {
    id: 'mobis-ssp585-3',
    title: '현대모비스 - SSP585 폭염일수 (2026-2030)',
    filename: 'SSP585_포항시_폭염일수_2026_2030.png',
    path: '/현대모비스/SSP585_포항시_폭염일수_2026_2030.png',
    description: '현대모비스 포항시 SSP585 시나리오 폭염일수 예측 (2026-2030)',
    category: '현대모비스-SSP585'
  },
  {
    id: 'mobis-ssp585-4',
    title: '현대모비스 - SSP585 열대야일수 (2026-2030)',
    filename: 'SSP585_포항시_열대야일수_2026_2030.png',
    path: '/현대모비스/SSP585_포항시_열대야일수_2026_2030.png',
    description: '현대모비스 포항시 SSP585 시나리오 열대야일수 예측 (2026-2030)',
    category: '현대모비스-SSP585'
  },
  {
    id: 'mobis-ssp585-5',
    title: '현대모비스 - SSP585 연평균기온 (2026-2030)',
    filename: 'SSP585_포항시_연평균기온_2026_2030.png',
    path: '/현대모비스/SSP585_포항시_연평균기온_2026_2030.png',
    description: '현대모비스 포항시 SSP585 시나리오 연평균기온 예측 (2026-2030)',
    category: '현대모비스-SSP585'
  }
];

export default function ClimateScenariosPage() {
  const router = useRouter();
  const [selectedTab, setSelectedTab] = useState<'ssp26' | 'ssp85' | 'climate' | 'hlmando' | 'hanon' | 'mobis'>('ssp26');
  const [selectedScenario, setSelectedScenario] = useState<'ssp26' | 'ssp85'>('ssp26');
  const [selectedImage, setSelectedImage] = useState<ClimateImage | ClimateAnalysisImage | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  
  // 그래프 생성 모달을 위한 새로운 상태들
  const [showGraphModal, setShowGraphModal] = useState(false);
  const [graphSettings, setGraphSettings] = useState({
    scenario: 'SSP126',
    variable: 'HW33',
    startYear: 2021,
    endYear: 2030,
    region: '전체 지역'
  });
  const [generatedGraph, setGeneratedGraph] = useState<string | null>(null);
  const [isGenerating, setIsGenerating] = useState(false);

  const handleBack = () => {
    router.push('/tcfd');
  };

  const handleImageClick = (image: ClimateImage) => {
    setSelectedImage(image);
  };

  const closeModal = () => {
    setSelectedImage(null);
  };

  const downloadImage = (imageSrc: string, imageTitle: string) => {
    const link = document.createElement('a');
    link.href = imageSrc;
    link.download = `${imageTitle}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // 그래프 생성 모달 관련 함수들
  const openGraphModal = () => {
    setShowGraphModal(true);
    setGeneratedGraph(null);
  };

  const closeGraphModal = () => {
    setShowGraphModal(false);
    setGeneratedGraph(null);
  };

  const generateGraph = async () => {
    setIsGenerating(true);
    try {
      // API 호출하여 그래프 생성
      const response = await apiClient.get('/api/v1/tcfd/climate-scenarios/table-image', {
        params: {
          scenario_code: graphSettings.scenario,
          variable_code: graphSettings.variable,
          start_year: graphSettings.startYear,
          end_year: graphSettings.endYear
        }
      });

      if (response.data.success) {
        setGeneratedGraph(response.data.image_data);
      } else {
        alert('그래프 생성에 실패했습니다.');
      }
    } catch (error) {
      console.error('그래프 생성 오류:', error);
      alert('그래프 생성 중 오류가 발생했습니다.');
    } finally {
      setIsGenerating(false);
    }
  };

  const downloadGeneratedGraph = () => {
    if (generatedGraph) {
      const link = document.createElement('a');
      link.href = generatedGraph;
      link.download = `${graphSettings.scenario}_${graphSettings.variable}_${graphSettings.startYear}_${graphSettings.endYear}.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  const getCurrentImages = () => {
    if (selectedTab === 'climate') {
      return climateAnalysisImages;
    } else if (selectedTab === 'hlmando') {
      return selectedScenario === 'ssp26' 
        ? hlMandoImages.filter(img => img.category === 'HL만도-SSP126')
        : hlMandoImages.filter(img => img.category === 'HL만도-SSP585');
    } else if (selectedTab === 'hanon') {
      return selectedScenario === 'ssp26' 
        ? hanonSystemImages.filter(img => img.category === '한온시스템-SSP126')
        : hanonSystemImages.filter(img => img.category === '한온시스템-SSP585');
    } else if (selectedTab === 'mobis') {
      return selectedScenario === 'ssp26' 
        ? hyundaiMobisImages.filter(img => img.category === '현대모비스-SSP126')
        : hyundaiMobisImages.filter(img => img.category === '현대모비스-SSP585');
    }
    return selectedScenario === 'ssp26' ? ssp26Images : ssp85Images;
  };

  const currentImages = getCurrentImages();

  // 인증 상태 확인
  useEffect(() => {
    // 클라이언트 사이드에서만 인증 확인
    if (typeof window !== 'undefined') {
      const checkAuth = async () => {
        try {
          // localStorage에서 토큰 확인
          const token = localStorage.getItem('auth_token');
          if (!token) {
            console.log('❌ 인증 토큰이 없습니다');
            router.push('/login');
            return;
          }

          // 토큰 유효성 확인 (API 호출)
          try {
            await apiClient.get('/api/v1/auth/verify');
            console.log('✅ 인증 토큰이 유효합니다');
            setIsAuthenticated(true);
          } catch (error: any) {
            if (error.response?.status === 401) {
              console.log('❌ 인증 토큰이 만료되었습니다');
              // 토큰 갱신 시도
              const refreshed = await useAuthStore.getState().refreshToken();
              if (refreshed) {
                console.log('✅ 토큰이 갱신되었습니다');
                setIsAuthenticated(true);
              } else {
                console.log('❌ 토큰 갱신 실패');
                router.push('/login');
              }
            } else {
              console.log('❌ 인증 확인 중 오류 발생');
              router.push('/login');
            }
          }
        } catch (error) {
          console.error('❌ 인증 확인 실패:', error);
          router.push('/login');
        }
      };

      checkAuth();
    }
  }, [router]);

  // 인증되지 않은 경우 로딩 화면 표시
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <Header />
        <div className="pt-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="text-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-4 text-gray-600">인증 확인 중...</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="pt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* 헤더 */}
          <div className="mb-8">
            <button
              onClick={handleBack}
              className="mb-4 flex items-center text-blue-600 hover:text-blue-800 transition-colors"
            >
              <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              TCFD 페이지로 돌아가기
            </button>
            
            <div className="flex items-center justify-between mb-2">
              <h1 className="text-3xl font-bold text-gray-900">기후 시나리오 분석</h1>
              <button
                onClick={openGraphModal}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                <span>더보기</span>
              </button>
            </div>
            <p className="text-gray-600">SSP 2.6과 SSP 8.5 시나리오에 따른 기후 변화 예측 이미지</p>
          </div>

          {/* 메인 탭 선택 */}
          <div className="mb-8">
            <div className="flex flex-wrap space-x-1 bg-gray-200 p-1 rounded-lg mb-6">
              <button
                onClick={() => setSelectedTab('ssp26')}
                className={`flex-1 min-w-0 py-3 px-4 rounded-md font-medium transition-colors text-sm ${
                  selectedTab === 'ssp26'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                SSP 2.6
              </button>
              <button
                onClick={() => setSelectedTab('ssp85')}
                className={`flex-1 min-w-0 py-3 px-4 rounded-md font-medium transition-colors text-sm ${
                  selectedTab === 'ssp85'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                SSP 8.5
              </button>
              <button
                onClick={() => setSelectedTab('hlmando')}
                className={`flex-1 min-w-0 py-3 px-4 rounded-md font-medium transition-colors text-sm ${
                  selectedTab === 'hlmando'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                HL만도
              </button>
              <button
                onClick={() => setSelectedTab('hanon')}
                className={`flex-1 min-w-0 py-3 px-4 rounded-md font-medium transition-colors text-sm ${
                  selectedTab === 'hanon'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                한온시스템
              </button>
              <button
                onClick={() => setSelectedTab('mobis')}
                className={`flex-1 min-w-0 py-3 px-4 rounded-md font-medium transition-colors text-sm ${
                  selectedTab === 'mobis'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-600 hover:text-gray-800'
                }`}
              >
                현대모비스
              </button>
              <button
                onClick={() => setSelectedTab('climate')}
                className={`flex-1 min-w-0 py-3 px-4 rounded-md font-medium transition-colors text-sm ${
                  selectedTab === 'climate'
                    ? 'bg-white text-blue-600 shadow-sm'
                    : 'text-gray-800'
                }`}
              >
                기후 분석
              </button>
            </div>

            {/* SSP 시나리오 하위 탭 (회사별 탭에서만 표시) */}
            {(selectedTab === 'hlmando' || selectedTab === 'hanon' || selectedTab === 'mobis') && (
              <div className="flex space-x-1 bg-gray-100 p-1 rounded-lg">
                <button
                  onClick={() => setSelectedScenario('ssp26')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    selectedScenario === 'ssp26'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  SSP 2.6
                </button>
                <button
                  onClick={() => setSelectedScenario('ssp85')}
                  className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
                    selectedScenario === 'ssp85'
                      ? 'bg-white text-blue-600 shadow-sm'
                      : 'text-gray-600 hover:text-gray-800'
                  }`}
                >
                  SSP 8.5
                </button>
              </div>
            )}
          </div>

          {/* 이미지 갤러리 */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
            {currentImages.map((image) => (
              <div
                key={image.id}
                className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow cursor-pointer"
                onClick={() => handleImageClick(image)}
              >
                <div className="aspect-w-16 aspect-h-9 bg-gray-100 relative">
                  <Image
                    src={image.path}
                    alt={image.title}
                    width={640}
                    height={360}
                    className="w-full h-48 object-cover"
                  />
                  {/* 다운로드 버튼 */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      downloadImage(image.path, image.title);
                    }}
                    className="absolute top-2 right-2 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700 transition-colors shadow-lg"
                    title="이미지 다운로드"
                  >
                    <span className="text-sm">⬇️</span>
                  </button>
                </div>
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">{image.title}</h3>
                  <p className="text-sm text-gray-600 line-clamp-2">{image.description}</p>
                  {'category' in image && (
                    <div className="mt-2">
                      <span className="inline-block bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">
                        {(image as ClimateAnalysisImage).category}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 이미지 상세 모달 */}
      {selectedImage && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-4">
                <h2 className="text-2xl font-bold text-gray-900">{selectedImage.title}</h2>
                <div className="flex items-center space-x-2">
                  <button
                    onClick={() => downloadImage(selectedImage.path, selectedImage.title)}
                    className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 transition-colors flex items-center space-x-1"
                  >
                    <span>⬇️</span>
                    <span>다운로드</span>
                  </button>
                  <button
                    onClick={closeModal}
                    className="text-gray-400 hover:text-gray-600 transition-colors"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <div className="mb-4">
                <Image
                  src={selectedImage.path}
                  alt={selectedImage.title}
                  width={1024}
                  height={576}
                  className="w-full h-auto rounded-lg"
                />
              </div>
              
              <div className="mb-4">
                <h3 className="font-semibold text-gray-900 mb-2">설명</h3>
                <p className="text-gray-600">{selectedImage.description}</p>
              </div>
              
              <div className="text-sm text-gray-500">
                <p>파일명: {selectedImage.filename}</p>
                {'category' in selectedImage ? (
                  <p>카테고리: {(selectedImage as ClimateAnalysisImage).category}</p>
                ) : (
                  <p>시나리오: {selectedScenario === 'ssp26' ? 'SSP 2.6' : 'SSP 8.5'}</p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 그래프 생성 모달 */}
      {showGraphModal && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-auto">
            <div className="p-6">
              <div className="flex justify-between items-start mb-6">
                <h2 className="text-2xl font-bold text-gray-900">직접 그래프 생성</h2>
                <button
                  onClick={closeGraphModal}
                  className="text-gray-400 hover:text-gray-600 transition-colors"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {/* 그래프 설정 폼 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                {/* 시나리오 선택 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    기후 시나리오
                  </label>
                  <select
                    value={graphSettings.scenario}
                    onChange={(e) => setGraphSettings({...graphSettings, scenario: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="SSP126">SSP1-2.6 (저탄소 시나리오)</option>
                    <option value="SSP585">SSP5-8.5 (고탄소 시나리오)</option>
                  </select>
                </div>

                {/* 기후 변수 선택 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    기후 변수
                  </label>
                  <select
                    value={graphSettings.variable}
                    onChange={(e) => setGraphSettings({...graphSettings, variable: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="HW33">폭염일수 (최고기온 33°C 이상)</option>
                    <option value="RN">연강수량 (mm)</option>
                    <option value="TA">연평균기온 (°C)</option>
                    <option value="TR25">열대야일수 (최저기온 25°C 이상)</option>
                    <option value="RAIN80">호우일수 (일강수량 80mm 이상)</option>
                  </select>
                </div>

                {/* 시작 연도 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    시작 연도
                  </label>
                  <select
                    value={graphSettings.startYear}
                    onChange={(e) => setGraphSettings({...graphSettings, startYear: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {Array.from({length: 80}, (_, i) => 2021 + i).map(year => (
                      <option key={year} value={year}>{year}년</option>
                    ))}
                  </select>
                </div>

                {/* 종료 연도 */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    종료 연도
                  </label>
                  <select
                    value={graphSettings.endYear}
                    onChange={(e) => setGraphSettings({...graphSettings, endYear: parseInt(e.target.value)})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {Array.from({length: 80}, (_, i) => 2021 + i).map(year => (
                      <option key={year} value={year}>{year}년</option>
                    ))}
                  </select>
                </div>
              </div>

              {/* 그래프 생성 버튼 */}
              <div className="flex justify-center mb-6">
                <button
                  onClick={generateGraph}
                  disabled={isGenerating}
                  className="px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors flex items-center space-x-2"
                >
                  {isGenerating ? (
                    <>
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                      <span>생성 중...</span>
                    </>
                  ) : (
                    <>
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      <span>그래프 생성</span>
                    </>
                  )}
                </button>
              </div>

              {/* 생성된 그래프 표시 */}
              {generatedGraph && (
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-4">
                  <div className="text-center mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 mb-2">
                      {graphSettings.scenario === 'SSP126' ? 'SSP1-2.6 (저탄소)' : 'SSP5-8.5 (고탄소)'} - 
                      {graphSettings.variable === 'HW33' ? '폭염일수' : 
                       graphSettings.variable === 'RN' ? '연강수량' :
                       graphSettings.variable === 'TA' ? '연평균기온' :
                       graphSettings.variable === 'TR25' ? '열대야일수' : '호우일수'}
                      ({graphSettings.startYear}년 ~ {graphSettings.endYear}년)
                    </h3>
                  </div>
                  
                  <div className="flex justify-center mb-4">
                    <img
                      src={generatedGraph}
                      alt="생성된 기후 그래프"
                      className="max-w-full h-auto rounded-lg shadow-lg"
                    />
                  </div>
                  
                  <div className="flex justify-center">
                    <button
                      onClick={downloadGeneratedGraph}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center space-x-2"
                    >
                      <span>⬇️</span>
                      <span>그래프 다운로드</span>
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
