# 시스템 아키텍처 개요
## 02_system/01_system_overview.md
## v1.0 | 2026-04 | 참조: 00_MASTER.md, 01_business/01_project_charter.md

---
> **Agent 사용 지침**
> CTO·Backend Lead·DevOps Agent가 시스템 전체 구조 파악 시 로드.
> 신규 기능 설계 또는 아키텍처 결정 전 반드시 이 문서 확인.
> 레이어 간 경계를 침범하는 설계는 CTO 승인 필요.

---

## 1. Executive Summary

Malaysia SLFF/MLFF Tolling BOS는 **3개 레이어** 구조로 설계된다. 통행료 수납부터 빅데이터 분석까지 10개 서비스 도메인을 커버하며, **10,000 TPS · 99.99% 가용성**을 목표로 한다.

```
핵심 설계 원칙:
  ① 레이어 간 명확한 책임 분리 (Layer 1 ↔ 2 ↔ 3)
  ② 이벤트 드리븐 아키텍처 (Kafka 중심)
  ③ AI-First 운영 (Paperclip 29개 Agent)
  ④ 멀티테넌시 (RLS 기반 콘세셔네어 격리)
  ⑤ 무중단 운영 (K8s + AWS 멀티 리전 DR)
```

---

## 2. 3-Layer 아키텍처 개요

```
┌─────────────────────────────────────────────────────────────────┐
│  Layer 1: Operations Layer                                       │
│  ┌─────────────────────────┐  ┌──────────────────────────────┐  │
│  │  BOS Admin Web (React)  │  │  현장 Mobile App             │  │
│  │  - BM/EN 다국어 지원    │  │  (React Native, iOS/Android) │  │
│  │  - Text-to-SQL 쿼리     │  │  - 장비 현황 실시간 조회     │  │
│  │  - 업무 판단 AI         │  │  - 위반 처리 현장 입력       │  │
│  │  - KPI 대시보드         │  │  - 오프라인 지원             │  │
│  └─────────────────────────┘  └──────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────┤
│  Layer 2: Communication Layer                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ RFID/ANPR    │  │ Core BOS     │  │ External API           │ │
│  │ Event Rcvr   │  │ Services     │  │ & MCP Server           │ │
│  │ (gRPC+Kafka) │  │ (Spring Boot)│  │ (TOC 연계)             │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ External Integration: JPJ · TnG · FPX · ANPR               │ │
│  └──────────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────────┤
│  Layer 3: Big Data / Analytics Platform                          │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────────┐ │
│  │ Delta Lake   │  │ Apache Spark │  │ Apache Airflow         │ │
│  │ (데이터 레이크)│  │ (분산 처리)  │  │ (워크플로 스케줄링)    │ │
│  └──────────────┘  └──────────────┘  └────────────────────────┘ │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │ 요금 시뮬레이션 · 교통 빅데이터 분석 · AI 고도화           │ │
│  └──────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴──────────┐
                    │  AWS Infrastructure │
                    │  Primary: ap-se-1   │
                    │  DR: ap-se-3        │
                    └────────────────────┘
```

---

## 3. Layer 1: Operations Layer

### 3.1 BOS Admin Web

```
기술 스택: React 18 + TypeScript + Tailwind CSS
배포 방식: AWS CloudFront + S3 (정적 호스팅)
지원 언어: 말레이어(BM) · 영어(EN) 기본, 한국어(KO) 옵션

주요 기능:
  ① 통행료 수납 현황 실시간 대시보드
  ② Transaction 조회·심사·정정
  ③ Account·Vehicle 관리
  ④ 위반·미납 관리 (Tier 1~4 추적)
  ⑤ Billing·Settlement 현황
  ⑥ 장비 모니터링 대시보드
  ⑦ 보고서 생성 및 다운로드
  ⑧ Text-to-SQL 자연어 쿼리 (AI 기반)
  ⑨ 업무 판단 AI (이의신청·면제 처리 권고)
  ⑩ 사용자·역할 관리 (RBAC, 30개 역할)
```

### 3.2 현장 Mobile App

```
기술 스택: React Native + Expo (iOS 15+, Android 12+)
배포 방식: App Store + Google Play (Enterprise 배포)

주요 기능:
  ① 레인별 장비 상태 실시간 확인
  ② 장애 발생 시 알림 수신 + 처리 기록
  ③ 현장 위반 이벤트 수동 입력
  ④ ANPR 이미지 현장 심사
  ⑤ 오프라인 모드 (네트워크 불안정 환경 대응)
  ⑥ 담당자 순찰 일지 기록

접근 권한: Plaza Manager · Field Technician · Supervisor 역할
```

### 3.3 AI 운영 기능 (Layer 1 내장)

| 기능 | 설명 | AI 모델 |
|------|------|---------|
| Text-to-SQL | 자연어 → SQL 변환, 복잡한 통계 쿼리 자동화 | Claude Sonnet |
| 업무 판단 AI | 이의신청·면제 처리 권고, 이상 거래 플래그 | Claude Sonnet |
| 스마트 커스터마이징 | 대시보드·보고서 레이아웃 AI 추천 | Claude Haiku |

---

## 4. Layer 2: Communication Layer

### 4.1 RFID/ANPR 이벤트 수신기

```
프로토콜: gRPC (단방향 스트리밍)
메시지 브로커: Apache Kafka (MSK Managed)
처리 목표: 10,000 TPS (피크)

이벤트 유형:
  SLFF_EVENT    — 단일 레인 RFID 통과 이벤트
  MLFF_ENTRY    — 다중 레인 RFID 진입 이벤트
  MLFF_EXIT     — 다중 레인 RFID 진출 이벤트
  ANPR_EVENT    — 번호판 인식 이벤트 (신뢰도 포함)
  EQUIPMENT_EVT — 장비 상태 변경 이벤트

Kafka Topic 구조:
  raw.rfid.events       — 원시 RFID 이벤트
  raw.anpr.events       — 원시 ANPR 이벤트
  processed.txn.events  — 처리 완료 트랜잭션
  violation.events      — 위반 이벤트
  equipment.status      — 장비 상태 이벤트
```

### 4.2 Core BOS Services

```
기술 스택: Spring Boot 3.x (Java 21)
배포: AWS EKS (Kubernetes, HPA 자동 스케일)
DB: PostgreSQL 16 (RLS 멀티테넌시), Redis 7 (캐시)

10개 서비스 도메인 (마이크로서비스 구조):
  txn-service       — Transaction Processing
  account-service   — Account & Vehicle
  billing-service   — Billing & Settlement
  violation-service — Violation & Enforcement
  unpaid-service    — Paid/Unpaid Management
  exemption-service — Exemption & Discount
  review-service    — Transaction Review
  equipment-service — Lane Equipment Monitoring
  reporting-service — Reporting & Analytics
  api-service       — External API & MCP

서비스 간 통신:
  동기: REST (내부 서비스 간)
  비동기: Kafka 이벤트 (상태 변경, 알림)
```

### 4.3 External Integration

```
연동 대상:
  ① JPJ (Jabatan Pengangkutan Jalan) — 차량 등록 조회, 도로세 차단
  ② TnG (Touch 'n Go) — Channel B 결제 정산
  ③ FPX (Financial Process Exchange) — 온라인 결제 게이트웨이
  ④ ANPR Vendor — 번호판 인식 카메라 시스템

연동 방식: REST API (HTTPS, OAuth 2.0)
재시도 정책: Exponential Backoff (최대 3회)
장애 처리: Circuit Breaker (Resilience4j)
```

### 4.4 External API & BOS MCP Server

```
External REST API:
  대상: TOC (유료도로 운영사) — 읽기 전용
  인증: API Key + IP Whitelist
  버전: /api/v1/
  하위 호환: 최소 12개월 보장

BOS MCP Server:
  대상: Paperclip AI Agent (내부 운영)
  Tools: 트랜잭션 조회, 계정 조회, 위반 이력, 장비 상태 등
  보안: JVC 내부망 전용 (외부 노출 불가)
```

### 4.5 AI 장애 탐지·자동 복구

```
담당 Agent: AI Lead + DevOps
기능:
  ① 서비스 이상 패턴 실시간 탐지 (Prometheus 메트릭 기반)
  ② 장애 원인 자동 분류 (AI 분석)
  ③ 1차 자동 복구 시도 (Pod 재시작, 스케일 업)
  ④ 복구 실패 시 DevOps Agent 에스컬레이션
  ⑤ 장애 보고서 자동 생성

탐지 지표:
  Error Rate > 1% → 경고
  Error Rate > 5% → 자동 복구 시도
  P99 Latency > 500ms → 스케일 업 트리거
```

---

## 5. Layer 3: Big Data / Analytics Platform

### 5.1 데이터 레이크 아키텍처

```
구성 요소:
  Delta Lake  — ACID 트랜잭션 지원 데이터 레이크
  Apache Spark — 대용량 분산 처리
  Apache Airflow — 배치 워크플로 스케줄링
  MinIO       — 오브젝트 스토리지 (Delta Lake 기반)

데이터 계층:
  Bronze Layer — 원시 이벤트 (변경 불가)
  Silver Layer — 정제·정규화 데이터
  Gold Layer   — 집계·분석용 데이터 마트
```

### 5.2 주요 Analytics 기능

| 기능 | 설명 | 담당 Phase |
|------|------|-----------|
| 요금 시뮬레이션 | 통행료 조정 시 수익 영향 시뮬레이션 | Phase 8 |
| 교통 패턴 분석 | 시간대·날씨별 교통 흐름 분석 | Phase 8 |
| 수익 예측 | AI 기반 월간·분기별 수익 예측 | Phase 9 |
| 이상 탐지 | 대규모 사기·클론 패턴 감지 | Phase 9 |
| TOC 운영 분석 | 콘세셔네어별 운영 효율 비교 | Phase 8 |

---

## 6. 10개 서비스 도메인 매핑

| # | 도메인 | Layer | 주요 Phase | 상세 문서 |
|---|--------|-------|-----------|----------|
| 1 | Transaction Processing | L2 | Phase 3 | [02_service_domains.md](./02_service_domains.md) |
| 2 | Account & Vehicle | L2 | Phase 4 | [02_service_domains.md](./02_service_domains.md) |
| 3 | Billing & Settlement | L2 | Phase 5 | [02_service_domains.md](./02_service_domains.md) |
| 4 | Violation & Enforcement | L2 | Phase 6 | [02_service_domains.md](./02_service_domains.md) |
| 5 | Paid/Unpaid Management | L2 | Phase 6 | [02_service_domains.md](./02_service_domains.md) |
| 6 | Exemption & Discount | L2 | Phase 6 | [02_service_domains.md](./02_service_domains.md) |
| 7 | Transaction Review | L2 | Phase 6 | [02_service_domains.md](./02_service_domains.md) |
| 8 | Lane Equipment Monitoring | L2 | Phase 7 | [02_service_domains.md](./02_service_domains.md) |
| 9 | Reporting & Analytics | L2/L3 | Phase 8 | [02_service_domains.md](./02_service_domains.md) |
| 10 | External API & MCP | L2 | Phase 11 | [06_api_mcp_spec.md](./06_api_mcp_spec.md) |

---

## 7. 핵심 데이터 흐름

### 7.1 SLFF 통행료 수납 흐름 (Channel A)

```
① 차량 RFID 태그 감지
   └── gRPC → Kafka (raw.rfid.events)

② txn-service 이벤트 소비
   └── RFID Tag → Account 조회 (account-service)
   └── 잔액 확인 → 과금 처리

③ 과금 성공
   └── Kafka (processed.txn.events)
   └── billing-service 집계
   └── reporting-service 통계 업데이트

④ 과금 실패 (잔액 부족)
   └── unpaid-service → Tier 1 등록
   └── 알림 발송 (Email/SMS)
   └── JPJ 조회 → 통지서 발행
```

### 7.2 MLFF Entry/Exit 매칭 흐름

```
① Entry 이벤트 수신
   └── MLFF_ENTRY → Kafka → txn-service
   └── Redis에 세션 저장 (TTL: 매칭 타임아웃)

② Exit 이벤트 수신
   └── MLFF_EXIT → Kafka → txn-service
   └── Redis에서 Entry 세션 조회 → 매칭

③ 매칭 성공
   └── 구간 요금 계산 → 과금 처리

④ 매칭 실패 (타임아웃)
   └── ANPR 이미지 기반 재시도
   └── 최종 실패 → review-service 수동 심사 큐
```

### 7.3 정산 흐름

```
일별 집계:
  billing-service → 콘세셔네어별 수납액 집계
  JVC 수수료 차감 (3~12%)
  TOC 지급액 산정

정기 정산 (월간):
  Clearing Center 정산 데이터 수신
  TnG 정산 수신 (Channel B)
  최종 대사 → 차액 조정

보고:
  CEO 주간 보고 (Heartbeat)
  TOC 월간 정산 보고서 발행
```

---

## 8. 성능 & 가용성 요구사항

| 지표 | 목표 | 측정 방법 |
|------|------|----------|
| 처리량 (TPS) | 10,000 TPS (피크) | Kafka 처리량 모니터링 |
| 가용성 | 99.99% (4-Nine) | 월간 다운타임 <4.4분 |
| RFID 이벤트 처리 | <100ms (P99) | Jaeger 분산 추적 |
| API 응답 시간 | <200ms (P99) | Prometheus |
| MLFF 매칭 정확도 | 99.9% | 배치 검증 |
| DR 복구 시간 (RTO) | <4시간 | DR 훈련 |
| DR 데이터 손실 (RPO) | <1시간 | Replication 지연 |

---

## 9. 보안 아키텍처 개요

```
경계 보안:
  - AWS WAF (SQL Injection, XSS 차단)
  - API Gateway (Rate Limiting, IP Whitelist)
  - VPC Private Subnet (Core Services 격리)

인증·인가:
  - JWT (Access Token 15분, Refresh Token 7일)
  - Spring Security + RBAC (30개 역할)
  - PostgreSQL RLS (콘세셔네어별 데이터 격리)

데이터 보안:
  - AES-256 암호화 (개인정보 컬럼)
  - Hyperledger Fabric (변경 불가 감사 로그)
  - ANPR 이미지 자동 파기 (PDPA 준수)

비밀 관리:
  - HashiCorp Vault (API Key, DB 암호)
  - GitHub Actions OIDC (CI/CD 시크릿 없는 배포)
```

---

## 10. 인프라 구성 (AWS 멀티 리전)

```
Primary Region: ap-southeast-1 (싱가포르)
  ├── EKS Cluster (K8s 1.29+)
  │   ├── Core BOS Services (Spring Boot)
  │   ├── Kafka Consumer Group
  │   └── AI Services (Claude API 연동)
  ├── RDS PostgreSQL 16 (Multi-AZ)
  ├── MSK (Managed Kafka, 3 Broker)
  ├── ElastiCache Redis 7 (Cluster Mode)
  ├── S3 + Delta Lake
  └── CloudFront (Admin Web CDN)

DR Region: ap-southeast-3 (자카르타)
  ├── EKS Cluster (Standby)
  ├── RDS PostgreSQL (Read Replica → Promoted)
  ├── MSK MirrorMaker 2.0 (토픽 복제)
  └── ElastiCache Redis (Standby)

Failover:
  - Route 53 Health Check 기반 자동 DNS 전환
  - RTO < 4시간 / RPO < 1시간 (Board 결정 필요 → BD-15)
```

---

## 11. 참조 문서

| 문서 | 내용 |
|------|------|
| [02_service_domains.md](./02_service_domains.md) | 10개 서비스 도메인 상세 |
| [03_tech_stack.md](./03_tech_stack.md) | 전체 기술 스택 상세 |
| [04_ai_features.md](./04_ai_features.md) | AI 기능 설계 |
| [05_external_integration.md](./05_external_integration.md) | 외부 API 연동 명세 |
| [06_api_mcp_spec.md](./06_api_mcp_spec.md) | BOS API & MCP 스펙 |
| [../01_business/01_project_charter.md](../01_business/01_project_charter.md) | 프로젝트 목적·사업 모델 |
| [../03_data/01_data_architecture.md](../03_data/01_data_architecture.md) | 데이터 아키텍처 |
| [../05_governance/01_decision_gates.md](../05_governance/01_decision_gates.md) | G-HARD 의사결정 게이트 |

---

*작성일: 2026-04*
*버전: v1.0*
*담당 Agent: CTO (총괄), Backend Lead, DevOps Lead*
