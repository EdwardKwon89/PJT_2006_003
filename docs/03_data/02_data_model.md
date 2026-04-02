# 02. Data Model 및 테이블 정의

**Document ID:** WAVE3A-02  
**Maintained By:** Data Architecture Team / DB Lead  
**Last Updated:** 2026-04-01  
**Status:** Draft for Review

---

## 목차

1. [개요](#개요)
2. [테이블 목록 (50+)](#테이블-목록-50)
3. [핵심 테이블 스키마](#핵심-테이블-스키마)
4. [Channel A/B 트랜잭션 구조](#channel-ab-트랜잭션-구조)
5. [집계 테이블 (AGG_* 정의)](#집계-테이블-agg_-정의)
6. [테이블 관계도 (ERD)](#테이블-관계도-erd)
7. [인덱싱 전략](#인덱싱-전략)
8. [데이터 파티셔닝](#데이터-파티셔닝)
9. [참조 문서](#참조-문서)

---

## 개요

이 문서는 Malaysia Tolling BOS의 **핵심 데이터 모델**을 정의한다. 50개 이상의 테이블을 통해:

- **Transaction Engine**: 일일 10,000 TPS 처리
- **Channel A/B**: RFID/ANPR, TnG 양 채널의 독립 트랜잭션 구조
- **Aggregation**: 실시간 집계를 통한 보고 및 대시보드 지원
- **RBAC & Data Boundary**: 30개 역할 기반 데이터 접근 제어

모든 테이블은 PostgreSQL 12+ 기반이며, JSON/JSONB 확장을 활용한 반정규화 설계를 포함한다.

---

## 테이블 목록 (50+)

### 1. 핵심 거래 테이블 (10개)

| # | 테이블명 | 용도 | 주요 컬럼 | 보유 기간 |
|----|---------|------|---------|---------|
| 1 | `transactions` | 모든 통행료 거래 원본 | trip_id, vehicle_id, toll_amount, channel, status | 7년 |
| 2 | `transactions_channel_a` | Channel A (RFID/ANPR) 거래 | clearing_account_id, tag_id, retry_count, float_days | 7년 |
| 3 | `transactions_channel_b` | Channel B (TnG) 거래 | tng_reference_id, tng_balance_before, tng_fee_amount | 7년 |
| 4 | `payment_logs` | 결제 시도 로그 | transaction_id, payment_method, amount, result_code | 2년 |
| 5 | `transaction_failures` | 실패한 거래 추적 | failure_reason, error_code, retry_policy_id, tier_level | 1년 |
| 6 | `clearing_account_batches` | Clearing Center 배치 정산 | batch_id, total_amount, settlement_date, reconciliation_status | 7년 |
| 7 | `tng_settlement_batches` | TnG 일일 정산 | batch_date, total_amount, tng_fee, jvc_net_amount | 7년 |
| 8 | `retry_policies` | 재시도 정책 마스터 | policy_id, max_retries, retry_intervals, fallback_channel | 1년 |
| 9 | `lane_realtime_stats` | Lane별 실시간 통계 | lane_id, transaction_count, total_amount, failure_count | 30일 |
| 10 | `transaction_audit_trail` | 거래 감시 로그 | transaction_id, changed_by, change_type, change_timestamp | 2년 |

---

### 2. 계정 & 차량 관리 테이블 (8개)

| # | 테이블명 | 용도 | 주요 컬럼 | 보유 기간 |
|----|---------|------|---------|---------|
| 11 | `vehicles` | 등록 차량 마스터 | vehicle_id, license_plate, owner_id, tag_id, vehicle_type | 영구 |
| 12 | `vehicle_tags` | RFID 태그 관리 | tag_id, vehicle_id, tag_type, activation_date, expiry_date | 영구 |
| 13 | `vehicle_accounts` | 차량 별 Clearing 계정 | account_id, vehicle_id, account_type, balance, linked_tng_account | 영구 |
| 14 | `vehicle_owners` | 차량 소유자 정보 | owner_id, name, phone, email, address, identity_number | 영구 (PDPA) |
| 15 | `vehicle_blacklist` | 미결제 또는 위반 차량 | vehicle_id, blacklist_reason, listed_date, expiry_date | 1년 |
| 16 | `tng_linked_accounts` | TnG 카드 연동 | tng_card_id, vehicle_id, link_date, last_transaction_date | 영구 |
| 17 | `vehicle_exemptions` | 차량별 감면 정보 | exemption_id, vehicle_id, exemption_type, validity_period | 영구 |
| 18 | `vehicle_suspension_logs` | 서스펜션 기록 | vehicle_id, suspension_reason, suspension_date, lifted_date | 2년 |

---

### 3. 미결제 관리 테이블 (8개)

| # | 테이블명 | 용도 | 주요 컬럼 | 보유 기간 |
|----|---------|------|---------|---------|
| 19 | `unpaid_transactions` | 미결제 거래 정의 | unpaid_id, transaction_id, tier_level, first_unpaid_date | 3년 |
| 20 | `unpaid_tier1` | Tier 1 (즉시 미결제) | unpaid_id, auto_retry_count, next_retry_timestamp | 30일 |
| 21 | `unpaid_tier2` | Tier 2 (30일 이상) | unpaid_id, jpj_inquiry_done, owner_notified_date, tier2_entry_date | 1년 |
| 22 | `unpaid_tier3` | Tier 3 (법적 절차) | unpaid_id, legal_notice_sent_date, court_case_id, case_status | 2년 |
| 23 | `unpaid_tier4` | Tier 4 (포기) | unpaid_id, writeoff_date, approval_by, writeoff_reason | 영구 |
| 24 | `unpaid_notifications` | 미결제 통지 기록 | notification_id, unpaid_id, notification_type, sent_date, acknowledgment_date | 1년 |
| 25 | `collection_actions` | 추심 활동 기록 | action_id, unpaid_id, action_type, action_date, action_by | 2년 |
| 26 | `dispute_claims` | 분쟁 청구 (차량주 이의) | dispute_id, unpaid_id, dispute_date, claim_status, resolution_date | 2년 |

---

### 4. 결제 채널별 테이블 (6개)

| # | 테이블명 | 용도 | 주요 컬럼 | 보유 기간 |
|----|---------|------|---------|---------|
| 27 | `clearing_center_accounts` | Clearing Center 계정 마스터 | cc_account_id, account_type, bank_partner, settlement_cycle | 영구 |
| 28 | `clearing_center_reconciliation` | Clearing Center 조정 | reconciliation_id, batch_date, submitted_amount, actual_amount, variance | 7년 |
| 29 | `tng_api_calls` | TnG API 호출 로그 | api_call_id, transaction_id, endpoint, request_payload, response_code | 6개월 |
| 30 | `tng_reconciliation_details` | TnG 상세 조정 | reconciliation_id, transaction_date, transacted_amount, settled_amount | 7년 |
| 31 | `payment_gateways` | 결제 게이트웨이 설정 | gateway_id, gateway_type, provider, api_endpoint, credentials_encrypted | 영구 |
| 32 | `payment_reversals` | 결제 취소/환급 | reversal_id, original_transaction_id, reversal_reason, reversal_amount | 3년 |

---

### 5. Lane & Equipment 테이블 (6개)

| # | 테이블명 | 용도 | 주요 컬럼 | 보유 기간 |
|----|---------|------|---------|---------|
| 33 | `toll_lanes` | 요금소 차선 정의 | lane_id, plaza_id, lane_number, lane_type, status | 영구 |
| 34 | `rfid_readers` | RFID 리더 장비 | reader_id, lane_id, reader_model, ip_address, last_maintenance_date | 영구 |
| 35 | `anpr_cameras` | ANPR 카메라 장비 | camera_id, lane_id, camera_model, resolution, last_calibration_date | 영구 |
| 36 | `lane_operating_hours` | Lane 운영 시간 | schedule_id, lane_id, open_time, close_time, effective_date | 영구 |
| 37 | `equipment_maintenance_logs` | 장비 유지보수 기록 | log_id, equipment_id, maintenance_date, issue_type, resolved_by | 2년 |
| 38 | `equipment_health_metrics` | 장비 상태 메트릭 | metric_id, equipment_id, metric_timestamp, uptime_percentage, error_rate | 90일 |

---

### 6. 청구 & 정산 테이블 (7개)

| # | 테이블명 | 용도 | 주요 컬럼 | 보유 기간 |
|----|---------|------|---------|---------|
| 39 | `billing_periods` | 청구 기간 정의 | period_id, start_date, end_date, period_status | 영구 |
| 40 | `billing_invoices` | 청구 송장 | invoice_id, vehicle_id, period_id, total_amount, due_date | 7년 |
| 41 | `billing_line_items` | 송장 상세 | line_item_id, invoice_id, transaction_id, item_amount | 7년 |
| 42 | `toc_settlement_amounts` | TOC (도로 운영사) 정산 | settlement_id, period_id, jvc_net_amount, toc_share, settlement_date | 7년 |
| 43 | `jvc_revenue_summary` | JVC 수익 요약 | summary_id, period_id, gross_revenue, fees, net_revenue | 7년 |
| 44 | `manual_adjustments` | 수동 조정 (할인, 분쟁 해결 등) | adjustment_id, transaction_id, adjustment_reason, adjustment_amount | 3년 |
| 45 | `credit_notes` | 크레딧 노트 (환불) | credit_note_id, original_invoice_id, credit_amount, issued_date | 3년 |

---

### 7. 위반 & 감면 테이블 (5개)

| # | 테이블명 | 용도 | 주요 컬럼 | 보유 기간 |
|----|---------|------|---------|---------|
| 46 | `violations` | 위반 기록 (불법 통행 등) | violation_id, vehicle_id, violation_type, detected_date, jpj_reported | 3년 |
| 47 | `violation_penalties` | 위반 벌금 부과 | penalty_id, violation_id, penalty_amount, penalty_status | 3년 |
| 48 | `exemption_policies` | 감면 정책 마스터 | policy_id, exemption_type, discount_percentage, validity_period | 영구 |
| 49 | `exemption_applications` | 감면 신청 기록 | application_id, vehicle_id, policy_id, application_date, approval_date | 영구 |
| 50 | `exemption_audit_log` | 감면 감시 로그 | log_id, exemption_id, audit_date, auditor_id, finding | 3년 |

---

### 8. 보고 및 집계 테이블 (AGG_* / 8개)

| # | 테이블명 | 용도 | 갱신 주기 | 보유 기간 |
|----|---------|------|---------|---------|
| 51 | `agg_hourly_lane_stats` | Lane별 시간 단위 집계 | 매 시간 | 90일 |
| 52 | `agg_daily_channel_revenue` | Channel별 일일 수익 | 매일 자정 | 3년 |
| 53 | `agg_daily_unpaid_summary` | 미결제 현황 일일 요약 | 매일 02:00 UTC+8 | 1년 |
| 54 | `agg_monthly_vehicle_usage` | 차량 월별 이용 현황 | 매월 1일 | 3년 |
| 55 | `agg_monthly_revenue_summary` | 월간 수익 요약 | 매월 15일 | 영구 |
| 56 | `agg_quarterly_kpi_metrics` | 분기별 KPI | 분기말 | 3년 |
| 57 | `agg_compliance_metrics` | 준수 지표 (PDPA, 감사) | 주간 | 2년 |
| 58 | `agg_equipment_performance` | 장비 성능 집계 | 주간 | 1년 |

---

## 핵심 테이블 스키마

### Table 1: transactions (모든 통행료 거래)

```sql
CREATE TABLE transactions (
  transaction_id BIGSERIAL PRIMARY KEY,
  trip_id VARCHAR(50) UNIQUE NOT NULL,
  vehicle_id UUID NOT NULL,
  lane_id INT NOT NULL,
  toll_amount DECIMAL(10, 2) NOT NULL,
  channel VARCHAR(1) NOT NULL CHECK (channel IN ('A', 'B')), -- A: Clearing, B: TnG
  status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    -- PENDING, PAID, UNPAID_TIER1, UNPAID_TIER2, UNPAID_TIER3, WRITTEN_OFF
  transaction_datetime TIMESTAMP WITH TIME ZONE NOT NULL,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  metadata JSONB, -- 확장 필드: vehicle_type, tag_type, anpr_confidence 등
  
  CONSTRAINT fk_vehicle FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id),
  CONSTRAINT fk_lane FOREIGN KEY (lane_id) REFERENCES toll_lanes(lane_id)
);

CREATE INDEX idx_transactions_vehicle ON transactions(vehicle_id);
CREATE INDEX idx_transactions_lane ON transactions(lane_id);
CREATE INDEX idx_transactions_datetime ON transactions(transaction_datetime);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_channel ON transactions(channel);
```

### Table 2: transactions_channel_a (Channel A 상세)

```sql
CREATE TABLE transactions_channel_a (
  channel_a_id BIGSERIAL PRIMARY KEY,
  transaction_id BIGINT NOT NULL,
  clearing_account_id VARCHAR(20) NOT NULL,
  tag_id VARCHAR(50),
  rfid_reader_id INT,
  anpr_image_path VARCHAR(500),
  anpr_confidence DECIMAL(3, 2), -- 0.00 ~ 1.00
  retry_count INT DEFAULT 0,
  first_retry_timestamp TIMESTAMP WITH TIME ZONE,
  last_retry_timestamp TIMESTAMP WITH TIME ZONE,
  float_days INT, -- Clearing Center 수탁 기간 (3~7일)
  reconciliation_status VARCHAR(20) DEFAULT 'PENDING',
    -- PENDING, FLOAT, SETTLED, DISPUTED
  
  FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
  FOREIGN KEY (clearing_account_id) REFERENCES clearing_center_accounts(cc_account_id),
  FOREIGN KEY (rfid_reader_id) REFERENCES rfid_readers(reader_id)
);

CREATE INDEX idx_channel_a_clearing_account ON transactions_channel_a(clearing_account_id);
CREATE INDEX idx_channel_a_tag_id ON transactions_channel_a(tag_id);
```

### Table 3: transactions_channel_b (Channel B / TnG)

```sql
CREATE TABLE transactions_channel_b (
  channel_b_id BIGSERIAL PRIMARY KEY,
  transaction_id BIGINT NOT NULL,
  tng_reference_id VARCHAR(50),
  tng_card_id VARCHAR(50),
  tng_api_response_code INT,
  tng_balance_before DECIMAL(10, 2),
  tng_balance_after DECIMAL(10, 2),
  tng_fee_amount DECIMAL(10, 2), -- TnG 수수료
  tng_settlement_batch_id BIGINT,
  rnr_window_start TIMESTAMP WITH TIME ZONE, -- Retention & Reconciliation 시작
  rnr_window_end TIMESTAMP WITH TIME ZONE,
  
  FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id) ON DELETE CASCADE,
  FOREIGN KEY (tng_settlement_batch_id) REFERENCES tng_settlement_batches(batch_id)
);

CREATE INDEX idx_channel_b_tng_reference ON transactions_channel_b(tng_reference_id);
CREATE INDEX idx_channel_b_tng_card ON transactions_channel_b(tng_card_id);
```

### Table 4: unpaid_transactions (미결제 거래 정의)

```sql
CREATE TABLE unpaid_transactions (
  unpaid_id BIGSERIAL PRIMARY KEY,
  transaction_id BIGINT NOT NULL UNIQUE,
  vehicle_id UUID NOT NULL,
  toll_amount DECIMAL(10, 2) NOT NULL,
  tier_level INT NOT NULL DEFAULT 1 CHECK (tier_level BETWEEN 1 AND 4),
    -- Tier 1: 즉시, 2: 30일, 3: 법적, 4: 포기
  first_unpaid_date TIMESTAMP WITH TIME ZONE NOT NULL,
  tier_escalation_dates JSONB, -- {"tier1": "2026-04-01", "tier2": "2026-05-01", ...}
  total_collection_cost DECIMAL(10, 2) DEFAULT 0, -- 추심 비용 누적
  writeoff_date TIMESTAMP WITH TIME ZONE,
  writeoff_approval_by VARCHAR(50),
  
  FOREIGN KEY (transaction_id) REFERENCES transactions(transaction_id),
  FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id)
);

CREATE INDEX idx_unpaid_tier ON unpaid_transactions(tier_level);
CREATE INDEX idx_unpaid_date ON unpaid_transactions(first_unpaid_date);
CREATE INDEX idx_unpaid_vehicle ON unpaid_transactions(vehicle_id);
```

### Table 5: agg_daily_channel_revenue (일일 채널별 수익 집계)

```sql
CREATE TABLE agg_daily_channel_revenue (
  agg_id BIGSERIAL PRIMARY KEY,
  revenue_date DATE NOT NULL,
  channel VARCHAR(1) NOT NULL,
  transaction_count INT,
  total_toll_amount DECIMAL(15, 2),
  total_fees_amount DECIMAL(15, 2),
  net_revenue DECIMAL(15, 2),
  paid_percentage DECIMAL(5, 2), -- 결제 성공률 (%)
  unpaid_count INT,
  unpaid_amount DECIMAL(15, 2),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  
  UNIQUE (revenue_date, channel)
);

CREATE INDEX idx_agg_revenue_date ON agg_daily_channel_revenue(revenue_date);
CREATE INDEX idx_agg_revenue_channel ON agg_daily_channel_revenue(channel);
```

### Table 6: clearing_center_accounts (Clearing Center 계정)

```sql
CREATE TABLE clearing_center_accounts (
  cc_account_id VARCHAR(20) PRIMARY KEY,
  account_type VARCHAR(30) NOT NULL, -- 'TOLL_COLLECTION_AGENT', 'FLOAT', 'SETTLEMENT'
  bank_partner VARCHAR(50),
  settlement_cycle VARCHAR(20), -- 'DAILY', 'WEEKLY'
  float_days INT DEFAULT 3, -- 3~7일
  account_balance DECIMAL(15, 2),
  account_status VARCHAR(20) DEFAULT 'ACTIVE',
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  last_settlement_date TIMESTAMP WITH TIME ZONE
);
```

### Table 7: vehicles (차량 마스터)

```sql
CREATE TABLE vehicles (
  vehicle_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  license_plate VARCHAR(10) NOT NULL UNIQUE,
  owner_id UUID NOT NULL,
  vehicle_type VARCHAR(20), -- 'CAR', 'MOTORCYCLE', 'TRUCK', 'BUS'
  tag_id VARCHAR(50),
  is_tagged BOOLEAN DEFAULT FALSE,
  is_blacklisted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (owner_id) REFERENCES vehicle_owners(owner_id),
  FOREIGN KEY (tag_id) REFERENCES vehicle_tags(tag_id)
);

CREATE INDEX idx_vehicles_license_plate ON vehicles(license_plate);
CREATE INDEX idx_vehicles_owner ON vehicles(owner_id);
CREATE INDEX idx_vehicles_tagged ON vehicles(is_tagged);
```

---

## Channel A/B 트랜잭션 구조

### Channel A 흐름 (Clearing Center 기반)

```
┌────────────────────────────────────────────────────────────┐
│ CHANNEL A: RFID/ANPR → Clearing Center → Settlement         │
└────────────────────────────────────────────────────────────┘

[Lane 통과]
    ↓
[RFID Reader 감지] → transactions.tag_id, rfid_reader_id 기록
[ANPR Camera 감지] → transactions_channel_a.anpr_image_path
    ↓
[Trip 생성]
    • transactions (trip_id, vehicle_id, toll_amount, channel='A')
    • transactions_channel_a (clearing_account_id, retry_count=0)
    ↓
[Clearing Center 과금 (배치, 1시간마다)]
    • clearing_center_batches 생성
    • 성공 → transactions.status = 'PAID'
    • 실패 → transactions.status = 'UNPAID_TIER1'
    ↓
[Float 기간 (3~7일)]
    • transactions_channel_a.reconciliation_status = 'FLOAT'
    • 미결제 감지 기간
    ↓
[정산 완료]
    • clearing_center_reconciliation 업데이트
    • transactions_channel_a.reconciliation_status = 'SETTLED'
```

### Channel B 흐름 (TnG 연동)

```
┌────────────────────────────────────────────────────────────┐
│ CHANNEL B: RFID/ANPR → TnG API → Real-time Settlement      │
└────────────────────────────────────────────────────────────┘

[Lane 통과]
    ↓
[TnG Card 인식] → vehicles.tag_id = TNG-*
    ↓
[Trip 생성]
    • transactions (trip_id, vehicle_id, toll_amount, channel='B')
    • transactions_channel_b (tng_reference_id, tng_card_id)
    ↓
[TnG API 호출 (실시간)]
    • POST /api/v2/toll/debit
    • tng_api_calls 로그 기록
    ↓
[응답 처리]
    • Success (200) → transactions.status = 'PAID'
              → transactions_channel_b.tng_balance_after 업데이트
    • Insufficient (402) → transactions.status = 'UNPAID_TIER1'
              → retry_count=0, 첫 재시도 1시간 후
    ↓
[RnR Window (5일)]
    • transactions_channel_b.rnr_window_start/end
    • 추가 결제 시도 3회
    • 실패 시 → Channel A 폴백
    ↓
[일일 정산 (자정)]
    • tng_settlement_batches 생성
    • tng_reconciliation_details 상세 기록
    ↓
[주간 조정 (월요일 06:00)]
    • 거래액 오차율 검증 (<0.01%)
    ↓
[월간 지급 (15일)]
    • JVC 계정 입금
```

---

## 집계 테이블 (AGG_* 정의)

### 1. agg_hourly_lane_stats (Lane별 시간 단위)

```sql
CREATE TABLE agg_hourly_lane_stats (
  agg_id BIGSERIAL PRIMARY KEY,
  lane_id INT NOT NULL,
  hour_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
  transaction_count INT,
  total_amount DECIMAL(15, 2),
  channel_a_count INT,
  channel_b_count INT,
  failure_count INT,
  failure_percentage DECIMAL(5, 2),
  avg_processing_time_ms INT, -- 평균 처리 시간
  
  UNIQUE (lane_id, hour_timestamp),
  FOREIGN KEY (lane_id) REFERENCES toll_lanes(lane_id)
);
```

### 2. agg_daily_unpaid_summary (미결제 현황 일일)

```sql
CREATE TABLE agg_daily_unpaid_summary (
  agg_id BIGSERIAL PRIMARY KEY,
  summary_date DATE NOT NULL UNIQUE,
  tier1_count INT, tier1_amount DECIMAL(15, 2),
  tier2_count INT, tier2_amount DECIMAL(15, 2),
  tier3_count INT, tier3_amount DECIMAL(15, 2),
  tier4_count INT, tier4_amount DECIMAL(15, 2), -- 포기
  total_unpaid_amount DECIMAL(15, 2),
  collection_rate DECIMAL(5, 2), -- 회수율 (%)
  avg_days_to_resolution INT, -- Tier 2→3 평균 일수
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 3. agg_monthly_revenue_summary (월간 수익 요약)

```sql
CREATE TABLE agg_monthly_revenue_summary (
  agg_id BIGSERIAL PRIMARY KEY,
  year_month DATE NOT NULL UNIQUE, -- 월의 첫 날
  gross_revenue DECIMAL(15, 2),
  channel_a_revenue DECIMAL(15, 2),
  channel_b_revenue DECIMAL(15, 2),
  total_fees DECIMAL(15, 2),
  clearing_fees DECIMAL(15, 2),
  tng_fees DECIMAL(15, 2),
  net_revenue DECIMAL(15, 2),
  toc_share DECIMAL(15, 2), -- TOC 분배액
  jvc_net DECIMAL(15, 2), -- JVC 최종 수익
  paid_percentage DECIMAL(5, 2),
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

### 4. agg_quarterly_kpi_metrics (분기별 KPI)

```sql
CREATE TABLE agg_quarterly_kpi_metrics (
  kpi_id BIGSERIAL PRIMARY KEY,
  quarter VARCHAR(10) NOT NULL UNIQUE, -- '2026-Q1', '2026-Q2'
  total_transactions BIGINT,
  transaction_per_second DECIMAL(10, 2), -- 평균 TPS
  payment_success_rate DECIMAL(5, 2),
  unpaid_recovery_rate DECIMAL(5, 2),
  equipment_uptime_percentage DECIMAL(5, 2),
  customer_satisfaction_score DECIMAL(3, 1),
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);
```

---

## 테이블 관계도 (ERD)

### 핵심 엔티티 관계

```
┌─────────────────────────────────────────────────────────────┐
│                    MASTER TABLES                            │
│ (vehicles, vehicle_owners, toll_lanes, equipment)          │
└──────────────┬──────────────────────────────────────────────┘
               │
               ├─→ transactions (트랜잭션 원본)
               │       ├─→ transactions_channel_a (Clearing)
               │       ├─→ transactions_channel_b (TnG)
               │       ├─→ payment_logs (결제 로그)
               │       └─→ transaction_failures (실패)
               │
               ├─→ unpaid_transactions (미결제)
               │       ├─→ unpaid_tier1 (즉시)
               │       ├─→ unpaid_tier2 (30일)
               │       ├─→ unpaid_tier3 (법적)
               │       └─→ unpaid_tier4 (포기)
               │
               ├─→ billing_invoices (청구)
               │       └─→ billing_line_items (상세)
               │
               └─→ AGG_* (집계 테이블)
                   ├─→ agg_hourly_lane_stats
                   ├─→ agg_daily_channel_revenue
                   ├─→ agg_daily_unpaid_summary
                   ├─→ agg_monthly_revenue_summary
                   └─→ agg_quarterly_kpi_metrics
```

### 외래키 관계 맵

| 테이블 | FK | 참조 테이블 | 용도 |
|--------|----|-----------|----|
| `transactions` | vehicle_id | `vehicles` | 차량 조회 |
| `transactions` | lane_id | `toll_lanes` | 차선 조회 |
| `transactions_channel_a` | transaction_id | `transactions` | 트랜잭션 참조 |
| `transactions_channel_a` | clearing_account_id | `clearing_center_accounts` | 계정 참조 |
| `transactions_channel_b` | transaction_id | `transactions` | 트랜잭션 참조 |
| `vehicles` | owner_id | `vehicle_owners` | 소유자 조회 |
| `unpaid_transactions` | transaction_id | `transactions` | 미결제 원본 |
| `billing_invoices` | vehicle_id | `vehicles` | 차량 청구 |
| `violations` | vehicle_id | `vehicles` | 차량 위반 |

---

## 인덱싱 전략

### 1차 인덱스 (조회 성능)

```sql
-- transactions 테이블: 가장 높은 접근 빈도
CREATE INDEX idx_trx_vehicle_datetime ON transactions(vehicle_id, transaction_datetime DESC);
CREATE INDEX idx_trx_lane_datetime ON transactions(lane_id, transaction_datetime DESC);
CREATE INDEX idx_trx_status ON transactions(status) WHERE status IN ('UNPAID_TIER1', 'UNPAID_TIER2');
CREATE INDEX idx_trx_channel_status ON transactions(channel, status);

-- unpaid_transactions: Tier 관리
CREATE INDEX idx_unpaid_tier_date ON unpaid_transactions(tier_level, first_unpaid_date);
CREATE INDEX idx_unpaid_vehicle_tier ON unpaid_transactions(vehicle_id, tier_level);

-- Lane 실시간 통계
CREATE INDEX idx_lane_realtime_lane ON lane_realtime_stats(lane_id) WHERE transaction_count > 0;
```

### 2차 인덱스 (집계/보고)

```sql
-- 청구 조회
CREATE INDEX idx_billing_vehicle_period ON billing_invoices(vehicle_id, period_id);
CREATE INDEX idx_billing_date ON billing_invoices(created_at DESC);

-- 집계 테이블
CREATE INDEX idx_agg_revenue_date ON agg_daily_channel_revenue(revenue_date DESC);
CREATE INDEX idx_agg_unpaid_date ON agg_daily_unpaid_summary(summary_date DESC);
```

### 3차 인덱스 (RBAC/감사)

```sql
-- 감시 로그
CREATE INDEX idx_audit_entity ON transaction_audit_trail(transaction_id, changed_by);
CREATE INDEX idx_audit_date ON transaction_audit_trail(change_timestamp DESC);
```

---

## 데이터 파티셔닝

### 1. 시간 기반 파티셔닝 (transactions)

```sql
-- 월 단위 파티셔닝 (3년 보유 = 36개 파티션)
CREATE TABLE transactions (
  -- ... 컬럼 생략 ...
) PARTITION BY RANGE (DATE_TRUNC('month', transaction_datetime));

-- 2026년 4월 파티션
CREATE TABLE transactions_202604
  PARTITION OF transactions
  FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

-- 2026년 5월 파티션
CREATE TABLE transactions_202605
  PARTITION OF transactions
  FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- ... 추가 파티션 생성
```

### 2. Lane별 파티셔닝 (lane_realtime_stats)

```sql
-- 30일만 보유하므로, Lane별 sub-partition
-- 대형 도로(수십~수백 Lane)일 경우 조회 성능 향상
CREATE TABLE lane_realtime_stats (
  -- ... 컬럼 생략 ...
) PARTITION BY LIST (lane_id);

CREATE TABLE lane_realtime_stats_lane_001
  PARTITION OF lane_realtime_stats
  FOR VALUES IN (1, 2, 3, 4, 5); -- 첫 5개 Lane
```

### 3. 파티션 자동 갱신 (Archiving)

```sql
-- 매월 1일에 오래된 파티션 Detach & Archive
CREATE OR REPLACE FUNCTION archive_old_transactions()
RETURNS void AS $$
BEGIN
  -- 3년 이상 된 파티션 분리
  ALTER TABLE transactions DETACH PARTITION transactions_202301;
  -- S3 또는 Glacier로 이동
END;
$$ LANGUAGE plpgsql;

-- 자동 스케줄 (Cron)
-- 0 1 1 * * SELECT archive_old_transactions();
```

---

## 참조 문서

이 Data Model 문서는 다음 문서들과 긴밀히 연계된다:

| 문서 | 관련 섹션 | 링크 |
|------|---------|------|
| **01_data_architecture.md** | 5단계 계층 구조, 메타데이터 관리 | 상위 설계 문서 |
| **03_rbac_design.md** | 30개 역할 기반 데이터 접근 제어 | 테이블 행 수준 보안 (RLS) |
| **04_metadata_glossary.md** | KO/EN/BM 용어 사전, 데이터 정의서 | 테이블/컬럼 메타데이터 |
| **05_security_compliance.md** | PDPA 준수, ANPR 이미지 보존 정책 | 데이터 보유/삭제 규칙 |
| **02_system/02_service_domains.md** | Transaction, Billing, Unpaid Domain | 도메인별 테이블 매핑 |
| **02_system/03_tech_stack.md** | PostgreSQL 12+, 성능 목표 (10,000 TPS) | 기술 스택 명세 |
| **05_payment_architecture.md** | Channel A/B 결제 흐름, 미결제 Tier | 트랜잭션 흐름도 |

---

## 버전 관리

| 버전 | 날짜 | 주요 변경 사항 | 작성자 |
|------|------|--------------|--------|
| v0.1 | 2026-04-01 | 초안 작성 (테이블 목록 50+, 핵심 스키마 7개, Channel A/B 구조) | DB Lead |
| — | — | — | — |

---

**문서 상태:** Draft  
**다음 검토:** Data Architecture Team & DB Lead  
**예상 확정:** 2026-04-15  
**관련 Skill:** [data-architecture-standards](../07_skills/data-architecture-standards/SKILL.md), [aggregation-units](../07_skills/aggregation-units/SKILL.md)
