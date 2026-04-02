---
name: clearing-center-operations
description: Clearing Center daily/monthly reconciliation procedures, JVC fee deduction, and settlement workflow
use_when:
  - Clearing Center 정산 운영 절차를 이해해야 할 때
  - 일별·월별 대사(Reconciliation) 흐름을 설계할 때
  - JVC 수수료 차감 기준과 정책을 참조해야 할 때
  - Phase 5 빌링 & 정산 개발 시
dont_use_when:
  - 결제 실패·미납 처리가 필요할 때 (payment-failure-scenarios 사용)
  - TnG Channel B 연동 세부 사항이 필요할 때 (tng-payment 사용)
---

# 정산 센터 운영

## 1. 개요

**Clearing Center**는 JVC가 운영하는 중앙 정산 허브다. 20+ 콘세셔네어의 일별 수납 집계를 받아 JVC 수수료를 차감하고, TnG Channel B 정산을 처리하며, 최종 콘세셔네어 지급액을 결정한다.

---

## 2. 핵심 내용

### 2.1 정산 센터 역할

| 기능 | 설명 | 처리 주기 |
|------|------|---------|
| Channel A 집계 | 콘세셔네어별 직접 수납 집계 확인 | 일 1회 (T+1 01:00) |
| JVC 수수료 차감 | 3~12% 수수료 차감 후 순액 산출 | 일 1회 (T+1 01:30) |
| TnG Channel B 대사 | TnG ACK와 BOS 집계 비교 | 일 1회 (T Day 23:50) |
| 콘세셔네어 지급 준비 | 순수납액 계좌이체 스케줄 | 일 1회 (T+1 08:00) |
| 월별 정산 리포트 | 월말 전체 정산 총합 확인 | 월 1회 (매월 2일) |

### 2.2 JVC 수수료 정책

| 콘세셔네어 규모 | 월 수납액 기준 | 수수료율 | 정산 주기 |
|--------------|-------------|--------|---------|
| 소규모 | < RM 1M | 12% | 월 1회 |
| 중규모 | RM 1M ~ 5M | 8% | 15일 1회 |
| 대규모 | > RM 5M | 5% | 주 1회 |
| TnG Channel B | (별도 계약) | 3% | 일 1회 |
| 정부 기관 | (별도 계약) | 0% | 월말 후불 |

> ⚠️ 수수료율은 DB `jvc_fee_rates` 테이블에서만 조회. 코드 하드코딩 금지.

### 2.3 일별 정산 흐름

```
T일 23:00 — TnG Channel B 배치 정산 (billing-service)
T+1 01:00 — Daily Aggregation Finalize (T일 집계 확정)
T+1 01:30 — JVC 수수료 차감 적용
T+1 02:00 — Clearing Reconciliation (BOS vs Clearing Center 대사)
T+1 03:00 — 정산 리포트 생성 (PDF/CSV/Excel)
T+1 08:00 — 콘세셔네어 순수납액 지급 준비 완료
```

### 2.4 대사(Reconciliation) 결과 분류

| 결과 | 의미 | 처리 |
|------|------|------|
| MATCHED | BOS ↔ Clearing 완전 일치 | 완료 처리 |
| AMOUNT_MISMATCH | 금액 불일치 (±RM 0.01 이상) | 예외 큐 → 수동 심사 |
| MISSING_IN_CLEARING | BOS 기록 있음, Clearing 없음 | 재전송 요청 |
| MISSING_IN_BOS | Clearing 기록 있음, BOS 없음 | 원본 이벤트 조회 |

수동 심사 SLA: 불일치 발생 후 **2 영업일 내** 해결

---

## 3. 예시 시나리오

**시나리오: AMOUNT_MISMATCH 발생 — RM 150.20 vs RM 148.50**
1. Clearing Reconciliation 배치가 `AMOUNT_MISMATCH` 감지
2. `reconciliation_exceptions` 테이블에 등록
3. `review-lead` Agent가 수동 심사 큐에서 확인
4. 원인 분석: JVC 수수료율 적용 오류 (0.03 vs 0.0300001 부동소수점 오차)
5. 수동 조정 정산 실행 후 `RESOLVED` 처리

---

## 4. 주의사항 & 함정

- **반올림 정책**: 수수료 계산은 반드시 `HALF_UP` 반올림, 소수점 2자리 (BigDecimal 사용)
- **TnG ACK 타임아웃**: TnG API가 60초 내 응답 없을 시 재시도 최대 3회, 실패 시 수동 처리 큐
- **월별 합산 검증**: 일별 정산 합산이 월말 집계와 일치해야 함 (월말 배치에서 검증)

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| TnG 결제 연동 | [`../tng-payment/SKILL.md`](../tng-payment/SKILL.md) |
| 결제 실패 처리 | [`../payment-failure-scenarios/SKILL.md`](../payment-failure-scenarios/SKILL.md) |
| Phase 5 빌링 | [`../../docs/06_phases/05_phase05_billing.md`](../../docs/06_phases/05_phase05_billing.md) |
| 결제 아키텍처 | [`../../docs/01_business/05_payment_architecture.md`](../../docs/01_business/05_payment_architecture.md) |
