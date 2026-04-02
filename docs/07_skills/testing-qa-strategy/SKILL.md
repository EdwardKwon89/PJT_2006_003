---
name: testing-qa-strategy
description: Go/No-Go gate criteria, TDD workflow, contract testing (Pact), performance SLO benchmark
use_when:
  - Go/No-Go 게이트 기준을 참조해야 할 때
  - 마이크로서비스 간 계약(Contract) 테스트를 구현할 때
  - TDD 워크플로우 또는 성능 SLO 벤치마크가 필요할 때
  - Phase 3 또는 각 Phase의 QA 계획 수립 시
dont_use_when:
  - 배포 파이프라인 설정이 필요할 때 (devops-deployment 사용)
  - 인시던트 대응 절차가 필요할 때 (incident-runbook 사용)
---

# 테스트 & QA 전략

## 1. 개요

BOS는 **TDD(테스트 주도 개발)**, **계약 테스트(Pact)**, **성능 SLO 벤치마크**를 통해 프로덕션 품질을 보장한다. 각 Phase 배포 전 Go/No-Go 게이트를 통과해야 한다.

---

## 2. 핵심 내용

### 2.1 Go/No-Go 게이트 기준

| 기준 | Go 조건 | No-Go 조건 |
|------|---------|----------|
| 단위 테스트 커버리지 | ≥ 80% | < 80% |
| 통합 테스트 | 전체 통과 | 1건 이상 실패 |
| 계약 테스트 | 전체 통과 | 미실행 또는 실패 |
| 성능 SLO | P99 < SLO × 1.5배 | P99 ≥ SLO × 1.5배 |
| 보안 스캔 | Critical 0건 | Critical 1건 이상 |
| 코드 리뷰 | 2명 이상 LGTM | 2명 미만 |

### 2.2 TDD 워크플로우

```
RED → GREEN → REFACTOR

1. RED: 실패하는 테스트 먼저 작성
   - Acceptance Criteria에서 직접 테스트 케이스 도출
   - Given-When-Then 형식 사용

2. GREEN: 테스트를 통과시키는 최소 코드 작성
   - 완벽한 코드 불필요, 동작하는 코드 우선

3. REFACTOR: 코드 정리 (테스트는 GREEN 유지)
   - 중복 제거, 명명 개선, 패턴 적용
```

```java
// TDD 예시: 정산 불일치 탐지
@Test
void given_settlement_diff_over_50_cents_when_validate_then_escalate() {
    // Given
    BigDecimal bosTotal = new BigDecimal("98450.20");
    BigDecimal partnerTotal = new BigDecimal("98449.50");

    // When
    Decision result = settlementEngine.validate(bosTotal, partnerTotal);

    // Then
    assertThat(result).isEqualTo(Decision.ESCALATED);
    verify(escalationService).escalate(any(), eq("billing-lead"));
}
```

### 2.3 계약 테스트 (Pact)

```python
# Consumer (txn-service) 측 Pact 정의
from pact import Consumer, Provider

pact = Consumer("txn-service").has_pact_with(Provider("jpj-gateway"))

pact.given("차량 WXX1234 등록 완료") \
    .upon_receiving("차량 등록 조회") \
    .with_request("GET", "/vehicle/v2/lookup", query={"plate": "WXX1234"}) \
    .will_respond_with(200, body={
        "plate_number": "WXX1234",
        "vehicle_class": 2,
        "is_blocked": False
    })

# Provider (jpj-gateway) 측 검증
# pact-provider-verifier --pact-broker-url=https://pact.jvc.my
```

### 2.4 성능 SLO 벤치마크

```yaml
# k6 성능 테스트 시나리오
scenarios:
  peak_load:
    executor: ramping-vus
    stages:
      - duration: 2m, target: 100   # 점진적 증가
      - duration: 5m, target: 500   # 피크 유지 (5분)
      - duration: 2m, target: 0     # 점진적 감소

thresholds:
  # 핵심 SLO
  http_req_duration{name:POST_transaction}:
    - 'p(99) < 500'   # P99 < 500ms (txn-service)
  http_req_duration{name:GET_settlement}:
    - 'p(99) < 2000'  # P99 < 2s (정산 API)
  http_req_failed:
    - 'rate < 0.01'   # 에러율 < 1%
```

### 2.5 테스트 환경 구성

| 환경 | 목적 | 데이터 | 배포 방식 |
|------|------|--------|---------|
| `dev` | 개발자 로컬 통합 | 합성 데이터 | 수동 |
| `staging` | E2E 테스트 | 프로덕션 마스킹 | ArgoCD (자동) |
| `perf` | 성능 벤치마크 | 3개월치 합성 데이터 | 수동 (월 1회) |
| `prod` | 프로덕션 | 실제 데이터 | ArgoCD (수동 승인) |

---

## 3. 주의사항 & 함정

- **합성 데이터 생성 자동화**: 테스트 환경에 실제 개인정보 사용 절대 금지. PDPA 위반
- **계약 테스트 Pact Broker**: `pact.jvc.my`에 계약 파일 반드시 게시 (단순 로컬 파일 저장 금지)
- **성능 테스트 격리**: `perf` 환경은 프로덕션 DB와 완전 격리 필수. 부하 테스트가 프로덕션에 영향 금지

---

## 4. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| DevOps & 배포 | [`../devops-deployment/SKILL.md`](../devops-deployment/SKILL.md) |
| Phase 3 인프라 & QA | [`../../docs/06_phases/03_phase03_infra.md`](../../docs/06_phases/03_phase03_infra.md) |
| 시스템 아키텍처 | [`../../docs/02_system/01_system_architecture.md`](../../docs/02_system/01_system_architecture.md) |
