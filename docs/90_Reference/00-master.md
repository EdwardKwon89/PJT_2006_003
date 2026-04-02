# Malaysia SLFF·MLFF Tolling BOS
# 프로젝트 마스터 문서 (종합 개요)
## 00_MASTER.md | v1.0 | 2026-04

---

> **AI Agent 사용 지침**
> 이 문서는 프로젝트 전체 지도입니다.
> 모든 Agent는 작업 시작 전 이 문서를 먼저 읽으십시오.
> 세부 내용은 각 섹션의 참조 문서를 로드하십시오.

---

## 1. 프로젝트 한 줄 정의

> 한국 HiPass ETCS를 기준 모델로 삼아, 말레이시아 RFID/ANPR 기반
> SLFF·MLFF Tolling Back Office System을 AI Agent로 구축하고,
> 통행료의 3~12%를 수수료로 수취하는 JVC 사업 모델로 운영한다.

---

## 2. 사업 구조 요약

```
JVC (우리 회사)
├── SLFF/MLFF 시스템 구축·운영
├── 통행료 3~12% 수수료 수취
└── Toll Plaza·Toll Center 직접 운영

Clearing Center (독립 기관)
├── 지불 매체 발행·판매·충전
├── 결제 처리 및 정산
└── 수수료 차감 후 TOC 지급

유료도로 운영사 TOC
├── 설치 공간 제공
├── 통행료 수령 (Clearing Center로부터)
└── API/MCP로 데이터 조회 (읽기 전용)
```

→ 상세: `01_business/01_project_charter.md`

---

## 3. 시스템 구성 요약

```
Layer 1: Operations Web / App Application
  - BOS Admin Web (React, BM/EN)
  - 현장 Mobile App (React Native)
  - Text-to-SQL, 업무 판단 AI, 스마트 커스터마이징

Layer 2: Communication Application
  - RFID/ANPR 이벤트 수신 (gRPC + Kafka)
  - 외부 연동 (JPJ·TnG·FPX·ANPR)
  - External API & BOS MCP Server (TOC 연계)
  - AI 장애 탐지·자동 복구

Layer 3: Big Data / Analytics Platform
  - Delta Lake + Spark + Airflow
  - 요금 시뮬레이션, 교통 빅데이터 분석
```

→ 상세: `02_system/01_system_overview.md`

---

## 4. 핵심 도메인 (10개)

| # | 도메인 | 참조 문서 |
|---|---|---|
| 1 | Transaction Processing | `02_system/02_service_domains.md` |
| 2 | Account & Vehicle | `02_system/02_service_domains.md` |
| 3 | Billing & Settlement | `02_system/02_service_domains.md` |
| 4 | Violation & Enforcement | `02_system/02_service_domains.md` |
| 5 | Paid/Unpaid Management | `02_system/02_service_domains.md` |
| 6 | Exemption & Discount | `02_system/02_service_domains.md` |
| 7 | Transaction Review | `02_system/02_service_domains.md` |
| 8 | Lane Equipment Monitoring | `02_system/02_service_domains.md` |
| 9 | Reporting & Analytics | `02_system/02_service_domains.md` |
| 10 | External API & MCP | `02_system/06_api_mcp_spec.md` |

---

## 5. 결제 구조 핵심 (최종 확정)

```
Channel A: JVC/Clearing 발행 RFID or ANPR 등록 계좌
  → Clearing Center Account 과금
  → 미납 시: JPJ 조회 → 통지서 → 수납

Channel B: TnG 발행 RFID
  → TnG 정산 요청 → TnG→JVC 정기 입금
  → TnG 미납: 별도 프로세스 (현지 RnR 정의 후)

수납 합계 → JVC 수수료 차감 → TOC 지급
```

→ 상세: `01_business/05_payment_architecture.md`

---

## 6. 개발 환경 요약

| 도구 | 역할 |
|---|---|
| VS Code + Claude Code | IDE + 코드 생성 |
| GSD | Phase 기반 개발 관리 |
| Paperclip | AI Agent 조직 운영 |
| cmux | 멀티 터미널 환경 |
| Gemini Antigravity | Phase 7+ 병행 검토 |

→ 상세: `04_dev/01_toolchain.md`

---

## 7. Paperclip 조직 요약 (29개 Agent)

```
Board (나) — 이사회
└── CEO [Opus]
    ├── CTO [Opus] → Data Gov / App / Backend / AI / Infra
    ├── CPO [Sonnet] → UX Designer
    ├── CIO [Opus] → Innovation Planner / BigData SvcDesigner
    ├── PM [Sonnet] → QA Lead / Performance
    └── Compliance [Flash-Lite]
```

→ 상세: `04_dev/02_paperclip_org.md`
→ Agent별 설정: `04_dev/03_agent_roles.md`

---

## 8. 개발 Phase 요약 (12개월)

| Phase | 내용 | 기간 |
|---|---|---|
| 1 | 공통 인프라 | M1~M2 |
| 2 | 통신 Application | M2~M3 |
| 3 | Transaction Engine | M3~M4 |
| 4 | Account 관리 | M4~M5 |
| 5 | Billing & 정산 | M5~M6 |
| 6 | 위반·심사 | M6~M7 |
| 7 | 장비 모니터링 | M7~M8 |
| 8 | 빅데이터 플랫폼 | M8~M9 |
| 9 | AI 고도화 | M9~M10 |
| 10 | Web·Mobile App | M10~M11 |
| 11 | API·MCP·통합테스트 | M11~M12 |
| 12 | 운영 이관 | M12 |

→ 전체 일정: `06_phases/00_phase_overview.md`
→ Phase별 상세: `06_phases/0X_phaseXX_*.md`

---

## 9. 의사결정 게이트 요약

| 게이트 | 시점 | 핵심 결정 |
|---|---|---|
| G-HARD 0 | 착수 전 | 전략·수수료·법인 구조 |
| G-HARD 1 | M1 2~3주 | 요구사항 전체 확정 |
| G-HARD 2 | M2 1~2주 | 업무 프로세스 확정 |
| G-HARD 3 | M2 말 | 기술 규약 확정 |
| G-HARD 4 | M3 | UI/UX 승인 |
| G-HARD 5 | M7~M8 | SLFF MVP 검수 |
| G-HARD 6 | M9 | MLFF 확장 승인 |
| G-HARD 7 | M12 | 혁신 서비스 사업화 |

→ 상세: `05_governance/01_decision_gates.md`
→ Board 결정 목록: `05_governance/02_board_decisions.md`

---

## 10. 18개 보완 항목 요약

| 시점 | 항목 | 담당 | 참조 |
|---|---|---|---|
| Week 1~2 | 수주·영업 전략 | CEO + CIO | §13 |
| Week 1~2 | Mock 테스트 환경 | DevOps + Comm | §13 |
| Week 1~2 | 수수료 구조 & BEP | CIO + Innovation | §13 |
| Week 1~2 | 법적 계약 구조 | Compliance + Board | §13 |
| G-HARD 1 전 | 결제 실패 시나리오 | TXN + Billing | §13 |
| G-HARD 1 전 | AI 결정 책임 기준 | Compliance + AI Lead | §13 |
| G-HARD 1 전 | ANPR 이미지 보존 | Compliance + DA | §13 |
| G-HARD 3 전 | DR/BCP 설계 | DevOps + Security | §13 |
| G-HARD 3 전 | API 버전 관리 | CTO + Backend | §13 |
| G-HARD 3 전 | 보안 인증 로드맵 | Security + Compliance | §13 |
| G-HARD 3 전 | 오픈소스 라이선스 | Security + DevOps | §13 |
| Phase 중 | 데이터 마이그레이션 | DA + DBA + DevOps | §13 |
| Phase 중 | Agent 충돌 방지 | PM + CEO | §13 |
| Phase 중 | 코드 품질 기준 | CTO + QA | §13 |
| Phase 중 | 변경 관리 프로세스 | PM + CTO | §13 |
| Phase 8 후 | 고객 지원 체계 | CPO + PM | §13 |
| Phase 8 후 | 운영팀 전환 계획 | CEO + PM + CPO | §13 |
| Phase 8 후 | 혁신 서비스 수익화 | CIO + Innovation | §13 |

→ 상세: `05_governance/04_supplement_items.md`

---

## 11. Skills 파일 목록 (21개)

→ 전체 목록 및 용도: `04_dev/04_skills_index.md`
→ Skills 파일 본문: `07_skills/*/SKILL.md`

---

## 12. 타겟 국가 확장 계획

| 국가 | 시기 | 비고 |
|---|---|---|
| 말레이시아 | 2026~2027 | 1순위 MVP |
| 우즈베키스탄 | 2027~2028 | BOS 재사용 |
| 필리핀 | 2027~2028 | BOS 재사용 |
| 브라질 | 2028~ | BOS 재사용 |

→ 확장 전략: `01_business/02_market_malaysia.md` §확장 섹션

---

## 13. 문서 최신화 규칙

```
- 이 마스터 문서는 섹션 요약만 포함 (상세 내용 없음)
- 각 하위 문서 변경 시 해당 파일만 수정
- 마스터 문서는 참조 링크와 요약만 업데이트
- 버전: v1.0 → 각 G-HARD 게이트 완료 시 버전 업
- 담당: DA Lead (문서 일관성 관리)
```
