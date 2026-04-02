---
name: bigdata-service-framework
description: Spark, ClickHouse, Kafka Streams architecture, processing SLAs, and streaming vs batch decision guide
use_when:
  - Spark 배치 처리 또는 Kafka Streams 스트리밍 아키텍처를 선택해야 할 때
  - ClickHouse 실시간 집계 쿼리를 설계할 때
  - Phase 8 Big Data 파이프라인 구성 시
dont_use_when:
  - 집계 테이블 DDL이 필요할 때 (aggregation-units 사용)
  - 전체 데이터 레이어 구조가 필요할 때 (data-architecture-standards 사용)
---

# Big Data 서비스 프레임워크

## 1. 개요

BOS Big Data 플랫폼은 **Kafka Streams (실시간)**, **Apache Spark (배치)**, **ClickHouse (분석)** 3계층으로 구성된다. 처리 목적과 SLA에 따라 적절한 기술을 선택한다.

---

## 2. 핵심 내용

### 2.1 기술 스택 선택 가이드

| 기준 | Kafka Streams | Apache Spark | ClickHouse |
|------|-------------|-------------|-----------|
| 처리 지연 | < 500ms | 분 단위 | 초 단위 |
| 데이터 볼륨 | 중간 (이벤트 스트림) | 대용량 (전체 히스토리) | 대용량 (집계 조회) |
| 사용 사례 | 실시간 미납 탐지, 거래 검증 | 일/월별 집계 배치, Delta Lake ETL | 대시보드 KPI, Ad-hoc 분석 |
| 상태 관리 | RocksDB (로컬) | 외부 (S3 체크포인트) | 없음 (순수 집계) |

### 2.2 Kafka Streams 실시간 처리 패턴

```java
// RFID 이벤트 실시간 미납 탐지
StreamsBuilder builder = new StreamsBuilder();

KStream<String, RfidEvent> rfidEvents = builder.stream("raw.rfid.events");

rfidEvents
    .filter((key, event) -> event.getReadType() == ReadType.EXIT)
    .selectKey((key, event) -> event.getTagId())
    .join(
        vehicleTagTable,  // KTable: 차량 태그 정보
        (event, tag) -> new Transaction(event, tag),
        Joined.with(Serdes.String(), rfidEventSerde, vehicleTagSerde)
    )
    .filter((key, txn) -> txn.getPaymentStatus() == PaymentStatus.PENDING)
    .to("events.unpaid.detected");

// 처리 SLA: 통과 후 500ms 내 미납 이벤트 발행
```

### 2.3 Spark 배치 처리 패턴 (Delta Lake)

```python
# Spark 일별 집계 배치
spark.sql("""
    MERGE INTO silver_monthly_summary AS target
    USING (
        SELECT
            DATE_FORMAT(business_date, 'yyyy-MM') AS year_month,
            concessionaire_id,
            channel,
            vehicle_class,
            SUM(txn_count)    AS txn_count,
            SUM(gross_amount) AS gross_amount,
            SUM(net_amount)   AS net_amount
        FROM bronze_daily_txn
        WHERE business_date = DATE_SUB(CURRENT_DATE, 1)
        GROUP BY 1, 2, 3, 4
    ) AS source
    ON target.year_month = source.year_month
       AND target.concessionaire_id = source.concessionaire_id
       AND target.channel = source.channel
       AND target.vehicle_class = source.vehicle_class
    WHEN MATCHED THEN UPDATE SET *
    WHEN NOT MATCHED THEN INSERT *
""")
```

### 2.4 ClickHouse 실시간 집계 쿼리 패턴

```sql
-- 최근 1시간 요금소별 throughput (< 2초 응답 목표)
SELECT
    plaza_id,
    toStartOfFiveMinute(event_time) AS window_5min,
    countMerge(txn_count) AS txn_count,
    sumMerge(gross_amount) AS gross_amount
FROM agg_plaza_traffic_mv  -- MaterializedView 활용
WHERE event_time >= now() - INTERVAL 1 HOUR
GROUP BY plaza_id, window_5min
ORDER BY window_5min DESC;
```

### 2.5 처리 SLA 정의

| 파이프라인 | 처리 지연 SLA | 가용성 SLA |
|----------|------------|---------|
| RFID 이벤트 수신 | < 100ms | 99.9% |
| 미납 탐지 (실시간) | < 500ms | 99.9% |
| 일별 집계 완료 | 02:00 이전 | 99.5% |
| KPI 대시보드 갱신 | 15분 이내 | 99.0% |

---

## 3. 주의사항 & 함정

- **Kafka Streams 상태 저장**: RocksDB 디스크 공간 모니터링 필수 (State Store 폭증 가능)
- **Spark 메모리 설정**: `executor.memory` 최소 4GB. OOM 발생 시 `broadcast join` 해제 후 `sort merge join` 전환
- **ClickHouse 샤딩**: 데이터 볼륨 1TB 초과 시 클러스터 샤딩 적용 (현재 단일 노드 가용)

---

## 4. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 데이터 아키텍처 표준 | [`../data-architecture-standards/SKILL.md`](../data-architecture-standards/SKILL.md) |
| 집계 단위 설계 | [`../aggregation-units/SKILL.md`](../aggregation-units/SKILL.md) |
| Phase 8 Big Data | [`../../docs/06_phases/08_phase08_bigdata.md`](../../docs/06_phases/08_phase08_bigdata.md) |
