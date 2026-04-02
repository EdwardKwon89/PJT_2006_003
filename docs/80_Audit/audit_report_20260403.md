# Malaysia BOS 문서 품질 감사 보고서

> **감사 일시**: 2026-04-03
> **감사 대상**: `docs/` 전체 (68개 파일, 7개 Wave)
> **감사 유형**: 조직 운영 문서 품질 감사 (Paperclip Agent 활용 관점)
> **수정 금지**: 본 보고서는 원본 파일을 수정하지 않음

---

## 📊 감사 요약 (Executive Summary)

| 차원 | 이슈 수 | 심각도 |
|------|---------|--------|
| 1. 링크 무결성 | **54건** | 🔴 HIGH |
| 2. SKILL.md Agent 활용성 | **6건** | 🟠 MEDIUM |
| 3. 용어 일관성 | **11건** | 🟡 LOW-MED |
| 4. 섹션 구조 완전성 | **90건+** | 🟠 MEDIUM |
| 5. 콘텐츠 상호 일관성 | **2건** | 🔴 HIGH |

> **총 이슈 수**: 163건 이상
> **즉시 수정 권고**: 차원 1 (링크 무결성) + 차원 5 (Tier 기간 불일치)

---

## 차원 1: 링크 무결성 🔴 HIGH

### 1-1. SKILL.md 파일 4개 미생성 (인덱스에 등록되어 있으나 파일 없음)

`docs/04_dev/04_skills_index.md`에 등록되어 있으나 `docs/07_skills/` 내 파일이 존재하지 않음.

| # | 등록명 | 예상 경로 | 사용 Phase |
|---|--------|-----------|-----------|
| 1 | `rpa-workflows` | `docs/07_skills/rpa-workflows/SKILL.md` | Phase 8, 9 |
| 2 | `simulation-design` | `docs/07_skills/simulation-design/SKILL.md` | Phase 8 |
| 3 | `code-quality-standards` | `docs/07_skills/code-quality-standards/SKILL.md` | Phase 1~12 (전체) |
| 4 | `change-management` | `docs/07_skills/change-management/SKILL.md` | Phase 1~12 (전체) |

> [!CAUTION]
> `code-quality-standards`와 `change-management`는 전 Phase에서 사용되는 핵심 Skills임. 두 파일의 부재는 Agent가 코드 품질 기준 및 변경 관리 절차를 찾지 못하는 심각한 공백을 만든다.

### 1-2. SKILL.md 내부 참조 링크 깨짐 (49건)

Wave 7에서 생성된 SKILL.md 파일들이 `../../docs/` 경로로 참조하고 있으나, 실제 문서는 다른 경로에 위치함.

**핵심 원인**: SKILL.md 파일의 위치는 `docs/07_skills/{name}/SKILL.md`이므로,  
`../../`를 거치면 `PJT_2006_003/` 루트까지만 도달함. `docs/`를 추가로 포함해야 함.

**문제 패턴**: `../../docs/06_phases/XX.md` → 존재하지 않는 경로
**올바른 패턴**: `../../06_phases/XX.md` (이미 `docs/` 하위에 있으므로)

| 영향받는 파일 | 깨진 링크 수 |
|-------------|-----------|
| `agent-workflow-patterns/SKILL.md` | 2건 |
| `rfid-anpr-interface/SKILL.md` | 3건 |
| `data-architecture-standards/SKILL.md` | 2건 |
| `text-to-sql-engine/SKILL.md` | 2건 |
| `incident-runbook/SKILL.md` | 2건 |
| `ai-fault-detection/SKILL.md` | 2건 |
| `payment-failure-scenarios/SKILL.md` | 1건 |
| `tng-payment/SKILL.md` | 2건 |
| `clearing-center-operations/SKILL.md` | 2건 |
| `jpj-integration/SKILL.md` | 2건 |
| `rbac-data-boundary/SKILL.md` | 2건 |
| `testing-qa-strategy/SKILL.md` | 2건 |
| `metadata-management/SKILL.md` | 2건 |
| `external-api-mcp/SKILL.md` | 2건 |
| `traditional-tolling-roles/SKILL.md` | 1건 |
| `mlff-session-matching/SKILL.md` | 2건 |
| `malaysia-tolling-domain/SKILL.md` | 3건 |
| `devops-deployment/SKILL.md` | 2건 |
| `aggregation-units/SKILL.md` | 2건 |
| `ai-decision-policy/SKILL.md` | 2건 |
| `bigdata-service-framework/SKILL.md` | 1건 |

**수정 방법**: 각 SKILL.md의 `Related Documents` 섹션에서
`../../docs/XX/YY.md` → `../../XX/YY.md` 로 경로 일괄 치환

### 1-3. 존재하지 않는 문서를 참조하는 링크 (4건)

| 참조 위치 | 깨진 링크 | 비고 |
|---------|---------|------|
| `incident-runbook/SKILL.md` | `05_governance/01_settlement_governance.md` | 실제 파일명은 `01_decision_gates.md` |
| `testing-qa-strategy/SKILL.md` | `06_phases/03_phase03_infra.md` | 실제 파일명은 `03_phase03_txn.md` |
| `devops-deployment/SKILL.md` | `06_phases/03_phase03_infra.md` | 동일 오류 |
| `agent-workflow-patterns/SKILL.md` | `04_dev/02_agent_design.md` | 실제 파일명은 `02_paperclip_org.md` |

---

## 차원 2: SKILL.md Agent 활용성 🟠 MEDIUM

### 2-1. 코드 예시 부재

`metadata-management/SKILL.md` — 코드 블록이 전혀 없음.
메타데이터 관리는 Agent가 실제 SQL/API 호출 패턴을 참조해야 하는 기술 영역으로,
예시 부재 시 Agent의 실행 패턴이 불명확함.

### 2-2. 파일 분량 과소 (95줄 이하)

Agent가 참조하기에 정보 밀도가 낮은 파일:

| SKILL.md | 줄 수 | 우려 사항 |
|---------|------|---------|
| `traditional-tolling-roles` | 95줄 | 12개 역할을 95줄에 정의 → 역할당 평균 8줄 미만 |
| `clearing-center-operations` | 96줄 | 정산 절차 복잡도 대비 과소 |
| `aggregation-units` | 103줄 | 집계 단위 로직 설명 부족 가능성 |

### 2-3. `dont_use_when` 필드 내용 형식적 작성

전체 21개 SKILL.md 중 `dont_use_when` 필드는 존재하나, 실제 내용이 형식적으로 작성된 경우가 다수.
Agent의 Skill 선택 오류 방지를 위해 구체적인 반례(negative case)가 필요.

**권고**: `dont_use_when` 항목에 최소 2개 이상의 구체적 케이스를 포함할 것.

---

## 차원 3: 용어 일관성 🟡 LOW-MEDIUM

### 3-1. Write-off 표기 혼용

| 표기 방식 | 발견 위치 | 표준 여부 |
|---------|---------|---------|
| `Write-off` | `03_data/02_data_model.md`, `external-api-mcp/SKILL.md` | ✅ 표준 |
| `writeoff` (소문자 연결) | `payment-failure-scenarios/SKILL.md:51`, `rbac-data-boundary/SKILL.md:93`, `03_data/02_data_model.md:79` | ⚠️ DB 컬럼명으로는 허용, 서술 문맥에서는 비표준 |
| `Write-off / 법적 조치` | `06_phases/06_phase06_violation.md:68` | ✅ 허용 |

> **권고**: DB 컬럼명/코드 변수 내의 `writeoff`는 허용하되, 서술 문맥에서는 항상 `Write-off`로 통일. 용어집(`docs/03_data/04_metadata_glossary.md`)에 명시 권고.

### 3-2. TnG 표기 혼용

| 표기 방식 | 발견 위치 |
|---------|---------|
| `TnG` | 대부분의 문서 (표준) |
| `Touch n Go` | `docs/01_business/02_market_malaysia.md:90` (1회) |

> **권고**: `Touch n Go`는 브랜드 풀네임으로 첫 언급 시 사용하고, 이후는 `TnG`로 통일.

### 3-3. 파일명 오류로 인한 혼동

`incident-runbook/SKILL.md`가 `01_settlement_governance.md`를 참조하나, 실제 파일명은 `01_decision_gates.md`.  
이는 링크 실패이자 용어 오류(Settlement Governance vs Decision Gates)이기도 함.

---

## 차원 4: 섹션 구조 완전성 🟠 MEDIUM

### 4-1. Phase 문서 공통 헤더 오류 (10개 파일)

전체 12개 Phase 문서 중 10개 문서에서 파일 경로가 `##` 섹션 헤더로 잘못 작성됨.

**현재 (잘못된 형식)**:
```
## 06_phases/06_phase06_violation.md     ← 파일명이 헤더
## v1.0 | 2026-04 | 참조: ...           ← 버전 정보가 헤더
## 1. Phase 개요                         ← 실제 첫 섹션
```

**권고 형식**:
```markdown
---
version: v1.0
date: 2026-04
refs:
  - 01_business/05_payment_architecture.md
---
## 1. Phase 개요
```

> [!WARNING]
> Markdown 파서가 파일명과 버전 정보를 본문 섹션으로 인식하여,
> 자동화 도구(목차 생성기, Agent 섹션 파싱 등)에서 오작동 가능.

### 4-2. Phase 문서 필수 섹션 `목표` / `주요 작업` 누락 (10개 파일)

| Phase 문서 | `목표` | `주요 작업` |
|-----------|-------|-----------|
| `01_phase01_infra.md` | ❌ | ❌ |
| `02_phase02_comm.md` | ❌ | ❌ |
| `03_phase03_txn.md` | ❌ | ❌ |
| `04_phase04_account.md` | ❌ | ❌ |
| `06_phase06_violation.md` | ❌ | ❌ |
| `07_phase07_monitoring.md` | ❌ | ❌ |
| `08_phase08_bigdata.md` | ❌ | ❌ |
| `09_phase09_ai.md` | ❌ | ❌ |
| `10_phase10_analytics.md` | ❌ | ❌ |
| `11_phase11_compliance.md` | ❌ | ❌ |

### 4-3. 빈 섹션 수동 확인 필요

자동 스캔에서 탐지되었으나, 실제 내용이 있을 수 있어 수동 확인 권고:

- `docs/05_governance/01_decision_gates.md` — `## 2. G-HARD 점수 정의` (L:21)
- `docs/05_governance/03_reporting_cycle.md` — `## 2. 보고 주기 및 일정` (L:29)
- `docs/06_phases/00_phase_overview.md` — `## 3. 각 Phase 한 줄 요약` (L:85)

---

## 차원 5: 콘텐츠 상호 일관성 🔴 HIGH

### 5-1. 미납 Tier 기간 정의 충돌 ⚠️ 심각

3개 문서에서 Tier 전이 기간 기준이 상이하게 정의되어 있음.

| Tier 전이 | `05_payment_architecture.md` | `06_phase06_violation.md` |
|---------|------------------------------|--------------------------|
| Tier 1 지속 기간 | "0~24h" | "D+1 ~ D+7 (7일)" |
| Tier 1 → 2 전이 | "24h 경과" | "7일 경과 후" |
| Tier 2 지속 기간 | "24h~30d" | "D+8 ~ D+30 (23일)" |
| Tier 2 → 3 전이 | "30일 경과" | `tier_updated_at + 23 days` |
| Tier 3 지속 기간 | "30d~**120d** (90일)" | "D+31 ~ D+**90** (60일)" |
| Tier 3 → 4 전이 | "**120일** 경과" | `tier_updated_at + **60** days` |
| Write-off 조건 | "120d+" | "D+91 진입 후 **6개월** 경과" |

> [!CAUTION]
> **이는 단순 표기 차이가 아님.** Tier 3 지속 기간이 한 문서는 90일, 다른 문서는 60일로 **실제 30일 차이**가 존재.
> 구현 Agent가 어느 문서를 기준으로 삼느냐에 따라 JPJ 도로세 차단 및 법적 절차 개시 시점이 달라짐.
>
> **즉시 정합성 확인 및 하나의 문서를 Single Source of Truth로 지정 권고.**

### 5-2. Tier 2 전이 기산점 혼동

`05_payment_architecture.md:91`에 "Tier 2: Tier 1 상태에서 30일 경과"로 정의되어 있으나,  
동일 문서 내 표(L475-478)에 "Tier 1: 0~24h, Tier 2: 24h~30d"로 기재되어 있어 내부 모순 존재.

**권고**: `docs/01_business/05_payment_architecture.md`의 L475-478 표를 공식 SSoT로 확정 후,  
`Phase 06` 문서의 SQL 쿼리 조건(`tier_updated_at + X days`)을 이에 맞게 동기화.
