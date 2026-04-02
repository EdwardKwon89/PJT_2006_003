# Phase 4: 계정 & 차량 관리
## 06_phases/04_phase04_account.md
## v1.0 | 2026-04 | 참조: 02_system/02_service_domains.md, 02_system/05_external_integration.md

---

> **Agent 사용 지침**
> `account-lead`, `account-dev` Agent가 계정 및 차량 관리 구현 시 반드시 로드.
> 본 문서는 Phase 4 실행의 유일한 정식 기준 문서이며, 모든 계정·차량·RLS 정책의 구현 기준으로 사용된다.
> JPJ 연동 코드 및 RLS 정책은 반드시 `account-lead` 리뷰 후 머지한다.

---

## 1. Phase 개요

### 1.1 목적 및 범위

Phase 4는 Malaysia SLFF/MLFF Tolling BOS의 **계정 및 차량 관리 도메인**을 구축하는 단계다. Phase 3의 트랜잭션 처리 엔진이 발행하는 `processed.txn.events`를 소비하여 계정 잔액 갱신 및 자동 충전 트리거를 실행하고, 고객 유형별(개인·법인·플릿·정부) 계정 서비스와 차량 등록·RFID 태그 발급 워크플로우를 완성한다.

**핵심 목표:**
- 개인·법인·플릿·정부 4종 계정 유형 완전 지원
- 차량 등록 및 RFID 태그 발급 워크플로우 구현
- JPJ (Jabatan Pengangkutan Jalan) 차량 조회 API 연동 (Circuit Breaker + Retry)
- PostgreSQL Row-Level Security (RLS)로 콘세셔네어 데이터 격리
- 계정 상태 머신 구현 (ACTIVE / SUSPENDED / CLOSED)
- 잔액 임계치 기반 자동 충전 트리거 연동

### 1.2 Phase 연계

| 구분 | 내용 |
|------|------|
| **선행 Phase** | Phase 3 — 트랜잭션 처리 엔진 (`processed.txn.events` 토픽 및 Outbox Pattern 완료 필수) |
| **후행 Phase** | Phase 5 — 빌링 & 정산 (계정·잔액 정보 의존) / Phase 6 — 위반 & 미납 관리 (계정 상태·차량 정보 의존) |
| **예상 기간** | **2주** (Sprint 8~9) |
| **병렬 가능 작업** | 개인·법인 계정 구현 ↔ 플릿·정부 계정 구현 (독립 개발 후 통합) |

### 1.3 아키텍처 포지션

```
[Kafka: processed.txn.events]
          │
          ▼
┌─────────────────────────────┐
│       account-service       │  ← Phase 4 구현 영역
│                             │
│  ┌─────────────────────┐   │
│  │  Account Manager    │   │  개인/법인/플릿/정부 계정
│  ├─────────────────────┤   │
│  │  Vehicle Registry   │   │  차량 등록 & RFID 태그
│  ├─────────────────────┤   │
│  │  JPJ Connector      │   │  외부 차량 조회 API
│  ├─────────────────────┤   │
│  │  Balance Manager    │   │  잔액 관리 & 자동 충전
│  └─────────────────────┘   │
│                             │
│  [PostgreSQL + RLS]         │  콘세셔네어 격리
│  [Redis: balance-cache]     │  잔액 캐시
└─────────────┬───────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
[Phase 5: billing]  [Phase 6: violation]
```

### 1.4 계정 유형별 주요 특성

| 계정 유형 | 코드 | RFID 태그 수 | 자동 충전 | 비고 |
|---------|------|------------|---------|------|
| 개인 (Individual) | `IND` | 1~3개 | 선택 | TnG 연동 |
| 법인 (Corporate) | `CORP` | 최대 50개 | 필수 | 세금계산서 발행 |
| 플릿 (Fleet) | `FLEET` | 최대 500개 | 필수 | 차량 그룹 관리 |
| 정부 (Government) | `GOV` | 제한 없음 | N/A | 후불 청구 |

---

## 2. 담당 Agent 및 역할 분담

### 2.1 Phase 4 참여 Agent

| Agent | 역할 | 주요 책임 |
|-------|------|---------|
| `account-lead` | 기술 리드 | 아키텍처 설계, 코드 리뷰, JPJ 연동 승인, RLS 정책 최종 검토 |
| `account-dev-1` | 개발 담당 1 | Account Manager 구현, 계정 상태 머신, 잔액 관리 로직 |
| `account-dev-2` | 개발 담당 2 | Vehicle Registry 구현, RFID 태그 발급 워크플로우, JPJ Connector |

### 2.2 협업 인터페이스

| 협업 대상 Agent | 협업 내용 |
|---------------|---------|
| `txn-lead` | `processed.txn.events` 스키마 확정, 잔액 차감 이벤트 규격 |
| `billing-lead` | 계정별 정산 그룹핑 키 정의, 법인·플릿 인보이스 연동 |
| `violation-lead` | 계정 SUSPENDED/CLOSED 상태 시 위반 처리 우선순위 정책 |
| `devops-lead` | JPJ API 크리덴셜 Vault 관리, PostgreSQL RLS 적용 환경 |

---

## 3. 주요 태스크 체크리스트

### 3.1 account-service 구현

#### 3.1.1 개인 계정 (Individual)

- [ ] `POST /api/v1/accounts/individual` — 개인 계정 생성 API
  - 입력 검증: IC 번호 형식 (YYMMDD-PB-###G), 이름, 연락처, 이메일
  - 중복 IC 번호 체크 (concessionaireId 범위 내)
  - 초기 상태: `PENDING_VERIFICATION`
- [ ] eKYC 연동 대기 로직 (비동기 webhook 수신)
- [ ] 계정 활성화 후 상태 → `ACTIVE` 전이
- [ ] TnG eWallet 연동 토큰 등록 (선택)

#### 3.1.2 법인 계정 (Corporate)

- [ ] `POST /api/v1/accounts/corporate` — 법인 계정 생성 API
  - 입력 검증: SSM 등록번호, 법인명, 담당자, GST 번호 (선택)
  - 법인 서류 첨부 (SSM Certificate, 담당자 IC)
- [ ] 법인 관리자 계정 연결 (최소 1명, 최대 5명)
- [ ] 세금계산서 자동 발행 설정 (월별)
- [ ] 신용한도 설정 API (법인 전용)

#### 3.1.3 플릿 계정 (Fleet)

- [ ] `POST /api/v1/accounts/fleet` — 플릿 계정 생성 API
  - 차량 그룹 초기 설정 (최소 5대 이상)
  - 플릿 관리자 지정 (fleet_manager role)
- [ ] 차량 일괄 등록 API (`POST /api/v1/accounts/{id}/vehicles/bulk`)
  - CSV 업로드 지원 (최대 500행)
  - 비동기 처리 + Job Status 조회
- [ ] 플릿별 월간 이용 보고서 자동 생성 스케줄 등록

#### 3.1.4 정부 계정 (Government)

- [ ] `POST /api/v1/accounts/government` — 정부 계정 생성 API
  - 부처 코드 매핑 (KKR, MoF, PDRM 등)
  - 후불 청구 설정 (선불 잔액 불필요)
- [ ] 정부 면제 플래그 연동 (`exemption-service` 협업)
- [ ] 월말 청구서 생성 (Billing 연동)

---

### 3.2 차량 등록 & RFID 태그 발급

#### 3.2.1 차량 등록 워크플로우

- [ ] `POST /api/v1/vehicles` — 차량 등록 API
  - 입력: 차량 번호판 (license_plate), 차종 클래스 (1~5), 계정 ID
  - JPJ API 조회 → 번호판 실소유자 검증
  - 차량 클래스 자동 배정 (Gross Weight 기준)
- [ ] 차량 번호판 형식 검증
  - 말레이시아 표준: `[A-Z]{1,3}[0-9]{1,4}[A-Z]?`
  - 외국 차량 번호판 별도 처리 (Visitor 플래그)
- [ ] 차량 상태 관리: `PENDING_JPJ` → `ACTIVE` → `DEREGISTERED`
- [ ] 차량-계정 다대다 연결 관리 (플릿 차량 공유 시나리오)

#### 3.2.2 RFID 태그 발급 워크플로우

- [ ] `POST /api/v1/vehicles/{vehicleId}/rfid-tags` — RFID 태그 발급 요청
  - 태그 타입: `OBU` (On-Board Unit, RM 50 보증금), `STICKER` (RM 5)
  - 발급 가능 조건: 계정 상태 `ACTIVE`, 잔액 ≥ 최소 임계치
- [ ] RFID 태그 시리얼 번호 자동 생성 (UUID v4 기반)
- [ ] 물리적 배송 요청 이벤트 발행 (`rfid.dispatch.requested` 토픽)
- [ ] 태그 활성화 API (`PATCH /api/v1/rfid-tags/{tagId}/activate`)
  - 활성화 조건: 배송 확인 웹훅 수신 후
- [ ] 태그 분실/손상 재발급 워크플로우
  - 기존 태그 `DEACTIVATED` 처리 후 신규 발급

---

### 3.3 JPJ 연동 (차량 조회 API)

#### 3.3.1 JPJ API 사양

| 항목 | 값 |
|------|---|
| 엔드포인트 | `https://api.jpj.gov.my/v2/vehicles/{plate}` |
| 인증 방식 | OAuth 2.0 Client Credentials |
| 과금 | RM 0.10 / 건 |
| 타임아웃 | 3초 |
| Retry 횟수 | 최대 3회 (Exponential Backoff) |
| SLA | 99.5% Uptime (영업일 08:00~18:00) |
| 야간 장애 | 18:00~08:00 간 차량 등록 시 → 익일 배치 검증 |

#### 3.3.2 연동 태스크

- [ ] JPJ OAuth 토큰 캐시 구현 (Redis, TTL 55분)
- [ ] Circuit Breaker 설정 (Resilience4j)
  - `failureRateThreshold`: 50%
  - `slowCallRateThreshold`: 80% (응답 >2초 시 슬로우콜)
  - `waitDurationInOpenState`: 60초
  - `slidingWindowSize`: 10
- [ ] Retry 설정 (Exponential Backoff)
  - 초기 대기: 500ms → 1000ms → 2000ms
  - Jitter: ±100ms
- [ ] JPJ 응답 캐시 (Redis, TTL 24시간)
  - 동일 번호판 반복 조회 비용 절감
  - 캐시 키: `jpj:vehicle:{licensePlate}`
- [ ] JPJ 야간 다운타임 폴백 처리
  - 임시 `PENDING_JPJ_VERIFICATION` 상태 저장
  - Cron Job: 매일 08:30 미검증 차량 재조회 배치

---

### 3.4 PostgreSQL RLS 콘세셔네어 격리

#### 3.4.1 RLS 설계 원칙

- 모든 계정·차량·RFID 태그 테이블에 `concessionaire_id` 컬럼 필수
- 각 콘세셔네어 서비스 계정은 자신의 `concessionaire_id` 데이터만 조회·수정 가능
- JVC 슈퍼 계정은 ALL 접근 가능 (별도 role: `jvc_admin`)
- RLS 정책은 DB 레벨에서 강제 적용 (Application 레벨 필터 불신)

#### 3.4.2 RLS 구현 태스크

- [ ] `concessionaire_id` 컬럼 추가 및 Index 생성 (accounts, vehicles, rfid_tags 테이블)
- [ ] DB role 생성: `concessionaire_app`, `jvc_admin`
- [ ] RLS 정책 활성화 및 정책 함수 구현
- [ ] 애플리케이션 connection pool 설정 (role-per-concessionaire)
- [ ] RLS 정책 통합 테스트 작성 (다른 콘세셔네어 데이터 접근 불가 검증)

---

### 3.5 계정 상태 관리

#### 3.5.1 상태 전이 다이어그램

```
                    [eKYC 성공]
PENDING_VERIFICATION ──────────► ACTIVE
         │                         │
         │ [eKYC 실패]              │ [위반 누적 / 미납]
         ▼                         ▼
      REJECTED                SUSPENDED
                                  │
                                  │ [90일 미해결]
                                  ▼
                              CLOSED
                                  │
                                  │ [데이터 보존 7년 후]
                                  ▼
                              ARCHIVED
```

#### 3.5.2 상태 관리 태스크

- [ ] 상태 머신 구현 (`AccountStateMachine` 클래스)
  - 허용된 전이만 실행 (유효하지 않은 전이 시 `InvalidStateTransitionException`)
  - 모든 전이 이력 `account_state_history` 테이블에 기록
- [ ] `ACTIVE → SUSPENDED` 트리거 조건 설정
  - 위반 Tier 3 이상 진입 시 자동 전이
  - 잔액 마이너스 90일 초과 시
- [ ] `SUSPENDED → ACTIVE` 복원 워크플로우
  - 미납금 전액 납부 확인
  - 관리자 수동 승인 또는 자동 복원 조건 충족
- [ ] `CLOSED` 전이 시 RFID 태그 일괄 비활성화
- [ ] 계정 상태 변경 이벤트 발행 (`account.status.changed` 토픽)

---

### 3.6 잔액 관리 & 자동 충전 트리거

#### 3.6.1 잔액 관리

- [ ] 잔액 조회 API (`GET /api/v1/accounts/{id}/balance`)
  - Redis 캐시 우선 조회 (TTL 30초)
  - 캐시 미스 시 PostgreSQL 조회 후 캐시 갱신
- [ ] 잔액 차감 이벤트 소비 (`processed.txn.events` Kafka 토픽)
  - Idempotency Key로 중복 처리 방지 (`txn_id` 기준)
  - 잔액 부족 시 `INSUFFICIENT_BALANCE` 이벤트 발행
- [ ] 잔액 충전 API (`POST /api/v1/accounts/{id}/topup`)
  - 지원 채널: FPX, 크레딧카드, TnG eWallet
  - 최소 충전 금액: RM 20
  - 최대 잔액 한도: 개인 RM 1,000 / 법인·플릿 RM 50,000

#### 3.6.2 자동 충전 트리거

- [ ] 자동 충전 설정 API (`PUT /api/v1/accounts/{id}/auto-topup`)
  - `trigger_threshold`: 임계 잔액 (예: RM 20)
  - `topup_amount`: 충전 금액 (예: RM 100)
  - `payment_method_id`: 저장된 결제 수단
- [ ] 잔액 차감 후 임계치 하향 탐지 로직
  - `processed.txn.events` 소비 시 잔액 갱신 후 즉시 체크
  - 자동 충전 조건 충족 시 `auto.topup.triggered` 이벤트 발행
- [ ] 자동 충전 실패 처리 (결제 수단 만료, 한도 초과 등)
  - 실패 시 Push 알림 발송
  - 3회 연속 실패 시 자동 충전 비활성화 + 관리자 알림

---

## 4. JPJ 연동 핵심 코드 (Circuit Breaker + Retry)

### 4.1 JPJ Connector 구현 (Kotlin + Resilience4j)

```kotlin
@Service
class JpjConnector(
    private val httpClient: WebClient,
    private val redisTemplate: ReactiveRedisTemplate<String, JpjVehicleResponse>,
    private val jpjConfig: JpjConfig,
    circuitBreakerRegistry: CircuitBreakerRegistry,
    retryRegistry: RetryRegistry,
) {
    private val circuitBreaker = circuitBreakerRegistry.circuitBreaker("jpj")
    private val retry = retryRegistry.retry("jpj")

    companion object {
        private const val CACHE_TTL_HOURS = 24L
        private const val CACHE_KEY_PREFIX = "jpj:vehicle:"
    }

    suspend fun lookupVehicle(licensePlate: String): JpjVehicleResponse {
        val cacheKey = "$CACHE_KEY_PREFIX${licensePlate.uppercase()}"

        // 캐시 우선 조회
        redisTemplate.opsForValue().get(cacheKey)
            .awaitFirstOrNull()
            ?.let { return it }

        // Circuit Breaker + Retry 감싸서 JPJ API 호출
        return CircuitBreakerOperator.of(circuitBreaker)
            .let { cbOp ->
                RetryOperator.of(retry)
                    .let { retryOp ->
                        fetchFromJpj(licensePlate)
                            .transformDeferred(retryOp)
                            .transformDeferred(cbOp)
                    }
            }
            .awaitSingle()
            .also { response ->
                // 응답 캐시 저장 (24시간)
                redisTemplate.opsForValue()
                    .set(cacheKey, response, Duration.ofHours(CACHE_TTL_HOURS))
                    .awaitSingleOrNull()
            }
    }

    private fun fetchFromJpj(licensePlate: String): Mono<JpjVehicleResponse> =
        httpClient
            .get()
            .uri("/v2/vehicles/${licensePlate.uppercase()}")
            .retrieve()
            .onStatus(HttpStatusCode::is4xxClientError) { response ->
                response.bodyToMono(String::class.java).flatMap { body ->
                    Mono.error(JpjVehicleNotFoundException("Vehicle not found: $licensePlate, body: $body"))
                }
            }
            .onStatus(HttpStatusCode::is5xxServerError) { response ->
                response.bodyToMono(String::class.java).flatMap { body ->
                    Mono.error(JpjServiceUnavailableException("JPJ service error: $body"))
                }
            }
            .bodyToMono(JpjVehicleResponse::class.java)
            .timeout(Duration.ofSeconds(3))
}
```

### 4.2 Resilience4j 설정 (application.yml)

```yaml
resilience4j:
  circuitbreaker:
    instances:
      jpj:
        registerHealthIndicator: true
        slidingWindowType: COUNT_BASED
        slidingWindowSize: 10
        failureRateThreshold: 50
        slowCallRateThreshold: 80
        slowCallDurationThreshold: 2000ms
        waitDurationInOpenState: 60s
        permittedNumberOfCallsInHalfOpenState: 3
        automaticTransitionFromOpenToHalfOpenEnabled: true

  retry:
    instances:
      jpj:
        maxAttempts: 3
        waitDuration: 500ms
        enableExponentialBackoff: true
        exponentialBackoffMultiplier: 2
        randomizedWaitFactor: 0.1
        retryExceptions:
          - org.springframework.web.reactive.function.client.WebClientRequestException
          - com.bos.account.exception.JpjServiceUnavailableException
        ignoreExceptions:
          - com.bos.account.exception.JpjVehicleNotFoundException
```

### 4.3 야간 폴백 배치 처리

```kotlin
@Component
class JpjNightBatchProcessor(
    private val vehicleRepository: VehicleRepository,
    private val jpjConnector: JpjConnector,
) {
    /**
     * 매일 08:30 — PENDING_JPJ_VERIFICATION 상태 차량 재검증
     */
    @Scheduled(cron = "0 30 8 * * MON-FRI")
    suspend fun retryPendingJpjVerifications() {
        val pendingVehicles = vehicleRepository
            .findAllByStatus(VehicleStatus.PENDING_JPJ_VERIFICATION)

        pendingVehicles.forEach { vehicle ->
            runCatching {
                val jpjResponse = jpjConnector.lookupVehicle(vehicle.licensePlate)
                vehicleRepository.save(
                    vehicle.copy(
                        status = VehicleStatus.ACTIVE,
                        vehicleClass = jpjResponse.vehicleClass,
                        ownerName = jpjResponse.ownerName,
                        verifiedAt = Instant.now(),
                    )
                )
            }.onFailure { ex ->
                log.warn("JPJ re-verification failed for ${vehicle.licensePlate}: ${ex.message}")
            }
        }
    }
}
```

---

## 5. RLS 정책 SQL 예시

### 5.1 테이블 구조 및 RLS 활성화

```sql
-- accounts 테이블 RLS 활성화
ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;
ALTER TABLE accounts FORCE ROW LEVEL SECURITY;

-- vehicles 테이블 RLS 활성화
ALTER TABLE vehicles ENABLE ROW LEVEL SECURITY;
ALTER TABLE vehicles FORCE ROW LEVEL SECURITY;

-- rfid_tags 테이블 RLS 활성화
ALTER TABLE rfid_tags ENABLE ROW LEVEL SECURITY;
ALTER TABLE rfid_tags FORCE ROW LEVEL SECURITY;
```

### 5.2 RLS 정책 함수 및 정책 생성

```sql
-- 현재 세션의 concessionaire_id를 반환하는 함수
CREATE OR REPLACE FUNCTION current_concessionaire_id()
RETURNS UUID AS $$
BEGIN
    RETURN NULLIF(current_setting('app.concessionaire_id', true), '')::UUID;
END;
$$ LANGUAGE plpgsql STABLE SECURITY DEFINER;

-- accounts 테이블: 콘세셔네어 격리 정책
CREATE POLICY concessionaire_isolation_accounts
    ON accounts
    USING (
        concessionaire_id = current_concessionaire_id()
        OR current_user = 'jvc_admin'
    );

-- vehicles 테이블: 콘세셔네어 격리 정책
CREATE POLICY concessionaire_isolation_vehicles
    ON vehicles
    USING (
        concessionaire_id = current_concessionaire_id()
        OR current_user = 'jvc_admin'
    );

-- rfid_tags 테이블: 콘세셔네어 격리 정책
CREATE POLICY concessionaire_isolation_rfid_tags
    ON rfid_tags
    USING (
        concessionaire_id = current_concessionaire_id()
        OR current_user = 'jvc_admin'
    );
```

### 5.3 애플리케이션 연결 설정

```kotlin
@Configuration
class DataSourceConfig(
    private val dataSourceProperties: DataSourceProperties,
) {
    @Bean
    fun dataSource(): DataSource {
        val ds = HikariDataSource().apply {
            jdbcUrl = dataSourceProperties.url
            username = "concessionaire_app"  // RLS 적용 role
            password = dataSourceProperties.password
            connectionInitSql = null
        }
        return ds
    }
}

// 요청별 concessionaire_id 세션 변수 설정 (Coroutine Context)
suspend fun <T> withConcessionaireContext(
    concessionaireId: UUID,
    block: suspend () -> T,
): T = withContext(Dispatchers.IO) {
    dataSource.connection.use { conn ->
        conn.prepareStatement(
            "SET LOCAL app.concessionaire_id = '${concessionaireId}'"
        ).execute()
        block()
    }
}
```

---

## 6. 완료 기준 체크리스트

### 6.1 기능 완료 기준

| 영역 | 기준 항목 | 검증 방법 |
|------|---------|---------|
| 계정 관리 | 4종 계정 유형 생성·조회·수정 API 동작 | Postman 컬렉션 전체 통과 |
| 차량 등록 | JPJ 검증 포함 차량 등록 E2E 완료 | 통합 테스트 시나리오 통과 |
| RFID 태그 | 발급 → 활성화 → 비활성화 전체 워크플로우 | E2E 테스트 통과 |
| JPJ 연동 | Circuit Breaker Open 상태에서 폴백 동작 | 카오스 테스트 (JPJ Mock 장애) |
| RLS | 타 콘세셔네어 데이터 접근 차단 확인 | 보안 테스트 시나리오 |
| 잔액 관리 | 자동 충전 트리거 정확성 | 시뮬레이션 테스트 |

### 6.2 성능 기준

| 지표 | 목표값 |
|------|-------|
| 계정 조회 API P99 응답시간 | < 50ms |
| 차량 등록 (JPJ 캐시 히트) P99 | < 100ms |
| 차량 등록 (JPJ 실제 호출) P99 | < 3,500ms |
| JPJ API 캐시 히트율 | > 70% |
| 잔액 조회 (Redis 캐시 히트) P99 | < 10ms |

### 6.3 테스트 커버리지 기준

- [ ] 단위 테스트 커버리지 ≥ 80% (전체 모듈)
- [ ] JPJ Circuit Breaker 상태 전이 시나리오 테스트 완료
- [ ] RLS 격리 보안 테스트 완료 (콘세셔네어 A가 콘세셔네어 B 데이터 접근 불가)
- [ ] 계정 상태 머신 전체 전이 경로 단위 테스트 완료
- [ ] 자동 충전 트리거 Edge Case 테스트 (잔액 정확히 임계치 일치 시)

---

## 7. 리스크 & 대응

### 7.1 주요 리스크

| 리스크 | 가능성 | 영향 | 대응 방안 |
|-------|-------|------|---------|
| JPJ API 야간·주말 다운타임 | 높음 | 중 | 폴백 `PENDING_JPJ_VERIFICATION` + 익일 배치 재검증 |
| JPJ API 과금 급증 (플릿 대량 등록) | 중간 | 중 | Redis 캐시 24시간 TTL, 캐시 히트율 모니터링 |
| RLS 정책 설정 오류 → 데이터 유출 | 낮음 | 매우 높음 | 배포 전 보안 테스트 필수, `security-reviewer` Agent 검토 |
| PostgreSQL connection pool 고갈 | 중간 | 높음 | 콘세셔네어별 pool 크기 제한, HikariCP `maximumPoolSize` 조정 |
| 자동 충전 중복 실행 (이중 청구) | 낮음 | 높음 | Idempotency Key (`auto_topup_job_id`) + DB Unique Constraint |

### 7.2 의존성 리스크

| 의존성 | 리스크 | 대응 |
|-------|-------|------|
| Phase 3 `processed.txn.events` 스키마 미확정 | Kafka Consumer 구현 지연 | Phase 3 완료 즉시 스키마 동결, Contract Test 도입 |
| JPJ API 인증서 갱신 주기 불명확 | 연동 중단 위험 | 인증서 만료 30일 전 알림 자동화 |

---

## 8. GSD 명령어 / 참조 문서

### 8.1 GSD 실행 명령어

```bash
# Phase 4 시작
/gsd:execute-phase phase=4 agents="account-lead,account-dev-1,account-dev-2"

# Phase 4 진행 상황 확인
/gsd:progress phase=4

# Phase 4 완료 검증
/gsd:verify-work phase=4

# JPJ 연동 전용 카오스 테스트 실행
/gsd:audit-uat scenario="jpj-chaos" phase=4
```

### 8.2 참조 문서

| 문서 | 경로 | 참조 목적 |
|------|------|---------|
| 서비스 도메인 설계 | `02_system/02_service_domains.md` | account-service 도메인 경계 |
| 외부 연동 명세 | `02_system/05_external_integration.md` | JPJ API 사양, OAuth 설정 |
| 데이터 모델 | `03_data/02_data_model.md` | accounts, vehicles, rfid_tags 테이블 구조 |
| RBAC 설계 | `03_data/03_rbac_design.md` | concessionaire_app role, jvc_admin role |
| 보안 & 컴플라이언스 | `03_data/05_security_compliance.md` | PDPA 준수, RLS 정책 요구사항 |
| 결제 아키텍처 | `01_business/05_payment_architecture.md` | 자동 충전 채널, 잔액 한도 정책 |

---

*Malaysia SLFF/MLFF Tolling BOS — Phase 4 계정 & 차량 관리 v1.0*
*생성일: 2026-04 | 담당: account-lead, account-dev×2*
