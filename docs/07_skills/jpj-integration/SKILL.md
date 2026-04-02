---
name: jpj-integration
description: JPJ vehicle registration lookup API, road tax block/unblock, RM 0.10/query cost management
use_when:
  - JPJ 차량 등록 정보 조회 API를 구현할 때
  - 도로세 차단/해제 API 연동 시
  - JPJ API 호출 비용(RM 0.10/건) 최적화가 필요할 때
  - Phase 4 계정 관리 또는 Phase 6 위반 처리 개발 시
dont_use_when:
  - JPJ 차단 비즈니스 흐름(에스컬레이션 티어)이 필요할 때 (payment-failure-scenarios 사용)
  - TnG 결제 연동이 필요할 때 (tng-payment 사용)
---

# JPJ 연동

## 1. 개요

**JPJ (Jabatan Pengangkutan Jalan)** — 말레이시아 육상교통국. 차량 등록, 도로세 관리, 운전 면허 발급을 담당하는 정부 기관이다. BOS는 ANPR 기반 번호판 인식 차량을 식별하거나, Tier 3 미납 차량의 도로세를 차단하기 위해 JPJ API를 호출한다.

---

## 2. 핵심 내용

### 2.1 JPJ API 엔드포인트

| API | 메서드 | 경로 | 비용 | 인증 |
|-----|--------|------|------|------|
| 차량 등록 조회 | GET | `/vehicle/v2/lookup?plate={plate}` | RM 0.10/건 | mTLS + API Key |
| 도로세 차단 | POST | `/roadtax/v1/block` | 무료 | mTLS + API Key |
| 도로세 해제 | POST | `/roadtax/v1/unblock` | 무료 | mTLS + API Key |
| 차단 상태 조회 | GET | `/roadtax/v1/status?plate={plate}` | 무료 | mTLS + API Key |

### 2.2 차량 조회 응답 스키마

```json
{
  "plate_number": "WXX 1234",
  "vehicle_class": 2,
  "owner_name": "Ahmad bin Abdullah",
  "owner_ic": "880101-14-1234",
  "roadtax_expiry": "2026-12-31",
  "insurance_expiry": "2026-11-30",
  "is_blocked": false,
  "query_cost_rm": 0.10,
  "query_id": "JPJ-20260403-ABCD1234"
}
```

### 2.3 비용 최적화 — Redis 캐시 전략

```python
# JPJ 조회 비용 RM 0.10/건 → 적극적 캐싱 필수
CACHE_TTL_SECONDS = 86400  # 24시간 (차량 정보 변경 빈도 낮음)

def lookup_vehicle(plate_number: str) -> VehicleInfo:
    cache_key = f"jpj:vehicle:{plate_number}"
    cached = redis.get(cache_key)

    if cached:
        return VehicleInfo.parse(cached)  # 캐시 히트: 비용 0

    # 캐시 미스: JPJ API 호출 (RM 0.10 과금)
    result = jpj_client.lookup(plate_number)
    redis.setex(cache_key, CACHE_TTL_SECONDS, result.to_json())
    billing_logger.record_api_cost("JPJ_LOOKUP", 0.10)
    return result
```

**예상 비용 절감**: 캐시 히트율 90% 가정 → 일 100만 건 조회 시
- 캐시 없음: RM 100,000/일
- 캐시 적용: RM 10,000/일 (90% 절감)

### 2.4 차단/해제 요청 페이로드

```json
// 차단 요청
POST /roadtax/v1/block
{
  "vehicle_plate": "WXX 1234",
  "reason": "TOLL_UNPAID",
  "reference_no": "UNPC-{case_id}",
  "blocking_authority": "JVC-BOS-v1",
  "block_date": "2026-04-03",
  "contact_for_release": "support@bos.jvc.my"
}

// 해제 요청
POST /roadtax/v1/unblock
{
  "vehicle_plate": "WXX 1234",
  "reason": "DEBT_CLEARED",
  "reference_no": "UNPC-{case_id}",
  "payment_reference": "PAY-{payment_id}"
}
```

### 2.5 오류 처리

| HTTP 상태 | 의미 | 처리 방법 |
|---------|------|---------|
| 200 | 성공 | 정상 처리 |
| 404 | 차량 미등록 | `UNREGISTERED_VEHICLE` 태그 후 수동 심사 |
| 429 | Rate Limit 초과 | Exponential Backoff (1s → 2s → 4s), 최대 3회 |
| 500/503 | JPJ 서버 오류 | 재시도 3회 후 PagerDuty P2 알림 |

---

## 3. 예시 시나리오

**시나리오: ANPR 인식 번호판으로 차량 등록 확인**
```python
anpr_plate = "WXX 1234"  # confidence_score = 0.97 (자동 승인 범위)
vehicle = lookup_vehicle(anpr_plate)

if vehicle is None:
    # 차량 미등록 → 수동 심사
    enqueue_manual_review(event, reason="UNREGISTERED_VEHICLE")
else:
    create_transaction(event, vehicle_class=vehicle.vehicle_class)
```

---

## 4. 주의사항 & 함정

- **RM 0.10 과금은 실제 비용**: 테스트 환경에서도 과금됨 (JPJ 테스트 계정 별도 협의)
- **API Key 보안**: JPJ API Key는 HashiCorp Vault에서만 조회. `.env` 파일 금지
- **mTLS 인증서 갱신**: 1년 유효기간, 만료 30일 전 자동 갱신 알림 설정 필수

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 결제 실패 & JPJ 차단 흐름 | [`../payment-failure-scenarios/SKILL.md`](../payment-failure-scenarios/SKILL.md) |
| Phase 4 계정 관리 | [`../../docs/06_phases/04_phase04_account.md`](../../docs/06_phases/04_phase04_account.md) |
| 외부 연동 명세 | [`../../docs/02_system/05_external_integration.md`](../../docs/02_system/05_external_integration.md) |
