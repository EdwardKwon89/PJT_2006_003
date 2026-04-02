# Phase 7: 모니터링 & 장애 대응
## 06_phases/07_phase07_monitoring.md
## v1.0 | 2026-04 | 참조: 02_system/03_tech_stack.md, 07_skills/ai-fault-detection/SKILL.md

---

> **Agent 사용 지침**
> `devops-lead`, CTO Agent가 모니터링 & 장애 대응 구현 시 반드시 로드.
> 본 문서는 Phase 7 실행의 유일한 정식 기준 문서이며, 모든 모니터링 임계값·대응 절차·온콜 정책의 구현 기준으로 사용된다.
> 임계값 변경 및 온콜 정책 수정은 반드시 CTO 검토 후 머지한다.

---

## 1. Phase 개요

### 1.1 목적 및 범위

Phase 7은 Malaysia SLFF/MLFF Tolling BOS의 **가시성(Observability) & 장애 대응 체계**를 구축하는 단계다. Prometheus + Grafana 기반 실시간 메트릭 수집, Loki 로그 집계, AI 기반 이상 탐지 (Claude + 통계 모델), PagerDuty 온콜 연동, 장애 대응 런북(Runbook) 자동화를 완성한다.

**핵심 목표:**
- 전 서비스 메트릭 수집 및 대시보드 구성 (SLO 기반)
- AI 기반 이상 탐지 및 자동 복구 3단계 구현
- 온콜 알림 체계 구축 (PagerDuty + Slack + SMS)
- 장애 대응 런북 자동화 (Incident Response Runbook)
- 포스트모템 자동 리포트 생성

### 1.2 Phase 연계

| 구분 | 내용 |
|------|------|
| **선행 Phase** | Phase 1 — 인프라 (Kubernetes 클러스터 완료 필수) / Phase 2~6 — 모든 마이크로서비스 배포 완료 |
| **병행 Phase** | Phase 7은 독립적이므로 Phase 8과 병행 가능 |
| **예상 기간** | **2주** (Sprint 16~17) |

### 1.3 Observability 스택 구성

```
┌──────────────────────────────────────────────────────┐
│               Observability Stack                     │
├──────────────────────────────────────────────────────┤
│                                                      │
│  [Metrics]        [Logs]          [Traces]           │
│  Prometheus       Loki            Jaeger            │
│  + Node Exporter  + Promtail      + OpenTelemetry   │
│       │               │                │            │
│       └───────────────┴────────────────┘            │
│                       │                             │
│                   Grafana (통합 대시보드)            │
│                       │                             │
│          ┌────────────┴────────────┐                │
│          │                        │                 │
│    [AI 이상 탐지]         [AlertManager]            │
│    Claude Sonnet           ↓                        │
│    + 통계 모델        PagerDuty + Slack + SMS        │
│                                                     │
└──────────────────────────────────────────────────────┘
```

---

## 2. 담당 Agent 및 역할

### 2.1 Phase 7 참여 Agent

| Agent | 역할 | 주요 책임 |
|-------|------|---------|
| `devops-lead` | 기술 리드 | 모니터링 인프라 설계, Prometheus 구성, 온콜 정책 |
| `devops-dev` | 개발 담당 | Grafana 대시보드 구성, Loki 로그 파이프라인, Runbook |
| `CTO` | 검토 & 승인 | SLO 목표값 승인, 임계값 최종 확정, 온콜 정책 승인 |
| `AI Lead` | AI 이상 탐지 | Claude 기반 이상 탐지 로직, 자동 복구 시나리오 |

---

## 3. SLO (Service Level Objective) 정의

### 3.1 핵심 SLO 목표값

| 서비스 | 가용성 SLO | 지연 SLO (P99) | 에러율 SLO |
|-------|-----------|--------------|----------|
| `txn-service` (트랜잭션) | 99.95% | < 200ms | < 0.1% |
| `payment-service` (결제) | 99.99% | < 500ms | < 0.01% |
| `billing-service` (정산) | 99.9% | < 1,000ms | < 0.5% |
| `account-service` (계정) | 99.9% | < 300ms | < 0.1% |
| `violation-service` (위반) | 99.5% | < 2,000ms | < 1.0% |
| API Gateway | 99.95% | < 100ms | < 0.05% |

### 3.2 SLO 계산 기준

```
가용성 = (총 요청 - 에러 요청) / 총 요청 × 100

에러 기준: HTTP 5xx 응답 (4xx는 클라이언트 에러, SLO 제외)

Error Budget = (1 - SLO) × 기간
  예) 99.95% SLO 기준 30일 Error Budget
    = 0.05% × 30일 × 24시간 × 60분
    = 21.6분/월
```

---

## 4. 주요 태스크 체크리스트

### 4.1 Prometheus 메트릭 수집

- [ ] 각 마이크로서비스에 Prometheus 클라이언트 라이브러리 적용
  - Java 서비스: `micrometer-registry-prometheus`
  - Node.js 서비스: `prom-client`
  - 공통 메트릭: `http_requests_total`, `http_request_duration_seconds`, `jvm_memory_*`
- [ ] 비즈니스 전용 커스텀 메트릭 정의
  ```promql
  # 트랜잭션 처리율
  bos_txn_processed_total{service="txn-service", channel="A|B"}
  # 결제 실패율
  bos_payment_failures_total{reason="gateway_error|timeout|rejected"}
  # JPJ 차단 API 성공/실패
  bos_jpj_block_requests_total{result="success|failure"}
  # 일별 집계 배치 처리 시간
  bos_daily_aggregation_duration_seconds
  ```
- [ ] Prometheus Operator 설치 및 `ServiceMonitor` 구성 (Kubernetes)
- [ ] AlertManager 규칙 파일 작성 (`alerts/rules/*.yaml`)

### 4.2 Grafana 대시보드 구성

- [ ] **대시보드 1: BOS Overview (경영진용)**
  - 전체 가용성 SLO, 에러율, P99 지연, 시스템 상태 신호등
  - 실시간 트랜잭션 처리량 (TPS)
  - 일별 수납 집계 현황
- [ ] **대시보드 2: 서비스별 상세 (기술팀용)**
  - `txn-service`, `payment-service`, `billing-service` 각 상세 메트릭
  - Kafka Consumer Lag, Airflow DAG 실행 현황
  - PostgreSQL 연결 수, 쿼리 P99
- [ ] **대시보드 3: 인프라 현황 (DevOps용)**
  - Kubernetes Pod 상태, Node CPU/Memory
  - Redis, PostgreSQL, Kafka 클러스터 상태
  - 네트워크 I/O, 디스크 사용량

### 4.3 AI 기반 이상 탐지

- [ ] 이상 탐지 모델 구현 (`AnomalyDetectionService`)
  - **통계 기반**: 롤링 평균 ± 3σ 이탈 탐지 (단기 이상)
  - **AI 기반**: Claude Sonnet API 호출 (복잡한 다변수 이상 판단)
    - 입력: 최근 15분 메트릭 시계열 데이터
    - 출력: 이상 여부, 원인 추정, 권장 조치
- [ ] 자동 복구 3단계 정의
  ```
  1단계: 자동 재시작 (Pod Restart)
     - 조건: 단일 Pod 에러율 > 10% (5분 지속)
     - 실행: kubectl rollout restart deployment/{service}

  2단계: 트래픽 전환 (Circuit Breaker Open)
     - 조건: 서비스 전체 에러율 > 20% (3분 지속)
     - 실행: Istio VirtualService 트래픽 우회

  3단계: 인간 개입 요청
     - 조건: 2단계 후에도 회복 안 됨 (5분 경과)
     - 실행: PagerDuty P1 알림 + Slack @channel
  ```
- [ ] 이상 탐지 감사 로그 (`anomaly_detection_log` 테이블)

### 4.4 온콜 알림 체계 (PagerDuty)

- [ ] PagerDuty 서비스 및 에스컬레이션 정책 설정
  - P1 (Critical): 즉시 → 5분 미응답 시 매니저 → 15분 미응답 시 CTO
  - P2 (High): 15분 내 → 30분 미응답 시 시니어 엔지니어
  - P3 (Medium): 4시간 내 업무 시간 대응
- [ ] AlertManager → PagerDuty 연동 설정
- [ ] 온콜 스케줄 관리 (주간 로테이션, 주말 대기)
- [ ] Slack Integration (#bos-alerts 채널)

### 4.5 장애 대응 런북 (Runbook) 자동화

- [ ] 런북 문서 작성 (주요 장애 시나리오 10개)
  - `RB-01`: txn-service Pod OOM Killed
  - `RB-02`: Kafka Consumer Lag > 10,000
  - `RB-03`: PostgreSQL 연결 풀 고갈
  - `RB-04`: JPJ API 응답 없음 (Timeout)
  - `RB-05`: TnG 배치 정산 실패
  - `RB-06`: 결제 게이트웨이 오류율 급증
  - `RB-07`: Redis 메모리 95% 초과
  - `RB-08`: Kubernetes Node NotReady
  - `RB-09`: Airflow DAG 연속 3회 실패
  - `RB-10`: 인증 서비스 (Keycloak) 다운
- [ ] 런북 자동 실행 Bot 구현 (Slack Bot)
  - Slack 명령어: `/runbook RB-01`
  - 해당 런북 단계별 안내 + 자동 실행 가능 단계 실행

### 4.6 포스트모템 자동 리포트

- [ ] 장애 종료 후 자동 포스트모템 초안 생성 (Claude API)
  - 입력: 장애 타임라인 (AlertManager 이벤트), 관련 메트릭, 런북 실행 로그
  - 출력: 원인 분석, 영향 범위, 재발 방지 대책 초안
- [ ] 포스트모템 템플릿
  ```markdown
  # 포스트모템: {서비스} {날짜}
  ## 영향 범위
  ## 타임라인
  ## 원인 분석 (Root Cause)
  ## 재발 방지 대책
  ## 액션 아이템
  ```

---

## 5. 완료 기준 체크리스트

| 영역 | 기준 항목 | 검증 방법 |
|------|---------|---------|
| 메트릭 수집 | 모든 서비스 Prometheus 메트릭 노출 | Prometheus 타겟 상태 확인 |
| 대시보드 | 3종 Grafana 대시보드 정상 동작 | 실제 트래픽 기준 데이터 표시 확인 |
| AI 이상 탐지 | 주입 이상 데이터 10분 내 탐지 | 테스트 이상 데이터 주입 시뮬레이션 |
| 자동 복구 | 1단계 자동 재시작 동작 확인 | Pod Kill 후 자동 복구 확인 |
| PagerDuty | Critical 알림 5분 내 수신 | 테스트 알림 발송 |
| 런북 | 10개 런북 문서 완성 및 Bot 연동 | Slack 명령어 실행 테스트 |

---

## 6. 참조 문서

| 문서 | 경로 |
|------|------|
| 기술 스택 | [`02_system/03_tech_stack.md`](../02_system/03_tech_stack.md) |
| 인프라 Phase 1 | [`06_phases/01_phase01_infra.md`](./01_phase01_infra.md) |
| AI 기능 설계 | [`02_system/04_ai_features.md`](../02_system/04_ai_features.md) |
| GSD 워크플로우 | [`04_dev/05_gsd_workflow.md`](../04_dev/05_gsd_workflow.md) |

---

*Malaysia SLFF/MLFF Tolling BOS — Phase 7 모니터링 & 장애 대응 v1.0*
*생성일: 2026-04 | 담당: devops-lead, devops-dev, CTO, AI Lead*
