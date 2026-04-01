# Project Charter: HiPass ETCS 기반 SLFF/MLFF 구축

**문서 버전**: 1.0  
**작성일**: 2026-04-01  
**상태**: Draft (Board Approval Pending)  
**담당자**: Project Steering Committee

---

## 1. 프로젝트 개요

### 1.1 프로젝트명
**HiPass ETCS 기반 SLFF/MLFF(Single/Multi Lingkage Financial Framework) 구축**

### 1.2 프로젝트 목적
말레이시아의 HiPass 고속도로 전자요금징수(ETCS) 시스템을 기반으로 **SLFF(Single Lingkage Financial Framework)**와 **MLFF(Multi Lingkage Financial Framework)**를 구축하여, 아시아·태평양 지역의 모빌리티 및 결제 솔루션 시장에 진출합니다.

### 1.3 전략적 비전
- **즉시 목표**: 말레이시아 시장 안정화 (Year 1-2)
- **확장 목표**: 우즈벡 → 필리핀 → 브라질 순차 진출 (Year 3-5)
- **최종 목표**: 아시아·태평양 지역 교통·결제 표준 플랫폼 확립

---

## 2. 사업 모델

### 2.1 JVC (Joint Venture Concept) 구조
```
┌─────────────────────────────────────┐
│   HiPass Authority (말레이시아)      │
│   - 시스템 운영 권한                 │
│   - 기술 기반 제공                   │
└────────────┬────────────────────────┘
             │
      ┌──────┴──────┐
      │   합의 범위  │
      └──────┬──────┘
             │
┌────────────┴──────────────────────┐
│   Our Platform Company (신규)      │
│   - SLFF/MLFF 개발                 │
│   - BOS, Web/App 운영              │
│   - 기술 혁신 및 확장               │
└─────────────────────────────────────┘
```

### 2.2 수익 모델
**수수료 기반 (Fee-Based Revenue Model)**

| 항목 | 비율 | 설명 |
|------|------|------|
| 기본 운영 수수료 | 3~5% | 월별 거래액 기준 |
| 부가 기능 수수료 | 2~3% | Web/App 추가 서비스 |
| 데이터 라이센싱 | 1~2% | 분석 데이터 판매 |
| 기술 지원료 | 2~2% | 현지화, 커스터마이징 |
| **총 예상 수수료** | **3~12%** | 연간 거래액 기준 |

### 2.3 초기 투자 및 ROI
- **예상 초기 투자**: USD 2-3M (개발, 인프라, 현지화)
- **예상 손익분기점**: Year 2 중반
- **3년 누적 수익**: USD 5-8M (보수적 추정)
- **IRR**: 25-35% (기대값)

---

## 3. 프로젝트 범위 (Scope)

### 3.1 In-Scope (포함 영역)

#### A. 기술 인프라
- **BOS (Back-Office System)**: 결제, 정산, 보고 시스템
- **Core Platform**: SLFF/MLFF 엔진
- **Web Portal**: 관리자, 운영자용 대시보드
- **Mobile App**: iOS/Android 기반 사용자 앱
- **API Gateway**: 제3자 통합 인터페이스
- **Security & Compliance**: ISO 27001, PCI-DSS 준수

#### B. 지역별 현지화
- **말레이시아 Phase 1**: 말레이어, 영어 UI/UX
- **향후 국가**: 각국 통화, 규제 요건 반영

#### C. 운영 역량
- 기술 운영팀 구성 (DevOps, QA, Support)
- 24/7 모니터링 및 SLA 관리 (99.9% 가용성)
- 사용자 교육 및 온보딩 프로그램

#### D. 데이터 & 분석
- Real-time Transaction Analytics
- 사용자 행동 분석 및 리포팅
- 규제 보고서 자동화

### 3.2 Out-of-Scope (제외 영역)
- **기존 HiPass 고속도로 인프라 개선**: 기존 시스템은 별도 운영
- **카드 발급 및 은행 운영**: 제3자 금융기관 담당
- **물리적 하드웨어(게이트, 센서)**: 기관에서 제공
- **정부 정책 결정**: 정부 협의 기반 진행

### 3.3 경계선 (Boundary)
| 항목 | 책임 | 비고 |
|------|------|------|
| 결제 게이트웨이 | Platform + Partner Bank | 표준 통합 |
| 고객 지원 | Platform (1st/2nd Level) | 제3자 콜센터는 추후 |
| 법무/컴플라이언스 | 양사 공동 | 최종 책임은 기관 |
| 데이터 센터 | AWS/GCP (클라우드) | 현지 규정 준수 |

---

## 4. 지역 확장 계획

### 4.1 시장 확장 로드맵
```
Year 1-2: 말레이시아 (Malaysia)
├─ HiPass 안정화
├─ 기본 SLFF/MLFF 구축
├─ 사용자 1M+ 확보
└─ Revenue: USD 500K-1M

Year 2-3: 우즈벡 (Uzbekistan)
├─ 중앙아시아 진출
├─ 현지 규제 적응
├─ 파트너십 구성
└─ Revenue: USD 300K-500K

Year 3-4: 필리핀 (Philippines)
├─ 동남아 강화
├─ 다중 언어 지원 확대
├─ 사용자 2M+ 목표
└─ Revenue: USD 500K-800K

Year 4-5: 브라질 (Brazil)
├─ 남미 진출
├─ 글로벌 프레임워크 적용
├─ 사용자 3M+ 목표
└─ Revenue: USD 800K-1.5M

Year 5+: 글로벌 확장 및 파트너십
├─ 추가 시장 기회 평가
├─ 플랫폼 표준화 강화
└─ 전략적 M&A 검토
```

### 4.2 각 시장별 KPI
| 시장 | Year 1 | Year 2 | Year 3 | Year 5 |
|------|--------|--------|--------|--------|
| 말레이시아 | 100K | 500K | 800K | 1.2M |
| 우즈벡 | - | - | 50K | 300K |
| 필리핀 | - | - | 100K | 1M |
| 브라질 | - | - | - | 500K |
| **누계** | **100K** | **500K** | **950K** | **3M+** |

---

## 5. 성공 기준 (Success Criteria)

### 5.1 기술 성공 기준

| 지표 | 목표값 | 달성 기한 |
|------|---------|----------|
| 시스템 가용성 (Uptime) | 99.9% | Ongoing (SLA) |
| API 응답 시간 | <200ms (p95) | Go-Live |
| 거래 성공률 | >99.5% | Month 3 |
| 데이터 처리량 | 100K TPS (Throughput) | Year 1 Q4 |
| 보안 준수율 | 100% (PCI-DSS, ISO 27001) | Go-Live |
| 자동화 테스트 커버리지 | >85% | Month 6 |

### 5.2 사업 성공 기준

| 지표 | 목표값 | 달성 기한 |
|------|---------|----------|
| 활성 사용자(DAU) | 100K | Month 6 |
| 월간 거래액 | USD 10M+ | Month 12 |
| 고객 만족도 (NPS) | >60 | Month 9 |
| 수익 실현 | USD 500K | Month 12 |
| 손익분기점 | Year 2 Q2 | - |
| 시장 점유율(ETCS) | >20% | Year 3 |

### 5.3 시간 기준 (Timeline)

| Phase | 기간 | 주요 Milestone |
|-------|------|--------|
| **Discovery & Design** | Month 1-3 | 기술 아키텍처 확정, 규제 검토 완료 |
| **Development (MVP)** | Month 4-8 | Alpha Release, 내부 테스트 완료 |
| **Pilot & UAT** | Month 9-11 | Beta 운영, 실제 거래 테스트 (100K/day) |
| **Go-Live** | Month 12 | 프로덕션 런칭 |
| **Scale-Up** | Month 13-24 | 사용자/거래 10배 확대 |

---

## 6. 개발 방식 및 운영

### 6.1 개발 방법론
**AI-Agent 기반 Agile + GSD (Goal-Driven Software Development)**

```
┌──────────────────────────────────┐
│   Agent-Based Development        │
├──────────────────────────────────┤
│ 1. Code Generation Agent         │
│    └─ 기본 코드 생성 및 레이아웃 │
│                                  │
│ 2. Review Agent                  │
│    └─ 코드 품질, 보안 검증      │
│                                  │
│ 3. Test Agent                    │
│    └─ 자동 테스트 케이스 작성   │
│    └─ 테스트 실행 및 커버리지   │
│                                  │
│ 4. Architecture Agent            │
│    └─ 시스템 설계 및 최적화     │
│                                  │
│ 5. Documentation Agent           │
│    └─ API 문서, 운영 가이드     │
└──────────────────────────────────┘
         ↓
┌──────────────────────────────────┐
│   GSD + Paperclip Framework      │
├──────────────────────────────────┤
│ • Sprint-based Delivery (2주)     │
│ • Goal-first Planning            │
│ • Continuous Integration/Delivery │
│ • Real-time Monitoring           │
└──────────────────────────────────┘
```

### 6.2 개발 팀 구성
**Estimated Team Size: 12-15 FTE**

| 역할 | FTE | 책임 |
|------|-----|------|
| AI Agent 운영자 | 2 | Agent 지시, 품질 감시 |
| 아키텍트 | 1 | 기술 의사결정, 설계 |
| Full-Stack 개발자 | 6 | Backend, Frontend 구현 |
| QA/테스트 | 2 | 품질 보증, E2E 테스트 |
| DevOps/인프라 | 2 | 클라우드, 모니터링, 보안 |
| 프로젝트 관리 | 1 | 일정, 이해관계자 관리 |
| 기술 작성자 | 1 | 문서, API 스펙 |

### 6.3 Paperclip 통합 (추적 및 최적화)
```
┌─────────────────────────────────────┐
│   Paperclip: Metrics & Tracking     │
├─────────────────────────────────────┤
│ • Code Quality Metrics              │
│   └─ Cyclomatic Complexity          │
│   └─ Code Duplication               │
│   └─ Test Coverage (Target: >85%)   │
│                                     │
│ • Performance Metrics               │
│   └─ Build Time                     │
│   └─ Test Execution Time            │
│   └─ Deployment Duration            │
│                                     │
│ • Delivery Metrics                  │
│   └─ Sprint Velocity                │
│   └─ Defect Escape Rate             │
│   └─ Deployment Frequency           │
│                                     │
│ • Cost Metrics                      │
│   └─ AI Token Usage                 │
│   └─ Cloud Infrastructure Cost      │
│   └─ Team Resource Allocation       │
└─────────────────────────────────────┘
```

---

## 7. 거버넌스 및 승인

### 7.1 프로젝트 거버넌스 구조
```
┌─────────────────────────────────────────────┐
│   Steering Committee (정책 결정)             │
│   • HiPass CEO/COO                          │
│   • Our Platform CTO/CFO                    │
│   • 정부 담당자 대표                         │
└────────────────┬────────────────────────────┘
                 │
┌────────────────┴────────────────────────────┐
│   Project Management Office (PMO)           │
│   • Project Manager                         │
│   • Technical Lead                          │
│   • Finance/Business Manager                │
└────────────────┬────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───┴────┐  ┌───┴────┐  ┌──┴────┐
│ Dev    │  │ Ops    │  │ QA    │
│ Team   │  │ Team   │  │ Team  │
└────────┘  └────────┘  └───────┘
```

### 7.2 의사결정 프로세스

| 항목 | 승인자 | 필요 시점 | SLA |
|------|--------|----------|-----|
| 기술 아키텍처 | Steering + CTO | Month 2 | 1주 |
| 마일스톤 진행 | PMO + Steering | Monthly | 3일 |
| 예산 변경 (>10%) | CFO + Steering | As-needed | 2주 |
| 위험 이슈 | Steering | Immediately | 24시간 |
| 규제 변경 | Legal + Gov | As-needed | 1주 |

### 7.3 Board 승인 항목 (G-HARD = 0 기준)

**G-HARD**: Governance, Headcount, Architecture, Risk, Dependency 점수

#### 승인 필요 항목:
1. **기술 아키텍처** (Architecture)
   - Cloud 인프라 (AWS/GCP)
   - 데이터베이스 및 캐싱 전략
   - API 설계 및 보안 모델
   - DevOps/CI-CD 파이프라인

2. **팀 구성** (Headcount)
   - 개발팀 규모 (12-15 FTE)
   - 외부 파트너 선정 (클라우드, 결제사)
   - 학습/교육 예산

3. **위험 관리** (Risk)
   - 보안 위험 (PCI-DSS, 데이터 유출)
   - 운영 위험 (99.9% SLA 달성 능력)
   - 규제 위험 (국가별 컴플라이언스)
   - 시장 위험 (확장 성공 가능성)

4. **의존성 관리** (Dependency)
   - HiPass Authority 협력 수준
   - 규제 당국 승인 기한
   - 금융기관 파트너십 상태
   - 기술 표준 준수

#### G-HARD = 0 달성 기준:
- **Green Status**: 모든 항목이 문제없음
- **No Escalation**: 주요 이슈 미해결 상태 없음
- **Sign-off**: Steering Committee 100% 동의

---

## 8. 위험 및 대응 계획

### 8.1 주요 위험 (Top Risks)

| Risk | 영향 | 확률 | 대응 전략 |
|------|------|------|----------|
| 규제 지연 | High | Medium | 사전 협의, 법무 팀 강화 |
| 기술 복잡도 | High | Low | PoC, 아키텍트 리뷰 |
| 팀 역량 부족 | Medium | Medium | 채용 가속, 외부 컨설팅 |
| 시장 성장 부진 | High | Low | 다양한 파트너십, 마케팅 |
| 보안 인시던트 | Critical | Low | PII 암호화, Pen Testing, ISO 27001 |

### 8.2 위험 모니터링
- **월간 위험 평가**: PMO 주관
- **분기별 리뷰**: Steering Committee
- **실시간 추적**: Paperclip 대시보드

---

## 9. 재정 요약

### 9.1 예상 예산 (24개월)

| 항목 | 금액 (USD) | 비고 |
|------|-----------|------|
| 인력 비용 | 1,200K | 팀 12-15 FTE × 24개월 |
| 클라우드 인프라 | 300K | AWS/GCP 초기 + 운영 |
| 기술 라이선스 | 150K | DB, 보안, 개발 도구 |
| 외부 컨설팅 | 200K | 법무, 규제, 보안 |
| 마케팅/학습 | 150K | 유저 온보딩, 교육 |
| **총 예산** | **2,000K** | **USD 2M (보수적)** |

### 9.2 예상 수익 (Year 1-3)

| 연도 | 거래액 | 수수료율 | 수익 |
|------|--------|---------|------|
| Year 1 | USD 120M | 5% | USD 600K |
| Year 2 | USD 400M | 4.5% | USD 1.8M |
| Year 3 | USD 800M | 4% | USD 3.2M |

---

## 10. 주요 성공 요인 (Critical Success Factors)

1. **조기 HiPass Authority 승인**: Month 2 이내
2. **강력한 기술 리더십**: 경험 많은 아키텍트 확보
3. **규제 컴플라이언스**: PCI-DSS, ISO 27001 준수
4. **팀 안정성**: 초기 18개월 팀 이탈률 <10%
5. **AI Agent 효율성**: 개발 생산성 20-30% 개선
6. **사용자 만족도**: NPS >60 달성
7. **확장 가능한 아키텍처**: 10배 사용자 증가 대응

---

## 11. 승인 및 서명

**이 문서는 다음 조건에서 유효합니다:**

- [ ] Steering Committee 승인 (Full Board)
- [ ] 기술 검토 완료 (CTO/Architecture)
- [ ] 재정 검토 완료 (CFO)
- [ ] 법무/규제 검토 완료 (Legal)

**서명:**

| 역할 | 이름 | 서명 | 날짜 |
|------|------|------|------|
| Executive Sponsor | _______________ | _______ | __/__/2026 |
| Project Manager | _______________ | _______ | __/__/2026 |
| Technical Lead | _______________ | _______ | __/__/2026 |
| CFO/Finance | _______________ | _______ | __/__/2026 |

---

## 12. 참고 문서 및 부록

### 12.1 관련 문서
- `02_business_plan.md` - 상세 사업 계획서
- `03_market_analysis.md` - 지역별 시장 분석
- `04_technical_architecture.md` - 기술 아키텍처 설계
- `05_financial_model.md` - 상세 재정 모델

### 12.2 부록
- **부록 A**: HiPass ETCS 기존 시스템 개요
- **부록 B**: SLFF/MLFF 기술 스펙 (별도 문서)
- **부록 C**: 규제 요건 체크리스트
- **부록 D**: 팀 구성 및 채용 계획

---

**Document Status**: Draft → Board Review → Approval → Execution

**Next Review**: 2026-04-15 (Steering Committee)

**Last Updated**: 2026-04-01

---
