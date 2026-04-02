# Phase 3: 트랜잭션 처리 엔진
## 06_phases/03_phase03_txn.md
## v1.0 | 2026-04 | 참조: 02_system/02_service_domains.md, 03_data/02_data_model.md

---

> **Agent 사용 지침**
> `txn-lead`, `txn-dev` Agent가 과금 로직 구현 시 반드시 로드.
> 본 문서는 Phase 3 실행의 유일한 정식 기준 문서이며, 모든 과금 로직의 구현 기준으로 사용된다.
> 금액 계산 관련 코드는 반드시 `txn-lead` 리뷰 후 머지한다.

---

## 1. Phase 개요

### 1.1 목적 및 범위

Phase 3은 Malaysia SLFF/MLFF Tolling BOS의 **핵심 트랜잭션 처리 엔진**을 구축하는 단계다. Phase 2에서 구성한 Kafka 파이프라인으로부터 원시 이벤트를 소비하여, SLFF/MLFF 두 운영 모델에 걸친 과금 로직을 실행하고, 처리 결과를 하위 서비스(정산, 위반, 감사)로 전달하는 `txn-service`를 완성한다.

**핵심 목표:**
- SLFF Channel A (RFID) 과금 로직 완성 (즉시 과금)
- MLFF Entry-Exit 매칭 엔진 구현 (Redis 세션 기반)
- Channel B (TnG eWallet) 과금 처리 연동
- 요금 클래스 조회 성능 최적화 (P99 < 10ms)
- Outbox Pattern 기반 이벤트 발행 (Exactly-once 보장)
- Hyperledger Fabric 감사 로그 연동
- 10,000 TPS 달성

### 1.2 Phase 연계

| 구분 | 내용 |
|------|------|
| **선행 Phase** | Phase 2 — 커뮤니케이션 레이어 (Kafka 토픽 5개, Consumer Group, Protobuf 스키마 등록 완료 필수) |
| **후행 Phase** | Phase 4 — 결제 게이트웨이 연동 / Phase 5 — 위반 처리 / Phase 6 — 정산 엔진 (모두 `processed.txn.events` 토픽 의존) |
| **예상 기간** | **3주** (Sprint 5~7) |
| **병렬 가능 작업** | SLFF 과금 로직 ↔ MLFF 매칭 엔진 (독립 개발 후 통합) |

### 1.3 아키텍처 포지션

```
[Kafka: raw.rfid.events]   [Kafka: raw.anpr.events]
          │                          │
          └──────────┬───────────────┘
                     ▼
          ┌──────────────────────┐
          │     txn-service      │  ← Phase 3 구현 영역
          │                      │
          │  ┌────────────────┐  │
          │  │ SLFF Processor │  │  Channel A 즉시 과금
          │  ├────────────────┤  │
          │  │ MLFF Matcher   │  │  Entry-Exit 매칭
          │  ├────────────────┤  │
          │  │ TnG Processor  │  │  Channel B 과금
          │  └────────────────┘  │
          │         │            │
          │  [Redis Session]     │  MLFF 세션 관리
          │  [TollFee Cache]     │  요금 캐시
          └──────────┬───────────┘
                     │
          ┌──────────┴──────────────────┐
          │                             │
          ▼                             ▼
[processed.txn.events]      [Hyperledger Fabric]
  (Phase 4/5/6 소비)           (감사 로그)
```

### 1.4 주요 비즈니스 규칙 요약

| 운영 모드 | 채널 | 과금 시점 | 매칭 방식 |
|---------|------|---------|---------|
| SLFF | Channel A (RFID) | 통과 즉시 | 단일 플라자 이벤트 |
| SLFF | Channel B (TnG) | 통과 즉시 | 단일 플라자 이벤트 |
| MLFF | Channel A (RFID) | Exit 시점 | Entry-Exit session_id 매칭 |
| MLFF | Channel B (TnG) | Exit 시점 | Entry-Exit session_id 매칭 |

---

## 2. 담당 Agent 및 역할 분담

### 2.1 Phase 3 참여 Agent

| Agent | 역할 | 주요 책임 영역 |
|-------|------|--------------|
| **txn-lead** | Phase 3 리드 | 과금 로직 설계 및 최종 리뷰, 성능 목표 달성 책임 |
| **txn-dev-1** | 백엔드 개발 #1 | SLFF 과금 로직, Channel B(TnG) 연동, Outbox Pattern |
| **txn-dev-2** | 백엔드 개발 #2 | MLFF Entry-Exit 매칭, Redis 세션 관리, Idempotency |

### 2.2 협업 방식

```
txn-lead
  ├── txn-dev-1: SLFF + Channel B 구현 위임
  │   ├── 요금 계산 로직 → txn-lead 코드 리뷰 필수
  │   └── TnG API 연동 → 연동 테스트 후 스테이징 배포
  └── txn-dev-2: MLFF 매칭 엔진 구현 위임
      ├── Redis 세션 TTL 정책 → txn-lead 승인 필수
      └── Idempotency Key 설계 → txn-lead 리뷰 후 확정

보고 라인: txn-lead → arch-lead (주간) → PM (마일스톤 기준)
의존 관계: txn-dev-1 ← txn-dev-2 (TollFee 캐시 인터페이스 공유)
```

### 2.3 코드 리뷰 정책

- **과금 금액 계산 코드**: 반드시 `txn-lead` + `arch-lead` 2인 이상 리뷰
- **Redis 세션 TTL 변경**: `txn-lead` 승인 필수 (비즈니스 영향도 검토)
- **Kafka Consumer 변경**: `devops-lead` 성능 영향 평가 포함

---

## 3. 주요 태스크 체크리스트

### 3.1 txn-service Spring Boot 구현

- [ ] **T3-01** Spring Boot 3.x 프로젝트 생성 (`txn-service`)
  - Java 21 (Virtual Thread 활성화)
  - 의존성: Spring Web, Spring Kafka, Spring Data Redis, Spring Data JPA
  - 빌드: Gradle Kotlin DSL
- [ ] **T3-02** 멀티 모듈 구조 설정

```
txn-service/
├── txn-api/           # REST API (내부 조회용)
├── txn-core/          # 과금 로직 (순수 Java, 프레임워크 독립)
├── txn-kafka/         # Kafka Consumer/Producer
├── txn-redis/         # Redis 세션 관리
├── txn-persistence/   # JPA 엔티티 및 Repository
└── txn-blockchain/    # Hyperledger Fabric 연동
```

- [ ] **T3-03** Virtual Thread 설정 (`spring.threads.virtual.enabled=true`)
- [ ] **T3-04** Actuator + Micrometer + Prometheus 설정
- [ ] **T3-05** 서비스 헬스 체크 구현 (Redis, Kafka, DB, Fabric 연결 포함)

### 3.2 SLFF 과금 로직 (Channel A)

- [ ] **T3-06** `SLFFTollCalculator` 서비스 구현
  - 입력: `SLFFEvent` (PlazaID, LaneID, VehicleClass, PaymentChannel)
  - 출력: `TollCalculationResult` (Amount, TollFeeId, Breakdown)
- [ ] **T3-07** 요금 테이블 조회 로직 구현

```
요금 결정 순서:
1. PlazaID + VehicleClass → 기본 요금 조회
2. 시간대 할인 적용 (야간 할인, 주말 할인)
3. 구독 할인 적용 (계절권 소지 여부)
4. 최종 청구 금액 산정
```

- [ ] **T3-08** SLFF 즉시 과금 트랜잭션 구현 (DB + Outbox 원자적 처리)
- [ ] **T3-09** SLFF 단위 테스트 작성 (모든 VehicleClass × 요금제 조합, 커버리지 100%)
- [ ] **T3-10** SLFF 통합 테스트 작성 (Kafka 이벤트 → DB 저장 → Outbox 발행)

### 3.3 MLFF Entry-Exit 매칭 (Redis 세션)

- [ ] **T3-11** `MLFFSessionManager` 서비스 구현
  - Entry 이벤트 수신 시 Redis에 세션 저장
  - Exit 이벤트 수신 시 session_id로 Entry 세션 조회 및 매칭
- [ ] **T3-12** Redis 세션 키 설계

```
Key   : mlff:session:{session_id}
Value : MLFFSessionData (JSON 직렬화)
TTL   : 24시간 (최대 고속도로 주행 시간 + 여유)
```

- [ ] **T3-13** TTL 만료 처리 로직 구현
  - TTL 만료 세션 → `violation.events`에 "EXIT_TIMEOUT" 위반 이벤트 발행
  - Keyspace Notification 활성화 (`notify-keyspace-events KEA`)
- [ ] **T3-14** MLFF 매칭 성공 시 과금 처리

```
매칭 완료 → 구간 거리 계산 → 요금 테이블 조회 → 과금 트랜잭션
Entry PlazaID + Exit PlazaID → 구간 요금 결정
```

- [ ] **T3-15** 중복 매칭 방어 로직 구현 (동일 session_id 중복 Exit 처리)
- [ ] **T3-16** MLFF 단위 테스트 (TTL 만료, 중복 Exit, 정상 매칭 시나리오)

### 3.4 Channel B (TnG) 과금 처리

- [ ] **T3-17** TnG API 클라이언트 구현 (`TnGPaymentClient`)
  - REST API 기반 (TnG 제공 Sandbox 환경 연동)
  - Retry 정책: 3회, Exponential Backoff (1s → 2s → 4s)
  - Circuit Breaker: 연속 5회 실패 시 OPEN, 30초 후 HALF_OPEN
- [ ] **T3-18** Channel B 과금 흐름 구현

```
[Kafka: raw.rfid.events (PaymentChannel=CHANNEL_B_TNG)]
  → TnG API 호출 (deduct_balance)
  → 성공: processed.txn.events 발행
  → 실패: DLQ 전송 + 재처리 스케줄
```

- [ ] **T3-19** TnG API 응답 처리 (잔액 부족, 카드 만료, 서비스 불가 등)
- [ ] **T3-20** TnG 연동 장애 시 fallback 로직 (미수 처리 → 위반 이벤트)
- [ ] **T3-21** TnG Sandbox 통합 테스트 (MockServer 기반)

### 3.5 요금 클래스 조회 (<10ms P99, Redis 캐시)

- [ ] **T3-22** `TollFeeCache` 서비스 구현

```
캐시 전략: Cache-Aside (Look-Aside)
Key  : tollfee:{plaza_id}:{vehicle_class}
Value: TollFeeEntry { baseAmount, nightDiscount, weekendDiscount }
TTL  : 1시간 (변경 시 즉시 무효화)
```

- [ ] **T3-23** 캐시 워밍업 구현 (서비스 시작 시 전체 요금 테이블 사전 로드)
- [ ] **T3-24** 캐시 무효화 이벤트 처리 (`toll-fee-update` Kafka 토픽 구독)
- [ ] **T3-25** 캐시 미스 시 DB Fallback 로직 구현 (타임아웃: 5ms)
- [ ] **T3-26** 캐시 적중률 메트릭 노출 (목표: > 99.5%)
- [ ] **T3-27** 요금 조회 P99 성능 테스트 (목표: < 10ms)

### 3.6 Outbox Pattern 구현

- [ ] **T3-28** `outbox_events` 테이블 생성

```sql
CREATE TABLE outbox_events (
    id            UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    aggregate_id  VARCHAR(64) NOT NULL,        -- txn_id 또는 session_id
    event_type    VARCHAR(64) NOT NULL,        -- 'TXN_PROCESSED', 'VIOLATION_DETECTED' 등
    payload       JSONB       NOT NULL,
    kafka_topic   VARCHAR(128) NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    published_at  TIMESTAMPTZ,
    status        VARCHAR(16) NOT NULL DEFAULT 'PENDING',  -- PENDING/PUBLISHED/FAILED
    retry_count   INT         NOT NULL DEFAULT 0
);
CREATE INDEX idx_outbox_status_created ON outbox_events (status, created_at)
    WHERE status = 'PENDING';
```

- [ ] **T3-29** `OutboxPublisher` 스케줄러 구현
  - 500ms 주기로 PENDING 이벤트 조회 (최대 500건 배치)
  - Kafka 발행 성공 시 `published_at` 업데이트
  - 발행 실패 시 `retry_count` 증가, 3회 초과 시 FAILED 처리
- [ ] **T3-30** 과금 트랜잭션 + Outbox 원자적 저장 구현

```java
@Transactional
public void processTollTransaction(TollCalculationResult result) {
    // 1. txn_records 테이블 저장
    TollTransaction txn = txnRepository.save(result.toEntity());
    // 2. outbox_events 테이블 저장 (동일 트랜잭션)
    OutboxEvent event = OutboxEvent.of(txn.getId(), "TXN_PROCESSED",
        txn.toEventPayload(), "processed.txn.events");
    outboxRepository.save(event);
    // 3. 커밋 → Publisher가 비동기로 Kafka 발행
}
```

- [ ] **T3-31** Outbox 재처리 API 구현 (`POST /admin/outbox/retry`)
- [ ] **T3-32** Outbox 모니터링 메트릭 (PENDING 적체, 발행 지연 시간)

### 3.7 Idempotency Key 처리 (중복 방지)

- [ ] **T3-33** Idempotency Key 설계

```
SLFF: {plaza_id}_{lane_id}_{event_time_epoch_ms}_{rfid_tag_id}
MLFF: {session_id}_{exit_plaza_id}
```

- [ ] **T3-34** Redis 기반 중복 감지 구현

```
Key   : idempotency:{idempotency_key}
Value : txn_id (처리된 트랜잭션 ID)
TTL   : 48시간
```

- [ ] **T3-35** 중복 이벤트 처리 로직

```
중복 감지 시 → 원본 txn_id 반환 (재처리 스킵)
              → 중복 수신 메트릭 증가
              → 경고 로그 기록
```

- [ ] **T3-36** Idempotency 단위 테스트 (동일 이벤트 3회 발행 → 1회만 처리 확인)
- [ ] **T3-37** 동시성 테스트 (동일 이벤트 동시 10개 요청 → 1개만 처리 확인)

### 3.8 트랜잭션 감사 로그 (Hyperledger Fabric)

- [ ] **T3-38** Hyperledger Fabric Java SDK 연동 (`fabric-gateway-java`)
- [ ] **T3-39** `TollAuditChaincode` 호출 구현

```
채널   : toll-audit-channel
체인코드: TollAuditCC
함수   : recordTransaction(txn_id, plaza_id, amount, timestamp, vehicle_hash)
```

- [ ] **T3-40** 감사 로그 비동기 처리 구현 (과금 처리 성능 영향 최소화)
  - Virtual Thread 기반 비동기 Fabric 호출
  - Fabric 호출 실패 시 별도 재시도 큐 사용 (과금 롤백 불가)
- [ ] **T3-41** 차량 ID 해싱 처리 (SHA-256, PDPA 개인정보 보호)
- [ ] **T3-42** Fabric 연결 장애 시 로컬 감사 로그 fallback (영구 저장)
- [ ] **T3-43** 감사 로그 조회 API 구현 (`GET /audit/transactions/{txn_id}`)

---

## 4. MLFF 매칭 핵심 코드 패턴 (Java 21 가상 스레드)

### 4.1 MLFF 세션 데이터 모델

```java
@JsonNaming(PropertyNamingStrategies.SnakeCaseStrategy.class)
public record MLFFSessionData(
    String      sessionId,
    String      entryPlazaId,
    String      entryLaneId,
    String      rfidTagId,
    String      plateNumber,
    VehicleClass vehicleClass,
    Instant     entryTime,
    String      entryEquipmentId,
    double      gantrySpeedKmh
) {
    public static MLFFSessionData fromEvent(MLFFEntryEvent event) {
        return new MLFFSessionData(
            event.getSessionId(),
            event.getEntryPlaza().getPlazaId(),
            event.getEntryPlaza().getLaneId(),
            event.getRfidTagId(),
            event.getPlateNumber(),
            event.getVehicleClass(),
            Instant.ofEpochSecond(
                event.getEntryTime().getSeconds(),
                event.getEntryTime().getNanos()),
            event.getEntryEquipmentId(),
            event.getGantrySpeedKmh()
        );
    }
}
```

### 4.2 MLFF 세션 관리 서비스

```java
@Service
@Slf4j
public class MLFFSessionManager {

    private static final String SESSION_KEY_PREFIX = "mlff:session:";
    private static final Duration SESSION_TTL       = Duration.ofHours(24);

    private final ReactiveRedisTemplate<String, MLFFSessionData> redisTemplate;
    private final MeterRegistry meterRegistry;

    public MLFFSessionManager(
            ReactiveRedisTemplate<String, MLFFSessionData> redisTemplate,
            MeterRegistry meterRegistry) {
        this.redisTemplate = redisTemplate;
        this.meterRegistry = meterRegistry;
    }

    // Entry 이벤트: 세션 저장
    public Mono<Void> createSession(MLFFEntryEvent entryEvent) {
        String key  = SESSION_KEY_PREFIX + entryEvent.getSessionId();
        MLFFSessionData data = MLFFSessionData.fromEvent(entryEvent);

        return redisTemplate.opsForValue()
            .set(key, data, SESSION_TTL)
            .doOnSuccess(v -> {
                log.debug("MLFF 세션 생성 [session_id={}]", entryEvent.getSessionId());
                meterRegistry.counter("mlff.session.created").increment();
            })
            .then();
    }

    // Exit 이벤트: 세션 조회 후 삭제 (원자적)
    public Mono<Optional<MLFFSessionData>> consumeSession(String sessionId) {
        String key = SESSION_KEY_PREFIX + sessionId;

        return redisTemplate.opsForValue()
            .getAndDelete(key)  // 조회와 동시에 삭제 (중복 처리 방지)
            .map(Optional::of)
            .defaultIfEmpty(Optional.empty())
            .doOnNext(result -> {
                if (result.isEmpty()) {
                    log.warn("MLFF 세션 미존재 [session_id={}] — 위반 처리 대상", sessionId);
                    meterRegistry.counter("mlff.session.miss").increment();
                }
            });
    }
}
```

### 4.3 MLFF 매칭 엔진 (가상 스레드 기반)

```java
@Service
@Slf4j
public class MLFFMatchingEngine {

    private final MLFFSessionManager    sessionManager;
    private final TollFeeCache          tollFeeCache;
    private final TollTransactionWriter txnWriter;
    private final ViolationEventPublisher violationPublisher;

    // Virtual Thread 실행자 (Spring Boot 3.2+ 자동 설정)
    private final Executor virtualThreadExecutor =
        Executors.newVirtualThreadPerTaskExecutor();

    public MLFFMatchingEngine(
            MLFFSessionManager sessionManager,
            TollFeeCache tollFeeCache,
            TollTransactionWriter txnWriter,
            ViolationEventPublisher violationPublisher) {
        this.sessionManager     = sessionManager;
        this.tollFeeCache       = tollFeeCache;
        this.txnWriter          = txnWriter;
        this.violationPublisher = violationPublisher;
    }

    @KafkaListener(topics = "raw.rfid.events", groupId = "txn-processor-group")
    public void handleEvent(ConsumerRecord<String, Object> record, Acknowledgment ack) {
        // 가상 스레드에서 처리 (블로킹 I/O 효율화)
        CompletableFuture.runAsync(() -> {
            try {
                if (record.value() instanceof MLFFEntryEvent entry) {
                    processEntry(entry);
                } else if (record.value() instanceof MLFFExitEvent exit) {
                    processExit(exit);
                }
            } catch (Exception e) {
                log.error("MLFF 처리 오류 [offset={}]: {}", record.offset(), e.getMessage(), e);
            }
        }, virtualThreadExecutor).join();

        ack.acknowledge();
    }

    private void processEntry(MLFFEntryEvent entry) {
        sessionManager.createSession(entry).block();
        log.info("MLFF Entry 세션 생성 완료 [session_id={}]", entry.getSessionId());
    }

    private void processExit(MLFFExitEvent exit) {
        Optional<MLFFSessionData> sessionOpt =
            sessionManager.consumeSession(exit.getSessionId()).block();

        if (sessionOpt.isEmpty()) {
            // 세션 없음 → 무단 통행 위반
            violationPublisher.publishNoEntryViolation(exit);
            return;
        }

        MLFFSessionData entry = sessionOpt.get();

        // 구간 요금 계산
        TollFeeEntry feeEntry = tollFeeCache
            .getInterSegmentFee(entry.entryPlazaId(), exit.getExitPlaza().getPlazaId(),
                entry.vehicleClass())
            .orElseThrow(() -> new TollFeeNotFoundException(
                "구간 요금 미정의: " + entry.entryPlazaId() + " → " + exit.getExitPlaza().getPlazaId()));

        // 트랜잭션 기록 + Outbox 이벤트 발행 (원자적)
        txnWriter.writeMLFFTransaction(entry, exit, feeEntry);

        log.info("MLFF 매칭 완료 [session_id={}, amount={}]",
            exit.getSessionId(), feeEntry.getFinalAmount());
    }
}
```

---

## 5. Redis 세션 관리 코드

### 5.1 Redis 설정

```java
@Configuration
public class RedisConfig {

    @Bean
    public ReactiveRedisConnectionFactory reactiveRedisConnectionFactory(
            @Value("${spring.data.redis.host}") String host,
            @Value("${spring.data.redis.port}") int port) {
        return new LettuceConnectionFactory(host, port);
    }

    @Bean
    public ReactiveRedisTemplate<String, MLFFSessionData> mlffSessionTemplate(
            ReactiveRedisConnectionFactory factory) {
        Jackson2JsonRedisSerializer<MLFFSessionData> serializer =
            new Jackson2JsonRedisSerializer<>(MLFFSessionData.class);
        RedisSerializationContext<String, MLFFSessionData> ctx =
            RedisSerializationContext.<String, MLFFSessionData>newSerializationContext(
                new StringRedisSerializer())
                .value(serializer)
                .build();
        return new ReactiveRedisTemplate<>(factory, ctx);
    }

    @Bean
    public ReactiveRedisTemplate<String, String> idempotencyTemplate(
            ReactiveRedisConnectionFactory factory) {
        RedisSerializationContext<String, String> ctx =
            RedisSerializationContext.string();
        return new ReactiveRedisTemplate<>(factory, ctx);
    }
}
```

### 5.2 Redis Keyspace Notification (TTL 만료 감지)

```java
@Component
@Slf4j
public class MLFFSessionExpiryListener
        implements MessageListener {

    private static final String EXPIRE_PATTERN = "__keyevent@0__:expired";

    private final ViolationEventPublisher violationPublisher;

    public MLFFSessionExpiryListener(ViolationEventPublisher violationPublisher) {
        this.violationPublisher = violationPublisher;
    }

    @Override
    public void onMessage(Message message, byte[] pattern) {
        String expiredKey = new String(message.getBody(), StandardCharsets.UTF_8);

        if (expiredKey.startsWith("mlff:session:")) {
            String sessionId = expiredKey.substring("mlff:session:".length());
            log.warn("MLFF 세션 TTL 만료 [session_id={}] — EXIT_TIMEOUT 위반 처리", sessionId);
            violationPublisher.publishExitTimeoutViolation(sessionId);
        }
    }

    @Bean
    public RedisMessageListenerContainer redisMessageListenerContainer(
            RedisConnectionFactory factory) {
        RedisMessageListenerContainer container = new RedisMessageListenerContainer();
        container.setConnectionFactory(factory);
        container.addMessageListener(this,
            new PatternTopic(EXPIRE_PATTERN));
        return container;
    }
}
```

### 5.3 요금 캐시 (TollFeeCache)

```java
@Service
@Slf4j
public class TollFeeCache {

    private static final String FEE_KEY_PREFIX     = "tollfee:";
    private static final String SEGMENT_KEY_PREFIX = "tollfee:segment:";
    private static final Duration CACHE_TTL        = Duration.ofHours(1);

    private final ReactiveRedisTemplate<String, String> redisTemplate;
    private final TollFeeRepository tollFeeRepository;
    private final ObjectMapper objectMapper;

    public TollFeeCache(
            ReactiveRedisTemplate<String, String> redisTemplate,
            TollFeeRepository tollFeeRepository,
            ObjectMapper objectMapper) {
        this.redisTemplate    = redisTemplate;
        this.tollFeeRepository = tollFeeRepository;
        this.objectMapper     = objectMapper;
    }

    // 단일 플라자 요금 조회 (SLFF)
    public Optional<TollFeeEntry> getPlazaFee(String plazaId, VehicleClass vehicleClass) {
        String cacheKey = FEE_KEY_PREFIX + plazaId + ":" + vehicleClass.name();
        String cached = redisTemplate.opsForValue().get(cacheKey).block();

        if (cached != null) {
            return Optional.of(deserialize(cached));
        }

        // Cache Miss → DB 조회
        return tollFeeRepository.findByPlazaIdAndVehicleClass(plazaId, vehicleClass)
            .map(entity -> {
                String json = serialize(entity.toTollFeeEntry());
                redisTemplate.opsForValue().set(cacheKey, json, CACHE_TTL).subscribe();
                return entity.toTollFeeEntry();
            });
    }

    // 구간 요금 조회 (MLFF)
    public Optional<TollFeeEntry> getInterSegmentFee(
            String entryPlazaId, String exitPlazaId, VehicleClass vehicleClass) {
        String cacheKey = SEGMENT_KEY_PREFIX
            + entryPlazaId + ":" + exitPlazaId + ":" + vehicleClass.name();
        String cached = redisTemplate.opsForValue().get(cacheKey).block();

        if (cached != null) {
            return Optional.of(deserialize(cached));
        }

        return tollFeeRepository.findSegmentFee(entryPlazaId, exitPlazaId, vehicleClass)
            .map(entity -> {
                String json = serialize(entity.toTollFeeEntry());
                redisTemplate.opsForValue().set(cacheKey, json, CACHE_TTL).subscribe();
                return entity.toTollFeeEntry();
            });
    }

    @EventListener
    public void onTollFeeUpdated(TollFeeUpdatedEvent event) {
        // 변경된 플라자 관련 캐시 즉시 무효화
        String pattern = FEE_KEY_PREFIX + event.getPlazaId() + ":*";
        redisTemplate.keys(pattern)
            .flatMap(key -> redisTemplate.delete(key))
            .subscribe(count ->
                log.info("요금 캐시 무효화 완료 [plaza_id={}, count={}]",
                    event.getPlazaId(), count));
    }

    private TollFeeEntry deserialize(String json) {
        try {
            return objectMapper.readValue(json, TollFeeEntry.class);
        } catch (JsonProcessingException e) {
            throw new CacheDeserializationException("요금 캐시 역직렬화 오류", e);
        }
    }

    private String serialize(TollFeeEntry entry) {
        try {
            return objectMapper.writeValueAsString(entry);
        } catch (JsonProcessingException e) {
            throw new CacheSerializationException("요금 캐시 직렬화 오류", e);
        }
    }
}
```

---

## 6. 완료 기준 체크리스트

### 6.1 기능 완료 기준

- [ ] SLFF Channel A 과금 로직: 모든 VehicleClass(CLASS_1~5) 정확한 금액 계산
- [ ] SLFF Channel B (TnG) 과금: Sandbox 환경 통합 테스트 통과
- [ ] MLFF Entry-Exit 매칭: 정상 매칭 시나리오 통합 테스트 통과
- [ ] MLFF TTL 만료: EXIT_TIMEOUT 위반 이벤트 자동 생성 확인
- [ ] Outbox Pattern: 과금 트랜잭션과 이벤트 발행 원자성 보장 테스트 통과
- [ ] Idempotency: 동일 이벤트 100회 중복 발행 시 1회만 과금 처리 확인
- [ ] Hyperledger Fabric: 모든 과금 트랜잭션 감사 로그 기록 확인

### 6.2 성능 완료 기준

- [ ] **전체 처리량**: **10,000 TPS** 달성 (SLFF + MLFF 혼합 부하)
- [ ] **SLFF 지연**: P99 < 100ms (Kafka 소비 → DB 저장 → Outbox 발행)
- [ ] **MLFF 지연**: P99 < 150ms (Entry-Exit 매칭 포함)
- [ ] **요금 캐시 조회**: P99 < **10ms** 달성
- [ ] **Redis 세션 저장/조회**: P99 < 5ms
- [ ] **캐시 적중률**: > 99.5% (워밍업 후 정상 부하 기준)
- [ ] **TnG API 호출**: P99 < 200ms (Circuit Breaker 동작 확인 포함)

### 6.3 데이터 정합성 기준

- [ ] 과금 금액 정밀도: 소수점 2자리 (MYR 기준) 정확도 100%
- [ ] Outbox PENDING → PUBLISHED 전환 시간: 평균 < 1초
- [ ] DLQ 비율: 정상 부하 조건에서 < 0.01%
- [ ] MLFF 미매칭 위반 이벤트 발행: 누락율 0%

### 6.4 보안 및 컴플라이언스 기준

- [ ] 차량 번호판 Fabric 저장 시 SHA-256 해싱 적용 확인
- [ ] PDPA 준수: 원본 번호판 DB 저장 기간 정책 적용 (90일 후 해싱 대체)
- [ ] TnG API 인증 토큰 Vault 저장 확인 (하드코딩 금지)

---

## 7. 리스크 & 대응 방안

| # | 리스크 | 심각도 | 발생 가능성 | 대응 방안 |
|---|--------|--------|-----------|---------|
| R1 | MLFF Entry 세션 유실 (Redis 장애) | CRITICAL | LOW | Redis Sentinel/Cluster 구성, 세션 손실 시 위반 처리 후 수동 검토 프로세스 수립 |
| R2 | 동일 session_id 중복 Exit 이벤트 (네트워크 중복 전송) | HIGH | MEDIUM | `getAndDelete` 원자적 연산으로 중복 처리 방지, Idempotency Key 이중 확인 |
| R3 | TnG API 장기 장애로 Channel B 미수 누적 | HIGH | LOW | Circuit Breaker OPEN 시 미수 처리 큐 전환, 복구 후 자동 재처리 파이프라인 |
| R4 | 요금 테이블 캐시 오염 (잘못된 요금 적용) | CRITICAL | LOW | 캐시 업데이트 시 검증 단계 필수, 관리자 알림 후 수동 승인 절차 |
| R5 | Hyperledger Fabric 성능 병목 (10,000 TPS 달성 실패) | HIGH | MEDIUM | 비동기 비차단 Fabric 호출, 과금과 감사 로그 분리 처리 (Fabric 실패가 과금 롤백 트리거 불가) |
| R6 | Virtual Thread 기반 Redis 블로킹 호출 성능 예측 불일치 | MEDIUM | MEDIUM | 사전 JMH 벤치마크 수행, 필요 시 WebFlux 기반 Reactive 전환 검토 |
| R7 | 10,000 TPS 달성 실패 | HIGH | MEDIUM | 수평 확장(Pod 추가), DB 커넥션 풀 최적화 (HikariCP), 배치 삽입 전환 검토 |

---

## 8. GSD 실행 명령어

### 8.1 Phase 3 시작

```bash
# Phase 3 실행 (Phase 2 완료 확인 후)
/gsd:execute-phase phase=03 agent=txn-lead

# 병렬 작업 시작 (SLFF ↔ MLFF 독립 개발)
/gsd:do T3-06  # txn-dev-1: SLFF 과금 로직
/gsd:do T3-11  # txn-dev-2: MLFF 세션 매칭 (병렬)
```

### 8.2 단계별 실행

```bash
# 1단계: 기반 구현 (T3-01 ~ T3-05)
/gsd:do T3-01 T3-02 T3-03 T3-04 T3-05

# 2단계: 핵심 과금 로직 (병렬)
/gsd:do T3-06 T3-07 T3-08  # SLFF (txn-dev-1)
/gsd:do T3-11 T3-12 T3-13  # MLFF (txn-dev-2, 병렬)

# 3단계: 채널 연동
/gsd:do T3-17 T3-18 T3-19  # Channel B TnG

# 4단계: 인프라 패턴
/gsd:do T3-22 T3-23 T3-24  # 요금 캐시
/gsd:do T3-28 T3-29 T3-30  # Outbox Pattern
/gsd:do T3-33 T3-34 T3-35  # Idempotency

# 5단계: 감사 로그
/gsd:do T3-38 T3-39 T3-40  # Hyperledger Fabric
```

### 8.3 진행 상황 확인

```bash
# Phase 3 전체 진행률
/gsd:progress phase=03

# 미완료 태스크 목록
/gsd:check-todos phase=03

# 성능 테스트 실행
/gsd:do T3-27  # 요금 캐시 P99 테스트
```

### 8.4 완료 처리

```bash
# Phase 3 마일스톤 완료 선언 (arch-lead 승인 필요)
/gsd:complete-milestone phase=03

# Phase 4 착수 (Phase 3 완료 후)
/gsd:execute-phase phase=04 agent=payment-lead
```

### 8.5 디버깅 명령어

```bash
# 처리 중인 트랜잭션 확인
kafka-consumer-groups.sh --bootstrap-server kafka-cluster:9092 \
  --describe --group txn-processor-group

# MLFF 세션 상태 확인 (Redis CLI)
redis-cli --scan --pattern "mlff:session:*" | wc -l

# Outbox PENDING 적체 확인
psql -d bosdb -c "SELECT COUNT(*) FROM outbox_events WHERE status='PENDING'"

# 요금 캐시 적중률 확인 (Prometheus)
curl -s http://localhost:8080/actuator/metrics/cache.gets | jq '.measurements'
```

---

## 9. 참조 문서

| 문서 | 경로 | 참조 내용 |
|------|------|---------|
| 시스템 서비스 도메인 | `docs/02_system/02_service_domains.md` | txn-service 위치, 의존 서비스 목록 |
| 기술 스택 | `docs/02_system/03_tech_stack.md` | Java 21, Spring Boot 3.x, Redis 버전 |
| 외부 통합 | `docs/02_system/05_external_integration.md` | TnG API 연동 명세, Hyperledger Fabric 설정 |
| 데이터 모델 | `docs/03_data/02_data_model.md` | `txn_records` 테이블, `toll_fee_table` 구조, Outbox 스키마 |
| 데이터 아키텍처 | `docs/03_data/01_data_architecture.md` | Kafka 토픽 데이터 흐름, 5단계 집계 구조 |
| RBAC 설계 | `docs/03_data/03_rbac_design.md` | txn-service 권한, 감사 로그 접근 정책 |
| 보안 컴플라이언스 | `docs/03_data/05_security_compliance.md` | PDPA 번호판 처리 정책, Fabric 감사 요건 |
| 결제 아키텍처 | `docs/01_business/05_payment_architecture.md` | Channel A/B 비즈니스 규칙, 수수료 구조 |
| Phase 2 (통신) | `docs/06_phases/02_phase02_comm.md` | Kafka 토픽 명세, Consumer Group 설정 |
| Phase 4 (결제) | `docs/06_phases/04_phase04_payment.md` | `processed.txn.events` 소비, 정산 연계 |

---

*문서 버전: v1.0 | 생성일: 2026-04 | 담당: txn-lead*
*다음 업데이트: Phase 3 완료 후 실측 성능 데이터 및 TnG API 실환경 연동 결과 반영*
