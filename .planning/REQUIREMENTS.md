# Requirements: Malaysia BOS Documentation

**Defined:** 2026-04-01
**Core Value:** AI Agent 기반 멀티-에이전트 병렬 실행으로 46개 설계 문서를 자동 생성하되, 일관성과 완성도를 보장

## v1 Requirements

46개 파일 + 21개 Skills = 67개 문서 생성. 각각 self-contained이어야 하며, Agent가 즉시 실행 가능한 수준의 품질.

### Wave 1: Master Structure

- [ ] **WAVE1-01**: 00_MASTER.md 검증 및 기존 문서 확인 (생략 가능 — 이미 확정)

### Wave 2: Business Domain (5개 파일)

- [ ] **WAVE2-01**: docs/01_business/01_project_charter.md — 프로젝트 목적, JVC 사업 모델, MVP 범위
- [ ] **WAVE2-02**: docs/01_business/02_market_malaysia.md — 말레이시아 시장 분석, TnG/PLUS 경쟁사, SLFF→MLFF 로드맵
- [ ] **WAVE2-03**: docs/01_business/03_domain_tolling.md — 통행료 징수 구조, 기관별 역할 정의, 기존 체계 비교
- [ ] **WAVE2-04**: docs/01_business/04_organization_roles.md — JVC 조직 구조, 5단계 계층 단위, 조직별 권한 정의
- [ ] **WAVE2-05**: docs/01_business/05_payment_architecture.md — Channel A/B 결제 구조, TnG 연동, 미결제 처리

### Wave 3A: Data Architecture (5개 파일)

- [ ] **WAVE3A-01**: docs/03_data/01_data_architecture.md — DA 역할, 5단계 계층, ERD 설계 방향, 메타데이터 관리
- [ ] **WAVE3A-02**: docs/03_data/02_data_model.md — 핵심 테이블 50+, Channel A/B 트랜잭션 구조, 집계 테이블 정의
- [ ] **WAVE3A-03**: docs/03_data/03_rbac_design.md — 30개 역할 목록, 역할별 데이터 접근 권한, PostgreSQL RLS
- [ ] **WAVE3A-04**: docs/03_data/04_metadata_glossary.md — KO/EN/BM 용어 사전 300+, 데이터 정의서, 검증 규칙
- [ ] **WAVE3A-05**: docs/03_data/05_security_compliance.md — PDPA 준수, ANPR 이미지 보존/삭제 정책, 보안 인증 로드맵

### Wave 3B: Governance (4개 파일)

- [ ] **WAVE3B-01**: docs/05_governance/01_decision_gates.md — G-HARD 0~7 게이트 (8개), 의사결정 항목, 책임, 산출물
- [ ] **WAVE3B-02**: docs/05_governance/02_board_decisions.md — 21개 Board 결정 사항 전체, 결정 내용, 최종 분기
- [ ] **WAVE3B-03**: docs/05_governance/03_reporting_cycle.md — 일일/주간/격주/Phase 보고 체계, CEO 주간 보고 템플릿, Heartbeat 스케줄
- [ ] **WAVE3B-04**: docs/05_governance/04_supplement_items.md — 18개 보충 항목 전체 (이미 기초 제공됨)

### Wave 4: System Design (6개 파일)

- [ ] **WAVE4-01**: docs/02_system/01_system_overview.md — 3개 레이어 구조, 10개 도메인 개요, 시스템 간 데이터 흐름
- [ ] **WAVE4-02**: docs/02_system/02_service_domains.md — 10개 도메인별 상세 기능 정의 (Transaction, Account, Billing, Violation, Unpaid, Exemption, Review, Equipment, Reporting, API)
- [ ] **WAVE4-03**: docs/02_system/03_tech_stack.md — 전체 기술 스택, 성능 목표(10,000 TPS, 99.99%), 인프라 구성(K8s, AWS, CI/CD)
- [ ] **WAVE4-04**: docs/02_system/04_ai_features.md — Text-to-SQL, 업무 판단 AI, RPA, AI 장애 진단, 가격 시뮬레이션 설계
- [ ] **WAVE4-05**: docs/02_system/05_external_integration.md — JPJ, TnG, FPX, ANPR 연동 상세 명세 (API 엔드포인트, 인증, 오류 처리)
- [ ] **WAVE4-06**: docs/02_system/06_api_mcp_spec.md — External REST API 엔드포인트 목록, BOS MCP Server Tools 명시, TOC 연계 보안

### Wave 5: Development Environment (6개 파일)

- [ ] **WAVE5-01**: docs/04_dev/01_toolchain.md — VS Code+Claude Code 설치, GSD 설치/사용법, Paperclip 설치/운영, cmux 구성, Antigravity 활용
- [ ] **WAVE5-02**: docs/04_dev/02_paperclip_org.md — 29개 Agent 전체 조직도, 4단계 계층 구조, 조직 지휘, 보고 체계, Heartbeat 스케줄
- [ ] **WAVE5-03**: docs/04_dev/03_agent_roles.md — Agent별 상세 설정 (Name, Adapter, Budget, Heartbeat, Skills, Capabilities, Job Description) 29개 전체
- [ ] **WAVE5-04**: docs/04_dev/04_skills_index.md — 21개 Skills 파일 목록, 각 Skills 용도, 로드 순서, 주요 사용 Agent, Skills 작성 규칙
- [ ] **WAVE5-05**: docs/04_dev/05_gsd_workflow.md — GSD 명령어 전체 목록, Phase별 실행 절차(discuss→plan→execute→verify), 멀티-에이전트 병렬 실행 방법
- [ ] **WAVE5-06**: docs/04_dev/06_budget_model.md — Paperclip 예산 구조 설명, Claude vs Gemini 하이브리드, 4단계 계층별 비용, 비용 최적화 전략

### Wave 6: Phase Plans (13개 파일)

- [ ] **WAVE6-01**: docs/06_phases/00_phase_overview.md — 전체 12개 Phase 일정, Agent 할당, 의존성 그래프, GSD 실행 명령어 요약
- [ ] **WAVE6-02**: docs/06_phases/01_phase01_infra.md — Phase 1 (공통 인프라) — 목표, 담당 Agent, 사전 조건, 기술 태스크 목록, 완료 기준
- [ ] **WAVE6-03**: docs/06_phases/02_phase02_comm.md — Phase 2 (통신 Application) — RFID/ANPR 이벤트 처리, gRPC+Kafka, 외부 연동
- [ ] **WAVE6-04**: docs/06_phases/03_phase03_txn.md — Phase 3 (Transaction Engine) — Channel A/B 처리 로직, 장애 시나리오, TPS 처리
- [ ] **WAVE6-05**: docs/06_phases/04_phase04_account.md — Phase 4 (Account 관리) — 계정 라이프사이클, Clearing Center 연동, 결제 매칭
- [ ] **WAVE6-06**: docs/06_phases/05_phase05_billing.md — Phase 5 (Billing & 결제) — 청구 프로세스, 수동 입금 처리, TOC 정산
- [ ] **WAVE6-07**: docs/06_phases/06_phase06_violation.md — Phase 6 (위반·사사) — 위반 등록, JPJ 통지, 미결제 관리, 감면 처리
- [ ] **WAVE6-08**: docs/06_phases/07_phase07_equipment.md — Phase 7 (장비 모니터링) — Lane 장비 상태, 실시간 알림, 통계 대시보드
- [ ] **WAVE6-09**: docs/06_phases/08_phase08_bigdata.md — Phase 8 (빅데이터 플랫폼) — Delta Lake + Spark + Airflow, 수금 시뮬레이션, 통행비 분석
- [ ] **WAVE6-10**: docs/06_phases/09_phase09_ai.md — Phase 9 (AI 고도화) — Text-to-SQL, 업무 판단 AI, RPA 자동화, AI 감시 및 복구
- [ ] **WAVE6-11**: docs/06_phases/10_phase10_app.md — Phase 10 (Web/Mobile App) — BOS Admin Web (React), 현장 Mobile App (React Native), 대시보드
- [ ] **WAVE6-12**: docs/06_phases/11_phase11_api.md — Phase 11 (API/MCP/통합테스트) — External API 엔드포인트, BOS MCP Server, 성능 테스트
- [ ] **WAVE6-13**: docs/06_phases/12_phase12_deploy.md — Phase 12 (운영 이관) — DR 설계, 데이터 마이그레이션, 운영 인수인계, 모니터링

### Wave 7: Skills Files (21개 파일)

- [ ] **WAVE7-01**: docs/07_skills/malaysia-tolling-domain/SKILL.md
- [ ] **WAVE7-02**: docs/07_skills/traditional-tolling-roles/SKILL.md
- [ ] **WAVE7-03**: docs/07_skills/rfid-anpr-interface/SKILL.md
- [ ] **WAVE7-04**: docs/07_skills/mlff-session-matching/SKILL.md
- [ ] **WAVE7-05**: docs/07_skills/clearing-center-operations/SKILL.md
- [ ] **WAVE7-06**: docs/07_skills/payment-failure-scenarios/SKILL.md
- [ ] **WAVE7-07**: docs/07_skills/jpj-integration/SKILL.md
- [ ] **WAVE7-08**: docs/07_skills/tng-payment/SKILL.md
- [ ] **WAVE7-09**: docs/07_skills/external-api-mcp/SKILL.md
- [ ] **WAVE7-10**: docs/07_skills/data-architecture-standards/SKILL.md
- [ ] **WAVE7-11**: docs/07_skills/metadata-management/SKILL.md
- [ ] **WAVE7-12**: docs/07_skills/rbac-data-boundary/SKILL.md
- [ ] **WAVE7-13**: docs/07_skills/aggregation-units/SKILL.md
- [ ] **WAVE7-14**: docs/07_skills/text-to-sql-engine/SKILL.md
- [ ] **WAVE7-15**: docs/07_skills/ai-fault-detection/SKILL.md
- [ ] **WAVE7-16**: docs/07_skills/rpa-workflows/SKILL.md
- [ ] **WAVE7-17**: docs/07_skills/ai-decision-policy/SKILL.md
- [ ] **WAVE7-18**: docs/07_skills/simulation-design/SKILL.md
- [ ] **WAVE7-19**: docs/07_skills/bigdata-service-framework/SKILL.md
- [ ] **WAVE7-20**: docs/07_skills/code-quality-standards/SKILL.md
- [ ] **WAVE7-21**: docs/07_skills/change-management/SKILL.md

## v2 Requirements

향후 릴리스에 포함될 항목들.

- **TRANS-01**: 각 파일의 KO→EN/BM 번역 (localization)
- **VERIFY-01**: 생성된 46개 파일의 의미론적 정확성 감수 (Compliance Agent 담당)
- **INTEG-01**: 파일 간 참조 링크 자동 검증 및 수정
- **VISUAL-01**: 각 섹션별 다이어그램/플로우차트 추가 (Mermaid/PlantUML)
- **SAMPLE-01**: 코드 샘플 및 Mock 구현 추가 (실제 기술 스택별)
- **AUTOMATION-01**: 문서 생성 파이프라인 자동화 (CI/CD 연동)

## Out of Scope

| 항목 | 이유 |
|------|------|
| 실제 코드 구현 | 설계 문서 생성만 범위 — 코드는 별도 프로젝트 |
| Paperclip 29개 Agent 실제 구현 | Agent 역할 정의만 제공 — 실제 구현은 Phase 12 이후 |
| 파일 번역 (KO→EN/BM) | 현재 v1은 한국어만 제공 — v2에 포함 계획 |
| 외부 시스템 실제 API 연동 테스트 | Mock 서버 기반 문서만 제공 — 실제 테스트는 Phase별 진행 |
| 대규모 데이터 마이그레이션 시뮬레이션 | 설계 문서 및 점검표만 제공 |
| 보안 감수 및 인증 취득 | Compliance Agent가 감수하지만 실제 인증은 별도 프로세스 |

## Traceability

각 v1 요구사항이 어느 Wave/Phase에 매핑되는지.

| 요구사항 | Wave | Phase | Status |
|---------|------|-------|--------|
| WAVE1-01 | Wave 1 | Master | Pending |
| WAVE2-01 | Wave 2 | Phase N/A | Pending |
| WAVE2-02 | Wave 2 | Phase N/A | Pending |
| WAVE2-03 | Wave 2 | Phase N/A | Pending |
| WAVE2-04 | Wave 2 | Phase N/A | Pending |
| WAVE2-05 | Wave 2 | Phase N/A | Pending |
| WAVE3A-01 | Wave 3A | Phase 1 | Pending |
| WAVE3A-02 | Wave 3A | Phase 3 | Pending |
| WAVE3A-03 | Wave 3A | Phase 4 | Pending |
| WAVE3A-04 | Wave 3A | Phase 3 | Pending |
| WAVE3A-05 | Wave 3A | Phase 1 | Pending |
| WAVE3B-01 | Wave 3B | Phase N/A | Pending |
| WAVE3B-02 | Wave 3B | Phase N/A | Pending |
| WAVE3B-03 | Wave 3B | Phase N/A | Pending |
| WAVE3B-04 | Wave 3B | Phase N/A | Pending |
| WAVE4-01 | Wave 4 | Phase 2 | Pending |
| WAVE4-02 | Wave 4 | Phase 2 | Pending |
| WAVE4-03 | Wave 4 | Phase 1 | Pending |
| WAVE4-04 | Wave 4 | Phase 9 | Pending |
| WAVE4-05 | Wave 4 | Phase 2 | Pending |
| WAVE4-06 | Wave 4 | Phase 11 | Pending |
| WAVE5-01 | Wave 5 | Phase 1 | Pending |
| WAVE5-02 | Wave 5 | Phase 4 | Pending |
| WAVE5-03 | Wave 5 | Phase 4 | Pending |
| WAVE5-04 | Wave 5 | Phase 7 | Pending |
| WAVE5-05 | Wave 5 | Phase 1 | Pending |
| WAVE5-06 | Wave 5 | Phase 1 | Pending |
| WAVE6-01 | Wave 6 | Phase 1 | Pending |
| WAVE6-02 to WAVE6-13 | Wave 6 | Phase 1~12 | Pending |
| WAVE7-01 to WAVE7-21 | Wave 7 | Phase 7+ | Pending |

**Coverage:**
- v1 requirements: 67개 (파일 46 + Skills 21)
- 매핑된 파일: 67개
- 미매핑: 0 ✓

---

*Requirements defined: 2026-04-01*
*Last updated: 2026-04-01 after initial definition*
