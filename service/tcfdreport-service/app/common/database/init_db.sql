-- TCFD 입력 데이터 테이블 생성
CREATE TABLE IF NOT EXISTS tcfd_inputs (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    governance_g1 TEXT,
    governance_g2 TEXT,
    strategy_s1 TEXT,
    strategy_s2 TEXT,
    strategy_s3 TEXT,
    risk_management_r1 TEXT,
    risk_management_r2 TEXT,
    risk_management_r3 TEXT,
    metrics_targets_m1 TEXT,
    metrics_targets_m2 TEXT,
    metrics_targets_m3 TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_company_name ON tcfd_inputs(company_name);
CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_user_id ON tcfd_inputs(user_id);
CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_created_at ON tcfd_inputs(created_at);
