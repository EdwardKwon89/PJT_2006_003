# 21개 Skills 파일 인덱스
## 04_dev/04_skills_index.md
## v1.0 | 2026-04 | 참조: 04_dev/03_agent_roles.md, .planning/ROADMAP.md

---

> **Agent 사용 지침**
> 새로운 도메인 지식이 필요할 때 이 인덱스에서 적합한 Skill 파일을 탐색.
> Skills 파일 추가 시 이 인덱스 반드시 업데이트.
> 각 Skill 로드 전 `use_when` 조건을 확인하여 적합성 검토.

---

## 1. Executive Summary

Skills 파일은 Malaysia SLFF/MLFF Tolling BOS 운영에 필요한 **도메인 지식과 절차를 Agent가 즉시 실행 가능한 형태로 정리한 지식 베이스**다.

```
목적:   Agent가 반복 학습 없이 도메인 지식을 즉시 활용
범위:   21개 Skills (도메인 · 연동 · 데이터 · AI · 운영)
위치:   docs/07_skills/{skill-name}/SKILL.md
형식:   YAML 프론트매터 + Markdown 본문
```

---

## 2. Skills 파일 표준 포맷

```yaml
---
name: skill-name
description: 한 줄 설명 (영어)
use_when:
  - 이 Skill을 로드해야 하는 상황 1
  - 이 Skill을 로드해야 하는 상황 2
  - 이 Skill을 로드해야 하는 상황 3
dont_use_when:
  - 이 Skill이 불필요한 상황 1
  - 이 Skill이 불필요한 상황 2
---

# {제목}

## 1. 개요
...

## 2. 핵심 내용
...

## 3. 예시 시나리오
...

## 4. 주의사항 & 함정
...

## 5. 관련 Skills & 참조 문서
...
```

---

## 3. 21개 Skills 전체 인덱스

| # | 파일 경로 | 제목 | 주요 사용 Agent | 관련 Phase | 한 줄 설명 |
|---|-----------|------|----------------|-----------|-----------|
| 1 | [malaysia-tolling-domain](../07_skills/malaysia-tolling-domain/SKILL.md) | 말레이시아 톨링 도메인 | CEO, PM, CIO | 전체 | SLFF/MLFF 구조, 콘세셔네어 체계, JPJ 규제, Channel A/B |
| 2 | [traditional-tolling-roles](../07_skills/traditional-tolling-roles/SKILL.md) | 전통 톨링 운영 역할 | PM, Compliance | Phase 1, 7 | 플라자 관리자·현장 기술자·슈퍼바이저 역할과 권한 |
| 3 | [rfid-anpr-interface](../07_skills/rfid-anpr-interface/SKILL.md) | RFID/ANPR 인터페이스 | txn-lead, devops-lead | Phase 2, 3 | gRPC 이벤트 수신, 신뢰도 점수, Kafka raw.* 패턴 |
| 4 | [mlff-session-matching](../07_skills/mlff-session-matching/SKILL.md) | MLFF Entry-Exit 매칭 | txn-lead, txn-dev | Phase 3 | 진입·진출 페어링, Redis TTL, 타임아웃·수동 심사 |
| 5 | [clearing-center-operations](../07_skills/clearing-center-operations/SKILL.md) | 정산 센터 운영 | billing-lead, CFO | Phase 5 | Clearing Center 역할, 일별·월별 대사, JVC 수수료 |
| 6 | [payment-failure-scenarios](../07_skills/payment-failure-scenarios/SKILL.md) | 결제 실패 시나리오 | unpaid-lead, violation-lead | Phase 6 | Tier 1~4 미납 처리, JPJ 도로세 차단, Write-off 기준 |
| 7 | [jpj-integration](../07_skills/jpj-integration/SKILL.md) | JPJ 연동 | account-lead, api-lead | Phase 4 | 차량 등록 조회, 도로세 차단 API, RM 0.10/조회 비용 |
| 8 | [tng-payment](../07_skills/tng-payment/SKILL.md) | TnG 결제 연동 | billing-lead, api-lead | Phase 5 | Channel B 배치 정산, TnG API 인증, Reconciliation |
| 9 | [external-api-mcp](../07_skills/external-api-mcp/SKILL.md) | 외부 API & MCP 설계 | api-lead, devops-lead | Phase 11 | External REST API(TOC용), MCP 15개 Tool 활용 패턴 |
| 10 | [data-architecture-standards](../07_skills/data-architecture-standards/SKILL.md) | 데이터 아키텍처 표준 | CIO, reporting-lead | Phase 8 | 5단계 집계, Bronze/Silver/Gold, Delta Lake, Airflow |
| 11 | [metadata-management](../07_skills/metadata-management/SKILL.md) | 메타데이터 관리 | CIO, Compliance | 전체 | 300+ 용어 사전(KO/EN/BM), 코드 값 표준, 데이터 소유자 |
| 12 | [rbac-data-boundary](../07_skills/rbac-data-boundary/SKILL.md) | RBAC & 데이터 경계 | CIO, Compliance | Phase 1, 4 | 30개 역할, PostgreSQL RLS, 콘세셔네어 격리, 감사 로그 |
| 13 | [aggregation-units](../07_skills/aggregation-units/SKILL.md) | 집계 단위 설계 | reporting-lead, CIO | Phase 8 | 시간별·일별·월별 집계, 파티셔닝, 집계 테이블 DDL |
| 14 | [text-to-sql-engine](../07_skills/text-to-sql-engine/SKILL.md) | Text-to-SQL 엔진 | reporting-lead, AI Lead | Phase 9 | Claude Sonnet 프롬프트, 스키마 주입, SELECT 전용, SLA <10초 |
| 15 | [ai-fault-detection](../07_skills/ai-fault-detection/SKILL.md) | AI 장애 탐지 | devops-lead, CTO | Phase 7, 9 | Prometheus 메트릭, Error Rate 임계값, 자동 복구 3단계 |
| 16 | [rpa-workflows](../07_skills/rpa-workflows/SKILL.md) | RPA 워크플로우 | PM, reporting-lead | Phase 8, 9 | 반복 업무 자동화, Airflow DAG, 수동 심사 큐 처리 |
| 17 | [ai-decision-policy](../07_skills/ai-decision-policy/SKILL.md) | AI 의사결정 정책 | Compliance, exemption-lead | Phase 9 | Human-in-the-loop, 이의신청 권고, 면제 승인 기준 |
| 18 | [simulation-design](../07_skills/simulation-design/SKILL.md) | 시뮬레이션 설계 | CFO, reporting-lead | Phase 8 | 요금 시뮬레이션 모델, 수익 예측 알고리즘, 교통 패턴 |
| 19 | [bigdata-service-framework](../07_skills/bigdata-service-framework/SKILL.md) | 빅데이터 서비스 프레임워크 | reporting-lead, devops-lead | Phase 8 | Spark 작업 패턴, Airflow DAG 설계, Delta Lake 읽기·쓰기 |
| 20 | [code-quality-standards](../07_skills/code-quality-standards/SKILL.md) | 코드 품질 표준 | CTO, devops-lead | Phase 1~12 | Java 21 체크스타일, ESLint, SonarQube, 커버리지 80%+ |
| 21 | [change-management](../07_skills/change-management/SKILL.md) | 변경 관리 | PM, Compliance | Phase 1~12 | G-HARD 게이트, Board 결정 추적, API Breaking Change 정책 |

---

## 4. 도메인별 그룹핑

### 4.1 톨링 도메인 (6개)

말레이시아 SLFF/MLFF 톨링 시스템의 비즈니스 도메인 지식.

| Skill | 핵심 내용 | 선수 지식 |
|-------|----------|----------|
| malaysia-tolling-domain | 시장·규제·구조 전반 | 없음 |
| traditional-tolling-roles | 운영 인력 역할 | malaysia-tolling-domain |
| rfid-anpr-interface | 이벤트 수신 기술 | malaysia-tolling-domain |
| mlff-session-matching | MLFF 페어링 알고리즘 | rfid-anpr-interface |
| clearing-center-operations | 정산 운영 절차 | malaysia-tolling-domain |
| payment-failure-scenarios | 미납·위반 처리 흐름 | clearing-center-operations |

### 4.2 외부 연동 (3개)

외부 기관 및 결제 시스템 연동.

| Skill | 연동 대상 | 담당 서비스 |
|-------|----------|-----------|
| jpj-integration | JPJ (차량 등록) | account-service |
| tng-payment | TnG (Channel B) | billing-service |
| external-api-mcp | TOC, Paperclip | api-service |

### 4.3 데이터 & 보안 (3개)

데이터 거버넌스 및 접근 제어.

| Skill | 핵심 내용 | PDPA 관련 |
|-------|----------|----------|
| data-architecture-standards | 5단계 집계, Delta Lake | - |
| metadata-management | 300+ 용어, 코드 값 표준 | 데이터 민감도 분류 |
| rbac-data-boundary | 30개 역할, RLS, 감사 | 접근 제어 감사 |

### 4.4 AI & 분석 (6개)

AI 기능 설계 및 빅데이터 분석.

| Skill | AI 모델 | Phase |
|-------|---------|-------|
| text-to-sql-engine | Claude Sonnet | Phase 9 |
| ai-fault-detection | Prometheus + AI | Phase 7, 9 |
| ai-decision-policy | Claude Sonnet | Phase 9 |
| rpa-workflows | Airflow + Agent | Phase 8, 9 |
| simulation-design | 통계 모델 | Phase 8 |
| bigdata-service-framework | Spark + Delta Lake | Phase 8 |

### 4.5 운영 & 품질 (3개)

개발 표준 및 변경 관리.

| Skill | 적용 범위 | 주요 도구 |
|-------|----------|----------|
| code-quality-standards | 전 Phase | SonarQube, CheckStyle, ESLint |
| change-management | 전 Phase | G-HARD 게이트, BD-XX 추적 |
| aggregation-units | Phase 8+ | PostgreSQL 파티셔닝, DDL |

---

## 5. Skills × Agent 매핑

| Skill | CEO | CTO | CFO | CIO | PM | Compliance | txn | account | billing | violation | unpaid | equipment | reporting | api | devops |
|-------|:---:|:---:|:---:|:---:|:--:|:----------:|:---:|:-------:|:-------:|:---------:|:------:|:---------:|:---------:|:---:|:------:|
| malaysia-tolling-domain | ✓ | | | ✓ | ✓ | ✓ | | | | | | | | | |
| traditional-tolling-roles | | | | | ✓ | ✓ | | | | ✓ | | | | | |
| rfid-anpr-interface | | ✓ | | | | | ✓ | | | | | ✓ | | | ✓ |
| mlff-session-matching | | ✓ | | | | | ✓ | | | | | | | | |
| clearing-center-operations | | | ✓ | | | | | | ✓ | | | | | | |
| payment-failure-scenarios | | | | | | ✓ | | | | ✓ | ✓ | | | | |
| jpj-integration | | | | | | | | ✓ | | | | | | ✓ | |
| tng-payment | | | ✓ | | | | | | ✓ | | | | | ✓ | |
| external-api-mcp | | ✓ | | | | | | | | | | | | ✓ | ✓ |
| data-architecture-standards | | | | ✓ | | | | | | | | | ✓ | | |
| metadata-management | | | | ✓ | | ✓ | | | | | | | | | |
| rbac-data-boundary | | ✓ | | ✓ | | ✓ | | | | | | | | | |
| aggregation-units | | | | ✓ | | | | | | | | | ✓ | | |
| text-to-sql-engine | | ✓ | | | | | | | | | | | ✓ | | |
| ai-fault-detection | | ✓ | | | | | | | | | | | | | ✓ |
| rpa-workflows | | | | | ✓ | | | | | | | | ✓ | | |
| ai-decision-policy | | | | | | ✓ | | | | | | | | | |
| simulation-design | | | ✓ | | | | | | | | | | ✓ | | |
| bigdata-service-framework | | ✓ | | | | | | | | | | | ✓ | | ✓ |
| code-quality-standards | | ✓ | | | | | | | | | | | | | ✓ |
| change-management | ✓ | | | | ✓ | ✓ | | | | | | | | | |

---

## 6. Skills × Phase 매핑

| Skill | P1 | P2 | P3 | P4 | P5 | P6 | P7 | P8 | P9 | P10 | P11 | P12 |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:---:|:---:|:---:|
| malaysia-tolling-domain | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| traditional-tolling-roles | ✓ | | | | | | ✓ | | | | | ✓ |
| rfid-anpr-interface | | ✓ | ✓ | | | | | | | | | |
| mlff-session-matching | | | ✓ | | | | | | | | | |
| clearing-center-operations | | | | | ✓ | | | | | | | |
| payment-failure-scenarios | | | | | | ✓ | | | | | | |
| jpj-integration | | | | ✓ | | ✓ | | | | | | |
| tng-payment | | | | | ✓ | | | | | | | |
| external-api-mcp | | | | | | | | | | | ✓ | |
| data-architecture-standards | ✓ | | | | | | | ✓ | | | | |
| metadata-management | ✓ | | | | | | | ✓ | | | | |
| rbac-data-boundary | ✓ | | | ✓ | | | | | | | | |
| aggregation-units | | | | | | | | ✓ | | | | |
| text-to-sql-engine | | | | | | | | | ✓ | ✓ | | |
| ai-fault-detection | | | | | | | ✓ | | ✓ | | | |
| rpa-workflows | | | | | | | | ✓ | ✓ | | | |
| ai-decision-policy | | | | | | | | | ✓ | | | |
| simulation-design | | | | | | | | ✓ | | | | |
| bigdata-service-framework | | | | | | | | ✓ | | | | |
| code-quality-standards | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| change-management | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

---

## 7. Skills 사용 가이드

### 7.1 Skill 로드 방법

```
# Claude Code에서 Skill 로드
/load docs/07_skills/malaysia-tolling-domain/SKILL.md

# 또는 Agent 프롬프트에 경로 명시
"docs/07_skills/rfid-anpr-interface/SKILL.md 를 로드하고 ..."
```

### 7.2 적합한 Skill 탐색 순서

```
1. 이 인덱스에서 관련 Skill 검색 (섹션 3 표)
2. use_when 조건 확인
3. 선수 지식(섹션 4) 확인 → 필요 시 선수 Skill 먼저 로드
4. dont_use_when 조건 확인 → 부적합 시 다른 Skill 탐색
```

### 7.3 Skill 업데이트 절차

```
1. 해당 SKILL.md 수정
2. 이 인덱스(04_skills_index.md) 업데이트
3. 영향받는 Agent에게 변경 공지
4. git commit: chore(skills): update {skill-name}
```

### 7.4 신규 Skill 추가 절차

```
1. docs/07_skills/{new-skill-name}/ 디렉토리 생성
2. SKILL.md 작성 (표준 포맷 준수)
3. 이 인덱스에 행 추가 (섹션 3, 4, 5, 6 모두 업데이트)
4. 관련 Agent 역할 카드(03_agent_roles.md) 업데이트
5. PM 승인 후 merge
```

---

## 8. 참조 문서

| 문서 | 내용 |
|------|------|
| [03_agent_roles.md](./03_agent_roles.md) | 각 Agent의 주요 Skills 목록 |
| [02_paperclip_org.md](./02_paperclip_org.md) | Agent × Skills 매핑 |
| [../07_skills/](../07_skills/) | Skills 파일 실제 위치 |
| [../.planning/ROADMAP.md](../.planning/ROADMAP.md) | Phase 6 Skills 생성 계획 |
| [../03_data/04_metadata_glossary.md](../03_data/04_metadata_glossary.md) | 용어 표준 (Skills 작성 기준) |

---

*작성일: 2026-04*
*버전: v1.0*
*담당 Agent: Knowledge Architect (총괄), PM Agent*
