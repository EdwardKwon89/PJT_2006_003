# 프로젝트 헌장 (Project Charter)
## 01_business/01_project_charter.md
## v1.0 | 2026-04 | 참조: 00_MASTER.md

---
> **Agent 사용 지침**
> CEO·CIO·PM Agent가 G-HARD 0 준비 및 전략 수립 시 로드.
> 프로젝트의 Why·What·How를 정의하는 최상위 사업 문서.

---

## 1. 프로젝트 목적

한국의 성숙한 HiPass ETCS(전자통행료 수납시스템)를 기준 모델로 삼아 말레이시아 RFID/ANPR 기반 SLFF(Single Lane Free Flow)·MLFF(Multi-Lane Free Flow) Tolling Back Office System(BOS)을 구축한다. AI Agent 기반 개발 환경으로 속도와 품질을 동시에 확보하고, 말레이시아 수주를 출발점으로 글로벌 Tolling 솔루션 플랫폼으로 성장한다.

## 2. 사업 모델

### JVC(Joint Venture Company) 수익 구조

```
[수익 원천]
  SLFF/MLFF 통행료 수입의 3~12% 수수료 수취
  (협상 하한선: Board G-HARD 0에서 확정)

[투자 내용]
  SLFF/MLFF 시스템 구축 비용 전액 JVC 부담
  Toll Plaza·Toll Center 운영 인력 (JVC 소속)
  BOS 개발·운영 비용

[수익 흐름]
  통행료 전체 수납
    → Clearing Center 집계
    → JVC 수수료 차감
    → 유료도로 운영사(TOC) 지급
```

### 역할 분담

| 주체 | 역할 |
|---|---|
| JVC | 시스템 구축·운영·수수료 수취·Plaza·Center 직접 운영 |
| Clearing Center | 지불 매체 발행·결제 처리·정산·TOC 지급 |
| 유료도로 운영사(TOC) | 설치 공간 제공·통행료 수령·기존 시스템 자체 운영 |

## 3. 프로젝트 범위

### In-Scope (개발 대상)

```
1. BOS Web Application (운영 Admin, BM/EN)
2. 현장 Mobile Application (운영자·기술자)
3. Communication Application (RFID/ANPR 이벤트 처리)
4. Big Data / Analytics Platform
5. External API & BOS MCP Server (TOC 연계)
10개 서비스 도메인 전체 (→ 02_system/02_service_domains.md)
```

### Out-of-Scope (개발 제외)

```
- 유료도로 운영사 기존 Manual Tolling 시스템
- RFID·ANPR·LiDAR 등 현장 장비 자체
- TnG eWallet 내부 시스템
- JPJ 차량 등록 시스템 내부
- 기존 운영사 시스템 통합 (API 연계만 제공)
```

### MVP 범위 (SLFF 우선)

```
Phase 1~6 완료 = SLFF MVP
  Transaction Engine (Channel A/B)
  Account 관리 (Clearing Center 연동)
  Billing & 정산 (수수료·TOC 지급)
  위반·미납 관리
  이상 거래 심사
  면제·할인 처리

Phase 7~12 = MLFF 확장 + AI 고도화 + 빅데이터
```

## 4. 타겟 시장 및 확장 계획

| 순서 | 국가 | 방식 | 목표 시기 |
|---|---|---|---|
| 1 | 말레이시아 | SLFF MVP → MLFF 확장 | 2026~2027 |
| 2 | 우즈베키스탄 | BOS 재사용 + 현지화 | 2027~2028 |
| 3 | 필리핀 | BOS 재사용 + 현지화 | 2027~2028 |
| 4 | 브라질 | BOS 재사용 + 현지화 | 2028~ |

**재사용 전략:** 공통 Core(Transaction·Billing·AI)는 그대로 사용, 국가별 모듈(결제 연동·법규·언어·요금 체계)만 현지화.

## 5. 성공 기준

```
기술적 성공:
  □ RFID 이벤트 처리: < 100ms
  □ 시스템 가용성: 99.99% (4-Nine)
  □ 동시 처리: 10,000 TPS
  □ MLFF Entry/Exit 매칭 정확도: 99.9%

사업적 성공:
  □ 말레이시아 콘세셔네어 1개사 이상 수주
  □ SLFF MVP 납품 완료 (M12 목표)
  □ 수수료 수입으로 개발 투자 18개월 내 회수
  □ 2개 이상 국가 확장 계약 체결
```

## 6. 개발 방식

```
AI Agent 기반 개발:
  GSD (Get Shit Done)   → Phase 기반 개발 관리
  Paperclip             → 29개 AI Agent 조직 운영
  VS Code + Claude Code → IDE + 코드 생성
  cmux                  → 멀티 터미널 환경

개발 비용 (Agent LLM API):
  1단계 착수: ~$380/월 (13개 Agent)
  전체 가동:  ~$720/월 (29개 Agent)
  → 상세: 04_dev/06_budget_model.md
```

## 7. 핵심 리스크 & 대응

| 리스크 | 영향도 | 대응 방안 |
|---|---|---|
| TnG 미납 처리 RnR 미확정 | 높음 | 별도 격리 저장, 현지 협의 후 반영 |
| JPJ API 연동 지연 | 높음 | Mock 서버 선행 개발, 병행 진행 |
| 말레이시아 MLFF 입찰 경쟁 | 높음 | SLFF 선납품으로 레퍼런스 확보 |
| 현지 법규·규제 변경 | 중간 | Compliance Agent 주기 모니터링 |
| TnG Tag ID 체계 미협의 | 중간 | 협의 전까지 패턴 기반 추정 로직 |

## 8. 프로젝트 일정 개요

```
M1~M2:  Phase 1 공통 인프라 (DA 선행 + 기반 구조)
M2~M7:  Phase 2~6 핵심 도메인 개발
M7~M8:  G-HARD 5 — SLFF MVP 내부 검수
M8~M12: Phase 7~12 고도화 + 납품 준비
M12:    말레이시아 콘세셔네어 납품
```

→ 전체 일정 상세: `06_phases/00_phase_overview.md`

## 9. Board 즉시 결정 필요 사항 (G-HARD 0)

```
1. Clearing Center와 JVC의 법적 관계
   (별도 법인 vs JVC 내부 조직)

2. JVC 수수료율 협상 하한선
   (3%~12% 범위 내 목표값)

3. 말레이시아 1순위 타겟 콘세셔네어
   (TnG·PLUS 외 4개 컨소시엄 중 선택)

4. 현지 법무법인 선임
   (Compliance Agent가 요건 초안 준비 완료)

5. Toll Plaza·Center 운영 인력 구성
   (JVC 직고용 vs 현지 파트너 위탁)

6. 초기 Paperclip Agent 예산 승인
   (1단계: ~$380/월)
```
