---
name: rbac-data-boundary
description: 30-role RBAC model, PostgreSQL RLS policies, concessionaire data isolation, audit logging
use_when:
  - 역할 기반 접근 제어(RBAC) 설계 또는 구현 시
  - PostgreSQL Row Level Security(RLS) 정책을 설정할 때
  - 콘세셔네어 간 데이터 격리를 보장해야 할 때
  - 감사 로그 패턴이 필요할 때
dont_use_when:
  - 메타데이터/용어 관리가 필요할 때 (metadata-management 사용)
  - 외부 API 인증이 필요할 때 (external-api-mcp 사용)
---

# RBAC & 데이터 경계

## 1. 개요

BOS는 **30개 역할** 기반 RBAC 모델을 사용하며, PostgreSQL Row Level Security(RLS)로 콘세셔네어별 데이터 격리를 강제한다. 모든 데이터 접근은 감사 로그에 기록된다.

---

## 2. 핵심 내용

### 2.1 역할 계층 구조

```
JVC 최고 관리자 (SuperAdmin)
├── JVC 운영자 (OperationsAdmin)
│   ├── JVC 정산 담당 (BillingOfficer)
│   ├── JVC 위반 심사관 (ViolationReviewer)
│   └── JVC 리포팅 분석가 (ReportingAnalyst)
├── 콘세셔네어 관리자 (ConcessionaireAdmin)
│   ├── 콘세셔네어 정산 담당 (ConcessionaireBilling)
│   └── 콘세셔네어 운영 직원 (ConcessionaireOps)
├── 정부 기관 (GovernmentReader)
│   ├── JPJ 담당 (JpjOfficer)
│   └── TOC 파트너 (TocPartner)
└── 시스템 Agent (SystemAgent)
    ├── txn-agent
    ├── billing-agent
    └── monitoring-agent
```

### 2.2 PostgreSQL RLS 설정

```sql
-- 콘세셔네어 격리를 위한 RLS 기본 설정
ALTER TABLE trip_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE daily_settlement_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE unpaid_cases ENABLE ROW LEVEL SECURITY;

-- JVC 내부: 전체 데이터 접근
CREATE POLICY jvc_all_access ON trip_records
    FOR ALL TO jvc_ops_role
    USING (true);

-- 콘세셔네어: 자사 데이터만 접근
CREATE POLICY concessionaire_isolation ON trip_records
    FOR SELECT TO concessionaire_role
    USING (concessionaire_id = current_setting('app.current_concessionaire_id')::uuid);

-- TOC 파트너: 집계 데이터만 (개인정보 제외)
CREATE POLICY toc_aggregated_only ON daily_settlement_summary
    FOR SELECT TO toc_role
    USING (true);  -- RLS는 허용, 뷰에서 컬럼 제한
```

### 2.3 세션 컨텍스트 설정

```java
// Spring Security + PostgreSQL RLS 연동
@Component
public class TenantContextFilter {
    @Override
    public void doFilter(HttpServletRequest req, HttpServletResponse res, FilterChain chain) {
        String concessionaireId = extractFromJwt(req, "concessionaire_id");
        jdbcTemplate.execute(
            "SET LOCAL app.current_concessionaire_id = '" + concessionaireId + "'"
        );
        chain.doFilter(req, res);
    }
}
```

### 2.4 API 엔드포인트별 권한 매핑

| 엔드포인트 | 필요 권한 | 콘세셔네어 격리 |
|-----------|---------|------------|
| `GET /transactions` | `TXN_READ` | ✅ RLS 적용 |
| `GET /settlements/daily` | `SETTLEMENT_READ` | ✅ RLS 적용 |
| `PUT /violations/{id}/approve` | `VIOLATION_APPROVE` | ✅ 担당 콘세셔네어만 |
| `GET /reports/kpi` | `REPORT_READ` | JVC only (전체) |
| `DELETE /violations/{id}/writeoff` | `WRITEOFF_EXECUTE` | JVC CFO only |

### 2.5 감사 로그 패턴

```sql
-- 감사 로그 테이블
CREATE TABLE audit_log (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL,
    role        VARCHAR(50) NOT NULL,
    action      VARCHAR(100) NOT NULL,  -- 'READ', 'CREATE', 'UPDATE', 'DELETE'
    resource    VARCHAR(100) NOT NULL,  -- 'trip_records', 'unpaid_cases'
    resource_id UUID,
    ip_address  INET,
    user_agent  TEXT,
    result      VARCHAR(20) NOT NULL,   -- 'SUCCESS', 'DENIED'
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- 파티셔닝: 월별
-- 보관: 7년 (금융·법적 요건)
```

```java
// AOP 기반 감사 로그 자동 기록
@Aspect
@Component
public class AuditLogAspect {
    @AfterReturning("@annotation(Auditable)")
    public void logAccess(JoinPoint jp, Object result) {
        auditLog.record(
            currentUser(), jp.getSignature().getName(),
            extractResourceId(jp), "SUCCESS"
        );
    }
}
```

---

## 3. 예시 시나리오

**시나리오: 콘세셔네어 A가 콘세셔네어 B 데이터 조회 시도**
1. JWT 토큰에 `concessionaire_id = A-UUID` 포함
2. Filter에서 `SET LOCAL app.current_concessionaire_id = 'A-UUID'`
3. RLS 정책: `concessionaire_id = current_setting('app.current_concessionaire_id')`
4. 콘세셔네어 B 데이터는 RLS에 의해 자동 필터링 → 빈 결과 반환
5. 감사 로그: `{user: A-admin, action: READ, resource: trip_records, result: SUCCESS (0 rows)}`

---

## 4. 주의사항 & 함정

- **RLS 비활성화 주의**: `SET row_security = OFF`는 SuperAdmin만 가능. 배치 작업에서 실수로 비활성화 금지
- **세션 컨텍스트 전파**: 멀티스레드 환경에서 `SET LOCAL`은 트랜잭션 범위 내에서만 유효
- **감사 로그는 삭제 불가**: 감사 로그 테이블에 `DELETE` 권한 부여 금지 (SOX 컴플라이언스)

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 메타데이터 관리 | [`../metadata-management/SKILL.md`](../metadata-management/SKILL.md) |
| RBAC 설계 문서 | [`../../docs/03_data/03_rbac_design.md`](../../docs/03_data/03_rbac_design.md) |
| 보안 & 컴플라이언스 | [`../../docs/03_data/05_security_compliance.md`](../../docs/03_data/05_security_compliance.md) |
