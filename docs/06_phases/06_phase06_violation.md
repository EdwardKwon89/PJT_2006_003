# Phase 6: 위반 & 미납 관리
## 06_phases/06_phase06_violation.md
## v1.0 | 2026-04 | 참조: 01_business/05_payment_architecture.md, 07_skills/payment-failure-scenarios/SKILL.md

---

> **Agent 사용 지침**
> `violation-lead`, `unpaid-lead` Agent가 미납·위반 처리 구현 시 반드시 로드.
> 본 문서는 Phase 6 실행의 유일한 정식 기준 문서이며, Tier 1~4 미납 처리, JPJ 도로세 차단, Write-off 기준의 구현 기준으로 사용된다.
> 차단/해제 API 및 Write-off 처리는 반드시 `Compliance` + `violation-lead` 검토 후 머지한다.

---

## 1. Phase 개요

### 1.1 목적 및 범위

Phase 6는 Malaysia SLFF/MLFF Tolling BOS의 **위반 & 미납 관리 도메인**을 구축하는 단계다. Phase 5에서 확정된 일별 정산 집계 기반으로 미납 트랜잭션을 탐지하고, 4단계 단계적 에스컬레이션(Tier 1~4)을 통해 채권 회수를 자동화하며, JPJ와 연동하여 도로세 차단을 실행하고, 회수 불가 채권에 대한 Write-off 절차를 정의한다.

**핵심 목표:**
- 미납 트랜잭션 탐지 (정산 T+1일 기준 자동 탐지)
- Tier 1~4 단계적 에스컬레이션 자동화
- JPJ 도로세 차단/해제 API 연동
- 위반 범칙금 산정 및 청구 자동화
- Write-off 기준 정의 및 감사 추적
- 이의신청 워크플로우 구현

### 1.2 Phase 연계

| 구분 | 내용 |
|------|------|
| **선행 Phase** | Phase 5 — 빌링 & 정산 (`daily_settlement_summary: FINALIZED` 완료 필수) / Phase 4 — 계정 서비스 (차량·소유자 정보 API 완료 필수) |
| **후행 Phase** | Phase 7 — 모니터링 & 장애 대응 (위반 처리 이상 상황 모니터링) |
| **예상 기간** | **3주** (Sprint 13~15) |
| **병렬 가능 작업** | Tier 1~2 자동화 개발 ↔ JPJ 차단 API 연동 개발 (독립 진행 후 통합) |

### 1.3 미납 처리 4단계 에스컬레이션 구조

```
[정산 확정 T+1] → 미납 탐지
        │
        ▼
  ┌──────────────────────────────────────┐
  │  Tier 1: 자동 알림 (D+1 ~ D+7)      │
  │  - SMS/이메일 3회 발송               │
  │  - APPs 푸시 알림                    │
  │  - 추가 수수료 없음                  │
  └──────────────┬───────────────────────┘
                 │ D+8 (미납 지속)
                 ▼
  ┌──────────────────────────────────────┐
  │  Tier 2: 연체 수수료 부과 (D+8~D+30)│
  │  - 원금 + 연체 수수료 10%            │
  │  - 주 1회 알림 발송                  │
  │  - 계정 서비스 일부 제한             │
  └──────────────┬───────────────────────┘
                 │ D+31 (미납 지속)
                 ▼
  ┌──────────────────────────────────────┐
  │  Tier 3: JPJ 도로세 차단 (D+31~D+90)│
  │  - JPJ API 연동 차단 요청            │
  │  - 차량 도로세 갱신 차단             │
  │  - 원금 + 연체 수수료 20%            │
  └──────────────┬───────────────────────┘
                 │ D+91 (미납 지속)
                 ▼
  ┌──────────────────────────────────────┐
  │  Tier 4: Write-off / 법적 조치       │
  │  - 채권 Write-off 처리               │
  │  - 법률 부서 이관                    │
  │  - 신용 기관 보고 (선택적)          │
  └──────────────────────────────────────┘
```

---

## 2. 담당 Agent 및 역할 분담

### 2.1 Phase 6 참여 Agent

| Agent | 역할 | 주요 책임 |
|-------|------|---------|
| `violation-lead` | 기술 리드 | 위반·미납 시스템 아키텍처, 에스컬레이션 로직 설계, 코드 리뷰 총괄 |
| `unpaid-lead` | 채권 관리 리드 | Tier 로직 구현, Write-off 절차, 이의신청 워크플로우 |
| `violation-dev` | 개발 담당 | 미납 탐지 배치, Tier 자동화, 알림 발송 시스템 |
| `account-lead` | 계정 연동 | 차량·소유자 데이터 제공, 계정 상태 동기화 |
| `Compliance` | 규제 검토 | JPJ 차단 절차 법적 검토, Write-off 기준 승인 |

### 2.2 협업 인터페이스

| 협업 대상 | 협업 내용 |
|----------|---------|
| `billing-lead` | 정산 확정 상태 이벤트 구독 스키마 정의 |
| `account-lead` | 차량 소유자 연락처, 계정 상태 변경 API |
| `api-lead` | JPJ 도로세 차단/해제 API 클라이언트 구현 |
| `devops-lead` | 알림 발송 서비스(SNS/SES), 배치 스케줄링, 감사 로그 S3 아카이브 |

---

## 3. 주요 태스크 체크리스트

### 3.1 미납 탐지 배치

- [ ] `UnpaidDetectionBatch` Airflow DAG 구현 (매일 06:00)
  - 전일 `daily_settlement_summary: FINALIZED` 기준 미납 트랜잭션 탐지
  - 기준: `payment_status = 'UNPAID'` AND `business_date = T-1`
  - 기존 미납 목록과 중복 탐지 방지 (Idempotent 처리)
- [ ] `unpaid_cases` 테이블 설계 및 마이그레이션
  ```sql
  CREATE TABLE unpaid_cases (
      id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      trip_id          UUID NOT NULL REFERENCES trip_records(id),
      vehicle_tag_id   UUID NOT NULL,
      owner_id         UUID NOT NULL,
      principal_amount NUMERIC(12,2) NOT NULL,
      penalty_amount   NUMERIC(12,2) NOT NULL DEFAULT 0,
      total_amount     NUMERIC(12,2) NOT NULL,
      tier             SMALLINT NOT NULL DEFAULT 1, -- 1~4
      tier_updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
      status           VARCHAR(20) NOT NULL DEFAULT 'OPEN',
      jpj_blocked      BOOLEAN NOT NULL DEFAULT false,
      writeoff_at      TIMESTAMPTZ,
      created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
      updated_at       TIMESTAMPTZ NOT NULL DEFAULT now()
  );
  CREATE INDEX idx_unpaid_cases_owner ON unpaid_cases(owner_id);
  CREATE INDEX idx_unpaid_cases_tier ON unpaid_cases(tier, status);
  ```

### 3.2 Tier 에스컬레이션 자동화

- [ ] `TierEscalationBatch` Airflow DAG 구현 (매일 07:00)
  - Tier 1→2: `created_at + 7 days < now()` AND `status = 'OPEN'`
  - Tier 2→3: `tier = 2` AND `tier_updated_at + 23 days < now()`
  - Tier 3→4: `tier = 3` AND `tier_updated_at + 60 days < now()`
- [ ] 연체 수수료 계산 로직
  - Tier 2: `principal_amount * 0.10` 추가
  - Tier 3: `principal_amount * 0.20` 추가 (누적 아님, 대체 적용)
- [ ] 에스컬레이션 이력 테이블 (`unpaid_tier_history`)
  - 모든 Tier 변경에 `from_tier`, `to_tier`, `changed_at`, `reason` 기록

### 3.3 알림 발송 시스템 (Tier 1~2)

- [ ] 알림 발송 서비스 구현 (`notification-service` 연동 또는 내장)
  - 채널: SMS (Twilio/Telco API), 이메일 (AWS SES), 앱 푸시 (FCM)
  - Tier 1: D+1, D+4, D+7 총 3회 발송
  - Tier 2: 매주 월요일 발송 (D+8 ~ D+30)
- [ ] 알림 템플릿 관리
  - 3언어 지원: BM, EN, ZH
  - 금액, 마감일, 납부 링크 동적 삽입
- [ ] 발송 이력 테이블 (`notification_log`)
  - `case_id`, `channel`, `template_id`, `sent_at`, `status`

### 3.4 JPJ 도로세 차단/해제 연동

- [ ] JPJ 차단 API 클라이언트 구현 (`JpjBlockingClient`)
  - 차단 요청: `POST https://api.jpj.gov.my/roadtax/v1/block`
  - 해제 요청: `POST https://api.jpj.gov.my/roadtax/v1/unblock`
  - 인증: mTLS + API Key (JPJ 발급)
  - 요청 페이로드: `{ "vehicle_plate": "...", "reason": "TOLL_UNPAID", "reference_no": "..." }`
- [ ] 차단 Airflow DAG 구현 (`jpj_block_batch`, 매일 09:00)
  - 대상: `tier = 3` AND `jpj_blocked = false`
  - 차단 성공 시 `jpj_blocked = true` 업데이트
  - 실패 시 재시도 3회 (1시간 간격)
- [ ] 납부 완료 시 JPJ 해제 자동 처리
  - 납부 이벤트 수신 → `jpj_blocked = true` 확인 → 해제 API 호출
  - 해제 실패 시 수동 처리 큐 등록
- [ ] JPJ 연동 감사 로그 (`jpj_block_audit`)
  - 모든 차단/해제 요청·응답 기록 (7년 보관)
  - 법적 증거 보존을 위한 Blockchain 발행

### 3.5 이의신청 워크플로우

- [ ] 이의신청 접수 API (`POST /api/v1/violation/disputes`)
  - 입력: `case_id`, `dispute_reason`, `evidence_files[]`
  - 이의신청 접수 시 Tier 에스컬레이션 일시 정지
  - SLA: 이의신청 후 5 영업일 내 처리
- [ ] 이의신청 심사 API (내부용, `review-lead` Agent 전용)
  - `PUT /api/v1/violation/disputes/{id}/approve` — 이의신청 승인 (미납 취소)
  - `PUT /api/v1/violation/disputes/{id}/reject` — 이의신청 기각 (에스컬레이션 재개)
- [ ] 이의신청 이력 테이블 (`dispute_cases`)

### 3.6 Write-off 처리

- [ ] Write-off 기준 정의 (CFO + Compliance 승인 필요)
  - Tier 4 진입 후 6개월 경과
  - 소액 기준: 미납 총액 < RM 10 (즉시 Write-off)
  - 채무자 사망·파산 등 특별 사유
- [ ] Write-off 실행 배치 (월 1회, 담당자 수동 승인 후 실행)
  - `status: 'OPEN'` → `'WRITTEN_OFF'`
  - `writeoff_at` 타임스탬프 기록
  - CFO 승인 전자서명 저장
- [ ] Write-off 감사 리포트 자동 생성 (월 1회)

---

## 4. 위반 처리 플로우 다이어그램

```
[billing: FINALIZED T+1]
         │ Kafka: settlement.finalized
         ▼
[미납 탐지 배치 06:00]
   │ UNPAID 탐지
   ▼
[unpaid_cases 생성 (Tier 1)]
         │
         │ D+1
         ▼
[알림 발송: SMS + 이메일 + 앱 푸시]
   ├─ D+1 1차 발송
   ├─ D+4 2차 발송
   └─ D+7 3차 발송

   │ D+8 미납 지속
   ▼
[Tier 2 에스컬레이션]
 - 연체 수수료 10% 추가
 - 주 1회 알림 (D+8~D+30)

   │ D+31 미납 지속
   ▼
[Tier 3 에스컬레이션]
 - JPJ 도로세 차단 요청
 - 연체 수수료 20% 적용

   │ D+91 미납 지속
   ▼
[Tier 4] ──→ Write-off 후보 등록
             │ 6개월 경과 + CFO 승인
             ▼
           [Write-off 실행]
           법률 부서 이관
```

---

## 5. 완료 기준 체크리스트

### 5.1 기능 완료 기준

| 영역 | 기준 항목 | 검증 방법 |
|------|---------|---------|
| 미납 탐지 | 정산 T+1 06:00 이전 탐지 완료 | Airflow DAG 실행 이력 |
| Tier 에스컬레이션 | D+7/30/90 자동 Tier 상승 | 시뮬레이션 데이터 주입 |
| JPJ 차단 | Tier 3 진입 후 24시간 내 차단 | JPJ 테스트 환경 연동 |
| 알림 발송 | 각 Tier별 발송 횟수 준수 | 알림 발송 로그 확인 |
| 이의신청 | 5 영업일 내 처리 SLA | 처리 시간 측정 테스트 |
| Write-off | CFO 승인 후만 실행 가능 | 승인 없이 실행 시 차단 확인 |

### 5.2 성능 기준

| 지표 | 목표값 |
|------|-------|
| 미납 탐지 배치 처리 시간 (100만 건) | < 15분 |
| JPJ 차단 API 응답시간 | < 3초/건 |
| 알림 발송 처리량 | > 1,000 건/분 |
| 이의신청 API P99 | < 300ms |

---

## 6. 리스크 & 대응

| 리스크 | 가능성 | 영향 | 대응 방안 |
|-------|-------|------|---------|
| JPJ API 다운 | 중간 | 높음 | 재시도 3회 + 수동 처리 큐 + PagerDuty 알림 |
| 이중 차단 요청 | 낮음 | 중간 | `jpj_blocked = true` 확인 후 요청, Idempotent 처리 |
| 알림 과다 발송 | 낮음 | 중간 | 발송 이력 확인 후 중복 발송 방지 (24시간 쿨다운) |
| Write-off 오류 (유효 채권) | 매우 낮음 | 매우 높음 | CFO 수기 서명 + 롤백 API 구비 |

---

## 7. 참조 문서

| 문서 | 경로 |
|------|------|
| 결제 아키텍처 | [`01_business/05_payment_architecture.md`](../01_business/05_payment_architecture.md) |
| 계정 관리 Phase | [`06_phases/04_phase04_account.md`](./04_phase04_account.md) |
| 빌링 & 정산 Phase | [`06_phases/05_phase05_billing.md`](./05_phase05_billing.md) |
| RBAC 설계 | [`03_data/03_rbac_design.md`](../03_data/03_rbac_design.md) |
| 보안 & 컴플라이언스 | [`03_data/05_security_compliance.md`](../03_data/05_security_compliance.md) |

---

*Malaysia SLFF/MLFF Tolling BOS — Phase 6 위반 & 미납 관리 v1.0*
*생성일: 2026-04 | 담당: violation-lead, unpaid-lead, violation-dev, Compliance*
