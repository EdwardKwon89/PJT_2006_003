# Roadmap: Malaysia BOS Documentation

**Created:** 2026-04-01
**Mode:** YOLO / Standard Granularity / Parallel Execution / Balanced (Sonnet)
**Total Phases:** 7 Wave / 12 Phase Implementation
**Total Deliverables:** 46 files + 21 Skills = 67 documents

---

## Phase Overview

```
Wave 1: Master
  â (skip — already confirmed)

Wave 2: Business Domain (5 files)
  â Phase 1

Wave 3A: Data Architecture (5 files)
  Wave 3B: Governance (4 files)
  â Phase 2

Wave 4: System Design (6 files)
  â Phase 3

Wave 5: Development Environment (6 files)
  â Phase 4

Wave 6: Phase Plans (13 files)
  â Phase 5

Wave 7: Skills Files (21 files)
  â Phase 6
```

---

## Phase Structure

### Phase 1: Wave 2 Execution (Business Domain)

**Duration:** 1 cycle (parallel execution)
**Artifacts:** 5 files (01_business/)
**Dependencies:** PROJECT.md + 00_MASTER.md (confirmed)
**Lead Agent:** CEO + CIO + PM

**Files (parallel):**
1. 01_project_charter.md — CEO (Project Charter & Vision)
2. 02_market_malaysia.md — CIO (Market Analysis)
3. 03_domain_tolling.md — Domain Expert (Tolling Structure)
4. 04_organization_roles.md — PM (Organizational Setup)
5. 05_payment_architecture.md — Billing Lead (Payment Flow)

**Success Criteria:**
- [ ] 5개 파일 모두 생성됨
- [ ] 파일 간 상호 참조 링크 작동
- [ ] 각 파일이 self-contained (독립적으로 이해 가능)
- [ ] 기초 문서(00_MASTER, 01_project_charter) 내용과 일관성

**Next Wave Dependency:** Wave 2 완료 후 Wave 3A/3B 병렬 진행 가능

---

### Phase 2: Wave 3A + 3B Execution (Data & Governance)

**Duration:** 1 cycle (Wave 3A 5개 파일 + Wave 3B 4개 파일 동시 병렬)
**Artifacts:** 9개 파일 (03_data/ + 05_governance/)
**Dependencies:** Wave 2 완료
**Lead Agent:** DA Lead (3A) + Compliance (3B)

**Wave 3A — Data Architecture (5 files, parallel):**
1. 01_data_architecture.md — DA Lead (Data Strategy)
2. 02_data_model.md — DBA (Table Definitions)
3. 03_rbac_design.md — Security Lead (Access Control)
4. 04_metadata_glossary.md — Data Steward (Glossary)
5. 05_security_compliance.md — Compliance (PDPA & Security)

**Wave 3B — Governance (4 files, parallel):**
1. 01_decision_gates.md — CEO (Decision Gates G-HARD 0~7)
2. 02_board_decisions.md — PM (21 Board Decisions)
3. 03_reporting_cycle.md — PM (Reporting Structure)
4. 04_supplement_items.md — Compliance (18 Supplement Items — already confirmed base)

**Success Criteria:**
- [ ] 9개 파일 모두 생성됨
- [ ] Wave 3A와 3B 파일 간 교차 참조 일관성
- [ ] Data Model과 RBAC의 정렬
- [ ] Decision Gates와 Supplement Items의 의사결정 프로세스 일관성

**Next Wave Dependency:** Phase 2 완료 후 Wave 4 진행

---

### Phase 3: Wave 4 Execution (System Design)

**Duration:** 1 cycle (parallel execution)
**Artifacts:** 6개 파일 (02_system/)
**Dependencies:** Phase 2 완료 (Data Model, Governance 기반)
**Lead Agent:** CTO + Backend Lead + Integration Lead

**Files (parallel):**
1. 01_system_overview.md — CTO (3-Layer Architecture)
2. 02_service_domains.md — Domain Experts (10 Service Domains)
3. 03_tech_stack.md — DevOps Lead (Technology Stack)
4. 04_ai_features.md — AI Lead (AI Features & Design)
5. 05_external_integration.md — Integration Lead (External APIs)
6. 06_api_mcp_spec.md — API Architect (BOS MCP Specification)

**Success Criteria:**
- [ ] 6개 파일 모두 생성됨
- [ ] 3-Layer Architecture와 10 Service Domains의 매핑 명확
- [ ] 외부 API 스펙(JPJ, TnG, FPX) 완전성
- [ ] AI Features와 Big Data Platform 연계 명확

**Next Wave Dependency:** Phase 3 완료 후 Wave 5 진행

---

### Phase 4: Wave 5 Execution (Development Environment)

**Duration:** 1 cycle (parallel execution)
**Artifacts:** 6개 파일 (04_dev/)
**Dependencies:** Phase 3 완료 (System Design 기반)
**Lead Agent:** CTO + DevOps + Paperclip Architect

**Files (parallel):**
1. 01_toolchain.md — DevOps Lead (Tool Setup)
2. 02_paperclip_org.md — Paperclip Architect (29-Agent Organization)
3. 03_agent_roles.md — PM (Agent Role Definitions)
4. 04_skills_index.md — Knowledge Architect (21 Skills Files Index)
5. 05_gsd_workflow.md — GSD Expert (Workflow & Commands)
6. 06_budget_model.md — CFO (Cost Model & Optimization)

**Success Criteria:**
- [ ] 6개 파일 모두 생성됨
- [ ] Paperclip 29-Agent 조직도와 Agent Roles 일관성
- [ ] 21개 Skills File Index와 Phase Plan의 매핑 명확
- [ ] GSD Workflow 명령어와 실제 실행 방식 일관성
- [ ] Budget Model의 현실성 (Agent LLM API 비용 정확성)

**Next Wave Dependency:** Phase 4 완료 후 Wave 6 진행

---

### Phase 5: Wave 6 Execution (Phase Plans)

**Duration:** 2~3 cycles (13개 파일을 3~4개씩 분할 병렬)
**Artifacts:** 13개 파일 (06_phases/)
**Dependencies:** Phase 4 완료 (Development Environment 기반)
**Lead Agent:** PM + Phase Leads (각 Phase별)

**Files (3~4개 라운드로 분할 병렬):**

**Round 1 (4개):**
1. 00_phase_overview.md — PM (Master Phase Overview)
2. 01_phase01_infra.md — DevOps + CTO (Common Infrastructure)
3. 02_phase02_comm.md — Comm App Lead (Communication Layer)
4. 03_phase03_txn.md — Transaction Engine Lead (Transaction Processing)

**Round 2 (4개):**
5. 04_phase04_account.md — Account Lead (Account Management)
6. 05_phase05_billing.md — Billing Lead (Billing & Settlement)
7. 06_phase06_violation.md — Violation Lead (Violation & Enforcement)
8. 07_phase07_equipment.md — Equipment Lead (Lane Equipment Monitoring)

**Round 3 (5개):**
9. 08_phase08_bigdata.md — BigData Lead (Big Data / Analytics)
10. 09_phase09_ai.md — AI Lead (AI Advanced Features)
11. 10_phase10_app.md — Frontend Lead (Web/Mobile Apps)
12. 11_phase11_api.md — Integration Lead (External API & MCP)
13. 12_phase12_deploy.md — DevOps + PM (Operations Handover)

**Success Criteria (Round별):**
- [ ] 각 Round 파일 생성 완료
- [ ] Phase 간 의존성 명확 (선행 Phase와 지연 Phase)
- [ ] 각 Phase의 Agent 할당과 예산 명확
- [ ] GSD 실행 명령어 정확성 (/gsd:plan-phase, /gsd:execute-phase 등)
- [ ] 완료 기준(체크리스트) 실행 가능

**Next Wave Dependency:** Phase 5 완료 후 Wave 7 진행

---

### Phase 6: Wave 7 Execution (Skills Files)

**Duration:** 3~4 cycles (21개 파일을 5~6개씩 분할 병렬)
**Artifacts:** 21개 SKILL.md 파일 (07_skills/)
**Dependencies:** Phase 5 완료 (모든 Phase Plan 기반)
**Lead Agent:** Knowledge Architect + Domain Experts

**Files (3~4개 라운드로 분할 병렬):**

**Round 1 (6개):**
1. malaysia-tolling-domain/SKILL.md
2. traditional-tolling-roles/SKILL.md
3. rfid-anpr-interface/SKILL.md
4. mlff-session-matching/SKILL.md
5. clearing-center-operations/SKILL.md
6. payment-failure-scenarios/SKILL.md

**Round 2 (6개):**
7. jpj-integration/SKILL.md
8. tng-payment/SKILL.md
9. external-api-mcp/SKILL.md
10. data-architecture-standards/SKILL.md
11. metadata-management/SKILL.md
12. rbac-data-boundary/SKILL.md

**Round 3 (6개):**
13. aggregation-units/SKILL.md
14. text-to-sql-engine/SKILL.md
15. ai-fault-detection/SKILL.md
16. rpa-workflows/SKILL.md
17. ai-decision-policy/SKILL.md
18. simulation-design/SKILL.md

**Round 4 (3개):**
19. bigdata-service-framework/SKILL.md
20. code-quality-standards/SKILL.md
21. change-management/SKILL.md

**Success Criteria (Round별):**
- [ ] 각 Round Skills 파일 생성 완료
- [ ] Skills 파일 포맷 일관성 (name, description, use when, don't use when, content)
- [ ] 각 Skills가 Agent가 즉시 실행 가능한 수준
- [ ] Skills 파일 간 교차 참조 링크 작동
- [ ] Paperclip Agent와의 매핑 명확 (어느 Agent가 어느 Skill 사용)

---

## Overall Success Criteria

### 완성도 기준

- [ ] **Coverage**: 46개 파일 + 21개 Skills = 67개 모두 생성 (100%)
- [ ] **Self-contained**: 각 파일이 독립적으로 이해 가능 (제외: 명시적 참조 문서)
- [ ] **Links**: 파일 간 참조 링크 모두 작동 (자동 검증 가능)
- [ ] **Consistency**: 용어, 약자, 숫자 정의의 일관성 (metadata glossary와 정렬)
- [ ] **Markdown**: GitHub Flavored Markdown 형식 준수 (코드블록, 표, 이미지 포함)
- [ ] **Structure**: 각 파일이 정의된 Outline 구조 준수

### 품질 기준

- [ ] **Agent Readiness**: 각 파일이 Agent가 즉시 실행 가능한 지시사항 포함
- [ ] **Business Accuracy**: 기초 문서(00_MASTER, 01_project_charter, 04_supplement_items)와의 일관성
- [ ] **Technical Depth**: 각 도메인별 충분한 기술적 깊이 (추상성 vs 구체성 균형)
- [ ] **Cross-phase Alignment**: Phase 간 의존성 및 input/output 명확

### 추적 가능성

- [ ] **Traceability Matrix**: REQUIREMENTS.md와의 매핑 완료
- [ ] **Git Commits**: Wave별 atomic commit으로 추적 가능
- [ ] **Versioning**: PROJECT.md 버전 관리 (v1.0 → v1.1 등)

---

## Execution Model

### Wave별 병렬 실행

**Wave 1:** 건너뛰기 (기존 확정 문서)
**Wave 2:** 1 cycle (5개 파일 병렬)
**Wave 3A/3B:** 동시 병렬 (9개 파일)
**Wave 4:** 1 cycle (6개 파일 병렬)
**Wave 5:** 1 cycle (6개 파일 병렬)
**Wave 6:** 2~3 cycles (13개 파일, 3~4개씩 분할)
**Wave 7:** 3~4 cycles (21개 파일, 5~6개씩 분할)

**총 소요 Cycle:** ~8~10 cycles

### GSD 명령어 (실행)

```bash
# 각 Phase별 실행

/gsd:quick "Wave 2: 01_business/ 5개 파일 병렬 생성
  â각 파일은 독립 Agent 담당, Wave 2 완료 후 Wave 3로"

/gsd:quick "Wave 3A + 3B: 03_data/ + 05_governance/ 9개 파일 동시 병렬 생성
  â Wave 2 기반, 03_data와 05_governance 교차 참조 정렬"

# ... 이런 식으로 각 Phase별 실행

/gsd:verify-work    # Phase별 완료 검증
/gsd:progress       # 전체 진행률 확인
```

---

## Timeline & Milestones

| Phase | Wave | Files | Cycles | Est. Duration | Milestone |
|-------|------|-------|--------|---------------|-----------|
| 1 | 2 | 5 | 1 | 1~2h | Business Domain Complete ✓ |
| 2 | 3A/3B | 9 | 1 | 1~2h | Data & Governance Complete ✓ |
| 3 | 4 | 6 | 1 | 1~2h | System Design Complete ✓ |
| 4 | 5 | 6 | 1 | 1~2h | DevEnvironment Complete ✓ |
| 5 | 6 | 13 | 2~3 | 2~3h | Phase Plans Complete ✓ |
| 6 | 7 | 21 | 3~4 | 3~4h | Skills Files Complete ✓ |
| **Verify & Publish** | — | — | 1 | 1~2h | **46+21 Files Ready ✓** |

**Estimated Total Duration:** 8~10 cycles × ~1h = ~8~10 hours (순차) 또는 Wave 병렬 시 ~4~6 hours

---

## Dependencies & Risks

### Critical Dependencies

1. **00_MASTER.md** → 모든 Wave (기초)
2. **PROJECT.md** → REQUIREMENTS.md → ROADMAP.md (GSD 구조)
3. **Wave 2 완료** → Wave 3A/3B 진행
4. **Wave 3A/3B 완료** → Wave 4 진행
5. **Wave 4 완료** → Wave 5 진행
6. **Wave 5 완료** → Wave 6 진행
7. **Wave 6 완료** → Wave 7 진행

### Key Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Agent 능력 부족 | 파일 품질 저하 | Research + Plan Check + Verifier 에이전트 활용 |
| 파일 간 참조 누락 | 일관성 저하 | 완료 후 자동 링크 검증 (Wave별) |
| 기초 문서와 불일치 | 의미 오류 | Compliance Agent 최종 감수 |
| LLM API 비용 초과 | Budget 운영 어려움 | Balanced 모델 선택, 비용 모니터링 |
| Wave 간 의존성 오류 | 재작업 필요 | 명확한 의존성 정의 & GSD 의존성 체크 |

---

## Post-Completion

### Phase 7: Validation & Verification

- [ ] 46개 파일 자동 생성 완료
- [ ] 21개 Skills 파일 생성 완료
- [ ] 링크 검증 (모든 참조 작동 확인)
- [ ] 용어 일관성 검증 (metadata glossary와 비교)
- [ ] Compliance Agent 최종 감수
- [ ] Git 커밋 정리 & 태깅 (v1.0)

### 산출물 저장소

- **docs/01_business/** — 5개 파일
- **docs/02_system/** — 6개 파일
- **docs/03_data/** — 5개 파일
- **docs/04_dev/** — 6개 파일
- **docs/05_governance/** — 4개 파일
- **docs/06_phases/** — 13개 파일
- **docs/07_skills/** — 21개 SKILL.md 파일

**총 67개 파일 (docs/ 폴더 하위)**

---

*Roadmap created: 2026-04-01*
*Version: v1.0*
*Last updated: 2026-04-01 after planning*
