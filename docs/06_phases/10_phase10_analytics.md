# Phase 10: 분석 & 리포팅 플랫폼
## 06_phases/10_phase10_analytics.md
## v1.0 | 2026-04 | 참조: 02_system/04_ai_features.md, 07_skills/text-to-sql-engine/SKILL.md

---

> **Agent 사용 지침**
> `reporting-lead`, `CIO` Agent가 분석 & 리포팅 플랫폼 구현 시 반드시 로드.
> Text-to-SQL 쿼리 모델 및 데이터 접근 범위는 반드시 `CIO` + `Compliance` 검토 후 머지한다.

---

## 1. Phase 개요

### 1.1 목적 및 범위

Phase 10은 **분석 & 리포팅 플랫폼**을 구축하는 단계다. Phase 8 (Big Data) Gold Layer 기반으로 경영진 BI 대시보드, Text-to-SQL 자연어 쿼리 엔진, KPI 자동 리포트, 수익 시뮬레이션 모델을 완성한다.

**핵심 목표:**
- 실시간 KPI BI 대시보드 (경영진/운영자/CFO 맞춤형)
- Text-to-SQL 엔진: 자연어로 데이터 조회 (SLA < 10초)
- 일별/월별 KPI 리포트 자동 생성 및 배포
- 요금 수익 시뮬레이션 모델 (교통 패턴 기반 예측)

### 1.2 Phase 연계

| 구분 | 내용 |
|------|------|
| **선행 Phase** | Phase 8 — Big Data (Gold Layer 완료 필수) |
| **후행 Phase** | Phase 11 — 컴플라이언스 & 감사 |
| **예상 기간** | **3주** (Sprint 22~24) |

### 1.3 데이터 플로우

```
[Gold Layer: AGG_DAILY_*, AGG_MONTHLY_*]
         │
    ┌────┴───────────────┐
    ▼                    ▼
[ClickHouse OLAP]   [PostgreSQL Read Replica]
[Grafana BI]        [Text-to-SQL Engine (Claude)]
```

---

## 2. 담당 Agent 및 역할

| Agent | 역할 | 주요 책임 |
|-------|------|---------|
| `reporting-lead` | 기술 리드 | 분석 아키텍처, Text-to-SQL 설계, 대시보드 구성 |
| `reporting-dev` | 개발 담당 | BI 구현, KPI 배치 리포트 개발 |
| `CIO` | 데이터 거버넌스 | 데이터 접근 정책, 쿼리 범위 승인 |
| `AI Lead` | AI 엔진 | Text-to-SQL 프롬프트 최적화 |
| `CFO` | 비즈니스 요구 | KPI 항목 정의, 리포트 형식 승인 |

---

## 3. 주요 태스크 체크리스트

### 3.1 BI 대시보드 (Grafana + ClickHouse)

- [ ] **Executive Dashboard**: 수납액, 미납율, Channel A/B 비율, 콘세셔네어별 성과
- [ ] **Operations Dashboard**: 요금소별 트랜잭션 실시간 히트맵, 장비 가용성
- [ ] **Finance Dashboard**: 일별 정산, JVC 수수료, TnG Channel B 정산 현황

### 3.2 Text-to-SQL 엔진

- [ ] `TextToSqlService` 구현
  - 자연어 → Claude Sonnet → SQL 생성 → 안전성 검증 → 실행 → 요약
  - SELECT Only 제한, 위험 키워드 차단
  - 민감 컬럼 마스킹 (vehicle_plate, owner_name, phone)
  - RBAC 연동: 역할별 접근 가능 테이블 제한
- [ ] 쿼리 예시 (퓨샷)
  ```
  Q: "이번 달 Channel A 총 수납액이 얼마야?"
  → SELECT SUM(gross_amount) FROM agg_monthly_summary WHERE channel='A' AND year_month=TO_CHAR(NOW(),'YYYY-MM')
  ```
- [ ] SLA: P99 < 10초 / 감사 로그 (`text_to_sql_audit_log`)

### 3.3 KPI 자동 리포트

- [ ] 일별 KPI 리포트 (매일 07:00): 콘세셔네어별 수납액, 미납율, 전일 대비 증감
- [ ] 월별 경영 리포트 (매월 2일 08:00): 전월 실적 종합, ROI, 전년 동월 대비
- [ ] 배포: PDF 이메일 / Excel 공유 드라이브 / Slack 링크

### 3.4 수익 시뮬레이션 모델

- [ ] 교통 패턴 기반 3개월 수납액 예측 (ARIMA / Prophet)
- [ ] 요금 변경 시뮬레이션 (시뮬레이션 요금표 → 예상 수입 변화)
- [ ] CFO 전용 시뮬레이션 대시보드

---

## 4. 완료 기준 체크리스트

| 영역 | 기준 항목 | 검증 방법 |
|------|---------|---------|
| BI 대시보드 | 3종 실시간 데이터 정상 표시 | Gold Layer 데이터 기준 검증 |
| Text-to-SQL | 10개 샘플 쿼리 정확률 > 90% | 사전 정의 쿼리 정합성 검증 |
| Text-to-SQL SLA | P99 < 10초 | 동시 10 쿼리 부하 테스트 |
| KPI 리포트 | 일별 07:00 이전 발송 완료 | Airflow DAG 실행 이력 |
| 수익 예측 | 12개월 모의 MAPE < 10% | 과거 데이터로 검증 |

---

## 5. 참조 문서

| 문서 | 경로 |
|------|------|
| AI 기능 설계 | [`02_system/04_ai_features.md`](../02_system/04_ai_features.md) |
| 데이터 아키텍처 | [`03_data/01_data_architecture.md`](../03_data/01_data_architecture.md) |
| RBAC 설계 | [`03_data/03_rbac_design.md`](../03_data/03_rbac_design.md) |
| Big Data Phase 8 | [`06_phases/08_phase08_bigdata.md`](./08_phase08_bigdata.md) |
| AI Feature Phase 9 | [`06_phases/09_phase09_ai.md`](./09_phase09_ai.md) |

---

*Malaysia SLFF/MLFF Tolling BOS — Phase 10 분석 & 리포팅 플랫폼 v1.0*
*생성일: 2026-04 | 담당: reporting-lead, reporting-dev, CIO, AI Lead, CFO*
