# Phase 9: AI 고도화

## 06_phases/09_phase09_ai.md
## v1.0 | 2026-04 | 참조: 02_system/04_ai_features.md, 04_dev/06_budget_model.md

> **담당 Agent:** AI Lead (reporting-lead), CTO  
> **선행 Phase:** Phase 8 (빅데이터 & 분석 플랫폼)  
> **후행 Phase:** Phase 10 (웹 & 모바일 앱)  
> **기간:** 2주 (Week 16~17)

---

## 1. Phase 개요

### 1.1 목적

Phase 9는 Malaysia SLFF/MLFF Tolling BOS의 **AI 기능을 고도화**하는 단계다. Phase 8에서 구축된 빅데이터 플랫폼 위에 Text-to-SQL 엔진, 업무 판단 AI, AI 기반 장애 탐지, 수익 예측 모델, 이상 탐지(사기·클론 패턴)를 구현한다. 모든 AI 기능은 Human-in-the-loop 원칙을 준수하며, 완전 자동 처리가 아닌 인간 의사결정을 보조하는 방식으로 설계된다.

### 1.2 AI 기능 전체 맵

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOS AI Feature Map                            │
├─────────────────┬───────────────────────────────────────────────┤
│ Text-to-SQL     │ 자연어 → SQL 변환, Gold Layer 조회              │
│ 업무 판단 AI    │ 이의신청·면제 승인 권고, 인간 최종 결정         │
│ 장애 탐지 AI    │ Prometheus 지표 이상 감지 → Claude 분석         │
│ 수익 예측 AI    │ 월간·분기별 수익 예측 (시계열 모델)             │
│ 이상 탐지 AI    │ 사기 패턴·클론 번호판 탐지                      │
└─────────────────┴───────────────────────────────────────────────┘
```

### 1.3 AI 모델 선택 전략

| 사용 사례 | 기본 모델 | Fallback 1 | Fallback 2 |
|----------|-----------|------------|------------|
| Text-to-SQL | Claude Sonnet 4.x | Claude Haiku 4.x | 미리 정의된 SQL 템플릿 |
| 이의신청 분석 | Claude Sonnet 4.x | Claude Haiku 4.x | 규칙 기반 스코어링 |
| 장애 탐지 | Claude Sonnet 4.x | Claude Haiku 4.x | 임계값 알림 |
| 수익 예측 | Prophet + Claude | Prophet만 | 이동 평균 |
| 이상 탐지 | Claude Sonnet 4.x | Isolation Forest | 블랙리스트 조회 |

### 1.4 AI 비용 예산 (월간)

| 항목 | 예상 호출 수 | 단가 | 월간 비용 (USD) |
|------|-------------|------|----------------|
| Text-to-SQL | 30,000회 | $0.003/호출 | ~$90 |
| 이의신청 분석 | 5,000회 | $0.005/호출 | ~$25 |
| 장애 탐지 | 10,000회 | $0.003/호출 | ~$30 |
| 수익 예측 | 100회 | $0.010/호출 | ~$1 |
| 이상 탐지 | 72,000회 | $0.002/호출 | ~$144 |
| **합계** | | | **~$290/월** |

> 상세 예산 모델: `04_dev/06_budget_model.md` 참조

---

## 2. 담당 Agent & 태스크 체크리스트

### 2.1 reporting-lead (AI Lead 역할 겸임)

```yaml
Agent: reporting-lead
Role: AI 기능 설계 및 구현 총괄
Sprint: Week 16~17
```

#### 태스크 체크리스트

- [ ] **AI-001** Text-to-SQL 엔진 구현
  - Claude Sonnet API 연동 (Anthropic SDK)
  - 프롬프트 엔지니어링: Gold Layer 스키마 주입
  - SQL 유효성 검증 및 샌드박스 실행
  - SLA 목표: 응답 시간 < 10초 (P95)
  - 결과 캐싱 (Redis, TTL 10분, 동일 질의 재사용)

- [ ] **AI-002** 업무 판단 AI 구현 (이의신청·면제 권고)
  - 이의신청 텍스트 분석 (Claude Sonnet)
  - 증거 서류 이미지 분석 (Claude Vision)
  - 승인/기각/추가 검토 3단계 권고 생성
  - Human-in-the-loop: 최종 결정은 appeal-reviewer Agent
  - 권고 근거 텍스트 생성 (한국어/말레이어/영어)

- [ ] **AI-003** AI 장애 탐지 고도화
  - Prometheus 지표 스트림 수집 (5초 간격)
  - 이상 패턴 감지: TPS 급락, 오류율 급등, 메모리 누수
  - Claude Sonnet 분석: 장애 원인 추론 및 조치 방안 제시
  - 자동 티켓 생성 (PagerDuty + Jira)
  - 장애 후 RCA 보고서 자동 초안 생성

- [ ] **AI-004** 수익 예측 모델 구현
  - Facebook Prophet 시계열 모델 학습 (Gold Layer 이력 데이터)
  - Claude Sonnet으로 예측 결과 자연어 해석
  - 월간 수익 예측 (다음 달)
  - 분기별 수익 예측 (다음 분기)
  - 예측 신뢰 구간 시각화

- [ ] **AI-005** 이상 탐지 (사기·클론 패턴)
  - 클론 번호판 탐지: 동일 번호판 동시간대 이중 통행
  - OBU 복제 탐지: 동일 OBU ID 이중 등록
  - 사기 결제 패턴: 반복 실패 후 다른 채널 시도
  - Claude Sonnet으로 탐지 근거 설명 생성
  - 실시간 알림 (Kafka → fraud-detection Topic)

- [ ] **AI-006** Fallback 전략 구현
  - Sonnet → Haiku 자동 전환 (Sonnet 오류 시)
  - Haiku → 템플릿 자동 전환 (Haiku 오류 시)
  - Circuit Breaker: 3회 연속 실패 시 템플릿 모드 전환
  - 복구 감지: 30초 간격 Health Check, 자동 복귀

### 2.2 CTO (기술 의사결정 및 승인)

- [ ] **AI-011** AI 기능 아키텍처 검토 및 승인
- [ ] **AI-012** AI 윤리 가이드라인 승인 (Human-in-the-loop 원칙)
- [ ] **AI-013** AI 비용 예산 승인 ($290/월)
- [ ] **AI-014** AI 감사 로그 보존 정책 승인 (90일)

---

## 3. Text-to-SQL 프롬프트 설계 예시

### 3.1 시스템 프롬프트 구조

```python
# ai_text_to_sql.py
from anthropic import Anthropic
from typing import Optional
import time

client = Anthropic()

GOLD_LAYER_SCHEMA = """
=== BOS Gold Layer 테이블 스키마 ===

1. gold_daily_revenue (일별 수익 집계)
   - plaza_code VARCHAR     : 플라자 코드 (예: KES-001, LNK-002)
   - vehicle_class VARCHAR  : 차량 클래스 (Class1/Class2/Class3)
   - channel CHAR(1)        : 결제 채널 (A=RFID/OBU, B=수동/현금)
   - aggregation_date DATE  : 집계 기준일
   - txn_count BIGINT       : 트랜잭션 건수
   - total_revenue DECIMAL  : 총 수익 (RM)
   - avg_toll DECIMAL       : 평균 통행료 (RM)
   - paid_count BIGINT      : 정상 결제 건수
   - failed_count BIGINT    : 결제 실패 건수
   - success_rate DECIMAL   : 결제 성공률 (%)

2. gold_daily_traffic (일별 교통량)
   - plaza_code VARCHAR     : 플라자 코드
   - hour TIMESTAMP         : 시간 단위 (YYYY-MM-DD HH:00:00)
   - vehicle_count BIGINT   : 차량 통행 건수
   - hourly_revenue DECIMAL : 시간별 수익 (RM)

3. gold_monthly_summary (월별 요약)
   - report_month CHAR(7)   : 보고 월 (YYYY-MM)
   - plaza_code VARCHAR     : 플라자 코드
   - total_revenue DECIMAL  : 월 총 수익 (RM)
   - total_vehicles BIGINT  : 월 총 통행 차량
   - avg_daily_revenue DECIMAL : 일평균 수익

=== 쿼리 규칙 ===
- AWS Athena SQL 문법 사용 (Presto 기반)
- SELECT만 허용 (INSERT/UPDATE/DELETE 금지)
- LIMIT 1000 기본 적용
- 날짜 함수: date('2026-01-01'), date_format(date_col, '%Y-%m')
"""

SYSTEM_PROMPT = f"""당신은 Malaysia SLFF/MLFF Tolling BOS의 데이터 분석 전문가입니다.
사용자의 자연어 질문을 분석하여 AWS Athena SQL 쿼리로 변환하세요.

{GOLD_LAYER_SCHEMA}

응답 형식:
1. SQL 쿼리 (```sql 블록)
2. 쿼리 설명 (1~2문장, 한국어)
3. 주의사항 (있을 경우)

절대 금지:
- DDL 구문 (CREATE, DROP, ALTER)
- DML 구문 (INSERT, UPDATE, DELETE)
- 개인식별정보(PII) 직접 조회
"""


def text_to_sql(
    question: str,
    model: str = "claude-sonnet-4-5",
    max_retries: int = 2,
) -> dict:
    """자연어 질문을 SQL로 변환. SLA: P95 < 10초."""

    start_time = time.time()
    last_error = None

    # Fallback 모델 체인: Sonnet → Haiku → Template
    model_chain = [model, "claude-haiku-4-5"]

    for attempt, current_model in enumerate(model_chain):
        try:
            response = client.messages.create(
                model=current_model,
                max_tokens=1024,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": question}],
            )

            elapsed = time.time() - start_time
            sql_text = response.content[0].text

            return {
                "success": True,
                "sql": extract_sql(sql_text),
                "explanation": extract_explanation(sql_text),
                "model_used": current_model,
                "elapsed_seconds": round(elapsed, 2),
                "fallback_triggered": attempt > 0,
            }

        except Exception as e:
            last_error = str(e)
            print(f"[Text-to-SQL] {current_model} 실패: {e}, Fallback 시도")

    # 최종 Fallback: 미리 정의된 SQL 템플릿
    return {
        "success": False,
        "sql": get_template_sql(question),
        "explanation": "AI 서비스 일시적 장애 — 템플릿 모드로 전환됨",
        "model_used": "template",
        "elapsed_seconds": round(time.time() - start_time, 2),
        "fallback_triggered": True,
        "error": last_error,
    }


def extract_sql(response_text: str) -> str:
    """응답에서 SQL 코드 블록 추출."""
    import re
    match = re.search(r"```sql\n(.*?)```", response_text, re.DOTALL)
    return match.group(1).strip() if match else ""


def extract_explanation(response_text: str) -> str:
    """응답에서 설명 텍스트 추출 (SQL 블록 제외)."""
    import re
    return re.sub(r"```sql.*?```", "", response_text, flags=re.DOTALL).strip()


def get_template_sql(question: str) -> str:
    """질문 키워드 기반 미리 정의된 SQL 반환."""
    q_lower = question.lower()
    if "수익" in question or "revenue" in q_lower:
        return "SELECT plaza_code, SUM(total_revenue) as revenue FROM gold_daily_revenue WHERE aggregation_date = CURRENT_DATE GROUP BY plaza_code ORDER BY revenue DESC LIMIT 100"
    if "교통량" in question or "traffic" in q_lower:
        return "SELECT plaza_code, SUM(vehicle_count) as vehicles FROM gold_daily_traffic WHERE date(hour) = CURRENT_DATE GROUP BY plaza_code ORDER BY vehicles DESC LIMIT 100"
    return "SELECT * FROM gold_monthly_summary ORDER BY report_month DESC LIMIT 10"
```

### 3.2 프롬프트 사용 예시

```python
# 사용 예시
examples = [
    "지난주 Kesas 플라자의 Channel A 수익은 얼마입니까?",
    "오늘 오전 피크타임(08:00~09:00)에 통행량이 가장 많은 플라자 상위 5개를 알려주세요.",
    "이번 달 Class3 차량의 결제 성공률이 90% 미만인 플라자 목록을 보여주세요.",
    "지난 3개월 간 월별 총 수익 트렌드를 보여주세요.",
]

for question in examples:
    result = text_to_sql(question)
    print(f"Q: {question}")
    print(f"SQL: {result['sql'][:100]}...")
    print(f"모델: {result['model_used']}, 응답: {result['elapsed_seconds']}초\n")
```

---

## 4. AI 감사 로그 스키마 (DDL)

### 4.1 AI 감사 로그 테이블

```sql
-- AI 감사 로그: 모든 AI 호출 기록 (보존 90일)
CREATE TABLE ai_audit_log (
    audit_id        UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    feature_type    VARCHAR(50)     NOT NULL,  -- TEXT_TO_SQL | APPEAL_ANALYSIS | FAULT_DETECTION | REVENUE_FORECAST | ANOMALY_DETECTION
    request_id      VARCHAR(100)    NOT NULL,  -- 요청 추적 ID (X-Request-ID)
    agent_id        VARCHAR(50)     NOT NULL,  -- 호출 Agent 식별자
    user_id         UUID,                      -- 인간 사용자 ID (해당 시)
    model_requested VARCHAR(50)     NOT NULL,  -- 요청 모델 (claude-sonnet-4-5)
    model_used      VARCHAR(50)     NOT NULL,  -- 실제 사용 모델 (Fallback 포함)
    fallback_level  SMALLINT        DEFAULT 0, -- 0=정상, 1=Haiku, 2=Template
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    cost_usd        NUMERIC(10, 6),
    prompt_hash     VARCHAR(64),               -- SHA-256 (감사 추적, PII 제외)
    response_hash   VARCHAR(64),               -- SHA-256
    elapsed_ms      INTEGER         NOT NULL,
    success         BOOLEAN         NOT NULL,
    error_code      VARCHAR(50),
    human_reviewed  BOOLEAN         DEFAULT FALSE, -- Human-in-the-loop 완료 여부
    human_decision  VARCHAR(20),               -- APPROVED | REJECTED | MODIFIED
    human_agent_id  VARCHAR(50),               -- 검토한 인간 Agent ID
    reviewed_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     DEFAULT NOW() NOT NULL,
    expires_at      TIMESTAMPTZ     GENERATED ALWAYS AS (created_at + INTERVAL '90 days') STORED
) PARTITION BY RANGE (created_at);

-- 월별 파티션 자동 생성
CREATE TABLE ai_audit_log_2026_04 PARTITION OF ai_audit_log
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

CREATE TABLE ai_audit_log_2026_05 PARTITION OF ai_audit_log
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- 인덱스
CREATE INDEX idx_ai_audit_feature_type ON ai_audit_log (feature_type, created_at DESC);
CREATE INDEX idx_ai_audit_request_id   ON ai_audit_log (request_id);
CREATE INDEX idx_ai_audit_agent_id     ON ai_audit_log (agent_id, created_at DESC);
CREATE INDEX idx_ai_audit_expires_at   ON ai_audit_log (expires_at);

-- RLS: 감사 로그는 audit-reviewer, CTO, CIO만 조회
ALTER TABLE ai_audit_log ENABLE ROW LEVEL SECURITY;

CREATE POLICY ai_audit_log_access ON ai_audit_log
    FOR SELECT
    USING (
        current_setting('app.current_role') IN ('audit-reviewer', 'cto', 'cio', 'admin')
    );

-- TTL 자동 정리 (pg_cron 사용)
-- SELECT cron.schedule('ai-audit-cleanup', '0 3 * * *',
--   $$DELETE FROM ai_audit_log WHERE expires_at < NOW()$$);
```

### 4.2 이의신청 AI 분석 결과 테이블

```sql
-- 이의신청 AI 분석 결과 저장
CREATE TABLE appeal_ai_analysis (
    analysis_id     UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    appeal_id       UUID            NOT NULL REFERENCES appeals(appeal_id),
    audit_id        UUID            NOT NULL REFERENCES ai_audit_log(audit_id),
    recommendation  VARCHAR(20)     NOT NULL CHECK (recommendation IN ('APPROVE', 'REJECT', 'ESCALATE')),
    confidence      NUMERIC(5, 2)   NOT NULL CHECK (confidence BETWEEN 0 AND 100),
    reasoning_ko    TEXT            NOT NULL,  -- 한국어 근거
    reasoning_ms    TEXT,                      -- 말레이어 근거
    reasoning_en    TEXT,                      -- 영어 근거
    evidence_flags  JSONB,                     -- 근거 문서 분석 결과
    risk_score      SMALLINT        CHECK (risk_score BETWEEN 0 AND 100),
    created_at      TIMESTAMPTZ     DEFAULT NOW() NOT NULL
);

-- 이상 탐지 이벤트 테이블
CREATE TABLE anomaly_detection_events (
    event_id        UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    anomaly_type    VARCHAR(50)     NOT NULL CHECK (anomaly_type IN (
                        'CLONE_PLATE', 'CLONE_OBU', 'FRAUD_PAYMENT', 'SUSPICIOUS_PATTERN'
                    )),
    plate_number    VARCHAR(20),
    obu_id          VARCHAR(50),
    plaza_code      VARCHAR(20),
    transaction_ids UUID[],                    -- 관련 트랜잭션 ID 배열
    confidence      NUMERIC(5, 2),
    ai_explanation  TEXT            NOT NULL,  -- Claude 설명
    audit_id        UUID            REFERENCES ai_audit_log(audit_id),
    status          VARCHAR(20)     DEFAULT 'OPEN' CHECK (status IN ('OPEN', 'INVESTIGATING', 'CONFIRMED', 'FALSE_POSITIVE')),
    assigned_to     VARCHAR(50),
    resolved_at     TIMESTAMPTZ,
    created_at      TIMESTAMPTZ     DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_anomaly_type    ON anomaly_detection_events (anomaly_type, created_at DESC);
CREATE INDEX idx_anomaly_plate   ON anomaly_detection_events (plate_number) WHERE plate_number IS NOT NULL;
CREATE INDEX idx_anomaly_status  ON anomaly_detection_events (status) WHERE status IN ('OPEN', 'INVESTIGATING');
```

### 4.3 수익 예측 결과 테이블

```sql
-- 수익 예측 저장
CREATE TABLE revenue_forecasts (
    forecast_id     UUID            DEFAULT gen_random_uuid() PRIMARY KEY,
    forecast_type   VARCHAR(20)     NOT NULL CHECK (forecast_type IN ('MONTHLY', 'QUARTERLY')),
    target_period   CHAR(7)         NOT NULL,  -- 예측 대상 기간 (YYYY-MM 또는 YYYY-QN)
    plaza_code      VARCHAR(20),               -- NULL = 전체 합산
    predicted_rm    NUMERIC(15, 2)  NOT NULL,
    lower_bound_rm  NUMERIC(15, 2),            -- 신뢰 구간 하한
    upper_bound_rm  NUMERIC(15, 2),            -- 신뢰 구간 상한
    confidence_pct  NUMERIC(5, 2),
    model_version   VARCHAR(20),               -- Prophet 모델 버전
    ai_narrative    TEXT,                      -- Claude 생성 자연어 해석
    audit_id        UUID            REFERENCES ai_audit_log(audit_id),
    generated_at    TIMESTAMPTZ     DEFAULT NOW() NOT NULL
);

CREATE INDEX idx_forecast_period ON revenue_forecasts (forecast_type, target_period DESC);
```

---

## 5. AI 장애 탐지 구현 패턴

### 5.1 Prometheus + Claude 연동

```python
# ai_fault_detection.py
import asyncio
from anthropic import AsyncAnthropic
from prometheus_api_client import PrometheusConnect

prom = PrometheusConnect(url="http://prometheus.bos-internal:9090")
client = AsyncAnthropic()

FAULT_DETECTION_PROMPT = """당신은 Malaysia BOS 시스템 장애 분석 전문가입니다.
아래 Prometheus 지표 데이터를 분석하여 이상 여부를 판단하세요.

판단 기준:
- TPS < 5,000 (정상: 8,000~10,000): 심각한 처리 저하
- 오류율 > 1% (정상: < 0.1%): 서비스 장애
- 응답 시간 P95 > 500ms (정상: < 200ms): 성능 저하
- 메모리 사용률 > 85%: OOM 위험

응답 형식:
1. 이상 여부: [정상 | 주의 | 경고 | 심각]
2. 감지된 이상 항목
3. 예상 원인 (1~3가지)
4. 즉각 조치 방안
5. 자동화 가능 조치 (있을 경우)
"""

async def analyze_system_health(metrics: dict) -> dict:
    """Prometheus 지표를 AI로 분석하여 장애 여부 판단."""

    metrics_text = "\n".join([
        f"- {key}: {value}" for key, value in metrics.items()
    ])

    try:
        response = await client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=512,
            system=FAULT_DETECTION_PROMPT,
            messages=[{
                "role": "user",
                "content": f"현재 시스템 지표:\n{metrics_text}"
            }],
        )
        analysis = response.content[0].text
        severity = extract_severity(analysis)
        return {"severity": severity, "analysis": analysis, "model": "claude-sonnet-4-5"}

    except Exception:
        # Fallback: 임계값 기반 룰
        return rule_based_fault_detection(metrics)


def rule_based_fault_detection(metrics: dict) -> dict:
    """AI 장애 시 임계값 기반 Fallback."""
    tps = metrics.get("current_tps", 0)
    error_rate = metrics.get("error_rate_pct", 0)

    if tps < 2000 or error_rate > 5:
        severity = "심각"
    elif tps < 5000 or error_rate > 1:
        severity = "경고"
    elif tps < 7000 or error_rate > 0.5:
        severity = "주의"
    else:
        severity = "정상"

    return {
        "severity": severity,
        "analysis": f"[Fallback 모드] TPS={tps}, 오류율={error_rate}%",
        "model": "rule-based",
    }


def extract_severity(analysis_text: str) -> str:
    for level in ["심각", "경고", "주의", "정상"]:
        if level in analysis_text:
            return level
    return "알 수 없음"
```

---

## 6. 완료 기준

### 6.1 기술적 완료 기준

| 항목 | 목표값 | 측정 방법 |
|------|--------|-----------|
| Text-to-SQL SLA | P95 < 10초 | API 응답 시간 모니터링 |
| Text-to-SQL 정확도 | > 85% (SQL 유효 실행) | 테스트 케이스 100개 |
| 이의신청 AI 정확도 | > 80% (인간 검토 일치) | Pilot 50건 |
| 장애 탐지 정밀도 | > 90% (False Positive < 10%) | 1주 운영 데이터 |
| Fallback 전환 시간 | < 5초 | Circuit Breaker 테스트 |
| AI 감사 로그 커버리지 | 100% (모든 AI 호출) | 감사 로그 검증 |

### 6.2 비즈니스 완료 기준

- [ ] TOC 운영자가 자연어로 데이터를 조회할 수 있음 (Text-to-SQL)
- [ ] 이의신청 AI 권고 기능이 appeal-service에 통합됨
- [ ] AI 기반 장애 탐지가 Prometheus와 연동되어 자동 티켓 생성됨
- [ ] 수익 예측 결과가 경영진 대시보드에 표시됨
- [ ] 클론 번호판 탐지 1건 이상 실증 (테스트 데이터)
- [ ] CTO가 AI 감사 로그 및 윤리 가이드라인 최종 승인

### 6.3 품질 게이트

```
G-HARD Gate 6 통과 조건:
  ✅ Text-to-SQL P95 < 10초 달성
  ✅ AI 감사 로그 100% 기록 확인
  ✅ Human-in-the-loop 플로우 E2E 테스트 통과
  ✅ Fallback 전략 3단계 전환 테스트 통과
  ✅ AI 비용 예산 ($290/월) 범위 내 검증
  ✅ 보안 감사: AI 프롬프트 인젝션 방어 확인
```

---

## 7. 리스크 관리

| 리스크 | 발생 가능성 | 영향도 | 대응 방안 |
|--------|-----------|--------|-----------|
| Claude API Rate Limit | 중 | 고 | Exponential Backoff + 요청 큐 |
| Text-to-SQL 악의적 입력 | 중 | 매우고 | SQL 파서 검증, READ-ONLY 권한 격리 |
| AI 판단 오류 (이의신청) | 중 | 고 | Human-in-the-loop 필수, 90일 감사 |
| AI 비용 급증 | 저 | 중 | 월간 비용 알림 ($400 초과 시 PagerDuty) |
| AI 모델 API 버전 변경 | 저 | 중 | 모델 버전 고정 + 변경 테스트 파이프라인 |
| 이상 탐지 False Positive | 중 | 중 | 신뢰도 임계값 조정, 인간 검토 후 처리 |

---

## 8. GSD 명령어

```bash
# Phase 9 시작
/gsd:execute-phase phase=09_ai

# 개별 태스크 실행
/gsd:do AI-001  # Text-to-SQL 엔진 구현
/gsd:do AI-002  # 업무 판단 AI (이의신청·면제)
/gsd:do AI-003  # AI 장애 탐지 고도화
/gsd:do AI-004  # 수익 예측 모델
/gsd:do AI-005  # 이상 탐지 (사기·클론)
/gsd:do AI-006  # Fallback 전략 구현
/gsd:do AI-011  # CTO 아키텍처 검토
/gsd:do AI-012  # AI 윤리 가이드라인 승인

# 진행 상황 확인
/gsd:progress phase=09_ai

# Phase 9 완료
/gsd:complete-milestone phase=09_ai
/gsd:next
```

---

## 9. 참조 문서

| 문서 | 경로 | 관련 내용 |
|------|------|-----------|
| AI 기능 사양 | `02_system/04_ai_features.md` | AI 기능 전체 명세 |
| 예산 모델 | `04_dev/06_budget_model.md` | AI 비용 상세 |
| 데이터 아키텍처 | `03_data/01_data_architecture.md` | Gold Layer 스키마 |
| 보안 컴플라이언스 | `03_data/05_security_compliance.md` | AI 데이터 처리 PDPA |
| RBAC 설계 | `03_data/03_rbac_design.md` | AI 감사 로그 접근 제어 |
| Phase 8 (빅데이터) | `06_phases/08_phase08_bigdata.md` | 선행 Phase |
| Phase 10 (앱) | `06_phases/10_phase10_app.md` | 후행 Phase |

---

*최종 업데이트: 2026-04 | Phase 9: AI 고도화 | v1.0*
