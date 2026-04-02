# AI 기능 설계
## 02_system/04_ai_features.md
## v1.0 | 2026-04 | 참조: 01_system_overview.md, 02_service_domains.md, 04_dev/02_paperclip_org.md

---

> **Agent 사용 지침**
> AI Lead, Product Owner Agent가 AI 기능 설계·우선순위 결정 시 로드.
> Text-to-SQL 쿼리 추가 또는 MCP Tool 변경 전 반드시 이 문서 확인.
> AI 결정(이의신청 처리, 면제 승인)은 반드시 Human-in-the-loop 패턴 유지.

---

## 목차

1. [Executive Summary](#1-executive-summary)
2. [Text-to-SQL 설계](#2-text-to-sql-설계)
3. [업무 판단 AI 설계](#3-업무-판단-ai-설계)
4. [스마트 커스터마이징 AI](#4-스마트-커스터마이징-ai)
5. [AI 장애 탐지·자동 복구](#5-ai-장애-탐지자동-복구)
6. [Layer 3 Analytics AI (Phase 8/9)](#6-layer-3-analytics-ai-phase-89)
7. [Paperclip 29개 Agent 조직 & MCP 연계](#7-paperclip-29개-agent-조직--mcp-연계)
8. [AI 거버넌스 & 윤리](#8-ai-거버넌스--윤리)
9. [Fallback & 비용 관리](#9-fallback--비용-관리)
10. [참조 문서](#10-참조-문서)

---

## 1. Executive Summary

Malaysia SLFF/MLFF Tolling BOS 시스템은 운영 효율성 향상과 Human Agent 의사결정 지원을 위해 5개 범주의 AI 기능을 단계적으로 도입한다. 모든 AI 기능은 **Anthropic Claude** 모델 기반이며, 비용·성능·안전성을 기준으로 모델을 분리 적용한다.

### 1.1 AI 기능 전체 현황

| # | 기능명 | 모델 | 레이어 | Phase | 담당 서비스 | SLA |
|---|--------|------|--------|-------|-------------|-----|
| 1 | Text-to-SQL | claude-sonnet-4-5 | Layer 2 Query | Phase 3 | api-service | <10초 |
| 2 | 업무 판단 AI (이의신청·면제) | claude-sonnet-4-5 | Layer 2 Business | Phase 4 | violation-service, exemption-service | <15초 |
| 3 | 스마트 커스터마이징 | claude-haiku-4-5 | Layer 2 UI | Phase 5 | bos-frontend | <3초 |
| 4 | AI 장애 탐지·자동 복구 | Rule-based + Claude | Layer 1 Infra | Phase 3 | devops-service | <30초 복구 시작 |
| 5 | Layer 3 Analytics AI | claude-sonnet-4-5 | Layer 3 Analytics | Phase 8/9 | analytics-service | <30초 |

### 1.2 AI 도입 원칙

```
┌─────────────────────────────────────────────────────────────┐
│                     AI 도입 원칙 (BOS)                       │
├────────────────┬────────────────────────────────────────────┤
│ 안전성         │ Human-in-the-loop: 이의신청·면제 AI 결정은  │
│                │ 반드시 Human Agent 최종 승인 필요           │
├────────────────┼────────────────────────────────────────────┤
│ 비용 최적화    │ 고빈도·저복잡도 → Haiku                    │
│                │ 저빈도·고복잡도 → Sonnet                   │
├────────────────┼────────────────────────────────────────────┤
│ 감사 가능성    │ 모든 AI 결정은 감사 로그에 기록             │
│                │ 이유·신뢰도·담당 Agent 포함                │
├────────────────┼────────────────────────────────────────────┤
│ 보안           │ Text-to-SQL: SELECT만 허용, DDL/DML 차단   │
│                │ Row Limit 1,000건 기본값                   │
├────────────────┼────────────────────────────────────────────┤
│ PDPA 준수      │ 개인정보(IC, 차량번호) AI 처리 최소화       │
│                │ AI 로그에 마스킹 적용                      │
└────────────────┴────────────────────────────────────────────┘
```

---

## 2. Text-to-SQL 설계

### 2.1 개요

운영 Agent (CEO, CFO, reporting-lead 등)가 자연어로 데이터 조회 요청을 입력하면 Claude Sonnet이 안전한 SQL을 생성·실행하고 결과를 반환하는 기능이다.

**핵심 제약:**
- `SELECT` 쿼리만 허용 — `INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, `TRUNCATE` 등 DDL/DML 완전 차단
- Row Limit 기본 1,000건, 최대 10,000건 (명시적 요청 시)
- 실행 전 Dry-run 검증 필수

### 2.2 아키텍처

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Text-to-SQL 처리 파이프라인                      │
└─────────────────────────────────────────────────────────────────────┘

  Agent 자연어 입력
        │
        ▼
┌───────────────────┐
│  입력 전처리       │  • 의도 분류 (조회/분석/비교/시계열)
│  (Pre-processing) │  • 민감어 필터링 (IC번호 직접 포함 등)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  스키마 컨텍스트   │  • 관련 테이블 스키마 동적 주입
│  주입              │  • 외래키 관계, 컬럼 설명, 코드 값 포함
│  (Schema Context) │  • 최대 4,000 토큰 스키마 컨텍스트
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  Claude Sonnet    │  • Model: claude-sonnet-4-5
│  SQL 생성          │  • System Prompt: SQL 생성 전용
│                   │  • Temperature: 0 (결정론적)
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│  SQL 보안 검증     │  • SELECT 전용 파서
│  (Validator)      │  • Dry-run (EXPLAIN만 실행)
│                   │  • Row Limit 자동 삽입 (LIMIT 1000)
└────────┬──────────┘
         │
        성공 ──────────────────► 실패
         │                        │
         ▼                        ▼
┌───────────────────┐    ┌────────────────────┐
│  DB 실행           │    │  에러 메시지 반환   │
│  (Read Replica)   │    │  + 재생성 요청      │
└────────┬──────────┘    └────────────────────┘
         │
         ▼
┌───────────────────┐
│  결과 포맷팅       │  • 표 형식 (Markdown Table)
│  & 반환            │  • 요약 코멘트 (AI 생성)
│                   │  • 실행 시간, 행 수 메타데이터
└───────────────────┘
```

### 2.3 지원 쿼리 유형

| 유형 | 설명 | 예시 |
|------|------|------|
| 통계/집계 | COUNT, SUM, AVG, MAX, MIN | 오늘 총 거래 건수 및 금액 |
| 비교 분석 | 기간별, 톨게이트별, 채널별 비교 | 이번 달 vs 지난 달 미납 비율 |
| 시계열 | 일별/주별/월별 추이 | 최근 30일 일별 수익 추이 |
| 조건 조회 | 특정 조건에 해당하는 레코드 | 위반 3회 이상 미납 계정 목록 |

### 2.4 보안 정책

```sql
-- 허용 예시 (SELECT만)
SELECT date_trunc('day', txn_created_at) AS day,
       COUNT(*) AS txn_count,
       SUM(amount) AS total_amount
  FROM transactions
 WHERE txn_created_at >= NOW() - INTERVAL '30 days'
 GROUP BY 1
 ORDER BY 1
 LIMIT 1000;

-- 차단 예시 (DML 시도)
-- UPDATE transactions SET status = 'PAID'; → 즉시 차단
-- DROP TABLE accounts;                     → 즉시 차단
-- INSERT INTO exemptions VALUES (...);     → 즉시 차단
```

**보안 레이어:**

```
┌─────────────────────────────────────┐
│ 레이어 1: Prompt-level 차단         │
│  → System Prompt에 SELECT 전용 명시 │
├─────────────────────────────────────┤
│ 레이어 2: 파서 기반 검증            │
│  → AST 파싱으로 DML 키워드 탐지     │
├─────────────────────────────────────┤
│ 레이어 3: Read-only DB 사용자       │
│  → DB 레벨 권한: SELECT only        │
└─────────────────────────────────────┘
```

### 2.5 자연어 → SQL 예시

**예시 1: 일별 수익 조회**
```
[자연어] 이번 달 일별 톨 수익을 보여줘

[생성 SQL]
SELECT date_trunc('day', txn_created_at)::date AS txn_date,
       COUNT(*) AS txn_count,
       SUM(amount_myr) AS revenue_myr
  FROM transactions
 WHERE txn_created_at >= date_trunc('month', NOW())
   AND status = 'COMPLETED'
 GROUP BY 1
 ORDER BY 1
 LIMIT 1000;
```

**예시 2: 채널별 비교**
```
[자연어] Channel A와 Channel B의 이번 주 거래 건수와 금액을 비교해줘

[생성 SQL]
SELECT channel_type,
       COUNT(*) AS txn_count,
       SUM(amount_myr) AS total_amount_myr,
       AVG(amount_myr) AS avg_amount_myr
  FROM transactions
 WHERE txn_created_at >= date_trunc('week', NOW())
   AND status = 'COMPLETED'
 GROUP BY channel_type
 ORDER BY channel_type
 LIMIT 1000;
```

**예시 3: 미납 현황**
```
[자연어] 미납금이 500 MYR 이상인 계정 상위 10개를 보여줘

[생성 SQL]
SELECT a.account_id,
       a.account_type,
       SUM(u.outstanding_amount_myr) AS total_unpaid_myr,
       COUNT(u.unpaid_id) AS unpaid_count
  FROM accounts a
  JOIN unpaid_transactions u ON a.account_id = u.account_id
 WHERE u.status = 'OUTSTANDING'
 GROUP BY a.account_id, a.account_type
HAVING SUM(u.outstanding_amount_myr) >= 500
 ORDER BY total_unpaid_myr DESC
 LIMIT 10;
```

**예시 4: 장비 상태**
```
[자연어] 현재 오프라인 상태인 장비 목록과 마지막 온라인 시각을 알려줘

[생성 SQL]
SELECT equipment_id,
       equipment_type,
       location_code,
       last_heartbeat_at,
       NOW() - last_heartbeat_at AS offline_duration
  FROM equipment
 WHERE status = 'OFFLINE'
 ORDER BY last_heartbeat_at ASC
 LIMIT 1000;
```

### 2.6 SLA & 성능

| 지표 | 목표값 | 초과 시 처리 |
|------|--------|-------------|
| 전체 응답 시간 | < 10초 | 15초 타임아웃 → Fallback 응답 |
| SQL 생성 시간 | < 5초 | Haiku로 재시도 |
| DB 실행 시간 | < 5초 | 쿼리 최적화 권고 + 결과 부분 반환 |
| Dry-run 시간 | < 1초 | 검증 스킵 후 직접 실행 (위험도 낮은 경우) |

---

## 3. 업무 판단 AI 설계

### 3.1 개요

이의신청(Dispute)과 면제(Exemption) 처리에서 Claude Sonnet이 사례 분석 및 권고를 제공하고, Human Agent가 최종 결정을 내리는 **Human-in-the-loop** 패턴을 적용한다.

### 3.2 이의신청 처리 권고 플로우

```
┌──────────────────────────────────────────────────────────────────────┐
│                     이의신청 처리 권고 플로우                         │
└──────────────────────────────────────────────────────────────────────┘

  이의신청 접수 (고객 제출)
         │
         ▼
  ┌─────────────────┐
  │ 데이터 수집      │  • 거래 내역, 이미지 증거
  │ (자동)           │  • 계정 이력, 위반 횟수
  │                  │  • 이의신청 사유 텍스트
  └────────┬─────────┘
           │
           ▼
  ┌─────────────────┐
  │ Claude Sonnet   │  • 사유 유형 분류
  │ 분석·권고        │  • 유사 사례 패턴 매칭
  │                  │  • 인정/기각/보류 권고
  │                  │  • 신뢰도 점수 (0~100)
  └────────┬─────────┘
           │
           ▼
  ┌─────────────────────────────────────────┐
  │          권고 결과 분기                   │
  ├──────────┬────────────┬─────────────────┤
  │신뢰도≥85  │ 신뢰도50~84│   신뢰도<50      │
  │+ 명확 인정│            │  또는 복잡 사례  │
  └────┬─────┴─────┬──────┴──────┬──────────┘
       │           │             │
       ▼           ▼             ▼
  [자동 처리   [review-lead  [Senior Agent
   후보 표시]  Agent 검토]    에스컬레이션]
       │           │             │
       └─────┬─────┘             │
             ▼                   │
  ┌─────────────────┐            │
  │ Human Agent     │◄───────────┘
  │ 최종 결정        │  승인 / 기각 / 추가조사
  │ (필수)           │
  └────────┬─────────┘
           │
           ▼
  ┌─────────────────┐
  │ 감사 로그 기록   │  • AI 권고 내용, 신뢰도
  │ (자동)           │  • Human 결정, 담당자 ID
  │                  │  • 처리 시각
  └─────────────────┘
```

### 3.3 이의신청 유형별 권고 기준

| 이의신청 유형 | 인정 권고 조건 | 기각 권고 조건 |
|--------------|---------------|---------------|
| 장비 오류 | ANPR 오인식 증거 + 장비 로그 이상 | 정상 장비 + 반복 미통과 패턴 |
| 결제 실패 | PG 오류 코드 존재 + 잔액 충분 | 잔액 부족 이력 + 재시도 없음 |
| 차량 번호판 불일치 | 등록 번호판 변경 이력 일치 | 미등록 번호판 + 위반 이력 |
| 외국 차량 | 임시 등록 증빙 서류 제출 | 증빙 없음 + 복수 위반 |
| 기술적 오류 | 시스템 장애 시간대 일치 | 정상 운영 시간대 |

### 3.4 면제 승인 권고 로직

| 면제 유형 | 승인 조건 | 필요 서류 | 담당 Agent |
|----------|----------|----------|-----------|
| 긴급 차량 | 긴급출동 기록 + 관할 기관 확인 | 출동 기록서 | exemption-lead |
| 정부 차량 | 차량 등록 데이터베이스 매칭 | 공식 차량 등록증 | exemption-lead |
| 외교 차량 | 외교부 등록 확인 | 외교 면허증 | exemption-lead + CIO |
| 장애인 차량 | JPJ 장애 등록 확인 | 장애인 차량 스티커 | exemption-lead |
| 시스템 오류 면제 | 오류 로그 + 영향 거래 목록 | 기술 보고서 | review-lead |

### 3.5 이상 거래 플래그 기준

```python
# 이상 거래 탐지 규칙 (AI 보조)
ANOMALY_RULES = {
    "velocity_check": {
        "desc": "단시간 다수 통과",
        "threshold": "동일 차량 30분 내 5회 이상 통과",
        "action": "FLAG → violation-lead 검토"
    },
    "amount_spike": {
        "desc": "비정상 금액",
        "threshold": "평균 대비 10배 이상 청구",
        "action": "FLAG → billing-lead 검토"
    },
    "phantom_transaction": {
        "desc": "ANPR 미확인 거래",
        "threshold": "결제 기록 있으나 ANPR 이미지 없음",
        "action": "FLAG → equipment-lead + review-lead"
    },
    "clone_pattern": {
        "desc": "클론 차량 의심",
        "threshold": "동일 번호판 동시간대 다른 톨게이트",
        "action": "FLAG → Compliance Agent 에스컬레이션"
    }
}
```

### 3.6 Human-in-the-loop 설계

```
┌─────────────────────────────────────────────────────────────┐
│              Human-in-the-loop 인터페이스                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  AI 권고 카드                                                 │
│  ┌──────────────────────────────────────────────────┐       │
│  │ 이의신청 #D-2026-0042                             │       │
│  │ 권고: 인정 (신뢰도: 87%)                           │       │
│  │                                                  │       │
│  │ 근거:                                             │       │
│  │  • ANPR 장비 오류 로그 확인 (2026-04-01 14:32)    │       │
│  │  • 해당 시간대 장비 #GW-012 이상 감지              │       │
│  │  • 고객 이의신청 이력 없음 (신규 이의신청)          │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  Human 결정 (필수 선택)                                       │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐      │
│  │ ✅ 승인   │  │ ❌ 기각   │  │ ⏸ 추가 조사 요청      │      │
│  └──────────┘  └──────────┘  └──────────────────────┘      │
│                                                              │
│  결정 메모 (선택)                                             │
│  ┌──────────────────────────────────────────────────┐       │
│  │ (Human Agent 코멘트 입력)                         │       │
│  └──────────────────────────────────────────────────┘       │
└─────────────────────────────────────────────────────────────┘
```

**결정 옵션:**

| 결정 | 처리 | 알림 |
|------|------|------|
| 승인 | 위반 취소 + 환불 처리 | 고객 SMS/Email 발송 |
| 기각 | 위반 유지 + 납부 독촉 | 고객 거절 사유 통보 |
| 추가 조사 | SLA 연장 + 담당자 배정 | 고객 진행 중 안내 |

### 3.7 감사 로그

모든 AI 권고 및 Human 결정은 감사 로그에 기록되며, 이는 규제 감사 및 AI 성능 개선에 활용된다.

```sql
-- ai_decision_log 테이블 (상세 설계는 섹션 8 참조)
INSERT INTO ai_decision_log (
    case_id, case_type, ai_recommendation,
    ai_confidence, ai_reasoning, human_decision,
    human_agent_id, decision_at
) VALUES (...);
```

---

## 4. 스마트 커스터마이징 AI

### 4.1 개요

운영 Agent의 사용 패턴을 분석하여 개인화된 대시보드 레이아웃과 메뉴 구조를 제안하는 기능이다. 고빈도 저복잡도 작업이므로 **Claude Haiku** 모델을 사용하여 비용을 최적화한다.

### 4.2 대시보드 레이아웃 추천

```
┌─────────────────────────────────────────────────────────────┐
│                  레이아웃 추천 로직                           │
└─────────────────────────────────────────────────────────────┘

  사용 데이터 수집 (7일 롤링 윈도우)
  • 위젯 클릭 횟수
  • 페이지 체류 시간
  • 쿼리 패턴
  • 업무 역할 (Agent 타입)
        │
        ▼
  Claude Haiku 분석
  • 역할별 템플릿 매칭
  • 개인 사용 패턴 보정
  • 레이아웃 우선순위 결정
        │
        ▼
  추천 레이아웃 생성
  • 상단: 고빈도 KPI 위젯
  • 중단: 주요 업무 액션
  • 하단: 레포트 & 알림
        │
        ▼
  Agent 확인 & 적용 (선택)
```

### 4.3 역할별 기본 레이아웃 템플릿

| Agent 역할 | 상단 위젯 | 중단 위젯 | 하단 위젯 |
|-----------|---------|---------|---------|
| CEO | 전체 수익 KPI, 목표 달성률 | 주요 알림, 임원 리포트 | 시스템 상태, 주간 트렌드 |
| CFO | 일별 수익, 미납 현황 | 결제 채널 현황, 정산 상태 | 수익 예측, 예산 vs 실적 |
| CTO | 시스템 상태, 에러율 | 장애 알림, 배포 현황 | 성능 메트릭, 용량 예측 |
| txn-lead | 실시간 거래 현황 | 오류 거래, 재처리 대기 | 시간대별 거래량 |
| violation-lead | 신규 위반 건수 | 이의신청 처리 큐 | 위반 유형 분석 |
| reporting-lead | 리포트 생성 큐 | 마감 일정, 승인 대기 | 리포트 이력 |

### 4.4 사용 빈도 기반 메뉴 재배치

```javascript
// 메뉴 재배치 알고리즘 (개념)
const reorderMenu = (usageStats, role) => {
  const baseMenu = getBaseMenuForRole(role);
  const personalizedOrder = usageStats
    .sort((a, b) => b.clickCount - a.clickCount)
    .map(item => item.menuId);
  return mergeMenuOrder(baseMenu, personalizedOrder);
};
```

**재배치 적용 조건:**
- 최소 7일 사용 데이터 누적 후 첫 추천
- 주 1회 재분석 및 추천 업데이트
- Agent가 수동으로 고정(Pin)한 항목은 재배치 제외

### 4.5 Haiku 모델 선택 이유

| 기준 | Sonnet | Haiku | 선택 |
|------|--------|-------|------|
| 레이아웃 추천 복잡도 | 필요 이상 | 충분 | **Haiku** |
| 응답 속도 | 중간 | 빠름 (<1초) | **Haiku** |
| 비용 (상대적) | 높음 | 낮음 (3~5× 절감) | **Haiku** |
| 호출 빈도 | - | - | 고빈도 (수백 회/일) |

---

## 5. AI 장애 탐지·자동 복구

### 5.1 개요

Prometheus 메트릭을 실시간 모니터링하여 임계값 초과 시 자동 알림 및 복구를 수행한다. Claude는 복잡한 장애 원인 분석 및 복구 전략 수립에 보조 역할로 활용된다.

### 5.2 탐지 지표 & 임계값

| 지표 | 경고 (Warning) | 긴급 (Critical) | 자동 복구 트리거 |
|------|---------------|----------------|----------------|
| Error Rate | > 1% | > 5% | > 5% |
| P99 Latency | > 300ms | > 500ms | > 500ms |
| CPU 사용률 | > 70% | > 90% | > 85% |
| Memory 사용률 | > 75% | > 90% | > 85% |
| Pod 재시작 횟수 | > 2회/시간 | > 5회/시간 | > 3회/시간 |
| DB Connection | > 80% Pool | > 95% Pool | > 90% Pool |
| Kafka Lag | > 10,000 msg | > 50,000 msg | > 30,000 msg |

### 5.3 자동 복구 단계별 흐름

```
┌──────────────────────────────────────────────────────────────────┐
│                     자동 복구 흐름도                              │
└──────────────────────────────────────────────────────────────────┘

  Prometheus 메트릭 수집 (15초 간격)
           │
           ▼
  임계값 초과 감지
           │
     ┌─────┴──────┐
     │            │
  Warning       Critical
  (>1%)         (>5%)
     │            │
     ▼            ▼
  알림 발송     즉시 복구 시도
  (Slack/PD)         │
                     ├─── 1차: Pod 재시작
                     │    (kubectl rollout restart)
                     │         │
                     │    회복 확인 (2분 대기)
                     │         │
                     │    회복? ──→ Yes: 완료 + 알림
                     │         │
                     │         No
                     │         │
                     ├─── 2차: HPA 스케일 업
                     │    (최대 Replica × 2)
                     │         │
                     │    회복 확인 (3분 대기)
                     │         │
                     │    회복? ──→ Yes: 완료 + 알림
                     │         │
                     │         No
                     │         │
                     └─── 3차: DevOps Agent 에스컬레이션
                              │
                              ▼
                         devops-lead 긴급 알림
                         + Claude 장애 분석 리포트
                         + 수동 복구 가이드 제공
```

### 5.4 자동 복구 상세 절차

**1차 복구: Pod 재시작**
```bash
# 자동 실행 (devops-service)
kubectl rollout restart deployment/${SERVICE_NAME} -n bos-prod
kubectl rollout status deployment/${SERVICE_NAME} -n bos-prod --timeout=120s
```

**2차 복구: HPA 스케일 업**
```yaml
# HPA 트리거 조건
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Pods
    pods:
      metric:
        name: http_requests_per_second
      target:
        type: AverageValue
        averageValue: "1000"
```

### 5.5 복구 실패 처리 (DevOps Agent 에스컬레이션)

```
복구 실패 감지
      │
      ▼
Claude Sonnet 장애 분석
• 에러 패턴 분류 (Network / Code / DB / Infra)
• 관련 로그 요약 (최근 100줄)
• 예상 원인 Top 3 도출
• 권고 복구 조치
      │
      ▼
devops-lead Agent에 전달
• 장애 분석 요약
• 권고 조치 목록
• 영향 범위 (서비스, 거래 수)
• 에스컬레이션 시각
      │
      ▼
devops-lead → CTO 보고 (Critical P0 장애 시)
```

---

## 6. Layer 3 Analytics AI (Phase 8/9)

### 6.1 개요

Phase 8/9에 도입되는 고급 분석 AI로, 요금 시뮬레이션·수익 예측·이상 탐지를 통해 전략적 의사결정을 지원한다.

### 6.2 요금 시뮬레이션 모델

```
┌─────────────────────────────────────────────────────────────┐
│                   요금 시뮬레이션 구조                        │
└─────────────────────────────────────────────────────────────┘

  입력 변수
  • 현재 요금 체계 (구간별 MYR)
  • 시뮬레이션 요금 체계 (변경안)
  • 기간 (N개월)
  • 차량 유형 분포 (승용/화물/버스)
        │
        ▼
  Claude Sonnet 시뮬레이션
  • 변경 요금 적용 시 수익 예측
  • 차량 행동 변화 추정 (이탈률 모델)
  • 채널 전환율 시뮬레이션 (A→B)
        │
        ▼
  결과 리포트
  • 수익 변화 (MYR, %)
  • 거래량 변화 예측
  • 채널별 영향도
  • 시나리오 비교 (Best/Base/Worst)
```

### 6.3 수익 예측 알고리즘

| 예측 모델 | 적용 시나리오 | 예측 기간 | 정확도 목표 |
|----------|-------------|---------|-----------|
| 7일 이동 평균 | 단기 일별 예측 | 1~7일 | ±5% |
| 계절성 보정 모델 | 공휴일·이벤트 반영 | 1~4주 | ±8% |
| 연간 트렌드 외삽 | 월별 예산 계획 | 1~3개월 | ±15% |
| 시나리오 기반 | 정책 변경 시뮬레이션 | 6~12개월 | ±20% |

### 6.4 이상 탐지 패턴

**사기 패턴 탐지:**

| 패턴명 | 설명 | 탐지 기준 | 처리 |
|--------|------|---------|------|
| Ghost Toll | 결제 없이 통과 기록 | ANPR O + 결제 X | 자동 위반 생성 |
| Clone Plate | 번호판 복제 | 동일 번호판 동시간대 복수 위치 | Compliance 에스컬레이션 |
| Bulk Fraud | 단체 미납 패턴 | 동일 기업 계정 30일 내 10건+ | CFO + Compliance 알림 |
| Velocity Fraud | 단시간 반복 통과 | 1시간 내 20회+ 동일 차량 | violation-lead 플래그 |
| Account Takeover | 비정상 계정 활동 | 24시간 내 5개국+ IP 로그인 | 계정 즉시 잠금 |

---

## 7. Paperclip 29개 Agent 조직 & MCP 연계

### 7.1 Agent 조직 전체 현황

```
┌─────────────────────────────────────────────────────────────────────┐
│                 Paperclip 29개 Agent 조직도 (BOS)                    │
└─────────────────────────────────────────────────────────────────────┘

운영팀 (6명)
├── CEO Agent          — 전체 전략·KPI 모니터링
├── CTO Agent          — 기술 아키텍처·시스템 품질
├── CFO Agent          — 재무·수익·결제 감독
├── CIO Agent          — 정보 보안·PDPA·Compliance 감독
├── Compliance Agent   — 규제 준수·감사·보고
└── PM Agent           — 프로젝트 진행·일정 관리

도메인팀 (23명)
├── 거래 도메인 (3명)
│   ├── txn-lead        — 거래 처리 전체 감독
│   ├── txn-dev-1       — Channel A (RFID/Tag) 구현
│   └── txn-dev-2       — Channel B (오픈루프/ANPR) 구현
│
├── 계정 도메인 (3명)
│   ├── account-lead    — 계정 관리 감독
│   ├── account-dev-1   — TnG/PLUS 계정 연동
│   └── account-dev-2   — 외국인 계정·임시등록
│
├── 청구 도메인 (3명)
│   ├── billing-lead    — 청구·정산 전체 감독
│   ├── billing-dev-1   — 청구서 생성·발송
│   └── billing-dev-2   — 정산·수수료 계산
│
├── 위반 도메인 (3명)
│   ├── violation-lead  — 위반 관리 전체 감독
│   ├── violation-dev-1 — 위반 탐지·생성
│   └── violation-dev-2 — 위반 통보·이력 관리
│
├── 미납 도메인 (1명)
│   └── unpaid-lead     — 미납 추적·독촉 관리
│
├── 면제 도메인 (1명)
│   └── exemption-lead  — 면제 신청·승인 처리
│
├── 검토 도메인 (1명)
│   └── review-lead     — 이의신청 검토·처리
│
├── 장비 도메인 (2명)
│   ├── equipment-lead  — 장비 관리 전체 감독
│   └── equipment-dev   — 장비 모니터링·유지보수
│
├── 리포팅 도메인 (2명)
│   ├── reporting-lead  — 리포트 설계·감독
│   └── reporting-dev   — 리포트 생성·배포
│
├── API 도메인 (1명)
│   └── api-lead        — BOS MCP Server 관리
│
└── DevOps 도메인 (3명)
    ├── devops-lead     — 인프라·배포 전체 감독
    ├── devops-dev-1    — CI/CD·컨테이너 관리
    └── devops-dev-2    — 모니터링·장애 대응

합계: 운영팀 6 + 도메인팀 23 = 29명
```

### 7.2 BOS MCP Server 8개 Tool 상세

**서비스:** `api-service` (BOS MCP Server)
**관리:** `api-lead` Agent

| # | Tool명 | 설명 | 주요 파라미터 | 담당 도메인 |
|---|--------|------|-------------|-----------|
| 1 | `get_transaction` | 단일 거래 상세 조회 | `txn_id: string` | 거래 |
| 2 | `search_transactions` | 조건별 거래 목록 조회 | `filter: TxnFilter, page, limit` | 거래 |
| 3 | `get_account` | 단일 계정 상세 조회 | `account_id: string` | 계정 |
| 4 | `search_accounts` | 조건별 계정 목록 조회 | `filter: AccountFilter, page, limit` | 계정 |
| 5 | `get_violation_history` | 계정별 위반 이력 조회 | `account_id: string, from_date, to_date` | 위반 |
| 6 | `get_equipment_status` | 장비 상태 조회 | `equipment_id?: string, location?: string` | 장비 |
| 7 | `get_kpi_summary` | KPI 요약 지표 조회 | `period: 'today'|'week'|'month', metrics: string[]` | 리포팅 |
| 8 | `get_unpaid_summary` | 미납 현황 요약 조회 | `account_id?: string, status?: UnpaidStatus` | 미납 |

**Tool 사용 예시 (api-lead Agent):**

```typescript
// get_kpi_summary 호출 예시
const kpi = await mcp.call('get_kpi_summary', {
  period: 'today',
  metrics: ['total_revenue', 'txn_count', 'error_rate', 'unpaid_amount']
});

// search_transactions 호출 예시
const disputes = await mcp.call('search_transactions', {
  filter: {
    status: 'DISPUTED',
    created_after: '2026-04-01',
    channel_type: 'CHANNEL_A'
  },
  page: 1,
  limit: 50
});
```

### 7.3 Agent 간 위임 패턴 예시

**패턴 1: 이의신청 처리 위임**
```
고객 이의신청 접수
      │
      ▼
violation-lead (1차 수신)
      │ 복잡 사례 판단
      ▼
review-lead (검토 위임)
      │ AI 권고 + Human 결정
      ▼
exemption-lead (면제 필요 시)
      │ 최종 처리 완료
      ▼
billing-lead (환불 처리 위임)
```

**패턴 2: 장애 에스컬레이션 위임**
```
devops-dev-1 (장애 1차 감지)
      │ 자동 복구 실패
      ▼
devops-lead (복구 전략 수립)
      │ P0 장애 판단
      ▼
CTO Agent (임원 보고)
      │ 서비스 영향 확인
      ▼
PM Agent (스테이크홀더 통보)
```

**패턴 3: Text-to-SQL 위임**
```
CEO Agent (자연어 질의)
      │
      ▼
api-lead (MCP Tool 라우팅)
      │ 복잡 쿼리 → Text-to-SQL
      ▼
reporting-lead (리포트 포맷팅)
      │
      ▼
CEO Agent (결과 수신)
```

---

## 8. AI 거버넌스 & 윤리

### 8.1 AI 결정 감사 로그 스키마

```sql
-- AI 결정 감사 로그 테이블
CREATE TABLE ai_decision_log (
    log_id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- 케이스 정보
    case_id             VARCHAR(50) NOT NULL,       -- 이의신청/면제 ID
    case_type           VARCHAR(30) NOT NULL,        -- 'DISPUTE'|'EXEMPTION'|'ANOMALY'
    
    -- AI 분석 결과
    ai_model            VARCHAR(50) NOT NULL,        -- 'claude-sonnet-4-5'
    ai_recommendation   VARCHAR(20) NOT NULL,        -- 'APPROVE'|'REJECT'|'PENDING'
    ai_confidence       DECIMAL(5,2) NOT NULL,       -- 0.00 ~ 100.00
    ai_reasoning        TEXT NOT NULL,               -- AI 판단 근거 (마스킹 적용)
    ai_analyzed_at      TIMESTAMPTZ NOT NULL,
    
    -- Human 결정
    human_decision      VARCHAR(20),                 -- 'APPROVED'|'REJECTED'|'ESCALATED'
    human_agent_id      VARCHAR(50),                 -- Paperclip Agent ID
    human_comment       TEXT,
    decision_at         TIMESTAMPTZ,
    
    -- 메타데이터
    ai_version          VARCHAR(20) NOT NULL,        -- AI 기능 버전
    processing_ms       INTEGER,                     -- 처리 시간 (밀리초)
    fallback_used       BOOLEAN DEFAULT FALSE,       -- Fallback 사용 여부
    
    -- 감사
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 인덱스
CREATE INDEX idx_ai_log_case_id ON ai_decision_log(case_id);
CREATE INDEX idx_ai_log_case_type ON ai_decision_log(case_type);
CREATE INDEX idx_ai_log_analyzed_at ON ai_decision_log(ai_analyzed_at);
CREATE INDEX idx_ai_log_human_agent ON ai_decision_log(human_agent_id);

-- AI 일치율 분석 뷰 (Human vs AI 결정 비교)
CREATE VIEW v_ai_human_agreement AS
SELECT
    case_type,
    DATE_TRUNC('week', ai_analyzed_at) AS week,
    COUNT(*) AS total_cases,
    SUM(CASE WHEN ai_recommendation = human_decision THEN 1 ELSE 0 END) AS agreed,
    ROUND(
        SUM(CASE WHEN ai_recommendation = human_decision THEN 1 ELSE 0 END)::DECIMAL
        / COUNT(*) * 100, 2
    ) AS agreement_rate_pct
FROM ai_decision_log
WHERE human_decision IS NOT NULL
GROUP BY 1, 2
ORDER BY 2 DESC, 1;
```

### 8.2 개인정보 마스킹 정책 (PDPA)

```
┌─────────────────────────────────────────────────────────────┐
│              AI 로그 개인정보 마스킹 규칙                     │
├──────────────────┬──────────────────┬───────────────────────┤
│ 데이터 유형       │ 원본             │ 마스킹 형식            │
├──────────────────┼──────────────────┼───────────────────────┤
│ IC 번호          │ 900101-14-1234   │ 9001**-**-1234        │
│ 차량 번호판       │ WXY 1234        │ W** 1234              │
│ 이메일           │ user@mail.com    │ u***@mail.com         │
│ 전화번호         │ 0123456789      │ 012***6789            │
│ 계정 ID          │ ACC-00012345    │ ACC-*****345           │
└──────────────────┴──────────────────┴───────────────────────┘
```

### 8.3 편향 방지 & 공정성 가이드라인

| 항목 | 기준 | 모니터링 주기 |
|------|------|-------------|
| 국적별 이의신청 승인율 | ±5% 이내 편차 허용 | 월별 |
| 차량 유형별 위반 플래그율 | 실제 위반 비율과 ±10% 이내 | 월별 |
| AI vs Human 결정 일치율 | 최소 75% 유지 | 주별 |
| 신뢰도 점수 분포 | 과도한 극단값(0~10, 90~100) < 20% | 주별 |

**편향 탐지 시 처리:**
1. ai-lead Agent에 알림
2. 해당 케이스 유형 AI 권고 일시 중단
3. 프롬프트 재검토 및 수정
4. 재검토 후 점진적 재도입

### 8.4 PDPA 준수 사항

```
┌─────────────────────────────────────────────────────────────┐
│           PDPA (개인정보 보호법) AI 처리 제한                 │
├─────────────────────────────────────────────────────────────┤
│ 1. 목적 제한                                                 │
│    → AI 분석은 업무 판단 지원 목적으로만 사용                 │
│    → AI 프로파일링 결과를 마케팅에 활용 금지                  │
│                                                              │
│ 2. 데이터 최소화                                             │
│    → AI 프롬프트에 필요 최소 데이터만 포함                    │
│    → IC 번호, 전화번호는 마스킹 후 전달                       │
│                                                              │
│ 3. 보유 기간                                                 │
│    → AI 분석 로그: 5년 보관 (규제 요구사항)                   │
│    → AI 프롬프트 원본: 90일 후 삭제                           │
│                                                              │
│ 4. 당사자 권리                                               │
│    → AI 자동 결정에 대한 Human 검토 요청 권리 보장            │
│    → AI 결정 근거 공개 요청 시 제공 (마스킹 적용)             │
└─────────────────────────────────────────────────────────────┘
```

---

## 9. Fallback & 비용 관리

### 9.1 3단계 Fallback 전략

```
┌─────────────────────────────────────────────────────────────┐
│                  AI Fallback 전략                             │
└─────────────────────────────────────────────────────────────┘

  1단계 (기본): Claude Sonnet
  ┌──────────────────────────────────────────┐
  │ Model: claude-sonnet-4-5                  │
  │ 사용: Text-to-SQL, 업무 판단, Analytics AI│
  │ 타임아웃: 10초 (Text-to-SQL), 15초 (판단) │
  │ 실패 조건: 타임아웃 | API 오류 | Rate Limit│
  └───────────────────┬──────────────────────┘
                      │ 실패
                      ▼
  2단계 (강등): Claude Haiku
  ┌──────────────────────────────────────────┐
  │ Model: claude-haiku-4-5                   │
  │ 기능 제한: 단순 분류·요약만 수행          │
  │ 타임아웃: 5초                             │
  │ 실패 조건: 타임아웃 | API 오류            │
  │ 알림: devops-lead에 Haiku Fallback 발생  │
  └───────────────────┬──────────────────────┘
                      │ 실패
                      ▼
  3단계 (최후): 미리 정의된 템플릿
  ┌──────────────────────────────────────────┐
  │ 방식: 규칙 기반 (Rule-based)             │
  │ Text-to-SQL: 미리 정의된 쿼리 카탈로그  │
  │ 업무 판단: "수동 검토 필요" 권고로 대체  │
  │ 스마트 커스터마이징: 역할별 기본 템플릿  │
  │ 알림: CTO + CIO에 AI 전면 장애 보고      │
  └──────────────────────────────────────────┘
```

### 9.2 Fallback 트리거 조건

| 상황 | Fallback 레벨 | 복구 조건 |
|------|-------------|---------|
| Sonnet API 타임아웃 (>임계값) | Sonnet → Haiku | Sonnet 응답 재개 |
| Anthropic API Rate Limit | Sonnet → Haiku | Rate Limit 해제 (분 단위) |
| Anthropic API 전체 장애 | → 템플릿 | API 복구 확인 후 재전환 |
| Haiku 타임아웃 | Haiku → 템플릿 | Haiku 복구 확인 |
| 예산 한도 초과 | Sonnet → Haiku → 차단 | 월초 예산 리셋 |

### 9.3 모델별 비용 최적화 기준

```
┌─────────────────────────────────────────────────────────────────┐
│                    모델 선택 의사결정 트리                        │
└─────────────────────────────────────────────────────────────────┘

  호출 빈도가 높은가?  (하루 100회+)
      │
   Yes│                  │No
      ▼                  ▼
  응답 품질이           복잡한 추론이
  충분한가?             필요한가?
  (Haiku 기준)              │
      │                     │
   Yes│     │No         Yes │          │No
      ▼     ▼              ▼           ▼
   Haiku  Sonnet         Sonnet      Haiku
```

**기능별 비용 최적화 적용:**

| 기능 | 모델 | 선택 근거 |
|------|------|---------|
| Text-to-SQL | Sonnet | 정확성 최우선, 오류 비용 높음 |
| 이의신청 분석 | Sonnet | 복잡한 사례 판단, 법적 영향 |
| 면제 승인 권고 | Sonnet | 규제 준수 민감도 높음 |
| 대시보드 커스터마이징 | Haiku | 단순 패턴 매칭, 고빈도 호출 |
| 메뉴 재배치 추천 | Haiku | 단순 정렬, 실시간 필요 |
| 장애 분석 요약 | Sonnet | 에스컬레이션 시만 호출 (저빈도) |
| 쿼리 카탈로그 검색 | Haiku | 유사도 매칭, 고빈도 |

### 9.4 월별 AI 비용 모니터링

```
비용 임계값 알림 체계:
• 예산 70% 도달 → CFO Agent 알림
• 예산 85% 도달 → Haiku 우선 전환 시작
• 예산 95% 도달 → 비필수 AI 기능 일시 중단
• 예산 100% 초과 → 전체 AI 차단 (템플릿 전환)

모니터링 지표:
• 일별 토큰 사용량 (Input / Output 분리)
• 기능별 비용 분배
• Fallback 발생 횟수 및 사유
• 월별 AI ROI (처리 건수 × 단가 절감)
```

---

## 10. 참조 문서

| 문서 | 경로 | 관련 섹션 |
|------|------|---------|
| 시스템 개요 | `02_system/01_system_overview.md` | 전체 아키텍처, Layer 구조 |
| 서비스 도메인 | `02_system/02_service_domains.md` | 서비스별 기능 정의 |
| 기술 스택 | `02_system/03_tech_stack.md` | Kubernetes, Prometheus, Kafka |
| 외부 연동 | `02_system/05_external_integration.md` | TnG, PLUS, PG 연동 |
| Paperclip 조직 | `04_dev/02_paperclip_org.md` | 29개 Agent 상세 역할 |
| 데이터 아키텍처 | `03_data/01_data_architecture.md` | DB 스키마, Read Replica |
| RBAC 설계 | `03_data/03_rbac_design.md` | Agent 권한, RLS 패턴 |
| 보안 컴플라이언스 | `03_data/05_security_compliance.md` | PDPA, 보안 인증 |
| 거버넌스 게이트 | `05_governance/01_decision_gates.md` | G-HARD 0~7 게이트 |

---

*문서 버전: v1.0 | 최초 작성: 2026-04 | 담당: AI Lead, CTO Agent*
*다음 검토 시점: Phase 4 착수 시 (업무 판단 AI 상세 설계 반영)*
