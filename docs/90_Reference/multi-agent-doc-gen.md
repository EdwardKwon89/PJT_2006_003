# Malaysia BOS 문서 세트
## Multi-Agent 병렬 생성 실행 전략

---

## 1. 실행 전략 개요

```
총 46개 파일을 7개 Wave로 나눠 병렬 생성
각 Wave는 독립적 Agent가 담당 폴더 전체를 생성
Wave 내 파일들은 병렬 실행, Wave 간은 순차 실행
(하위 Wave가 상위 Wave 결과물을 참조하기 때문)
```

### Wave 순서 및 의존 관계

```
Wave 1: 00_MASTER.md (완성 — 건너뜀)
         ↓
Wave 2: 01_business/ (5개) ← 가장 먼저 — 모든 문서의 기반
         ↓
Wave 3: 03_data/ (5개)     ← 비즈니스 기반 후 데이터 설계
Wave 3: 05_governance/ (4개) ← 동시 실행 가능
         ↓
Wave 4: 02_system/ (6개)   ← 데이터 모델 기반 후 시스템 설계
         ↓
Wave 5: 04_dev/ (6개)      ← 시스템 설계 기반 후 개발 환경
         ↓
Wave 6: 06_phases/ (13개)  ← 모든 설계 완료 후 Phase 계획
         ↓
Wave 7: 07_skills/ (21개)  ← 모든 문서 기반 후 Skills 생성
```

---

## 2. Wave별 실행 방법

### 방법 A: GSD 병렬 실행 (권장)

```bash
# GSD 프로젝트 초기화 (이미 되어 있으면 건너뜀)
cd malaysia-bos-docs
/gsd:new-project

# Wave 2 실행 (01_business 폴더 — 5개 파일 병렬)
/gsd:quick --research "01_business 폴더의 5개 문서를 
  병렬로 생성해줘. 각 파일은 독립적 Sub-Agent가 담당."

# Wave 3 실행 (03_data + 05_governance 동시)
/gsd:quick "03_data 폴더 5개 + 05_governance 폴더 4개를
  병렬 생성. Wave 2 결과물 참조."
```

### 방법 B: Paperclip Multi-Agent (대규모 병렬)

```
각 Wave를 Paperclip 태스크로 등록
→ 담당 Agent에게 할당
→ Agent가 Sub-Agent 생성하여 파일별 병렬 처리
→ PM Agent가 완료 여부 추적
→ CEO가 Board에 Wave별 완료 보고
```

### 방법 C: 이 채팅에서 직접 (지금 바로)

```
Claude가 각 Wave를 순서대로 Artifact로 생성
각 파일 = 독립 Artifact
→ 다운로드 후 해당 경로에 저장

한 번에 처리 가능한 파일 수: 약 5~8개
총 소요 시간 추정: 7~10 라운드
```

---

## 3. 각 파일 생성용 마스터 프롬프트

각 Agent(또는 이 채팅)가 파일 생성 시 사용할 공통 지침:

```markdown
[공통 생성 지침]
- 파일 상단에 항상 포함:
  # 파일명
  ## 버전: v1.0 | 날짜: 2026-04
  ## 참조: 관련 문서 링크
  ## Agent 사용 지침: 이 파일을 로드해야 하는 상황

- 내용 원칙:
  1. Self-contained: 이 파일만 읽어도 이해 가능
  2. 구체적 예시 포함 (추상적 설명 금지)
  3. Agent가 즉시 실행 가능한 수준의 상세함
  4. 말레이시아 현지 요소 명시 (BM 용어, 법규, 통화)
  5. 코드 예시는 실제 동작 가능한 수준

- 분량 기준:
  비즈니스/거버넌스 문서: 300~500줄
  시스템/데이터 문서: 400~600줄
  Phase 문서: 200~400줄
  Skills 파일: 150~300줄
```

---

## 4. Wave별 생성 프롬프트 (복사해서 사용)

### Wave 2: 01_business/ (5개 파일)

```
아래 5개 파일을 각각 독립 Artifact로 생성해줘.
이전 대화의 최종 계획서 내용을 기반으로 작성.
각 파일은 [공통 생성 지침]을 따를 것.

파일 1: docs/01_business/01_project_charter.md
  내용: 프로젝트 목적, JVC 사업 모델, 수수료 구조(3~12%),
        타겟 시장(말레이시아→우즈베키스탄→필리핀→브라질),
        성공 기준, 프로젝트 범위 정의

파일 2: docs/01_business/02_market_malaysia.md
  내용: 말레이시아 시장 현황(2026), TnG/PLUS 경쟁 분석,
        6개 컨소시엄 수주 기회, SLFF→MLFF 전환 로드맵,
        한국 HiPass GAP 분석, 타겟 국가 확장 전략

파일 3: docs/01_business/03_domain_tolling.md
  내용: 전통적 Tolling 구조, 말레이시아 JVC 모델,
        Toll Plaza/Center/Clearing Center/TOC 역할 정의,
        기관별 업무 범위 상세

파일 4: docs/01_business/04_organization_roles.md
  내용: JVC 소속 조직 구조, 5단계 집계 단위(Line→Plaza→
        유료도로→TOC→JVC), 조직별 BOS 접근 권한 개요

파일 5: docs/01_business/05_payment_architecture.md
  내용: Channel A/B 결제 구조, TnG 정산 채널,
        미납 처리 흐름, JVC 수수료 차감 → TOC 지급,
        TnG 미납 미결 사항 명시
```

### Wave 3A: 03_data/ (5개 파일)

```
아래 5개 파일을 각각 독립 Artifact로 생성해줘.

파일 1: docs/03_data/01_data_architecture.md
  내용: DA 역할과 선행 작업 필수성, 데이터 설계 원칙,
        5단계 집계 참조 필드 체계, ERD 설계 방향,
        멀티테넌시 격리 전략

파일 2: docs/03_data/02_data_model.md
  내용: 핵심 테이블 목록(50+), 주요 테이블 스키마 예시,
        Channel A/B 트랜잭션 구조, 코드 값 표준 정의,
        집계 테이블 AGG_* 구조

파일 3: docs/03_data/03_rbac_design.md
  내용: 30개 역할 목록, 역할별 데이터 접근 범위,
        기능 권한 매트릭스(단순조회~청구완료),
        PostgreSQL RLS 구현 패턴, API 레벨 필터

파일 4: docs/03_data/04_metadata_glossary.md
  내용: KO/EN/BM 3개 언어 용어 사전(300+ 용어),
        코드 값 표준 테이블, 데이터 품질 규칙,
        Apache Atlas 운영 방법

파일 5: docs/03_data/05_security_compliance.md
  내용: PDPA 준수 체계, ANPR 이미지 보존·파기 정책,
        개인정보 마스킹 기준, Blockchain 감사 로그,
        보안 인증 취득 로드맵(ISO 27001 등)
```

### Wave 3B: 05_governance/ (4개 파일)

```
아래 4개 파일을 각각 독립 Artifact로 생성해줘.

파일 1: docs/05_governance/01_decision_gates.md
  내용: G-HARD 0~7 각 게이트 상세
        (시점·확인 항목·산출물·승인 기준·담당 Agent)

파일 2: docs/05_governance/02_board_decisions.md
  내용: 21개 Board 결정 사항 전체 목록
        (시점·결정 내용·담당 준비 Agent·옵션 분석)

파일 3: docs/05_governance/03_reporting_cycle.md
  내용: 일일·주간·격주·Phase 보고 체계,
        CEO 주간 보고서 템플릿,
        Paperclip Heartbeat 스케줄 연동

파일 4: docs/05_governance/04_supplement_items.md
  내용: 18개 보완 항목 전체
        (항목명·담당 Agent·처리 방법·산출물·
         계획서 반영 위치·Board 결정 필요 여부)
```

### Wave 4: 02_system/ (6개 파일)

```
아래 6개 파일을 각각 독립 Artifact로 생성해줘.

파일 1: docs/02_system/01_system_overview.md
  내용: 3개 레이어 구조, 10개 도메인 개요,
        시스템 간 데이터 흐름도

파일 2: docs/02_system/02_service_domains.md
  내용: 10개 도메인별 상세 기능 명세
        (Transaction·Account·Billing·Violation·
         Unpaid·Exemption·Review·Equipment·Reporting·API)

파일 3: docs/02_system/03_tech_stack.md
  내용: 전체 기술 스택, 성능 목표(10,000 TPS·99.99%),
        인프라 구성(K8s·AWS·CI/CD)

파일 4: docs/02_system/04_ai_features.md
  내용: Text-to-SQL·업무판단AI·RPA·AI장애탐지·
        요금시뮬레이션 상세 설계, 혁신 서비스 포트폴리오

파일 5: docs/02_system/05_external_integration.md
  내용: JPJ·TnG·FPX·ANPR 연동 상세 명세
        (API 스펙·인증·오류 처리·Mock 전략)

파일 6: docs/02_system/06_api_mcp_spec.md
  내용: External REST API 엔드포인트 목록,
        BOS MCP Server Tools 명세,
        TOC 연계 인증·보안·버전 관리
```

### Wave 5: 04_dev/ (6개 파일)

```
아래 6개 파일을 각각 독립 Artifact로 생성해줘.

파일 1: docs/04_dev/01_toolchain.md
  내용: VS Code+Claude Code 설정, GSD 설치·사용법,
        Paperclip 설치·운영, cmux 탭 구성,
        Antigravity 도입 시점 및 방법

파일 2: docs/04_dev/02_paperclip_org.md
  내용: 29개 Agent 전체 조직도,
        4단계 활성화 계획, 예산 집계,
        보고 체계, Heartbeat 스케줄

파일 3: docs/04_dev/03_agent_roles.md
  내용: Agent별 상세 설정
        (Name·Adapter·Budget·Heartbeat·
         Skills·Capabilities·Job Description)
        전체 29개 완전 기술

파일 4: docs/04_dev/04_skills_index.md
  내용: 21개 Skills 파일 목록,
        각 Skills 용도·로드 시점·주요 사용 Agent,
        Skills 작성 규칙

파일 5: docs/04_dev/05_gsd_workflow.md
  내용: GSD 명령어 전체 목록,
        Phase별 실행 절차(discuss→plan→execute→verify),
        Multi-Agent 병렬 실행 방법,
        문서 생성 자동화 방법

파일 6: docs/04_dev/06_budget_model.md
  내용: Paperclip 예산 구조 설명($가 LLM API 비용),
        Claude vs Gemini 하이브리드 모델,
        4단계 활성화별 예산($380→$530→$620→$720),
        비용 최적화 전략
```

### Wave 6: 06_phases/ (13개 파일)

```
아래 13개 파일을 각각 독립 Artifact로 생성해줘.
각 Phase 파일 포함 내용:
  - 목표 (한 문장)
  - 담당 Agent 목록
  - 선행 조건
  - 구현 태스크 상세 목록
  - GSD 실행 명령어
  - 완료 기준 (체크리스트)
  - 다음 Phase 연결

파일 목록:
  06_phases/00_phase_overview.md (전체 일정·Agent 활성화)
  06_phases/01_phase01_infra.md
  06_phases/02_phase02_comm.md
  06_phases/03_phase03_txn.md
  06_phases/04_phase04_account.md
  06_phases/05_phase05_billing.md
  06_phases/06_phase06_violation.md
  06_phases/07_phase07_equipment.md
  06_phases/08_phase08_bigdata.md
  06_phases/09_phase09_ai.md
  06_phases/10_phase10_app.md
  06_phases/11_phase11_api.md
  06_phases/12_phase12_deploy.md
```

### Wave 7: 07_skills/ (21개 SKILL.md)

```
아래 21개 SKILL.md 파일을 각각 독립 Artifact로 생성해줘.
각 SKILL.md 포맷:
---
name: [skill-name]
description: >
  Use when: [사용 상황]
  Don't use when: [비사용 상황]
---
# [Skill 제목]
[상세 지식 내용 — Agent가 즉시 활용 가능한 수준]

Skills 목록:
  malaysia-tolling-domain
  traditional-tolling-roles
  rfid-anpr-interface
  mlff-session-matching
  clearing-center-operations
  payment-failure-scenarios
  jpj-integration
  tng-payment
  external-api-mcp
  data-architecture-standards
  metadata-management
  rbac-data-boundary
  aggregation-units
  text-to-sql-engine
  ai-fault-detection
  rpa-workflows
  ai-decision-policy
  simulation-design
  bigdata-service-framework
  code-quality-standards
  change-management
```

---

## 5. 이 채팅에서 지금 바로 시작하는 방법

```
[진행 방식]
1. "Wave 2 시작해줘" → 5개 파일 Artifact 생성
2. "Wave 3A 시작해줘" + "Wave 3B 시작해줘" (동시)
3. "Wave 4 시작해줘"
4. "Wave 5 시작해줘"
5. "Wave 6 시작해줘" (13개 — 2~3 라운드로 분할)
6. "Wave 7 시작해줘" (21개 — 3~4 라운드로 분할)

[파일 저장 방법]
각 Artifact 우측 상단 "복사" 버튼 → 해당 경로에 저장
또는 Claude Code로 직접 파일 생성:
  /gsd:quick "생성된 문서 내용을 실제 파일로 저장"
```

---

## 6. GSD + Paperclip 완전 자동화 방법

```bash
# 1. GSD로 문서 생성 프로젝트 초기화
cd ~/malaysia-bos
npx get-shit-done-cc@latest --claude --local
/gsd:new-project
# → "Malaysia BOS 문서 세트 자동 생성"

# 2. Phase 설계 (7개 Wave = 7개 Phase)
/gsd:discuss-phase 1  → "01_business 폴더 5개 문서 생성"
/gsd:plan-phase 1
/gsd:execute-phase 1  → 5개 Sub-Agent 병렬 실행

# 3. Wave별 순차 실행
/gsd:execute-phase 2  → data + governance (9개 병렬)
/gsd:execute-phase 3  → system (6개 병렬)
/gsd:execute-phase 4  → dev (6개 병렬)
/gsd:execute-phase 5  → phases (13개 병렬)
/gsd:execute-phase 6  → skills (21개 병렬)

# 4. 전체 완료 후 검증
/gsd:verify-work      → 파일 존재·형식·내용 검증
```
