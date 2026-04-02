# Phase 8: 빅데이터 & 분석 플랫폼

## 06_phases/08_phase08_bigdata.md
## v1.0 | 2026-04 | 참조: 02_system/01_system_overview.md, 03_data/01_data_architecture.md

> **담당 Agent:** reporting-lead, reporting-dev, CIO  
> **선행 Phase:** Phase 3 (트랜잭션), Phase 4 (정산), Phase 5 (이미징), Phase 6 (이의신청), Phase 7 (알림)  
> **후행 Phase:** Phase 9 (AI 고도화)  
> **기간:** 3주 (Week 13~15)

---

## 1. Phase 개요

### 1.1 목적

Phase 8은 Malaysia SLFF/MLFF Tolling BOS의 **빅데이터 분석 플랫폼**을 구축하는 단계다. Delta Lake 기반의 3계층(Bronze/Silver/Gold) 데이터 레이크를 구성하고, Apache Spark 분산 처리 잡을 통해 일별·월별 집계를 수행한다. Airflow DAG로 파이프라인을 자동화하며, TOC 운영 대시보드와 교통 패턴 분석 기능을 제공한다.

### 1.2 비즈니스 맥락

| 항목 | 내용 |
|------|------|
| 분석 대상 | SLFF/MLFF 구간별 통행료 트랜잭션, ANPR 이미지 처리 결과, Channel A/B 결제 이력 |
| 일일 데이터 규모 | 약 2.4M 건 트랜잭션 (Peak 10,000 TPS × 24h) |
| 집계 주기 | 실시간(Kafka), 시간별, 일별, 월별, 분기별 |
| 주요 수혜자 | 플라자 관리자, TOC 운영팀, 재무팀, CEO/CIO 경영진 |
| 규정 준수 | PDPA 2010 준수, ANPR 이미지 30일 자동 삭제 |

### 1.3 아키텍처 전체 흐름

```
Kafka Streams (실시간)
        │
        ▼
[Bronze Layer] ─ Raw 원시 데이터 적재 (S3 Parquet)
        │
        ▼
[Silver Layer] ─ 정제·정규화·중복 제거 (Delta Lake)
        │
        ▼
[Gold Layer]   ─ 집계·KPI·비즈니스 뷰 (Delta Lake)
        │
        ▼
[Reporting Service] ─ REST API / Dashboard / MCP
```

### 1.4 주요 기술 스택

| 컴포넌트 | 기술 | 버전 |
|----------|------|------|
| 분산 처리 | Apache Spark | 3.5.x |
| 데이터 레이크 | Delta Lake | 3.x |
| 오케스트레이션 | Apache Airflow | 2.8.x |
| 스토리지 | AWS S3 + Glue Data Catalog | - |
| 쿼리 엔진 | AWS Athena | - |
| 시각화 | Grafana + Custom Dashboard | 10.x |
| 언어 | Python (PySpark), SQL | 3.11 |

---

## 2. 담당 Agent & 태스크 체크리스트

### 2.1 reporting-lead (분석 플랫폼 리드)

```yaml
Agent: reporting-lead
Role: 빅데이터 플랫폼 설계 및 총괄 구현
Sprint: Week 13~15
```

#### 태스크 체크리스트

- [ ] **BIGDATA-001** Delta Lake 클러스터 프로비저닝 (AWS EMR on EKS)
  - EMR 클러스터 설정 (m5.xlarge × 3 노드)
  - Spark 3.5 + Delta Lake 3.x 설치 및 구성
  - S3 버킷 구조 생성 (`bos-datalake-bronze/silver/gold/`)
  - AWS Glue Data Catalog 연동

- [ ] **BIGDATA-002** Bronze Layer 구현
  - Kafka → S3 Parquet 스트리밍 적재 (Spark Structured Streaming)
  - 파티셔닝 전략: `year=/month=/day=/hour=`
  - 스키마 레지스트리 연동 (Confluent Schema Registry)
  - 데이터 체크섬 및 무결성 검증

- [ ] **BIGDATA-003** Silver Layer 구현
  - Bronze 데이터 정제 및 정규화 Spark Job
  - 중복 트랜잭션 제거 (idempotency_key 기반)
  - NULL 처리 및 타입 캐스팅
  - Delta Lake ACID 트랜잭션 적용
  - 증분 업데이트 (MERGE INTO 패턴)

- [ ] **BIGDATA-004** Gold Layer 구현
  - 일별 플라자별 수익 집계 테이블
  - 차량 클래스별 통행 빈도 집계
  - Channel A/B 결제 비율 집계
  - 요금 미납 비율 및 이의신청 패턴 집계
  - 월별 재무 보고 뷰 생성

- [ ] **BIGDATA-005** Airflow DAG 파이프라인 구성
  - Bronze → Silver ETL DAG (시간별 트리거)
  - Silver → Gold 집계 DAG (일별 트리거: 01:00 MYT)
  - 월별 재무 보고 DAG (매월 1일 02:00 MYT)
  - DAG 실패 알림 (Slack + SNS)

- [ ] **BIGDATA-006** 요금 시뮬레이션 모델
  - 신규 요금제 적용 시 수익 변화 예측
  - 차량 클래스별 시뮬레이션 파라미터 설정
  - 시뮬레이션 결과 Gold Layer 저장
  - 경영진용 시뮬레이션 리포트 생성

### 2.2 reporting-dev (분석 개발 담당)

```yaml
Agent: reporting-dev
Role: reporting-service API 구현 및 대시보드 개발
Sprint: Week 13~15
```

#### 태스크 체크리스트

- [ ] **BIGDATA-007** reporting-service 마이크로서비스 구현
  - Spring Boot 3.x 기반 REST API
  - Gold Layer 데이터 조회 API 12개 엔드포인트
  - Athena 쿼리 실행 및 결과 캐싱 (Redis, TTL 5분)
  - 보고서 스케줄링 API (PDF/Excel 생성)

- [ ] **BIGDATA-008** TOC 운영 분석 대시보드
  - 실시간 KPI 패널 (총 수익, TPS, 오류율)
  - 플라자별 수익 비교 차트
  - 시간대별 교통량 히트맵
  - 알림 현황 패널 (미납, 이의신청, 장비 오류)
  - Grafana 대시보드 JSON 템플릿 작성

- [ ] **BIGDATA-009** 교통 패턴 분석
  - 일별·주별·월별 교통량 트렌드
  - 구간별 혼잡도 분석
  - 차량 클래스 분포 시각화
  - 계절성 패턴 탐지 (공휴일, 라마단 등)

- [ ] **BIGDATA-010** 재무 보고 자동화
  - 월별 수익 보고서 PDF 자동 생성 (JasperReports)
  - PLUS Concession 제출용 Excel 포맷
  - 이메일 자동 발송 (SES)
  - 보고서 이력 관리 (S3 아카이브)

### 2.3 CIO (의사결정 및 승인)

- [ ] **BIGDATA-011** 분석 플랫폼 인프라 예산 승인 (EMR, S3, Athena)
- [ ] **BIGDATA-012** 데이터 보존 정책 최종 승인 (PDPA 준수)
- [ ] **BIGDATA-013** 대시보드 요구사항 검토 및 승인
- [ ] **BIGDATA-014** Gold Layer KPI 정의 최종 확정

---

## 3. Bronze → Silver → Gold 변환 Spark 코드 패턴

### 3.1 Bronze Layer: Kafka → S3 스트리밍 적재

```python
# bronze_streaming_job.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, from_json, current_timestamp, sha2, concat_ws
from pyspark.sql.types import StructType, StructField, StringType, LongType, DoubleType, TimestampType

KAFKA_BOOTSTRAP = "kafka.bos-internal:9092"
BRONZE_PATH = "s3://bos-datalake-bronze/transactions/"
CHECKPOINT_PATH = "s3://bos-datalake-checkpoints/bronze-transactions/"

TRANSACTION_SCHEMA = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("plaza_code", StringType(), False),
    StructField("lane_id", StringType(), False),
    StructField("vehicle_class", StringType(), False),
    StructField("channel", StringType(), False),          # A or B
    StructField("toll_amount", DoubleType(), False),
    StructField("payment_status", StringType(), False),
    StructField("obu_id", StringType(), True),
    StructField("plate_number", StringType(), True),
    StructField("timestamp", LongType(), False),
])

def create_bronze_stream(spark: SparkSession):
    """Kafka에서 트랜잭션 읽어 Bronze Layer에 적재."""
    raw_stream = (
        spark.readStream
        .format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", "bos.transactions.raw")
        .option("startingOffsets", "latest")
        .option("failOnDataLoss", "false")
        .load()
    )

    parsed = (
        raw_stream
        .select(
            from_json(col("value").cast("string"), TRANSACTION_SCHEMA).alias("data"),
            col("timestamp").alias("kafka_timestamp"),
        )
        .select("data.*", "kafka_timestamp")
        .withColumn("ingested_at", current_timestamp())
        .withColumn("checksum", sha2(concat_ws("|", col("transaction_id"), col("toll_amount")), 256))
    )

    query = (
        parsed.writeStream
        .format("delta")
        .outputMode("append")
        .option("checkpointLocation", CHECKPOINT_PATH)
        .option("path", BRONZE_PATH)
        .partitionBy("plaza_code")
        .trigger(processingTime="60 seconds")
        .start()
    )

    return query


if __name__ == "__main__":
    spark = (
        SparkSession.builder
        .appName("BOS-Bronze-Streaming")
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog")
        .getOrCreate()
    )
    query = create_bronze_stream(spark)
    query.awaitTermination()
```

### 3.2 Silver Layer: 정제 및 중복 제거 배치 잡

```python
# silver_etl_job.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_timestamp, upper, trim, when
from delta.tables import DeltaTable

BRONZE_PATH = "s3://bos-datalake-bronze/transactions/"
SILVER_PATH = "s3://bos-datalake-silver/transactions/"


def run_bronze_to_silver(spark: SparkSession, processing_date: str):
    """Bronze에서 Silver로 정제·중복 제거 배치 처리."""

    # 1. Bronze 증분 데이터 로드 (처리 대상 날짜)
    bronze_df = (
        spark.read.format("delta")
        .load(BRONZE_PATH)
        .filter(col("ingested_at").cast("date") == processing_date)
    )

    # 2. 데이터 정제
    cleaned_df = (
        bronze_df
        .withColumn("plate_number", upper(trim(col("plate_number"))))
        .withColumn("vehicle_class", trim(col("vehicle_class")))
        .withColumn("channel", upper(col("channel")))
        .withColumn("transaction_ts", to_timestamp(col("timestamp") / 1000))
        .withColumn(
            "payment_status_std",
            when(col("payment_status").isin("SUCCESS", "PAID", "COMPLETED"), "PAID")
            .when(col("payment_status").isin("FAILED", "DECLINED", "ERROR"), "FAILED")
            .when(col("payment_status").isin("PENDING", "PROCESSING"), "PENDING")
            .otherwise("UNKNOWN")
        )
        .filter(col("transaction_id").isNotNull())
        .filter(col("toll_amount") >= 0)
        .filter(col("plaza_code").isNotNull())
        .drop("kafka_timestamp", "ingested_at", "checksum")
    )

    # 3. Delta Lake MERGE (중복 제거 + 업서트)
    if DeltaTable.isDeltaTable(spark, SILVER_PATH):
        silver_table = DeltaTable.forPath(spark, SILVER_PATH)
        (
            silver_table.alias("existing")
            .merge(
                cleaned_df.alias("incoming"),
                "existing.transaction_id = incoming.transaction_id"
            )
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
    else:
        cleaned_df.write.format("delta").mode("overwrite").save(SILVER_PATH)

    print(f"[Silver ETL] {processing_date} 완료: {cleaned_df.count()}건 처리")
```

### 3.3 Gold Layer: 일별 집계 배치 잡

```python
# gold_aggregation_job.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, sum as spark_sum, count, avg, date_trunc,
    countDistinct, when, round as spark_round
)

SILVER_PATH = "s3://bos-datalake-silver/transactions/"
GOLD_REVENUE_PATH = "s3://bos-datalake-gold/daily_revenue/"
GOLD_TRAFFIC_PATH = "s3://bos-datalake-gold/daily_traffic/"


def run_silver_to_gold(spark: SparkSession, aggregation_date: str):
    """Silver에서 Gold로 일별 집계 수행."""

    silver_df = (
        spark.read.format("delta")
        .load(SILVER_PATH)
        .filter(col("transaction_ts").cast("date") == aggregation_date)
    )

    # 1. 플라자별 일별 수익 집계
    daily_revenue = (
        silver_df
        .groupBy("plaza_code", "vehicle_class", "channel")
        .agg(
            count("transaction_id").alias("txn_count"),
            spark_sum("toll_amount").alias("total_revenue"),
            avg("toll_amount").alias("avg_toll"),
            countDistinct(
                when(col("payment_status_std") == "PAID", col("transaction_id"))
            ).alias("paid_count"),
            countDistinct(
                when(col("payment_status_std") == "FAILED", col("transaction_id"))
            ).alias("failed_count"),
        )
        .withColumn("success_rate",
            spark_round(col("paid_count") / col("txn_count") * 100, 2))
        .withColumn("aggregation_date", col("aggregation_date").cast("date").alias("aggregation_date"))
    )

    # 2. 시간대별 교통량 집계 (히트맵용)
    hourly_traffic = (
        silver_df
        .withColumn("hour", date_trunc("hour", col("transaction_ts")))
        .groupBy("plaza_code", "hour")
        .agg(
            count("transaction_id").alias("vehicle_count"),
            spark_sum("toll_amount").alias("hourly_revenue"),
        )
    )

    # 3. Gold Layer 저장 (파티셔닝: plaza_code + aggregation_date)
    (
        daily_revenue
        .write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"aggregation_date = '{aggregation_date}'")
        .partitionBy("plaza_code")
        .save(GOLD_REVENUE_PATH)
    )

    (
        hourly_traffic
        .write.format("delta")
        .mode("overwrite")
        .option("replaceWhere", f"date(hour) = '{aggregation_date}'")
        .partitionBy("plaza_code")
        .save(GOLD_TRAFFIC_PATH)
    )

    print(f"[Gold Aggregation] {aggregation_date} 완료")
```

### 3.4 요금 시뮬레이션 모델

```python
# toll_simulation_job.py
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, when
from dataclasses import dataclass
from typing import Dict

@dataclass
class TollScenario:
    """요금 시뮬레이션 시나리오 정의."""
    scenario_id: str
    description: str
    multipliers: Dict[str, float]  # vehicle_class → multiplier

SCENARIOS = [
    TollScenario("S001", "10% 인상 (전체)", {"Class1": 1.10, "Class2": 1.10, "Class3": 1.10}),
    TollScenario("S002", "대형 차량 15% 인상", {"Class1": 1.00, "Class2": 1.05, "Class3": 1.15}),
    TollScenario("S003", "심야 할인 20% 적용", {"Class1": 0.80, "Class2": 0.80, "Class3": 0.80}),
]

def run_simulation(spark: SparkSession, base_date: str):
    """역사 데이터 기반 요금 시나리오 시뮬레이션."""
    gold_df = spark.read.format("delta").load("s3://bos-datalake-gold/daily_revenue/")
    base_df = gold_df.filter(col("aggregation_date") >= "2025-01-01")

    results = []
    for scenario in SCENARIOS:
        sim_df = base_df
        for vehicle_class, multiplier in scenario.multipliers.items():
            sim_df = sim_df.withColumn(
                "simulated_revenue",
                when(col("vehicle_class") == vehicle_class,
                     col("total_revenue") * lit(multiplier))
                .otherwise(col("total_revenue"))
            )
        sim_df = sim_df.withColumn("scenario_id", lit(scenario.scenario_id))
        results.append(sim_df)

    simulation_result = results[0]
    for df in results[1:]:
        simulation_result = simulation_result.union(df)

    (
        simulation_result
        .write.format("delta")
        .mode("overwrite")
        .save("s3://bos-datalake-gold/simulation_results/")
    )
    print(f"[Simulation] {len(SCENARIOS)}개 시나리오 완료")
```

---

## 4. Airflow DAG 예시

### 4.1 Bronze → Silver ETL DAG (시간별)

```yaml
# dags/bos_bronze_to_silver.yaml
# Airflow DAG Definition (YAML 형식 표현, 실제는 Python DAG 파일)

dag_id: bos_bronze_to_silver_etl
description: "BOS Bronze to Silver ETL - 시간별 정제 파이프라인"
schedule_interval: "0 * * * *"   # 매 시 정각 실행
start_date: "2026-01-01"
catchup: false
max_active_runs: 1
tags:
  - bos
  - etl
  - silver

default_args:
  owner: reporting-lead
  retries: 3
  retry_delay_minutes: 5
  email_on_failure: true
  email:
    - bos-ops@jvc.my

tasks:
  - task_id: check_bronze_data
    operator: PythonOperator
    python_callable: check_bronze_availability
    doc: "Bronze Layer 신규 데이터 가용성 확인"

  - task_id: run_silver_etl
    operator: SparkSubmitOperator
    application: s3://bos-spark-jobs/silver_etl_job.py
    conf:
      spark.executor.instances: "3"
      spark.executor.memory: "4g"
      spark.driver.memory: "2g"
    depends_on:
      - check_bronze_data

  - task_id: validate_silver_data
    operator: PythonOperator
    python_callable: validate_silver_quality
    doc: "Silver 데이터 품질 검증 (NULL 비율, 중복 건수)"
    depends_on:
      - run_silver_etl

  - task_id: notify_success
    operator: SlackWebhookOperator
    http_conn_id: slack_bos_alerts
    message: "✅ Silver ETL 완료: {{ ds_nodash }} {{ execution_date.hour }}시"
    depends_on:
      - validate_silver_data
    trigger_rule: all_success

  - task_id: notify_failure
    operator: SlackWebhookOperator
    http_conn_id: slack_bos_alerts
    message: "❌ Silver ETL 실패: {{ ds_nodash }} {{ execution_date.hour }}시 — 즉시 확인 필요"
    trigger_rule: one_failed
```

### 4.2 Silver → Gold 집계 DAG (일별)

```yaml
dag_id: bos_silver_to_gold_daily
description: "BOS Silver to Gold 일별 집계 파이프라인"
schedule_interval: "0 1 * * *"   # 매일 01:00 MYT (UTC+8 → UTC 17:00 전일)
start_date: "2026-01-01"
catchup: false
max_active_runs: 1
tags:
  - bos
  - aggregation
  - gold

tasks:
  - task_id: run_daily_revenue_aggregation
    operator: SparkSubmitOperator
    application: s3://bos-spark-jobs/gold_aggregation_job.py
    args:
      - "--aggregation_date={{ ds }}"

  - task_id: run_toll_simulation
    operator: SparkSubmitOperator
    application: s3://bos-spark-jobs/toll_simulation_job.py
    depends_on:
      - run_daily_revenue_aggregation

  - task_id: refresh_athena_views
    operator: AWSAthenaOperator
    query: "MSCK REPAIR TABLE gold_daily_revenue"
    database: bos_analytics
    depends_on:
      - run_daily_revenue_aggregation

  - task_id: generate_daily_report
    operator: PythonOperator
    python_callable: generate_pdf_report
    op_kwargs:
      report_date: "{{ ds }}"
      recipients:
        - cio@jvc.my
        - toc-manager@jvc.my
    depends_on:
      - refresh_athena_views
```

### 4.3 월별 재무 보고 DAG

```yaml
dag_id: bos_monthly_finance_report
description: "BOS 월별 재무 보고서 자동 생성"
schedule_interval: "0 2 1 * *"   # 매월 1일 02:00 MYT
start_date: "2026-02-01"
catchup: false
tags:
  - bos
  - finance
  - monthly

tasks:
  - task_id: aggregate_monthly_revenue
    operator: SparkSubmitOperator
    application: s3://bos-spark-jobs/monthly_finance_job.py
    args:
      - "--report_month={{ macros.ds_format(ds, '%Y-%m-%d', '%Y-%m') }}"

  - task_id: generate_excel_report
    operator: PythonOperator
    python_callable: generate_excel_finance_report
    depends_on:
      - aggregate_monthly_revenue

  - task_id: upload_to_s3_archive
    operator: S3CopyObjectOperator
    source_bucket: bos-reports-temp
    dest_bucket: bos-reports-archive
    depends_on:
      - generate_excel_report

  - task_id: send_email_to_board
    operator: EmailOperator
    to:
      - ceo@jvc.my
      - cfo@jvc.my
      - board@jvc.my
    subject: "BOS 월별 수익 보고서 - {{ macros.ds_format(ds, '%Y-%m-%d', '%Y년 %m월') }}"
    files:
      - "/tmp/monthly_report_{{ ds_nodash }}.pdf"
      - "/tmp/monthly_report_{{ ds_nodash }}.xlsx"
    depends_on:
      - generate_excel_report
```

---

## 5. TOC 운영 분석 대시보드

### 5.1 대시보드 패널 구성

```
┌─────────────────────────────────────────────────────────────┐
│  BOS TOC 운영 대시보드 (실시간 갱신: 60초)                    │
├──────────────┬──────────────┬──────────────┬────────────────┤
│ 오늘 총 수익  │  처리 TPS   │  오류율      │ 미납 건수       │
│  RM 485,230  │  8,432/s    │  0.03%       │  1,247건       │
├──────────────┴──────────────┴──────────────┴────────────────┤
│  [플라자별 수익 막대 차트]    [시간대별 교통량 히트맵]          │
├──────────────────────────────────────────────────────────────┤
│  [Channel A vs B 결제 비율]  [차량 클래스 분포 파이 차트]      │
├──────────────────────────────────────────────────────────────┤
│  최근 이상 알림                                               │
│  ⚠ 14:32 Kesas Toll Gate 3 — 오류율 급등 (2.1%)             │
│  ⚠ 13:15 Linkedua Plaza — ANPR 인식 실패 증가               │
└──────────────────────────────────────────────────────────────┘
```

### 5.2 Grafana 대시보드 핵심 패널 정의

```json
{
  "panels": [
    {
      "id": 1,
      "title": "실시간 TPS",
      "type": "stat",
      "datasource": "Prometheus",
      "targets": [
        {
          "expr": "sum(rate(bos_transactions_total[1m]))",
          "legendFormat": "TPS"
        }
      ]
    },
    {
      "id": 2,
      "title": "플라자별 일 수익 (RM)",
      "type": "barchart",
      "datasource": "Athena",
      "targets": [
        {
          "rawSQL": "SELECT plaza_code, SUM(total_revenue) as revenue FROM gold_daily_revenue WHERE aggregation_date = CURRENT_DATE GROUP BY plaza_code ORDER BY revenue DESC"
        }
      ]
    },
    {
      "id": 3,
      "title": "교통량 히트맵 (시간대 × 플라자)",
      "type": "heatmap",
      "datasource": "Athena",
      "targets": [
        {
          "rawSQL": "SELECT date_format(hour, '%H') as hour_label, plaza_code, vehicle_count FROM gold_hourly_traffic WHERE date(hour) = CURRENT_DATE"
        }
      ]
    }
  ]
}
```

---

## 6. 완료 기준

### 6.1 기술적 완료 기준

| 항목 | 목표값 | 측정 방법 |
|------|--------|-----------|
| Bronze 적재 지연 | < 2분 (Kafka 이벤트 발생 대비) | Kafka lag 모니터링 |
| Silver ETL 처리 시간 | 시간당 배치 < 10분 | Airflow 실행 이력 |
| Gold 집계 처리 시간 | 일별 배치 < 30분 | Airflow 실행 이력 |
| 데이터 정합성 | Silver ↔ OLTP 오차 < 0.01% | 일일 조정 검증 |
| 대시보드 응답 시간 | 쿼리 < 5초 | Athena 실행 시간 |
| DAG 성공률 | > 99.5% (월간) | Airflow 통계 |

### 6.2 비즈니스 완료 기준

- [ ] 플라자 관리자가 대시보드에서 실시간 KPI를 조회할 수 있음
- [ ] 월별 재무 보고서가 자동으로 이사회에 이메일 발송됨
- [ ] 요금 시뮬레이션 3개 이상 시나리오가 Gold Layer에 저장됨
- [ ] ANPR 이미지 30일 자동 삭제 정책이 S3 Lifecycle으로 설정됨
- [ ] CIO가 대시보드 및 보고서 최종 승인

### 6.3 품질 게이트

```
G-HARD Gate 5 통과 조건:
  ✅ Delta Lake Bronze/Silver/Gold 3계층 구성 완료
  ✅ Airflow DAG 7일 연속 무장애 실행
  ✅ 재무 보고서 자동 생성 검증
  ✅ 데이터 정합성 검증 통과 (OLTP vs Gold 오차 < 0.01%)
  ✅ 보안 감사: PDPA 준수 (ANPR 30일 삭제 확인)
```

---

## 7. 리스크 관리

| 리스크 | 발생 가능성 | 영향도 | 대응 방안 |
|--------|-----------|--------|-----------|
| EMR 클러스터 비용 초과 | 중 | 중 | Spot Instance 활용, 자동 스케일링 설정 |
| Spark Job OOM 오류 | 중 | 고 | 파티션 분할 최적화, 메모리 튜닝 |
| Delta Lake 스키마 충돌 | 저 | 고 | Schema Evolution 정책 사전 정의 |
| Airflow DAG 연쇄 실패 | 저 | 중 | Circuit Breaker 패턴, 독립 DAG 설계 |
| Gold Layer 집계 오류 | 저 | 고 | Unit Test + 데이터 검증 Task 필수 포함 |
| PDPA 이미지 미삭제 | 저 | 매우고 | S3 Lifecycle 자동 정책 + 월간 감사 |

---

## 8. GSD 명령어

```bash
# Phase 8 시작
/gsd:execute-phase phase=08_bigdata

# 개별 태스크 실행
/gsd:do BIGDATA-001  # Delta Lake 클러스터 프로비저닝
/gsd:do BIGDATA-002  # Bronze Layer 구현
/gsd:do BIGDATA-003  # Silver Layer 구현
/gsd:do BIGDATA-004  # Gold Layer 구현
/gsd:do BIGDATA-005  # Airflow DAG 구성
/gsd:do BIGDATA-006  # 요금 시뮬레이션 모델
/gsd:do BIGDATA-007  # reporting-service API
/gsd:do BIGDATA-008  # TOC 운영 대시보드
/gsd:do BIGDATA-009  # 교통 패턴 분석
/gsd:do BIGDATA-010  # 재무 보고 자동화

# 진행 상황 확인
/gsd:progress phase=08_bigdata

# Phase 8 완료 및 다음 Phase 이동
/gsd:complete-milestone phase=08_bigdata
/gsd:next
```

---

## 9. 참조 문서

| 문서 | 경로 | 관련 내용 |
|------|------|-----------|
| 시스템 개요 | `02_system/01_system_overview.md` | 마이크로서비스 아키텍처 |
| 데이터 아키텍처 | `03_data/01_data_architecture.md` | Delta Lake 설계 |
| 데이터 모델 | `03_data/02_data_model.md` | Gold Layer 스키마 |
| 보안 컴플라이언스 | `03_data/05_security_compliance.md` | PDPA, 데이터 보존 |
| AI 기능 | `02_system/04_ai_features.md` | Phase 9 연계 |
| GSD 워크플로우 | `04_dev/05_gsd_workflow.md` | 실행 명령어 |
| Phase 7 (알림) | `06_phases/07_phase07_notification.md` | 선행 Phase |
| Phase 9 (AI) | `06_phases/09_phase09_ai.md` | 후행 Phase |

---

*최종 업데이트: 2026-04 | Phase 8: 빅데이터 & 분석 플랫폼 | v1.0*
