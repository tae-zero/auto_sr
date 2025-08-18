-- TCFD 입력 데이터 테이블 생성
CREATE TABLE IF NOT EXISTS tcfd_inputs (
    id SERIAL PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    g1_text TEXT,
    g2_text TEXT,
    s1_text TEXT,
    s2_text TEXT,
    s3_text TEXT,
    r1_text TEXT,
    r2_text TEXT,
    r3_text TEXT,
    m1_text TEXT,
    m2_text TEXT,
    m3_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 인덱스 생성
CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_company_name ON tcfd_inputs(company_name);
CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_user_id ON tcfd_inputs(user_id);
CREATE INDEX IF NOT EXISTS idx_tcfd_inputs_created_at ON tcfd_inputs(created_at);
