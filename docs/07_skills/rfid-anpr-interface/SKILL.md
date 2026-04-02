---
name: rfid-anpr-interface
description: RFID/ANPR hardware event ingestion — gRPC schema, confidence scoring, Kafka raw.* topic pattern
use_when:
  - RFID 태그 읽기 이벤트 처리 로직을 구현해야 할 때
  - ANPR 카메라 번호판 인식 신뢰도 점수를 다뤄야 할 때
  - Kafka raw.* 토픽 스키마를 참조해야 할 때
  - Phase 2 (장비 통신) 또는 Phase 3 (트랜잭션) 개발 시
dont_use_when:
  - MLFF Entry-Exit 페어링 로직이 필요할 때 (mlff-session-matching 사용)
  - 비즈니스 도메인 개요가 필요할 때 (malaysia-tolling-domain 먼저 로드)
---

# RFID/ANPR 인터페이스

## 1. 개요

현장 장비(RFID 리더, ANPR 카메라, RSU)에서 발생하는 **원시 이벤트를 BOS로 수집**하는 파이프라인을 정의한다. 모든 이벤트는 gRPC로 수신 후 Kafka `raw.*` 토픽에 발행된다.

---

## 2. 핵심 내용

### 2.1 하드웨어 이벤트 종류

| 이벤트 유형 | 소스 | Kafka 토픽 | 설명 |
|-----------|------|-----------|------|
| RFID 태그 읽기 | RFID 리더 | `raw.rfid.events` | TnG RFID 태그 UID + 차선 ID |
| ANPR 인식 | ANPR 카메라 | `raw.anpr.events` | 번호판 문자 + 신뢰도 점수 |
| RSU 이벤트 | RSU (Road Side Unit) | `raw.rsu.events` | MLFF 통과 속도, 타임스탬프 |
| 장비 상태 | 모든 현장 장비 | `raw.equipment.heartbeat` | 장비 상태 (정상/경고/오류) |

### 2.2 gRPC 이벤트 스키마

```protobuf
// rfid_event.proto
syntax = "proto3";
package bos.tolling.v1;

message RfidEvent {
  string  event_id       = 1;  // UUID
  string  device_id      = 2;  // 리더 장비 ID
  string  lane_id        = 3;  // 차선 ID (예: PLUS-KL-L01)
  string  tag_uid        = 4;  // TnG RFID 태그 UID
  int64   captured_at_ms = 5;  // Unix ms (장비 현지시각)
  string  direction      = 6;  // ENTRY / EXIT
}

message AnprEvent {
  string  event_id         = 1;
  string  device_id        = 2;
  string  lane_id          = 3;
  string  plate_number     = 4;  // "WXX 1234" 형식
  float   confidence_score = 5;  // 0.0 ~ 1.0
  bytes   image_data       = 6;  // JPEG 이미지 (선택적)
  int64   captured_at_ms   = 7;
  string  direction        = 8;  // ENTRY / EXIT
}
```

### 2.3 신뢰도 점수(Confidence Score) 처리 기준

| 신뢰도 범위 | 처리 방식 |
|-----------|---------|
| ≥ 0.95 | 자동 승인 — 트랜잭션 생성 |
| 0.80 ~ 0.94 | 조건부 승인 — RFID 크로스체크 필수 |
| 0.60 ~ 0.79 | 수동 심사 큐 등록 (`manual_review_queue`) |
| < 0.60 | 자동 기각 — 이벤트 폐기 (감사 로그만 기록) |

### 2.4 Kafka 토픽 설정

```yaml
# raw.rfid.events
partitions: 12       # 차선 수 × 2
replication: 3
retention.ms: 604800000  # 7일
compression: lz4

# raw.anpr.events
partitions: 12
replication: 3
retention.ms: 604800000
compression: lz4
# 이미지 데이터 포함 시 max.message.bytes: 10485760 (10MB)
```

### 2.5 장비 연결 인증

```
현장 장비 → mTLS (클라이언트 인증서) → gRPC Gateway → Kafka
              └─ 인증서: 장비별 개별 발급 (JPJ 요구사항)
              └─ 유효기간: 1년, 갱신 30일 전 알림
```

---

## 3. 예시 시나리오

**시나리오: ANPR 신뢰도 0.72 — 수동 심사 큐 등록**
```python
def process_anpr_event(event: AnprEvent) -> None:
    if event.confidence_score >= 0.95:
        create_transaction(event)
    elif event.confidence_score >= 0.80:
        rfid_event = get_rfid_for_lane(event.lane_id, event.captured_at_ms)
        if rfid_event:
            create_transaction_with_rfid_cross_check(event, rfid_event)
        else:
            enqueue_manual_review(event, reason="LOW_CONFIDENCE_NO_RFID")
    elif event.confidence_score >= 0.60:
        enqueue_manual_review(event, reason="BELOW_AUTO_APPROVAL_THRESHOLD")
    else:
        log_rejected_event(event, reason="CONFIDENCE_TOO_LOW")
```

---

## 4. 주의사항 & 함정

- **타임스탬프 편차**: 현장 장비 시계가 NTP와 최대 500ms 편차 가능. 이벤트 수신 서버 시각(`server_received_at`)을 병행 기록하여 정렬에 사용
- **이미지 데이터 선택적 포함**: 이미지는 `raw.anpr.events`에 포함하지 않고 S3에 별도 업로드 후 `image_url`만 전달 권장 (Kafka 메시지 크기 제한)
- **RFID 중복 이벤트**: 동일 태그가 짧은 시간 내 2회 이상 읽힐 수 있음 → `event_id` 기반 Idempotent 처리 필수

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| MLFF 세션 매칭 | [`../mlff-session-matching/SKILL.md`](../mlff-session-matching/SKILL.md) |
| 외부 연동 명세 | [`../../docs/02_system/05_external_integration.md`](../../docs/02_system/05_external_integration.md) |
| Phase 2 통신 | [`../../docs/06_phases/02_phase02_comm.md`](../../docs/06_phases/02_phase02_comm.md) |
| Phase 3 트랜잭션 | [`../../docs/06_phases/03_phase03_txn.md`](../../docs/06_phases/03_phase03_txn.md) |
