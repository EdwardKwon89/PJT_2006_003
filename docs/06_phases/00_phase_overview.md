# 전체 Phase 개요

## 06_phases/00_phase_overview.md

## v1.0 | 2026-04 | 참조: 04_dev/05_gsd_workflow.md, .planning/ROADMAP.md

---

> **Agent 사용 지침**
> PM Agent가 Phase 진행 현황 파악 또는 신규 Phase 계획 수립 시 로드.
> 각 Phase의 선행·후행 의존성을 반드시 확인 후 실행.
> 신규 Phase 추가 시 이 문서의 의존성 다이어그램과 타임라인을 먼저 갱신할 것.

---

## 1. Executive Summary — 전체 12개 Phase 개요

Malaysia SLFF/MLFF Tolling BOS는 **12개 Phase**로 나뉘어 순차·병렬 실행된다. 각 Phase는 독립적인 산출물과 완료 기준을 보유하며, G-HARD 게이트 통과 조건을 갖춘다.

| # | Phase명 | 기간 (주) | 예상 시작 | Lead Agent | 핵심 산출물 | 의존 Phase |
| - | ------- | --------- | --------- | ---------- | ----------- | ---------- |
| **0** | 공통 인프라 구축 | 3 | 2026-04-22 | devops-lead | EKS·RDS·Kafka·Vault 배포 | — (독립) |
| **1** | 통신 레이어 구축 | 3 | 2026-05-13 | backend-lead | gRPC/REST Gateway, MSK 토픽 | Phase 0 |
| **2** | 트랜잭션 엔진 | 4 | 2026-06-03 | transaction-lead | SLFF/MLFF 세션 처리, 정산 엔진 | Phase 1 |
| **3** | 계정 관리 | 3 | 2026-07-01 | account-lead | 사용자·차량 등록, Tag 관리, KYC | Phase 2 |
| **4** | 빌링 & 정산 | 4 | 2026-07-22 | billing-lead | Channel A/B 정산, 수수료 계산 | Phase 2, 3 |
| **5** | 위반 & 집행 | 3 | 2026-08-19 | violation-lead | 위반 감지, ANPR 연동, 법적 처리 | Phase 2, 3 |
| **6** | 장비 모니터링 | 3 | 2026-09-09 | equipment-lead | 차선 장비 헬스, OTA 업데이트 | Phase 0, 2 |
| **7** | 빅데이터·분석 | 4 | 2026-09-30 | bigdata-lead | Delta Lake, Spark ETL, BI 대시보드 | Phase 2, 4 |
| **8** | AI 고급 기능 | 4 | 2026-10-28 | ai-lead | Text-to-SQL, 이상 감지, 예측 분석 | Phase 7 |
| **9** | 웹·모바일 앱 | 4 | 2026-10-28 | frontend-lead | BOS Admin, Operator App, 고객 앱 | Phase 3, 4, 5 |
| **10** | 외부 API·MCP | 3 | 2026-11-25 | integration-lead | JPJ·TnG·FPX 연동, MCP 게이트웨이 | Phase 2, 4 |
| **11** | 운영 이관 | 3 | 2026-12-16 | devops-lead + pm | DR 구성, SLA 검증, 운영 인수 | Phase 0~10 |

**총 기간:** 약 9개월 (2026-04-22 ~ 2027-01-14 예상)
**총 예산:** Agent 호출 약 1,800~2,400회 (USD 720~1,200)

---

## 2. Phase 의존성 다이어그램

```
Phase 0: 공통 인프라 구축
├── EKS, RDS, Kafka, Redis, Vault, Prometheus
└─┬─────────────────────────────────────────────────────────┐
  ▼                                                         ▼
Phase 1: 통신 레이어                             Phase 6: 장비 모니터링
├── gRPC Gateway                                ├── RFID/ANPR 수신
├── REST API Gateway                            └── (→ Phase 2와 병렬 가능)
└─┬──────────────────────────────────────────────────┐
  ▼                                                  ▼
Phase 2: 트랜잭션 엔진                      Phase 5: 위반 집행 (Phase 2 완료 후)
├── SLFF 세션 매칭                          ├── 위반 감지 룰
├── MLFF 다구간 처리                        └── ANPR 법적 처리
└─┬────────────────┬──────────────────────┐
  ▼                ▼                      ▼
Phase 3          Phase 4: 빌링 & 정산   Phase 10: 외부 API·MCP
계정 관리         ├── Channel A/B 정산    ├── JPJ/TnG/FPX 연동
├── KYC 처리      └── 수수료 엔진         └── MCP 게이트웨이
└──┬──────────────────┘
   ▼
Phase 7: 빅데이터·분석
├── Delta Lake ETL
├── Spark Batch
└─┬──────────────
  ▼
Phase 8: AI 고급 기능    Phase 9: 웹·모바일 앱
├── Text-to-SQL          ├── BOS Admin (React)
├── 이상 감지            ├── Operator Mobile
└── 예측 분석            └── 고객 앱
              └─────────────────────────────┐
                                            ▼
                               Phase 11: 운영 이관
                               ├── DR 검증 & SLA
                               └── 운영팀 인수인계
```

**병렬 실행 가능 구간:**
- Phase 1 ↔ Phase 6 (Phase 0 완료 후 동시 시작)
- Phase 3 ↔ Phase 4 ↔ Phase 5 (Phase 2 완료 후 동시 시작)
- Phase 8 ↔ Phase 9 (Phase 7 + Phase 4 완료 후 동시 시작)

---

## 3. 각 Phase 한 줄 요약 + 핵심 완료 기준

### Phase 0: 공통 인프라 구축

**한 줄 요약**: 모든 후속 Phase가 사용할 AWS 기반 클라우드 인프라를 Terraform IaC로 구성한다.

**핵심 완료 기준:**
- [ ] `terraform apply` 성공, 상태 파일 S3 백엔드에 저장
- [ ] EKS 클러스터 `kubectl get nodes` → 3 노드 `Ready`
- [ ] RDS PostgreSQL Multi-AZ Failover 테스트 통과 (<30초)
- [ ] MSK Kafka 프로듀서·컨슈머 왕복 레이턴시 <5ms
- [ ] HashiCorp Vault `vault status` → `Sealed: false`
- [ ] Prometheus + Grafana 대시보드 접근 가능 (포트 3000)

---

### Phase 1: 통신 레이어 구축

**한 줄 요약**: RFID/ANPR 이벤트를 수신하는 gRPC Gateway와 외부 통합용 REST API Gateway를 구성한다.

**핵심 완료 기준:**
- [ ] gRPC TollEvent 수신 1,000 req/s 무손실 처리
- [ ] REST OpenAPI 3.1 스펙 `/docs` 경로에서 조회 가능
- [ ] MSK 토픽 `toll-event-raw` → `toll-event-validated` 파이프라인 동작
- [ ] Circuit Breaker (Resilience4j) OPEN → HALF_OPEN → CLOSED 시나리오 통과

---

### Phase 2: 트랜잭션 엔진

**한 줄 요약**: SLFF(단일 구간)·MLFF(다구간) 요금 계산 엔진 및 실시간 정산 처리 파이프라인을 구현한다.

**핵심 완료 기준:**
- [ ] SLFF 세션 매칭 정확도 ≥ 99.5%
- [ ] MLFF 다구간 시나리오 100개 테스트 케이스 통과
- [ ] 10,000 TPS 부하 테스트 p95 레이턴시 <200ms
- [ ] 정산 배치 일 마감 15분 이내 처리

---

### Phase 3: 계정 관리

**한 줄 요약**: 사용자·차량·RFID 태그 등록 및 KYC, eKYC 인증 흐름을 구현한다.

**핵심 완료 기준:**
- [ ] 사용자 등록·수정·삭제 API 커버리지 100%
- [ ] KYC 문서 업로드 → 승인 워크플로우 E2E 통과
- [ ] 차량 번호판 변경 이력 추적 (감사 로그 확인)
- [ ] RBAC 역할별 접근 제한 통합 테스트 통과

---

### Phase 4: 빌링 & 정산

**한 줄 요약**: Channel A(선불 RFID)·Channel B(후불 ANPR) 이중 정산 흐름 및 수수료 계산 엔진을 구현한다.

**핵심 완료 기준:**
- [ ] Channel A 잔액 차감 → 영수증 생성 E2E 통과
- [ ] Channel B 후불 청구서 생성 → FPX 결제 연동 통과
- [ ] 수수료 계산 (Plaza × Lane × 구간 × 차종) 정확도 100%
- [ ] 월 마감 정산 리포트 T+1 07:00 자동 생성

---

### Phase 5: 위반 & 집행

**한 줄 요약**: ANPR 이미지 분석을 통한 위반 감지, 고지서 발송, 법적 처리 흐름을 구현한다.

**핵심 완료 기준:**
- [ ] ANPR 위반 감지 → 고지서 초안 자동 생성 <5초
- [ ] 이미지 증거 S3 업로드 → URL 유효기간 72시간
- [ ] 위반 이의신청 워크플로우 (접수 → 검토 → 결정) E2E 통과
- [ ] PDPA 이미지 보관 30일 자동 삭제 스케줄러 동작 확인

---

### Phase 6: 장비 모니터링

**한 줄 요약**: 차선 RFID·ANPR·DSRC 장비의 상태 모니터링, 알림, OTA 펌웨어 업데이트를 구현한다.

**핵심 완료 기준:**
- [ ] 장비 헬스비트 수신 인터벌 <30초
- [ ] 장비 오프라인 감지 → Slack/SMS 알림 <2분
- [ ] OTA 펌웨어 패키지 배포 → 롤백 시나리오 통과
- [ ] Grafana 장비 대시보드 Plaza × Lane 매트릭스 표시

---

### Phase 7: 빅데이터·분석

**한 줄 요약**: Delta Lake 기반 데이터 레이크, Spark ETL 파이프라인, BI 대시보드를 구축한다.

**핵심 완료 기준:**
- [ ] Airflow DAG `daily_toll_etl` 스케줄 실행 성공
- [ ] Delta Lake Time Travel 쿼리 (7일 전 스냅샷) 동작
- [ ] Grafana BI 대시보드 KPI 10개 지표 표시
- [ ] Spark Job 1억 건 배치 처리 2시간 이내 완료

---

### Phase 8: AI 고급 기능

**한 줄 요약**: Claude 기반 Text-to-SQL 질의, ANPR 이상 감지, 요금 수입 예측 분석을 구현한다.

**핵심 완료 기준:**
- [ ] Text-to-SQL 질의 정확도 ≥ 85% (100개 벤치마크)
- [ ] 이상 거래 감지 F1-Score ≥ 0.80 (테스트셋 1만 건)
- [ ] 수입 예측 MAPE ≤ 10% (90일 예측 기준)
- [ ] AI 응답 평균 레이턴시 <3초 (95th percentile)

---

### Phase 9: 웹·모바일 앱

**한 줄 요약**: BOS Admin Web(React), Operator 모바일 앱(React Native), 고객 셀프서비스 앱을 개발한다.

**핵심 완료 기준:**
- [ ] BOS Admin 페이지 Lighthouse 점수 ≥ 85 (Performance)
- [ ] React Native iOS/Android 앱 스토어 심사 통과
- [ ] Accessibility (WCAG 2.1 AA) 핵심 페이지 10개 통과
- [ ] 다국어 (BM·EN·KO) 전환 UI 전체 페이지 적용

---

### Phase 10: 외부 API·MCP

**한 줄 요약**: JPJ(차량 등록청)·TnG(Touch'n Go)·FPX 결제 API 및 BOS MCP 게이트웨이를 완성한다.

**핵심 완료 기준:**
- [ ] JPJ API 차량 조회 SLA ≤ 2초 (99th percentile)
- [ ] TnG 결제 승인·취소 E2E 시나리오 통과
- [ ] FPX 온라인 뱅킹 18개 은행 연동 테스트 통과
- [ ] MCP Server `/tools/list` 응답 정상, Claude Agent 호출 통과

---

### Phase 11: 운영 이관

**한 줄 요약**: DR 구성, SLA 7일 연속 99.99% 검증, 운영팀 교육, v1.0 배포 및 Go-Live를 수행한다.

**핵심 완료 기준:**
- [ ] DR Region (ap-southeast-3) Failover RTO ≤ 4시간, RPO ≤ 1시간
- [ ] SLA 모니터링 7일 연속 99.99% 이상 유지
- [ ] 운영팀 Runbook 교육 이수 (100% 대상자)
- [ ] G-HARD Gate 7 Board 사인오프 완료

---

## 4. Phase별 예산 배분표

Agent 호출 비용은 Sonnet 4.6 기준 (Input $3/1M tokens, Output $15/1M tokens) 추정치.

| Phase | 주요 작업 | 예상 Agent 호출 수 | 예상 비용 (USD) | 비고 |
| ----- | --------- | ------------------- | --------------- | ---- |
| Phase 0 | 인프라 IaC 작성, 구성 검증 | 120~160회 | $48~64 | Terraform 모듈 복잡도 높음 |
| Phase 1 | gRPC/REST Gateway 구현 | 100~140회 | $40~56 | ProtoBuf 스키마 설계 포함 |
| Phase 2 | 트랜잭션 엔진 (핵심 로직) | 180~240회 | $72~96 | 테스트 케이스 100개 포함 |
| Phase 3 | 계정·KYC 흐름 구현 | 120~160회 | $48~64 | 외부 eKYC API 통합 |
| Phase 4 | 빌링·정산 엔진 | 160~200회 | $64~80 | Channel A/B 이중 경로 |
| Phase 5 | 위반 처리·ANPR 연동 | 100~140회 | $40~56 | 이미지 처리 포함 |
| Phase 6 | 장비 모니터링 구현 | 80~120회 | $32~48 | 장비 수 ~1,500대 기준 |
| Phase 7 | BigData ETL·BI 구축 | 140~180회 | $56~72 | Spark Job 최적화 포함 |
| Phase 8 | AI 기능 구현·튜닝 | 160~200회 | $64~80 | 모델 평가 사이클 포함 |
| Phase 9 | Frontend 앱 개발 | 180~220회 | $72~88 | iOS/Android 빌드 포함 |
| Phase 10 | 외부 API·MCP 통합 | 120~160회 | $48~64 | 3rd Party Sandbox 테스트 |
| Phase 11 | 운영 이관·Go-Live | 80~100회 | $32~40 | DR 시나리오 포함 |
| **합계** | — | **1,540~2,020회** | **$616~808** | 10% 버퍼 포함 시 ~$900 |

> **비용 최적화 전략**: Worker Agent는 Haiku 4.5 사용 (3× 비용 절감), Orchestrator만 Sonnet 4.6 사용.

---

## 5. 전체 타임라인 (월별 Gantt)

```
             Apr      May      Jun      Jul      Aug      Sep      Oct      Nov      Dec      Jan
             W4  W1 W2 W3 W4  W1 W2 W3 W4  W1 W2 W3 W4  W1 W2 W3 W4  W1 W2 W3 W4  W1 W2 W3 W4  W1 W2 W3 W4  W1 W2 W3 W4  W1 W2

Phase 0      [======]
             인프라

Phase 1              [======]
                     통신

Phase 6              [======]
                     장비 (병렬)

Phase 2                       [========]
                               트랜잭션

Phase 3                                  [======]
                                         계정

Phase 4                                  [========]
                                         빌링 (병렬)

Phase 5                                  [======]
                                         위반 (병렬)

Phase 7                                           [========]
                                                  빅데이터

Phase 8                                                    [========]
                                                           AI (병렬)

Phase 9                                                    [========]
                                                           앱 (병렬)

Phase 10                                                           [======]
                                                                   외부 API

Phase 11                                                                    [======]
                                                                            운영이관

Gate 0  ◆
Gate 1       ◆
Gate 2           ◆
Gate 3                ◆
Gate 4                               ◆
Gate 5                                               ◆
Gate 6                                                           ◆
Gate 7                                                                               ◆
```

**마일스톤 요약:**
- **M1** (2026-05-12): Phase 0 완료 — 인프라 기반 준비
- **M2** (2026-06-02): Phase 1, 6 완료 — 통신·장비 기반 준비
- **M3** (2026-07-28): Phase 2 완료 — 핵심 트랜잭션 엔진 가동
- **M4** (2026-09-08): Phase 3, 4, 5 완료 — BOS 핵심 기능 완성
- **M5** (2026-10-27): Phase 6, 7 완료 — 빅데이터 플랫폼 가동
- **M6** (2026-11-24): Phase 8, 9 완료 — AI·앱 서비스 오픈
- **M7** (2026-12-15): Phase 10 완료 — 외부 통합 완성
- **M8** (2027-01-14): Phase 11 완료 — **Go-Live v1.0**

---

## 6. 리스크 매트릭스

| Phase | 주요 리스크 | 발생 확률 | 영향도 | 심각도 | 대응 방안 |
| ----- | ----------- | --------- | ------ | ------ | --------- |
| 0 | AWS 리전 서비스 제한 (ap-southeast-3) | 중 (30%) | 높음 | HIGH | ap-southeast-1 임시 사용 후 이전 |
| 0 | Terraform State 충돌 | 낮 (10%) | 중간 | MEDIUM | S3 DynamoDB 락 설정 필수 |
| 1 | RFID 제조사 gRPC 스키마 비호환 | 중 (35%) | 높음 | HIGH | ProtoBuf Adapter Layer 설계 |
| 2 | MLFF 세션 매칭 정확도 미달 | 중 (25%) | 매우높음 | CRITICAL | 알고리즘 POC → 정확도 검증 선행 |
| 3 | 말레이시아 eKYC API 계약 지연 | 높 (45%) | 높음 | HIGH | 내부 KYC 플로우 대체 구현 준비 |
| 4 | FPX 정산 마감 시간 변동 | 중 (30%) | 높음 | HIGH | 어댑터 패턴으로 유연한 스케줄 처리 |
| 5 | PDPA 이미지 보관 규정 해석 불명확 | 중 (35%) | 중간 | MEDIUM | Legal Counsel 자문 선행 |
| 6 | 레거시 장비 펌웨어 OTA 미지원 | 높 (50%) | 중간 | HIGH | 현장 수동 업데이트 프로세스 병행 |
| 7 | Spark 클러스터 비용 폭증 | 낮 (20%) | 중간 | MEDIUM | Spot Instance + 비용 알림 설정 |
| 8 | Claude API 레이턴시 SLA 미달 | 낮 (15%) | 중간 | MEDIUM | 응답 캐싱 + 프롬프트 최적화 |
| 9 | 앱스토어 심사 거절 | 중 (25%) | 높음 | HIGH | 심사 가이드라인 선행 검토, 2주 여유 |
| 10 | TnG API 버전 Deprecation | 중 (30%) | 높음 | HIGH | API 버전 협약 명문화, 어댑터 설계 |
| 11 | Go-Live 후 트래픽 급증 | 높 (60%) | 매우높음 | CRITICAL | HPA 오토스케일 사전 부하 테스트 |

**전체 리스크 요약:**
- CRITICAL: 2건 (Phase 2 세션 매칭, Phase 11 트래픽 급증)
- HIGH: 7건 — 미티게이션 계획 수립 후 진행
- MEDIUM: 4건 — 모니터링 후 필요 시 조치

---

## 7. G-HARD 게이트 연계

각 Phase가 통과해야 하는 G-HARD 게이트와 책임 승인자를 정의한다.

| Gate | 이름 | 연계 Phase | 목표 G-HARD 점수 | 승인자 | SLA |
| ---- | ---- | ---------- | ---------------- | ------ | --- |
| **Gate 0** | Discovery & Planning | Phase 시작 전 | ≤ 4 (Yellow) | CEO + CFO | 2026-04-21 |
| **Gate 1** | Technical Architecture Review | Phase 0 진입 전 | ≤ 3 (Green) | CTO + Security Lead | 2026-05-06 |
| **Gate 2** | Team & Resource Allocation | Phase 1 진입 전 | ≤ 4 (Yellow) | COO + CFO | 2026-05-27 |
| **Gate 3** | Development Sprint Planning | Phase 2 진입 전 | ≤ 3 (Green) | PM + QA Lead | 2026-06-17 |
| **Gate 4** | MVP Development Completion | Phase 4, 5 완료 후 | ≤ 3 (Green) | CTO + QA Lead | 2026-09-09 |
| **Gate 5** | Beta Testing & Pilot | Phase 7 완료 후 | ≤ 3 (Green) | PM + Security Lead | 2026-10-27 |
| **Gate 6** | Pre-Production Readiness | Phase 9, 10 완료 후 | ≤ 2 (Green) | CTO + Operations | 2026-12-15 |
| **Gate 7** | Go-Live Authorization | Phase 11 완료 후 | ≤ 2 (Green) | CEO + Board | 2027-01-07 |

**게이트 통과 조건 요약:**
```
Gate 점수 0~2 → GREEN  → CEO/CTO 사인으로 즉시 진행
Gate 점수 3~5 → YELLOW → Steering Committee 검토 (1주 SLA)
Gate 점수 6~7 → RED    → Board 심화 검토 (2주 이상)
Gate 점수 8+  → BLOCKED → 재계획 후 재심의
```

상세 의사결정 항목 → [05_governance/01_decision_gates.md](../05_governance/01_decision_gates.md)

---

## 8. Phase 간 입출력 매핑 (Input / Output)

각 Phase의 선행 입력물(Input)과 후행 Phase에 전달하는 산출물(Output)을 정의한다.
Agent는 이 매핑 테이블을 통해 어떤 산출물이 준비된 후 자신의 Phase를 시작할 수 있는지 확인한다.

| Phase | Input (선행 산출물) | Output (후행 전달 산출물) |
| ----- | ------------------- | ------------------------- |
| **Phase 0** | Gate 1 승인서, Terraform 모듈 코드 | EKS kubeconfig, RDS Endpoint, MSK Bootstrap URL, Redis Endpoint, Vault URL, Prometheus URL |
| **Phase 1** | Phase 0 Output 전체, ProtoBuf 스키마 (RFID 제조사 제공) | gRPC Gateway URL, REST API Base URL, MSK 토픽 목록, Schema Registry URL |
| **Phase 2** | Phase 1 Output, SLFF/MLFF 요금 테이블 (Plaza × 차종 × 구간) | Transaction Service API, Settlement Batch Job, Kafka `transaction-created` 토픽 |
| **Phase 3** | Phase 2 Output, KYC/eKYC API 계약서, RFID 태그 제조사 스펙 | User Service API, Vehicle Service API, Tag Management API, RBAC 역할 구성 |
| **Phase 4** | Phase 2, 3 Output, 은행 FPX 가맹점 코드, TnG 파트너 키 | Billing Service API, Settlement Report (T+1), 수수료 계산 엔진 |
| **Phase 5** | Phase 2, 3 Output, ANPR 카메라 스펙, 법무팀 위반 처리 기준 | Violation Service API, 위반 고지서 템플릿, 이미지 증거 URL |
| **Phase 6** | Phase 0 Output, 장비 대수 목록 (Plaza × Lane), OTA 펌웨어 패키지 | Equipment Health API, 장비 상태 Kafka 토픽, Grafana 장비 대시보드 |
| **Phase 7** | Phase 2, 4 Output, BI 요구사항 명세 (KPI 목록 10+개) | Delta Lake 테이블 스키마, Airflow DAG, Grafana BI 대시보드, Spark Job 라이브러리 |
| **Phase 8** | Phase 7 Output, Claude API 키, AI 학습 데이터셋 | Text-to-SQL API, 이상 감지 API, 예측 분석 API, AI 평가 리포트 |
| **Phase 9** | Phase 3, 4, 5 Output, UX 디자인 파일 (Figma), 다국어 번역본 | BOS Admin Web URL, iOS App TestFlight, Android App APK, 앱스토어 심사 결과 |
| **Phase 10** | Phase 2, 4 Output, JPJ API 키, TnG API 문서, FPX Merchant ID | External API Adapter, MCP Server URL, MCP tools/list 스펙 |
| **Phase 11** | Phase 0~10 Output 전부, 운영팀 인수인계 체크리스트, DR 훈련 시나리오 | Go-Live 완료 보고서, SLA 7일 연속 리포트, 운영 Runbook v1.0, Gate 7 사인오프 |

### 8.1 핵심 산출물 저장 위치

```
산출물 유형          저장 위치
──────────────       ──────────────────────────────────────────────
Terraform State      s3://bos-terraform-state/
K8s Manifests        github.com/your-org/malaysia-bos/infra/k8s/
Helm Values          github.com/your-org/malaysia-bos/infra/helm/
API 스펙 (OpenAPI)   github.com/your-org/malaysia-bos/docs/api/
ProtoBuf 스키마      github.com/your-org/malaysia-bos/proto/
Grafana 대시보드     github.com/your-org/malaysia-bos/infra/grafana/
Delta Lake 스키마    s3://bos-delta-lake-processed/ (DDL 스크립트)
AI 모델 평가 결과   s3://bos-artifacts/ai-eval/
운영 Runbook         docs/06_phases/11_phase11_deploy.md 내 포함
```

---

## 9. Agent 역할 매핑 — Phase별 담당

각 Phase에서 활성화되는 Paperclip Agent 목록. 상세 역할 정의 → [01_business/04_organization_roles.md](../01_business/04_organization_roles.md)

| Phase | 리드 Agent | 참여 Agent | 승인 Agent |
| ----- | ---------- | ---------- | ---------- |
| Phase 0 | devops-lead | devops-dev-1, devops-dev-2 | CTO |
| Phase 1 | backend-lead | backend-dev-1, devops-dev-1 | CTO |
| Phase 2 | transaction-lead | backend-dev-1, backend-dev-2, qa-lead | CTO |
| Phase 3 | account-lead | backend-dev-1, security-lead | CPO |
| Phase 4 | billing-lead | backend-dev-2, finance-analyst | CFO |
| Phase 5 | violation-lead | backend-dev-1, legal-analyst, security-lead | Compliance |
| Phase 6 | equipment-lead | devops-dev-1, backend-dev-2 | CTO |
| Phase 7 | bigdata-lead | da-lead, dba-lead, devops-dev-2 | CIO |
| Phase 8 | ai-lead | bigdata-lead, backend-dev-1 | CTO |
| Phase 9 | frontend-lead | frontend-dev-1, frontend-dev-2, ux-designer | CPO |
| Phase 10 | integration-lead | backend-dev-1, security-lead | CTO |
| Phase 11 | devops-lead | pm, operations-manager, qa-lead | CEO + Board |

**PM Agent 역할:** 모든 Phase에서 일정 추적·리스크 관리·보고를 담당. Phase 리드 Agent의 요청 시 즉시 지원.

---

## 10. Phase 진행 현황 추적 (State Tracker)

PM Agent는 각 Phase 완료 시 아래 체크리스트를 업데이트하고 `STATE.md`와 동기화한다.

| Phase | 상태 | 완료일 | 담당 Lead | 커밋 해시 | 비고 |
| ----- | ---- | ------ | --------- | --------- | ---- |
| Phase 0 | ⏳ 대기 | — | devops-lead | — | Gate 1 통과 후 시작 |
| Phase 1 | ⏳ 대기 | — | backend-lead | — | Phase 0 완료 후 |
| Phase 2 | ⏳ 대기 | — | transaction-lead | — | Phase 1 완료 후 |
| Phase 3 | ⏳ 대기 | — | account-lead | — | Phase 2 완료 후 |
| Phase 4 | ⏳ 대기 | — | billing-lead | — | Phase 2, 3 완료 후 |
| Phase 5 | ⏳ 대기 | — | violation-lead | — | Phase 2, 3 완료 후 |
| Phase 6 | ⏳ 대기 | — | equipment-lead | — | Phase 0, 2 완료 후 |
| Phase 7 | ⏳ 대기 | — | bigdata-lead | — | Phase 2, 4 완료 후 |
| Phase 8 | ⏳ 대기 | — | ai-lead | — | Phase 7 완료 후 |
| Phase 9 | ⏳ 대기 | — | frontend-lead | — | Phase 3, 4, 5 완료 후 |
| Phase 10 | ⏳ 대기 | — | integration-lead | — | Phase 2, 4 완료 후 |
| Phase 11 | ⏳ 대기 | — | devops-lead | — | Phase 0~10 전부 완료 후 |

**상태 코드:**
- `⏳ 대기` — 선행 Phase 완료 대기 중
- `🔄 진행 중` — 현재 실행 중
- `✅ 완료` — 완료 기준 전항목 통과, 커밋됨
- `🚫 블록` — 리스크 또는 Gate 실패로 중단

---

## 11. GSD 실행 명령어 — Phase 전환 흐름

```bash
# 현재 전체 진행률 확인
/gsd:progress

# 특정 Phase 계획 상세 논의
/gsd:discuss-phase 0    # Phase 0 (인프라)
/gsd:discuss-phase 1    # Phase 1 (통신)
# ... Phase 번호를 바꿔 반복

# 특정 Phase 상세 계획 수립
/gsd:plan-phase 0

# 특정 Phase 실행
/gsd:execute-phase 0

# 특정 Phase 완료 검증 (완료 기준 체크리스트 자동 검사)
/gsd:verify-work 0

# 마일스톤 완료 기록
/gsd:complete-milestone "Phase 0: 공통 인프라 구축 완료"

# 다음 Phase 자동 추천
/gsd:next

# 전체 Phase 상태 요약 보고
/gsd:session-report

# Phase 간 의존성 위반 검사
/gsd:health
```

**Phase 전환 규칙:**
1. 현재 Phase의 완료 기준 체크리스트 100% 통과 후에만 다음 Phase 시작
2. G-HARD 게이트 점수가 Red(6+)이면 `/gsd:pause-work` 실행 후 Board 검토 대기
3. 병렬 Phase(예: Phase 3, 4, 5)는 동시에 `/gsd:execute-phase`를 별도 세션에서 실행
4. 블로커 발생 시 `/gsd:debug` 후 devops-lead → CTO 에스컬레이션

---

## 12. 참조 문서

| 문서 | 경로 | 설명 |
| ---- | ---- | ---- |
| GSD 워크플로우 | [04_dev/05_gsd_workflow.md](../04_dev/05_gsd_workflow.md) | Phase 실행 명령어 |
| 7 Wave 로드맵 | [.planning/ROADMAP.md](../../.planning/ROADMAP.md) | Wave 기반 실행 계획 |
| G-HARD 게이트 | [05_governance/01_decision_gates.md](../05_governance/01_decision_gates.md) | 8단계 의사결정 게이트 |
| 예산 모델 | [04_dev/06_budget_model.md](../04_dev/06_budget_model.md) | Agent 비용 상세 |
| 조직 & 역할 | [01_business/04_organization_roles.md](../01_business/04_organization_roles.md) | Paperclip 29 Agent |
| 기술 스택 | [02_system/03_tech_stack.md](../02_system/03_tech_stack.md) | 기술 선택 매트릭스 |
| 프로젝트 헌장 | [01_business/01_project_charter.md](../01_business/01_project_charter.md) | 전략 비전 |
| 시스템 개요 | [02_system/01_system_overview.md](../02_system/01_system_overview.md) | 3-Layer 아키텍처 |

---

*문서 생성: 2026-04-02*
*버전: v1.0*
*다음 검토: Phase 0 완료 후 (2026-05-12)*
