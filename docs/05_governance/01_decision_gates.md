# G-HARD Decision Gates (Governance-0 to Governance-7)

**문서 버전**: 1.0  
**작성일**: 2026-04-01  
**상태**: Draft (Board Approval Pending)  
**담당자**: Project Steering Committee

---

## 1. Executive Summary

Malaysia SLFF/MLFF 프로젝트의 8단계 의사결정 게이트(Gate 0~7)를 정의한다. **G-HARD Score (Governance, Headcount, Architecture, Risk, Dependency)** 기반으로 각 게이트별 의사결정 항목, Board 책임, 산출물, 일정을 명시한다.

**핵심 원칙:**
- Gate 0-2 (Green): CEO 또는 CTO 사인으로 즉시 진행 가능
- Gate 3-5 (Yellow): Steering Committee 검토 필수 (1주 SLA)
- Gate 6-7 (Red): Board 심화 검토 및 재계획 필요 (2주 이상)

---

## 2. G-HARD 점수 정의

### 2.1 점수 산정 방식

```
G-HARD Score = Governance(0-2) + Headcount(0-2) + Architecture(0-2) + Risk(0-2) + Dependency(0-2)
범위: 0-10 (점수 낮을수록 위험 낮음)
```

### 2.2 각 항목별 점수 기준

#### Governance (거버넌스 준비도)
| 점수 | 기준 | 예시 |
|------|------|------|
| **0** | 완벽한 거버넌스 구조 | 조직도 확정, 역할 명확, RACI 매트릭스 완성 |
| **1** | 기본 거버넌스 수립 | 주요 역할 정의, 보고 체계 구성 |
| **2** | 거버넌스 미흡 | 역할 모호, 결정 구조 불명확 |

#### Headcount (인력 준비도)
| 점수 | 기준 | 예시 |
|------|------|------|
| **0** | 팀 완전 구성 | 필요 인력 100% 확보, 온보딩 완료 |
| **1** | 팀 부분 구성 | 필요 인력 70-99% 확보, 채용 진행 중 |
| **2** | 팀 미구성 | 필요 인력 <70%, 채용 미시작 |

#### Architecture (기술 아키텍처)
| 점수 | 기준 | 예시 |
|------|------|------|
| **0** | 아키텍처 확정 | 설계 문서 완성, 기술 선택 최종화, PoC 검증 |
| **1** | 아키텍처 기본 수립 | 개념 설계, 주요 기술 선택 중 |
| **2** | 아키텍처 미정 | 설계 초기 단계, 기술 선택 미완료 |

#### Risk (위험 평가)
| 점수 | 기준 | 예시 |
|------|------|------|
| **0** | 위험 최소화 | Critical/High 위험 0개, 미티게이션 계획 수립 |
| **1** | 위험 중등도 | Critical 위험 0개, High 위험 1-2개 |
| **2** | 위험 높음 | Critical 위험 1개 이상, High 위험 3개 이상 |

#### Dependency (외부 의존도)
| 점수 | 기준 | 예시 |
|------|------|------|
| **0** | 의존도 낮음 | 내부 리소스로 진행 가능, 외부 승인 불필요 |
| **1** | 의존도 중간 | 1-2개 외부 승인 필요, 타이밍 명확 |
| **2** | 의존도 높음 | 3개 이상 외부 의존, 진행 불확실성 높음 |

---

## 3. Decision Gates (8단계)

### Gate 0: Discovery & Planning (Month 1 ~ Week 3)

**목표**: 프로젝트 전체 범위 확정 및 마스터 계획 수립

**의사결정 항목** (총 5개):
1. 프로젝트 헌장 (Project Charter) 승인
2. JVC 구조 및 역할 정의 확정
3. 마스터 일정 및 마일스톤 수립
4. 초기 예산 및 자금 배분 승인
5. 규제 검토 로드맵 확정

**Board 책임**:
- [ ] Executive Sponsor: Charter 최종 검토 및 서명
- [ ] Steering Committee: 범위 및 일정 검증
- [ ] CFO: 초기 예산 승인

**산출물**:
- Project Charter v1.0
- Project Master Plan (WBS, 일정, 예산)
- Stakeholder Communication Plan
- Governance Structure RACI Matrix
- Risk Register (초기 20개 항목)

**일정**:
- 시작: 2026-04-01
- 완료 SLA: 2026-04-20 (3주)
- Gate Review: 2026-04-21 (월요일)
- 승인자 사인오프: CEO + CTO + CFO

**G-HARD 점수 기준**: Yellow (3-4) 예상
- Governance: 1 (조직도 수립 중)
- Headcount: 2 (팀 구성 미시작)
- Architecture: 2 (초기 검토 단계)
- Risk: 1 (초기 위험 식별)
- Dependency: 2 (정부 승인 대기)

---

### Gate 1: Technical Architecture Review (Week 4 ~ Week 6)

**목표**: 기술 아키텍처 최종 확정 및 기술 검증

**의사결정 항목** (총 6개):
1. Cloud 인프라 선정 (AWS/GCP) 및 비용 승인
2. 데이터베이스 아키텍처 (RDBMS, Cache, Analytics) 확정
3. 마이크로서비스 설계 및 API 스펙 승인
4. 보안 아키텍처 (PCI-DSS, ISO 27001) 확정
5. DevOps/CI-CD 파이프라인 설계 승인
6. PoC (Proof of Concept) 결과 검증

**Board 책임**:
- [ ] CTO: 아키텍처 기술 검증 및 승인
- [ ] Steering Committee: 아키텍처 리스크 평가
- [ ] Security Lead: 보안 설계 최종 검토

**산출물**:
- Technical Architecture Document v1.0
- System Design Diagram (C4 Model)
- Technology Stack Decision Matrix
- Security Architecture Design (NIST, PCI-DSS)
- DevOps Pipeline Design
- PoC Report & Validation Results

**일정**:
- 시작: 2026-04-22
- 완료 SLA: 2026-05-06 (2주)
- Gate Review: 2026-05-06 (화요일 Steering 정례)
- 승인자 사인오프: CTO + Security Lead

**G-HARD 점수 기준**: Green (2-3)
- Governance: 1 (기본 구조 확정)
- Headcount: 2 (기술 리드 배치, 팀 구성 진행 중)
- Architecture: 0 (아키텍처 확정)
- Risk: 1 (기술 위험 미티게이션 계획 수립)
- Dependency: 1 (Cloud 파트너 선정 진행)

---

### Gate 2: Team & Resource Allocation (Week 7 ~ Week 9)

**목표**: 개발팀 구성 완료 및 리소스 배분 확정

**의사결정 항목** (총 5개):
1. 개발팀 구성 확정 (12-15 FTE, 각 역할 인력)
2. 외부 파트너 선정 (Cloud, 결제 게이트웨이, QA)
3. Training & On-boarding Program 확정
4. 팀 보상 및 인센티브 구조 승인
5. 리소스 배분 계획 및 예산 조정

**Board 책임**:
- [ ] COO: 조직 구성 및 채용 계획 승인
- [ ] CFO: 인력 예산 및 파트너 비용 검토
- [ ] HR Lead: 채용 및 온보딩 계획 승인

**산출물**:
- Org Chart & RACI Matrix v1.0
- Team Staffing Plan (Role, Skills, Timeline)
- Partner Selection & Contract Summary
- Training & On-boarding Schedule
- Budget Revision v1.1 (인력 + 파트너 비용)
- Resource Allocation Plan (월별)

**일정**:
- 시작: 2026-05-07
- 완료 SLA: 2026-05-27 (3주)
- Gate Review: 2026-05-27 (화요일 Steering 정례)
- 승인자 사인오프: COO + CFO

**G-HARD 점수 기준**: Yellow (3-4)
- Governance: 0 (조직도 최종 확정)
- Headcount: 1 (인력 70-90% 확보)
- Architecture: 0 (아키텍처 확정)
- Risk: 1 (인력 배치 리스크)
- Dependency: 1 (파트너 협력 조건)

---

### Gate 3: Development Sprint Planning (Week 10 ~ Week 12)

**목표**: 개발 스프린트 계획 수립 및 MVP 정의 확정

**의사결정 항목** (총 6개):
1. 제품 로드맵 (MVP, Phase 1-3) 확정
2. Sprint Backlog 우선순위 결정
3. 품질 기준 (Coverage >85%, SLA 99.9%) 승인
4. 테스트 전략 (Unit, Integration, E2E) 확정
5. 배포 전략 및 Rollback Plan 수립
6. 모니터링 & 알림 기준 (SLA, 성능) 정의

**Board 책임**:
- [ ] Product Manager: 로드맵 및 우선순위 승인
- [ ] QA Lead: 품질 기준 및 테스트 전략 검증
- [ ] DevOps Lead: 배포 및 모니터링 계획 승인

**산출물**:
- Product Roadmap v1.0 (MVP + Phase 1-3)
- Detailed Sprint Plan (Sprint 1-6, 각 2주)
- Definition of Done & Acceptance Criteria
- Test Strategy & Automation Framework
- Deployment Plan & Rollback Procedures
- Monitoring & Alerting Configuration

**일정**:
- 시작: 2026-05-28
- 완료 SLA: 2026-06-17 (3주)
- Gate Review: 2026-06-17 (화요일 Steering 정례)
- 승인자 사인오프: Product Manager + QA Lead

**G-HARD 점수 기준**: Green (2-3)
- Governance: 1 (의사결정 프로세스 확정)
- Headcount: 0 (팀 완전 구성 및 온보딩 완료)
- Architecture: 0 (아키텍처 확정, 구현 시작)
- Risk: 1 (개발 리스크 미티게이션 계획)
- Dependency: 1 (정부 협의 진행 중)

---

### Gate 4: MVP Development Completion (Week 13 ~ Week 24)

**목표**: MVP 개발 완료 및 Internal Acceptance Test 통과

**의사결정 항목** (총 6개):
1. 핵심 기능 개발 완료 (Transaction, Settlement, BOS)
2. API 구현 및 통합 테스트 완료
3. 보안 패치 적용 및 Pen Testing 결과 검증
4. 성능 최적화 (TPS 100K 목표 달성) 검증
5. 데이터 마이그레이션 계획 최종화
6. UAT 시나리오 및 테스트 케이스 확정

**Board 책임**:
- [ ] CTO: 개발 완료도 및 기술 검증
- [ ] QA Lead: 테스트 결과 및 품질 승인
- [ ] Security Lead: 보안 테스트 및 컴플라이언스 검증

**산출물**:
- MVP Source Code v1.0 (Git Repository)
- API Documentation & Swagger Spec
- Test Coverage Report (Target >85%)
- Security Assessment Report & Remediation Plan
- Performance Test Report (100K TPS, <200ms p95)
- Data Migration Scripts & Validation Plan
- UAT Scenario & Test Case Matrix

**일정**:
- 시작: 2026-06-18
- 완료 SLA: 2026-09-09 (12주)
- Gate Review: 2026-09-09 (화요일 Steering 정례)
- 승인자 사인오프: CTO + QA Lead + Security Lead

**G-HARD 점수 기준**: Green (2-3)
- Governance: 0 (거버넌스 정상 운영)
- Headcount: 0 (팀 완전 구성)
- Architecture: 0 (설계 준수 확인)
- Risk: 1 (개발 리스크 관리 중)
- Dependency: 1 (정부 협의 진행)

---

### Gate 5: Beta Testing & Pilot Deployment (Week 25 ~ Week 35)

**목표**: Beta 테스트 완료 및 Pilot 거래 성공 검증

**의사결정 항목** (총 6개):
1. Beta 테스트 결과 분석 및 버그 수정
2. 실 거래 Pilot (100K~500K 거래/일) 성공 검증
3. User Feedback 수집 및 개선사항 반영
4. SLA 99.9% 달성 검증 (7일 연속 운영)
5. 규제 컴플라이언스 최종 검증 (PCI-DSS, PDPA)
6. Go-Live Readiness Checklist 완성

**Board 책임**:
- [ ] Product Manager: Beta 피드백 및 개선안 승인
- [ ] Operations Lead: SLA 달성 검증
- [ ] Compliance Officer: 규제 준수 최종 승인

**산출물**:
- Beta Test Report & Bug Fix Log
- Pilot Operation Result (거래수, 성공율, 응답시간)
- User Feedback Summary & Improvement List
- SLA Compliance Report (99.9% 달성 증명)
- Compliance Checklist & Certification
- Go-Live Readiness Checklist (Green)
- Contingency & Rollback Plan

**일정**:
- 시작: 2026-09-10
- 완료 SLA: 2026-11-10 (9주)
- Gate Review: 2026-11-10 (화요일 Steering 정례)
- 승인자 사인오프: Product Manager + Operations Lead + Compliance Officer

**G-HARD 점수 기준**: Green (2-3)
- Governance: 0 (거버넌스 정상 운영)
- Headcount: 0 (팀 완전 구성)
- Architecture: 0 (아키텍처 검증 완료)
- Risk: 0 (Critical/High 위험 해소)
- Dependency: 1 (정부 최종 승인 대기)

---

### Gate 6: Go-Live Preparation & Final Approval (Week 36 ~ Week 40)

**목표**: Go-Live 최종 준비 완료 및 Board 최종 승인

**의사결정 항목** (총 5개):
1. 모든 Gate 5 산출물 최종 검증
2. Support Team & On-call Schedule 확정
3. User Communication & Training Material 최종 확인
4. Disaster Recovery & Backup Plan 테스트 완료
5. Board 최종 승인 (Go-Live 고고/노고 결정)

**Board 책임**:
- [ ] Executive Sponsor: Go-Live 최종 승인
- [ ] Steering Committee: 위험 & 준비도 최종 검증
- [ ] Operations Lead: 운영 준비 완료 확인

**산출물**:
- Gate 5 산출물 최종 검증 리포트
- Support & On-call Schedule (24/7 SLA)
- Training Material & User Guides
- DR/Backup Test Results & Procedures
- Change Log & Release Notes
- Board Approval Letter (Go-Live Authorization)

**일정**:
- 시작: 2026-11-11
- 완료 SLA: 2026-12-02 (3주)
- Gate Review: 2026-12-02 (화요일 Steering 정례)
- 승인자 사인오프: Executive Sponsor + Steering Committee

**G-HARD 점수 기준**: Green (1-2)
- Governance: 0 (완벽한 거버넌스)
- Headcount: 0 (팀 완전 구성)
- Architecture: 0 (아키텍처 검증 완료)
- Risk: 0 (Critical/High 위험 해소)
- Dependency: 1 (정부 최종 승인 대기)

---

### Gate 7: Post-Launch & Scale-Up (Week 41 onwards)

**목표**: 프로덕션 런칭 완료 및 확장 단계 시작

**의사결정 항목** (총 5개):
1. Go-Live 성공 검증 (거래량, 가용성, 응답시간)
2. 초기 이슈 해결 및 Hotfix 배포
3. 사용자 피드백 수집 및 개선 아이템 우선순위
4. Scale-Up Phase 1 계획 확정 (사용자 10배 증가)
5. 다음 Phase (P2, P3) 로드맵 업데이트

**Board 책임**:
- [ ] Operations Lead: 운영 안정화 검증
- [ ] Product Manager: 향후 로드맵 승인
- [ ] CEO: 비즈니스 성과 평가 및 확장 결정

**산출물**:
- Go-Live Success Report (거래수, SLA 달성도)
- Hotfix & Issue Resolution Log
- User Feedback & Feature Request Analysis
- Scale-Up Phase 1 Plan (12개월)
- Financial Performance Report (Revenue, Cost)
- Lessons Learned & Process Improvement Plan
- Next Phase Roadmap (P2, P3, 국가 확장)

**일정**:
- 시작: 2026-12-03 (Go-Live Day)
- 완료 SLA: 2027-01-31 (8주)
- Gate Review: 2027-01-31 (월간 리뷰)
- 승인자 사인오프: Operations Lead + Product Manager + CEO

**G-HARD 점수 기준**: Green (1-2)
- Governance: 0 (완벽한 거버넌스)
- Headcount: 0 (팀 완전 구성)
- Architecture: 0 (아키텍처 검증 완료)
- Risk: 0 (Critical/High 위험 해소)
- Dependency: 0 (모든 의존도 해소)

---

## 4. Gate Review 회의 체크리스트

### 4.1 Gate Review 전 (준비 3일 전)

- [ ] Gate 담당자가 산출물 완성도 검증 (100% 기준)
- [ ] G-HARD 점수 계산 및 Status (Green/Yellow/Red) 결정
- [ ] 위험 항목 식별 및 미티게이션 계획 수립
- [ ] Board Review Meeting 일정 공지 (승인자 최소 5인)

### 4.2 Gate Review 회의 (Steering Committee 정례 활용)

**회의 구성:**
- 의장: CEO 또는 Steering Committee Chair
- 참석: CTO, CPO, CIO, COO, Compliance Officer
- 보고자: Gate 담당 PM/Lead

**회의 진행 (30분):**
1. 산출물 프리젠테이션 (5분)
2. G-HARD 점수 검토 (5분)
3. 위험 & 이슈 토론 (10분)
4. Go/No-Go 결정 (5분)
5. Action Items & Next Steps (5분)

### 4.3 Gate Review 후 (승인 후 1일 내)

- [ ] 승인 문서 서명 (최소 3인: 의장 + 2명 이상)
- [ ] Go/No-Go 결정 통지 (모든 팀에 메일)
- [ ] No-Go 시: Remediation Plan 수립 (SLA 명시)
- [ ] Gate 기록 보관 (Project Master File)

---

## 5. G-HARD 상태별 행동 지침

| G-HARD 점수 | 상태 | SLA | 승인자 | 행동 |
|-------------|------|-----|--------|------|
| **0-1** | Green | 3일 이내 | CEO/CTO | 즉시 승인, 다음 단계 진행 |
| **2-3** | Green | 5일 이내 | Steering Cmte | 표준 Gate Review, 승인 |
| **4-5** | Yellow | 1주 | Steering Cmte | 심화 검토, 위험 감소 필요 |
| **6** | Orange | 2주 | Board | Escalation, 재계획 고려 |
| **7-10** | Red | 재계획 | Board | Go/No-Go 보류, 전체 재검토 |

---

## 6. No-Go 시나리오 및 대응

### 6.1 No-Go 발생 원인

| 시나리오 | G-HARD | 원인 | 대응 |
|---------|--------|------|------|
| **산출물 미완성** | 5-6 | 일정 지연 | 일정 조정, 스코프 축소 검토 |
| **심각한 버그** | 6-7 | 품질 이슈 | 버그 수정 후 재테스트 (1주) |
| **규제 거절** | 7-10 | 컴플라이언스 | 규제 기관 협의, 설계 수정 |
| **인력 부족** | 5-6 | 인력 배치 실패 | 채용 가속, 일정 연장 |

### 6.2 No-Go 재검토 프로세스

```
No-Go Decision
    ↓
Remediation Plan 수립 (2일)
    ↓
이슈 해결 및 재작업 (SLA: 1~2주)
    ↓
Gate 담당자 재검증 (1주)
    ↓
Board 재승인 (Gate Review 재개)
    ↓
Go Decision → 다음 단계 진행
```

---

## 7. 게이트별 일정 전체 요약

| Gate | 기간 | 시작 | 완료 | 소요 기간 |
|------|------|------|------|---------|
| **Gate 0** | Discovery | 2026-04-01 | 2026-04-21 | 3주 |
| **Gate 1** | Architecture | 2026-04-22 | 2026-05-06 | 2주 |
| **Gate 2** | Team & Resource | 2026-05-07 | 2026-05-27 | 3주 |
| **Gate 3** | Sprint Planning | 2026-05-28 | 2026-06-17 | 3주 |
| **Gate 4** | MVP Development | 2026-06-18 | 2026-09-09 | 12주 |
| **Gate 5** | Beta & Pilot | 2026-09-10 | 2026-11-10 | 9주 |
| **Gate 6** | Go-Live Prep | 2026-11-11 | 2026-12-02 | 3주 |
| **Gate 7** | Launch & Scale | 2026-12-03 | 2027-01-31 | 8주 |
| **TOTAL** | Project | 2026-04-01 | 2027-01-31 | **40주** |

---

## 8. 참고 문서

### 8.1 관련 게버넌스 문서
- `04_organization_roles.md` - 조직 역할 및 권한 정의
- `02_board_decisions.md` - Board 의사결정 항목 21개
- `03_decision_authority.md` - 의사결정 권한 매트릭스
- `04_supplement_items.md` - 보충 항목 18개

### 8.2 프로젝트 문서
- `01_business/01_project_charter.md` - 프로젝트 헌장
- `01_business/04_organization_roles.md` - 조직 구조

### 8.3 참고 표준
- **PRINCE2**: Project Management Best Practice
- **PMI PMBOK**: Gate Review Framework
- **ISO 27001**: 보안 거버넌스

---

## 9. 승인 및 서명

**이 문서는 다음 조건에서 유효합니다:**

- [ ] Steering Committee 검토 및 동의
- [ ] CTO 기술 검토 완료
- [ ] CFO 재정 검토 완료
- [ ] Legal/Compliance 규제 검토 완료

**승인자 서명:**

| 역할 | 이름 | 서명 | 날짜 |
|------|------|------|------|
| CEO (의장) | _______________ | _______ | __/__/2026 |
| CTO | _______________ | _______ | __/__/2026 |
| CFO | _______________ | _______ | __/__/2026 |
| Compliance Officer | _______________ | _______ | __/__/2026 |

---

## 10. 문서 이력

| 버전 | 날짜 | 변경 사항 | 담당자 |
|------|------|---------|--------|
| 1.0 | 2026-04-01 | 초판 작성 (Gate 0~7 정의) | Steering Cmte |
| - | - | - | - |

---

**Document Status**: Draft → Board Review → Approval → Implementation

**Next Review**: 2026-04-21 (Gate 0 Review)

**Last Updated**: 2026-04-01

**관련 링크:**
- Project Master: `00_MASTER.md`
- Gate Review 정례: 매주 수요일 10:00 AM (Steering Committee)
- G-HARD 계산기: Google Sheet (별도 배포)

