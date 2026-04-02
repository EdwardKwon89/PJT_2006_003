---
name: traditional-tolling-roles
description: Traditional toll plaza operational roles — plaza manager, field technician, supervisor responsibilities
use_when:
  - 플라자 운영 인력의 역할과 책임을 참조해야 할 때
  - 현장 장비 점검·유지보수 절차가 필요할 때
  - 시스템 전환(SLFF→MLFF) 시 운영 인력 재배치 계획 수립 시
dont_use_when:
  - 기술적 시스템 구현이 필요할 때 (rfid-anpr-interface 사용)
  - 비즈니스 도메인 전반을 이해해야 할 때 (malaysia-tolling-domain 먼저 로드)
---

# 전통 톨링 운영 역할

## 1. 개요

SLFF/MLFF 전환 과정에서 기존 플라자 인력을 BOS 기반 운영 체계로 통합하는 것이 핵심 과제다. 본 Skill은 **전통 톨링 운영 인력 역할 정의**와 **BOS 통합 후 역할 변화**를 다룬다.

---

## 2. 핵심 내용

### 2.1 전통 운영 역할 체계

| 역할 | 한국어 | 주요 책임 | BOS 접근 권한 |
|------|--------|---------|-------------|
| Plaza Manager | 플라자 관리자 | 일별 운영 총괄, 보고서 승인 | 플라자 데이터 읽기·쓰기 |
| Shift Supervisor | 교대 감독자 | 교대조 관리, 이상 상황 보고 | 플라자 데이터 읽기 |
| Toll Collector | 수납원 | 현금 수납, 이의신청 접수 | SLFF 전용 (수납 메뉴만) |
| Field Technician | 현장 기술자 | 장비 점검·수리, RFID/ANPR 교정 | 장비 상태 읽기·쓰기 |
| Back Office Clerk | 사무직원 | 정산 검증, 미납 처리 보조 | 정산 데이터 읽기 |

### 2.2 일일 운영 루틴

```
06:00 — 교대 시작: Shift Supervisor 인수인계 체크리스트 확인
06:30 — 장비 점검: Field Technician RFID/ANPR 상태 확인
07:00 — 전일 정산 보고서 검토 (Plaza Manager)
12:00 — 중간 집계 확인 (Shift Supervisor)
22:00 — 교대 종료: 일별 수납 집계 마감 서명
23:00 — TnG Channel B 배치 정산 자동 실행 (BOS 배치)
```

### 2.3 MLFF 전환 후 역할 변화

| 역할 | SLFF 시대 | MLFF 전환 후 |
|------|-----------|------------|
| Toll Collector | 현금 수납 수행 | 이의신청 처리 전담 (현금 수납 없음) |
| Field Technician | 차단기·부스 유지 | Camera/RSU 교정, 네트워크 유지 |
| Plaza Manager | 수납원 관리 | 데이터 품질 모니터링, 이상 보고 |

### 2.4 이의신청 처리 절차 (현장 운영)

```
고객 현장 접수
      │
      ▼
Back Office Clerk: BOS 이의신청 등록
      │ (dispute API 호출)
      ▼
Shift Supervisor: 증빙 자료 확인 (CCTV, RFID 로그)
      │
      ▼
Plaza Manager: 이의신청 승인/기각 결정
      │
      ▼
BOS 자동 처리 (미납 취소 또는 에스컬레이션 재개)
```

---

## 3. 예시 시나리오

**시나리오: 고객이 "나 톨 요금 낸 적 없는데 미납 통보 받았어요" 민원 제기**
1. Back Office Clerk가 `violation-service` 이의신청 API 호출
2. Shift Supervisor가 해당 시간대 RFID 로그 및 CCTV 확인
3. Plaza Manager가 BOS에서 이의신청 승인 처리
4. BOS 자동으로 미납 상태 취소 및 고객 SMS 발송

---

## 4. 주의사항 & 함정

- **MLFF 환경에서 Toll Collector=이의신청 처리자**: 기존 수납 업무 대신 고객 응대/이의신청 처리가 주 업무
- **현장 운영 인력 BOS 접근은 최소 권한 원칙**: Plaza Manager도 자신의 플라자 데이터만 접근 가능 (`rbac-data-boundary` 참조)

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 도메인 개요 | [`../malaysia-tolling-domain/SKILL.md`](../malaysia-tolling-domain/SKILL.md) |
| 결제 실패 처리 | [`../payment-failure-scenarios/SKILL.md`](../payment-failure-scenarios/SKILL.md) |
| 조직 & 역할 문서 | [`../../docs/01_business/04_organization_roles.md`](../../docs/01_business/04_organization_roles.md) |
