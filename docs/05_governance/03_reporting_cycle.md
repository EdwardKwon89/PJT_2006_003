# 보고 체계 및 주기 (Reporting Cycle & Dashboard)

**문서 버전**: 1.0  
**작성일**: 2026-04-01  
**상태**: Draft  
**담당자**: Governance & Compliance Office

---

## 1. 보고 체계 개요

### 1.1 목적
- **의사결정 지원**: CEO, Board, Steering Committee의 실시간 정보 제공
- **진행 상황 추적**: Phase/Wave별 마일스톤 달성도 모니터링
- **위험 조기 발견**: KPI 이탈, 일정 지연, 예산 초과 조기 감지
- **투명성 확보**: 이해관계자(HiPass Authority, 투자사)에 대한 정기 보고

### 1.2 원칙
| 원칙 | 설명 |
|------|------|
| **정시성** | 정해진 일정에 정확히 제출 (지연 금지) |
| **정확성** | 검증된 데이터만 포함 (추정값 명시) |
| **실행성** | 실제 의사결정으로 연결되는 내용 중심 |
| **간결성** | 핵심 지표만 포함 (5~10개 KPI 집중) |
| **추적성** | 문제 해결 조치 사항 및 결과 기록 |

---

## 2. 보고 주기 및 일정

### 2.1 4층 보고 체계

```
┌──────────────────────────────────────────────────────┐
│  Level 1: 일일 보고 (Daily Standup)                 │
│  - 팀 단위 / 15분 / 개발/QA/운영 팀                  │
│  - 작업 진행률, 블로커, 당일 목표                    │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────┴───────────────────────────────────────┐
│  Level 2: 주간 보고 (Weekly Digest)                 │
│  - 팀별 / 매주 금요일 17:00 / 30분                   │
│  - 완료 작업, KPI, 위험 요소, 다음주 계획            │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────┴───────────────────────────────────────┐
│  Level 3: 격주 임원진 보고 (CEO Heartbeat)          │
│  - CEO / 매 2주 월요일 09:00 / 45분                  │
│  - Phase 진행도, 위험 현황, 의사결정 필요 사항      │
└──────────────┬───────────────────────────────────────┘
               │
┌──────────────┴───────────────────────────────────────┐
│  Level 4: 월간 Steering 보고 (Monthly Governance)   │
│  - Steering Committee / 매월 첫 주 목요일 14:00     │
│  - 단계별 성과, 투자대비 성과(ROI), Board 보고      │
└──────────────────────────────────────────────────────┘
```

### 2.2 상세 보고 일정

| 레벨 | 주기 | 요일 | 시간 | 참석자 | 형식 | 페이지 |
|------|------|------|------|--------|------|--------|
| **L1: Daily** | 평일 | 월~금 | 09:30 | 개발팀, Tech Lead | Standup | 1-2 줄 요약 |
| **L2: Weekly** | 매주 | 금 | 17:00 | 팀 Lead, PM | Digest | 1~2 페이지 |
| **L3: Bi-weekly (Heartbeat)** | 격주 | 월 | 09:00 | CEO, CTO, PM | Dashboard | 3~5 페이지 |
| **L4: Monthly** | 월 | 첫주 목 | 14:00 | Steering Committee | Board Report | 5~8 페이지 |

### 2.3 보고 캘린더 (2026년 기준)

```
 4월 (Phase 1 Kick-off)
 ├─ 04/06 (월) → L1 Daily Start
 ├─ 04/11 (금) → L2 Weekly 1차
 ├─ 04/14 (월) → L3 Heartbeat 1차
 ├─ 04/18 (금) → L2 Weekly 2차
 ├─ 04/21 (월) → L3 Heartbeat 2차 + L4 Monthly 1차

 5월 (Phase 1 진행)
 ├─ 05/09 (금) → L2 Weekly 3차
 ├─ 05/12 (월) → L3 Heartbeat 3차
 ├─ 05/16 (금) → L2 Weekly 4차
 ├─ 05/19 (월) → L3 Heartbeat 4차 + L4 Monthly 2차

 6월 (Phase 1 마무리 / Phase 2 시작)
 ├─ 06/06 (금) → L2 Weekly 5차 (Phase 1 완료 보고)
 ├─ 06/09 (월) → L3 Heartbeat 5차 (Phase 2 Kick-off)
 ...
```

---

## 3. CEO 주간 보고서 (Bi-weekly Heartbeat Template)

### 3.1 표준 템플릿

```markdown
# Paperclip CEO Heartbeat
**보고 기간**: 2026-04-07 ~ 2026-04-20
**보고자**: Project Management Office
**상태**: 🟢 On Track / 🟡 At Risk / 🔴 Critical

---

## 1. 실행 요약 (Executive Summary)
[1~2문장] 이번 2주간 주요 성과 및 현재 상태

---

## 2. Phase 진행도 (Phase Progress)

### Phase 1: Foundation (기간: 04/06 ~ 06/30)
- **목표**: BOS 개발, 환경 설정, 보안 감시 활성화
- **진행률**: ██████░░░░ 60% (Target: 50%)
- **다음 마일스톤**: 2026-05-15 (API Gateway v1.0)
- **상태**: ✅ On Track

### Phase 2: Core Platform (기간: 07/01 ~ 09/30)
- **목표**: SLFF/MLFF 핵심 모듈 개발
- **진행률**: ░░░░░░░░░░ 0% (아직 미시작)
- **예정 시작**: 2026-07-01
- **상태**: ⏳ Planned

---

## 3. 핵심 KPI (5대 지표)

| KPI | 목표 | 현황 | 상태 |
|-----|------|------|------|
| **개발 생산성** | 12 Story Points/주 | 14 pts | ✅ +17% |
| **결함 해결률** | 95% | 92% | 🟡 -3% |
| **일정 준수도** | 100% | 98% | ✅ -2% |
| **보안 점수** | 90/100 | 87/100 | 🟡 -3% |
| **팀 행복도** | 8.0/10 | 7.8/10 | 🟡 -0.2 |

---

## 4. 위험 현황 (Risk Dashboard)

### 4.1 활성 위험 (Active Risks)

| ID | 위험 | 심각도 | 소유자 | 상태 |
|----|------|--------|--------|------|
| R-01 | API 응답 시간 초과 (>500ms) | 🔴 High | Tech Lead | 🔧 Mitigating |
| R-02 | 말레이시아 규제 변경 | 🟡 Medium | Legal | 🟢 Managed |
| R-03 | 팀 인력 부족 (QA) | 🟡 Medium | HR | ⏳ Pending |

### 4.2 해결 완료 (Resolved)
- ✅ R-00: 데이터베이스 성능 → 인덱싱 최적화로 해결 (2026-04-18)

---

## 5. 의사결정 필요 사항 (Decisions Needed)

| 항목 | 현황 | 요청 | 마감 |
|------|------|------|------|
| **QA 팀 증원** | 현재 2명, 필요 3명 | 예산 승인 | 2026-04-30 |
| **API 기술 스택** | Node.js vs Golang | 선택 | 2026-04-25 |
| **Phase 2 예산** | USD 1.2M 검토 중 | 최종 승인 | 2026-05-15 |

---

## 6. 주요 성과 (Key Achievements)

✅ BOS 데이터베이스 스키마 v1.0 완성  
✅ 결제 API 4개 모듈화 (Payment, Settlement, Reconciliation, Reporting)  
✅ 환경별 CI/CD 파이프라인 구축 (Dev, Staging, Production)  
✅ 보안 감시 대시보드 운영 시작 (실시간 모니터링)  

---

## 7. 다음주 포커스 (Next 2-Week Focus)

1. **개발**: API Gateway v1.0 완성 테스트 (예정: 04/25)
2. **QA**: Integration Test Suite 작성 시작
3. **운영**: Kubernetes 클러스터 프로덕션 환경 배포 준비
4. **거버넌스**: Steering Committee 월간 보고 준비

---

## 8. 역할별 상태 (Team Status)

| 역할 | 팀 | 책임자 | 상태 | 비고 |
|------|-----|---------|------|------|
| **개발** | Dev Squad | Tech Lead A | ✅ On Track | 14 pts 완료 |
| **QA** | QA Team | QA Lead | 🟡 At Risk | 테스트 케이스 20% 지연 |
| **운영** | DevOps | Infra Lead | ✅ On Track | 모니터링 시스템 완성 |
| **데이터** | Analytics | Data Lead | ✅ On Track | BI 대시보드 프로토타입 완성 |
| **거버넌스** | PMO | PMO Director | ✅ On Track | 보고 체계 정상 운영 |

---

## 9. 첨부 & 대시보드 링크

- **📊 실시간 대시보드**: https://dashboard.internal/paperclip/phase-1
- **📋 상세 위험 현황**: Risk_Register_2026-04-20.xlsx
- **📈 KPI 추이**: KPI_Trend_Q2_2026.pdf
- **🔐 보안 감시 리포트**: Security_Scan_2026-04-20.pdf

---

**보고 종료**
```

### 3.2 Heartbeat 템플릿 커스터마이징 변형

#### 경영진(C-Suite) 용 축약본 (1페이지)
```
📌 **3줄 요약**
- Phase 1 진행률 60% (목표 50% 달성)
- 5대 KPI 중 3개 목표 달성, 2개 개선 필요
- 2개 위험 현황: API 응답 시간 개선 진행 중, QA 인력 추가 필요

⚠️  **즉시 조치 필요**
- QA 팀 1명 추가 승인 필요 (4월 30일까지)
- API 기술 스택 선택 (4월 25일까지)

✅ **다음주 핵심**
- API Gateway v1.0 완성 (예정: 4월 25일)
- Kubernetes 프로덕션 배포 준비
```

#### 기술팀(Tech Lead) 용 상세본 (5~7페이지)
- 코드 커버리지 현황 (목표 85%, 현황 82%)
- 성능 지표 (응답시간, 처리량, 메모리)
- 인프라 상태 (가용성 99.95%, 비용 USD 12K/월)
- 기술 부채 현황 (남은 리팩토링 4개, 의존성 업데이트 2개)

---

## 4. Paperclip Heartbeat 일정 및 자동화

### 4.1 격주 Heartbeat 스케줄

```bash
# 매 격주 월요일 08:00 UTC+8 (말레이시아 시간)
# 자동 생성 및 배포
0 8 * * 1  # 격주 월요일 (첫번째, 세번째)

보고 기간: 2주 단위
- 주기 1: 04/07 ~ 04/20 (보고: 04/21 월 09:00)
- 주기 2: 04/21 ~ 05/04 (보고: 05/05 월 09:00)
- 주기 3: 05/05 ~ 05/18 (보고: 05/19 월 09:00)
...
```

### 4.2 자동 데이터 수집 (Data Ingestion)

| 데이터 소스 | 수집 시기 | 빈도 | 담당 |
|------------|---------|------|------|
| **Jira** (Story Points, Bug) | 매일 23:00 | Daily | Automation |
| **GitHub** (Commit, PR) | 매일 23:00 | Daily | CI/CD |
| **SonarQube** (Code Quality) | 매일 00:00 | Daily | QA |
| **Datadog** (성능, 가용성) | 실시간 | Real-time | Monitoring |
| **Survey** (팀 행복도) | 목요일 | Weekly | HR |
| **수동 입력** (의사결정, 위험) | 일요일 18:00 | Weekly | PMO |

### 4.3 보고서 자동 생성 파이프라인

```
┌─────────────────────┐
│  자동 데이터 수집   │  (매일/주 수집)
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  데이터 검증 & 통합  │  (일요일 18:00)
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  Heartbeat 초안 생성 │  (일요일 19:00)
│  (마크다운 자동화)   │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  PMO 검토 & 수정    │  (월요일 07:00~08:00)
│  (수동 최종 검토)    │
└──────────┬──────────┘
           │
           ↓
┌─────────────────────┐
│  CEO 배포 & 공지   │  (월요일 08:30)
│  (메일, 대시보드)    │
└─────────────────────┘
```

---

## 5. KPI 모니터링 & 대시보드

### 5.1 5대 핵심 KPI 정의

#### KPI-1: 개발 생산성 (Dev Velocity)
```
지표: 주당 완료 Story Points
목표: 12 pts/주 (±2)
계산: Jira에서 자동 추출
임계값:
  - 🟢 Green: 10~14 pts
  - 🟡 Yellow: 8~9 pts 또는 15~16 pts
  - 🔴 Red: <8 pts 또는 >16 pts (과부하)
```

#### KPI-2: 버그 해결률 (Bug Resolution Rate)
```
지표: 발견된 버그 중 해결된 비율 (%)
목표: 95% 이상
계산: Resolved_Bugs / Total_Bugs
임계값:
  - 🟢 Green: 95~100%
  - 🟡 Yellow: 90~94%
  - 🔴 Red: <90%
산정 기간: 주 단위
```

#### KPI-3: 일정 준수도 (Schedule Adherence)
```
지표: 계획된 마일스톤 대비 실제 완료율 (%)
목표: 100% (지연 없음)
계산: On_Time_Deliverables / Planned_Deliverables
임계값:
  - 🟢 Green: 100%
  - 🟡 Yellow: 95~99% (±1주)
  - 🔴 Red: <95% (>1주 지연)
산정 기간: Phase 단위
```

#### KPI-4: 보안 점수 (Security Score)
```
지표: 보안 감시 종합 점수 (0~100)
목표: 90점 이상
계산: OWASP + CVE 검사 + Compliance 점수 통합
임계값:
  - 🟢 Green: 90~100
  - 🟡 Yellow: 80~89
  - 🔴 Red: <80 (취약점 있음)
산정 기간: 주 단위 (실시간 모니터링)
세부 항목:
  - 취약점 개수 (Critical, High, Medium, Low)
  - Compliance: PCI-DSS, ISO 27001 준수도
  - 보안 테스트: SAST, DAST 실행률
```

#### KPI-5: 팀 행복도 (Team Satisfaction)
```
지표: 팀 만족도 점수 (0~10)
목표: 8.0 이상
계산: 주간 익명 설문 (Slack/Google Form)
임계값:
  - 🟢 Green: 8.0~10
  - 🟡 Yellow: 7.0~7.9
  - 🔴 Red: <7.0 (문제 있음)
산정 기간: 주 단위
측정 항목:
  - 일과 삶의 균형
  - 팀 협력도
  - 프로젝트 이해도
  - 리더십 만족도
```

### 5.2 실시간 대시보드 (Dashboard)

#### 구성 요소
```
┌─────────────────────────────────────────────────────────┐
│  Paperclip Project Dashboard (Real-time)               │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  ┌─ Phase Progress ──────────┐  ┌─ Key Metrics ────────┐
│  │ Phase 1: ██████░░░░ 60%   │  │ Velocity:    14 pts  │
│  │ Phase 2: ░░░░░░░░░░  0%   │  │ Bugs:        92%    │
│  │ Phase 3: ░░░░░░░░░░  0%   │  │ Schedule:   98%    │
│  └───────────────────────────┘  │ Security:    87/100  │
│                                   │ Happiness:   7.8/10 │
│  ┌─ Risk Heatmap ────────────┐  └──────────────────────┘
│  │ 🔴 1 Critical             │
│  │ 🟡 2 Medium               │
│  │ 🟢 3 Low                  │
│  └───────────────────────────┘
│
│  ┌─ Resource Allocation ─────────┐
│  │ Dev: 6/6 (100%)               │
│  │ QA:  2/3 (67%)  ⚠️  Need +1   │
│  │ Ops: 3/3 (100%)               │
│  └───────────────────────────────┘
│
│  ┌─ Upcoming Deadlines ──────────────┐
│  │ 🟢 04/25: API Gateway v1.0        │
│  │ 🟡 05/15: Phase 1 Completion      │
│  │ ⏳ 07/01: Phase 2 Kick-off        │
│  └───────────────────────────────────┘
│
└─────────────────────────────────────────────────────────┘
```

#### 접근 권한 & 배포 채널

| 사용자 | 대시보드 | 업데이트 주기 | 접근 방식 |
|--------|---------|------------|---------|
| **CEO/CTO** | Executive Summary | 격주 | Web Portal |
| **Tech Lead** | Technical Metrics | 실시간 | Datadog/Grafana |
| **QA Lead** | Bug & Test Metrics | 일일 | Jira |
| **Team** | Personal Metrics | 일일 | Slack Bot |

---

## 6. 월간 Steering Committee 보고 (Monthly Governance Report)

### 6.1 구조 및 내용

```markdown
# Monthly Steering Committee Report
**보고 기간**: 2026년 4월
**보고자**: PMO Director
**승인자**: Steering Committee Chair

---

## 1. Phase 단계별 성과 (Phase-by-Phase Progress)

### Phase 1: Foundation (Goal: Infrastructure Ready)
- **계획 대비 진행률**: 60% / 목표 50% → **+10% ahead**
- **완료된 마일스톤**:
  - ✅ BOS DB 스키마 설계 완료 (04/10)
  - ✅ API Framework 구축 완료 (04/15)
  - ✅ 환경 자동화 파이프라인 구축 (04/20)
- **예정된 마일스톤**:
  - ⏳ API Gateway v1.0 (04/25)
  - ⏳ Phase 1 완료 (06/30)

---

## 2. 투자 대비 성과 (ROI & Cost-Benefit)

| 항목 | 계획 | 실제 | 차이 |
|------|------|------|------|
| **Phase 1 예산** | USD 500K | USD 480K | -USD 20K (✅ -4%) |
| **개발 인력** | 6명 | 6명 | 0명 |
| **인프라 비용** | USD 15K/월 | USD 12K/월 | -USD 3K/월 (✅ -20%) |
| **누적 투자** | USD 500K | USD 480K | **계획보다 4% 저비용** |

**ROI 추정**:
- Phase 1 투자: USD 480K
- 예상 연간 수익 (말레이시아 시장): USD 2~3M
- 예상 회수 기간: 3~4개월 (Phase 3 이후)

---

## 3. 리스크 & 대응 (Risk Management)

| ID | 위험 | 영향도 | 대응 |
|----|------|--------|------|
| R-01 | API 응답 시간 초과 (>500ms) | High | DB 인덱싱 최적화 진행 |
| R-02 | 규제 변경 (통화 규정) | Medium | Legal 팀 협의 중 |
| R-03 | QA 팀 부족 (2→3명 필요) | Medium | HR에 채용 요청 진행 중 |

---

## 4. 이해관계자 만족도 (Stakeholder Satisfaction)

- **HiPass Authority**: 🟢 Very Satisfied (기술 진행 만족)
- **투자사**: 🟢 Satisfied (예산 관리 및 진도 만족)
- **개발팀**: 🟡 Satisfied (일정 압박, 개선 필요)
- **고객사**: ⏳ TBD (아직 상용화 전)

---

## 5. 다음 달 포커스 (May Priorities)

1. **API Gateway v1.0 완성** (4월 25일 목표)
2. **Integration Test 커버리지 80% 달성**
3. **QA 팀 1명 추가 채용 완료**
4. **보안 감시 대시보드 Phase 2 확대**
```

### 6.2 월간 보고 제출 일정

| 월 | 보고 날짜 | Phase | 초점 | 담당자 |
|----|---------|-------|------|--------|
| 4월 | 04/21 목 14:00 | Phase 1 시작 | 초기 기반 구축 | PMO |
| 5월 | 05/19 목 14:00 | Phase 1 진행 | 개발 가속화 | PMO |
| 6월 | 06/16 목 14:00 | Phase 1 마무리 | 완료 전 최종 점검 | PMO |
| 7월 | 07/21 목 14:00 | Phase 2 시작 | Phase 2 Kick-off | PMO |

---

## 7. 보고 양식 및 도구

### 7.1 사용 도구

| 보고 레벨 | 도구 | 자동화 | 승인 |
|----------|------|--------|------|
| **L1: Daily** | Slack Standup Bot | ✅ 자동 | 팀 Lead |
| **L2: Weekly** | Jira Report + Google Sheets | 🟡 반자동 | PM |
| **L3: Heartbeat** | Markdown + Datadog API | 🟡 반자동 | CEO |
| **L4: Monthly** | PDF + PowerPoint | ⚠️  수동 | Steering Chair |

### 7.2 데이터 검증 프로세스

```
1. 데이터 수집 (자동)
   ├─ Jira API (Story Points, Bugs)
   ├─ GitHub API (Commits, PRs)
   └─ Datadog API (Performance, Availability)

2. 데이터 통합 & 정제 (자동)
   ├─ 중복 제거
   ├─ 데이터 타입 검증
   └─ 이상치 감지

3. 지표 계산 (자동)
   ├─ KPI 계산
   ├─ 추이 분석
   └─ 임계값 비교

4. 사람 검수 (수동)
   ├─ PMO 리뷰
   ├─ 비즈니스 맥락 추가
   └─ 의사결정 제안 작성

5. 배포 & 공지
   ├─ 메일 발송
   ├─ 대시보드 업데이트
   └─ 회의 개최
```

### 7.3 예외 상황 보고 (Out-of-Cycle)

**즉시 보고 필요한 경우**:
- 🔴 **Critical 위험** 발생 (보안 침해, 심각한 버그, 일정 큰 지연)
- 🟠 **예산 초과** (±10% 이상)
- ⚠️  **핵심 인력 결원** (팀 리드, 책임자)

**보고 절차**:
1. 팀 Lead → PM에 즉시 알림 (문제 인지 후 30분 내)
2. PM → CEO/CTO에 긴급 보고 (1시간 내)
3. CEO → Steering 멤버 통보 (2시간 내)
4. 대응 방안 회의 개최 (당일 또는 익일)

---

## 8. 보고 체계 최적화 및 개선

### 8.1 정기 검토 (월 1회)

```
매월 마지막 목요일 11:00 → 보고 체계 Review
- 보고 기한 준수율 검토
- 데이터 정확성 검증
- 개선 사항 도출 및 적용
- 다음 달 포커스 조정
```

### 8.2 개선 사항 추적 (Continuous Improvement)

| 개선사항 | 우선순위 | 상태 | 기한 |
|---------|---------|------|------|
| 자동 보고 생성 자동화 | High | ⏳ Planning | 2026-05-30 |
| 대시보드 모바일 최적화 | Medium | ⏳ Pending | 2026-06-30 |
| 다국어 보고 (영어/말레이) | Medium | ⏳ Pending | 2026-07-31 |
| 예측 분석 추가 (예측 KPI) | Low | ⏳ Backlog | 2026-08-31 |

---

## 9. 부록 (Appendix)

### 9.1 관련 문서
- [Project Charter](../01_business/01_project_charter.md) — 프로젝트 목표 및 범위
- [Organization & Roles](../01_business/04_organization_roles.md) — 조직 구조 및 역할
- [Decision Gates](./01_decision_gates.md) — G-HARD 게이트 및 의사결정 현황

### 9.2 유용한 링크
- **대시보드**: https://dashboard.internal/paperclip
- **Jira**: https://jira.internal/paperclip
- **Datadog**: https://datadog.internal/paperclip
- **Slack Channel**: #paperclip-reporting

### 9.3 자주 묻는 질문 (FAQ)

**Q: 왜 격주 보고(Heartbeat)인가?**  
A: 일일 보고는 실행 팀 관점, 월간은 전략 관점이므로, 경영진 의사결정을 위해 2주 단위의 균형 잡힌 주기가 필요합니다.

**Q: KPI 임계값은 누가 정하는가?**  
A: CEO/CTO와 협의하여 Phase별로 재검토하며, 현실적인 목표 설정과 도전적 목표의 균형을 맞춥니다.

**Q: 데이터가 일치하지 않으면?**  
A: PMO가 데이터 소스(Jira, Datadog, 수동 입력)를 교차 검증하고, 최종 책임은 PMO Director가 부담합니다.

---

**버전**: 1.0 | **최종 검토**: 2026-04-01 | **다음 검토**: 2026-05-01
