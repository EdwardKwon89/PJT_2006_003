# Organization Roles & Governance Structure

**문서 버전**: 1.0  
**작성일**: 2026-04-01  
**상태**: Draft (Board Approval Pending)  
**담당자**: Project Steering Committee

---

## 1. Executive Summary

Malaysia SLFF/MLFF 프로젝트의 조직 구조 및 역할 정의. JVC(Joint Venture Company) 체제에서 5단계 계층 단위(Line, Plaza, Toll Center, Clearing Center, TOC)를 기반으로 명확한 책임 및 권한을 설정하고, BOS 접근 권한(열람/입력/결제), Paperclip 29개 Agent의 조직화, 의사결정 권한을 상세히 정의한다.

---

## 2. JVC (Joint Venture Company) 구조

### 2.1 JVC 조직 계층

```
┌─────────────────────────────────────────────────────────┐
│   HiPass Authority (말레이시아 정부 기관)               │
│   • 감독 권한, 규제 준수 강제                           │
└────────────────────┬────────────────────────────────────┘
                     │
         ┌───────────┴──────────┐
         │                      │
         ▼                      ▼
┌─────────────────────┐  ┌──────────────────────┐
│ Our Platform        │  │ HiPass Authority     │
│ (본사/개발)         │  │ (운영 감독)          │
│                     │  │                      │
│ • CEO               │  │ • Overall Authority  │
│ • CTO/Tech Lead     │  │ • Policy Setting     │
│ • CPO (Product)     │  │ • Compliance         │
│ • CIO (Operations)  │  └──────────────────────┘
│ • PM (Projects)     │
│ • Compliance        │
└─────────────────────┘
```

### 2.2 직급별 책임 (C-Level)

| 직급 | 이름 | 책임 | 보고처 |
|------|------|------|--------|
| **CEO** | Chief Executive Officer | 전략 수립, 외부 협력, 재정 관리 | Board of Directors |
| **CTO** | Chief Technology Officer | 기술 아키텍처, AI Agent 조직화, 개발 감독 | CEO |
| **CPO** | Chief Product Officer | 제품 로드맵, 사용자 경험, 기능 정의 | CEO |
| **CIO** | Chief Information Officer | 운영 시스템, 보안, 데이터 관리 | CEO |
| **PM** | Program Manager | 프로젝트 일정, 마일스톤, 리스크 관리 | CEO |
| **Compliance** | Chief Compliance Officer | 규제 준수, 감사, 보안 인증 | CEO |

### 2.3 Steering Committee

**구성:**
- CEO (의장)
- CTO, CPO, CIO
- HiPass Authority 대표 1명
- 정부 규제담당자 1명 (옵션)

**주요 결정사항:**
- 기술 아키텍처 승인
- 예산 변경 (>10%)
- 주요 위험 & 이슈 에스컬레이션
- 외부 파트너 선정
- Phase 마일스톤 승인

**회의 주기:** 주 1회 (수요일 10:00 AM)

---

## 3. 5단계 계층 단위 (Aggregation Levels)

Malaysia 통행료 징수 체계의 5단계 계층. BOS 권한 및 데이터 접근 범위를 정의한다.

### 3.1 계층 구조

```
Level 1: Line (운영진)
├─ 전국 고속도로 운영 정책 결정
├─ BOS 권한: 조회(R), 입력(W), 결제(P) — 전체
└─ Agent: Line Manager (1명)

Level 2: Plaza (요금소 - 10~15개)
├─ 요금소 수익, 장비 관리, 일일 보고
├─ BOS 권한: 조회(R), 입력(W), 결제(P) — 해당 Plaza만
└─ Agent: Plaza Manager (10~15명)

Level 3: Toll Center (지역 센터 - 3~4개)
├─ 지역 플래자 통합 관리, 정산 수합
├─ BOS 권한: 조회(R+), 입력(W+), 결제(P+) — 해당 Region
└─ Agent: Regional Manager (3~4명)

Level 4: Clearing Center (정산 센터 - 1개)
├─ 전국 거래 정산, 은행 연동, 수수료 계산
├─ BOS 권한: 조회(R++), 입력(W++), 결제(P++) — 전체
└─ Agent: Clearing Manager (1명)

Level 5: TOC (기존 시스템 연계)
├─ Legacy HiPass 시스템과의 데이터 교환
├─ BOS 권한: 조회(R-), 입력(API만), 결제(N/A)
└─ Agent: Integration Manager (1명)
```

### 3.2 계층별 역할 정의

| 계층 | 담당자 | 주요 책임 | 권한 범위 | 보고처 |
|------|--------|----------|---------|--------|
| **Line** | Operations Director | 전국 운영 정책, 목표 설정, 예산 승인 | 전체 | CEO |
| **Plaza** | Toll Manager | 요금 수집, 장비 모니터링, 일일 보고 | 해당 요금소 | Regional Manager |
| **Toll Center** | Regional Manager | 지역 통합 관리, 정산 수합, 보고서 작성 | 해당 지역 | Operations Director |
| **Clearing Center** | Finance Manager | 전국 정산, 거래 조정, 은행 연동 | 전체 (금융) | CFO |
| **TOC** | Legacy Admin | 기존 시스템 유지, 데이터 마이그레이션 | 읽기 전용 | Operations Director |

---

## 4. BOS (Back-Office System) 접근 권한 매트릭스

### 4.1 권한 정의

| 권한 | 약어 | 설명 | 예시 |
|------|------|------|------|
| **조회 (Read)** | R | 거래, 보고서 열람 | 매출 현황, 거래 내역 |
| **조회+ (Read+)** | R+ | 자신 + 하위 조직 열람 | 지역 매출 + 하위 플래자 |
| **조회++ (Read++)** | R++ | 전사 조회 (민감 데이터 제외) | 전체 거래, 정산 현황 |
| **입력 (Write)** | W | 거래 조정, 수동 입력 | 미수 등록, 감면 처리 |
| **입력+ (Write+)** | W+ | 조정 + 승인 | 거래 취소, 예외 처리 |
| **입력++ (Write++)** | W++ | 전사 입력 권한 | 정산 결정, 수수료 설정 |
| **결제 (Payment)** | P | 거래 승인, 청구 확정 | 일일 정산 확정 |
| **결제+ (Payment+)** | P+ | 결제 + 조정 | 오류 거래 복구 |
| **결제++ (Payment++)** | P++ | 전사 결제 권한 | 예외 결제, 적립금 처리 |

### 4.2 역할별 BOS 권한 매트릭스

| 역할 | 거래 조회 | 거래 입력 | 정산 조회 | 정산 입력 | 결제 승인 | 보고서 생성 |
|------|----------|----------|----------|----------|----------|-----------|
| **CEO** | R++ | - | R++ | W++ | P++ | Y (전체) |
| **CIO** | R++ | W+ | R++ | W+ | P+ | Y (전체) |
| **Operations Director** | R+ | W | R+ | W | P | Y (전체) |
| **Regional Manager** | R+ | W | R+ | W | P | Y (지역) |
| **Toll Manager** | R | - | - | - | - | Y (플래자) |
| **Finance Manager** | R++ | W++ | R++ | W++ | P++ | Y (전체) |
| **Compliance Officer** | R++ | - | R++ | - | - | Y (감사) |
| **Support Agent** | R | - | - | - | - | Y (제한) |

### 4.3 데이터 경계 (Data Boundary)

각 역할은 다음 범위의 데이터만 접근:

| 역할 | 접근 범위 | 제약 |
|------|---------|------|
| Toll Manager | 해당 Plaza의 거래만 | 24시간 뒤 데이터 조회 불가 (감사용) |
| Regional Manager | 해당 Region의 모든 Plaza | 다른 Region 데이터 접근 불가 |
| Finance Manager | 전국 거래 + 정산 데이터 | 개인 정보 (차량번호) 마스킹 가능 |
| CEO | 전국 모든 데이터 | 제약 없음 |
| Compliance | 감사용 읽기 전용 | 편집 불가 |

---

## 5. Paperclip 29개 Agent 조직화

### 5.1 Agent 조직도 (4단계 계층)

```
┌─────────────────────────────────────────────────────────────┐
│                  Executive Board (2)                         │
│            • CEO Agent / Steering Agent                      │
└────┬─────────────────────────────────────────────┬───────────┘
     │                                             │
     ▼                                             ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│   Technology Bureau (8)      │    │   Operations Bureau (6)      │
│ • CTO Agent                  │    │ • COO Agent                  │
│ • Architecture Agent         │    │ • Operations Manager Agent   │
│ • Backend Agent (2)          │    │ • Finance Agent              │
│ • Frontend Agent (2)         │    │ • Compliance Agent           │
│ • DevOps Agent               │    │ • Support Agent              │
│ • Security Agent             │    └──────────────────────────────┘
└────┬─────────────────────────┘
     │
     ├─────────────────────────────────────────────────┐
     │                                                 │
     ▼                                                 ▼
┌──────────────────────────────┐    ┌──────────────────────────────┐
│    Data & Analytics (7)      │    │   Business Development (6)   │
│ • Data Architect             │    │ • Product Manager            │
│ • Data Engineer (2)          │    │ • Business Analyst (2)       │
│ • Analytics Agent            │    │ • QA Agent                   │
│ • Metadata Agent             │    │ • User Research Agent        │
│ • RBAC Agent                 │    │ • Partnership Agent          │
│ • Data Quality Agent         │    └──────────────────────────────┘
└──────────────────────────────┘
```

### 5.2 Agent별 상세 역할

#### **Executive Board (2)**

| Agent | 주요 책임 | Heartbeat |
|-------|----------|-----------|
| **CEO Agent** | 전략 수립, Board 의사결정, 리스크 에스컬레이션 | 일일 (9:00 AM) |
| **Steering Agent** | 의사결정 추진, 기록 관리, 보고 조정 | 주 1회 (수요일) |

#### **Technology Bureau (8)**

| Agent | 주요 책임 | 보고처 | Heartbeat |
|-------|----------|--------|-----------|
| **CTO Agent** | 기술 아키텍처, 기술 선정, 성능 모니터링 | CEO | 주 1회 |
| **Architecture Agent** | 시스템 설계, API 정의, 기술 부채 관리 | CTO | 주 2회 |
| **Backend Agent (1)** | 핵심 도메인 개발 (Transaction, Payment) | CTO | 일일 |
| **Backend Agent (2)** | 보조 도메인 개발 (Account, Billing, Violation) | CTO | 일일 |
| **Frontend Agent (1)** | Web UI 개발, 대시보드 구현 | CTO | 일일 |
| **Frontend Agent (2)** | Mobile App 개발 (React Native) | CTO | 일일 |
| **DevOps Agent** | 클라우드 인프라, CI/CD, 모니터링 | CTO | 일일 |
| **Security Agent** | 보안 설계, 펜 테스트, 규정 준수 | CTO + Compliance | 주 1회 |

#### **Operations Bureau (6)**

| Agent | 주요 책임 | 보고처 | Heartbeat |
|-------|----------|--------|-----------|
| **COO Agent** | 운영 전략, 인력 관리, 예산 운영 | CEO | 주 1회 |
| **Operations Manager Agent** | 일일 운영, 스케줄 관리, 팀 조율 | COO | 일일 |
| **Finance Agent** | 예산 관리, 수익 추적, 비용 최적화 | CFO | 주 1회 |
| **Compliance Agent** | 규제 준수, 감사, 보안 인증 | Steering | 주 1회 |
| **Support Agent** | 고객 지원, 이슈 해결, 피드백 수집 | Operations Manager | 일일 |

#### **Data & Analytics (7)**

| Agent | 주요 책임 | 보고처 | Heartbeat |
|-------|----------|--------|-----------|
| **Data Architect** | 데이터 모델 설계, EDW 구축 방향 | CTO | 주 2회 |
| **Data Engineer (1)** | ETL/ELT 개발, 파이프라인 구축 | Data Architect | 일일 |
| **Data Engineer (2)** | 빅데이터 플랫폼 (Spark, Airflow) | Data Architect | 일일 |
| **Analytics Agent** | 리포팅, BI 대시보드, 분석 | Data Architect | 주 1회 |
| **Metadata Agent** | 메타데이터 관리, 용어사전 | Data Architect | 주 1회 |
| **RBAC Agent** | 역할 기반 접근 제어, 데이터 경계 | Security + CIO | 주 1회 |
| **Data Quality Agent** | 데이터 검증, 품질 모니터링 | Data Architect | 주 1회 |

#### **Business Development (6)**

| Agent | 주요 책임 | 보고처 | Heartbeat |
|-------|----------|--------|-----------|
| **Product Manager** | 제품 로드맵, 기능 정의, 우선순위 | CPO | 주 1회 |
| **Business Analyst (1)** | 요구사항 분석, 프로세스 설계 | Product Manager | 주 2회 |
| **Business Analyst (2)** | 기존 시스템 (TOC) 통합 분석 | Product Manager | 주 2회 |
| **QA Agent** | 테스트 계획, 테스트 자동화, 품질 보증 | Product Manager | 일일 |
| **User Research Agent** | 사용자 조사, UX 피드백, 개선안 | Product Manager | 주 1회 |
| **Partnership Agent** | 외부 파트너 관리 (TnG, JPJ) | Business Development | 주 1회 |

### 5.3 Agent 기본 정보 (29개 전체)

**Template:**
```
Name: [Agent Name]
Department: [Bureau]
Reporting To: [Manager]
Heartbeat: [주기]
Budget: [월별 토큰 예산]
Skills: [기술 영역]
Capabilities: [주요 기능]
Job Description: [역할 설명]
```

**예시 (CEO Agent):**
```
Name: CEO Agent
Department: Executive Board
Reporting To: Steering Committee
Heartbeat: Daily (9:00 AM)
Budget: 50K tokens/month
Skills: Strategic Planning, Decision Making, Board Management
Capabilities: 
  - 전략 수립 및 Board 의사결정
  - 주요 리스크 & 기회 식별
  - 이해관계자 관리
  - CEO 업무 위임 (비상 상황)
Job Description: |
  최고경영자 역할을 대행하는 Agent.
  주요 의사결정 추진, 리스크 에스컬레이션,
  Board 회의 준비 및 기록 관리 담당.
  Steering Committee 의장이 최종 승인.
```

---

## 6. 의사결정 권한 (Authority Matrix)

### 6.1 Board 결정사항 (CEO/Steering 스코프)

| 항목 | 승인자 | 예 | SLA | 에스컬레이션 |
|------|--------|-----|-----|----------|
| **기술 아키텍처** | CTO + Board | AWS/GCP, DB, API 설계 | 1주 | CEO |
| **예산 변경 (>10%)** | CFO + CEO | 인력, 클라우드, 라이선스 | 2주 | Board |
| **외부 파트너** | CEO + Steering | 클라우드, 결제사, 통신사 | 3주 | Board |
| **마일스톤 승인** | PMO + CTO | Phase 완료, 릴리스 | 3일 | CEO |
| **위험 이슈** | Steering | Critical/High 위험 | 24시간 | Board |
| **규제 변경** | Legal + CEO | 정부 지침 반영, 컴플라이언스 | 1주 | CEO |
| **인력 변경** | COO + CEO | 팀 구성, 조직 개편 | 1주 | CEO |

### 6.2 CTO/CIO 스코프 (위임 권한)

**CTO는 다음 권한을 직접 행사 가능:**
- 기술 표준 선택 (프로그래밍 언어, 프레임워크)
- DevOps 파이프라인 구축
- Agent 조직화 및 역할 배정
- 성능 목표 설정 (TPS, 응답시간, 가용성)
- 기술 리뷰 및 승인 (코드, 아키텍처)

**CIO는 다음 권한을 직접 행사 가능:**
- 데이터 정책 수립 (접근 제어, 암호화)
- 보안 표준 선택 (인증, 인가, 감사)
- 운영 프로세스 정의 (모니터링, 알림, SLA)
- 시스템 유지보수 일정 결정
- 인프라 용량 계획

### 6.3 대리인 권한 (Delegation)

**CEO가 부재 중 시:**
- CTO → 기술 의사결정 권한
- COO → 운영/인력 의사결정 권한
- CFO → 재정 의사결정 권한

**Board Approval이 필요한 경우:**
- 2인 이상의 C-Level이 공동 결정

---

## 7. 보고 및 Heartbeat 일정

### 7.1 보고 주기

| 주기 | 담당자 | 대상 | 주요 항목 |
|------|--------|------|---------|
| **일일** | Operations Manager | CTO/COO | 빌드 상태, 배포 현황, 이슈 |
| **주 2회** | Architecture Agent | CTO | 설계 리뷰, 기술 부채 추적 |
| **주 1회** | Team Leads | CTO/COO | 진행도, 리스크, 성과 |
| **주 1회** | CTO/COO | CEO | 기술/운영 요약, 결정사항 |
| **월 1회** | CEO | Board | 월간 성과, 위험 평가, 예산 현황 |
| **분기** | Steering | HiPass Authority | 분기 보고서, 규제 준수 현황 |

### 7.2 Heartbeat 스케줄 (일일 & 주간)

**일일 Heartbeat (9:00 AM)**
```
참석: CEO Agent, CTO Agent, Operations Manager Agent, PM Agent
소요: 15분
내용: 
  - 어제 진행도 및 이슈 (3분)
  - 오늘 목표 (3분)
  - 차단 항목 (3분)
  - 의사결정 필요 항목 (3분)
  - 다음 미팅 안내 (3분)
```

**주간 Heartbeat (수요일 10:00 AM)**
```
참석: Steering Committee (CEO, CTO, CPO, CIO, COO)
소요: 60분
내용:
  - 주간 성과 요약 (10분)
  - 기술 & 운영 리뷰 (20분)
  - 리스크 & 이슈 (15분)
  - 다음 주 계획 (10분)
  - 보드 공고 & 결정사항 (5분)
```

---

## 8. G-HARD 의사결정 게이트 (참고)

**G-HARD Score**: Governance(0-2) + Headcount(0-2) + Architecture(0-2) + Risk(0-2) + Dependency(0-2) = 0-10

자세한 내용은 `05_governance/02_board_decisions.md` 참조.

| G-HARD 점수 | 상태 | 행동 |
|-------------|------|------|
| **0** | Green | 즉시 승인 가능 (CEO 결정) |
| **1-3** | Yellow | Board 검토 필요 (1주 SLA) |
| **4-6** | Orange | 심화 검토 필요 (2주 SLA, 위험 감소 필요) |
| **7-10** | Red | 심각한 우려 (Board 결정 보류, 재계획 필요) |

---

## 9. 조직 변경 관리

### 9.1 인력 추가/변경 프로세스

```
1. 신청 (Staffing Request)
   └─ COO Agent 제출 → CEO 검토 (3일)

2. 예산 검증 (Budget Review)
   └─ Finance Agent → CFO 승인 (3일)

3. 공개 채용 또는 재배치
   └─ HR Agent 처리 (2주)

4. 온보딩 및 권한 부여
   └─ Operations Manager 처리 (3일)

5. 보고 (Monthly Report)
   └─ CEO → Board (매월 1일)
```

### 9.2 Agent 역할 변경

모든 Agent 역할 변경은 **CTO + CEO** 합의로 진행.

변경 항목:
- Agent 이름 또는 제목
- 보고처 변경
- 책임 범위 확대/축소
- Heartbeat 주기 변경

---

## 10. 권한 침해 및 이슈 처리

### 10.1 권한 침해 시나리오

| 시나리오 | 원인 | 대응 |
|---------|------|------|
| Toll Manager가 다른 Plaza 데이터 조회 | 시스템 오류 또는 악의 | 즉시 BOS 접근 차단, 조사, 재권한 부여 |
| Finance Agent가 결제 승인 없이 거래 입력 | 권한 범위 오해 | 거래 롤백, 재교육, 권한 재확인 |
| Agent가 할당된 권한 범위 초과 사용 | 시스템 버그 | 로그 분석, CEO 보고, 권한 재설정 |

### 10.2 이슈 에스컬레이션 경로

```
Detected Issue (발견)
    ↓
Team Lead (1차 판단) — 1시간
    ↓
CTO/CIO (2차 판단) — 4시간
    ↓
CEO (3차 판단) — 8시간
    ↓
Steering Committee (4차 판단) — 24시간
    ↓
Board (최종) — 48시간 (Critical만)
```

---

## 11. 권한 모니터링 및 감시

### 11.1 월간 권한 감사

**감사 항목:**
- 새로 부여된 권한 목록
- 삭제된 권한 목록
- 권한 남용 의심 거래
- 권한 범위 외 접근 시도

**담당:** Compliance Agent + RBAC Agent

**보고:** 월 1회 (CEO → Board)

### 11.2 분기별 권한 재검증

모든 사용자/Agent의 권한을 재검증하고 필요 시 조정.

**프로세스:**
1. RBAC Agent가 현재 권한 목록 추출
2. 각 Department Head가 권한 확인
3. 부정확한 권한 업데이트
4. Compliance Agent 최종 승인

---

## 12. 참고 문서

### 12.1 관련 문서
- `01_project_charter.md` — 프로젝트 목적, JVC 구조, 성공 기준
- `02_market_malaysia.md` — 말레이시아 시장 & 경쟁 환경
- `03_domain_tolling.md` — 통행료 징수 도메인, 기존 체계
- `05_payment_architecture.md` — 결제 구조, Channel A/B
- `05_governance/01_decision_gates.md` — G-HARD 의사결정 게이트
- `05_governance/02_board_decisions.md` — Board 결정사항 21개
- `05_governance/04_supplement_items.md` — 18개 보충 항목

### 12.2 참고 표준
- **ISO 27001**: 정보 보안 관리
- **PCI-DSS**: 결제 카드 산업 보안
- **PDPA (Malaysia)**: 개인정보보호법
- **MLFF Board**: 규제 기준 (HiPass Authority)

---

## 13. 승인 및 서명

**이 문서는 다음 조건에서 유효합니다:**

- [ ] Steering Committee 승인 (Full Board)
- [ ] CTO 기술 검토 및 동의
- [ ] CIO 운영 검토 및 동의
- [ ] Legal/Compliance 규제 검토

**서명:**

| 역할 | 이름 | 서명 | 날짜 |
|------|------|------|------|
| CEO | _______________ | _______ | __/__/2026 |
| CTO | _______________ | _______ | __/__/2026 |
| COO | _______________ | _______ | __/__/2026 |
| Compliance | _______________ | _______ | __/__/2026 |

---

## 14. 문서 이력

| 버전 | 날짜 | 변경 사항 | 담당자 |
|------|------|---------|--------|
| 1.0 | 2026-04-01 | 초판 작성 | Project Team |
| - | - | - | - |

---

**Document Status**: Draft → Board Review → Approval → Implementation

**Next Review**: 2026-04-15 (Steering Committee)

**Last Updated**: 2026-04-01

**관련 링크:**
- Project Master: `00_MASTER.md`
- 조직도 상세: Paperclip 29개 Agent 목록 (별도 문서)
- 의사결정 기준: G-HARD Score 계산 방식 (`05_governance/01_decision_gates.md`)
