# 기술 스택 상세
## 02_system/03_tech_stack.md
## v1.0 | 2026-04 | 참조: 01_system_overview.md, 04_dev/01_toolchain.md

---

> **Agent 사용 지침**
> DevOps Lead, Backend Lead Agent가 환경 구성 및 기술 선택 시 로드.
> 신규 라이브러리 도입 또는 버전 업그레이드 전 반드시 이 문서의 버전 호환성 매트릭스 확인.
> 기술 스택 변경은 CTO 승인 후 이 문서 업데이트 필수.

---

## 1. Executive Summary — 기술 스택 전체 표

Malaysia SLFF/MLFF Tolling BOS는 **10,000 TPS · 99.99% 가용성** 목표 달성을 위해 엔터프라이즈급 기술 스택을 채택한다. 아래 표는 카테고리별 핵심 기술 목록이다.

| 카테고리 | 기술 | 버전 | 역할 | 선택 이유 |
|---|---|---|---|---|
| **Frontend Web** | React | 18.x | Admin SPA | 생태계, RSC 지원 |
| **Frontend Web** | TypeScript | 5.x | 정적 타입 | 런타임 오류 사전 차단 |
| **Frontend Web** | Tailwind CSS | 3.x | UI 스타일링 | 유틸리티 기반 빠른 개발 |
| **Frontend Web** | Vite | 5.x | 빌드 도구 | HMR 속도, ESM 네이티브 |
| **Mobile** | React Native | 0.74+ | iOS/Android 앱 | 코드 공유, 빠른 출시 |
| **Mobile** | Expo | 51+ | RN 개발 플랫폼 | OTA 업데이트, EAS Build |
| **Backend Core** | Spring Boot | 3.x | BOS 마이크로서비스 | Java 생태계, 엔터프라이즈 검증 |
| **Backend Core** | Java | 21 LTS | JVM 런타임 | 가상 스레드, 장기 지원 |
| **Backend Core** | Resilience4j | 2.x | Circuit Breaker | 경량, Spring 통합 |
| **API 통신** | gRPC | 1.6x | RFID/ANPR 이벤트 수신 | 고성능 바이너리 프로토콜 |
| **API 통신** | REST/OpenAPI | 3.1 | 외부 연계 API | 표준, 가독성 |
| **메시지 브로커** | Apache Kafka | 3.7 | 이벤트 스트리밍 | 고처리량, 내구성 |
| **메시지 브로커** | AWS MSK | Managed | Kafka 관리형 | 운영 부담 절감 |
| **RDBMS** | PostgreSQL | 16 | 주요 데이터 저장 | RLS 멀티테넌시, JSONB |
| **캐시/세션** | Redis | 7.x | 캐시, 세션 관리 | 인메모리 고속 처리 |
| **데이터 레이크** | Delta Lake | 3.x | ACID 트랜잭션 레이크 | ACID, Time Travel |
| **분산 처리** | Apache Spark | 3.5 | 빅데이터 배치 처리 | 병렬 처리, ML 통합 |
| **워크플로** | Apache Airflow | 2.9 | DAG 스케줄링 | 가시성, Python DSL |
| **오브젝트 스토리지** | MinIO | RELEASE | S3 호환 스토리지 | 온프레미스 유연성 |
| **AI Text-to-SQL** | Claude Sonnet | 최신 | 업무 판단 AI | 정확도, 추론 품질 |
| **AI 커스터마이징** | Claude Haiku | 최신 | 경량 AI 작업 | 속도, 비용 효율 |
| **컨테이너** | AWS EKS | 1.30 | K8s 관리형 | 운영 효율, 오토스케일 |
| **컨테이너** | K8s HPA | 내장 | 수평 자동 스케일 | 트래픽 급증 대응 |
| **CDN/호스팅** | AWS CloudFront + S3 | — | 정적 자산 배포 | 글로벌 엣지, 저지연 |
| **보안 게이트** | AWS WAF | — | L7 방화벽 | OWASP 룰셋 |
| **보안 게이트** | AWS API Gateway | — | API 관리, 스로틀링 | 인증·속도 제한 |
| **인증** | JWT | — | Access/Refresh 토큰 | Stateless, 표준 |
| **권한** | Spring Security + RBAC | 6.x | 역할 기반 접근 | 세분화 제어 |
| **비밀 관리** | HashiCorp Vault | 1.17 | 시크릿 중앙 관리 | 동적 시크릿, 감사 |
| **감사 로그** | Hyperledger Fabric | 2.5 | 불변 감사 체인 | 변조 방지, 규제 대응 |
| **암호화** | AES-256 | — | 개인정보 암호화 | PDPA 준수 |
| **모니터링** | Prometheus | 2.x | 메트릭 수집 | 오픈소스 표준 |
| **모니터링** | Grafana | 11.x | 대시보드 시각화 | 풍부한 플러그인 |
| **분산 추적** | Jaeger | 1.x | 트레이싱 | 마이크로서비스 디버깅 |
| **로그 집계** | ELK Stack | 8.x | 로그 분석 | 검색, 알림 |
| **CI/CD** | GitHub Actions OIDC | — | 빌드·배포 자동화 | 비밀 없는 인증 |
| **인프라 코드** | Terraform | 1.8 | IaC | 선언적, 버전 관리 |
| **DNS/HA** | Route 53 Health Check | — | 헬스 기반 라우팅 | 자동 DR 전환 |
| **DB 고가용성** | RDS PostgreSQL Multi-AZ | 16 | DB HA | 자동 장애 조치 |

---

## 2. Frontend 스택 상세

### 2.1 BOS Admin Web (React 18)

```
기술: React 18 + TypeScript 5 + Tailwind CSS 3 + Vite 5
배포: AWS CloudFront + S3
타겟: 크롬 최신 2버전, Edge 최신 2버전 (IE 미지원)
지원 언어: 말레이어(BM) · 영어(EN) · 한국어(KO)
```

**핵심 의존성:**

| 패키지 | 버전 | 용도 |
|---|---|---|
| `react` | ^18.3 | UI 렌더링 |
| `react-dom` | ^18.3 | DOM 바인딩 |
| `typescript` | ^5.4 | 정적 타입 |
| `tailwindcss` | ^3.4 | 유틸리티 CSS |
| `vite` | ^5.2 | 빌드 도구 |
| `react-router-dom` | ^6.x | SPA 라우팅 |
| `@tanstack/react-query` | ^5.x | 서버 상태 관리 |
| `zustand` | ^4.x | 클라이언트 상태 |
| `react-i18next` | ^14.x | 다국어 지원 |
| `recharts` | ^2.x | KPI 차트 |
| `@radix-ui/react-*` | latest | 접근성 UI 컴포넌트 |
| `axios` | ^1.x | HTTP 클라이언트 |
| `zod` | ^3.x | 런타임 스키마 검증 |

**Vite 빌드 전략:**

```typescript
// vite.config.ts 핵심 설정
export default defineConfig({
  build: {
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          router: ['react-router-dom'],
          charts: ['recharts'],
        },
      },
    },
    chunkSizeWarningLimit: 500, // KB
  },
  server: {
    proxy: {
      '/api': 'http://localhost:8080',
    },
  },
});
```

**테스트 도구:**

| 도구 | 버전 | 용도 |
|---|---|---|
| Vitest | ^1.x | 단위 테스트 |
| @testing-library/react | ^14.x | 컴포넌트 테스트 |
| Playwright | ^1.x | E2E 테스트 |
| MSW (Mock Service Worker) | ^2.x | API 모킹 |

---

### 2.2 현장 Mobile App (React Native + Expo)

```
기술: React Native 0.74+ + Expo 51+ + TypeScript 5
플랫폼: iOS 15+, Android 12+ (API Level 31+)
배포: EAS Build + EAS Submit (App Store / Google Play)
업데이트: Expo OTA (Over-The-Air) — 긴급 패치 적용
```

**오프라인 우선 전략:**

```
온라인 모드: REST API 실시간 동기화
오프라인 모드:
  - MMKV (고속 로컬 스토리지) — 위반 이력 임시 저장
  - 네트워크 복구 시 자동 동기화 (큐 기반)
  - 장비 현황 캐시 최대 24시간 유지
```

**핵심 패키지:**

| 패키지 | 용도 |
|---|---|
| `expo-camera` | ANPR 이미지 촬영 |
| `expo-location` | GPS 위치 수집 |
| `react-native-mmkv` | 고속 오프라인 스토리지 |
| `@react-navigation/native` | 화면 네비게이션 |
| `react-native-reanimated` | 고성능 애니메이션 |
| `expo-notifications` | 푸시 알림 |

---

## 3. Backend 스택 상세

### 3.1 Spring Boot 3.x + Java 21

```
런타임: Java 21 LTS (OpenJDK / Amazon Corretto 21)
프레임워크: Spring Boot 3.3.x
빌드: Gradle 8.x (Kotlin DSL)
배포: Docker 컨테이너 → AWS EKS
```

**Java 21 가상 스레드 (Virtual Threads) 활용:**

```java
// Spring Boot 3.2+ — 가상 스레드 자동 활성화
// application.yml
spring:
  threads:
    virtual:
      enabled: true  # Tomcat 스레드 풀을 가상 스레드로 대체

// 효과: 블로킹 I/O 작업 시 OS 스레드 블로킹 없이
//       수십만 개 동시 연결 처리 가능 (10,000 TPS 지원 핵심)
```

**핵심 Spring 의존성:**

| 의존성 | 버전 | 역할 |
|---|---|---|
| `spring-boot-starter-web` | 3.3.x | REST API 서버 |
| `spring-boot-starter-data-jpa` | 3.3.x | JPA / Hibernate ORM |
| `spring-boot-starter-security` | 3.3.x | 인증/인가 |
| `spring-boot-starter-actuator` | 3.3.x | 헬스체크, 메트릭 |
| `spring-boot-starter-cache` | 3.3.x | 캐시 추상화 |
| `spring-kafka` | 3.x | Kafka 프로듀서/컨슈머 |
| `grpc-spring-boot-starter` | 3.x | gRPC 서버 |
| `resilience4j-spring-boot3` | 2.x | Circuit Breaker |
| `micrometer-registry-prometheus` | 1.13.x | Prometheus 메트릭 |
| `opentelemetry-spring-boot-starter` | 2.x | 분산 추적 |
| `postgresql` | 42.x | JDBC 드라이버 |
| `flyway-core` | 10.x | DB 마이그레이션 |
| `mapstruct` | 1.5.x | DTO 매핑 |

**마이크로서비스 구조:**

```
bos-services/
  ├── bos-toll-collection/      # 통행료 수납 (핵심)
  ├── bos-violation/            # 위반 처리
  ├── bos-payment/              # 결제 (Channel A/B)
  ├── bos-concession/           # 콘세셔네어 관리
  ├── bos-equipment/            # 차로 장비 모니터링
  ├── bos-reporting/            # 보고서 생성
  ├── bos-auth/                 # 인증/인가 서비스
  ├── bos-gateway/              # API Gateway (Spring Cloud Gateway)
  └── bos-event-receiver/       # gRPC RFID/ANPR 수신
```

**Resilience4j Circuit Breaker 설정:**

```yaml
# application.yml
resilience4j:
  circuitbreaker:
    instances:
      payment-service:
        slidingWindowSize: 10
        failureRateThreshold: 50      # 50% 실패 시 Open
        waitDurationInOpenState: 30s
        permittedNumberOfCallsInHalfOpenState: 3
  retry:
    instances:
      external-api:
        maxAttempts: 3
        waitDuration: 1s
        enableExponentialBackoff: true
  ratelimiter:
    instances:
      api-limiter:
        limitForPeriod: 1000
        limitRefreshPeriod: 1s
        timeoutDuration: 100ms
```

---

## 4. 데이터 스택 상세

### 4.1 PostgreSQL 16 (주요 RDBMS)

```
배포: AWS RDS PostgreSQL 16 Multi-AZ (Primary: ap-southeast-1)
스토리지: gp3 SSD, 자동 확장
멀티테넌시: Row Level Security (RLS) — 콘세셔네어 데이터 격리
백업: 자동 스냅샷 7일 보관 + Point-in-Time Recovery
```

**RLS 멀티테넌시 패턴:**

```sql
-- 테넌트 격리 RLS 정책
ALTER TABLE toll_transactions ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation ON toll_transactions
  USING (concessionaire_id = current_setting('app.current_tenant')::UUID);

-- 앱에서 세션 변수 설정
SET app.current_tenant = '콘세셔네어_UUID';
```

**핵심 PostgreSQL 16 기능 활용:**

| 기능 | 활용 목적 |
|---|---|
| JSONB | 동적 메타데이터, 설정 저장 |
| Partitioning (Range) | toll_transactions 월별 파티션 |
| pg_trgm | 차량번호 퍼지 검색 |
| LISTEN/NOTIFY | 실시간 이벤트 발행 |
| Logical Replication | Delta Lake 변경 데이터 캡처 (CDC) |
| Generated Columns | 집계 컬럼 자동 산출 |

---

### 4.2 Redis 7 (캐시 & 세션)

```
배포: AWS ElastiCache for Redis 7 (클러스터 모드)
노드 구성: Primary 1 + Replica 2 (ap-southeast-1 3 AZ)
최대 메모리 정책: allkeys-lru
```

**캐시 전략:**

| 캐시 키 패턴 | TTL | 캐시 대상 |
|---|---|---|
| `session:{userId}` | 15분 | JWT 세션 컨텍스트 |
| `tariff:{laneId}` | 30분 | 차로별 요금표 |
| `vehicle:{plate}` | 10분 | 차량 조회 결과 |
| `dashboard:{tenantId}` | 1분 | KPI 집계 데이터 |
| `rate_limit:{ip}` | 1초 | API Rate Limit 카운터 |
| `otp:{userId}` | 5분 | OTP 인증 코드 |

**Redis Pub/Sub — 실시간 이벤트:**

```
채널: toll.event.{laneId}  →  Admin Web WebSocket으로 브릿지
채널: violation.alert.{tenantId}  →  모바일 푸시 알림 트리거
```

---

### 4.3 Apache Kafka / AWS MSK (이벤트 스트리밍)

```
배포: AWS MSK (Managed Streaming for Apache Kafka) 3.7
브로커: 3 브로커 × 2 AZ (ap-southeast-1)
복제 팩터: 3 (RF=3)
보존 정책: 7일 (toll-events), 30일 (payment-events)
```

**토픽 설계:**

| 토픽 이름 | 파티션 수 | 용도 |
|---|---|---|
| `toll.rfid.events` | 24 | RFID 차량 감지 이벤트 |
| `toll.anpr.events` | 24 | ANPR 번호판 인식 이벤트 |
| `toll.transactions` | 12 | 완료된 통행 트랜잭션 |
| `payment.requests` | 12 | 결제 요청 이벤트 |
| `payment.results` | 12 | 결제 완료/실패 결과 |
| `violation.created` | 6 | 신규 위반 생성 |
| `audit.trail` | 6 | 감사 로그 (Hyperledger 연계) |
| `notification.push` | 6 | 모바일 푸시 발송 요청 |

**처리량 설계:**

```
피크 처리량 목표:
  RFID 이벤트:    5,000 events/sec (전체 차로 합산)
  ANPR 이벤트:    3,000 events/sec
  결제 트랜잭션:   2,000 TPS
  합계:           10,000 TPS (목표치)

Consumer Group 구성:
  toll-processor-cg   → bos-toll-collection 서비스
  payment-cg          → bos-payment 서비스
  audit-cg            → Hyperledger Fabric 브릿지
```

---

### 4.4 Delta Lake + Apache Spark (빅데이터 플랫폼)

**Delta Lake 3.x:**

```
ACID 트랜잭션: 동시 읽기/쓰기 충돌 없음
Time Travel: 최대 30일 이력 조회
Schema Enforcement: 스키마 드리프트 자동 차단
Z-Ordering: plate_number, transaction_date 기준 클러스터링
```

**데이터 레이크 레이어 구조:**

```
MinIO (S3 호환) 버킷 구조:
  bos-datalake/
    ├── bronze/          # 원시 데이터 (Kafka → Delta)
    │   ├── toll_events/
    │   └── payment_events/
    ├── silver/          # 정제 데이터 (중복 제거, 검증)
    │   ├── transactions/
    │   └── violations/
    └── gold/            # 집계 데이터 (보고서용)
        ├── daily_summary/
        ├── monthly_revenue/
        └── concession_kpi/
```

**Apache Spark 3.5 배치 잡:**

| 잡 이름 | 실행 주기 | 처리 내용 |
|---|---|---|
| `bronze-ingestion` | 5분 | Kafka → Delta Bronze |
| `silver-transform` | 15분 | 중복 제거, 데이터 정제 |
| `daily-aggregation` | 매일 02:00 | 일일 집계 → Gold |
| `monthly-revenue` | 매월 1일 00:00 | 월별 수익 정산 집계 |
| `violation-reconcile` | 매일 03:00 | 위반 미수금 대사 |

**Apache Airflow 2.9 DAG 관리:**

```python
# 예시 DAG 구조 (pseudo)
with DAG('daily_bos_pipeline', schedule='0 2 * * *') as dag:
    bronze = SparkSubmitOperator(task_id='bronze_ingestion', ...)
    silver = SparkSubmitOperator(task_id='silver_transform', ...)
    gold   = SparkSubmitOperator(task_id='daily_aggregation', ...)
    report = PythonOperator(task_id='generate_reports', ...)

    bronze >> silver >> gold >> report
```

---

## 5. AI/ML 스택

### 5.1 Claude API 활용 전략

```
제공사: Anthropic Claude API
통합 방식: AWS Bedrock (프로덕션) 또는 Direct API (개발)
지역: us-east-1 (Bedrock Claude 지원 리전)
```

**모델 선택 전략:**

| 사용 사례 | 모델 | 이유 |
|---|---|---|
| Text-to-SQL 쿼리 생성 | Claude Sonnet | 복잡한 SQL 추론, 높은 정확도 |
| 업무 판단 AI (이상 감지, 보고서 초안) | Claude Sonnet | 깊은 맥락 이해 |
| 스마트 커스터마이징 (설정 추천, 간단 분류) | Claude Haiku | 빠른 응답, 비용 효율 |
| 아키텍처 결정, 복잡한 분석 | Claude Opus | 최대 추론 품질 |

**Text-to-SQL 시스템 설계:**

```
흐름:
  1. 사용자 자연어 입력 (BM/EN/KO)
  2. Claude Sonnet → SQL 생성 (스키마 컨텍스트 주입)
  3. SQL 안전성 검증 (읽기 전용 허용, DDL/DML 차단)
  4. PostgreSQL 실행 → 결과 반환
  5. Claude Sonnet → 결과 자연어 요약

보안:
  - 허용 쿼리: SELECT만 허용
  - 차단 패턴: DROP, DELETE, UPDATE, INSERT
  - 테넌트 격리: RLS 자동 적용 (SET app.current_tenant)
  - 최대 실행 시간: 30초 (타임아웃)
```

**Fallback 전략:**

```
Primary:   Claude Sonnet (Bedrock)
Fallback1: Claude Haiku (Bedrock) — 응답 지연 > 5초 시
Fallback2: 미리 정의된 쿼리 템플릿 (AI 불가 시)
Circuit Breaker: 3회 연속 실패 → 템플릿 모드 전환, 알림 발송
```

---

## 6. 인프라 & DevOps

### 6.1 AWS 서비스 구성

**리전 구성:**

| 역할 | 리전 | 코드 |
|---|---|---|
| Primary (주 운영) | 싱가포르 | ap-southeast-1 |
| DR (재해복구) | 자카르타 | ap-southeast-3 |

**핵심 AWS 서비스:**

| 서비스 | 용도 | 구성 |
|---|---|---|
| EKS 1.30 | 컨테이너 오케스트레이션 | 워커 노드 c6i.2xlarge × 최소 6개 |
| RDS PostgreSQL 16 Multi-AZ | 주 데이터베이스 | db.r6g.2xlarge, 스토리지 자동 확장 |
| ElastiCache Redis 7 | 캐시, 세션 | cache.r7g.large × 3 노드 |
| MSK 3.7 | Kafka 관리형 | kafka.m5.large × 3 브로커 |
| CloudFront + S3 | 정적 자산 CDN | 글로벌 엣지 배포 |
| API Gateway | REST API 관리 | 스로틀링, WAF 연동 |
| WAF | L7 웹 방화벽 | OWASP 관리형 룰셋 |
| Route 53 | DNS, 헬스 라우팅 | 30초 헬스체크, 자동 DR 전환 |
| ACM | SSL/TLS 인증서 | 와일드카드 인증서 자동 갱신 |
| ECR | 컨테이너 레지스트리 | 이미지 스캔 활성화 |
| Secrets Manager | 비밀값 관리 | Vault 연동 |
| CloudWatch | AWS 메트릭, 로그 | MSK, RDS, EKS 메트릭 |

---

### 6.2 Kubernetes (EKS) 구성

**네임스페이스 구조:**

```
네임스페이스:
  production/
    bos-core/       # 핵심 BOS 서비스
    bos-data/       # 데이터 처리 서비스
    bos-ai/         # AI 서비스
    bos-monitoring/ # Prometheus, Grafana, Jaeger
  staging/
    [동일 구조]
  development/
    [동일 구조]
```

**HPA (Horizontal Pod Autoscaler) 설정:**

```yaml
# bos-toll-collection HPA 예시
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: bos-toll-collection-hpa
spec:
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
    - type: External
      external:
        metric:
          name: kafka_consumer_lag
        target:
          type: AverageValue
          averageValue: "1000"
```

**리소스 프로파일 (서비스별 기본값):**

| 서비스 | CPU Request | CPU Limit | Memory Request | Memory Limit | Min Pods |
|---|---|---|---|---|---|
| bos-toll-collection | 500m | 2000m | 512Mi | 2Gi | 3 |
| bos-payment | 500m | 2000m | 512Mi | 2Gi | 3 |
| bos-gateway | 250m | 1000m | 256Mi | 1Gi | 2 |
| bos-event-receiver | 1000m | 4000m | 1Gi | 4Gi | 3 |
| bos-reporting | 250m | 1000m | 512Mi | 2Gi | 2 |

---

### 6.3 CI/CD 파이프라인 (GitHub Actions OIDC)

```
트리거:
  push to main     → 스테이징 배포
  release tag      → 프로덕션 배포 (수동 승인 필요)
  pull_request     → 빌드 + 테스트 + 보안 스캔

OIDC 인증:
  GitHub Actions → AWS OIDC → IAM Role (비밀 없는 인증)
  ECR push, EKS deploy 권한만 부여 (최소 권한 원칙)
```

**파이프라인 단계:**

```
Stage 1 — Build & Test (병렬)
  ├── Backend: ./gradlew build test
  ├── Frontend: npm run build && vitest
  └── Mobile: expo export

Stage 2 — Security Scan (병렬)
  ├── SAST: Semgrep (코드 취약점)
  ├── SCA: Trivy (의존성 CVE)
  └── Container: Trivy image scan

Stage 3 — Docker Build & Push
  └── ECR: {service}:{git-sha} 태그

Stage 4 — Deploy to Staging
  └── helm upgrade --install (EKS staging)

Stage 5 — Integration Tests
  └── Playwright E2E (스테이징 환경)

Stage 6 — Deploy to Production (수동 승인)
  └── helm upgrade --install (EKS production)
      → Blue/Green 배포 전략
      → 롤백: helm rollback (자동, 헬스체크 실패 시)
```

---

## 7. 보안 도구

### 7.1 AWS WAF + API Gateway

```
AWS WAF 룰셋:
  ├── AWS 관리형: AWSManagedRulesCommonRuleSet (OWASP Top 10)
  ├── AWS 관리형: AWSManagedRulesSQLiRuleSet (SQL Injection)
  ├── AWS 관리형: AWSManagedRulesKnownBadInputsRuleSet
  └── 커스텀: 말레이시아 IP 화이트리스트 (정부 연계 API)

API Gateway 설정:
  - 기본 스로틀: 1,000 req/sec per API key
  - 버스트 한도: 2,000 req
  - 사용 계획: 파트너사별 별도 할당량
```

**JWT 토큰 전략:**

```
Access Token:
  유효 기간: 15분
  알고리즘: RS256 (비대칭 키)
  클레임: sub, tenant_id, roles[], permissions[]

Refresh Token:
  유효 기간: 7일
  저장소: Redis (세션 무효화 즉시 가능)
  회전 정책: 사용 시마다 새 Refresh Token 발급

비상 시나리오:
  - 대량 강제 로그아웃: Redis 키 패턴 삭제
  - 특정 사용자 차단: JWT 블랙리스트 (Redis SET)
```

---

### 7.2 HashiCorp Vault (비밀 관리)

```
배포: Vault 1.17 — AWS EKS 내 Vault Agent Injector
백엔드: AWS KMS (Auto Unseal)
인증: Kubernetes ServiceAccount 연동

동적 시크릿 (Dynamic Secrets):
  - PostgreSQL: 90초 TTL 자격증명 자동 생성
  - AWS IAM: 단기 자격증명 (15분 TTL)

정적 시크릿 저장:
  - 외부 API 키 (JPJ, TnG, FPX)
  - Claude API 키
  - JWT 서명 키 (RSA PEM)
```

**Vault 경로 구조:**

```
secret/
  bos/
    production/
      database/          # DB 자격증명
      external-api/      # 외부 연계 API 키
      jwt/               # JWT 서명 키
      claude-api/        # Anthropic API 키
    staging/
      [동일 구조]
```

---

### 7.3 Hyperledger Fabric (감사 로그 블록체인)

```
버전: Hyperledger Fabric 2.5 LTS
목적: 거래 감사 로그 불변성 보장 (PDPA/규제 요건)
노드 구성: Orderer 3개 + Peer 2개 (JVC + 규제기관)
채널: bos-audit-channel (허가형 블록체인)

로깅 대상:
  - 통행 트랜잭션 (금액 변경 이력)
  - 결제 처리 결과
  - 위반 처리 상태 변경
  - 사용자 권한 변경 (RBAC 수정)
  - 요금표 변경 이력
```

**감사 로그 브릿지 흐름:**

```
BOS 서비스 → Kafka(audit.trail) → Audit Bridge Service → Hyperledger Fabric
                                                          ↓
                                                  감사 보고서 API
                                                  (조회 전용, 변경 불가)
```

---

### 7.4 AES-256 개인정보 암호화

```
적용 대상 (PDPA 준수):
  - 차량 소유자 이름, IC 번호
  - 연락처 (전화번호, 이메일)
  - 결제 카드 정보 (마스킹 + 암호화)
  - ANPR 캡처 이미지 (저장 시 암호화)

구현 방식:
  - 컬럼 레벨 암호화: PostgreSQL pgcrypto 확장
  - 애플리케이션 레벨: Java AES-256-GCM (인증된 암호화)
  - 키 관리: HashiCorp Vault (키 자동 순환 90일)
```

---

## 8. 모니터링 & 관찰가능성

### 8.1 Prometheus + Grafana (메트릭)

```
Prometheus 수집 주기: 15초
보존 기간: 15일 (단기), 1년 (장기 — Thanos/S3)
알림 채널: PagerDuty (Critical), Slack (Warning)
```

**핵심 SLI/SLO 메트릭:**

| 메트릭 | SLO 목표 | 알림 임계값 |
|---|---|---|
| API 응답 P99 지연 | < 500ms | > 800ms |
| 가용성 (Uptime) | 99.99% | < 99.95% (30일) |
| Kafka Consumer Lag | < 1,000 | > 5,000 |
| 결제 성공률 | > 99.5% | < 99% |
| DB 연결 풀 사용률 | < 80% | > 90% |
| 포드 재시작 | 0/시간 | > 3/시간 |

**Grafana 대시보드 구성:**

```
대시보드:
  ├── 01_BOS_Overview          # 전체 KPI 요약
  ├── 02_Transaction_Flow      # 통행 흐름 실시간
  ├── 03_Payment_Status        # 결제 채널 상태
  ├── 04_Kafka_Streams         # Kafka 처리량/레그
  ├── 05_DB_Performance        # PostgreSQL 성능
  ├── 06_K8s_Cluster           # EKS 리소스 현황
  ├── 07_Security_Events       # WAF/보안 이벤트
  └── 08_AI_API_Usage          # Claude API 사용량/비용
```

---

### 8.2 Jaeger (분산 추적)

```
배포: Jaeger All-in-One → EKS (프로덕션: Jaeger Operator)
샘플링 전략:
  - 기본: 1% (고처리량 환경)
  - 오류 발생 시: 100% (강제 샘플링)
  - 느린 요청 (> 1초): 100% (강제 샘플링)
백엔드 스토리지: Elasticsearch 8.x
보존 기간: 7일
```

**추적 전파:**

```
표준: W3C Trace Context (traceparent 헤더)
전파 경로:
  React Web → Spring Boot (HTTP) → Kafka → Consumer → PostgreSQL
                                  → gRPC → RFID/ANPR 수신
```

---

### 8.3 ELK Stack (로그 집계)

```
Elasticsearch: 8.x (AWS OpenSearch 관리형 대안 가능)
Logstash: 8.x (로그 파이프라인)
Kibana: 8.x (로그 검색/시각화)
Filebeat: EKS DaemonSet으로 배포
```

**로그 파이프라인:**

```
애플리케이션 로그 (JSON 구조화)
  → Filebeat (EKS DaemonSet)
  → Logstash (필터링, 마스킹)
  → Elasticsearch (인덱스: bos-logs-YYYY.MM.DD)
  → Kibana (검색, 알림)

민감정보 마스킹 (Logstash):
  - 카드 번호: **** **** **** XXXX
  - IC 번호: ****-**-XXXX
  - 전화번호: +60-**-***XXXX
```

---

## 9. 버전 호환성 매트릭스

> **중요:** 아래 버전 조합은 통합 테스트 완료 기준이다. 버전 변경 전 반드시 전체 매트릭스 검토 필요.

### 9.1 Backend 호환성

| 컴포넌트 | 확정 버전 | 최소 버전 | 최대 테스트 버전 | 비고 |
|---|---|---|---|---|
| Java | 21 LTS | 21 | 21 | 가상 스레드 필수 |
| Spring Boot | 3.3.x | 3.2 | 3.3 | Java 21 지원 확인 |
| Spring Security | 6.3.x | 6.2 | 6.3 | Spring Boot 연동 |
| Hibernate | 6.5.x | 6.4 | 6.5 | Spring Data JPA 포함 |
| Kafka Client | 3.7.x | 3.5 | 3.7 | MSK 3.7 호환 |
| gRPC | 1.64.x | 1.60 | 1.64 | Protobuf 3 |
| Resilience4j | 2.2.x | 2.1 | 2.2 | Spring Boot 3 전용 |
| Flyway | 10.x | 10.0 | 10.x | PostgreSQL 16 지원 |

### 9.2 Frontend 호환성

| 컴포넌트 | 확정 버전 | Node.js 최소 | 비고 |
|---|---|---|---|
| React | 18.3 | 18.0 LTS | React 19 미지원 (미검증) |
| TypeScript | 5.4 | — | strict 모드 필수 |
| Vite | 5.2 | 18.0 LTS | — |
| React Native | 0.74 | 18.0 LTS | New Architecture 활성화 |
| Expo | 51 | 18.0 LTS | EAS CLI 10+ |

### 9.3 데이터 플랫폼 호환성

| 컴포넌트 | 확정 버전 | Python 버전 | 비고 |
|---|---|---|---|
| PostgreSQL | 16 | — | RLS, pg_trgm 확장 |
| Redis | 7.2 | — | 클러스터 모드 |
| Delta Lake | 3.1 | 3.10+ | Spark 3.5 필수 |
| Apache Spark | 3.5 | 3.10+ | Java 17+ (21 호환) |
| Apache Airflow | 2.9 | 3.10+ | Celery Executor |
| MinIO | RELEASE.2024 | — | S3 API v4 |

### 9.4 인프라 호환성

| 컴포넌트 | 확정 버전 | 비고 |
|---|---|---|
| EKS | 1.30 | 2025년 10월 EOL — 1.31 업그레이드 계획 |
| Terraform | 1.8 | AWS Provider 5.x |
| Helm | 3.15 | — |
| Docker | 26.x | — |
| Vault | 1.17 | AWS KMS Auto Unseal |
| Hyperledger Fabric | 2.5 LTS | 2027년까지 지원 |

---

## 10. 참조 문서

| 문서 | 경로 | 관련 내용 |
|---|---|---|
| 시스템 아키텍처 개요 | `docs/02_system/01_system_overview.md` | 3-Layer 구조, 전체 설계 원칙 |
| 개발 환경 툴체인 | `docs/04_dev/01_toolchain.md` | 로컬 개발 환경 설정, IDE 플러그인 |
| 데이터 아키텍처 | `docs/03_data/01_data_architecture.md` | ERD, 데이터 흐름 |
| RBAC 설계 | `docs/03_data/03_rbac_design.md` | 30개 역할, 권한 매트릭스 |
| 보안 & 컴플라이언스 | `docs/03_data/05_security_compliance.md` | PDPA, ANPR 정책, 보안 인증 |
| 프로젝트 헌장 | `docs/01_business/01_project_charter.md` | 사업 목적, JVC 구조 |
| 결제 아키텍처 | `docs/01_business/05_payment_architecture.md` | Channel A/B 결제 흐름 |

---

> **문서 변경 이력**
>
> | 버전 | 날짜 | 변경 내용 | 작성자 |
> |---|---|---|---|
> | v1.0 | 2026-04 | 초안 작성 — 전체 기술 스택 정의 | DevOps Lead |
