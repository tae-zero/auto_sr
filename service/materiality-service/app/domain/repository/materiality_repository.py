from sqlalchemy.orm import Session
from app.common.models import (
    CategoryTable, KCGSTable, SASBTable, 
    SustainbestETable, SustainbestSTable, SustainbestGTable
)
from typing import List, Optional, Dict, Any

class MaterialityRepository:
    """Materiality 데이터 Repository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Category Table Repository Methods
    def get_all_categories(self) -> List[CategoryTable]:
        """모든 카테고리 데이터 조회"""
        return self.db.query(CategoryTable).all()
    
    def get_categories_by_esg_division(self, esg_division: str) -> List[CategoryTable]:
        """ESG 구분별 카테고리 데이터 조회"""
        return self.db.query(CategoryTable).filter(
            CategoryTable.esg_division == esg_division
        ).all()
    
    def get_esg_divisions(self) -> List[str]:
        """ESG 구분 목록 조회"""
        divisions = self.db.query(CategoryTable.esg_division).distinct().all()
        return [division[0] for division in divisions]
    
    # KCGS Table Repository Methods
    def get_all_kcgs(self) -> List[KCGSTable]:
        """모든 KCGS 데이터 조회"""
        return self.db.query(KCGSTable).all()
    
    def get_kcgs_by_environment(self, environment: str) -> List[KCGSTable]:
        """환경(E) 기준 KCGS 데이터 조회"""
        return self.db.query(KCGSTable).filter(
            KCGSTable.environment == environment
        ).all()
    
    def get_kcgs_by_social(self, social: str) -> List[KCGSTable]:
        """사회(S) 기준 KCGS 데이터 조회"""
        return self.db.query(KCGSTable).filter(
            KCGSTable.social == social
        ).all()
    
    def get_kcgs_by_governance(self, governance: str) -> List[KCGSTable]:
        """거버넌스(G) 기준 KCGS 데이터 조회"""
        return self.db.query(KCGSTable).filter(
            KCGSTable.governance == governance
        ).all()
    
    # SASB Table Repository Methods
    def get_all_sasb(self) -> List[SASBTable]:
        """모든 SASB 데이터 조회"""
        return self.db.query(SASBTable).all()
    
    def get_sasb_by_industry(self, industry: str) -> List[SASBTable]:
        """산업별 SASB 데이터 조회"""
        return self.db.query(SASBTable).filter(
            SASBTable.industry == industry
        ).all()
    
    def get_sasb_industries(self) -> List[str]:
        """SASB 산업 목록 조회"""
        industries = self.db.query(SASBTable.industry).distinct().all()
        return [industry[0] for industry in industries]
    
    # Sustainbest E Table Repository Methods
    def get_all_sustainbest_e(self) -> List[SustainbestETable]:
        """모든 서스틴베스트 E 데이터 조회"""
        return self.db.query(SustainbestETable).all()
    
    def get_sustainbest_e_by_category(self, kpi_category_e: str) -> List[SustainbestETable]:
        """KPI 카테고리별 서스틴베스트 E 데이터 조회"""
        return self.db.query(SustainbestETable).filter(
            SustainbestETable.kpi_category_e == kpi_category_e
        ).all()
    
    def get_sustainbest_e_categories(self) -> List[str]:
        """서스틴베스트 E KPI 카테고리 목록 조회"""
        categories = self.db.query(SustainbestETable.kpi_category_e).distinct().all()
        return [category[0] for category in categories]
    
    # Sustainbest S Table Repository Methods
    def get_all_sustainbest_s(self) -> List[SustainbestSTable]:
        """모든 서스틴베스트 S 데이터 조회"""
        return self.db.query(SustainbestSTable).all()
    
    def get_sustainbest_s_by_category(self, kpi_category_s: str) -> List[SustainbestSTable]:
        """KPI 카테고리별 서스틴베스트 S 데이터 조회"""
        return self.db.query(SustainbestSTable).filter(
            SustainbestSTable.kpi_category_s == kpi_category_s
        ).all()
    
    def get_sustainbest_s_categories(self) -> List[str]:
        """서스틴베스트 S KPI 카테고리 목록 조회"""
        categories = self.db.query(SustainbestSTable.kpi_category_s).distinct().all()
        return [category[0] for category in categories]
    
    # Sustainbest G Table Repository Methods
    def get_all_sustainbest_g(self) -> List[SustainbestGTable]:
        """모든 서스틴베스트 G 데이터 조회"""
        return self.db.query(SustainbestGTable).all()
    
    def get_sustainbest_g_by_category(self, kpi_category_g: str) -> List[SustainbestGTable]:
        """KPI 카테고리별 서스틴베스트 G 데이터 조회"""
        return self.db.query(SustainbestGTable).filter(
            SustainbestGTable.kpi_category_g == kpi_category_g
        ).all()
    
    def get_sustainbest_g_categories(self) -> List[str]:
        """서스틴베스트 G KPI 카테고리 목록 조회"""
        categories = self.db.query(SustainbestGTable.kpi_category_g).distinct().all()
        return [category[0] for category in categories]
    
    # 통합 검색 메서드
    def search_materiality_data(self, keyword: str, table_type: str = "all") -> Dict[str, Any]:
        """키워드로 모든 테이블에서 검색"""
        results = {}
        
        if table_type in ["all", "category"]:
            category_results = self.db.query(CategoryTable).filter(
                CategoryTable.materiality_list.contains(keyword)
            ).all()
            results["category"] = category_results
        
        if table_type in ["all", "kcgs"]:
            kcgs_results = self.db.query(KCGSTable).filter(
                (KCGSTable.environment.contains(keyword)) |
                (KCGSTable.social.contains(keyword)) |
                (KCGSTable.governance.contains(keyword))
            ).all()
            results["kcgs"] = kcgs_results
        
        if table_type in ["all", "sasb"]:
            sasb_results = self.db.query(SASBTable).filter(
                (SASBTable.industry.contains(keyword)) |
                (SASBTable.disclosure_topic.contains(keyword))
            ).all()
            results["sasb"] = sasb_results
        
        if table_type in ["all", "sustainbest_e"]:
            sustainbest_e_results = self.db.query(SustainbestETable).filter(
                (SustainbestETable.kpi_category_e.contains(keyword)) |
                (SustainbestETable.index_name.contains(keyword))
            ).all()
            results["sustainbest_e"] = sustainbest_e_results
        
        if table_type in ["all", "sustainbest_s"]:
            sustainbest_s_results = self.db.query(SustainbestSTable).filter(
                (SustainbestSTable.kpi_category_s.contains(keyword)) |
                (SustainbestSTable.index_name.contains(keyword))
            ).all()
            results["sustainbest_s"] = sustainbest_s_results
        
        if table_type in ["all", "sustainbest_g"]:
            sustainbest_g_results = self.db.query(SustainbestGTable).filter(
                (SustainbestGTable.kpi_category_g.contains(keyword)) |
                (SustainbestGTable.index_name.contains(keyword))
            ).all()
            results["sustainbest_g"] = sustainbest_g_results
        
        return results
