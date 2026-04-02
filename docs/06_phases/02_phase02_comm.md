# Phase 2: 커뮤니케이션 레이어
## 06_phases/02_phase02_comm.md
## v1.0 | 2026-04 | 참조: 02_system/02_service_domains.md, 04_dev/02_paperclip_org.md

---

> **Agent 사용 지침**
> `txn-lead`, `devops-lead` Agent가 RFID/ANPR 이벤트 파이프라인 구현 시 반드시 로드.
> 본 문서는 Phase 2 실행의 유일한 정식 기준 문서이며, 태스크 분배 및 완료 판정의 근거로 사용된다.

---

## 1. Phase 개요

### 1.1 목적 및 범위

Phase 2는 Malaysia SLFF/MLFF Tolling BOS의 **커뮤니케이션 레이어**를 구축하는 단계다. 물리적 톨게이트 장비(RFID 리더, ANPR 카메라, RSU)로부터 수신되는 원시 이벤트를 수집하고, Kafka 메시지 파이프라인을 통해 하위 처리 서비스로 안정적으로 전달하는 인프라를 완성한다.

**핵심 목표:**
- gRPC 기반의 고성능 이벤트 수신 서버 구축 (10,000 TPS 목표)
- Kafka 토픽 구조 정의 및 파티션 전략 수립
- Protobuf 스키마 버전 관리 체계 확립
- Dead Letter Queue(DLQ)를 통한 장애 복원력 확보
- 이벤트 유효성 검증 및 역직렬화 파이프라인 완성

### 1.2 Phase 연계

| 구분 | 내용 |
|------|------|
| **선행 Phase** | Phase 1 — 인프라 기반 (Kubernetes 클러스터, Kafka 클러스터, 네트워크 설정 완료 필수) |
| **후행 Phase** | Phase 3 — 트랜잭션 처리 엔진 (Phase 2의 Kafka 토픽 및 Consumer Group 설정 완료 후 착수 가능) |
| **예상 기간** | **2주** (Sprint 3~4) |
| **병렬 가능 작업** | Protobuf 스키마 정의 ↔ Kafka 토픽 생성 (독립 진행 가능) |

### 1.3 아키텍처 포지션

```
[RFID Reader]  [ANPR Camera]  [RSU / OBU]
      │               │              │
      └───────────────┼──────────────┘
                      ▼
            ┌─────────────────┐
            │  gRPC Gateway   │  ← Phase 2 구현 영역
            │  (event-ingest) │
            └────────┬────────┘
                     │ Protobuf
                     ▼
            ┌─────────────────┐
            │  Kafka Cluster  │  ← Phase 2 구현 영역
            │  (5 Topics)     │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  txn-service    │  ← Phase 3 영역
            │  (Consumer)     │
            └─────────────────┘
```

---

## 2. 담당 Agent 및 역할 분담

### 2.1 Phase 2 참여 Agent

| Agent | 역할 | 주요 책임 영역 |
|-------|------|--------------|
| **txn-lead** | Phase 2 리드 | gRPC 서비스 설계, 스키마 리뷰, 완료 판정 |
| **txn-dev-1** | 백엔드 개발 #1 | gRPC 서버 구현, Protobuf 스키마 정의 |
| **txn-dev-2** | 백엔드 개발 #2 | Kafka Consumer Group 설정, DLQ 구현 |
| **devops-lead** | 인프라 & 운영 | Kafka 토픽 생성, 파티션 전략, 모니터링 설정 |

### 2.2 협업 방식

```
txn-lead
  ├── txn-dev-1: gRPC 서버 구현 위임 → 일일 리뷰
  ├── txn-dev-2: Kafka Consumer 구현 위임 → 일일 리뷰
  └── devops-lead: 인프라 설정 협업 → Kafka 토픽 파라미터 협의

보고 라인: txn-lead → arch-lead (주간) → PM (마일스톤 기준)
```

### 2.3 Agent 간 인터페이스

- **txn-lead ↔ devops-lead**: Kafka 토픽 명세서(토픽명, 파티션 수, 보존 정책) 문서로 인터페이스
- **txn-dev-1 ↔ txn-dev-2**: Protobuf 스키마 파일(`.proto`)을 공유 저장소에 등록 후 Consumer 구현

---

## 3. 주요 태스크 체크리스트

### 3.1 gRPC 서버 구현 (RFID/ANPR 이벤트 수신기)

- [ ] **T2-01** Spring Boot 3.x + `grpc-spring-boot-starter` 프로젝트 생성
- [ ] **T2-02** `EventIngestService` gRPC 서비스 클래스 구현
  - `receiveSLFFEvent(SLFFEventRequest) → EventAck`
  - `receiveMLFFEntry(MLFFEntryRequest) → EventAck`
  - `receiveMLFFExit(MLFFExitRequest) → EventAck`
  - `receiveANPREvent(ANPREventRequest) → EventAck`
  - `receiveEquipmentStatus(EquipmentStatusRequest) → EventAck`
- [ ] **T2-03** TLS 1.3 mutual authentication 설정 (장비 인증서 기반)
- [ ] **T2-04** gRPC 서버 포트 설정: `9090` (내부), `443` (외부 장비 연결)
- [ ] **T2-05** 연결 풀링 및 keepalive 설정 최적화
- [ ] **T2-06** 서버 반영구 스트림(server-side streaming) 구현 — 장비 상태 실시간 Push
- [ ] **T2-07** gRPC Health Check 프로토콜 구현 (`grpc.health.v1.Health`)
- [ ] **T2-08** Micrometer + Prometheus 메트릭 연동 (요청수, 지연시간, 에러율)

### 3.2 Kafka 토픽 생성 및 파티션 전략

- [ ] **T2-09** Kafka 클러스터 토픽 생성 (아래 5개 토픽)

| 토픽명 | 파티션 수 | 복제 인수 | 보존 기간 | 설명 |
|--------|----------|---------|---------|------|
| `raw.rfid.events` | 24 | 3 | 7일 | RFID 리더 원시 이벤트 |
| `raw.anpr.events` | 24 | 3 | 7일 | ANPR 카메라 원시 이벤트 |
| `processed.txn.events` | 32 | 3 | 30일 | 처리 완료 트랜잭션 |
| `violation.events` | 16 | 3 | 90일 | 위반 이벤트 (법적 보존) |
| `equipment.status` | 8 | 3 | 3일 | 장비 상태 이벤트 |

- [ ] **T2-10** 파티션 키 전략 정의
  - `raw.rfid.events`: `{plaza_id}_{lane_id}` 기준 파티셔닝
  - `raw.anpr.events`: `{plaza_id}_{lane_id}` 기준 파티셔닝
  - `processed.txn.events`: `{vehicle_id}` 기준 파티셔닝 (순서 보장)
  - `violation.events`: `{vehicle_id}` 기준 파티셔닝
  - `equipment.status`: `{equipment_id}` 기준 파티셔닝
- [ ] **T2-11** Kafka Schema Registry 연동 (Confluent Schema Registry)
- [ ] **T2-12** 토픽별 압축 설정: `lz4` (처리 토픽), `snappy` (원시 이벤트)
- [ ] **T2-13** Kafka 모니터링 대시보드 구성 (Grafana + Kafka Exporter)

### 3.3 Protobuf 스키마 정의

- [ ] **T2-14** `slff_event.proto` 스키마 작성 및 등록
- [ ] **T2-15** `mlff_event.proto` 스키마 작성 및 등록 (Entry/Exit 통합)
- [ ] **T2-16** `anpr_event.proto` 스키마 작성 및 등록
- [ ] **T2-17** `equipment_event.proto` 스키마 작성 및 등록
- [ ] **T2-18** `common_types.proto` 공통 타입 정의 (Timestamp, PlazaId, LaneId, VehicleClass)
- [ ] **T2-19** 스키마 버전 관리 정책 수립 (하위 호환 필드 추가만 허용, 필드 번호 변경 금지)
- [ ] **T2-20** 스키마 호환성 테스트 자동화 (CI/CD 파이프라인 연동)

### 3.4 Kafka Consumer Group 설정

- [ ] **T2-21** Consumer Group 정의

| Consumer Group | 구독 토픽 | 인스턴스 수 |
|---------------|---------|-----------|
| `txn-processor-group` | `raw.rfid.events`, `raw.anpr.events` | 4 |
| `violation-detector-group` | `processed.txn.events` | 2 |
| `equipment-monitor-group` | `equipment.status` | 2 |
| `audit-logger-group` | `processed.txn.events`, `violation.events` | 2 |

- [ ] **T2-22** Consumer Group offset 관리 전략 수립 (자동 커밋 비활성화, 수동 커밋)
- [ ] **T2-23** Consumer Group rebalance 정책 설정 (`CooperativeStickyAssignor`)
- [ ] **T2-24** `max.poll.records=500`, `max.poll.interval.ms=300000` 설정

### 3.5 이벤트 역직렬화 & 유효성 검증

- [ ] **T2-25** Protobuf Deserializer 구현 (`KafkaProtobufDeserializer` 확장)
- [ ] **T2-26** 이벤트 유효성 검증 규칙 구현

| 검증 항목 | 규칙 | 실패 시 처리 |
|---------|------|-----------|
| PlazaID 유효성 | 등록된 PlazaID 목록 조회 | DLQ 전송 |
| LaneID 유효성 | PlazaID 기준 LaneID 매핑 확인 | DLQ 전송 |
| 타임스탬프 범위 | 현재 시각 ±5분 이내 | 경고 로그 + 처리 계속 |
| 차량 번호판 형식 | 말레이시아 번호판 정규식 검증 | DLQ 전송 |
| 필수 필드 누락 | proto `required` 필드 존재 확인 | DLQ 전송 |

- [ ] **T2-27** 검증 실패 이벤트 상세 로깅 (원본 바이트 + 실패 사유)
- [ ] **T2-28** 검증 통계 메트릭 노출 (검증 성공률, 실패율 by 토픽)

### 3.6 Dead Letter Queue (DLQ) 설정

- [ ] **T2-29** DLQ 토픽 생성

| DLQ 토픽명 | 보존 기간 | 대상 |
|-----------|---------|------|
| `dlq.raw.rfid.events` | 30일 | RFID 역직렬화/검증 실패 |
| `dlq.raw.anpr.events` | 30일 | ANPR 역직렬화/검증 실패 |
| `dlq.processed.txn.events` | 30일 | 트랜잭션 처리 실패 |

- [ ] **T2-30** DLQ 라우팅 로직 구현 (실패 사유 헤더 포함)
- [ ] **T2-31** DLQ 재처리 유틸리티 CLI 개발 (수동 재처리 지원)
- [ ] **T2-32** DLQ 이벤트 알림 설정 (임계값 초과 시 PagerDuty/Slack 알림)
- [ ] **T2-33** DLQ 이벤트 대시보드 구성 (토픽별 DLQ 적재량 모니터링)

### 3.7 처리량 테스트 (10,000 TPS 목표)

- [ ] **T2-34** 부하 테스트 환경 구성 (k6 + Grafana)
- [ ] **T2-35** gRPC 엔드포인트 부하 테스트
  - 목표: 10,000 req/s (단일 엔드포인트 기준)
  - 지연 목표: P99 < 50ms
- [ ] **T2-36** Kafka Producer 처리량 테스트
  - 목표: 15,000 msg/s (버퍼 확보 포함)
- [ ] **T2-37** Kafka Consumer 처리량 테스트
  - 목표: 10,000 msg/s (Consumer Group 병렬)
- [ ] **T2-38** 병목 구간 분석 및 튜닝 (JVM 힙, 네트워크 버퍼, Kafka 배치 설정)
- [ ] **T2-39** 최종 성능 테스트 리포트 작성 (arch-lead 승인 필요)

---

## 4. gRPC 서비스 정의 (.proto 파일)

### 4.1 공통 타입 정의

```protobuf
// common_types.proto
syntax = "proto3";
package com.bos.common.v1;

import "google/protobuf/timestamp.proto";

// 차량 등급 (말레이시아 도로공사 기준)
enum VehicleClass {
  VEHICLE_CLASS_UNSPECIFIED = 0;
  CLASS_1 = 1;  // 모터사이클
  CLASS_2 = 2;  // 소형차
  CLASS_3 = 3;  // 중형차 (택시 포함)
  CLASS_4 = 4;  // 대형차 (버스/트럭)
  CLASS_5 = 5;  // 중형 트럭
}

// 결제 채널
enum PaymentChannel {
  PAYMENT_CHANNEL_UNSPECIFIED = 0;
  CHANNEL_A_RFID = 1;   // RFID SmartTAG
  CHANNEL_B_TNG  = 2;   // TnG eWallet
  CHANNEL_CASH   = 3;   // 현금 (예외 처리용)
}

// 플라자 및 차로 식별자
message PlazaLaneId {
  string plaza_id = 1;  // 예: "PLZ-001"
  string lane_id  = 2;  // 예: "LANE-A1"
}

// 표준 응답
message EventAck {
  string event_id    = 1;
  bool   accepted    = 2;
  string reject_code = 3;  // accepted=false 시 실패 코드
}
```

### 4.2 SLFF 이벤트 스키마

```protobuf
// slff_event.proto
syntax = "proto3";
package com.bos.slff.v1;

import "google/protobuf/timestamp.proto";
import "common_types.proto";

// SLFF (Single Lane Free Flow) 원시 이벤트
message SLFFEvent {
  string          event_id       = 1;  // UUID v4
  PlazaLaneId     plaza_lane     = 2;
  string          rfid_tag_id    = 3;  // RFID 태그 고유 ID
  string          plate_number   = 4;  // 번호판 (ANPR 보조 인식)
  VehicleClass    vehicle_class  = 5;
  PaymentChannel  payment_channel = 6;
  double          transaction_amount = 7;  // 말레이시아 링깃 (MYR)
  google.protobuf.Timestamp event_time = 8;
  string          equipment_id   = 9;
  bytes           raw_rfid_data  = 10; // 원시 RFID 바이트 (감사용)
}

// gRPC 요청/응답 래퍼
message SLFFEventRequest {
  SLFFEvent event = 1;
}
```

### 4.3 MLFF 이벤트 스키마

```protobuf
// mlff_event.proto
syntax = "proto3";
package com.bos.mlff.v1;

import "google/protobuf/timestamp.proto";
import "common_types.proto";

// MLFF Entry 이벤트 (진입 플라자)
message MLFFEntryEvent {
  string          event_id       = 1;
  string          session_id     = 2;  // Entry-Exit 매칭 키
  PlazaLaneId     entry_plaza    = 3;
  string          rfid_tag_id    = 4;
  string          plate_number   = 5;
  VehicleClass    vehicle_class  = 6;
  google.protobuf.Timestamp entry_time = 7;
  string          entry_equipment_id = 8;
  double          gantry_speed_kmh   = 9;  // 통과 속도 (km/h)
}

// MLFF Exit 이벤트 (진출 플라자)
message MLFFExitEvent {
  string          event_id       = 1;
  string          session_id     = 2;  // Entry session_id와 매칭
  PlazaLaneId     exit_plaza     = 3;
  string          rfid_tag_id    = 4;
  string          plate_number   = 5;
  VehicleClass    vehicle_class  = 6;
  PaymentChannel  payment_channel = 7;
  google.protobuf.Timestamp exit_time = 8;
  string          exit_equipment_id = 9;
}

message MLFFEntryRequest { MLFFEntryEvent event = 1; }
message MLFFExitRequest  { MLFFExitEvent  event = 1; }
```

### 4.4 ANPR 이벤트 스키마

```protobuf
// anpr_event.proto
syntax = "proto3";
package com.bos.anpr.v1;

import "google/protobuf/timestamp.proto";
import "common_types.proto";

// ANPR (Automatic Number Plate Recognition) 이벤트
message ANPREvent {
  string          event_id       = 1;
  PlazaLaneId     plaza_lane     = 2;
  string          plate_number   = 3;  // 인식된 번호판
  float           confidence     = 4;  // OCR 신뢰도 (0.0~1.0)
  string          image_ref      = 5;  // MinIO 이미지 참조 경로
  VehicleClass    vehicle_class  = 6;  // 카메라 AI 분류
  google.protobuf.Timestamp capture_time = 7;
  string          camera_id      = 8;
  // 위반 감지 플래그
  bool            is_no_rfid     = 9;   // RFID 미감지
  bool            is_wrong_class = 10;  // 차량 등급 불일치
}

message ANPREventRequest { ANPREvent event = 1; }
```

### 4.5 장비 상태 이벤트 스키마

```protobuf
// equipment_event.proto
syntax = "proto3";
package com.bos.equipment.v1;

import "google/protobuf/timestamp.proto";

enum EquipmentStatus {
  EQUIPMENT_STATUS_UNSPECIFIED = 0;
  ONLINE  = 1;
  OFFLINE = 2;
  DEGRADED = 3;  // 부분 장애
  MAINTENANCE = 4;
}

message EquipmentStatusEvent {
  string           event_id      = 1;
  string           equipment_id  = 2;
  string           plaza_id      = 3;
  EquipmentStatus  status        = 4;
  string           status_detail = 5;  // 장애 사유 (선택)
  google.protobuf.Timestamp report_time = 6;
  map<string, string> diagnostics = 7;  // 진단 데이터 KV
}

message EquipmentStatusRequest { EquipmentStatusEvent event = 1; }
```

### 4.6 gRPC 서비스 인터페이스 통합

```protobuf
// event_ingest_service.proto
syntax = "proto3";
package com.bos.ingest.v1;

import "slff_event.proto";
import "mlff_event.proto";
import "anpr_event.proto";
import "equipment_event.proto";
import "common_types.proto";

service EventIngestService {
  // SLFF 단일 이벤트 수신 (Unary RPC)
  rpc ReceiveSLFFEvent(com.bos.slff.v1.SLFFEventRequest)
      returns (com.bos.common.v1.EventAck);

  // MLFF 진입 이벤트 수신 (Unary RPC)
  rpc ReceiveMLFFEntry(com.bos.mlff.v1.MLFFEntryRequest)
      returns (com.bos.common.v1.EventAck);

  // MLFF 진출 이벤트 수신 (Unary RPC)
  rpc ReceiveMLFFExit(com.bos.mlff.v1.MLFFExitRequest)
      returns (com.bos.common.v1.EventAck);

  // ANPR 이벤트 수신 (Unary RPC)
  rpc ReceiveANPREvent(com.bos.anpr.v1.ANPREventRequest)
      returns (com.bos.common.v1.EventAck);

  // 장비 상태 이벤트 수신 (Unary RPC)
  rpc ReceiveEquipmentStatus(com.bos.equipment.v1.EquipmentStatusRequest)
      returns (com.bos.common.v1.EventAck);

  // 장비 상태 실시간 스트림 (Server-side Streaming)
  rpc StreamEquipmentAlerts(EquipmentAlertSubscription)
      returns (stream com.bos.equipment.v1.EquipmentStatusEvent);
}

message EquipmentAlertSubscription {
  repeated string plaza_ids = 1;  // 구독할 플라자 목록 (비어있으면 전체)
}
```

---

## 5. Kafka Consumer 코드 패턴 (Spring Boot)

### 5.1 Consumer 설정 (application.yml)

```yaml
spring:
  kafka:
    bootstrap-servers: kafka-cluster:9092
    consumer:
      group-id: txn-processor-group
      auto-offset-reset: earliest
      enable-auto-commit: false          # 수동 커밋 (데이터 손실 방지)
      max-poll-records: 500
      max-poll-interval-ms: 300000
      key-deserializer: org.apache.kafka.common.serialization.StringDeserializer
      value-deserializer: io.confluent.kafka.serializers.protobuf.KafkaProtobufDeserializer
      properties:
        schema.registry.url: http://schema-registry:8081
        specific.protobuf.value.type: com.bos.slff.v1.SLFFEvent
        isolation.level: read_committed  # Exactly-once 보장
    listener:
      ack-mode: MANUAL_IMMEDIATE         # 처리 완료 후 수동 커밋
      concurrency: 4                     # Consumer 스레드 수 (파티션 수 고려)
      type: batch                        # 배치 처리 모드
```

### 5.2 RFID 이벤트 Consumer 구현

```java
@Component
@Slf4j
public class RFIDEventConsumer {

    private final EventValidationService validationService;
    private final TransactionRouter       txnRouter;
    private final KafkaTemplate<String, ProcessedTxnEvent> kafkaTemplate;

    public RFIDEventConsumer(
            EventValidationService validationService,
            TransactionRouter txnRouter,
            KafkaTemplate<String, ProcessedTxnEvent> kafkaTemplate) {
        this.validationService = validationService;
        this.txnRouter         = txnRouter;
        this.kafkaTemplate     = kafkaTemplate;
    }

    @KafkaListener(
        topics   = "raw.rfid.events",
        groupId  = "txn-processor-group",
        containerFactory = "batchKafkaListenerContainerFactory"
    )
    public void consumeRFIDEvents(
            List<ConsumerRecord<String, SLFFEvent>> records,
            Acknowledgment ack) {

        log.debug("배치 수신: {} 건", records.size());

        List<ConsumerRecord<String, SLFFEvent>> valid   = new ArrayList<>();
        List<ConsumerRecord<String, SLFFEvent>> invalid = new ArrayList<>();

        // 1단계: 유효성 검증 분류
        for (ConsumerRecord<String, SLFFEvent> record : records) {
            ValidationResult result = validationService.validate(record.value());
            if (result.isValid()) {
                valid.add(record);
            } else {
                invalid.add(record);
                log.warn("검증 실패 [topic={}, offset={}, reason={}]",
                    record.topic(), record.offset(), result.getFailureReason());
            }
        }

        // 2단계: 유효 이벤트 라우팅
        for (ConsumerRecord<String, SLFFEvent> record : valid) {
            try {
                txnRouter.route(record.value());
            } catch (Exception e) {
                log.error("라우팅 오류 [event_id={}]: {}", record.value().getEventId(), e.getMessage());
                sendToDLQ(record, "ROUTING_ERROR: " + e.getMessage());
            }
        }

        // 3단계: 무효 이벤트 DLQ 전송
        invalid.forEach(record ->
            sendToDLQ(record, "VALIDATION_FAILED"));

        // 4단계: 수동 커밋 (모든 처리 완료 후)
        ack.acknowledge();
    }

    private void sendToDLQ(ConsumerRecord<String, SLFFEvent> record, String reason) {
        Headers headers = new RecordHeaders();
        headers.add("dlq-reason",        reason.getBytes(StandardCharsets.UTF_8));
        headers.add("original-topic",    record.topic().getBytes(StandardCharsets.UTF_8));
        headers.add("original-partition",
            String.valueOf(record.partition()).getBytes(StandardCharsets.UTF_8));
        headers.add("original-offset",
            String.valueOf(record.offset()).getBytes(StandardCharsets.UTF_8));

        ProducerRecord<String, SLFFEvent> dlqRecord =
            new ProducerRecord<>("dlq.raw.rfid.events",
                null, record.key(), record.value(), headers);

        kafkaTemplate.send(dlqRecord)
            .whenComplete((result, ex) -> {
                if (ex != null) {
                    log.error("DLQ 전송 실패 [event_id={}]", record.value().getEventId(), ex);
                }
            });
    }
}
```

### 5.3 이벤트 유효성 검증 서비스

```java
@Service
public class EventValidationService {

    // 말레이시아 번호판 정규식 (예: ABC 1234, W 1234 AB)
    private static final Pattern PLATE_PATTERN =
        Pattern.compile("^[A-Z]{1,3}\\s?\\d{1,4}(\\s?[A-Z]{1,2})?$");

    private static final Duration TIMESTAMP_TOLERANCE = Duration.ofMinutes(5);

    private final PlazaRegistryCache plazaCache;

    public EventValidationService(PlazaRegistryCache plazaCache) {
        this.plazaCache = plazaCache;
    }

    public ValidationResult validate(SLFFEvent event) {
        // 1. PlazaID 유효성
        if (!plazaCache.isValidPlaza(event.getPlazaLane().getPlazaId())) {
            return ValidationResult.fail("INVALID_PLAZA_ID");
        }
        // 2. LaneID 유효성
        if (!plazaCache.isValidLane(
                event.getPlazaLane().getPlazaId(),
                event.getPlazaLane().getLaneId())) {
            return ValidationResult.fail("INVALID_LANE_ID");
        }
        // 3. 번호판 형식 (옵셔널 — ANPR 미인식 허용)
        if (!event.getPlateNumber().isEmpty()
                && !PLATE_PATTERN.matcher(event.getPlateNumber()).matches()) {
            return ValidationResult.fail("INVALID_PLATE_FORMAT");
        }
        // 4. 타임스탬프 범위
        Instant eventTime = Instant.ofEpochSecond(
            event.getEventTime().getSeconds(),
            event.getEventTime().getNanos());
        if (Duration.between(eventTime, Instant.now()).abs().compareTo(TIMESTAMP_TOLERANCE) > 0) {
            // 경고만 — 처리는 계속
            log.warn("타임스탬프 범위 초과 [event_id={}, event_time={}]",
                event.getEventId(), eventTime);
        }
        // 5. 거래 금액 유효성
        if (event.getTransactionAmount() < 0) {
            return ValidationResult.fail("NEGATIVE_AMOUNT");
        }
        return ValidationResult.ok();
    }
}
```

### 5.4 Kafka Producer 설정 (고성능 튜닝)

```java
@Configuration
public class KafkaProducerConfig {

    @Bean
    public ProducerFactory<String, Message> producerFactory() {
        Map<String, Object> config = new HashMap<>();
        config.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, "kafka-cluster:9092");
        config.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
            StringSerializer.class);
        config.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
            KafkaProtobufSerializer.class);
        // 처리량 최적화
        config.put(ProducerConfig.BATCH_SIZE_CONFIG,           65536);     // 64KB
        config.put(ProducerConfig.LINGER_MS_CONFIG,            5);         // 5ms 배치 대기
        config.put(ProducerConfig.COMPRESSION_TYPE_CONFIG,     "lz4");
        config.put(ProducerConfig.BUFFER_MEMORY_CONFIG,        67108864L); // 64MB
        // Exactly-once 시맨틱
        config.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG,   true);
        config.put(ProducerConfig.ACKS_CONFIG,                 "all");
        config.put(ProducerConfig.MAX_IN_FLIGHT_REQUESTS_PER_CONNECTION, 5);
        config.put("schema.registry.url",                      "http://schema-registry:8081");
        return new DefaultKafkaProducerFactory<>(config);
    }
}
```

---

## 6. 완료 기준 체크리스트

### 6.1 기능 완료 기준

- [ ] 5개 gRPC 엔드포인트 모두 정상 응답 확인 (통합 테스트 통과)
- [ ] 5개 Kafka 토픽 생성 완료 및 Schema Registry 등록 완료
- [ ] 3개 DLQ 토픽 생성 및 라우팅 로직 동작 확인
- [ ] 5가지 Protobuf 스키마 등록 완료 (호환성 버전: BACKWARD)
- [ ] Consumer Group 4개 모두 정상 구독 및 처리 확인
- [ ] 이벤트 유효성 검증 5개 규칙 단위 테스트 통과 (100% 커버리지)

### 6.2 성능 완료 기준

- [ ] **gRPC 처리량**: 10,000 req/s 달성 (P99 지연 < 50ms)
- [ ] **Kafka Producer**: 15,000 msg/s 이상 (버퍼 포함)
- [ ] **Kafka Consumer**: 10,000 msg/s 이상 (Consumer Group 병렬)
- [ ] **DLQ 비율**: 정상 부하 조건에서 < 0.1%
- [ ] **장애 복구**: Kafka 브로커 1대 다운 시 30초 내 자동 복구

### 6.3 보안 완료 기준

- [ ] gRPC mutual TLS 인증 활성화 및 장비 인증서 등록 완료
- [ ] Kafka SASL/SSL 클라이언트 인증 완료
- [ ] Schema Registry ACL 설정 완료 (write: txn-service, read: all authorized consumers)

### 6.4 운영 완료 기준

- [ ] Prometheus 메트릭 수집 확인 (gRPC, Kafka 모두)
- [ ] Grafana 대시보드 구성 완료 (처리량, 지연, DLQ, Consumer Lag)
- [ ] 알림 규칙 설정 완료 (Consumer Lag > 10,000, DLQ 증가율 > 100/분)
- [ ] Runbook 작성 완료 (장애 시나리오별 대응 절차)

---

## 7. 리스크 & 대응 방안

| # | 리스크 | 심각도 | 발생 가능성 | 대응 방안 |
|---|--------|--------|-----------|---------|
| R1 | gRPC 연결 과부하로 인한 장비 재연결 루프 | HIGH | MEDIUM | Circuit Breaker 패턴 적용, 장비 재연결 백오프 정책 수립 |
| R2 | Kafka 파티션 불균형으로 Consumer Lag 누적 | HIGH | MEDIUM | 파티션 키 분포 사전 시뮬레이션, 핫 파티션 감지 알림 설정 |
| R3 | Protobuf 스키마 변경으로 하위 호환 파괴 | CRITICAL | LOW | Schema Registry BACKWARD 호환 모드 강제, CI 검증 자동화 |
| R4 | DLQ 누적으로 인한 저장 공간 초과 | MEDIUM | LOW | DLQ 토픽 TTL 30일 설정, 누적량 임계값 알림 |
| R5 | 10,000 TPS 미달성 | HIGH | MEDIUM | 수직 확장(CPU/메모리) + 수평 확장(gRPC 인스턴스 추가) 대비 |
| R6 | 말레이시아 장비 벤더 프로토콜 미호환 | CRITICAL | LOW | 벤더 장비와 사전 POC 테스트, 어댑터 레이어 설계 검토 |

---

## 8. GSD 실행 명령어

### 8.1 Phase 2 시작

```bash
# Phase 2 실행 (txn-lead 주도)
/gsd:execute-phase phase=02 agent=txn-lead

# 개별 태스크 실행
/gsd:do T2-01  # gRPC 서버 프로젝트 생성
/gsd:do T2-09  # Kafka 토픽 생성 (devops-lead)
/gsd:do T2-14  # Protobuf 스키마 정의 시작
```

### 8.2 진행 상황 확인

```bash
# Phase 2 전체 진행률
/gsd:progress phase=02

# 미완료 태스크 목록
/gsd:check-todos phase=02

# Phase 2 완료 검증
/gsd:verify-work phase=02
```

### 8.3 완료 처리

```bash
# Phase 2 마일스톤 완료 선언 (arch-lead 승인 필요)
/gsd:complete-milestone phase=02

# Phase 3 착수 (Phase 2 완료 후)
/gsd:execute-phase phase=03 agent=txn-lead
```

### 8.4 디버깅 명령어

```bash
# Kafka Consumer Lag 확인
kafka-consumer-groups.sh --bootstrap-server kafka-cluster:9092 \
  --describe --group txn-processor-group

# DLQ 이벤트 확인 (최근 10건)
kafka-console-consumer.sh --bootstrap-server kafka-cluster:9092 \
  --topic dlq.raw.rfid.events --max-messages 10 \
  --property print.headers=true

# gRPC 서비스 헬스 체크
grpcurl -plaintext localhost:9090 grpc.health.v1.Health/Check
```

---

## 9. 참조 문서

| 문서 | 경로 | 참조 내용 |
|------|------|---------|
| 시스템 서비스 도메인 | `docs/02_system/02_service_domains.md` | event-ingest-service 위치, Kafka 클러스터 구성 |
| 기술 스택 | `docs/02_system/03_tech_stack.md` | gRPC, Kafka, Protobuf 버전 정의 |
| Paperclip 조직 | `docs/04_dev/02_paperclip_org.md` | txn-lead, txn-dev, devops-lead Agent 역할 정의 |
| 데이터 아키텍처 | `docs/03_data/01_data_architecture.md` | Kafka 토픽 데이터 흐름, 5단계 집계 구조 |
| 보안 컴플라이언스 | `docs/03_data/05_security_compliance.md` | TLS 정책, 데이터 암호화 요건 |
| Phase 1 (인프라) | `docs/06_phases/01_phase01_infra.md` | Kafka 클러스터 설정, 네트워크 토폴로지 |
| Phase 3 (트랜잭션) | `docs/06_phases/03_phase03_txn.md` | Phase 2 완료 후 착수, Consumer 인터페이스 정의 |

---

*문서 버전: v1.0 | 생성일: 2026-04 | 담당: txn-lead*
*다음 업데이트: Phase 2 완료 후 실측 성능 데이터 반영*
