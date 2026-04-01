# 05. Payment Architecture

**Document ID:** WAVE2-05  
**Maintained By:** Billing Lead / Finance  
**Last Updated:** 2026-04-01  
**Status:** Draft for Review

---

## Overview

Malaysia Tolling BOS는 두 가지 주요 결제 채널을 통해 통행료 징수를 관리한다:

- **Channel A (JVC/Clearing Center 기반)**: RFID/ANPR 기술을 통한 자동 인식 및 Clearing Center 연계 결제
- **Channel B (TnG 연동)**: Touch 'n Go 카드/디지털 지갑을 통한 실시간 결제

이 문서는 양 채널의 결제 흐름, 미결제 처리 프로세스, 수익 분배 모델, 그리고 법적/금융 근거를 정의한다.

---

## 1. Channel A: JVC/Clearing Center 기반 RFID/ANPR 결제

### 1.1 개요

Channel A는 **전통적인 통행료 징수 방식**으로, Lane 통과 시점에 RFID/ANPR으로 자동 인식되고, Clearing Center 계정을 통해 배후에서 정산된다.

### 1.2 Clearing Center 계정 설립

JVC는 Malaysia의 중앙 Clearing Center(예: BNM 산하 결제 기관)에 기관 계정을 설립하고 통행료 수금을 위탁한다.

**주요 계정 속성:**

| 항목 | 설명 | 예시 |
|------|------|------|
| **Clearing Center Account ID** | JVC가 보유한 고유 계정 ID | `CC-JVC-2026-001` |
| **Account Type** | 결제 기관 체계 | Toll Collection Agent |
| **Banking Partner** | 기본 정산 은행 | Maybank / CIMB |
| **Settlement Cycle** | 정산 주기 (일일/주간) | D+1 또는 T+2 |
| **Float Account** | Clearing Center 수탁 계정 (임시 보유) | JVC Float (3~7일) |
| **Settlement Account** | 최종 정산 계정 | JVC Operating Account |

**법적 근거:**
- Malaysia Bank Negara (BNM) Payment Systems Directive (PSD)
- Money Services Act 2013 (개정 2018) — Toll Collection Agent 허가
- JVC 금융기관 라이선스 (Phase 1 완료 가정)

### 1.3 결제 흐름 (상세 단계)

#### 1.3.1 통행료 징수 및 Clearing Center 과금

```
[차량 Lane 통과]
    ↓
[RFID/ANPR 인식] → 차량 번호판, 라이센스 정보 포착
    ↓
[Trip Record 생성]
    • Trip ID: TRX-20260401-000001
    • Vehicle ID / License Plate
    • Lane ID, Timestamp
    • Toll Amount: RM 6.50
    • Channel: A (RFID/ANPR)
    ↓
[Clearing Center 과금 요청]
    • Batch Processing (매 5분 또는 1시간마다)
    • Amount: RM 6.50
    • Toll Account debit
    • JVC Operating Account credit (선 적립, 추후 검증)
    ↓
[임시 정산 (Float)]
    • JVC Float Account에 자금 보유 (3~7일)
    • 미결제 확인 기간
```

#### 1.3.2 미결제 감지 및 처리 (Tier 1 ~ Tier 4)

##### Tier 1: 즉시 미결제 (Immediate Unpaid)

**조건:** 통행료 수금 실패 (Clearing Center 계정 부족, 거부 등)

| 단계 | 조치 | 책임 기관 | 기한 |
|------|------|---------|------|
| 1. Trip Record 플래깅 | Status: UNPAID_TIER1 | BOS System | Immediately |
| 2. Lane 알림 | 차량 번호판 사진 저장, Lane 디스플레이 "토큰 부족" | JVC Operations | 즉시 |
| 3. 시스템 로깅 | Unpaid_log 테이블 기록 | BOS | 즉시 |

**재시도 정책:**
- Clearing Center 자동 재시도: 24시간 내 3회
- 재시도 성공 시 → Status: PAID (확정)
- 재시도 실패 시 → Tier 2로 승격

##### Tier 2: 미결제 (30일 이상)

**조건:** Tier 1 상태에서 30일 경과

**프로세스:**

```
[Unpaid Trip 확인]
    ↓
[JPJ 조회 (Vehicle Registration Database)]
    • SPAD 표준 API 활용 (Malaysia Transport Ministry)
    • 차량 소유자 정보 조회
    • 라이센스 상태 확인
    ↓
[소유자 통지]
    • SMS 발송: "RM 6.50 통행료 미결제. 7일 내 결제 바랍니다."
    • Email 발송: 청구서 (Invoice) 상세
    • Portal 알림: BOS Owner Portal에 통지 등록
    ↓
[추심 시작]
    • 15일 경과: 최종 통지 (Final Notice)
    • 30일 경과: Tier 3 승격
```

**법적 근거:**
- Road Transport Act 1987 — 미결제 통행료 추심 권한
- Personal Data Protection Act 2010 (PDPA) — 개인정보 조회 동의

**책임 기관:**
- JVC: 소유자 통지 & 청구
- JPJ (Malaysia Road Transport Department): 차량 정보 제공

##### Tier 3: 법적 절차 (Legal Action)

**조건:** Tier 2에서 30일 경과 (총 60일 미결제)

| 조치 | 세부 사항 | 기한 |
|------|---------|------|
| 법무팀 검토 | 청구서 & 미결제 기록 문서화 | 60일 경과 시점 |
| 최종 독촉장 | 변호사 명의 법적 통지 | 70일 경과 |
| 법원 소송 제기 | Small Claims Court (RM 5,000 이하) | 90일 경과 |
| 강제 집행 | Vehicle Boot / License Suspension (JPJ 연계) | 120일 경과 |

**법적 근거:**
- Small Claims Court Act 1981 (RM 5,000 이하 민사소송)
- Enforcement of Judgments Act 1956 (강제 집행)
- Road Transport Act 1987 § 118 (라이센스 정지 권한)

##### Tier 4: 포기 (Write-off)

**조건:** Tier 3에서 6개월 경과, 회수 불가능 판정

| 조치 | 세부 사항 |
|------|---------|
| 회수 불가 판정 | Legal Team & Finance approval |
| 회계 처리 | Bad Debt Allowance 기록 (조세 감면) |
| System 기록 | Unpaid_log.status = 'WRITTEN_OFF' |
| 보고 | 분기별 금융 보고서 반영 |

---

### 1.4 미결제 처리 흐름도

```
┌─────────────────────────────────────────────────────────────────┐
│ CHANNEL A UNPAID PROCESSING FLOW                                 │
└─────────────────────────────────────────────────────────────────┘

         TRX 발생 (RFID/ANPR)
                ↓
    ┌───────────────────────┐
    │ Clearing Center 과금   │
    │ (자동 결제 시도)      │
    └───────────────────────┘
           ↓         ↑
    [성공] │         │ [실패]
         │         │
         ↓         ↓
      PAID     UNPAID_TIER1
              (즉시 미결제)
                   ↓
             [24시간 재시도]
                ↓
        ┌───────────────────┐
        │ 재시도 성공? (3회) │
        └───────────────────┘
           ↓         ↓
         YES       NO
          │        │
       PAID    [30일 경과]
              UNPAID_TIER2
                   ↓
           [JPJ 조회 & 통지]
           [추심 시작]
                   ↓
              [30일 경과]
           UNPAID_TIER3
                   ↓
          [법적 절차 시작]
          [변호사 독촉장]
          [소송/강제집행]
                   ↓
              [6개월 경과]
              or 회수 불가
                   ↓
           WRITTEN_OFF
         (회계 처리 & 제거)
```

---

## 2. Channel B: TnG (Touch 'n Go) 연동

### 2.1 개요

Channel B는 **TnG 카드/디지털 지갑 기반 결제**로, 차량 RFID 인식 후 실시간 또는 배치 방식으로 TnG 계정에서 차감된다.

**주요 특징:**
- TnG와 JVC 간 API 연동 (기존 PLUS Toll과 유사)
- 실시간 결제 또는 일일 배치 정산
- TnG 미결제: 별도 정책 (RnR — Retention & Reconciliation 조건)

### 2.2 TnG 결제 신청 프로세스

#### 2.2.1 TnG API 연동 (개략)

```
[Lane RFID 인식]
    ↓
[Trip Record 생성]
    • Trip ID
    • Vehicle Tag ID (TnG associated)
    • Amount: RM 6.50
    ↓
[TnG API 호출 (실시간 또는 배치)]
    POST /api/v2/toll/debit
    {
      "tag_id": "TNG-ABC123456",
      "amount": 6.50,
      "toll_id": "JVC-LANE-001",
      "reference": "TRX-20260401-000001"
    }
    ↓
[TnG Response]
    • Success: 200 OK, "balance_remaining": 45.30
    • Insufficient: 402, "balance": 2.50 (부족)
    • Error: 500, retry policy
    ↓
[Result 기록]
    • Channel B 트랜잭션 완료 또는 실패
```

#### 2.2.2 결제 신청 및 정산 흐름

| Phase | 상세 | 시점 |
|-------|------|------|
| **Phase 1: 실시간 청구** | Trip 발생 시 TnG API 호출, 결과 수신 | Trip 발생 후 <10초 |
| **Phase 2: 일일 정산** | 정산 배치: 전일 Trip 합계 vs TnG 차감액 검증 | 자정 UTC+8 |
| **Phase 3: 주간 Reconciliation** | 주간 거래액 비교 & 차이 분석 | 매주 월요일 06:00 |
| **Phase 4: TnG↔JVC 정산** | TnG 은행 계정 → JVC Operating Account 송금 | T+2 (영업일 기준) |

### 2.3 TnG↔JVC 정산 시점

**정산 일정:**

| 정산 주기 | 시간 | 담당 기관 | 기준 |
|----------|------|---------|------|
| **일일 정산** | 매일 02:00 (UTC+8) | BOS System | 전일 전체 Channel B 거래액 |
| **주간 Reconciliation** | 월 06:00 | BOS + TnG Joint Team | 거래액 오차율 <0.01% |
| **월간 지급** | 매월 15일 | TnG Finance | 전월 순 수금액 |

**지급 구조:**

```
[월간 집계]
총 Channel B 수금액: RM 500,000
- TnG Commission (2%): RM 10,000
- Card Network Fee (0.5%): RM 2,500
- Processing Fee (0.3%): RM 1,500
─────────────────────────
JVC 수취액: RM 486,000
    ↓
[T+2 송금]
TnG Operating Bank Account
→ JVC Operating Account
금액: RM 486,000
```

### 2.4 TnG 미결제 처리 (RnR Condition)

**정의:** TnG 계정에 잔액 부족으로 결제 실패한 경우

**처리 정책 (Retention & Reconciliation):**

```
[TnG 결제 실패]
Status: TNG_INSUFFICIENT_BALANCE
    ↓
[JVC Retry Policy]
    • 1차 재시도: 1시간 후
    • 2차 재시도: 4시간 후
    • 3차 재시도: 24시간 후
    ↓
[재시도 모두 실패]
    → Channel A (JPJ/Clearing) 폴백
    (해당 차량이 Clearing 계정 가능한 경우)
    ↓
[Channel A 폴백도 실패]
    → Tier 1 미결제로 전환 (Clearing Center 기준 처리)
```

**특수 조건:**

- **RnR Window:** 영업일 기준 5일 내 추가 결제 시도
- **RnR Retention:** TnG 수수료 발생 X (재시도 비용 TnG 부담)
- **TnG Owner 통지:** TnG Portal → Push Notification (자동)

---

## 3. 결제 흐름도 (통합)

```
┌─────────────────────────────────────────────────────────────────┐
│ INTEGRATED PAYMENT FLOW (CHANNEL A + B)                          │
└─────────────────────────────────────────────────────────────────┘

                    [Lane RFID/ANPR 인식]
                            ↓
              ┌─────────────────────────────┐
              │ 차량 Tag 정보 확인          │
              │ • Clearing Account?         │
              │ • TnG Card?                 │
              │ • Both?                     │
              └─────────────────────────────┘
                    ↓
        ┌─────────────────────────────────┐
        │ Channel 선택 로직               │
        └─────────────────────────────────┘
         /         |         \
        /          |          \
    [Clearing]  [TnG]      [기타]
       (A)        (B)      (Manual)
        ↓          ↓          ↓
    ┌────────┐  ┌────────┐  ┌──────────┐
    │Debit   │  │Debit   │  │Pending   │
    │Clear   │  │TnG API │  │Manual    │
    │Account │  │        │  │Payment   │
    └────────┘  └────────┘  └──────────┘
      ↓            ↓            ↓
   [성공]      ┌─성공?─┐    [처리 대기]
    │          │       │
   ↓         YES     NO
[PAID]        │       │
             ↓       ↓
           [PAID] [RETRY]
                      ↓
                  [재시도 3회]
                      ↓
                    ┌─성공?─┐
                   YES    NO
                    │      │
                   ↓      ↓
                [PAID] [FAIL→
                          UNPAID
                          TIER1]
                       ↓
                  [JPJ Lookup]
                  [추심 프로세스]
```

---

## 4. 수익 분배 모델

### 4.1 수수료 체계

#### 4.1.1 JVC 수수료 (Channel A)

JVC는 Clearing Center를 통한 결제 처리에 대해 수수료를 납부한다.

**수수료율:**

| 항목 | 수수료율 | 비고 |
|------|---------|------|
| **Clearing Center Fee** | 1~2% | BNM 산하 결제 기관 |
| **Banking Partner Fee** | 0.5~1% | Maybank/CIMB 정산 수수료 |
| **JVC Processing Fee** | 1~1.5% | BOS System 운영비 |
| **JPJ Inquiry Fee** | RM 0.10/건 | 미결제 차량 조회 |
| **Legal/Collection Fee** | 2~5%* | Tier 3 이상 진행 시 (변호사 비용) |
| **총 수수료율** | **3~12%** | Board 결정 (G-HARD 0) |

*최종 수수료율은 Board가 결정하며, 시장 경쟁력과 운영 비용을 고려한다.

#### 4.1.2 TnG 수수료 (Channel B)

TnG는 결제 중개 기관으로서 고정 수수료 + 변동 수수료를 징수한다.

**TnG 수수료:**

| 항목 | 수수료율 | 기준 |
|------|---------|------|
| **Transaction Fee** | 2.0% | 거래액 기준 |
| **Card Network Fee** | 0.5% | Visa/Mastercard (TnG 가맹점 기준) |
| **Settlement Fee** | 0.3% | T+2 정산 수수료 |
| **RnR Retention** | 0.2% | 재시도 비용 (미결제 건) |
| **총 TnG 수수료** | **3.0%** | 거래액 기준 |

**JVC 수취액:**

```
Channel B 수금액: RM 1,000,000
- TnG 수수료 (3.0%): RM 30,000
- Card Network Fee (0.5%): RM 5,000
- Processing Fee (0.3%): RM 3,000
─────────────────────────
JVC 수취액: RM 962,000
```

### 4.2 월간 수익 분배 예시

**가정:**
- 월간 총 통행료 수금: RM 2,000,000
- Channel A (Clearing): 70% = RM 1,400,000
- Channel B (TnG): 30% = RM 600,000

**분배 시뮬레이션:**

| Channel | 수금액 | 수수료율 | 수수료액 | JVC 수취액 |
|---------|--------|---------|---------|-----------|
| A (Clearing) | RM 1,400,000 | 5% | RM 70,000 | RM 1,330,000 |
| B (TnG) | RM 600,000 | 3% | RM 18,000 | RM 582,000 |
| **합계** | **RM 2,000,000** | — | **RM 88,000** | **RM 1,912,000** |

**수취 흐름:**

```
Clearing Center
→ JVC Operating Account: RM 1,330,000 (D+1)

TnG Operating Account
→ JVC Operating Account: RM 582,000 (T+2, 월 15일)

JVC Finance:
- Operating: RM 1,912,000
- Reserve Fund (1%): RM 20,000
- Operational Expense: RM 50,000
- Net: RM 1,842,000
```

### 4.3 TOC (Toll Operating Company) 정산

**정의:** JVC가 Toll Road 소유자(예: LLM, PLUS 운영사)에게 지급해야 할 의무금

**TOC 정산 구조:**

```
JVC 순 수취액: RM 1,912,000
    ↓
[TOC 기여금 차감]
(계약상 고정비 또는 변동비)
    • Fixed: RM 100,000/월
    • Variable: 수금액의 1.5%
      RM 1,912,000 × 1.5% = RM 28,680
    ↓
[TOC 지급액]
RM 100,000 + RM 28,680 = RM 128,680
    ↓
[JVC 최종 수익]
RM 1,912,000 - RM 128,680 = RM 1,783,320
```

**지급 일정:**
- 월간 수금액 정산: 월말 T+5
- TOC 지급: 익월 10일
- 보고: 분기별 재무 리포트

---

## 5. 미결제 처리 상세 프로세스

### 5.1 Tier별 책임 및 SLA

| Tier | 기간 | 상태 | 책임 기관 | SLA | 조치 |
|------|------|------|---------|-----|------|
| **Tier 1** | 0~24h | UNPAID_TIER1 | BOS Auto Retry | <10초 결과 전달 | 자동 재시도 3회 |
| **Tier 2** | 24h~30d | UNPAID_TIER2 | JVC + JPJ | 7일 내 통지 | JPJ 조회 & 소유자 통지 |
| **Tier 3** | 30d~120d | UNPAID_TIER3 | JVC Legal | 10일 내 독촉장 | 법적 절차 개시 |
| **Tier 4** | 120d+ | WRITTEN_OFF | JVC Finance | 6개월 판정 | 회계 처리 & 제거 |

### 5.2 미결제 통지 템플릿

**Tier 2 SMS 통지:**

```
[JVC TOLL] 차량번호 ABC1234의 통행료 RM 6.50이 미결제되었습니다. 
7일 내 결제 부탁드립니다. 
결제: https://bos.jvc.my/payment/TRX-20260401-000001 
또는 Clearing Account 충전 문의: +60-1234-5678
```

**Tier 2 Email 통지:**

```
Subject: 통행료 미결제 청구서 - 차량 ABC1234

송금인: JVC Malaysia
차량: ABC1234
거래일: 2026-04-01 14:23:45
거래액: RM 6.50
거래ID: TRX-20260401-000001
Lane: KUALA LUMPUR NORTH #5

결제 방법:
1. TnG 카드 충전 (https://tng.my)
2. Clearing Center 계정 송금 (Account: CC-JVC-2026-001)
3. 온라인 결제: https://bos.jvc.my

기한: 2026-04-08 23:59:59
미납 시 법적 조치가 진행될 수 있습니다.

---
JVC Malaysia Finance Team
```

### 5.3 미결제 통계 & 모니터링

**월간 KPI:**

```
Unpaid_Tier1 건수: 
→ 목표: <0.5% of total transactions
→ Alert: >1%

Unpaid_Tier2→Tier3 전환율:
→ 목표: 70% (정산율)
→ Alert: <50%

Tier 3 회수율:
→ 목표: 80% (법적 조치 효과)
→ Alert: <60%

Write-off Rate:
→ 목표: <1% of total unpaid
→ Alert: >2%
```

---

## 6. 외부 기관 연계

### 6.1 JPJ (Malaysia Road Transport Department) 연동

**목적:** 미결제 차량의 소유자 정보 조회

**연동 방식:**

| 항목 | 명세 |
|------|------|
| **API Endpoint** | `https://jpj.gov.my/api/v1/vehicle/inquiry` |
| **인증** | OAuth 2.0 (JVC 서비스 계정) |
| **조회 항목** | 차량번호판 → 소유자명, 주소, 연락처, 라이센스 상태 |
| **응답 시간** | <5초 (동기식) |
| **호출 주기** | Tier 2 진입 시 1회 (24시간 내) |
| **비용** | RM 0.10/조회 |
| **법적 근거** | Road Transport Act 1987 § 53 |

**샘플 Request/Response:**

```json
[Request]
POST /api/v1/vehicle/inquiry
{
  "license_plate": "ABC1234",
  "country": "MY",
  "auth_token": "JWT_TOKEN_HERE"
}

[Response - Success]
{
  "status": 200,
  "vehicle": {
    "license_plate": "ABC1234",
    "owner_name": "Ahmad Bin Abdul",
    "owner_address": "123 Jalan Merdeka, 50050 KL",
    "phone": "+60123456789",
    "email": "ahmad@example.my",
    "license_status": "ACTIVE",
    "expiry_date": "2027-12-31"
  }
}

[Response - Not Found]
{
  "status": 404,
  "error": "Vehicle not found or invalid plate"
}
```

### 6.2 TnG API 연동 (기존 PLUS 유사)

**목적:** TnG 카드 결제 & 잔액 조회

**기술 명세는** [**02_system/05_external_integration.md**](../02_system/05_external_integration.md)를 참조.

---

## 7. 법적 & 규제 근거

### 7.1 적용 법규

| 법규 | 관련 조항 | 적용 범위 |
|------|---------|---------|
| **Road Transport Act 1987** | § 53, § 118 | 차량정보 조회, 라이센스 정지 권한 |
| **Money Services Act 2013** | § 10~25 | Toll Collection Agent 허가 & 운영 |
| **Payment Systems Directive (BNM)** | PSD 2024 | Clearing Center 정산 규범 |
| **Personal Data Protection Act 2010** | § 32~40 | 개인정보 조회 & 보호 의무 |
| **Small Claims Court Act 1981** | § 1~40 | RM 5,000 이하 소송 절차 |
| **Enforcement of Judgments Act 1956** | § 1~30 | 강제 집행 절차 |
| **Goods and Services Tax Act 2014** | § 1~50 | 통행료 세무 처리 |

### 7.2 컴플라이언스 체크리스트

**운영 시작 전 필수 확인 사항:**

- [ ] JVC Toll Collection Agent 라이선스 취득 (Money Services Act)
- [ ] Clearing Center 계정 설립 (BNM 승인)
- [ ] TnG API 연동 계약 체결 (기술 & 금융 조항)
- [ ] JPJ 데이터 조회 MOU 체결 (PDPA 준수)
- [ ] 개인정보보호 정책 수립 및 공시 (PDPA)
- [ ] 법무팀 독촉장 & 소송 프로세스 정의
- [ ] 감사(Audit) 준비: 월간 정산 기록 & 통제

---

## 8. 의사결정 게이트 (G-HARD)

### 8.1 Board 결정 사항

현재 문서에 영향을 미치는 Board 결정 (G-HARD 0):

| 결정 ID | 항목 | 상태 | 비고 |
|---------|------|------|------|
| **G-HARD 0-01** | JVC 수수료율 (3~12% 범위 내 확정) | Pending | Finance Lead 제안 예상 |
| **G-HARD 0-02** | Clearing Center 정산 주기 (일일 vs 주간) | Pending | Operations Lead 협의 |
| **G-HARD 0-03** | TnG 연동 우선순위 (MVP Phase vs Phase 4) | Pending | CIO 의사결정 |
| **G-HARD 0-04** | 미결제 Tier 3 법적 조치 위임 (내부 vs 외부 법무) | Pending | Legal Review |
| **G-HARD 0-05** | JPJ API 이용료 예산 및 SLA | Pending | Operations & JPJ MOU |

### 8.2 승인 요구사항

이 문서의 최종 승인을 위해서는:

- [ ] **CEO**: 전략적 방향성 & 재무 영향 검토
- [ ] **CFO**: 수익 분배 모델 & 예산 타당성
- [ ] **CIO/CTO**: 기술 연동 (API, Integration) 검토
- [ ] **Legal**: 법적 근거 & 컴플라이언스 확인
- [ ] **Compliance**: PDPA & 규제 요구사항 검증

---

## 9. 부록: 용어 정의

| 용어 | 정의 | 예시 |
|------|------|------|
| **Channel A** | Clearing Center 기반 결제 (RFID/ANPR) | 대부분의 일반 차량 |
| **Channel B** | TnG 카드 기반 결제 (실시간) | TnG 가입자 |
| **Trip Record** | 통행료 거래 한 건의 기록 | TRX-20260401-000001 |
| **Clearing Center** | 중앙 결제 기관 (BNM 산하) | Malaysia Payment Systems |
| **JPJ** | Jabatan Pengangkutan Jalan (Road Transport Dept) | 차량 등록청 |
| **RnR** | Retention & Reconciliation (재시도 정책) | TnG 미결제 5일 추가 시도 |
| **TOC** | Toll Operating Company (Toll Road 소유자) | LLM, PLUS, etc. |
| **Unpaid Tier 1~4** | 미결제 단계별 분류 | 즉시 → 법적 → 포기 |
| **Float Account** | 임시 자금 보유 계정 (3~7일) | Clearing Center 수탁 |
| **Write-off** | 회계상 미수금 제거 | Bad Debt Allowance |

---

## 10. 참고 문서

이 문서와 연계된 설계 문서:

- [01_project_charter.md](./01_project_charter.md) — 프로젝트 목적 & MVP 범위
- [02_market_malaysia.md](./02_market_malaysia.md) — TnG/PLUS 경쟁 분석
- [03_domain_tolling.md](./03_domain_tolling.md) — 통행료 징수 구조 기초
- [04_organization_roles.md](./04_organization_roles.md) — Billing 팀 조직 구조
- [02_system/02_service_domains.md](../02_system/02_service_domains.md) — Transaction & Billing Domain
- [02_system/05_external_integration.md](../02_system/05_external_integration.md) — JPJ, TnG API 상세 스펙
- [03_data/02_data_model.md](../03_data/02_data_model.md) — Unpaid 트랜잭션 테이블 정의
- [05_governance/02_board_decisions.md](../05_governance/02_board_decisions.md) — 21개 Board 결정 전체

---

## 11. 버전 관리

| 버전 | 날짜 | 주요 변경 사항 | 작성자 |
|------|------|--------------|--------|
| v0.1 | 2026-04-01 | 초안 작성 | Billing Lead |
| — | — | — | — |

---

**문서 상태:** Draft  
**다음 검토:** Board Decision (G-HARD 0-01 ~ 0-05) 이후  
**예상 확정:** 2026-04-15
