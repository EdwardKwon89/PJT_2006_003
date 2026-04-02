---
name: text-to-sql-engine
description: Claude Sonnet-powered natural language to SQL engine — prompt injection, schema injection, SELECT-only safety
use_when:
  - 자연어(KO/EN/BM)로 BOS 데이터를 조회하는 기능을 구현할 때
  - Claude Sonnet 기반 Text-to-SQL 프롬프트를 설계할 때
  - SQL 안전성 검증 로직이 필요할 때
  - Phase 9 또는 Phase 10 분석 기능 개발 시
dont_use_when:
  - 일반 SQL 쿼리 최적화가 필요할 때 (aggregation-units 사용)
  - AI 장애 탐지 기능이 필요할 때 (ai-fault-detection 사용)
---

# Text-to-SQL 엔진

## 1. 개요

BOS는 비기술자(경영진, 콘세셔네어 담당자)가 자연어로 데이터를 조회할 수 있도록 **Claude Sonnet 기반 Text-to-SQL 엔진**을 제공한다. 쿼리 생성부터 실행·결과 요약까지 전체 파이프라인을 자동화한다.

---

## 2. 핵심 내용

### 2.1 처리 파이프라인

```
사용자 자연어 입력 (KO/EN/BM)
        │
        ▼
[1] 스키마 주입 (허용 테이블 + 컬럼 메타데이터)
        │
        ▼
[2] Claude Sonnet API 호출 (SQL 생성)
        │
        ▼
[3] SQL 안전성 검증 (SELECT Only, 위험 키워드 차단)
        │
        ▼
[4] PostgreSQL Read Replica 실행 (최대 30초 타임아웃)
        │
        ▼
[5] 결과 자연어 요약 (Claude, 해당 언어로)
        │
        ▼
사용자에게 테이블 + 자연어 요약 반환
```

### 2.2 시스템 프롬프트 (스키마 주입)

```python
SYSTEM_PROMPT = """
You are a SQL expert for the Malaysia BOS (Back Office System) tolling platform.
Generate a single, safe PostgreSQL SELECT query based on the user's question.

## Available Tables
{schema_injection}  # 허용 테이블 목록과 컬럼 설명 동적 주입

## Rules (MUST follow)
1. Generate ONLY SELECT statements. Never INSERT, UPDATE, DELETE, DROP, etc.
2. Always include a LIMIT clause (max 1000 rows unless aggregation query).
3. Mask sensitive columns: replace vehicle_plate with 'PLATE-***', owner_name with 'OWNER-***'.
4. Use only the provided table list. Never reference system tables.
5. Add comments explaining the query logic.

## Output Format
Return JSON:
{
  "sql": "SELECT ...",
  "explanation": "이 쿼리는 ..."
}
"""
```

### 2.3 SQL 안전성 검증

```python
DANGEROUS_KEYWORDS = [
    "INSERT", "UPDATE", "DELETE", "DROP", "TRUNCATE",
    "CREATE", "ALTER", "GRANT", "REVOKE", "EXECUTE",
    "pg_", "information_schema", "sys.", "--", "/*"
]

def validate_sql_safety(sql: str) -> bool:
    sql_upper = sql.upper().strip()

    # SELECT로 시작해야 함
    if not sql_upper.startswith("SELECT"):
        raise SqlSafetyError("Only SELECT statements allowed")

    # 위험 키워드 포함 여부 확인
    for keyword in DANGEROUS_KEYWORDS:
        if keyword.upper() in sql_upper:
            raise SqlSafetyError(f"Dangerous keyword detected: {keyword}")

    return True
```

### 2.4 허용 테이블 목록 (읽기 전용)

```python
ALLOWED_TABLES = [
    "agg_daily_summary",      # 일별 집계
    "agg_monthly_summary",    # 월별 집계
    "agg_plaza_traffic",      # 요금소별 트래픽
    "agg_vehicle_class",      # 차량 등급별
    "unpaid_cases_summary",   # 미납 현황 집계 뷰 (원본 아님)
    "gold_kpi_dashboard",     # KPI 대시보드
]
# 원본 OLTP 테이블 (trip_records, payment_attempts) 접근 금지
```

### 2.5 SLA 및 성능

| 지표 | 목표값 |
|------|-------|
| 전체 파이프라인 P99 | < 10초 |
| Claude API 호출 | < 3초 |
| DB 쿼리 실행 | < 5초 (타임아웃) |
| 동시 처리 | 10개 쿼리/초 |

---

## 3. 예시 시나리오

```python
# 사용자 입력
query = "이번 달 Channel B 수납액이 가장 높은 콘세셔네어 Top 3 알려줘"

# Claude 생성 SQL
sql = """
SELECT
    concessionaire_id,
    SUM(gross_amount) AS channel_b_total
FROM agg_monthly_summary
WHERE year_month = TO_CHAR(NOW(), 'YYYY-MM')
  AND channel = 'B'
GROUP BY concessionaire_id
ORDER BY channel_b_total DESC
LIMIT 3;
"""

# 자연어 요약 응답
summary = "이번 달 Channel B 수납액 기준 Top 3 콘세셔네어는 PLUS (RM 1.2M), LEKAS (RM 0.8M), SILK (RM 0.5M)입니다."
```

---

## 4. 주의사항 & 함정

- **프롬프트 인젝션 방어**: 사용자 입력을 시스템 프롬프트에 직접 삽입 금지. 별도 `user` 메시지로 전달
- **RBAC 연동 필수**: 콘세셔네어 사용자는 자사 집계 통계만 접근 (세션 컨텍스트에서 필터 추가)
- **결과 캐싱**: 동일 쿼리 해시 기준 5분 캐싱 (Redis) — 반복 호출 비용 절감

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| AI 기능 설계 | [`../../docs/02_system/04_ai_features.md`](../../docs/02_system/04_ai_features.md) |
| Phase 10 분석 플랫폼 | [`../../docs/06_phases/10_phase10_analytics.md`](../../docs/06_phases/10_phase10_analytics.md) |
| RBAC 경계 | [`../rbac-data-boundary/SKILL.md`](../rbac-data-boundary/SKILL.md) |
