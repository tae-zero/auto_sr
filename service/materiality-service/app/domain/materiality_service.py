from sqlalchemy.orm import Session
from app.domain.repository.materiality_repository import MaterialityRepository
from typing import List, Dict, Any, Optional

class MaterialityService:
    """Materiality 비즈니스 로직 서비스"""
    
    def __init__(self, db: Session):
        self.repository = MaterialityRepository(db)
    
    # Category Table Service Methods
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """모든 카테고리 데이터 조회"""
        categories = self.repository.get_all_categories()
        return [
            {
                "id": cat.id,
                "esg_division": cat.esg_division,
                "materiality_list": cat.materiality_list,
                "created_at": cat.created_at.isoformat() if cat.created_at else None
            }
            for cat in categories
        ]
    
    def get_categories_by_esg_division(self, esg_division: str) -> List[Dict[str, Any]]:
        """ESG 구분별 카테고리 데이터 조회"""
        categories = self.repository.get_categories_by_esg_division(esg_division)
        return [
            {
                "id": cat.id,
                "esg_division": cat.esg_division,
                "materiality_list": cat.materiality_list,
                "created_at": cat.created_at.isoformat() if cat.created_at else None
            }
            for cat in categories
        ]
    
    def get_esg_divisions(self) -> List[str]:
        """ESG 구분 목록 조회"""
        return self.repository.get_esg_divisions()
    
    # KCGS Table Service Methods
    def get_all_kcgs(self) -> List[Dict[str, Any]]:
        """모든 KCGS 데이터 조회"""
        kcgs_data = self.repository.get_all_kcgs()
        return [
            {
                "id": kcgs.id,
                "environment": kcgs.environment,
                "social": kcgs.social,
                "governance": kcgs.governance,
                "created_at": kcgs.created_at.isoformat() if kcgs.created_at else None
            }
            for kcgs in kcgs_data
        ]
    
    def get_kcgs_by_environment(self, environment: str) -> List[Dict[str, Any]]:
        """환경(E) 기준 KCGS 데이터 조회"""
        kcgs_data = self.repository.get_kcgs_by_environment(environment)
        return [
            {
                "id": kcgs.id,
                "environment": kcgs.environment,
                "social": kcgs.social,
                "governance": kcgs.governance,
                "created_at": kcgs.created_at.isoformat() if kcgs.created_at else None
            }
            for kcgs in kcgs_data
        ]
    
    def get_kcgs_by_social(self, social: str) -> List[Dict[str, Any]]:
        """사회(S) 기준 KCGS 데이터 조회"""
        kcgs_data = self.repository.get_kcgs_by_social(social)
        return [
            {
                "id": kcgs.id,
                "environment": kcgs.environment,
                "social": kcgs.social,
                "governance": kcgs.governance,
                "created_at": kcgs.created_at.isoformat() if kcgs.created_at else None
            }
            for kcgs in kcgs_data
        ]
    
    def get_kcgs_by_governance(self, governance: str) -> List[Dict[str, Any]]:
        """거버넌스(G) 기준 KCGS 데이터 조회"""
        kcgs_data = self.repository.get_kcgs_by_governance(governance)
        return [
            {
                "id": kcgs.id,
                "environment": kcgs.environment,
                "social": kcgs.social,
                "governance": kcgs.governance,
                "created_at": kcgs.created_at.isoformat() if kcgs.created_at else None
            }
            for kcgs in kcgs_data
        ]
    
    # SASB Table Service Methods
    def get_all_sasb(self) -> List[Dict[str, Any]]:
        """모든 SASB 데이터 조회"""
        sasb_data = self.repository.get_all_sasb()
        return [
            {
                "id": sasb.id,
                "industry": sasb.industry,
                "disclosure_topic": sasb.disclosure_topic,
                "created_at": sasb.created_at.isoformat() if sasb.created_at else None
            }
            for sasb in sasb_data
        ]
    
    def get_sasb_by_industry(self, industry: str) -> List[Dict[str, Any]]:
        """산업별 SASB 데이터 조회"""
        sasb_data = self.repository.get_sasb_by_industry(industry)
        return [
            {
                "id": sasb.id,
                "industry": sasb.industry,
                "disclosure_topic": sasb.disclosure_topic,
                "created_at": sasb.created_at.isoformat() if sasb.created_at else None
            }
            for sasb in sasb_data
        ]
    
    def get_sasb_industries(self) -> List[str]:
        """SASB 산업 목록 조회"""
        return self.repository.get_sasb_industries()
    
    # Sustainbest E Table Service Methods
    def get_all_sustainbest_e(self) -> List[Dict[str, Any]]:
        """모든 서스틴베스트 E 데이터 조회"""
        sustainbest_e_data = self.repository.get_all_sustainbest_e()
        return [
            {
                "id": data.id,
                "kpi_category_e": data.kpi_category_e,
                "index_name": data.index_name,
                "created_at": data.created_at.isoformat() if data.created_at else None
            }
            for data in sustainbest_e_data
        ]
    
    def get_sustainbest_e_by_category(self, kpi_category_e: str) -> List[Dict[str, Any]]:
        """KPI 카테고리별 서스틴베스트 E 데이터 조회"""
        sustainbest_e_data = self.repository.get_sustainbest_e_by_category(kpi_category_e)
        return [
            {
                "id": data.id,
                "kpi_category_e": data.kpi_category_e,
                "index_name": data.index_name,
                "created_at": data.created_at.isoformat() if data.created_at else None
            }
            for data in sustainbest_e_data
        ]
    
    def get_sustainbest_e_categories(self) -> List[str]:
        """서스틴베스트 E KPI 카테고리 목록 조회"""
        return self.repository.get_sustainbest_e_categories()
    
    # Sustainbest S Table Service Methods
    def get_all_sustainbest_s(self) -> List[Dict[str, Any]]:
        """모든 서스틴베스트 S 데이터 조회"""
        sustainbest_s_data = self.repository.get_all_sustainbest_s()
        return [
            {
                "id": data.id,
                "kpi_category_s": data.kpi_category_s,
                "index_name": data.index_name,
                "created_at": data.created_at.isoformat() if data.created_at else None
            }
            for data in sustainbest_s_data
        ]
    
    def get_sustainbest_s_by_category(self, kpi_category_s: str) -> List[Dict[str, Any]]:
        """KPI 카테고리별 서스틴베스트 S 데이터 조회"""
        sustainbest_s_data = self.repository.get_sustainbest_s_by_category(kpi_category_s)
        return [
            {
                "id": data.id,
                "kpi_category_s": data.kpi_category_s,
                "index_name": data.index_name,
                "created_at": data.created_at.isoformat() if data.created_at else None
            }
            for data in sustainbest_s_data
        ]
    
    def get_sustainbest_s_categories(self) -> List[str]:
        """서스틴베스트 S KPI 카테고리 목록 조회"""
        return self.repository.get_sustainbest_s_categories()
    
    # Sustainbest G Table Service Methods
    def get_all_sustainbest_g(self) -> List[Dict[str, Any]]:
        """모든 서스틴베스트 G 데이터 조회"""
        sustainbest_g_data = self.repository.get_all_sustainbest_g()
        return [
            {
                "id": data.id,
                "kpi_category_g": data.kpi_category_g,
                "index_name": data.index_name,
                "created_at": data.created_at.isoformat() if data.created_at else None
            }
            for data in sustainbest_g_data
        ]
    
    def get_sustainbest_g_by_category(self, kpi_category_g: str) -> List[Dict[str, Any]]:
        """KPI 카테고리별 서스틴베스트 G 데이터 조회"""
        sustainbest_g_data = self.repository.get_sustainbest_g_by_category(kpi_category_g)
        return [
            {
                "id": data.id,
                "kpi_category_g": data.kpi_category_g,
                "index_name": data.index_name,
                "created_at": data.created_at.isoformat() if data.created_at else None
            }
            for data in sustainbest_g_data
        ]
    
    def get_sustainbest_g_categories(self) -> List[str]:
        """서스틴베스트 G KPI 카테고리 목록 조회"""
        return self.repository.get_sustainbest_g_categories()
    
    # 통합 검색 서비스
    def search_materiality_data(self, keyword: str, table_type: str = "all") -> Dict[str, Any]:
        """키워드로 모든 테이블에서 검색"""
        search_results = self.repository.search_materiality_data(keyword, table_type)
        
        # 결과를 JSON 직렬화 가능한 형태로 변환
        formatted_results = {}
        
        if "category" in search_results:
            formatted_results["category"] = [
                {
                    "id": item.id,
                    "esg_division": item.esg_division,
                    "materiality_list": item.materiality_list,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in search_results["category"]
            ]
        
        if "kcgs" in search_results:
            formatted_results["kcgs"] = [
                {
                    "id": item.id,
                    "environment": item.environment,
                    "social": item.social,
                    "governance": item.governance,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in search_results["kcgs"]
            ]
        
        if "sasb" in search_results:
            formatted_results["sasb"] = [
                {
                    "id": item.id,
                    "industry": item.industry,
                    "disclosure_topic": item.disclosure_topic,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in search_results["sasb"]
            ]
        
        if "sustainbest_e" in search_results:
            formatted_results["sustainbest_e"] = [
                {
                    "id": item.id,
                    "kpi_category_e": item.kpi_category_e,
                    "index_name": item.index_name,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in search_results["sustainbest_e"]
            ]
        
        if "sustainbest_s" in search_results:
            formatted_results["sustainbest_s"] = [
                {
                    "id": item.id,
                    "kpi_category_s": item.kpi_category_s,
                    "index_name": item.index_name,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in search_results["sustainbest_s"]
            ]
        
        if "sustainbest_g" in search_results:
            formatted_results["sustainbest_g"] = [
                {
                    "id": item.id,
                    "kpi_category_g": item.kpi_category_g,
                    "index_name": item.index_name,
                    "created_at": item.created_at.isoformat() if item.created_at else None
                }
                for item in search_results["sustainbest_g"]
            ]
        
        return formatted_results
    
    # 통계 정보 서비스
    def get_materiality_statistics(self) -> Dict[str, Any]:
        """Materiality 데이터 통계 정보 조회"""
        return {
            "category_count": len(self.repository.get_all_categories()),
            "kcgs_count": len(self.repository.get_all_kcgs()),
            "sasb_count": len(self.repository.get_all_sasb()),
            "sustainbest_e_count": len(self.repository.get_all_sustainbest_e()),
            "sustainbest_s_count": len(self.repository.get_all_sustainbest_s()),
            "sustainbest_g_count": len(self.repository.get_all_sustainbest_g()),
            "esg_divisions": self.repository.get_esg_divisions(),
            "sasb_industries": self.repository.get_sasb_industries(),
            "sustainbest_e_categories": self.repository.get_sustainbest_e_categories(),
            "sustainbest_s_categories": self.repository.get_sustainbest_s_categories(),
            "sustainbest_g_categories": self.repository.get_sustainbest_g_categories()
        }
