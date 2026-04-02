---
name: malaysia-tolling-domain
description: Malaysia SLFF/MLFF tolling domain overview — concessionaires, JPJ regulations, Channel A/B structure
use_when:
  - 말레이시아 톨링 시스템의 비즈니스 구조를 이해해야 할 때
  - 콘세셔네어 체계, Channel A/B, JPJ 규제를 참조해야 할 때
  - SLFF(전통 톨링)와 MLFF(다차선 자유통행) 차이를 설명해야 할 때
  - 신규 Agent가 프로젝트에 온보딩될 때 (가장 먼저 로드)
dont_use_when:
  - 특정 기술 구현 세부사항이 필요할 때 (rfid-anpr-interface 또는 mlff-session-matching 사용)
  - 결제 실패 처리가 필요할 때 (payment-failure-scenarios 사용)
---

# 말레이시아 톨링 도메인

## 1. 개요

Malaysia SLFF/MLFF Tolling BOS는 **JVC(Joint Venture Company)**가 운영하는 고속도로 톨링 백오피스 시스템이다. 말레이시아 전국 콘세셔네어사(Concessionaire)들의 톨링 데이터를 수집·정산·감사·보고하는 중앙 허브 역할을 한다.

**시스템 범위:**
- SLFF (Single Lane Free-Flow): 단일 차선, 기존 톨게이트 RF 태그 방식
- MLFF (Multi-Lane Free-Flow): 다차선, 감속 없이 통과하는 자유통행 방식

---

## 2. 핵심 내용

### 2.1 시장 구조

```
[JPJ (정부 규제기관)]
       │ 면허·감독
       ▼
[JVC (Joint Venture Company)] ← BOS 운영 주체
       │
       ├─ 콘세셔네어 A (PLUS Expressways)
       ├─ 콘세셔네어 B (LEKAS)
       ├─ 콘세셔네어 C (SILK)
       └─ ... (총 20+ 콘세셔네어)
```

### 2.2 결제 채널 구조

| 채널 | 명칭 | 방식 | 정산 주기 | JVC 수수료 |
|------|------|------|---------|----------|
| Channel A | 직접 결제 | TnG RFID 태그 → 콘세셔네어 직접 정산 | 일 1회 | 5~12% |
| Channel B | TnG eWallet | TnG 선불 지갑 → TnG → JVC → 콘세셔네어 | 일 1회 배치 | 3% |

### 2.3 차량 등급 (Vehicle Class)

| 등급 | 설명 | 요금 배수 |
|------|------|---------|
| Class 1 | 승용차 (Motorcycles) | 0.5x |
| Class 2 | 경라이트 트럭 (Car/Jeep/Taxi) | 1.0x (기준) |
| Class 3 | 중형 트럭 5축 이하 | 1.5x |
| Class 4 | 대형 트럭 5축 초과 | 2.0x |
| Class 5 | 특수 차량 | 협의 |

### 2.4 JPJ 규제 핵심 사항

- **차량 등록 조회**: 모든 ANPR 기반 차량 식별은 JPJ 차량 DB 조회 필요
- **도로세(Road Tax)**: 미납 지속 시 JPJ API를 통해 도로세 갱신 차단 가능
- **TOC(Toll Operator Certificate)**: 외부 시스템 데이터 접근을 위한 JVC 인증서
- **데이터 현지화**: 모든 톨링 데이터는 Malaysia 내 데이터 센터 보관 의무 (BNM 규정)

### 2.5 주요 이해관계자

| 이해관계자 | 역할 | BOS 접근 권한 |
|-----------|------|-------------|
| JVC (운영사) | BOS 소유 및 운영 | 전체 관리자 |
| 콘세셔네어 | 고속도로 운영사 | 자사 데이터 열람 |
| JPJ | 정부 규제기관 | 차단/해제 신청 수신 |
| TnG | 결제 파트너 | Channel B 정산 API |
| TOC | 외부 제3자 | PUSH/PULL API 사용 |

---

## 3. 예시 시나리오

**시나리오: 콘세셔네어가 "우리 이번 달 수납액이 얼마야?" 질문**
1. `reporting-lead` Agent가 `text-to-sql-engine` Skill 로드
2. 콘세셔네어 ID로 `agg_monthly_summary` 조회
3. Channel A/B 구분하여 합산
4. 결과를 콘세셔네어 포털 대시보드에 표시

---

## 4. 주의사항 & 함정

- **콘세셔네어 격리**: 콘세셔네어 A가 콘세셔네어 B의 데이터를 볼 수 없다. PostgreSQL RLS 필수 (`rbac-data-boundary` 참조)
- **Channel B 수수료는 3% 고정**: 계약상 고정값이므로 코드에 하드코딩 금지 (DB 마스터 테이블에서만 조회)
- **MLFF는 Entry-Exit 페어 필수**: 단독 진입 이벤트는 미완성 세션으로 처리 (`mlff-session-matching` 참조)
- **JPJ API 비용**: 차량 조회당 RM 0.10 과금. 불필요한 중복 조회 방지 (Redis 캐시 필수)

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 전통 톨링 역할 | [`traditional-tolling-roles/SKILL.md`](../traditional-tolling-roles/SKILL.md) |
| 시장 상세 | [`../../docs/01_business/02_market_malaysia.md`](../../docs/01_business/02_market_malaysia.md) |
| 도메인 설계 | [`../../docs/01_business/03_domain_tolling.md`](../../docs/01_business/03_domain_tolling.md) |
| 결제 아키텍처 | [`../../docs/01_business/05_payment_architecture.md`](../../docs/01_business/05_payment_architecture.md) |
