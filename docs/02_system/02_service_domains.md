# 10개 서비스 도메인 상세
## 02_system/02_service_domains.md
## v1.0 | 2026-04 | 참조: 01_system_overview.md, 03_data/02_data_model.md

---

> **Agent 사용 지침**
> Backend Lead, Domain Expert Agent가 각 도메인 설계 시 로드.
> 신규 API 또는 Kafka 토픽 추가 전 반드시 이 문서의 의존성 매핑 확인.
> 서비스 간 계약(Contract) 변경은 Backend Lead 승인 필요.

---

## 1. Executive Summary — 10개 도메인 개요

| # | 서비스명 | 도메인 | Phase | 핵심 책임 |
|---|---------|--------|-------|----------|
| 1 | `txn-service` | Transaction Processing | Phase 3 | RFID/ANPR 이벤트 수신, 트랜잭션 생성 및 과금 처리, MLFF Entry/Exit 매칭 |
| 2 | `account-service` | Account & Vehicle | Phase 4 | 계정·차량 등록·관리, Channel A/B 잔액, 요금 클래스 산정 |
| 3 | `billing-service` | Billing & Settlement | Phase 5 | 일별·월별 청구 집계, 콘세셔네어 정산, TOC 지급 처리 |
| 4 | `violation-service` | Violation & Enforcement | Phase 6 | 위반 이벤트 탐지, 위반 등급 분류, JPJ 연동 집행 |
| 5 | `unpaid-service` | Paid/Unpaid Management | Phase 6 | 미납 Tier 1~4 상태 추적, 알림 발송, 채권 관리 |
| 6 | `exemption-service` | Exemption & Discount | Phase 6 | 면제·할인 정책 관리, 대상 차량 검증, 적용 이력 감사 |
| 7 | `review-service` | Transaction Review | Phase 6 | 수동 심사 큐 관리, 이의신청 처리, ANPR 이미지 재심사 |
| 8 | `equipment-service` | Lane Equipment Monitoring | Phase 7 | 레인 장비 상태 모니터링, 장애 탐지, 유지보수 이력 |
| 9 | `reporting-service` | Reporting & Analytics | Phase 8/L3 | KPI 보고서, CEO Heartbeat, TOC 정산 보고, Layer 3 연동 |
| 10 | `api-service` | External API & MCP | Phase 11 | TOC용 읽기 전용 REST API, Paperclip Agent용 MCP Server |

---

## 2. 서비스 도메인 상세

---

### 2.1 txn-service — Transaction Processing

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① RFID/ANPR 원시 이벤트 수신 (Kafka raw.rfid.events, raw.anpr.events)
  ② SLFF: 단일 이벤트 즉시 과금 처리
  ③ MLFF: Redis 기반 Entry/Exit 세션 매칭 (TTL: 구간 최대 이동 시간)
  ④ account-service 호출 → 요금 클래스 확인 + 잔액 차감
  ⑤ 과금 성공 → processed.txn.events 발행
  ⑥ 매칭 실패(타임아웃) → review-service 수동 심사 큐 등록
  ⑦ 중복 이벤트 방지 (Idempotency Key: rfid_tag + timestamp + lane_id)
```

#### 주요 API 엔드포인트 (REST)

```http
POST   /api/v1/transactions/rfid          # RFID 이벤트 수동 주입 (테스트/재처리)
GET    /api/v1/transactions/{txnId}        # 트랜잭션 단건 조회
GET    /api/v1/transactions?vehicleId=&from=&to=  # 차량별 트랜잭션 이력
POST   /api/v1/transactions/{txnId}/retry  # 과금 실패 트랜잭션 재시도
GET    /api/v1/transactions/mlff/sessions  # MLFF 진행 중 세션 조회
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Subscribe | `raw.rfid.events` | RFID 장비 원시 이벤트 |
| Subscribe | `raw.anpr.events` | ANPR 번호판 인식 이벤트 |
| Publish | `processed.txn.events` | 과금 완료 트랜잭션 |
| Publish | `txn.failed.events` | 과금 실패 이벤트 (미납 처리용) |
| Publish | `review.queue.events` | 수동 심사 등록 이벤트 |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `transactions` | 트랜잭션 마스터 (txn_id, vehicle_id, lane_id, amount, status, channel) |
| `mlff_sessions` | MLFF Entry/Exit 세션 (session_id, entry_event_id, exit_event_id, matched_at) |
| `raw_rfid_events` | 원시 RFID 이벤트 보관 (이벤트 소싱, 변경 불가) |
| `raw_anpr_events` | 원시 ANPR 이벤트 보관 (신뢰도 점수 포함) |

#### 성능 요구사항

```
처리량: 10,000 TPS (피크), 3,000 TPS (평시)
RFID 이벤트 처리 지연: <100ms P99 (Kafka 소비 → 과금 완료)
MLFF 매칭 정확도: 99.9% (월간 기준)
Redis TTL 설정: SLFF = 즉시, MLFF = 구간 이동 예상 시간 × 1.5
```

#### 의존성

```
→ account-service  : 잔액 확인 및 차감 (동기 REST, Circuit Breaker 적용)
→ review-service   : 매칭 실패 이벤트 전달 (비동기 Kafka)
← unpaid-service   : txn.failed.events 구독 (Tier 1 등록)
← billing-service  : processed.txn.events 구독 (집계)
← reporting-service: processed.txn.events 구독 (통계)
```

---

### 2.2 account-service — Account & Vehicle

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① 계정 생성·수정·조회 (개인/법인/정부 계정 유형 구분)
  ② 차량 등록·수정·말소 (RFID 태그 + 번호판 매핑)
  ③ Channel A 잔액 관리 (Clearing Center 계정 연동)
  ④ Channel B 상태 조회 (TnG 잔액은 TnG 측 관리)
  ⑤ 요금 클래스 결정 (차종 Class 1~6, 면제 여부 확인)
  ⑥ JPJ 차량 등록 실시간 조회 (외부 API 호출)
  ⑦ 계정 정지·복구 처리 (미납 Tier 4 연동)
```

#### 주요 API 엔드포인트 (REST)

```http
POST   /api/v1/accounts                        # 신규 계정 생성
GET    /api/v1/accounts/{accountId}            # 계정 단건 조회
PUT    /api/v1/accounts/{accountId}            # 계정 정보 수정
POST   /api/v1/accounts/{accountId}/vehicles   # 차량 등록
GET    /api/v1/accounts/{accountId}/balance    # Channel A 잔액 조회
GET    /api/v1/vehicles/{rfidTag}/class        # 요금 클래스 조회 (txn-service 전용)
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Subscribe | `unpaid.tier4.events` | Tier 4 미납 → 계정 정지 트리거 |
| Publish | `account.status.changed` | 계정 상태 변경 알림 (정지/복구) |
| Publish | `vehicle.registered.events` | 신규 차량 등록 알림 |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `accounts` | 계정 마스터 (account_id, type, status, channel_a_balance) |
| `vehicles` | 차량 마스터 (vehicle_id, account_id, rfid_tag, plate_no, class) |
| `account_audit_log` | 계정 변경 이력 (Hyperledger Fabric 연동) |

#### 성능 요구사항

```
요금 클래스 조회: <10ms P99 (Redis 캐시 우선)
계정 조회 캐시 TTL: 5분 (잔액은 실시간, 차종 정보는 캐시)
JPJ 외부 조회 타임아웃: 3초 (이후 Circuit Breaker 오픈)
```

#### 의존성

```
→ JPJ API       : 차량 등록 정보 조회 (외부, Circuit Breaker)
→ TnG API       : Channel B 상태 조회 (외부, Circuit Breaker)
← txn-service   : 요금 클래스 + 잔액 조회 (동기 REST)
← exemption-service: 면제 적용 요청 (동기 REST)
← unpaid-service: Tier 4 계정 정지 트리거 (비동기 Kafka)
```

---

### 2.3 billing-service — Billing & Settlement

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① 일별 수납액 집계 (콘세셔네어 × 요금소 × Channel A/B)
  ② JVC 수수료 차감 (3~12%, 콘세셔네어 계약별 상이)
  ③ TOC 지급액 산정 및 정산서 생성
  ④ Clearing Center 정산 데이터 수신·대사
  ⑤ TnG 정산 수신 (Channel B, 월간)
  ⑥ 차액 조정 (Variance Reconciliation)
  ⑦ 콘세셔네어별 월간 Statement 발행
```

#### 주요 API 엔드포인트 (REST)

```http
GET    /api/v1/billing/daily?concessionId=&date=     # 일별 집계 조회
GET    /api/v1/billing/statements/{statementId}       # 정산서 단건 조회
POST   /api/v1/billing/reconcile                      # 대사 실행 (배치 트리거)
GET    /api/v1/billing/variance?month=&concessionId=  # 차액 조정 내역
POST   /api/v1/billing/statements/{id}/approve        # 정산서 승인 (Finance 권한)
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Subscribe | `processed.txn.events` | 과금 완료 트랜잭션 집계 |
| Publish | `billing.daily.closed` | 일별 집계 마감 이벤트 |
| Publish | `settlement.ready.events` | 정산 준비 완료 알림 |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `billing_daily` | 일별 집계 (concession_id, plaza_id, channel, amount, fee, net_amount) |
| `settlement_statements` | 정산서 마스터 (statement_id, period, status, approved_by) |
| `reconciliation_log` | 대사 이력 (clearing_center_amount, bos_amount, variance) |
| `tng_settlement_records` | TnG Channel B 정산 수신 기록 |

#### 성능 요구사항

```
일별 집계 배치: D+1 06:00 완료 (전날 00:00~23:59 기준)
정산서 생성: 월 마감 후 3 영업일 이내
대사 처리: 건당 <500ms, 전체 대사 <30분 (일별 기준)
```

#### 의존성

```
← txn-service        : processed.txn.events 구독 (집계 소스)
→ Clearing Center API : 정산 데이터 수신 (외부)
→ TnG API            : Channel B 정산 수신 (외부)
← reporting-service  : 정산 보고서 데이터 제공
```

---

### 2.4 violation-service — Violation & Enforcement

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① 위반 이벤트 탐지 (미결제 통행, RFID 불일치, 번호판 위조 의심)
  ② 위반 등급 분류 (Minor / Major / Fraud)
  ③ ANPR 이미지 기반 위반 증빙 생성
  ④ JPJ 연동 → 도로세 차단(Roadtax Block) 요청
  ⑤ 위반 통지서(Notice) 발행 및 발송
  ⑥ 법적 집행 에스컬레이션 (Major 이상)
  ⑦ 위반 이력 관리 (차량·계정 연계)
```

#### 주요 API 엔드포인트 (REST)

```http
GET    /api/v1/violations/{violationId}              # 위반 단건 조회
GET    /api/v1/violations?vehicleId=&status=         # 차량별 위반 이력
POST   /api/v1/violations/{violationId}/notice        # 통지서 발행
PUT    /api/v1/violations/{violationId}/escalate      # 법적 에스컬레이션
GET    /api/v1/violations/pending-jpj                 # JPJ 연동 대기 목록
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Subscribe | `txn.failed.events` | 과금 실패 → 위반 후보 등록 |
| Subscribe | `violation.events` | 장비 레이어에서 탐지된 위반 이벤트 |
| Publish | `violation.created.events` | 신규 위반 등록 알림 |
| Publish | `jpj.block.requests` | JPJ 도로세 차단 요청 |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `violations` | 위반 마스터 (violation_id, vehicle_id, type, grade, status) |
| `violation_evidence` | 위반 증빙 (anpr_image_path, rfid_mismatch_log, timestamp) |
| `jpj_block_requests` | JPJ 차단 요청 이력 (request_id, status, response_code) |
| `violation_notices` | 통지서 발행 이력 (notice_id, channel, sent_at, delivered) |

#### 성능 요구사항

```
위반 탐지 지연: <200ms (txn.failed.events 소비 후)
JPJ API 호출 타임아웃: 5초 (재시도 2회, Exponential Backoff)
ANPR 이미지 보관: 7년 (PDPA 및 법적 요건 준수)
```

#### 의존성

```
← txn-service      : txn.failed.events 구독
← equipment-service: 장비 감지 위반 이벤트 구독
→ JPJ API          : 도로세 차단 요청 (외부)
→ unpaid-service   : 위반 미납 Tier 연동 (비동기 Kafka)
→ review-service   : 이의신청 접수 연동
```

---

### 2.5 unpaid-service — Paid/Unpaid Management

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① 미납 Tier 상태 머신 관리 (Tier 1 → 2 → 3 → 4)
  ② Tier 1: 즉시 미납 등록 + Email/SMS 알림
  ③ Tier 2: 30일 경과 + 연체료 부과 + 재알림
  ④ Tier 3: 90일 경과 + 법적 통지 + JPJ 연동 준비
  ⑤ Tier 4: 180일 경과 + 계정 정지 + 법적 집행 의뢰
  ⑥ 미납 채권 이력 관리 (법적 분쟁 대비)
  ⑦ 자발적 납부 수신 시 Tier 해제 처리
```

#### 주요 API 엔드포인트 (REST)

```http
GET    /api/v1/unpaid/{unpaidId}                    # 미납 단건 조회
GET    /api/v1/unpaid?accountId=&tier=              # 계정별 미납 목록
POST   /api/v1/unpaid/{unpaidId}/payment            # 납부 처리 (Tier 해제)
GET    /api/v1/unpaid/escalation-queue              # 에스컬레이션 대기 목록
GET    /api/v1/unpaid/statistics?month=             # 미납 통계 요약
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Subscribe | `txn.failed.events` | 과금 실패 → Tier 1 등록 |
| Publish | `unpaid.tier4.events` | Tier 4 도달 → 계정 정지 트리거 |
| Publish | `notification.events` | 알림 발송 요청 (Email/SMS) |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `unpaid_records` | 미납 마스터 (unpaid_id, account_id, txn_id, tier, overdue_days, penalty) |
| `tier_transitions` | Tier 변경 이력 (from_tier, to_tier, transitioned_at, reason) |
| `notification_log` | 알림 발송 이력 (channel, sent_at, delivered_at, error_code) |

#### 성능 요구사항

```
Tier 전환 배치: 매일 02:00 실행 (D-day 기준 상태 갱신)
알림 발송 지연: <60초 (Tier 등록 후 Email/SMS)
Tier 4 계정 정지 실행: <5분 (unpaid.tier4.events 발행 후)
```

#### 의존성

```
← txn-service       : txn.failed.events 구독
← violation-service : 위반 미납 연동
→ account-service   : unpaid.tier4.events → 계정 정지
→ JPJ API           : Tier 3 이상 도로세 차단 요청
→ notification-engine: 알림 발송 (Email/SMS)
```

---

### 2.6 exemption-service — Exemption & Discount

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① 면제·할인 정책 생성·수정·폐기 (Policy CRUD)
  ② 대상 차량·계정 자격 검증 (정부 차량, 장애인, 노선버스 등)
  ③ 트랜잭션 처리 시 실시간 면제 적용 (txn-service 연동)
  ④ 면제 적용 이력 감사 로그 (PDPA 및 감사 요건)
  ⑤ 면제 만료 관리 (유효기간 기반 자동 해제)
  ⑥ 콘세셔네어별 할인 정책 격리 (RLS 기반)
```

#### 주요 API 엔드포인트 (REST)

```http
GET    /api/v1/exemptions/policies                         # 면제 정책 목록
POST   /api/v1/exemptions/policies                         # 신규 정책 생성
GET    /api/v1/exemptions/vehicles/{vehicleId}/eligibility # 차량 자격 조회
POST   /api/v1/exemptions/apply                            # 면제 적용 요청 (txn-service 호출)
GET    /api/v1/exemptions/audit?vehicleId=&from=&to=       # 면제 적용 감사 이력
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Publish | `exemption.applied.events` | 면제 적용 완료 이벤트 |
| Publish | `exemption.expired.events` | 면제 만료 이벤트 |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `exemption_policies` | 정책 마스터 (policy_id, type, discount_rate, valid_from, valid_to) |
| `vehicle_exemptions` | 차량별 면제 적용 (vehicle_id, policy_id, approved_by, expires_at) |
| `exemption_audit_log` | 적용 이력 감사 (txn_id, policy_id, discount_amount, applied_at) |

#### 성능 요구사항

```
자격 조회 응답: <20ms P99 (Redis 캐시 적용)
캐시 무효화: 정책 변경 즉시 (Cache-Aside 패턴)
만료 배치: 매일 01:00 (당일 만료 건 자동 해제)
```

#### 의존성

```
← txn-service    : 실시간 자격 조회 (동기 REST)
→ account-service: 계정·차량 정보 조회
→ reporting-service: 면제 통계 데이터 제공
```

---

### 2.7 review-service — Transaction Review

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① 수동 심사 큐 관리 (MLFF 매칭 실패, ANPR 저신뢰도, 이의신청)
  ② 심사 담당자 배정 및 SLA 추적 (처리 기한 초과 시 에스컬레이션)
  ③ ANPR 이미지 기반 수동 번호판 식별
  ④ 이의신청(Appeal) 접수·처리·결정 기록
  ⑤ 심사 결정에 따른 트랜잭션 정정·취소
  ⑥ AI 보조 심사 (Claude Sonnet 기반 이상 탐지 권고)
```

#### 주요 API 엔드포인트 (REST)

```http
GET    /api/v1/reviews/queue?assignedTo=&status=     # 심사 큐 조회
POST   /api/v1/reviews/{reviewId}/decision           # 심사 결정 입력
GET    /api/v1/reviews/{reviewId}/images             # ANPR 이미지 조회
POST   /api/v1/reviews/appeals                       # 이의신청 접수
PUT    /api/v1/reviews/appeals/{appealId}/resolve    # 이의신청 처리 결정
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Subscribe | `review.queue.events` | 심사 큐 등록 이벤트 |
| Subscribe | `violation.created.events` | 위반 관련 이의신청 연동 |
| Publish | `review.decided.events` | 심사 결정 이벤트 (txn 정정 트리거) |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `review_queue` | 심사 큐 (review_id, type, priority, assigned_to, sla_deadline) |
| `review_decisions` | 심사 결정 이력 (decision, decided_by, decided_at, reason) |
| `appeals` | 이의신청 마스터 (appeal_id, txn_id, submitter, status, resolution) |

#### 성능 요구사항

```
심사 SLA: 심사 유형별 상이 (이의신청 5 영업일, MLFF 매칭 실패 24시간)
큐 등록 → 배정: <10분 (자동 배정 알고리즘)
AI 권고 생성: <30초 (Claude Sonnet API 호출)
```

#### 의존성

```
← txn-service        : review.queue.events 구독 (MLFF 매칭 실패)
← violation-service  : 이의신청 연동
→ txn-service        : 심사 결정 후 트랜잭션 정정 요청
→ notification-engine: 이의신청 결과 알림 발송
```

---

### 2.8 equipment-service — Lane Equipment Monitoring

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① 레인별 장비 상태 실시간 모니터링 (RFID 리더, ANPR 카메라, 루프 감지기)
  ② 장비 Heartbeat 수신 및 이상 탐지 (30초 무응답 → 경고)
  ③ 장비 장애 분류 (Major / Minor / Warning)
  ④ 유지보수 작업 지시 생성 및 이력 관리
  ⑤ 장비 성능 지표 수집 (인식률, 처리 지연, 오류 빈도)
  ⑥ 장비별 설치·교체·폐기 이력 추적 (Asset Management)
```

#### 주요 API 엔드포인트 (REST)

```http
GET    /api/v1/equipment/lanes/{laneId}/status        # 레인 장비 현황 조회
GET    /api/v1/equipment/{equipmentId}/history         # 장비 상태 이력
POST   /api/v1/equipment/{equipmentId}/maintenance     # 유지보수 작업 지시
GET    /api/v1/equipment/alerts?plaza=&severity=       # 장비 경보 목록
GET    /api/v1/equipment/performance?plazaId=&date=   # 장비 성능 지표
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Subscribe | `equipment.status` | 장비 상태 변경 이벤트 |
| Publish | `equipment.alert.events` | 장비 경보 발생 이벤트 |
| Publish | `violation.events` | 장비 감지 위반 이벤트 (RFID 불일치 등) |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `equipment_master` | 장비 마스터 (equipment_id, lane_id, type, installed_at, status) |
| `equipment_status_log` | 상태 이력 (status, recorded_at, heartbeat_latency_ms) |
| `maintenance_orders` | 유지보수 지시 (order_id, equipment_id, priority, assigned_to, resolved_at) |

#### 성능 요구사항

```
Heartbeat 수신 주기: 10초 (장비 → equipment-service)
장애 탐지 지연: <60초 (30초 무응답 감지 + 처리)
현장 Mobile App 실시간 조회: <3초 응답
장비 이력 보관: 5년 (감사 요건)
```

#### 의존성

```
→ violation-service  : 장비 감지 위반 이벤트 발행
→ reporting-service  : 장비 성능 지표 제공
← Mobile App         : 실시간 현황 조회 (REST)
← DevOps Agent       : 장비 경보 수신 및 자동 조치
```

---

### 2.9 reporting-service — Reporting & Analytics

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① CEO Heartbeat 보고서 자동 생성 (주간·월간)
  ② TOC 운영 보고서 생성 (콘세셔네어별 수납 현황)
  ③ KPI 대시보드 데이터 집계 (실시간 + 일별)
  ④ Layer 3 (Delta Lake) 데이터 공급 (Bronze Layer 원시 데이터)
  ⑤ 규제 보고 (Bank Negara, 도로부 요건)
  ⑥ Text-to-SQL 쿼리 실행 지원 (AI 기반 자연어 분석)
  ⑦ 보고서 Export (PDF, XLSX, CSV)
```

#### 주요 API 엔드포인트 (REST)

```http
GET    /api/v1/reports/heartbeat?week=               # CEO Heartbeat 보고서
GET    /api/v1/reports/toc/{concessionId}?month=     # TOC 운영 보고서
GET    /api/v1/reports/kpi/realtime                  # 실시간 KPI 데이터
POST   /api/v1/reports/query                         # Text-to-SQL 쿼리 실행
GET    /api/v1/reports/{reportId}/export?format=     # 보고서 Export
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Subscribe | `processed.txn.events` | 트랜잭션 통계 집계 |
| Subscribe | `billing.daily.closed` | 일별 수납 마감 데이터 수신 |
| Subscribe | `equipment.alert.events` | 장비 경보 현황 집계 |
| Publish | `report.generated.events` | 보고서 생성 완료 알림 |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `kpi_snapshots` | KPI 스냅샷 (시간별 집계: tps, revenue, unpaid_count, violation_count) |
| `report_definitions` | 보고서 정의 (report_id, type, schedule, recipients) |
| `generated_reports` | 생성 보고서 이력 (report_id, generated_at, storage_path, status) |

#### 성능 요구사항

```
실시간 KPI 조회: <500ms (Redis 집계 캐시)
Heartbeat 보고서 생성: 주간 마감 후 1시간 이내 자동 생성
Layer 3 데이터 동기화: 매시간 배치 (Bronze Layer 공급)
Text-to-SQL 응답: <10초 (Claude Sonnet API 포함)
```

#### 의존성

```
← txn-service, billing-service, equipment-service: 이벤트 구독
→ Layer 3 (Delta Lake): Bronze Layer 데이터 공급 (배치)
→ Email/Portal: 보고서 배포
← api-service: 외부 조회 요청 수신
```

---

### 2.10 api-service — External API & MCP

#### 역할 & 책임

```
핵심 비즈니스 로직:
  ① TOC용 읽기 전용 REST API 제공 (수납 현황, 미납 통계)
  ② API 인증·인가 (API Key + IP Whitelist)
  ③ Rate Limiting (TOC별 쿼터 관리)
  ④ Paperclip AI Agent용 MCP Server (내부망 전용)
  ⑤ MCP Tools: 트랜잭션 조회, 계정 조회, 위반 이력, 장비 상태, 실시간 KPI
  ⑥ API 버전 관리 (하위 호환 12개월 보장)
  ⑦ 외부 API 감사 로그 (모든 조회 기록)
```

#### 주요 API 엔드포인트 (REST)

```http
GET    /api/v1/external/transactions?plazaId=&date=    # TOC: 수납 현황 조회
GET    /api/v1/external/unpaid/summary?concessionId=   # TOC: 미납 통계 요약
GET    /api/v1/external/equipment/status?plazaId=      # TOC: 장비 현황 조회
GET    /api/v1/external/kpi?period=                    # TOC: KPI 요약
GET    /api/v1/health                                  # API 헬스체크 (공개)
```

#### MCP Tools (Paperclip Agent 전용)

```json
{
  "tools": [
    "get_transaction_detail",
    "search_transactions_by_vehicle",
    "get_account_status",
    "get_violation_history",
    "get_equipment_status",
    "get_realtime_kpi",
    "get_unpaid_summary",
    "get_billing_statement"
  ]
}
```

#### Kafka 토픽

| 방향 | 토픽 | 설명 |
|------|------|------|
| Publish | `api.access.log` | API 접근 감사 로그 (보안 감사용) |

#### 핵심 DB 테이블

| 테이블 | 설명 |
|--------|------|
| `api_clients` | API 클라이언트 등록 (client_id, api_key_hash, ip_whitelist, quota) |
| `api_access_log` | 접근 감사 로그 (client_id, endpoint, timestamp, response_code) |

#### 성능 요구사항

```
TOC API 응답: <200ms P99 (reporting-service 캐시 활용)
Rate Limit: TOC별 1,000 RPM (Rate Per Minute) 기본
MCP Tool 응답: <5초 (Claude API 연동 고려)
API Key 검증: <5ms (Redis 캐시)
```

#### 의존성

```
→ reporting-service  : KPI·보고서 데이터 조회 (내부 REST)
→ txn-service        : 트랜잭션 상세 조회 (내부 REST)
→ account-service    : 계정 상태 조회 (내부 REST)
→ violation-service  : 위반 이력 조회 (내부 REST)
→ equipment-service  : 장비 현황 조회 (내부 REST)
```

---

## 3. 서비스 간 의존성 매핑

### 3.1 동기 의존성 (REST 호출)

```
txn-service ──────────────────────────────────────────► account-service
                                                          (잔액 확인 + 요금 클래스)

txn-service ──────────────────────────────────────────► exemption-service
                                                          (면제 자격 확인)

api-service ──┬──────────────────────────────────────► reporting-service
              ├──────────────────────────────────────► txn-service
              ├──────────────────────────────────────► account-service
              ├──────────────────────────────────────► violation-service
              └──────────────────────────────────────► equipment-service
```

### 3.2 비동기 의존성 (Kafka 이벤트)

```
                    ┌─────────────────────────────────────────────┐
                    │              Kafka MSK                       │
                    │                                             │
  txn-service ─────┼─► processed.txn.events ──────┬─► billing-service
                    │                              ├─► reporting-service
                    │                              └─► (Layer 3 Bronze)
                    │
  txn-service ─────┼─► txn.failed.events ──────────┬─► unpaid-service
                    │                              └─► violation-service
                    │
  txn-service ─────┼─► review.queue.events ─────────► review-service
                    │
  equipment-service─┼─► equipment.alert.events ───────► reporting-service
                    │
  equipment-service─┼─► violation.events ─────────────► violation-service
                    │
  unpaid-service ──┼─► unpaid.tier4.events ───────────► account-service
                    │
  billing-service ─┼─► billing.daily.closed ──────────► reporting-service
                    └─────────────────────────────────────────────┘
```

### 3.3 외부 시스템 의존성

| 서비스 | 외부 시스템 | 방향 | 용도 |
|--------|------------|------|------|
| `account-service` | JPJ API | → | 차량 등록 조회 |
| `account-service` | TnG API | → | Channel B 상태 조회 |
| `violation-service` | JPJ API | → | 도로세 차단 요청 |
| `unpaid-service` | JPJ API | → | Tier 3 이상 차단 요청 |
| `billing-service` | Clearing Center | ↔ | 정산 데이터 교환 |
| `billing-service` | TnG API | ← | Channel B 정산 수신 |

---

## 4. 공통 패턴

### 4.1 Circuit Breaker (Resilience4j)

외부 API 및 내부 서비스 간 동기 호출에 적용.

```java
// Spring Boot Resilience4j 설정 예시
@CircuitBreaker(name = "jpj-api", fallbackMethod = "jpjApiFallback")
@Retry(name = "jpj-api")
public VehicleInfo queryJpj(String plateNo) { ... }

// application.yml
resilience4j:
  circuitbreaker:
    instances:
      jpj-api:
        slidingWindowSize: 10
        failureRateThreshold: 50      # 50% 실패 시 Open
        waitDurationInOpenState: 30s  # 30초 후 Half-Open 시도
        permittedNumberOfCallsInHalfOpenState: 3
  retry:
    instances:
      jpj-api:
        maxAttempts: 3
        waitDuration: 1s
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
```

### 4.2 Outbox Pattern (트랜잭션 이벤트 안전 발행)

DB 커밋과 Kafka 발행의 원자성 보장.

```
[Business Logic]
  ├── DB 트랜잭션 시작
  ├── 비즈니스 데이터 저장 (e.g., transactions 테이블)
  ├── Outbox 테이블에 이벤트 삽입
  └── DB 트랜잭션 커밋
              │
              ▼
  [Outbox Poller] (별도 스레드, 500ms 주기)
  ├── outbox_events WHERE status = 'PENDING' 조회
  ├── Kafka 발행
  └── status = 'PUBLISHED' 업데이트
```

```sql
-- outbox_events 테이블 구조
CREATE TABLE outbox_events (
    event_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic       VARCHAR(128) NOT NULL,
    payload     JSONB        NOT NULL,
    status      VARCHAR(16)  NOT NULL DEFAULT 'PENDING',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    published_at TIMESTAMPTZ
);
CREATE INDEX idx_outbox_pending ON outbox_events (status, created_at)
  WHERE status = 'PENDING';
```

### 4.3 Idempotency Key (중복 이벤트 방지)

RFID/ANPR 이벤트는 네트워크 장애로 중복 수신 가능.

```java
// txn-service: Idempotency Key 기반 중복 처리 방지
String idempotencyKey = rfidTag + "_" + laneId + "_" + epochSecond;

// Redis SET NX (Not Exists) 활용
Boolean isNew = redisTemplate.opsForValue()
    .setIfAbsent(idempotencyKey, "1", Duration.ofHours(24));

if (Boolean.FALSE.equals(isNew)) {
    log.warn("Duplicate event detected: {}", idempotencyKey);
    return; // 중복 이벤트 무시
}
```

### 4.4 RLS 멀티테넌시 (PostgreSQL Row-Level Security)

콘세셔네어(TOC)별 데이터 격리.

```sql
-- 모든 핵심 테이블에 concession_id 컬럼 존재
ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY txn_rls ON transactions
  USING (concession_id = current_setting('app.concession_id')::UUID);

-- Spring Boot: 요청 시작 시 컨텍스트 설정
-- (JwtAuthFilter에서 추출한 concession_id 주입)
jdbcTemplate.execute(
    "SET LOCAL app.concession_id = '" + concessionId + "'"
);
```

### 4.5 Saga Pattern (분산 트랜잭션)

과금 실패 시 보상 트랜잭션 처리.

```
[Choreography-based Saga: 과금 흐름]

① txn-service:    과금 시도 → 성공 → processed.txn.events 발행
                               실패 → txn.failed.events 발행
② unpaid-service: txn.failed.events 구독 → Tier 1 등록
③ account-service: (보상) 잔액 복구 불필요 (선차감하지 않았으므로)
```

### 4.6 Health Check & Readiness Probe

모든 서비스에 K8s Probe 표준화.

```yaml
# deployment.yaml 공통 설정
livenessProbe:
  httpGet:
    path: /actuator/health/liveness
    port: 8080
  initialDelaySeconds: 30
  periodSeconds: 10

readinessProbe:
  httpGet:
    path: /actuator/health/readiness
    port: 8080
  initialDelaySeconds: 20
  periodSeconds: 5

# application.yml (Spring Boot Actuator)
management:
  endpoint:
    health:
      probes:
        enabled: true
      group:
        readiness:
          include: db, redis, kafka
```

---

## 5. 참조 문서

| 문서 | 내용 |
|------|------|
| [01_system_overview.md](./01_system_overview.md) | 시스템 전체 아키텍처 및 3-Layer 구조 |
| [03_tech_stack.md](./03_tech_stack.md) | Spring Boot, Kafka, PostgreSQL 상세 스택 |
| [04_ai_features.md](./04_ai_features.md) | Claude 기반 AI 기능 설계 |
| [05_external_integration.md](./05_external_integration.md) | JPJ, TnG, FPX, ANPR 외부 연동 명세 |
| [06_api_mcp_spec.md](./06_api_mcp_spec.md) | api-service REST API & MCP Tool 명세 |
| [../03_data/01_data_architecture.md](../03_data/01_data_architecture.md) | 데이터 아키텍처 (5단계 집계 구조) |
| [../03_data/02_data_model.md](../03_data/02_data_model.md) | DB 테이블 상세 ERD |
| [../03_data/03_rbac_design.md](../03_data/03_rbac_design.md) | 30개 역할 권한 매트릭스 |
| [../01_business/05_payment_architecture.md](../01_business/05_payment_architecture.md) | Channel A/B 결제 구조 상세 |

---

*작성일: 2026-04*
*버전: v1.0*
*담당 Agent: Backend Lead (총괄), Domain Expert Agent (각 도메인)*
