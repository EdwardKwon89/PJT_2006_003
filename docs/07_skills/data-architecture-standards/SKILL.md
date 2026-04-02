---
name: data-architecture-standards
description: 5-tier aggregation pipeline, Bronze/Silver/Gold Delta Lake layers, Airflow DAG patterns
use_when:
  - 데이터 파이프라인 설계 또는 구현 시
  - Bronze/Silver/Gold 레이어 구조를 참조해야 할 때
  - Delta Lake 읽기·쓰기 패턴이 필요할 때
  - Phase 8 Big Data 파이프라인 개발 시
dont_use_when:
  - 집계 테이블 DDL 세부사항이 필요할 때 (aggregation-units 사용)
  - 메타데이터 용어 관리 시 (metadata-management 사용)
---

# 데이터 아키텍처 표준

## 1. 개요

BOS 데이터 플랫폼은 **5단계 집계 구조**와 **Bronze/Silver/Gold Medallion Architecture**를 기반으로 한다. 원시 이벤트부터 경영진 KPI까지의 데이터 흐름을 정의한다.

---

## 2. 핵심 내용

### 2.1 5단계 집계 구조

```
Level 0: Raw Event (원시 이벤트)
   └─ Kafka: raw.rfid.events, raw.anpr.events
   └─ 보관: 7일

Level 1: Processed Transaction (처리된 트랜잭션)
   └─ PostgreSQL: trip_records, payment_attempts
   └─ 보관: 7년 (금융 규정)

Level 2: Daily Aggregation (일별 집계)
   └─ PostgreSQL: daily_settlement_summary
   └─ Delta Lake: bronze_daily_txn

Level 3: Monthly Aggregation (월별 집계)
   └─ Delta Lake: silver_monthly_summary
   └─ ClickHouse: agg_monthly_summary

Level 4: KPI / Dashboard (경영진 지표)
   └─ ClickHouse: gold_kpi_*, gold_dashboard_*
   └─ 갱신 주기: 15분 (실시간 유사)
```

### 2.2 Medallion Architecture

| 레이어 | 설명 | 기술 스택 | 보관 기간 |
|-------|------|---------|---------|
| Bronze | 원시 데이터 (정제 전) | Delta Lake on S3 | 1년 |
| Silver | 정제·보강 데이터 | Delta Lake on S3 | 3년 |
| Gold | 집계·분석 최적화 | ClickHouse | 무기한 (요약만) |

### 2.3 Delta Lake 읽기·쓰기 패턴 (Spark)

```python
from delta.tables import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Bronze 레이어 쓰기 (Append)
df.write \
  .format("delta") \
  .mode("append") \
  .option("mergeSchema", "true") \
  .partitionBy("year", "month", "day") \
  .save("s3://bos-datalake/bronze/daily_txn/")

# Silver 레이어 MERGE (UPSERT)
delta_table = DeltaTable.forPath(spark, "s3://bos-datalake/silver/monthly_summary/")
delta_table.alias("t").merge(
    source=new_data.alias("s"),
    condition="t.concessionaire_id = s.concessionaire_id AND t.year_month = s.year_month"
).whenMatchedUpdateAll() \
 .whenNotMatchedInsertAll() \
 .execute()
```

### 2.4 파티셔닝 전략

```python
# 모든 데이터 테이블 파티션 기준
partitionBy = ["year", "month", "day"]  # Bronze, Silver
# 예: s3://bos-datalake/bronze/daily_txn/year=2026/month=04/day=03/

# Gold 레이어: concessionaire_id 추가 파티션
partitionBy = ["year", "month", "concessionaire_id"]
```

### 2.5 Airflow DAG 패턴

```python
# 표준 ETL DAG 구조 (Bronze → Silver)
bronze_to_silver = DAG(
    dag_id="bronze_to_silver_daily",
    schedule_interval="0 4 * * *",  # 매일 04:00
    default_args={"retries": 2, "retry_delay": timedelta(minutes=10)},
)

# 태스크 구성
extract_bronze >> validate_schema >> transform_silver >> load_silver >> notify_success
```

---

## 3. 주의사항 & 함정

- **Delta Lake VACUUM**: 기본 7일 이상 과거 버전 삭제. `VACUUM bronze_daily_txn RETAIN 30 HOURS` 주의
- **ClickHouse와 Delta Lake 동기**: Gold 레이어 ClickHouse는 Silver에서 15분 주기로 동기화 (Spark Structured Streaming)
- **파티션 pruning**: 쿼리 시 반드시 `year`, `month` 필터 포함 (전체 스캔 방지)

---

## 4. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 집계 단위 설계 | [`../aggregation-units/SKILL.md`](../aggregation-units/SKILL.md) |
| 빅데이터 프레임워크 | [`../bigdata-service-framework/SKILL.md`](../bigdata-service-framework/SKILL.md) |
| 데이터 아키텍처 | [`../../docs/03_data/01_data_architecture.md`](../../docs/03_data/01_data_architecture.md) |
| Phase 8 Big Data | [`../../docs/06_phases/08_phase08_bigdata.md`](../../docs/06_phases/08_phase08_bigdata.md) |
