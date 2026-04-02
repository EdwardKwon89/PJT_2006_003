# Malaysia SLFF·MLFF Tolling Back Office System
# AI Agent 기반 개발 최종 계획서 v1.0

---
> 작성일: 2026년 4월 | 상태: 최종 확정 | Board 승인 필요

---

# CHAPTER 1. 프로젝트 개요

## 1.1 프로젝트 목적

한국의 성숙한 Tolling 시스템(HiPass ETCS)을 기준 모델로 삼아, 말레이시아 RFID/ANPR 기반 SLFF(Single Lane Free Flow) 및 MLFF(Multi-Lane Free Flow) Tolling Back Office System(BOS)을 구축한다. AI Agent 기반 개발 환경을 활용하여 개발 속도와 품질을 동시에 확보하고, 말레이시아 수주를 시작으로 우즈베키스탄·필리핀·브라질로 확장하는 글로벌 Tolling 솔루션 플랫폼을 구축하는 것을 최종 목표로 한다.

## 1.2 사업 모델

```
JVC (우리 회사)
├── SLFF/MLFF 시스템 구축 비용 투자
├── 시스템 전반 운영 관리
├── 통행료의 3~12% 수수료 수취
└── Toll Plaza·Toll Center 직접 운영 (JVC 소속)

수익 구조:
  통행료 수입 전체
    → JVC 수수료 차감 (3~12%)
    → 잔액을 Clearing Center가 유료도로 운영사(TOC)에 지급
```

## 1.3 타겟 시장

| 우선순위 | 국가 | 방식 | 시기 |
|---|---|---|---|
| 1 | 말레이시아 | SLFF MVP → MLFF 확장 | 2026~2027 |
| 2 | 우즈베키스탄 | BOS 재사용 + 현지화 | 2027~2028 |
| 3 | 필리핀 | BOS 재사용 + 현지화 | 2027~2028 |
| 4 | 브라질 | BOS 재사용 + 현지화 | 2028~ |

---

# CHAPTER 2. 말레이시아 시장 및 도메인 이해

## 2.1 말레이시아 Tolling 시장 현황 (2026 기준)

- 총 유료도로: 5,000km (40% 유료), 33개 콘세셔네어
- PLUS 일일 트랜잭션: 약 180만 건
- KL 일일 차량: 약 600만 대
- TnG Titan Flow MLFF POC 완료 (2025.10, Alam Impian)
- PLUS JustGo ANPR Pilot 진행 중 (2025.10~, 13개 플라자)
- 6개 컨소시엄 MLFF 입찰 경쟁 중 → **수주 기회**
- 정부 B2B 모델: 콘세셔네어가 파트너 직접 선택 가능

## 2.2 SLFF → MLFF 전환 로드맵

```
현재 (RFID 배리어)  →  SLFF  →  MLFF
  30km/h 배리어       50km/h     고속 다차로 자유 통과
  RFID 전용           배리어 제거  RFID+ANPR+LiDAR 통합
```

## 2.3 물리적 운영 조직 구조

```
JVC (시스템 구축·운영·수수료 수취)
│
├── Toll Center (JVC 소속 — 유료도로별 운영 본부)
│   ├── 전 Plaza 데이터 수집·집계
│   ├── 이상 거래·면제·할인 영상 재심사
│   ├── 수입금·미납금 집계
│   └── Clearing Center 청구 및 조정
│
├── Toll Plaza (JVC 소속 — 영업소 단위)
│   ├── 통행료 수납 (RFID/ANPR)
│   ├── 미납금 수납
│   ├── 통행량 집계
│   ├── 수납금 집계
│   ├── 심사
│   ├── 지불 매체 판매·충전
│   └── 장비 모니터링·보수
│
├── Clearing Center (독립 기관)
│   ├── 지불 매체 발행·판매·충전 (JVC RFID, ANPR 계좌)
│   ├── 결제 처리 (Account 과금)
│   ├── TnG 등 타 정산 기관 연계 정산
│   ├── 수수료 차감 후 TOC 지급
│   └── ANPR 연동 Account 서비스 (은행·간편결제 연계)
│
└── 유료도로 운영사 (TOC) — 조회 권한만
    ├── SLFF/MLFF 설치 공간 제공
    ├── 수수료 제외 통행료 수령 (Clearing Center로부터)
    ├── 기존 Manual Tolling 자체 운영 (별개)
    └── API/MCP 통해 BOS 데이터 조회 (읽기 전용)
```

## 2.4 집계 단위 체계 (5단계)

```
Line (차로) → Plaza (영업소) → 유료도로 → TOC (운영사) → JVC 전체
```

모든 트랜잭션은 위 5단계 참조 필드를 포함하며, 각 단계별 독립 집계가 가능해야 한다.

## 2.5 결제 구조 (최종 확정)

```
통행 발생 → 통행 이력 기록 (BOS)
         ↓
      발급 주체 판별
         ├── Channel A: JVC/Clearing 발행 RFID or ANPR 등록 계좌
         │              → Clearing Center Account 과금
         │              → 미납 시: JPJ 조회 → 통지서 발행 → 수납
         │
         └── Channel B: TnG 발행 RFID
                        → TnG 정산 요청 (방식은 TnG 협의)
                        → TnG → JVC 정기 정산 입금
                        → TnG 미납: 별도 프로세스 (현지 RnR 정의 후)
         ↓
      수납 금액 집계 (Clearing Center)
         ↓
      JVC 수수료 차감 (3~12%)
         ↓
      TOC 지급 (Clearing Center → 각 TOC)
```

## 2.6 한국 모델(HiPass ETCS) 기반 GAP 분석

| 구분 | 직접 적용 가능 | 현지화 필요 | 신규 개발 |
|---|---|---|---|
| 구간 요금 계산 로직 | ✅ | | |
| 미납 단계별 처리 | ✅ | | |
| 영업소 수입금 집계 | ✅ | | |
| 이의신청 워크플로 | ✅ | | |
| 정산 배치 처리 | ✅ | | |
| RFID 프로토콜 | | 🔄 DSRC→ISO18000-6C | |
| 결제 연동 | | 🔄 TnG·FPX | |
| 차량 DB 연동 | | 🔄 JPJ API | |
| 세금 처리 | | 🔄 GST 6% | |
| 다국어 | | 🔄 BM/EN | |
| MLFF 세션 매칭 | | | ⭐ 신규 |
| AI 장애 자동 복구 | | | ⭐ 신규 |
| Blockchain 정산 | | | ⭐ 신규 |
| Text-to-SQL | | | ⭐ 신규 |
| 요금 시뮬레이션 | | | ⭐ 신규 |

---

# CHAPTER 3. 시스템 구성

## 3.1 3개 Application 레이어

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1. Operations Web / App Application                  │
│  • BOS 운영 Admin Web (React + Ant Design Pro, BM/EN)       │
│  • 현장 운영자 Mobile App (React Native)                    │
│  • 역할·조직 기반 데이터 접근 제어 (RBAC)                   │
│  • 이상 거래 영상 재심사 UI                                  │
│  • 면제·할인 처리 UI                                        │
│  • 스마트 커스터마이징 (커스텀 필드·Workflow 설정)           │
│  • Text-to-SQL 자연어 데이터 조회                           │
│  • 업무 판단 AI (이상 탐지·자동 의사결정)                   │
├─────────────────────────────────────────────────────────────┤
│  Layer 2. Communication Application                         │
│  • RFID/ANPR 장비 이벤트 실시간 수신 (gRPC·Kafka)           │
│  • 장비 ↔ BOS 양방향 실시간 통신 (WebSocket)               │
│  • 외부 시스템 연동 (JPJ·TnG·FPX·ANPR Engine)              │
│  • External API (TOC 기존 시스템 연계)                      │
│  • BOS MCP Server (TOC AI Agent 연계)                       │
│  • AI 장애 탐지 및 자동 복구                                │
├─────────────────────────────────────────────────────────────┤
│  Layer 3. Big Data / Analytics Platform                     │
│  • 교통 빅데이터 실시간 수집·저장·분석                      │
│  • 실시간 스트리밍 분석 (Kafka + Spark Streaming)           │
│  • 배치 분석 (Spark Batch + Airflow)                        │
│  • 데이터 레이크 (AWS S3 + Delta Lake)                      │
│  • 혁신 서비스 (시뮬레이션·예측·외부 데이터 판매)           │
└─────────────────────────────────────────────────────────────┘
```

## 3.2 BOS 서비스 도메인 (10개)

| # | 도메인 | 핵심 기능 |
|---|---|---|
| 1 | Transaction Processing | RFID/ANPR 이벤트 처리, Channel A/B 분기, MLFF 세션 매칭 |
| 2 | Account & Vehicle Mgmt | Clearing Center Account 관리, 차량 등록, JPJ 연동 |
| 3 | Billing & Settlement | 요금 계산, Clearing Center 정산, GST, Blockchain |
| 4 | Violation & Enforcement | 위반 탐지·분류·고지서 발행, 이의신청 |
| 5 | Paid/Unpaid Management | 미납 Tier 관리, JPJ 차단 연계, RPA 자동화 |
| 6 | Exemption & Discount | 면제 차량 등록, 할인 코드 관리 |
| 7 | Transaction Review | 이상 거래 영상 재심사, 심사 이력 |
| 8 | Lane Equipment Monitoring | 장비 상태, 예측 정비, AI 자동 복구 |
| 9 | Reporting & Analytics | 5단계 집계, LLM 규제 리포트, 빅데이터 분석 |
| 10 | External API & MCP | TOC 연계 REST API, BOS MCP Server |

## 3.3 기술 스택

```
[Application]
  Web:    React 18 + TypeScript + Ant Design Pro
  Mobile: React Native + Expo
  Comm:   Java 21 + Spring Boot 3.x + gRPC + Kafka

[Backend / Database]
  Core:        Java 21 + Spring Boot 3.x + Spring Batch
  RDBMS:       PostgreSQL 16 (RLS 기반 멀티테넌시)
  시계열:      TimescaleDB (장비 데이터)
  캐시:        Redis 7 (세션·MLFF Entry/Exit)
  검색:        Elasticsearch 8 (번호판·위반 조회)
  메시지:      Apache Kafka (10,000 TPS)

[Big Data]
  레이크:      Delta Lake on AWS S3
  분석:        Apache Spark 3.x + Airflow
  SQL:         Trino (SQL-on-Lake, Text-to-SQL 연동)

[AI/ML]
  LLM:         Claude API (Opus·Sonnet·Haiku)
  ML 서빙:     Python + FastAPI
  MLOps:       MLflow

[Blockchain]
  플랫폼:      Hyperledger Fabric (정산 감사 로그)

[Infrastructure]
  컨테이너:    Docker + Kubernetes (EKS)
  클라우드:    AWS ap-southeast-1 (싱가포르 리전)
  CI/CD:       GitHub Actions + Blue-Green 배포
  모니터링:    Prometheus + Grafana + ELK
```

## 3.4 외부 연동

| 시스템 | 용도 | 방식 |
|---|---|---|
| JPJ API | 차량 소유자 조회, 번호판 검증, 도로세 차단 | REST API |
| TnG | Channel B 정산 수령 | REST API (협의) |
| FPX | 실시간 계좌이체 | REST API |
| ANPR Engine | 번호판 OCR | REST API (외부 엔진) |
| 은행/간편결제 | Clearing Account 충전 | 각 사 API |
| TOC 기존 시스템 | 데이터 조회 연계 | BOS External API·MCP |

## 3.5 AI 기능 체계

```
[Text-to-SQL]        자연어 → SQL → 결과 반환 (역할 기반 쿼리 제한)
[업무 판단 AI]       위반 자동 분류, 미납 리스크 스코어링, 이상 탐지
[RPA]                JPJ 차단·고지서 발송·LLM 리포트 자동화
[AI 장애 탐지]       사전 예측, 자동 복구, RCA 자동 생성
[요금 시뮬레이션]    요금 변경 시나리오 → 통행량·수입 예측
```

## 3.6 혁신 서비스 포트폴리오

```
시뮬레이션:   요금 변경·동적 요금제·이벤트 시나리오
빅데이터:     교통 패턴 분석, 미납 예측, 혼잡 예측, 장비 예측 정비
신규 사업:    Fleet Management, 교통 데이터 외부 판매, 탄소 크레딧
```

---

# CHAPTER 4. 데이터 거버넌스

## 4.1 DA(Data Architect) 선행 작업 (Phase 1 Day 1 필수)

- 전체 논리/물리 ERD 설계 (50+ 테이블)
- 비즈니스 용어 사전 (KO / EN / BM 3개 언어, 300+ 용어)
- 코드 값 표준 (차량 등급·위반 유형·조직 유형·결제 채널)
- 5단계 집계 참조 필드 체계 (line_id·plaza_id·highway_id·toc_id)
- RBAC 데이터 접근 경계 설계 (RLS 기반)
- Text-to-SQL용 데이터 카탈로그
- Apache Atlas 기반 META 데이터 관리

## 4.2 RBAC 구조 (최종)

```
[조직 계층]
JVC 최고관리자    → 전체 데이터 + 수수료 정산
JVC 운영자        → 전체 데이터 (수수료 제외)
Clearing Center   → 계정·결제·정산 데이터
Toll Center 장    → 담당 유료도로 전체
Toll Center 직원  → 담당 유료도로 전체
Plaza 관리자      → 해당 영업소만
Plaza 직원        → 해당 영업소만
TOC 관리자        → 소속 유료도로 조회 (읽기 전용)
TOC 운영자        → 소속 유료도로 조회 (읽기 전용)
개인 이용자       → 본인 데이터만

[기능 권한]
단순 조회 → 심사 → 조정 요청 → 청구 → 청구 완료
각 역할별 허용 단계는 기능 권한 매트릭스 별도 관리
```

## 4.3 보안 정책

- PostgreSQL Row-Level Security (조직별 데이터 격리)
- PDPA (Personal Data Protection Act 2010) 준수
- ANPR 이미지 보존: 정상 30일 / 위반 90일 / 분쟁 종결까지
- 개인정보 마스킹 (역할별 차등: 이름 홍*동, IC ****1234)
- Blockchain 불변 감사 로그 (모든 트랜잭션·정산 이력)
- TLS 1.3, AES-256, OWASP Top 10 준수

---

# CHAPTER 5. 개발 환경 (AI Agent 툴체인)

## 5.1 전체 툴체인

```
[IDE & 코드 생성]
  VS Code + Claude Code Extension
  Google Antigravity (Phase 7+ 병행 도입 검토)

[개발 방법론]
  GSD (Get Shit Done) — Phase 기반 개발 관리
  npx get-shit-done-cc@latest --claude --local

[Agent 조직 관리]
  Paperclip — AI Agent 회사 운영 플랫폼
  npx paperclipai onboard --yes

[터미널 환경]
  cmux — macOS 멀티 터미널 (Agent별 독립 탭)

[MCP 연동]
  Jira, GitHub, Supabase, Confluence, Slack, Linear, Notion, Atlassian
```

## 5.2 모델 배분 전략 (비용 최적화)

| Tier | 모델 | Agent | 비용/MTok |
|---|---|---|---|
| 1 | Claude Opus 4.6 | CEO·CTO·DA Lead·AI Lead·CIO | $5/$25 |
| 2 | Claude Sonnet 4.6 | RBAC·Integration·Billing·Text2SQL·Comm·PM | $3/$15 |
| 3 | Gemini 3.1 Pro | Transaction·Violation·Lane·Frontend·DevOps·DBA·Security | $2/$12 |
| 4 | Gemini 3.1 Flash | BigData·Innovation Planner·BigData SvcDesigner·MLOps | $0.5/$3 |
| 5 | Gemini Flash-Lite | Compliance·META·Data Modeler·QA·Performance·UX | $0.1/$0.4 |

---

# CHAPTER 6. Paperclip 조직 구성 (최종 v4.0)

## 6.1 전체 조직도 (29개 Agent)

```
Board (나) — 이사회 / 최종 의사결정자
└── CEO [Opus $80] — 전체 조율·주간 보고·Board 인터페이스
    │
    ├── CTO [Opus $80] — 기술 아키텍처 총괄
    │   ├── [Data Governance]
    │   │   ├── DA Lead [Opus $60] ★ Phase 1 Day 1 필수
    │   │   ├── Data Modeler [Flash-Lite $40→$20]
    │   │   └── META Agent [Flash-Lite $35→$15]
    │   │
    │   ├── [Application Division]
    │   │   ├── Web App Lead [Sonnet $45]
    │   │   │   └── RBAC Specialist [Sonnet $35]
    │   │   ├── Mobile App Lead [Gemini Pro $35→$25]
    │   │   └── Comm App Lead [Sonnet $45]
    │   │         (External API + BOS MCP Server 포함)
    │   │
    │   ├── [Backend Division]
    │   │   ├── Transaction Engine [Gemini Pro $35→$25]
    │   │   │     (Channel A/B 분기, MLFF 세션 매칭)
    │   │   ├── Billing & Settlement [Sonnet $35]
    │   │   │     (Clearing Center 정산, TnG 정산 수령)
    │   │   ├── Integration [Sonnet $35]
    │   │   │     (JPJ·TnG·FPX·ANPR Engine·External API)
    │   │   ├── Violation & Unpaid [Gemini Pro $30→$20]
    │   │   └── Lane & Equipment [Gemini Pro $30→$20]
    │   │
    │   ├── [AI/Data Division]
    │   │   ├── AI Lead [Opus $60]
    │   │   │   ├── Text2SQL [Sonnet $35]
    │   │   │   ├── BigData Engineer [Gemini Flash $40→$15]
    │   │   │   └── MLOps [Gemini Flash $35→$15]
    │   │
    │   └── [Infra/Security Division]
    │       ├── DevOps [Gemini Pro $35→$25]
    │       ├── Security & Blockchain [Gemini Pro $35→$25]
    │       └── DBA [Gemini Pro $40→$28]
    │
    ├── CPO [Sonnet $50] — 제품 로드맵·UX 전략
    │   └── UX Designer [Flash-Lite $30→$12]
    │
    ├── CIO [Opus $70] — 교통/Tolling 도메인 혁신 기획
    │   ├── Innovation Planner [Gemini Flash $50→$20]
    │   └── BigData SvcDesigner [Gemini Flash $45→$18]
    │
    ├── PM [Sonnet $45] — Phase 관리·Jira MCP
    │   ├── QA Lead [Flash-Lite $35→$14]
    │   └── Performance Agent [Flash-Lite $20→$8]
    │
    └── Compliance [Flash-Lite $25→$10]
```

## 6.2 예산 집계 (하이브리드 모델 기준)

| 단계 | 활성 Agent | 예상 월 비용 | 커버 Phase |
|---|---|---|---|
| 1단계 | 13개 | ~$380 | Phase 1~3 |
| 2단계 | 21개 | ~$530 | Phase 4~6 |
| 3단계 | 26개 | ~$620 | Phase 7~9 |
| 4단계 | 29개 | ~$720 | Phase 10~12 |

*Claude+Gemini 하이브리드 기준 (순수 Claude 대비 약 40% 절감)

## 6.3 정기 보고 체계

```
일일:   CEO → Board  오후 6시 (완료·진행·블로커 3줄 요약)
주간:   CEO → Board  월요일 오전 (주간 보고서 + Approval 목록)
격주:   CIO → CEO → Board (혁신 서비스 현황)
Phase:  PM → QA → CEO → Board (완료 보고 + 다음 Phase 승인 요청)
```

---

# CHAPTER 7. Skills 파일 전체 목록 (21개)

## 도메인 지식 (5개)
```
malaysia-tolling-domain.md      — SLFF/MLFF, 차종, 요금, 3개 언어 용어
traditional-tolling-roles.md    — 전통 구조 vs JVC 모델, 각 기관 역할
rfid-anpr-interface.md          — 프로토콜, 이벤트 포맷, Channel A/B
mlff-session-matching.md        — Entry/Exit 매칭 알고리즘, Timeout
traffic-engineering-knowledge.md — 탄력성 계수, 시뮬레이션 공식
```

## 외부 연동 (4개)
```
jpj-integration.md              — JPJ API, 차량 조회, 번호판 클론 탐지
tng-payment.md                  — TnG 정산 채널, 배치/실시간 요청
clearing-center-operations.md   — Account 관리, 정산 흐름, TOC 지급
external-api-mcp.md             — REST API 스펙, BOS MCP Tool 목록
```

## 데이터 거버넌스 (4개)
```
data-architecture-standards.md  — DB 명명 규칙, 5단계 집계 구조
metadata-management.md          — Atlas 운영, 용어 사전(KO/EN/BM)
rbac-data-boundary.md           — 조직별 접근 범위, RLS 패턴
text-to-sql-engine.md           — 허용 테이블, 자연어 별칭, 보안 필터
```

## AI/혁신 (4개)
```
ai-fault-detection.md           — 임계값, 복구 절차, K8s 트리거
rpa-workflows.md                — JPJ 차단, 고지서 발송, 리포트 제출
simulation-design.md            — 시뮬레이션 파라미터, 출력 포맷
bigdata-service-framework.md    — 서비스 카탈로그, 분석 방향
```

## 운영 프로세스 (4개)
```
payment-failure-scenarios.md    — 결제 실패 유형별 처리 흐름
ai-decision-policy.md           — 자동 결정 허용 범위, 책임 귀속
code-quality-standards.md       — 커버리지 목표, 정적 분석 기준
change-management.md            — 변경 유형별 처리, 영향도 분석
```

---

# CHAPTER 8. 의사결정 게이트 체계

## 8.1 전체 게이트 맵

| 게이트 | 유형 | 시점 | 핵심 확인 항목 |
|---|---|---|---|
| G-HARD 0 | 필수 정지 | 착수 전 | 전략·수수료율·예산·법인 구조 |
| **G-HARD 1** | **필수 정지** | **M1 2~3주** | **요구사항 정의 확정 (FRD/NFR)** |
| G-REVIEW 1 | 검토 | M1 3~4주 | 한국→말레이시아 GAP 분석 |
| **G-HARD 2** | **필수 정지** | **M2 1~2주** | **업무 프로세스 확정 (To-Be)** |
| **G-HARD 3** | **필수 정지** | **M2 말** | **데이터·기술 규약 확정** |
| G-HARD 4 | 필수 정지 | M3 | UI/UX 프로토타입 승인 |
| Phase 착수 | 반복 (매 Phase) | Phase 시작 | 계획 검토 및 착수 승인 |
| Phase 완료 | 반복 (매 Phase) | Phase 완료 | QA 결과 검토 및 다음 Phase 승인 |
| G-HARD 5 | 필수 정지 | M8 전후 | SLFF MVP 검수 및 납품 승인 |
| G-HARD 6 | 필수 정지 | M9 | MLFF 확장 착수 승인 |
| G-HARD 7 | 필수 정지 | Phase 8 후 | 혁신 서비스 사업화 승인 |

## 8.2 G-HARD 1 — 요구사항 확정 상세

```
확정 필수 항목:
  □ 8개 도메인 기능 요건 목록 (FRD)
  □ MVP 범위 vs 전체 범위 구분 (MoSCoW)
  □ 조직별 역할 & 기능 권한 매트릭스
  □ Channel A/B 결제 흐름 확정
  □ TnG 미납 처리: 미결 사항으로 명시적 표기
  □ 5단계 집계 단위 요건
  □ External API·MCP 제공 범위
  □ 현금 수납 BOS 통합 여부
  □ 면제·할인 처리 범위
  □ 이상 거래 심사 프로세스
  □ 비기능 요건 (10,000 TPS, 99.99% 가용성 등)
```

---

# CHAPTER 9. 개발 Phase 전체 계획 (12개 Phase)

## Phase 01: 공통 인프라 구축 (M1~M2)

**목표:** 전체 시스템의 기반. DA Lead 선행 작업 후 개발 착수.

```
DA Lead 선행 (Week 1):
  전체 ERD v1.0, 용어 사전, 코드 값 표준
  5단계 집계 참조 필드 체계, RBAC 설계
  Text-to-SQL 데이터 카탈로그

구현 항목:
  멀티테넌시 (PostgreSQL RLS, 유료도로별 격리)
  Auth·RBAC (OAuth2 + JWT, 30+ 역할)
  5단계 집계 참조 필드 기반 구조
  Kafka 클러스터 (토픽 설계)
  Kubernetes + CI/CD (GitHub Actions)
  Apache Atlas 데이터 카탈로그
  커스텀 필드·Workflow 엔진 기반
  Blockchain (Hyperledger Fabric) 기반 설정
  Mock 테스트 환경 (JPJ·TnG·RFID 시뮬레이터)
  오픈소스 라이선스 자동 검사 (CI/CD 포함)

완료 기준:
  □ ERD v1.0 Board 승인
  □ RBAC 30개 역할 구현 검증
  □ 유료도로별 데이터 격리 확인
  □ Kafka 처리량 기준치 확인
  □ Mock 서버 전체 시나리오 동작
```

## Phase 02: Communication Application (M2~M3)

**목표:** 장비 ↔ BOS 실시간 통신 레이어 완성.

```
구현 항목:
  RFID 이벤트 수신 서버 (gRPC + Kafka)
  ANPR 이벤트 수신 + 외부 OCR 엔진 연동
  Channel A/B 판별 로직 (Tag ID 파싱)
  장비 상태 WebSocket 실시간 통신
  JPJ API 연동 (차량 조회 Mock)
  TnG API 연동 (정산 요청 Mock)
  FPX API 연동 (Mock)
  AI 장애 탐지 Prometheus 기반 구조
  통신 이중화·Failover

성능 목표:
  RFID: < 50ms / ANPR: < 200ms / Kafka: 10,000 msg/sec

완료 기준:
  □ RFID/ANPR 이벤트 E2E 테스트
  □ 10,000 TPS 부하 테스트
  □ Failover 시나리오 검증
```

## Phase 03: Transaction Processing Engine (M3~M4)

**목표:** 핵심 비즈니스 로직. Channel 분기 및 MLFF 세션 매칭.

```
구현 항목:
  Channel A: Clearing Center Account 과금 흐름
  Channel B: TnG 정산 요청 흐름
  MLFF Entry/Exit 세션 매칭 (Redis TTL 24h)
  요금 계산 엔진 (차종·구간·시간대·할인·면제)
  TnG 미납 케이스 격리 테이블 (처리 로직 보류)
  5단계 집계 참조 필드 자동 부여
  실시간 집계 업데이트 (WebSocket Push)
  결제 실패 시나리오 처리 (전체 유형 정의)

완료 기준:
  □ Channel A/B 분기 E2E 테스트
  □ MLFF 세션 매칭 정확도 99.9%
  □ 요금 계산 정확성 100%
  □ TnG 미납 격리 동작 확인
```

## Phase 04: Account & Vehicle Management (M4~M5)

**목표:** Clearing Center 자체 Account 관리 완성.

```
구현 항목:
  Clearing Center Account 관리
    (선불·후불·법인 Account)
  RFID 태그 발행·판매·충전 (Clearing Center)
  ANPR 연동 Account (은행·간편결제 연계)
  차량 등록·RFID 태그 연결
  JPJ 실시간 차량 조회 연동
  번호판 클론 탐지 AI
  면제 차량 등록 모듈
  할인 코드 관리
  TOC 전용 조회 기능 (소속 유료도로, 읽기 전용)

완료 기준:
  □ JPJ 실시간 연동 검증
  □ 클론 탐지 시나리오 테스트
  □ TOC 읽기 전용 권한 격리 확인
```

## Phase 05: Billing & Settlement (M5~M6)

**목표:** Clearing Center 정산 구조 완성. Blockchain 정산 투명성.

```
구현 항목:
  Clearing Center 정산 처리 (Spring Batch)
    Channel A 수납금 일별 집계
    TnG 정산 수령 검증 및 Reconciliation
    JVC 수수료 차감 (3~12%)
    TOC별 지급 처리
  GST 세금계산서 자동 생성 (6%)
  Blockchain 정산 기록 (Hyperledger Fabric)
  5단계 집계 정산 내역 생성
  TOC 정산 조회 포털 (읽기 전용)
  정산 이상 AI 탐지

완료 기준:
  □ 일별 정산 배치 정확성 100%
  □ Blockchain 무결성 검증
  □ GST 세금계산서 현지 검증
  □ TOC 정산 조회 권한 격리
```

## Phase 06: Violation, Unpaid & Review (M6~M7)

**목표:** 위반·미납 자동화 + 이상 거래 심사.

```
구현 항목:
  위반 유형 분류 AI (V001~V006)
  미납 Tier 1~4 자동 에스컬레이션
  JPJ 도로세 차단 연계 (RPA)
  고지서 자동 생성·발송 (BM/EN, RPA)
  이의신청 워크플로
  이상 거래 영상 재심사 UI
    (ANPR 이미지 조회, 심사 처리, 이력 관리)
  면제·할인 처리 검증
  Toll Center의 Clearing Center 청구·조정

완료 기준:
  □ 위반 분류 정확도 95% 이상
  □ RPA 고지서 발송 E2E 검증
  □ 영상 재심사 UI 심사관 검증
```

## Phase 07: Lane Equipment Monitoring (M7~M8)

**목표:** AI 장애 예측·자동 복구 시스템 완성.

```
구현 항목:
  전국 플라자 장비 실시간 지도 대시보드
  TimescaleDB 시계열 저장
  AI 장애 예측 (ML 모델)
  자동 복구 (K8s + RCA 리포트)
  현장 모바일 앱 알림·조치 기록
  Critical·Warning·Info 알림 체계

완료 기준:
  □ AI 장애 예측 정밀도 80% 이상
  □ 자동 복구 시나리오 테스트
  □ 현장 모바일 앱 E2E 검증
```

## Phase 08: Big Data Platform (M8~M9)

**목표:** 교통 빅데이터 플랫폼 완성. 혁신 서비스 기반 데이터 제공.

```
구현 항목:
  Delta Lake on S3 스키마 설계·적재
  Spark Streaming (실시간 교통량 집계)
  Spark Batch (일별·월별 통계)
  Airflow DAG (배치 파이프라인)
  Trino SQL-on-Lake (Text-to-SQL 연동)
  교통 패턴 분석 대시보드 (D01·D02·D04)

완료 기준:
  □ 데이터 적재 정확성 검증
  □ Spark 스트리밍 지연 < 5분
  □ Trino 쿼리 응답 < 10초
```

## Phase 09: AI 고도화 (M9~M10)

**목표:** Text-to-SQL, 업무 판단 AI, MLOps 완성.

```
구현 항목:
  Text-to-SQL 엔진 (Claude API + RBAC 필터)
  업무 판단 AI 고도화 (위반·미납·이상 탐지)
  RPA 완전 자동화
  MLOps 파이프라인 (MLflow + Drift Detection)
  요금 시뮬레이션 서비스 v1.0
  빅데이터 분석 서비스 완성

완료 기준:
  □ Text-to-SQL 정확도 90% 이상
  □ RPA 자동화 100%
  □ 시뮬레이션 서비스 Board 데모
```

## Phase 10: Web / Mobile Application (M10~M11)

**목표:** 운영 Web·Mobile 완성. 스마트 커스터마이징 UI 완성.

```
구현 항목:
  역할별 맞춤 Web 대시보드 (30개 역할)
    Plaza 직원: 단순 조회
    Toll Center: 심사·집계
    Clearing Center: 정산·지급
    TOC: 읽기 전용 조회
    JVC: 전체 관리
  이상 거래 영상 재심사 UI
  Workflow 편집기 (BPMN 시각화)
  커스텀 필드 Builder (드래그&드롭)
  Text-to-SQL 자연어 조회 UI
  현장 Mobile App (알림·조치·RFID 판매)
  BM/EN 완전 다국어

완료 기준:
  □ 30개 역할 UI 테스트
  □ 다국어 완성도 100%
  □ WCAG 2.1 AA 접근성
```

## Phase 11: External API & MCP + 통합 테스트 (M11~M12)

**목표:** TOC 연계 API 완성 + 전체 시스템 통합 검증.

```
구현 항목:
  External REST API (TOC 기존 시스템 연계)
    GET 통행량·수입금·정산·미납·장비 상태
    OAuth2 인증, IP Whitelist, OpenAPI 문서
  BOS MCP Server (TOC AI Agent 연계)
    Tools: 조회 5종, 인증 연동
  
  통합 테스트:
    SLFF 완전 시나리오 (Channel A/B 포함)
    MLFF Entry/Exit 매칭 전체
    위반→고지→이의신청→종결
    미납 Tier 1~4 에스컬레이션
    TOC 데이터 격리 검증
    정산 전 과정 (수수료 차감→TOC 지급)
  
  보안:
    OWASP Top 10 스캔·수정
    PDPA 전수 감사
    침투 테스트

완료 기준:
  □ External API E2E 검증
  □ MCP Tools 동작 검증
  □ 통합 시나리오 전수 Pass
  □ OWASP Zero 취약점
```

## Phase 12: 운영 이관 & 문서화 (M12)

**목표:** 말레이시아 콘세셔네어 납품 준비 완성.

```
구현 항목:
  운영 매뉴얼 (BM/EN, 역할별)
  API 문서 자동 생성 (OpenAPI)
  장애 대응 Runbook
  교육 자료 (운영자·기술자)
  콘세셔네어 온보딩 자동화
  혁신 서비스 데모 패키지 준비
  운영팀 전환 계획 실행
  타겟 국가 확장 전략 수립 (우즈베키스탄 시작)
```

---

# CHAPTER 10. 단계적 Agent 활성화 계획

## 1단계 — Phase 1~3 착수 ($380/월 추정)

```
활성화 (13개):
  CEO, CTO
  DA Lead ★(Day 1), Data Modeler, META Agent
  RBAC Specialist, Comm App Lead
  Transaction Engine, Integration
  DevOps, DBA, Security & BC
  PM, Compliance

완료 목표:
  ✅ ERD v1.0 Board 승인
  ✅ Mock 테스트 환경 완성
  ✅ RFID/ANPR E2E 파이프라인
  ✅ Channel A/B 분기 동작
  ✅ MLFF 세션 매칭 동작
  ✅ RBAC 30개 역할 구현
```

## 2단계 — Phase 4~6 추가 ($530/월 추정)

```
추가 활성화 (8개):
  CPO, UX Designer
  Web App Lead, Billing & Settlement
  Violation & Unpaid, Lane & Equipment
  QA Lead, Performance Agent

완료 목표:
  ✅ Clearing Center Account 시스템
  ✅ 면제·할인·이상 거래 심사
  ✅ 정산 배치 (GST·Blockchain)
  ✅ 미납 Tier 자동화·RPA
```

## 3단계 — Phase 7~9 추가 ($620/월 추정)

```
추가 활성화 (5개):
  AI Lead, Text2SQL, BigData Engineer
  MLOps, Mobile App Lead

완료 목표:
  ✅ AI 장애 예측·자동 복구
  ✅ 빅데이터 플랫폼
  ✅ Text-to-SQL·업무 판단 AI
  ✅ 시뮬레이션 서비스
```

## 4단계 — Phase 10~12 + Innovation ($720/월 추정)

```
추가 활성화 (3개):
  CIO, Innovation Planner, BigData SvcDesigner

완료 목표:
  ✅ Web·Mobile App 완성
  ✅ External API·MCP Server
  ✅ 혁신 서비스 수익화 모델
  ✅ 납품 준비 완료
```

---

# CHAPTER 11. Board 의사결정 전체 목록

## 즉시 결정 (G-HARD 0 — 착수 전)

| # | 결정 사항 |
|---|---|
| 1 | Clearing Center와 JVC의 법적 관계 (별도 법인 vs 내부 조직) |
| 2 | JVC 수수료율 목표 범위 (협상 하한선) |
| 3 | 1순위 타겟 콘세셔네어 선정 |
| 4 | 말레이시아 현지 법무법인 선임 |
| 5 | Toll Plaza·Center 운영 인력 (JVC 직고용 vs 위탁) |
| 6 | 초기 예산 승인 ($380/월 1단계) |

## G-HARD 1 전 결정 (M1 2주)

| # | 결정 사항 |
|---|---|
| 7 | 현금 수납 데이터 BOS 통합 여부 |
| 8 | TnG 외 타 지불 매체 연계 범위 (Grab Pay 등) |
| 9 | TOC 기존 시스템 API 연계 의무화 여부 |
| 10 | 결제 실패 시 후불 전환 권한 기준 |

## G-HARD 2 전 결정 (M2 1주)

| # | 결정 사항 |
|---|---|
| 11 | AI 자동 결정 허용 범위 (Level 1~3 경계) |
| 12 | TnG 미납 처리 책임 구조 (현지 RnR 협의 후) |

## G-HARD 3 전 결정 (M2 말)

| # | 결정 사항 |
|---|---|
| 13 | 클라우드 리전 확정 (AWS 싱가포르 vs Azure Malaysia) |
| 14 | TnG 연동 방식 (건당 실시간 vs 배치) |
| 15 | 보안 인증 취득 종류·시점 (ISO 27001 등) |

## Phase 진행 중

| # | 결정 사항 | 시점 |
|---|---|---|
| 16 | SLFF MVP 검수 및 납품 승인 | G-HARD 5 |
| 17 | MLFF 확장 착수 승인 | G-HARD 6 |
| 18 | 혁신 서비스 외부 판매 범위·가격 | Phase 8 후 |
| 19 | Innovation Division 활성화 시점 | Phase 8 완료 |
| 20 | 혁신 서비스 사업화 승인 | G-HARD 7 |
| 21 | 타겟 국가 확장 착수 승인 | Phase 12 후 |

---

# CHAPTER 12. 전체 일정 (12개월)

```
M1:  Phase 1 착수 — DA 선행 + 공통 인프라
     G-HARD 0, G-HARD 1, G-REVIEW 1, G-HARD 2, G-HARD 3

M2:  Phase 1 완료 + Phase 2 착수
     G-HARD 4 (UI/UX 프로토타입)

M3:  Phase 2 완료 + Phase 3 착수

M4:  Phase 3 완료 + Phase 4 착수
     2단계 Agent 활성화

M5:  Phase 4 완료 + Phase 5 착수

M6:  Phase 5 완료 + Phase 6 착수

M7:  Phase 6 완료 + Phase 7 착수
     ★ G-HARD 5: SLFF MVP 내부 검수

M8:  Phase 7 완료 + Phase 8 착수
     3단계 Agent 활성화

M9:  Phase 8 완료 + Phase 9 착수
     ★ G-HARD 6: MLFF 확장 착수 승인

M10: Phase 9 완료 + Phase 10 착수
     4단계 Agent 활성화 (Innovation Division)

M11: Phase 10 완료 + Phase 11 착수

M12: Phase 11 완료 + Phase 12 착수
     ★ 말레이시아 콘세셔네어 납품 준비 완료
     ★ G-HARD 7: 혁신 서비스 사업화 승인
     ★ 타겟 국가 확장 전략 수립 시작
```

---

# CHAPTER 13. 즉시 시작 — 실행 순서

```bash
# Step 1: 개발 환경 구성
npx get-shit-done-cc@latest --claude --local
/gsd:new-project  → "Malaysia SLFF/MLFF Tolling BOS"

# Step 2: Skills 파일 21개 생성
mkdir -p skills/{malaysia-tolling-domain,traditional-tolling-roles,...}

# Step 3: Paperclip 설치 및 회사 생성
npx paperclipai onboard --yes
# Company: Malaysia-Tolling-BOS
# Goal: "말레이시아 RFID/ANPR 기반 SLFF·MLFF BOS 구축.
#        2027년 Q1까지 SLFF MVP 납품 가능 수준 완성."
# Budget: $380/월 (1단계)

# Step 4: 1단계 Agent 채용 순서
# CEO → Board 승인 → CEO 전략 수립
# → DA Lead (Day 1 필수) → Data Modeler → META Agent
# → CTO → PM → DevOps → DBA → Security & BC
# → RBAC Specialist → Comm App Lead
# → Transaction Engine → Integration → Compliance

# Step 5: CEO 초기 지시 티켓
"Malaysia SLFF/MLFF Tolling BOS 개발 전략 수립 후
 Board 승인 요청하세요.
 포함: Phase 1 상세 계획, DA 선행 작업 일정,
       수수료 구조 분석, 타겟 콘세셔네어 후보 3개"

# Step 6: G-HARD 0 처리 (Board 승인)

# Step 7: Phase 1 착수
/gsd:discuss-phase 1
/gsd:plan-phase 1
/gsd:execute-phase 1
```

---

*Malaysia SLFF/MLFF Tolling BOS 최종 계획서 v1.0*
*작성: AI Agent 기반 협업 설계 | 검토: Board*
*다음 갱신: G-HARD 1 (요구사항 확정) 완료 후*
