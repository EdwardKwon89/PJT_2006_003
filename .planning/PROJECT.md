# Malaysia BOS Documentation

## What This Is

AI Agent 기반 멀티-에이전트 병렬 실행으로 Malaysia SLFF/MLFF Tolling BOS 프로젝트의 전체 설계 문서 세트(46개 파일 + 21개 Skills 파일)를 자동 생성한다. GSD Phase 기반 개발 관리와 Paperclip 조직(29개 Agent)을 활용하여 docs/ 폴더 하위 7개 섹션별 병렬 생성을 수행한다.

## Core Value

**AI Agent 기반 멀티-에이전트 병렬 실행으로 46개 설계 문서를 자동 생성하되, 일관성과 완성도를 보장하는 것.** 기존 3개 확정 문서(00_MASTER.md, 01_project_charter.md, 04_supplement_items.md)와 실행 전략(multi-agent-doc-gen.md)을 기반으로 Wave별 순차 의존성을 유지하면서 파일 생성을 병렬화한다.

## Requirements

### Validated

(신규 프로젝트 — ship to validate)

### Active

- [ ] **DOC-01**: 00_MASTER.md 기반 마스터 구조 확정 및 Wave별 의존성 정의
- [ ] **DOC-02**: Wave 1 실행 — 00_MASTER.md 검증 및 건너뛰기 (기존 확정 문서)
- [ ] **DOC-03**: Wave 2 실행 — 01_business/ 폴더 5개 파일 병렬 생성
- [ ] **DOC-04**: Wave 3A 실행 — 03_data/ 폴더 5개 파일 병렬 생성
- [ ] **DOC-05**: Wave 3B 실행 — 05_governance/ 폴더 4개 파일 병렬 생성
- [ ] **DOC-06**: Wave 4 실행 — 02_system/ 폴더 6개 파일 병렬 생성
- [ ] **DOC-07**: Wave 5 실행 — 04_dev/ 폴더 6개 파일 병렬 생성
- [ ] **DOC-08**: Wave 6 실행 — 06_phases/ 폴더 13개 파일 병렬 생성 (2~3 라운드 분할)
- [ ] **DOC-09**: Wave 7 실행 — 07_skills/ 폴더 21개 SKILL.md 병렬 생성 (3~4 라운드 분할)
- [ ] **DOC-10**: 파일 생성 후 자동 저장 및 git commit (Wave별 atomic commit)
- [ ] **DOC-11**: 46개 파일 완성도 검증 (구조, 링크, 내용 일관성)
- [ ] **DOC-12**: Markdown 문서 최적화 (TOC 생성, 백링크 확인, 포맷 통일)

### Out of Scope

- 각 파일의 실제 내용 검증 (의미론적 정확성) — Compliance Agent 책임
- 파일 번역 (KO→EN/BM) — 별도 localization 프로젝트
- Paperclip 29개 Agent 실제 구현 및 운영 — 추후 Phase 12 이후 과제
- 외부 시스템(JPJ, TnG, FPX) 실제 API 연동 테스트 — Mock 서버 기반만 문서화
- 대규모 데이터 마이그레이션 시뮬레이션 — 설계 문서만 제공

## Context

### 기초 문서 (확정)

- **00_MASTER.md** — 전체 프로젝트 마스터 구조, 핵심 도메인(10개), 결제 구조, Paperclip 조직(29개 Agent)
- **01_project_charter.md** — 프로젝트 목적, JVC 사업 모델, MVP 범위(Phase 1~6), 성공 기준
- **04_supplement_items.md** — 18개 보충항목 (Agent 담당 배정 & 처리 계획), G-HARD 0~7 의사결정 게이트
- **multi-agent-doc-gen.md** — 46개 파일을 7개 Wave로 나누어 병렬 생성하는 실행 전략

### 기술 환경

- **개발 프레임워크**: GSD (Goal-driven Software Development) — Phase 기반 관리
- **Agent 조직화**: Paperclip (29개 AI Agent) — 조직, 보고, 심사 체계
- **IDE 환경**: VS Code + Claude Code + cmux (멀티 터미널)
- **문서 포맷**: Markdown (GitHub Flavored) + 참조 링크 + 코드 블록
- **버전 관리**: Git (Wave별 atomic commit)

### 기존 경험 & 제약

- **MLFF_BOS 프로젝트** — 이전 세션에서 유사한 Agent 기반 설계 문서 작업 경험
- **Multi-Agent 병렬 실행** — Paperclip/GSD를 통한 Wave별 순차 + 파일 병렬 실행
- **의존성 관리** — Wave 간 순차 의존성 (Wave 2 → Wave 3A/3B → Wave 4 → Wave 5 → Wave 6 → Wave 7)
- **Agent 능력 제약** — 각 Agent는 지정된 파일 세트만 담당, 교차 검증은 PM/QA Agent가 담당

## Constraints

- **Timeline**: 현재 시점부터 진행 가능 (마감 기한 미지정 — 가능한 빠른 완성 목표)
- **기술 스택**: Markdown 문서 생성만 포함 (실제 코드 구현 제외)
- **Agent 가용성**: Paperclip 29개 Agent 전부 활용 가능 (LLM API 비용: ~$720/월)
- **문서 범위**: 46개 파일 + 21개 Skills = 67개 파일 (이외 추가 파일 제외)
- **콘텐츠 품질**: 각 파일은 self-contained이어야 함 (Agent가 즉시 실행 가능한 수준)

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| 7개 Wave 병렬 실행 (순차 의존성 유지) | 파일 간 참조 관계를 고려하면서 최대한 병렬화 필요 | — Pending |
| 각 파일을 별도 Sub-Agent가 담당 | 46개 파일을 균등하게 분산 & 병렬 처리 효율화 | — Pending |
| Markdown 포맷 + GitHub Flavored 문법 | 읽기 용이 & 코드 블록/표/링크 지원 | — Pending |
| Wave별 atomic commit | 추적 가능성 & 롤백 용이성 확보 | — Pending |
| Compliance Agent 최종 검증 | 의미론적 정확성 & 일관성 검증 책임 할당 | — Pending |

---

## Evolution

이 문서는 프로젝트 진행 단계별로 진화합니다.

**Wave별 완료 후:**
1. 완료한 Wave의 파일 수 & 상태 업데이트
2. 발견된 이슈 & 조정 사항 기록
3. 다음 Wave 의존성 확인
4. "What This Is" 섹션 필요 시 정제

**프로젝트 완료 후:**
1. 전체 46개 파일 최종 검증 결과 통합
2. 발견된 설계 부채 & 향후 과제 정리
3. Paperclip 29개 Agent 실제 구현을 위한 기초 문서 평가

---

*Last updated: 2026-04-01 after initialization*
