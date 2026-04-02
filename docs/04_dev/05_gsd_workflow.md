# GSD 워크플로우 & 명령어
## 04_dev/05_gsd_workflow.md
## v1.0 | 2026-04 | 참조: 04_dev/02_paperclip_org.md, 05_governance/03_reporting_cycle.md

> **Agent 사용 지침**
> 모든 Agent가 GSD 명령 실행 전 이 문서 참조.
> 명령어 오용 또는 Phase 순서 위반 시 PM Agent에 에스컬레이션.

---

## 목차

1. [Executive Summary — GSD 워크플로우 철학](#1-executive-summary--gsd-워크플로우-철학)
2. [핵심 GSD 명령어 레퍼런스](#2-핵심-gsd-명령어-레퍼런스)
3. [Phase 실행 표준 절차](#3-phase-실행-표준-절차)
4. [Heartbeat 워크플로우](#4-heartbeat-워크플로우)
5. [Agent 충돌 방지 프로토콜](#5-agent-충돌-방지-프로토콜)
6. [STATE.md 구조 설명](#6-statemd-구조-설명)
7. [시나리오별 명령어 예시](#7-시나리오별-명령어-예시)
8. [GSD 안티패턴](#8-gsd-안티패턴)
9. [참조 문서](#9-참조-문서)

---

## 1. Executive Summary — GSD 워크플로우 철학

### 1.1 GSD란 무엇인가

**GSD(Get Shit Done)**는 AI Agent 기반 멀티-에이전트 개발 환경에서 작업의 계획(Plan) → 실행(Execute) → 검증(Verify) → 보고(Report) 사이클을 표준화한 워크플로우 프레임워크다.

Malaysia SLFF/MLFF Tolling BOS 프로젝트에서는 Paperclip 29개 Agent가 GSD 명령어를 통해 상호 협업하며, G-HARD 0~7 게이트 기반 Phase 진행 승인과 Heartbeat 보고 체계를 결합하여 프로젝트를 운영한다.

### 1.2 핵심 원칙

| 원칙 | 설명 |
|------|------|
| **계획 우선 (Plan First)** | 실행 전 반드시 `/gsd:plan-phase` 완료 후 진행 |
| **단계 순서 준수 (Gate Control)** | G-HARD 게이트를 건너뛰는 Phase 진행 금지 |
| **상태 가시성 (State Visibility)** | `.planning/STATE.md` 항상 최신 상태 유지 |
| **병렬 안전성 (Parallel Safety)** | 동일 파일 동시 수정 방지; 충돌 전 `/gsd:pause-work` 선행 |
| **원자적 커밋 (Atomic Commit)** | Wave 단위 git commit (중간 커밋 금지) |

### 1.3 GSD와 기존 프로젝트 구조의 관계

```
.planning/
  ├── PROJECT.md       ← GSD new-project 산출물 (비전, 범위)
  ├── REQUIREMENTS.md  ← GSD 요구사항 정의
  ├── ROADMAP.md       ← Wave/Phase 실행 계획
  ├── STATE.md         ← GSD progress 실시간 상태
  └── config.json      ← 워크플로우 설정 (YOLO/Standard/Parallel)

docs/                  ← GSD execute-phase 산출물 (46개 파일)
  ├── 01_business/
  ├── 02_system/
  ├── 03_data/
  ├── 04_dev/
  ├── 05_governance/
  ├── 06_phases/
  └── 07_skills/
```

---

## 2. 핵심 GSD 명령어 레퍼런스

### 2.1 상태 조회 명령어

| 명령어 | 용도 | 사용 시점 |
|--------|------|-----------|
| `/gsd:progress` | 전체 프로젝트 진행률 조회 | 세션 시작 시, 현황 파악 필요 시 |
| `/gsd:health` | Agent/시스템 상태 점검 | 오류 발생 후, 재개 전 |
| `/gsd:check-todos` | 미완료 TODO 항목 조회 | Phase 실행 중 블로커 확인 |
| `/gsd:stats` | 작업 통계 (완료/진행/대기) | 주간 보고 준비 전 |

#### `/gsd:progress` 예시

```bash
/gsd:progress
# 출력 예시:
# Wave 1~4 완료 (20/46 files)
# 현재 Phase: 4 (Wave 5 — 04_dev/ 실행 중)
# 완료율: 43.5%
# G-HARD 현재 점수: 3 (Yellow — Steering Committee 검토 필요)
```

#### `/gsd:health` 예시

```bash
/gsd:health
# 출력 예시:
# Agent 상태: 29/29 Active
# Rate Limit: 정상 (다음 리셋: 17:00)
# STATE.md: 최신 (2026-04-02 09:15 업데이트)
# Git: 클린 (uncommitted 없음)
```

#### `/gsd:check-todos` 예시

```bash
/gsd:check-todos
# 출력 예시:
# [BLOCKED] 04_dev/01_environment_setup.md — DA Lead 응답 대기
# [IN_PROGRESS] 04_dev/02_paperclip_org.md — CTO Agent 작성 중
# [PENDING] 04_dev/03_cicd_pipeline.md — 의존성: 02 완료 후 진행
```

---

### 2.2 계획 수립 명령어

| 명령어 | 용도 | 사용 시점 |
|--------|------|-----------|
| `/gsd:plan-phase <N>` | Phase N의 상세 실행 계획 수립 | execute-phase 실행 전 반드시 선행 |
| `/gsd:discuss-phase <N>` | Phase N 계획 논의 및 가정 검토 | plan-phase 전 불명확한 사항 정리 |
| `/gsd:note <내용>` | 임시 메모 기록 (STATE.md에 저장) | 중요 사항 발생 즉시 |

#### `/gsd:plan-phase` 예시

```bash
/gsd:plan-phase 4
# 실행 내용:
# 1. Wave 5 (04_dev/ 6개 파일) 의존성 분석
# 2. 각 파일별 담당 Agent 배정
# 3. 병렬 실행 그룹 구성 (충돌 위험 파일 분리)
# 4. 성공 기준(Success Criteria) 정의
# 5. STATE.md Phase 4 섹션 업데이트
```

#### `/gsd:discuss-phase` 예시

```bash
/gsd:discuss-phase 4
# 예: "04_dev/02_paperclip_org.md와 04_dev/05_gsd_workflow.md가
#      상호 참조하는 경우 어떤 파일을 먼저 생성해야 하는가?"
# → PM Agent가 의존성 그래프 분석 후 실행 순서 결정
```

---

### 2.3 실행 명령어

| 명령어 | 용도 | 사용 시점 |
|--------|------|-----------|
| `/gsd:execute-phase <N>` | Phase N 실행 (파일 생성/코드 작성) | plan-phase 완료 후 |
| `/gsd:do <작업>` | 단일 작업 즉시 실행 | 소규모 긴급 작업 |
| `/gsd:quick <작업>` | 빠른 단일 태스크 (계획 생략) | 30분 이내 완료 가능한 작업 |
| `/gsd:next` | 다음 우선순위 작업 자동 선택 및 실행 | 현재 작업 완료 직후 |
| `/gsd:fast` | 계획 단계 최소화하고 빠른 실행 | 반복적이고 명확한 작업 |

#### `/gsd:execute-phase` 예시

```bash
/gsd:execute-phase 4 --wave 5
# 실행 내용 (병렬):
# Group A (동시): 01_environment_setup.md, 03_cicd_pipeline.md
# Group B (동시): 02_paperclip_org.md, 04_monitoring.md
# Group C (순차): 05_gsd_workflow.md (Group A/B 완료 후)
#                 06_deployment_guide.md (Group A/B 완료 후)
```

#### `/gsd:do` 예시

```bash
/gsd:do "04_dev/05_gsd_workflow.md 파일에 시나리오 7번 추가"
# 단일 작업 즉시 실행 (plan-phase 생략)
```

#### `/gsd:quick` 예시

```bash
/gsd:quick "03_reporting_cycle.md의 Heartbeat 일정 표 업데이트"
# 30분 이내 소작업 — 계획 오버헤드 없이 바로 실행
```

---

### 2.4 검증 & 보고 명령어

| 명령어 | 용도 | 사용 시점 |
|--------|------|-----------|
| `/gsd:verify-work <N>` | Phase N 완료 기준 충족 여부 검증 | execute-phase 완료 직후 |
| `/gsd:review <파일>` | 특정 파일/코드 품질 리뷰 | 중요 산출물 생성 후 |
| `/gsd:update` | STATE.md 및 진행 현황 업데이트 | 각 작업 완료 후 |

#### `/gsd:verify-work` 예시

```bash
/gsd:verify-work 4
# 검증 항목:
# ✅ 04_dev/ 6개 파일 모두 생성됨
# ✅ 파일 간 상호 참조 링크 유효
# ✅ 각 파일 200줄 이상 (최소 기준)
# ✅ GFM(GitHub Flavored Markdown) 형식 준수
# ⚠️ 04_dev/06_deployment_guide.md — 참조 링크 1개 누락 (수동 수정 필요)
```

#### `/gsd:review` 예시

```bash
/gsd:review docs/04_dev/05_gsd_workflow.md
# 리뷰 항목:
# - 내용 완성도 (요구사항 대비)
# - 참조 문서 정확성
# - 코드 블록 문법 오류
# - 표 형식 일관성
```

---

### 2.5 일시 중지 & 재개 명령어

| 명령어 | 용도 | 사용 시점 |
|--------|------|-----------|
| `/gsd:pause-work` | 현재 작업 안전하게 중지 | 충돌 감지, Rate Limit, 세션 종료 전 |
| `/gsd:resume-work` | 중지된 작업 재개 | 새 세션 시작 시, 문제 해결 후 |

#### `/gsd:pause-work` 예시

```bash
/gsd:pause-work
# 실행 내용:
# 1. 현재 진행 중인 파일 생성 상태 저장
# 2. STATE.md에 중단 지점 기록
# 3. uncommitted 변경사항 WIP 커밋
# 4. 다음 재개 지점 명시
```

#### `/gsd:resume-work` 예시

```bash
/gsd:resume-work
# 출력 예시:
# 마지막 중단 지점: 2026-04-02 14:30
# 진행 중이던 작업: 04_dev/05_gsd_workflow.md (섹션 7까지 완료)
# 다음 작업: 섹션 8 (GSD 안티패턴) 작성
# → 재개 여부 확인 후 실행
```

---

### 2.6 전체 명령어 요약표

| 카테고리 | 명령어 | 한 줄 설명 |
|----------|--------|-----------|
| **조회** | `/gsd:progress` | 전체 진행률 대시보드 |
| **조회** | `/gsd:health` | 시스템/Agent 상태 점검 |
| **조회** | `/gsd:check-todos` | 미완료 TODO 목록 |
| **조회** | `/gsd:stats` | 작업 통계 요약 |
| **계획** | `/gsd:plan-phase <N>` | Phase N 상세 계획 수립 |
| **계획** | `/gsd:discuss-phase <N>` | Phase N 논의 및 가정 검토 |
| **계획** | `/gsd:note <내용>` | 메모 기록 (STATE.md 저장) |
| **실행** | `/gsd:execute-phase <N>` | Phase N 전체 실행 |
| **실행** | `/gsd:do <작업>` | 단일 작업 즉시 실행 |
| **실행** | `/gsd:quick <작업>` | 빠른 소작업 실행 |
| **실행** | `/gsd:next` | 다음 우선순위 작업 자동 실행 |
| **실행** | `/gsd:fast` | 최소 계획으로 빠른 실행 |
| **검증** | `/gsd:verify-work <N>` | Phase N 완료 기준 검증 |
| **검증** | `/gsd:review <파일>` | 특정 파일 품질 리뷰 |
| **보고** | `/gsd:update` | STATE.md 진행 현황 업데이트 |
| **제어** | `/gsd:pause-work` | 현재 작업 안전하게 중지 |
| **제어** | `/gsd:resume-work` | 중지된 작업 재개 |

---

## 3. Phase 실행 표준 절차

### 3.1 전체 실행 흐름도

```
┌─────────────────────────────────────────────────────────────┐
│                   Phase 실행 표준 절차                       │
└─────────────────────────────────────────────────────────────┘

  ① /gsd:progress
     └─ 현재 상태 확인, 다음 Phase 식별
            │
            ▼
  ② /gsd:discuss-phase <N>                    [선택]
     └─ 불명확한 가정 정리, 의존성 확인
            │
            ▼
  ③ /gsd:plan-phase <N>                       [필수]
     └─ 파일 목록, 담당 Agent, 병렬 그룹, 성공 기준 정의
            │
            ▼
  ④ G-HARD Gate 확인                          [필수]
     ├─ Gate 0~2 (Green): 즉시 진행 가능
     ├─ Gate 3~5 (Yellow): Steering Committee 검토 대기
     └─ Gate 6~7 (Red): Board 심화 검토 후 재계획
            │ (Green 또는 승인 후)
            ▼
  ⑤ /gsd:execute-phase <N>                    [필수]
     └─ 병렬 그룹별 파일 생성/코드 작성
            │
            ▼
  ⑥ /gsd:verify-work <N>                      [필수]
     ├─ 성공 기준 충족 확인
     ├─ 파일 참조 링크 검증
     └─ 불합격 → ⑤ 재실행 (해당 파일만)
            │ (검증 통과)
            ▼
  ⑦ git commit (Wave 단위 원자적 커밋)        [필수]
     └─ 예: "docs(wave5): generate 6 dev environment files"
            │
            ▼
  ⑧ /gsd:update                               [필수]
     └─ STATE.md 완료 표시, 다음 Phase 준비
            │
            ▼
  ⑨ /gsd:next
     └─ 다음 Phase로 자동 이동
```

### 3.2 단계별 세부 지침

#### 단계 ③ plan-phase 체크리스트

```
/gsd:plan-phase 실행 후 반드시 확인:
□ 생성 파일 목록 (경로, 파일명, 예상 줄 수)
□ 각 파일별 담당 Agent 배정
□ 의존성 순서 (A 완료 후 B 시작 등)
□ 병렬 실행 그룹 구성 (Group A/B/C...)
□ 성공 기준 (Success Criteria) 명확화
□ 예상 소요 시간 (Rate Limit 고려)
```

#### 단계 ④ G-HARD 게이트 확인 방법

```bash
# G-HARD 현재 점수 확인
/gsd:health
# 또는 05_governance/01_decision_gates.md 참조

# 점수별 대응:
# 0-2점 (Green):  즉시 execute-phase 진행
# 3-5점 (Yellow): /gsd:note "Steering Committee 검토 요청"
#                 수요일 10:00 AM 주간 회의 대기
# 6-7점 (Red):    /gsd:pause-work 후 Board 심화 검토 에스컬레이션
```

#### 단계 ⑦ Wave 단위 커밋 형식

```bash
git commit -m "$(cat <<'EOF'
docs(wave<N>): <설명>

- 생성 파일 목록 (개수, 총 줄 수)
- 주요 내용 요약
EOF
)"

# 예시:
git commit -m "$(cat <<'EOF'
docs(wave5): generate 6 dev environment files (3,200 lines)

- 04_dev/01_environment_setup.md (480줄)
- 04_dev/02_paperclip_org.md (520줄)
- 04_dev/03_cicd_pipeline.md (510줄)
- 04_dev/04_monitoring.md (490줄)
- 04_dev/05_gsd_workflow.md (530줄)
- 04_dev/06_deployment_guide.md (470줄)
EOF
)"
```

---

## 4. Heartbeat 워크플로우

### 4.1 4층 보고 체계 개요

Malaysia BOS 프로젝트의 보고 체계는 `05_governance/03_reporting_cycle.md`에 정의된 4단계 구조를 따른다. GSD 명령어는 각 보고 레벨에서 아래와 같이 활용된다.

```
Level 1: Daily Standup (09:30)
Level 2: Weekly Digest (금요일 17:00)
Level 3: Bi-weekly Heartbeat (격주 월요일 09:00)
Level 4: Monthly Steering (매월 첫째 주 목요일 14:00)
```

### 4.2 일별 체크인 (Daily Standup)

**시간:** 매 영업일 09:30 AM  
**참석:** 개발팀 Agent (CTO, Tech Lead, PM, DA Lead, QA)  
**소요:** 15분

#### Daily 워크플로우

```
09:15 — 각 Agent: /gsd:check-todos (자체 블로커 확인)
          │
          ▼
09:25 — 각 Agent: /gsd:update (당일 계획 STATE.md 반영)
          │
          ▼
09:30 — PM Agent: /gsd:progress (전체 진행률 취합)
          │
          ▼
09:35 — Standup 진행 (Agent별 3분 이내 보고)
        ┌─ 어제 완료한 작업
        ├─ 오늘 할 작업
        └─ 블로커 (있으면 /gsd:note 기록)
          │
          ▼
09:45 — PM Agent: CEO에 1~2줄 요약 전달
```

#### Daily 보고 템플릿

```markdown
## Daily Standup — {날짜}

### 진행 현황
- 완료: {어제 완료 파일/작업 수}
- 진행 중: {현재 작업 중인 파일/작업}
- 대기: {블로킹된 항목}

### 블로커
- {블로커 내용} → 담당: {Agent명}

### 오늘 목표
- {목표 1}
- {목표 2}
```

### 4.3 주별 Gate 심사 (Weekly Review)

**시간:** 매주 수요일 10:00 AM (Steering Committee 회의)  
**참석:** CEO, CTO, CPO, CIO, PM, Compliance  
**소요:** 45분

#### Weekly 워크플로우

```
수요일 09:00 — PM Agent: /gsd:stats (주간 통계 생성)
                │
                ▼
수요일 09:15 — DA Lead: /gsd:review (주요 산출물 품질 리뷰)
                │
                ▼
수요일 09:30 — Compliance Agent: G-HARD 점수 갱신
              ┌─ 05_governance/01_decision_gates.md 참조
              └─ 각 항목(G/H/A/R/D) 재평가 후 총점 산출
                │
                ▼
수요일 10:00 — Steering Committee 회의 시작
              ┌─ /gsd:progress (전체 현황 공유)
              ├─ G-HARD 점수 발표 및 Gate 결정
              ├─ 위험 요소 및 의사결정 사항
              └─ 다음 주 Phase 계획 확인
                │
                ▼
수요일 11:00 — PM Agent: /gsd:update (결정 사항 STATE.md 반영)
                          /gsd:note "Steering 결정: {내용}"
```

#### G-HARD 점수 갱신 절차

```bash
# 1. 현재 점수 조회
/gsd:health

# 2. 각 항목 재평가
# G (Governance): 조직도, RACI, 보고 체계 완성도
# H (Headcount): Agent 가용률, Rate Limit 상태
# A (Architecture): 설계 문서 완성도, PoC 검증 여부
# R (Risk): 블로커 수, 일정 지연율
# D (Dependency): 외부 의존성(JPJ, TnG, FPX) 준비 상태

# 3. 점수 기록
/gsd:note "G-HARD 갱신: G=0, H=1, A=1, R=0, D=1 → 총점 3 (Yellow)"
```

### 4.4 격주 임원진 보고 (CEO Heartbeat)

**시간:** 격주 월요일 09:00 AM  
**참석:** CEO  
**소요:** 30~45분

#### Heartbeat 보고 내용

```bash
# PM Agent가 Heartbeat 보고서 생성
/gsd:stats
/gsd:progress

# 보고 항목:
# 1. 완료 Wave 수 (현재/목표)
# 2. 생성 파일 수 (현재/46)
# 3. 전체 진행률 (%)
# 4. 주요 위험 요소 (Top 3)
# 5. 의사결정 필요 사항
# 6. 다음 2주 계획
```

#### Heartbeat 보고 형식

```markdown
## CEO Heartbeat — {날짜}

### 프로젝트 현황 (신호등)
🟢 일정: 정상 진행 중
🟡 예산: 소폭 초과 (5% 이내)
🔴 의존성: JPJ API 연동 지연

### 핵심 지표
| 항목 | 목표 | 현재 | 상태 |
|------|------|------|------|
| 완료 파일 | 46 | 20 | 43.5% |
| Wave 완료 | 7 | 4 | 57.1% |
| G-HARD 점수 | ≤3 | 3 | Yellow |

### 의사결정 요청
1. {결정 사항 1} — 기한: {날짜}
2. {결정 사항 2} — 기한: {날짜}

### 다음 2주 계획
- Wave 5 (04_dev/ 6개 파일) 완료 목표
- Wave 6 착수 (06_phases/ 13개 파일)
```

---

## 5. Agent 충돌 방지 프로토콜

### 5.1 충돌 발생 원인

| 원인 | 설명 | 빈도 |
|------|------|------|
| **동일 파일 동시 수정** | 두 Agent가 같은 파일을 동시에 편집 | 높음 |
| **STATE.md 동시 업데이트** | 여러 Agent가 동시에 STATE.md 갱신 | 중간 |
| **참조 파일 미완성** | A 파일이 미완성인 B 파일을 참조 | 중간 |
| **Rate Limit 충돌** | Agent가 API 한도 초과 중 다른 Agent 시작 | 낮음 |

### 5.2 파일 잠금 프로토콜

```
충돌 방지 절차:

1. execute-phase 시작 전
   └─ PM Agent: 작업 파일 목록 공개 (어떤 Agent가 어떤 파일 담당)

2. 작업 시작 시
   └─ 각 Agent: /gsd:note "{Agent명} {파일경로} 작업 시작"
      예: /gsd:note "CTO Agent: docs/04_dev/02_paperclip_org.md 작업 시작"

3. 작업 완료 시
   └─ 각 Agent: /gsd:note "{Agent명} {파일경로} 작업 완료"
      예: /gsd:note "CTO Agent: docs/04_dev/02_paperclip_org.md 작업 완료"

4. 충돌 감지 시 (다른 Agent가 같은 파일 작업 중임을 확인)
   └─ 나중에 시작한 Agent: /gsd:pause-work → PM Agent에 에스컬레이션
```

### 5.3 `/gsd:pause-work` 사용 시점

다음 상황에서 반드시 `/gsd:pause-work` 먼저 실행:

```
✅ pause-work 필수 상황:
□ 다른 Agent가 동일 파일 작업 중임을 확인했을 때
□ Rate Limit 초과 경고 발생 시
□ G-HARD 점수가 6~7점 (Red)으로 상승했을 때
□ 세션 종료 전 (uncommitted 변경사항 있을 때)
□ 블로커로 인해 30분 이상 진행 불가 시
□ PM Agent로부터 중지 요청을 받았을 때
□ 예상치 못한 오류로 파일이 손상되었을 때

❌ pause-work 불필요한 상황:
□ 정상적인 Phase 완료 후 → /gsd:update 사용
□ 단순 휴식 (세션 종료 없음)
□ 다음 명령어 입력 전 잠시 대기
```

### 5.4 동일 파일 동시 수정 방지 규칙

#### 병렬 실행 그룹 구성 원칙

```
규칙 1: 같은 폴더 내 파일은 상호 의존성 확인 후 그룹 분리
규칙 2: 참조 관계가 있는 파일은 다른 그룹에 배치
규칙 3: STATE.md는 한 번에 하나의 Agent만 수정 (Lock 방식)
규칙 4: 00_MASTER.md는 읽기 전용 (수정 금지)

올바른 병렬 그룹 예시 (Wave 5):
┌─ Group A (동시 실행) ─────────────────┐
│  01_environment_setup.md (Tech Lead)  │
│  03_cicd_pipeline.md (DevOps Agent)   │
└───────────────────────────────────────┘
           ↓ (A 완료 후)
┌─ Group B (동시 실행) ─────────────────┐
│  02_paperclip_org.md (CTO)            │
│  04_monitoring.md (CIO)               │
└───────────────────────────────────────┘
           ↓ (B 완료 후)
┌─ Group C (순차 실행) ─────────────────┐
│  05_gsd_workflow.md (PM)              │
│  06_deployment_guide.md (DevOps)      │
└───────────────────────────────────────┘
```

### 5.5 재개 절차 (`/gsd:resume-work`)

```bash
# 새 세션 시작 시 반드시 실행
/gsd:resume-work

# 자동으로 수행:
# 1. .planning/STATE.md 로드 (마지막 중단 지점 확인)
# 2. uncommitted 변경사항 확인
# 3. 진행 중이던 파일 목록 복원
# 4. 다음 실행 명령어 제안

# 출력 예시:
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 재개 지점: 2026-04-02 14:30 (CTO Agent)
# 완료된 파일: 04_dev/01_environment_setup.md ✅
# 진행 중: 04_dev/02_paperclip_org.md (50% 완료)
# 다음 실행: /gsd:execute-phase 4 --resume 02_paperclip_org.md
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 6. STATE.md 구조 설명

### 6.1 파일 위치 및 역할

| 속성 | 내용 |
|------|------|
| **파일 경로** | `.planning/STATE.md` |
| **갱신 주체** | PM Agent (주), 각 Agent (부) |
| **갱신 빈도** | 각 작업 완료 후, 세션 종료 전 |
| **잠금 정책** | 동시 수정 금지; `/gsd:update` 명령으로만 수정 |
| **git 추적** | 활성화 (Wave별 커밋에 포함) |

### 6.2 STATE.md 섹션 구조

```markdown
# State: Malaysia BOS Documentation

**Updated:** {날짜}
**Phase:** {현재 Phase 번호} (Wave {N} — {설명})
**Progress:** Wave {X}~{Y} 완료 ({완료 파일 수}/46 files)

---

## Project Reference
# PROJECT.md 핵심 내용 요약 (변경 없음)

---

## Current Status

### ✅ Completed
# 완료된 Wave/파일 목록 (체크박스 형식)

### ⏳ Pending
# 진행 예정 Wave/파일 목록

---

## Next Actions

### 즉시 (Next Cycle)
# 다음 실행할 GSD 명령어 (Action 1, 2, 3...)

### 진행 중 (During Waves X~Y)
# 반복 작업 지침

### 최종 (After Wave 7)
# 완료 기준 및 배포 계획

---

## Key Metrics
# 주요 지표 표 (목표/현재/상태)

---

## Configuration
# 워크플로우 설정 (config.json 미러링)

---

## Session Continuity

### Last Session Summary
# 마지막 세션 완료 사항

### Continue From Here
# 다음 세션 재개 명령어

---

## Logs
# 날짜별 작업 로그 (최신순)
```

### 6.3 STATE.md 업데이트 규칙

```bash
# 올바른 업데이트 방법 (항상 /gsd:update 사용)
/gsd:update

# 업데이트 시 반드시 포함할 내용:
# 1. Updated 날짜 갱신
# 2. Phase 번호 및 설명 갱신
# 3. Progress 파일 수 갱신
# 4. ✅ Completed 항목 추가
# 5. ⏳ Pending 항목에서 완료 항목 제거
# 6. Next Actions 갱신
# 7. Key Metrics 수치 갱신
# 8. Logs에 작업 기록 추가
```

### 6.4 STATE.md와 GSD 명령어 연동

```
/gsd:progress  → STATE.md의 Current Status + Key Metrics 읽기
/gsd:update    → STATE.md의 모든 섹션 갱신
/gsd:note      → STATE.md의 Logs 섹션에 추가
/gsd:pause-work → STATE.md에 중단 지점 기록
/gsd:resume-work → STATE.md에서 중단 지점 복원
```

---

## 7. 시나리오별 명령어 예시

### 시나리오 1: 새 세션 시작 (Wave 진행 중)

```bash
# 상황: 전날 Wave 5 실행 중 Rate Limit으로 세션 종료
# 목표: Wave 5 남은 파일 생성 재개

# Step 1: 상태 확인
/gsd:resume-work
# → 마지막 중단 지점: 04_dev/03_cicd_pipeline.md (미완료)

# Step 2: 현황 파악
/gsd:progress
# → Wave 5 진행률: 3/6 파일 완료

# Step 3: 블로커 확인
/gsd:check-todos
# → 블로커 없음

# Step 4: 남은 작업 재개
/gsd:execute-phase 4 --resume
# → 04_dev/03_cicd_pipeline.md 부터 재시작

# Step 5: 완료 후 검증
/gsd:verify-work 4

# Step 6: 커밋 및 상태 갱신
git commit -m "docs(wave5): complete remaining 3 files"
/gsd:update
```

### 시나리오 2: Rate Limit 도달 시 대응

```bash
# 상황: execute-phase 도중 API Rate Limit 경고
# 목표: 안전하게 중지 후 재개 계획 수립

# Step 1: 즉시 안전 중지
/gsd:pause-work
# → uncommitted 변경사항 WIP 커밋 자동 실행

# Step 2: 현재 상태 메모
/gsd:note "Rate Limit 도달 — 04_dev/04_monitoring.md 50% 완료. 리셋 시간: 17:00"

# Step 3: PM Agent에 보고
/gsd:note "PM 에스컬레이션: Wave 5 Rate Limit으로 2시간 지연 예상"

# Step 4: 17:00 이후 재개
/gsd:resume-work
/gsd:execute-phase 4 --resume
```

### 시나리오 3: G-HARD 점수 상승 (Yellow 진입)

```bash
# 상황: 주간 Gate 심사에서 G-HARD 점수 3점 → 4점으로 상승
# 목표: Steering Committee 검토 요청 및 계획 조정

# Step 1: 점수 갱신 기록
/gsd:note "G-HARD 갱신: G=1, H=1, A=1, R=1, D=0 → 총점 4 (Yellow) — JPJ API 연동 지연 원인"

# Step 2: 현재 Phase 일시 중지 (비즈니스 임팩트 없는 작업으로 전환)
/gsd:pause-work

# Step 3: 대안 작업 진행 (의존성 없는 문서 생성)
/gsd:do "docs/05_governance/03_reporting_cycle.md 검토 및 업데이트"

# Step 4: Steering Committee 결정 대기
/gsd:note "Steering Committee 검토 요청: 수요일 10:00 AM 회의에서 JPJ 연동 지연 처리 방안 결정 필요"

# Step 5: 승인 후 재개
/gsd:resume-work
/gsd:execute-phase <N>
```

### 시나리오 4: 파일 간 참조 링크 오류 발견

```bash
# 상황: /gsd:verify-work 결과 참조 링크 3개 오류 발견
# 목표: 오류 수정 후 재검증

# Step 1: 오류 내용 확인
/gsd:verify-work 4
# 출력: ⚠️ 04_dev/05_gsd_workflow.md — 참조 오류 3개
#        - Line 45: [../05_governance/03_reporting_cycle.md] → 파일 없음
#        - Line 112: [02_paperclip_org.md] → 경로 오류
#        - Line 287: [../03_data/01_data_architecture.md] → 파일 없음 (Wave 3A 미완료)

# Step 2: 수정 가능한 오류 즉시 수정
/gsd:do "04_dev/05_gsd_workflow.md Line 112 참조 경로 수정"

# Step 3: 의존 파일 미생성 오류는 메모 기록
/gsd:note "참조 오류 보류: 03_data/01_data_architecture.md — Wave 3A 완료 후 자동 해결 예정"

# Step 4: 재검증
/gsd:verify-work 4
```

### 시나리오 5: 긴급 소작업 처리

```bash
# 상황: PM이 즉각적인 보고 자료 업데이트 요청
# 목표: 계획 단계 없이 즉시 처리

# Step 1: 현재 작업 저장
/gsd:pause-work

# Step 2: 긴급 작업 즉시 실행
/gsd:quick "05_governance/03_reporting_cycle.md 4월 보고 캘린더 업데이트"

# Step 3: 완료 확인
/gsd:review docs/05_governance/03_reporting_cycle.md

# Step 4: 커밋
git commit -m "docs: update April reporting calendar"

# Step 5: 원래 작업 재개
/gsd:resume-work
```

### 시나리오 6: Wave 완료 후 다음 Wave 착수

```bash
# 상황: Wave 4 (02_system/ 6개 파일) 완료
# 목표: Wave 5 (04_dev/ 6개 파일) 착수

# Step 1: Wave 4 최종 검증
/gsd:verify-work 3
# → ✅ 모든 성공 기준 충족

# Step 2: 원자적 커밋
git commit -m "docs(wave4): generate 6 system design files (3,100 lines)"

# Step 3: STATE.md 갱신
/gsd:update

# Step 4: 진행 현황 공유 (Heartbeat)
/gsd:progress
# → CEO/Steering Committee에 보고

# Step 5: 다음 Wave G-HARD 점수 확인
/gsd:health
# → G-HARD 점수 확인 후 진행 여부 결정

# Step 6: 다음 Wave 계획
/gsd:discuss-phase 4
/gsd:plan-phase 4

# Step 7: 실행
/gsd:execute-phase 4
```

---

## 8. GSD 안티패턴

### 8.1 절대 하지 말아야 할 것

| 안티패턴 | 문제점 | 올바른 방법 |
|---------|--------|-------------|
| **plan-phase 없이 execute-phase 실행** | 담당 Agent 미배정, 충돌 발생 | 항상 plan-phase → execute-phase 순서 준수 |
| **G-HARD 게이트 건너뜀** | 승인 없이 고위험 Phase 진행 | 점수 확인 후 해당 승인 절차 완료 |
| **STATE.md 직접 수동 편집** | 포맷 파괴, 참조 오류 | `/gsd:update` 명령어만 사용 |
| **Wave 중간에 커밋** | 원자성 파괴, 불완전한 상태 커밋 | Wave 단위 완전 완료 후 1회 커밋 |
| **pause-work 없이 세션 종료** | 진행 상태 손실, 재개 불가 | 세션 종료 전 반드시 /gsd:pause-work |
| **00_MASTER.md 수정** | 전체 문서 구조 파괴 | 00_MASTER.md는 읽기 전용 |
| **동일 파일 동시 수정** | Git 충돌, 내용 손실 | 파일 잠금 프로토콜 준수 |
| **verify-work 없이 next 실행** | 불완전한 Phase가 완료로 표시 | 항상 verify-work 후 next |

### 8.2 주의해야 할 패턴

```
⚠️ 주의: /gsd:fast 남용
→ fast 명령은 계획 단계를 최소화함
→ 복잡한 Phase에서 사용 시 충돌/오류 위험 증가
→ 명확하고 반복적인 단순 작업에만 사용

⚠️ 주의: /gsd:do 연속 사용
→ 여러 파일을 연속으로 do 명령 처리 시 STATE.md 갱신 누락 위험
→ 3개 이상 연속 작업은 execute-phase 사용 권장

⚠️ 주의: Logs 섹션 과도한 기록
→ STATE.md Logs가 너무 길어지면 progress 명령 성능 저하
→ 오래된 로그(30일 이상)는 별도 archive 파일로 이동

⚠️ 주의: G-HARD 점수 임의 조정
→ G-HARD 점수는 Compliance Agent 또는 PM Agent만 공식 갱신 가능
→ 개별 Agent가 임의로 점수를 낮게 조정하면 위험 가시성 저하
```

### 8.3 일반적인 실수와 수정 방법

#### 실수 1: 잘못된 파일 경로로 작업 시작

```bash
# 잘못된 예:
/gsd:do "04_dev/gsd_workflow.md 생성"  # 올바른 경로: 04_dev/05_gsd_workflow.md

# 수정 방법:
/gsd:pause-work
/gsd:note "경로 오류: 04_dev/gsd_workflow.md → 04_dev/05_gsd_workflow.md 로 정정"
# 잘못 생성된 파일 삭제 후 올바른 경로로 재실행
```

#### 실수 2: 의존 파일 미완성 상태에서 참조 파일 생성

```bash
# 문제: 03_data/01_data_architecture.md 미생성 상태에서
#       04_dev/05_gsd_workflow.md가 해당 파일 참조

# 수정 방법:
# 1. 생성된 파일에서 참조 링크를 주석처리
#    <!-- TODO: 03_data/01_data_architecture.md Wave 3A 완료 후 링크 활성화 -->
# 2. /gsd:note "TODO: 파일명 참조 링크 — Wave 3A 완료 후 수동 활성화"
# 3. verify-work에서 해당 항목은 경고(Warning)로 처리
```

#### 실수 3: 여러 Agent가 STATE.md 동시 갱신

```bash
# 문제: CTO Agent와 DA Lead Agent가 동시에 /gsd:update 실행
#       → STATE.md 충돌 (Git merge conflict)

# 수정 방법:
# 1. PM Agent가 STATE.md 업데이트 큐 관리
# 2. 각 Agent는 /gsd:note 로 업데이트 요청
# 3. PM Agent가 순차적으로 /gsd:update 실행
```

---

## 9. 참조 문서

### 직접 연관 문서

| 문서 | 경로 | 관계 |
|------|------|------|
| Paperclip 조직 구조 | `docs/04_dev/02_paperclip_org.md` | Agent 역할 및 협업 체계 정의 |
| 보고 체계 및 주기 | `docs/05_governance/03_reporting_cycle.md` | Heartbeat 보고 일정 및 형식 |
| G-HARD 의사결정 게이트 | `docs/05_governance/01_decision_gates.md` | Gate 0~7 기준 및 승인 절차 |
| Board 의사결정 목록 | `docs/05_governance/02_board_decisions.md` | 21개 Board 결정 및 근거 |

### 기초 문서

| 문서 | 경로 | 관계 |
|------|------|------|
| 마스터 구조 | `docs/00_MASTER.md` | 전체 프로젝트 구조 (읽기 전용) |
| 프로젝트 현황 | `.planning/STATE.md` | GSD 상태 관리 파일 |
| 실행 계획 | `.planning/ROADMAP.md` | Wave/Phase 전체 계획 |
| 요구사항 정의 | `.planning/REQUIREMENTS.md` | 67개 문서 요구사항 |

### GSD 공식 문서

| 문서 | 설명 |
|------|------|
| GSD Skills (내장) | `/gsd:help` 명령으로 전체 명령어 목록 조회 |
| GSD 설정 | `.planning/config.json` (YOLO/Standard/Parallel/Balanced) |

---

*문서 버전: v1.0 | 최초 작성: 2026-04 | 담당: PM Agent*  
*다음 검토: Wave 5 실행 완료 후*
