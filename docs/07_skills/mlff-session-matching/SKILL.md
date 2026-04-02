---
name: mlff-session-matching
description: MLFF Entry-Exit session pairing algorithm — Redis TTL, timeout handling, manual review queue
use_when:
  - MLFF 진입(ENTRY)·진출(EXIT) 이벤트를 페어링하는 로직을 구현할 때
  - 미매칭 세션의 타임아웃 처리 또는 수동 심사 흐름을 설계할 때
  - Phase 3 트랜잭션 엔진 개발 시
dont_use_when:
  - RFID/ANPR 원시 이벤트 수집 단계라면 rfid-anpr-interface 사용
  - SLFF(단일 차선) 방식만 다룰 때 (페어링 불필요)
---

# MLFF Entry-Exit 세션 매칭

## 1. 개요

MLFF(Multi-Lane Free-Flow) 구간에서는 차량이 **진입(ENTRY) 지점**과 **진출(EXIT) 지점**에서 각각 이벤트를 발생시킨다. BOS의 트랜잭션 엔진은 두 이벤트를 **페어링(Pairing)**하여 하나의 완성된 트랜잭션을 생성해야 한다.

---

## 2. 핵심 내용

### 2.1 세션 생명주기

```
[진입 ANPR/RFID 이벤트]
        │
        ▼
  Redis: session:{tag_uid} = {entry_data}
  TTL: 4시간 (최대 MLFF 구간 통과 시간)
        │
        │ 진출 이벤트 수신
        ▼
  Redis: session:{tag_uid} 조회
        │
      ┌─┴─────────────────┐
      │                   │
   매칭 성공           매칭 실패 (키 없음)
      │                   │
  트랜잭션 생성      수동 심사 큐 등록
  Redis 키 삭제      (EXIT_WITHOUT_ENTRY)
```

### 2.2 키 설계 (Redis)

```
Key  : session:{vehicle_tag_uid}:{plaza_code}
Value: {
  "session_id"    : "uuid",
  "tag_uid"       : "TNG-XXXX-YYYY",
  "entry_lane_id" : "PLUS-KL-L01",
  "entry_at_ms"   : 1712000000000,
  "vehicle_class" : 2,
  "entry_toll_id" : "PLUS-KL-NORTH"
}
TTL  : 14400 (4시간, 초 단위)
```

### 2.3 매칭 알고리즘

```python
def match_exit_event(exit_event: RfidEvent | AnprEvent) -> Transaction | None:
    key = f"session:{exit_event.tag_uid}:{exit_event.plaza_code}"
    entry_data = redis.get(key)

    if entry_data is None:
        # 진입 이벤트 없이 진출 — 수동 심사
        enqueue_manual_review(exit_event, reason="EXIT_WITHOUT_ENTRY")
        return None

    entry = json.loads(entry_data)
    fare = calculate_fare(
        entry_toll_id=entry["entry_toll_id"],
        exit_toll_id=exit_event.toll_id,
        vehicle_class=entry["vehicle_class"]
    )
    redis.delete(key)  # 세션 종료

    return Transaction(
        session_id=entry["session_id"],
        tag_uid=exit_event.tag_uid,
        entry_lane_id=entry["entry_lane_id"],
        exit_lane_id=exit_event.lane_id,
        entry_at=entry["entry_at_ms"],
        exit_at=exit_event.captured_at_ms,
        fare_amount=fare,
        vehicle_class=entry["vehicle_class"]
    )
```

### 2.4 TTL 만료 (타임아웃) 처리

```
Redis TTL 만료 이벤트 (keyspace notification)
        │ __keyevent@0__:expired
        ▼
[expiry-processor]
  - session 키 만료 감지
  - 만료된 진입 이벤트를 manual_review_queue에 등록
  - 사유: ENTRY_TIMEOUT (4시간 경과)
```

TTL 만료 후 수동 심사 처리:
- 심사원이 CCTV/ANPR 영상 확인
- 정상 통과 확인 시: 표준 요금으로 트랜잭션 수동 생성
- 이상 상황(차량 고장 등): 면제 처리 또는 현장 확인 요청

### 2.5 이중 진입 방지 (중복 Entry)

```python
def handle_entry_event(entry_event: RfidEvent | AnprEvent) -> None:
    key = f"session:{entry_event.tag_uid}:{entry_event.plaza_code}"
    existing = redis.get(key)

    if existing:
        # 이미 진입 세션 존재 → 이전 세션 타임아웃 처리 후 새 세션 생성
        enqueue_manual_review(
            json.loads(existing),
            reason="DUPLICATE_ENTRY_OVERRIDE"
        )
    redis.setex(key, 14400, json.dumps(entry_data))
```

---

## 3. 예시 시나리오

**시나리오: 고객이 MLFF 구간 진입 후 차량 고장으로 비상 정차 → 4시간 초과**
1. 진입 RFID 이벤트 → Redis에 세션 저장 (TTL 4시간)
2. 4시간 후 TTL 만료 → `expiry-processor`가 만료 감지
3. `manual_review_queue`에 `ENTRY_TIMEOUT` 사유로 등록
4. 심사원이 확인 → 현장 상황 기록 후 면제 또는 표준 요금 처리

---

## 4. 주의사항 & 함정

- **Redis TTL 설정은 최대 MLFF 구간 통과 시간 기반**: 현재 4시간이지만 구간 연장 시 변경 필요 (환경 변수로 관리)
- **동일 태그 UID의 다중 플라자 진입 가능**: `key = session:{tag_uid}:{plaza_code}`에 plaza_code 포함 필수
- **keyspace notification 활성화 필요**: Redis 설정에서 `notify-keyspace-events KEA` 설정 필수

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| RFID/ANPR 이벤트 수집 | [`../rfid-anpr-interface/SKILL.md`](../rfid-anpr-interface/SKILL.md) |
| Phase 3 트랜잭션 처리 | [`../../docs/06_phases/03_phase03_txn.md`](../../docs/06_phases/03_phase03_txn.md) |
| 기술 스택 | [`../../docs/02_system/03_tech_stack.md`](../../docs/02_system/03_tech_stack.md) |
