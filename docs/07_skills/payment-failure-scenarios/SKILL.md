---
name: payment-failure-scenarios
description: Tier 1–4 unpaid escalation, JPJ road tax blocking, write-off criteria and workflow
use_when:
  - 미납 탐지 로직 또는 에스컬레이션 자동화를 구현할 때
  - JPJ 도로세 차단 절차를 참조해야 할 때
  - Write-off 기준 및 승인 절차가 필요할 때
  - Phase 6 위반 & 미납 관리 개발 시
dont_use_when:
  - 일반 정산 운영 절차가 필요할 때 (clearing-center-operations 사용)
  - JPJ API 기술 스펙이 필요할 때 (jpj-integration 사용)
---

# 결제 실패 시나리오

## 1. 개요

톨 요금이 정상 수납되지 않은 경우, BOS는 **4단계 Tier 에스컬레이션**을 통해 자동으로 채권 회수를 시도한다. 각 Tier는 명확한 기간, 조치, 알림 방식을 갖는다.

---

## 2. 핵심 내용

### 2.1 Tier 에스컬레이션 요약

| Tier | 기간 | 조치 | 추가 수수료 |
|------|------|------|---------|
| Tier 1 | D+1 ~ D+7 | SMS/이메일 3회 알림 | 없음 |
| Tier 2 | D+8 ~ D+30 | 주 1회 알림, 계정 제한 | 원금 × 10% |
| Tier 3 | D+31 ~ D+90 | JPJ 도로세 차단 | 원금 × 20% |
| Tier 4 | D+91 이후 | Write-off 후보, 법적 조치 | — |

### 2.2 Tier별 자동화 처리

```python
# Tier 에스컬레이션 배치 로직 (매일 07:00)
def escalate_unpaid_cases():
    cases = db.query("""
        SELECT id, principal_amount, tier, tier_updated_at
        FROM unpaid_cases WHERE status = 'OPEN'
    """)
    for case in cases:
        days_in_tier = (now() - case.tier_updated_at).days
        if case.tier == 1 and days_in_tier >= 7:
            upgrade_tier(case, new_tier=2, penalty_rate=0.10)
        elif case.tier == 2 and days_in_tier >= 23:
            upgrade_tier(case, new_tier=3, penalty_rate=0.20)
            schedule_jpj_block(case)
        elif case.tier == 3 and days_in_tier >= 60:
            upgrade_tier(case, new_tier=4)
            register_writeoff_candidate(case)
```

### 2.3 JPJ 도로세 차단 절차 (Tier 3)

```
Tier 3 진입 (D+31)
      │
      ▼
JPJ 차단 API 호출: POST https://api.jpj.gov.my/roadtax/v1/block
{
  "vehicle_plate": "WXX 1234",
  "reason": "TOLL_UNPAID",
  "reference_no": "UNPC-{case_id}",
  "blocking_authority": "JVC-BOS-v1"
}
      │ 성공
      ▼
unpaid_cases.jpj_blocked = true
jpj_block_audit 로그 기록

      │ 납부 완료
      ▼
JPJ 해제 API 호출: POST /roadtax/v1/unblock
unpaid_cases.jpj_blocked = false
```

### 2.4 알림 발송 스케줄

| Tier | 발송 시점 | 채널 | 내용 |
|------|---------|------|------|
| Tier 1 | D+1, D+4, D+7 | SMS + 이메일 + 앱 푸시 | 미납 안내, 납부 링크 |
| Tier 2 | 매주 월요일 | SMS + 이메일 | 연체 수수료 추가 경고 |
| Tier 3 | 차단 직전 1일 | SMS + 이메일 | JPJ 차단 경고 (최후 통보) |
| Tier 4 | 법적 조치 시작 전 | 우편 + 이메일 | 법적 조치 사전 고지 |

### 2.5 Write-off 기준

| 기준 | 조건 |
|------|------|
| 일반 Write-off | Tier 4 진입 후 6개월 경과 + CFO 승인 |
| 소액 즉시 Write-off | 미납 총액 < RM 10 |
| 특별 사유 Write-off | 채무자 사망 / 파산 / 차량 도난 |

Write-off 실행은 반드시 CFO 수동 승인 후에만 가능.

---

## 3. 예시 시나리오

**시나리오: RM 85 미납 — Tier 3 진입 → JPJ 차단 → 납부 완료**
1. D+31: 에스컬레이션 배치가 Tier 2→3 업그레이드
2. 연체 수수료 20% 적용: RM 85 → RM 102
3. JPJ 차단 API 호출 → 도로세 갱신 불가
4. D+35: 운전자 납부 완료 (RM 102)
5. 납부 확인 즉시 JPJ 해제 API 호출
6. `unpaid_cases.status = 'PAID'`, `jpj_blocked = false`

---

## 4. 주의사항 & 함정

- **연체 수수료는 累積이 아닌 대체 적용**: Tier 3 진입 시 10%가 20%로 교체됨 (10% + 20% = 30% 아님)
- **이의신청 시 에스컬레이션 정지**: 이의신청 접수 즉시 Tier 타이머 일시 정지
- **JPJ 차단은 법적 근거 필요**: 모든 차단 요청에 `reference_no` 포함 필수 (감사 추적)

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| JPJ API 연동 | [`../jpj-integration/SKILL.md`](../jpj-integration/SKILL.md) |
| 정산 센터 운영 | [`../clearing-center-operations/SKILL.md`](../clearing-center-operations/SKILL.md) |
| Phase 6 위반 관리 | [`../../docs/06_phases/06_phase06_violation.md`](../../docs/06_phases/06_phase06_violation.md) |
