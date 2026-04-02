---
name: aggregation-units
description: Hourly/daily/monthly aggregation DDL, partitioning strategy, and ClickHouse table design
use_when:
  - 집계 테이블 DDL 또는 파티션 설계가 필요할 때
  - 시간별·일별·월별 집계 배치 로직을 구현할 때
  - ClickHouse OLAP 쿼리 최적화 시
dont_use_when:
  - 전체 데이터 파이프라인 구조가 필요할 때 (data-architecture-standards 사용)
  - 데이터 용어 정의가 필요할 때 (metadata-management 사용)
---

# 집계 단위 설계

## 1. 개요

BOS의 집계 테이블은 **3가지 주기(시간별/일별/월별)**로 분류되며, PostgreSQL (OLTP용)과 ClickHouse (OLAP용)에 이중 저장된다.

---

## 2. 핵심 내용

### 2.1 집계 테이블 목록

| 테이블명 | 집계 주기 | 스토리지 | 보관 |
|---------|---------|---------|------|
| `agg_hourly_txn` | 시간별 | ClickHouse | 90일 |
| `agg_daily_summary` | 일별 | PostgreSQL + ClickHouse | 7년 |
| `agg_monthly_summary` | 월별 | ClickHouse | 무기한 |
| `agg_plaza_traffic` | 일별 (요금소별) | ClickHouse | 3년 |
| `agg_vehicle_class` | 일별 (차량 등급별) | ClickHouse | 3년 |

### 2.2 PostgreSQL 일별 집계 DDL

```sql
CREATE TABLE agg_daily_summary (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    concessionaire_id UUID NOT NULL,
    business_date    DATE NOT NULL,
    vehicle_class    SMALLINT NOT NULL,        -- 1~5
    channel          CHAR(3) NOT NULL,          -- 'A', 'B', 'GOV'
    txn_count        INTEGER NOT NULL DEFAULT 0,
    gross_amount     NUMERIC(15,2) NOT NULL DEFAULT 0,
    jvc_fee_rate     NUMERIC(5,4) NOT NULL,
    jvc_fee_amount   NUMERIC(15,2) NOT NULL DEFAULT 0,
    net_amount       NUMERIC(15,2) NOT NULL DEFAULT 0,
    unpaid_count     INTEGER NOT NULL DEFAULT 0,
    unpaid_amount    NUMERIC(15,2) NOT NULL DEFAULT 0,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (concessionaire_id, business_date, vehicle_class, channel)
) PARTITION BY RANGE (business_date);

-- 월별 파티션 생성 (매월 자동 생성 필요)
CREATE TABLE agg_daily_summary_2026_04
    PARTITION OF agg_daily_summary
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');
```

### 2.3 ClickHouse 월별 집계 DDL

```sql
CREATE TABLE agg_monthly_summary (
    year_month        String,        -- 'YYYY-MM'
    concessionaire_id UUID,
    channel           String,
    vehicle_class     UInt8,
    txn_count         UInt64,
    gross_amount      Decimal(15,2),
    net_amount        Decimal(15,2),
    unpaid_rate       Float32
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(toDate(year_month || '-01'))
ORDER BY (concessionaire_id, year_month, channel, vehicle_class)
TTL toDate(year_month || '-01') + INTERVAL 10 YEAR;
```

### 2.4 집계 배치 실행 시간

| 집계 유형 | 배치 실행 시각 | 데이터 기준 | SLA |
|---------|------------|---------|-----|
| 시간별 | 매 시간 :05 | 전 시간 전체 | 10분 내 |
| 일별 | 01:00 | 전일 전체 | 30분 내 |
| 요금소별 | 01:30 | 전일 전체 | 20분 내 |
| 월별 | 매월 2일 02:00 | 전월 전체 | 60분 내 |

---

## 3. 주의사항

- **ClickHouse Decimal 타입**: `Decimal(15,2)` 사용. `Float64` 사용 시 부동소수점 오차 발생
- **파티션 자동 생성**: CronJob으로 매월 1일 익월 파티션 자동 생성 스크립트 실행
- **집계 재실행**: 집계 배치 재실행 시 `INSERT OR REPLACE` 또는 `UPSERT ON CONFLICT` 필수

---

## 4. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 데이터 아키텍처 표준 | [`../data-architecture-standards/SKILL.md`](../data-architecture-standards/SKILL.md) |
| 데이터 모델 | [`../../docs/03_data/02_data_model.md`](../../docs/03_data/02_data_model.md) |
| Phase 8 Big Data | [`../../docs/06_phases/08_phase08_bigdata.md`](../../docs/06_phases/08_phase08_bigdata.md) |
