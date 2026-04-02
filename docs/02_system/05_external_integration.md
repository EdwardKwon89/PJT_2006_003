# 외부 API 연동 명세
## 02_system/05_external_integration.md
## v1.0 | 2026-04 | 참조: 01_system_overview.md, 02_service_domains.md

---

> **Agent 사용 지침**
> Integration Lead, Backend Lead Agent가 외부 연동 구현 시 반드시 로드.
> 신규 외부 연동 추가 또는 기존 연동 변경 전 이 문서 필수 확인.
> 외부 연동 장애 발생 시 섹션 7(공통 연동 패턴)의 Circuit Breaker 설정 우선 점검.

---

## 1. Executive Summary — 외부 연동 전체 현황

Malaysia SLFF/MLFF Tolling BOS는 **4개 외부 시스템**과 연동하며, TOC(콘세셔네어)에게는 읽기 전용 REST API를 제공한다.

```
연동 방향 기준:
  Inbound  — 외부 → BOS (데이터 수신)
  Outbound — BOS → 외부 (데이터 요청·전송)
  Bidirectional — 양방향
```

### 1.1 외부 연동 전체 표

| # | 연동 대상 | 방향 | 인증 방식 | 프로토콜 | 주요 용도 | 담당 서비스 |
|---|-----------|------|-----------|----------|-----------|------------|
| 1 | JPJ (Jabatan Pengangkutan Jalan) | Outbound | OAuth 2.0 (Client Credentials) | REST/HTTPS | 차량 등록 조회, 도로세(road tax) 차단 요청 | account-service, violation-service |
| 2 | TnG (Touch 'n Go) | Bidirectional | OAuth 2.0 (Client Credentials) | REST/HTTPS | Channel B 결제 승인·정산·대사 | billing-service, txn-service |
| 3 | FPX (Financial Process Exchange) | Bidirectional | TLS Mutual Auth + API Key | REST/HTTPS | 온라인 결제 게이트웨이 (미납 수납) | billing-service, unpaid-service |
| 4 | ANPR Vendor | Inbound | mTLS + Service Account | gRPC 스트리밍 | 번호판 인식 이벤트 수신 | txn-service, review-service |
| 5 | TOC (Toll Operating Company) | Outbound (BOS→TOC) | API Key + IP Whitelist | REST/HTTPS | 운영 데이터 제공 (읽기 전용) | api-service |

### 1.2 공통 연동 원칙

```
① 모든 외부 연동은 HashiCorp Vault에서 자격증명 동적 발급 (소스코드 하드코딩 금지)
② Circuit Breaker (Resilience4j) 적용 — 외부 장애 시 BOS 내부 영향 최소화
③ Exponential Backoff 재시도 (최대 3회, 초기 지연 1초, 배율 2.0)
④ 모든 외부 호출 OpenTelemetry 추적 (Jaeger) — 연동 SLA 실시간 모니터링
⑤ 외부 API 변경 시 최소 3개월 사전 공지 요구 (계약 조항)
```

---

## 2. JPJ 연동 상세

### 2.1 연동 목적

JPJ(Jabatan Pengangkutan Jalan, 말레이시아 육상교통부)는 차량 등록 정보와 도로세(road tax) 납부 상태를 관리하는 국가 기관이다. BOS는 두 가지 목적으로 JPJ와 연동한다.

| 목적 | 설명 | 트리거 |
|------|------|--------|
| 차량 등록 조회 | 번호판으로 차량 소유주·등록 정보 확인 | ANPR 인식, 위반 처리, 계정 등록 시 |
| 도로세 차단 요청 | 미납 Tier 3 이상 차량의 road tax 갱신 차단 | 미납 Tier 3 진입 시 자동 요청 |

### 2.2 API 엔드포인트 목록

| Method | 엔드포인트 | 설명 | 담당 서비스 |
|--------|-----------|------|------------|
| GET | `/api/v2/vehicle/{plate}` | 번호판으로 차량 등록 정보 조회 | account-service |
| GET | `/api/v2/vehicle/{plate}/roadtax` | 도로세 납부 상태 조회 | violation-service |
| POST | `/api/v2/vehicle/{plate}/roadtax/block` | 도로세 갱신 차단 요청 | unpaid-service |
| DELETE | `/api/v2/vehicle/{plate}/roadtax/block` | 도로세 차단 해제 (미납 완납 후) | unpaid-service |

> **주의:** 위 엔드포인트는 JPJ API 문서 기준 추정값이며, 실제 연동 계약 체결 후 JPJ 공식 명세로 업데이트 필요.

### 2.3 요청/응답 스키마

#### 차량 등록 조회 — GET `/api/v2/vehicle/{plate}`

**Request:**
```json
{
  "headers": {
    "Authorization": "Bearer {access_token}",
    "X-Request-ID": "uuid-v4",
    "X-Source-System": "BOS-MLFF",
    "Accept": "application/json"
  },
  "path": {
    "plate": "WXY1234"
  }
}
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": {
    "plate_number": "WXY1234",
    "vehicle_class": "CLASS_1",
    "vehicle_type": "PRIVATE_CAR",
    "make": "PROTON",
    "model": "SAGA",
    "year": 2022,
    "engine_cc": 1332,
    "owner": {
      "ic_number": "XXXXX-XX-XXXX",
      "name": "REDACTED",
      "address_state": "Selangor"
    },
    "registration_status": "ACTIVE",
    "roadtax_expiry": "2025-12-31",
    "roadtax_blocked": false
  },
  "request_id": "uuid-v4",
  "timestamp": "2026-04-01T08:00:00+08:00"
}
```

#### 도로세 차단 요청 — POST `/api/v2/vehicle/{plate}/roadtax/block`

**Request Body:**
```json
{
  "reason": "TOLL_UNPAID_TIER3",
  "reference_id": "UNPAID-2026-0001234",
  "outstanding_amount": 125.50,
  "currency": "MYR",
  "bos_contact": "enforcement@jvc-bos.my",
  "requested_by": "unpaid-service@bos-internal"
}
```

**Response (201 Created):**
```json
{
  "status": "success",
  "data": {
    "block_reference": "JPJ-BLOCK-2026-0009876",
    "plate_number": "WXY1234",
    "blocked_at": "2026-04-01T08:05:00+08:00",
    "estimated_effect_date": "2026-04-02T00:00:00+08:00"
  }
}
```

### 2.4 오류 처리 & Fallback

| HTTP 코드 | JPJ 오류 코드 | 의미 | BOS 처리 |
|-----------|--------------|------|---------|
| 404 | `VEHICLE_NOT_FOUND` | 번호판 미등록 | 수동 심사 큐 이관 (review-service) |
| 409 | `BLOCK_ALREADY_EXISTS` | 이미 차단됨 | 중복 처리 무시, 기존 block_reference 기록 |
| 429 | `RATE_LIMIT_EXCEEDED` | 호출 한도 초과 | Exponential Backoff 재시도, 이후 큐 적재 |
| 503 | `SERVICE_UNAVAILABLE` | JPJ 시스템 점검 | Circuit Breaker Open, 캐시 데이터 활용 |

**Fallback 전략:**
```
JPJ 장애 시:
  ① Circuit Breaker Open (연속 5회 실패 후)
  ② Redis 캐시에서 최대 24시간 이내 조회 데이터 반환
  ③ 캐시 미존재 시 → review-service 수동 심사 큐 이관
  ④ 차단 요청 실패 시 → Kafka Dead Letter Queue 적재 후 복구 시 재처리
  ⑤ 장애 지속 > 1시간 → DevOps Agent 자동 에스컬레이션
```

### 2.5 SLA & 제약사항

| 항목 | 값 |
|------|-----|
| 응답 시간 SLA | P99 < 2,000ms (JPJ 제공 SLA 기준) |
| 일일 호출 한도 | 100,000건 (계약 협의 필요) |
| 차단 요청 처리 지연 | 최대 24시간 (실질적 효과) |
| 운영 시간 | 06:00~24:00 MYT (점검 시간 제외) |
| 데이터 보존 | 조회 응답 캐시 최대 24시간 (PDPA 준수) |
| 개인정보 처리 | IC 번호 마스킹 후 로그 저장 (PDPA 제3조) |

---

## 3. TnG 연동 상세

### 3.1 Channel B 결제 흐름

Touch 'n Go는 말레이시아 최대 전자지갑으로, BOS Channel B 결제(TnG eWallet 직불)의 정산 파트너다.

```
Channel B 결제 흐름:
  ① 차량 RFID 태그 인식 (SLFF/MLFF 레인)
  ② txn-service: TnG 태그 식별 (Tag Prefix 기반)
  ③ TnG Authorization API 호출 (실시간 잔액 차감 승인)
  ④ 승인 성공 → 통행료 수납 완료 (processed.txn.events)
  ⑤ 승인 실패 (잔액 부족) → unpaid-service Tier 1 등록
  ⑥ 일별 Batch: billing-service → TnG 정산 API 호출
  ⑦ 월별 대사: TnG Reconciliation 파일 수신 → 대사 처리
```

### 3.2 정산 API 명세

| Method | 엔드포인트 | 설명 | 호출 주기 |
|--------|-----------|------|----------|
| POST | `/v3/transaction/authorize` | 실시간 결제 승인 | 통행 즉시 |
| POST | `/v3/transaction/void` | 결제 취소 (오류 시) | 필요 시 |
| GET | `/v3/settlement/daily/{date}` | 일별 정산 데이터 조회 | 매일 02:00 MYT |
| POST | `/v3/reconciliation/submit` | 대사 결과 제출 | 매월 5일 |
| GET | `/v3/reconciliation/status/{ref_id}` | 대사 처리 상태 조회 | 제출 후 폴링 |

#### 실시간 결제 승인 — POST `/v3/transaction/authorize`

**Request Body:**
```json
{
  "merchant_id": "JVC-BOS-001",
  "terminal_id": "PLAZA-KL-LANE-04",
  "transaction_ref": "TXN-2026-0001234567",
  "tag_id": "1234567890ABCDEF",
  "amount": 2.50,
  "currency": "MYR",
  "toll_category": "CLASS_1",
  "plaza_code": "PLAZA-KL-01",
  "transaction_time": "2026-04-01T08:00:00+08:00",
  "lane_type": "SLFF"
}
```

**Response (200 OK — 승인):**
```json
{
  "status": "APPROVED",
  "authorization_code": "TNG-AUTH-20260401-ABCDE",
  "transaction_ref": "TXN-2026-0001234567",
  "approved_amount": 2.50,
  "currency": "MYR",
  "ewallet_balance_after": 47.30,
  "response_time": "2026-04-01T08:00:00.085+08:00"
}
```

**Response (200 OK — 잔액 부족):**
```json
{
  "status": "DECLINED",
  "decline_code": "INSUFFICIENT_BALANCE",
  "transaction_ref": "TXN-2026-0001234567",
  "ewallet_balance": 1.20,
  "required_amount": 2.50,
  "response_time": "2026-04-01T08:00:00.091+08:00"
}
```

### 3.3 Reconciliation 프로세스

```
일별 대사 (매일 02:00~04:00 MYT):
  ① billing-service: 전일 Channel B 트랜잭션 집계
  ② TnG settlement/daily API 호출 → TnG 측 집계 수신
  ③ 건별 대사 (transaction_ref 키 기준)
  ④ 차액 분류:
     - 완전 일치 → MATCHED
     - BOS 집계 > TnG → BOS_EXCESS (오류 조사 필요)
     - TnG 집계 > BOS → TNG_EXCESS (누락 건 확인)
     - 미매칭 건 → UNMATCHED (수동 심사)
  ⑤ 대사 보고서 자동 생성 → Finance Agent 검토

월별 최종 정산:
  ① 일별 대사 결과 집계 (1일~말일)
  ② TnG reconciliation/submit 호출
  ③ 차액 조정 (Credit/Debit Note 발행)
  ④ TOC별 정산금 계산 및 지급
```

### 3.4 장애 시 처리

| 장애 유형 | BOS 처리 방식 |
|-----------|--------------|
| TnG Authorization API 타임아웃 (>500ms) | Exponential Backoff 재시도 2회, 이후 Fallback: 통행 허용 + 사후 정산 (Trusted Vehicle 한정) |
| TnG 시스템 점검 (사전 공지) | 점검 시간대 RFID 처리 → 오프라인 승인 모드 (사후 일괄 정산) |
| Settlement API 오류 | Kafka Dead Letter Queue 적재, 복구 후 자동 재처리 |
| 대사 차액 > 임계값 (MYR 10,000) | Finance Lead Agent 자동 알림 + 수동 조사 개시 |

---

## 4. FPX 연동 상세

### 4.1 온라인 결제 흐름

FPX(Financial Process Exchange)는 Bank Negara Malaysia 승인 결제 인프라로, BOS 미납 온라인 수납에 활용된다.

```
결제 요청 → 승인 → Callback 흐름:
  ① 고객: BOS 미납 포털 접속 (미납 조회)
  ② unpaid-service: FPX Payment Request 생성
  ③ 고객: FPX 결제 페이지로 리다이렉트 (은행 선택)
  ④ 고객: 인터넷 뱅킹 로그인 → 결제 승인
  ⑤ FPX: BOS Callback URL로 결제 결과 POST
  ⑥ billing-service: Callback 검증 → 수납 처리
  ⑦ 고객: 결제 완료 페이지 리다이렉트
  ⑧ unpaid-service: 미납 상태 업데이트 → Tier 조정
```

### 4.2 FPX API 명세

| Method | 엔드포인트 | 설명 |
|--------|-----------|------|
| POST | `/fpx/api/v2/payment/initiate` | 결제 세션 생성 및 리다이렉트 URL 획득 |
| POST | `/fpx/callback/payment` | FPX → BOS 결제 결과 수신 (Webhook) |
| GET | `/fpx/api/v2/payment/{fpx_txn_id}/status` | 결제 상태 조회 (Callback 미수신 시) |
| POST | `/fpx/api/v2/payment/{fpx_txn_id}/refund` | 환불 요청 |

#### 결제 세션 생성 — POST `/fpx/api/v2/payment/initiate`

**Request Body:**
```json
{
  "merchant_code": "BOS-JVC-2024",
  "order_id": "UNPAID-2026-0001234",
  "amount": 125.50,
  "currency": "MYR",
  "description": "Toll Unpaid — WXY1234 (3 transactions)",
  "buyer_name": "Ahmad bin Abdullah",
  "buyer_email": "ahmad@example.com",
  "buyer_phone": "+601112345678",
  "callback_url": "https://bos-api.jvc-bos.my/api/v1/payments/fpx/callback",
  "success_url": "https://portal.jvc-bos.my/payment/success",
  "fail_url": "https://portal.jvc-bos.my/payment/failed",
  "expiry_minutes": 30
}
```

**Response (200 OK):**
```json
{
  "status": "PENDING",
  "fpx_transaction_id": "FPX-2026-XXXXXXXXX",
  "order_id": "UNPAID-2026-0001234",
  "redirect_url": "https://www.mepsfpx.com.my/FPXMain/checkout?token=XXXXXXX",
  "expires_at": "2026-04-01T08:30:00+08:00"
}
```

#### FPX → BOS Callback (Webhook) — POST `/fpx/callback/payment`

**FPX가 BOS로 전송하는 Callback 데이터:**
```json
{
  "fpx_transaction_id": "FPX-2026-XXXXXXXXX",
  "order_id": "UNPAID-2026-0001234",
  "status": "SUCCESS",
  "amount": 125.50,
  "currency": "MYR",
  "bank_code": "MBBEMYKL",
  "bank_name": "Maybank",
  "buyer_bank_ref": "MAYBK2026XXXXXX",
  "transaction_time": "2026-04-01T08:15:30+08:00",
  "checksum": "sha256_hmac_signature"
}
```

**BOS Callback 처리 로직:**
```
① Checksum 검증 (HMAC-SHA256, Secret Key 기반)
② fpx_transaction_id 중복 수신 확인 (멱등성)
③ order_id → unpaid-service 미납 건 조회
④ 결제 상태 업데이트 (PENDING → PAID)
⑤ billing-service: 수납 기록 생성
⑥ Tier 조정 및 JPJ 차단 해제 요청 (해당 시)
⑦ 고객 이메일/SMS 영수증 발송
⑧ FPX에 HTTP 200 응답 (미응답 시 FPX 재전송)
```

### 4.3 보안 요구사항

```
① TLS 1.2 이상 필수 (TLS 1.0/1.1 비허용)
② Callback Checksum 검증 필수 (HMAC-SHA256)
③ Callback IP Whitelist (FPX 공식 IP 대역만 허용)
④ Callback 중복 처리 방지 (Redis 기반 멱등성 키 TTL 24시간)
⑤ 카드 정보 BOS 서버 비저장 (PCI DSS 준수 — FPX 처리)
⑥ 결제 세션 만료 시간 30분 (생성 후)
```

### 4.4 환불 처리

**환불 요청 — POST `/fpx/api/v2/payment/{fpx_txn_id}/refund`:**
```json
{
  "refund_amount": 125.50,
  "currency": "MYR",
  "reason": "DUPLICATE_PAYMENT",
  "refund_reference": "REFUND-2026-0000123",
  "requested_by": "finance-agent@bos-internal"
}
```

```
환불 처리 흐름:
  ① Finance Lead Agent 또는 Finance Manager 역할 승인 필요
  ② 환불 금액 ≤ 원 결제 금액 (초과 환불 불가)
  ③ 환불 처리 시간: 3~7 영업일 (FPX → 고객 은행)
  ④ 환불 완료 후 unpaid-service 상태 재조정
  ⑤ 환불 이력 Hyperledger Fabric 감사 로그 기록
```

---

## 5. ANPR Vendor 연동 상세

### 5.1 이벤트 수신 방식

ANPR(Automatic Number Plate Recognition) Vendor는 고속도로 레인에 설치된 번호판 인식 카메라 시스템이다. BOS와의 연동은 gRPC 단방향 스트리밍 방식으로 이루어진다.

```
연동 프로토콜: gRPC (Server-side Streaming)
인증 방식: mTLS (Mutual TLS) + Service Account JWT
연결 유지: Keep-alive (ping 간격 30초)
처리량 목표: 최대 10,000 TPS (피크 시간대)

이벤트 스트림 구조:
  ANPR Vendor Camera → gRPC Stream → BOS RFID/ANPR Event Receiver
                                            │
                                            ▼
                                    Kafka (raw.anpr.events)
                                            │
                                            ▼
                                    txn-service (소비)
```

#### Protocol Buffer 정의 (proto3)

```protobuf
syntax = "proto3";
package bos.anpr.v1;

service ANPREventService {
  rpc StreamEvents (StreamRequest) returns (stream ANPREvent);
}

message StreamRequest {
  string plaza_code = 1;
  repeated string lane_ids = 2;
  string session_token = 3;
}

message ANPREvent {
  string event_id = 1;          // UUID v4
  string plaza_code = 2;        // e.g., "PLAZA-KL-01"
  string lane_id = 3;           // e.g., "LANE-04"
  string plate_number = 4;      // e.g., "WXY1234"
  string plate_country = 5;     // "MY" | "SG" | "TH"
  float confidence = 6;         // 0.0 ~ 1.0
  string image_ref = 7;         // S3 presigned URL (TTL 1시간)
  string direction = 8;         // "ENTRY" | "EXIT" | "PASS"
  int64 event_timestamp_ms = 9; // Unix ms
  string vehicle_class = 10;    // "CLASS_1" ~ "CLASS_5"
  ANPRImageMetadata metadata = 11;
}

message ANPRImageMetadata {
  int32 image_width = 1;
  int32 image_height = 2;
  string format = 3;           // "JPEG"
  int64 file_size_bytes = 4;
  bool is_night_mode = 5;
}
```

### 5.2 이미지 데이터 처리 & PDPA 준수

ANPR 이미지에는 차량 번호판과 함께 차량 내부 탑승자가 식별될 수 있어 PDPA(Personal Data Protection Act 2010) 적용 대상이다.

```
이미지 처리 정책 (PDPA 준수):
  ① 이미지 수신 즉시 S3 암호화 저장 (AES-256, SSE-S3)
  ② 번호판 ROI(Region of Interest) 추출 후 원본 이미지 처리:
     - 인식 성공 (confidence ≥ 0.85): 원본 이미지 72시간 후 자동 파기
     - 수동 심사 필요 (confidence < 0.85): 원본 이미지 30일 보존 후 파기
     - 법적 분쟁 이미지: 법무 승인 후 최대 7년 보존 (별도 S3 버킷)
  ③ 이미지 접근 권한: Review Officer, Plaza Manager 역할만 허용
  ④ 이미지 접근 이력 전량 감사 로그 기록 (Hyperledger Fabric)
  ⑤ 이미지 URL(presigned): TTL 1시간, 재발급 시 재인증 필요
```

### 5.3 신뢰도(Confidence) 기반 처리 로직

```
ANPR 이벤트 수신 후 처리 흐름:

confidence ≥ 0.95 (고신뢰도)
  → 자동 처리 (Auto-Process)
  → Account 조회 → 과금 또는 위반 처리
  → 이미지 72시간 후 자동 파기

0.85 ≤ confidence < 0.95 (중신뢰도)
  → 자동 처리 + 사후 샘플 검증 (전체의 5% 샘플링)
  → 이상 패턴 발견 시 review-service 이관

confidence < 0.85 (저신뢰도)
  → review-service 수동 심사 큐 이관
  → Review Officer 24시간 내 처리
  → 심사 결과: CONFIRMED / REJECTED / AMENDED

confidence < 0.50 (인식 실패)
  → 이벤트 폐기 (위반 미적용)
  → ANPR 장비 품질 이슈 모니터링 지표 기록
```

#### Confidence 임계값 조정

```
임계값은 운영 중 조정 가능 (System Config 테이블):
  AUTO_PROCESS_THRESHOLD: 0.85 (기본값)
  MANUAL_REVIEW_THRESHOLD: 0.50 (기본값)

임계값 변경 시 → CTO + Plaza Manager Lead 승인 필요
임계값 변경 이력 → Hyperledger Fabric 기록
```

### 5.4 ANPR 스트림 장애 처리

| 장애 유형 | 탐지 조건 | BOS 처리 |
|-----------|-----------|---------|
| gRPC 연결 끊김 | Ping 응답 없음 (30초) | 자동 재연결 (최대 3회, Backoff) |
| 이벤트 지연 | 이벤트 간격 > 5분 (레인별) | Equipment Alert 발생 |
| 높은 저신뢰도 비율 | confidence < 0.85 비율 > 30% | ANPR Vendor 기술 지원 에스컬레이션 |
| 스트림 완전 중단 | 연결 실패 > 15분 | DevOps Agent 알림 + 현장 점검 요청 |

---

## 6. TOC External REST API (BOS → TOC 방향)

### 6.1 개요

BOS는 TOC(Toll Operating Company, 콘세셔네어)에게 운영 데이터를 읽기 전용 REST API로 제공한다. TOC는 자사 운영 현황을 BOS를 통해 조회하며, 직접 BOS 데이터베이스 접근은 불허한다.

```
제공 방향: BOS api-service → TOC 시스템
접근 방식: API Key + IP Whitelist (TOC별 독립 Key 발급)
데이터 격리: RLS 기반 (TOC는 자사 콘세셔네어 데이터만 조회 가능)
버전: /api/v1/ (현행)
하위 호환: 최소 12개월 보장 (Deprecation Notice 최소 6개월 전)
```

### 6.2 제공 엔드포인트 목록

| Method | 엔드포인트 | 설명 | 응답 형식 |
|--------|-----------|------|----------|
| GET | `/api/v1/transactions` | 통행 트랜잭션 목록 조회 (페이지네이션) | JSON |
| GET | `/api/v1/transactions/{txn_id}` | 트랜잭션 단건 상세 조회 | JSON |
| GET | `/api/v1/transactions/summary` | 일별/월별 트랜잭션 집계 요약 | JSON |
| GET | `/api/v1/revenue/daily` | 일별 수납액 통계 (콘세셔네어 기준) | JSON |
| GET | `/api/v1/revenue/monthly` | 월별 수납액 통계 + 정산 현황 | JSON |
| GET | `/api/v1/plazas` | 담당 플라자 목록 및 레인 상태 조회 | JSON |
| GET | `/api/v1/violations/summary` | 위반·미납 집계 (Tier별) | JSON |

#### 트랜잭션 목록 조회 — GET `/api/v1/transactions`

**Query Parameters:**
```
date_from   : ISO 8601 (필수) — e.g., 2026-04-01
date_to     : ISO 8601 (필수) — e.g., 2026-04-01
plaza_code  : 플라자 코드 필터 (선택)
lane_id     : 레인 ID 필터 (선택)
vehicle_class: CLASS_1~CLASS_5 필터 (선택)
page        : 페이지 번호 (기본값: 1)
per_page    : 페이지당 건수 (기본값: 100, 최대: 500)
```

**Response (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "txn_id": "TXN-2026-0001234567",
      "plaza_code": "PLAZA-KL-01",
      "lane_id": "LANE-04",
      "vehicle_plate": "WXY****",
      "vehicle_class": "CLASS_1",
      "toll_amount": 2.50,
      "currency": "MYR",
      "channel": "CHANNEL_A",
      "payment_method": "RFID_PREPAID",
      "txn_status": "COMPLETED",
      "txn_timestamp": "2026-04-01T08:00:00+08:00"
    }
  ],
  "meta": {
    "total": 15234,
    "page": 1,
    "per_page": 100,
    "total_pages": 153
  }
}
```

> **개인정보 마스킹:** TOC API 응답에서 번호판은 뒤 4자리 마스킹 처리 (`WXY****`). 전체 번호판 조회는 BOS Admin Web을 통해서만 허용.

### 6.3 인증 방식

```
① API Key 발급:
   - TOC별 고유 API Key 발급 (UUID v4 기반, 256-bit 엔트로피)
   - HashiCorp Vault에서 관리 (소스코드·설정 파일 저장 금지)
   - Key 유효기간: 12개월 (만료 30일 전 자동 갱신 알림)
   - Key 갱신: TOC 요청 → api-service Admin 승인 후 발급

② IP Whitelist:
   - TOC별 허용 IP 대역 등록 (최대 10개 CIDR)
   - IP 변경 시 → BOS Integration Lead 사전 승인 필요 (5 영업일)

③ 요청 헤더:
   X-API-Key: {api_key}
   X-Request-ID: {uuid_v4}
   Accept: application/json

④ Rate Limiting:
   - 분당 600 요청 (기본)
   - 일 최대 100,000 요청
   - 초과 시 HTTP 429 응답 (Retry-After 헤더 포함)
```

### 6.4 버전 관리 정책

```
현행 버전: /api/v1/ (안정화)
다음 버전: /api/v2/ (계획 중 — Phase 11 이후)

버전 정책:
  ① Breaking Change → 새 메이저 버전 릴리스 (/api/v2/)
  ② 하위 호환 변경 → 마이너 업데이트 (버전 유지)
  ③ Deprecation Notice → 폐기 예정 버전 최소 6개월 전 공지
  ④ 이전 버전 지원 기간 → 최소 12개월 (계약 의무)

Breaking Change 정의:
  - 기존 필드 제거 또는 타입 변경
  - 필수 파라미터 추가
  - 엔드포인트 경로 변경
  - 응답 구조 재편

Non-Breaking Change (버전 유지 가능):
  - 새 선택 필드 추가
  - 새 선택 파라미터 추가
  - 새 엔드포인트 추가
```

---

## 7. 공통 연동 패턴

### 7.1 Circuit Breaker 설정 (Resilience4j)

모든 외부 연동에 Circuit Breaker를 적용하여 외부 장애 시 BOS 내부 서비스로의 장애 전파를 차단한다.

```yaml
# application-circuit-breaker.yml
resilience4j:
  circuitbreaker:
    configs:
      external-default:
        # Open 전환 조건
        failure-rate-threshold: 50         # 실패율 50% 초과 시 Open
        slow-call-rate-threshold: 80       # 슬로우콜 80% 초과 시 Open
        slow-call-duration-threshold: 3000 # 3,000ms 초과 = 슬로우콜
        minimum-number-of-calls: 10        # 최소 10회 호출 후 평가

        # Open → HalfOpen 전환
        wait-duration-in-open-state: 30s   # 30초 대기 후 HalfOpen
        permitted-number-of-calls-in-half-open-state: 5

        # 슬라이딩 윈도우
        sliding-window-type: COUNT_BASED
        sliding-window-size: 20

        # 예외 처리
        record-exceptions:
          - java.io.IOException
          - java.net.SocketTimeoutException
          - feign.RetryableException
        ignore-exceptions:
          - bos.exception.BusinessException  # 비즈니스 예외는 CB 카운트 제외

    instances:
      jpj-api:
        base-config: external-default
        wait-duration-in-open-state: 60s  # JPJ는 60초 대기 (점검 시간 고려)
      tng-api:
        base-config: external-default
        failure-rate-threshold: 30        # TnG는 30% 실패율에서 Open (결제 민감)
      fpx-api:
        base-config: external-default
        failure-rate-threshold: 30
      anpr-grpc:
        base-config: external-default
        slow-call-duration-threshold: 1000 # ANPR은 1,000ms 기준
```

**Circuit Breaker 상태 전환:**
```
[CLOSED] → 정상 동작
    ↓ 실패율 임계값 초과
[OPEN] → 즉시 실패 (Fallback 실행)
    ↓ wait-duration 경과
[HALF-OPEN] → 제한적 호출 허용
    ↓ 성공 시 CLOSED / 실패 시 OPEN
```

### 7.2 Retry & Exponential Backoff

```yaml
resilience4j:
  retry:
    configs:
      external-default:
        max-attempts: 3                    # 최초 1회 + 재시도 2회 (총 3회)
        wait-duration: 1000ms              # 초기 대기 1초
        enable-exponential-backoff: true
        exponential-backoff-multiplier: 2.0  # 1초 → 2초 → 4초
        exponential-max-wait-duration: 10s   # 최대 대기 10초

        retry-exceptions:
          - java.io.IOException
          - java.net.SocketTimeoutException
          - org.springframework.web.client.HttpServerErrorException  # 5xx
        ignore-exceptions:
          - org.springframework.web.client.HttpClientErrorException  # 4xx는 재시도 안 함

    instances:
      jpj-api:
        base-config: external-default
      tng-api:
        base-config: external-default
        max-attempts: 2               # TnG 결제는 재시도 최소화 (중복 결제 방지)
      fpx-api:
        base-config: external-default
        max-attempts: 2
```

**Jitter 적용 (동시 재시도 방지):**
```java
// Exponential Backoff + Jitter 구현 예시
long delay = (long) (baseDelay * Math.pow(multiplier, attempt));
long jitter = (long) (delay * 0.2 * Math.random()); // ±20% 랜덤 지터
Thread.sleep(delay + jitter);
```

### 7.3 연동 모니터링 & 알림

```
모니터링 지표 (Prometheus):
  external_api_request_total          — 외부 API 총 호출 수 (레이블: target, status)
  external_api_request_duration_ms    — 응답 시간 분포 (히스토그램)
  external_api_circuit_breaker_state  — CB 상태 (0=CLOSED, 1=OPEN, 2=HALF_OPEN)
  external_api_retry_total            — 재시도 발생 건수
  external_api_fallback_total         — Fallback 실행 건수

Grafana 대시보드 패널:
  ① 외부 API별 응답 시간 (P50/P95/P99)
  ② Circuit Breaker 상태 히트맵
  ③ 재시도 비율 트렌드
  ④ Fallback 발동 빈도

알림 규칙 (PagerDuty/Slack 연동):
```

```yaml
# Prometheus Alerting Rules
groups:
  - name: external-integration-alerts
    rules:
      - alert: ExternalAPIHighErrorRate
        expr: rate(external_api_request_total{status=~"5.."}[5m]) /
              rate(external_api_request_total[5m]) > 0.05
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "External API 오류율 5% 초과: {{ $labels.target }}"

      - alert: ExternalAPICircuitBreakerOpen
        expr: external_api_circuit_breaker_state == 1
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Circuit Breaker OPEN: {{ $labels.target }} — 즉시 확인 필요"

      - alert: ExternalAPIHighLatency
        expr: histogram_quantile(0.99,
              rate(external_api_request_duration_ms_bucket[5m])) > 3000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "외부 API P99 레이턴시 3,000ms 초과: {{ $labels.target }}"
```

### 7.4 연동 테스트 전략

#### Mock 환경 (개발·단위 테스트)

```
도구: WireMock (Spring Boot 통합)
목적: 외부 API 없이 로컬 개발 및 단위 테스트 수행

Mock 정의 위치: src/test/resources/wiremock/{target}/
  jpj/
    vehicle_found.json        — 정상 조회 응답
    vehicle_not_found.json    — 404 응답
    jpj_unavailable.json      — 503 응답 (Circuit Breaker 테스트)
  tng/
    auth_approved.json
    auth_declined_balance.json
    tng_timeout.json           — 응답 지연 시뮬레이션
  fpx/
    payment_initiated.json
    callback_success.json
    refund_success.json
```

```java
// WireMock 설정 예시 (Spring Boot Test)
@SpringBootTest
@AutoConfigureWireMock(port = 0)
class JpjIntegrationTest {

    @Test
    void should_return_vehicle_info_when_plate_found() {
        stubFor(get(urlPathMatching("/api/v2/vehicle/WXY1234"))
            .willReturn(aResponse()
                .withStatus(200)
                .withHeader("Content-Type", "application/json")
                .withBodyFile("jpj/vehicle_found.json")));

        VehicleInfo result = jpjClient.getVehicle("WXY1234");
        assertThat(result.getPlateNumber()).isEqualTo("WXY1234");
    }

    @Test
    void should_trigger_fallback_when_jpj_unavailable() {
        stubFor(get(urlPathMatching("/api/v2/vehicle/.*"))
            .willReturn(aResponse().withStatus(503)));

        VehicleInfo result = jpjClient.getVehicle("WXY1234");
        assertThat(result).isNull(); // Fallback: null 반환
        // review-service 큐 이관 확인
    }
}
```

#### Sandbox 환경 (통합 테스트)

| 연동 대상 | Sandbox 환경 | 비고 |
|-----------|--------------|------|
| JPJ | JPJ QA Gateway (`api-uat.jpj.gov.my`) | 실 JPJ와 계약 필요 |
| TnG | TnG Developer Portal Sandbox | 테스트 eWallet 계정 발급 |
| FPX | FPX UAT 환경 (`uat.mepsfpx.com.my`) | 테스트 은행 계정 제공 |
| ANPR Vendor | Vendor 제공 Replay 도구 (녹화된 이벤트 재생) | PCAP 파일 기반 |
| TOC API | BOS 내부 UAT 환경 (`api-uat.jvc-bos.my`) | BOS 자체 제공 |

```
통합 테스트 수행 절차:
  ① Sandbox 자격증명 발급 (각 벤더별 신청)
  ② Happy Path 시나리오 전수 테스트
  ③ 오류 시나리오 테스트 (4xx/5xx, 타임아웃, 부분 응답)
  ④ Circuit Breaker 동작 검증 (Chaos Engineering)
  ⑤ 성능 테스트 (k6 또는 JMeter, 목표 TPS의 120%)
  ⑥ 보안 테스트 (OWASP ZAP — API 취약점 스캔)
```

---

## 8. 참조 문서

| 문서 | 경로 | 내용 |
|------|------|------|
| 시스템 아키텍처 개요 | [01_system_overview.md](./01_system_overview.md) | 3-Layer 아키텍처, External Integration 위치 |
| 서비스 도메인 상세 | [02_service_domains.md](./02_service_domains.md) | 10개 서비스 도메인, 연동 서비스 매핑 |
| 기술 스택 상세 | [03_tech_stack.md](./03_tech_stack.md) | Resilience4j, Spring Boot 버전 정보 |
| BOS API & MCP 스펙 | [06_api_mcp_spec.md](./06_api_mcp_spec.md) | TOC External API 상세 스펙 |
| 보안 & 컴플라이언스 | [../03_data/05_security_compliance.md](../03_data/05_security_compliance.md) | PDPA, ANPR 이미지 정책 |
| 결제 아키텍처 | [../01_business/05_payment_architecture.md](../01_business/05_payment_architecture.md) | Channel A/B 결제 구조, 수수료 모델 |
| 데이터 아키텍처 | [../03_data/01_data_architecture.md](../03_data/01_data_architecture.md) | 연동 데이터 저장 구조 |
| 의사결정 게이트 | [../05_governance/01_decision_gates.md](../05_governance/01_decision_gates.md) | 연동 계약 관련 Board 결정 항목 |

---

*작성일: 2026-04*
*버전: v1.0*
*담당 Agent: Integration Lead, Backend Lead*
*다음 검토: Phase 3 착수 전 (JPJ/TnG 계약 체결 후 엔드포인트 업데이트 필요)*
