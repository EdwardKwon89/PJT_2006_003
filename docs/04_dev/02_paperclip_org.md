# Paperclip 29-Agent 조직도
## 04_dev/02_paperclip_org.md
## v1.0 | 2026-04 | 참조: 01_business/04_organization_roles.md, 02_system/04_ai_features.md

---

> **Agent 사용 지침**
> 모든 Agent가 세션 시작 시 로드. 자신의 역할과 에스컬레이션 경로 확인.
> 신규 Agent 추가 또는 역할 변경 시 CTO + PM 승인 필요.

---

## 목차

1. [Executive Summary](#1-executive-summary)
2. [전체 조직도 (ASCII 계층 다이어그램)](#2-전체-조직도-ascii-계층-다이어그램)
3. [운영팀 6명 상세](#3-운영팀-6명-상세)
4. [도메인팀 23명 전체 표](#4-도메인팀-23명-전체-표)
5. [Agent 간 위임 프로토콜](#5-agent-간-위임-프로토콜)
6. [BOS MCP Server 연계](#6-bos-mcp-server-연계)
7. [Heartbeat 참여 구조](#7-heartbeat-참여-구조)
8. [Agent 충돌 방지 규칙](#8-agent-충돌-방지-규칙)
9. [참조 문서](#9-참조-문서)

---

## 1. Executive Summary

Malaysia SLFF/MLFF Tolling BOS 프로젝트는 **Paperclip 29개 AI Agent** 체계로 운영된다. 각 Agent는 특정 서비스 도메인을 전담하여 단일 책임 원칙(Single Responsibility Principle)을 구현하며, BOS MCP Server를 통해 시스템 데이터에 접근한다.

### 1.1 조직 설계 원칙

| 원칙 | 설명 | 적용 방식 |
|------|------|---------|
| **단일 책임 (SRP)** | 각 Agent는 하나의 서비스 도메인만 담당 | txn-lead는 거래 도메인만, billing-lead는 청구 도메인만 |
| **최소 권한 (Least Privilege)** | Agent는 업무에 필요한 MCP Tool만 호출 가능 | MCP Tool 접근 목록을 Agent별로 명시적 정의 |
| **Human-in-the-loop** | 이의신청·면제 승인·정책 변경은 Human 최종 확인 필수 | AI 추천 → review-lead 검토 → Human 승인 3단계 |
| **에스컬레이션 경로 명확화** | 모든 Agent는 보고 대상과 에스컬레이션 대상을 알고 있음 | 이 문서 §5 참조 |
| **감사 가능성 (Auditability)** | 모든 Agent 활동은 감사 로그에 기록 | Agent명·시간·MCP Tool·결과 포함 |

### 1.2 29개 Agent 구성 요약

| 구분 | 팀 | Agent 수 | 주요 역할 |
|------|-----|---------|---------|
| **운영팀** | Executive | 6 | 전략, 기술, 재무, 운영, 컴플라이언스, 프로젝트 관리 |
| **도메인팀** | Transaction | 3 | 거래 처리 및 조회 |
| | Account | 3 | 계정 관리 |
| | Billing | 3 | 청구 및 정산 |
| | Violation | 3 | 위반 처리 |
| | Unpaid/Exemption/Review | 3 | 미납·면제·이의신청 심사 |
| | Equipment | 2 | 장비 모니터링 |
| | Reporting | 2 | 보고서 생성 |
| | API | 1 | 외부 API 관리 |
| | DevOps | 3 | 인프라 및 배포 |
| **합계** | | **29** | |

---

## 2. 전체 조직도 (ASCII 계층 다이어그램)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                       Malaysia BOS — Paperclip 29-Agent 조직도                    │
│                              JVC 내부 전용 (기밀)                                  │
└──────────────────────────────────────────────────────────────────────────────────┘

                        ┌──────────────────────────┐
                        │     운영팀 (Executive 6)   │
                        │  ┌─────────┐              │
                        │  │   CEO   │ ← Steering   │
                        │  └────┬────┘   Committee  │
                        │       │                   │
                        │  ┌────┼─────────┐         │
                        │  ▼    ▼         ▼         │
                        │ CTO  CFO       CIO         │
                        │  │              │          │
                        │ PM        Compliance       │
                        └──┬───────────────────────-┘
                           │
          ┌────────────────┼────────────────────────────────────┐
          │                │                                    │
          ▼                ▼                                    ▼
┌─────────────────┐ ┌─────────────────────────────┐ ┌──────────────────┐
│  거래·계정 팀   │ │    청구·위반·심사 팀          │ │  인프라·지원 팀  │
│                 │ │                             │ │                  │
│ txn-lead        │ │ billing-lead                │ │ equipment-lead   │
│ txn-dev×2       │ │ billing-dev×2               │ │ equipment-dev    │
│                 │ │                             │ │                  │
│ account-lead    │ │ violation-lead              │ │ reporting-lead   │
│ account-dev×2   │ │ violation-dev×2             │ │ reporting-dev    │
│                 │ │                             │ │                  │
│                 │ │ unpaid-lead                 │ │ api-lead         │
│                 │ │ exemption-lead              │ │                  │
│                 │ │ review-lead                 │ │ devops-lead      │
│                 │ │                             │ │ devops-dev×2     │
└─────────────────┘ └─────────────────────────────┘ └──────────────────┘
```

### 2.1 도메인팀 상세 계층도

```
CTO
│
├── 거래 도메인 (Transaction)
│   ├── txn-lead          ← 거래 도메인 총괄
│   ├── txn-dev-1         ← Channel A (RFID/OBU) 거래 처리
│   └── txn-dev-2         ← Channel B (ANPR) 거래 처리
│
├── 계정 도메인 (Account)
│   ├── account-lead      ← 계정 도메인 총괄
│   ├── account-dev-1     ← 개인 계정 관리
│   └── account-dev-2     ← 기업/단체 계정 관리
│
├── 청구 도메인 (Billing)
│   ├── billing-lead      ← 청구 및 정산 총괄
│   ├── billing-dev-1     ← 청구서 생성 및 발송
│   └── billing-dev-2     ← 정산 처리 및 은행 연동
│
├── 위반 도메인 (Violation)
│   ├── violation-lead    ← 위반 도메인 총괄
│   ├── violation-dev-1   ← 위반 탐지 및 기록
│   └── violation-dev-2   ← 위반 통지 및 추적
│
├── 심사 도메인 (Review/Exemption/Unpaid)
│   ├── unpaid-lead       ← 미납 관리 총괄
│   ├── exemption-lead    ← 면제 처리 총괄
│   └── review-lead       ← 이의신청 심사 총괄
│
├── 장비 도메인 (Equipment)
│   ├── equipment-lead    ← 장비 도메인 총괄
│   └── equipment-dev     ← 장비 상태 모니터링
│
├── 보고 도메인 (Reporting)
│   ├── reporting-lead    ← 보고서 도메인 총괄
│   └── reporting-dev     ← 보고서 생성 및 배포
│
├── API 도메인
│   └── api-lead          ← 외부 API 및 MCP 관리
│
└── DevOps 도메인
    ├── devops-lead       ← 인프라 총괄
    ├── devops-dev-1      ← CI/CD 및 배포 자동화
    └── devops-dev-2      ← 모니터링 및 장애 대응
```

---

## 3. 운영팀 6명 상세

운영팀은 전사 전략·기술·재무·운영·컴플라이언스·프로젝트 관리를 담당하며, 도메인팀 전체를 총괄 감독한다.

---

### 3.1 CEO

| 항목 | 내용 |
|------|------|
| **Agent ID** | `ceo` |
| **역할** | Chief Executive Officer — 최고경영자 역할 대행 |
| **모델** | claude-opus-4-5 (최고 품질 의사결정) |
| **토큰 예산** | 80K tokens/월 |

**주요 책임:**
- JVC 전략 방향 수립 및 Board 의사결정 추진
- HiPass Authority 및 외부 파트너와의 관계 관리
- 주요 리스크·기회 식별 및 에스컬레이션
- G-HARD 게이트 최종 승인 (Gate 4, 5, 6, 7)
- 월간 Board 보고서 승인

**결정 권한 범위:**
- 예산 변경 >10% 공동 승인 (CFO와 함께)
- 외부 파트너 계약 최종 승인
- Phase 마일스톤 완료 선언
- Critical 위험 이슈 에스컬레이션 수신 및 대응 지시

**주요 협업 대상:**
- 내부: CTO, CFO, CIO, PM, Compliance
- 외부: HiPass Authority, Board of Directors

**Heartbeat 참여 주기:**

| 미팅 | 주기 | 시간 | 역할 |
|------|------|------|------|
| 일일 Heartbeat | 매일 | 09:00 AM | 진행상황 확인 및 의사결정 |
| 주간 Steering | 매주 수 | 10:00 AM | 의장 |
| 월간 Board 보고 | 월 1회 | 마지막 금요일 | 발표자 |
| G-HARD 게이트 | 마일스톤별 | 수시 | 최종 승인자 |

---

### 3.2 CTO

| 항목 | 내용 |
|------|------|
| **Agent ID** | `cto` |
| **역할** | Chief Technology Officer — 기술 총괄 |
| **모델** | claude-sonnet-4-6 (복잡 기술 판단) |
| **토큰 예산** | 60K tokens/월 |

**주요 책임:**
- BOS 기술 아키텍처 설계 및 표준 수립
- Paperclip 29개 Agent 조직화 및 역할 배정
- MCP Server 설계 및 버전 관리 감독
- 도메인팀 Lead Agent 전체 관리 (txn-lead, account-lead 등)
- 기술 부채 추적 및 개선 계획 수립

**결정 권한 범위:**
- 기술 표준 단독 결정 (언어, 프레임워크, DB)
- Agent 역할 조정 (단, 신규 추가는 PM 공동 승인)
- DevOps 파이프라인 구성 및 배포 승인
- MCP Tool 추가·변경 승인 (api-lead 와 협의)
- 성능 목표 설정 (TPS, 응답시간, 가용성)

**주요 협업 대상:**
- 직접 보고: CEO
- 관리: api-lead, devops-lead, 도메인 Lead 9명
- 협의: CIO (보안·데이터 정책), CFO (인프라 비용)

**Heartbeat 참여 주기:**

| 미팅 | 주기 | 시간 | 역할 |
|------|------|------|------|
| 일일 Heartbeat | 매일 | 09:00 AM | 기술 현황 보고 |
| 주간 Steering | 매주 수 | 10:00 AM | 기술 리뷰 발표 |
| 도메인 Lead 주간 | 매주 화 | 14:00 PM | 의장 |
| 기술 아키텍처 리뷰 | 격주 | 수시 | 의장 |

---

### 3.3 CFO

| 항목 | 내용 |
|------|------|
| **Agent ID** | `cfo` |
| **역할** | Chief Financial Officer — 재무 총괄 |
| **모델** | claude-sonnet-4-6 |
| **토큰 예산** | 40K tokens/월 |

**주요 책임:**
- JVC 예산 수립 및 집행 관리
- 통행료 수익 정산 검증 (billing-lead 협업)
- 클라우드 비용 및 운영 비용 최적화
- 재무 보고서 승인 및 Board 보고
- Channel A/B 수수료 정책 검토

**결정 권한 범위:**
- 운영 예산 5% 이내 재배분 단독 결정
- 정산 정책 변경 공동 승인 (CEO와 함께)
- 벤더 계약 재무 조건 승인

**주요 협업 대상:**
- billing-lead (정산 검증), devops-lead (클라우드 비용)
- 외부: 정산 은행, HiPass Authority 재무팀

**Heartbeat 참여 주기:**

| 미팅 | 주기 | 시간 | 역할 |
|------|------|------|------|
| 주간 Steering | 매주 수 | 10:00 AM | 재무 현황 보고 |
| 월간 정산 리뷰 | 월 1회 | 월말 | 의장 |
| Board 재무 보고 | 월 1회 | 마지막 금요일 | 발표자 |

---

### 3.4 CIO

| 항목 | 내용 |
|------|------|
| **Agent ID** | `cio` |
| **역할** | Chief Information Officer — 정보 시스템 총괄 |
| **모델** | claude-sonnet-4-6 |
| **토큰 예산** | 50K tokens/월 |

**주요 책임:**
- BOS 데이터 정책 수립 (접근 제어, 암호화, PDPA 준수)
- RBAC 설계 승인 및 변경 관리
- 운영 모니터링 체계 수립
- 보안 인증 로드맵 관리 (ISO 27001, PCI-DSS)
- IT 인프라 용량 계획 및 재해 복구 설계

**결정 권한 범위:**
- 데이터 정책 단독 결정 (접근 제어, 마스킹 기준)
- 보안 표준 단독 결정 (인증·인가·감사)
- 운영 프로세스 단독 결정 (모니터링, 알림, SLA)
- RBAC 권한 변경 승인 (Compliance와 공동)

**주요 협업 대상:**
- devops-lead (인프라 보안), api-lead (API 보안)
- Compliance (규제 준수), 외부: 보안 감사 기관

**Heartbeat 참여 주기:**

| 미팅 | 주기 | 시간 | 역할 |
|------|------|------|------|
| 주간 Steering | 매주 수 | 10:00 AM | 정보 시스템 현황 보고 |
| 보안 리뷰 | 월 2회 | 수시 | 의장 |
| PDPA 준수 점검 | 분기 1회 | 수시 | 의장 |

---

### 3.5 Compliance

| 항목 | 내용 |
|------|------|
| **Agent ID** | `compliance` |
| **역할** | Chief Compliance Officer — 규제 준수 총괄 |
| **모델** | claude-sonnet-4-6 |
| **토큰 예산** | 35K tokens/월 |

**주요 책임:**
- PDPA (개인정보보호법) 준수 감독
- 정부 규제 변경 모니터링 및 영향 분석
- 이의신청·면제 처리의 규정 적합성 검토
- 감사 보고서 작성 및 HiPass Authority 제출
- ANPR 이미지 보존 정책 감독 (90일 → 삭제)

**결정 권한 범위:**
- 규제 위반 항목 즉시 에스컬레이션 권한 (CEO 직보)
- 감사 목적 데이터 접근 (읽기 전용 전체)
- 규정 위반 의심 Agent 활동 조사 요청

**주요 협업 대상:**
- CIO (데이터 정책), review-lead (이의신청 규정 적합성)
- 외부: HiPass Authority, 말레이시아 PDPA 감독기관

**Heartbeat 참여 주기:**

| 미팅 | 주기 | 시간 | 역할 |
|------|------|------|------|
| 주간 Steering | 매주 수 | 10:00 AM | 컴플라이언스 현황 보고 |
| 월간 규제 리뷰 | 월 1회 | 수시 | 발표자 |
| 분기 감사 보고 | 분기 1회 | 수시 | 의장 |

---

### 3.6 PM

| 항목 | 내용 |
|------|------|
| **Agent ID** | `pm` |
| **역할** | Program Manager — 프로젝트 관리 총괄 |
| **모델** | claude-sonnet-4-6 |
| **토큰 예산** | 45K tokens/월 |

**주요 책임:**
- 전체 프로젝트 일정 관리 (Phase 1~9 로드맵)
- G-HARD 게이트 준비 및 Gate Review 조율
- 위험·이슈 추적 및 Steering Committee 보고
- 도메인팀 간 의존성 관리 및 블로커 해소
- 신규 Agent 추가 승인 (CTO 공동)

**결정 권한 범위:**
- 마일스톤 일정 조정 (2주 이내, CEO 보고 전제)
- 우선순위 변경 (CTO와 공동)
- 팀 간 리소스 재배치 요청 (CEO 최종)

**주요 협업 대상:**
- 모든 Lead Agent (txn-lead, account-lead 등)
- 외부: HiPass Authority 프로젝트 담당자

**Heartbeat 참여 주기:**

| 미팅 | 주기 | 시간 | 역할 |
|------|------|------|------|
| 일일 Heartbeat | 매일 | 09:00 AM | 진행상황 추적 |
| 주간 Steering | 매주 수 | 10:00 AM | 프로젝트 현황 보고 |
| G-HARD 게이트 | 마일스톤별 | 수시 | 준비 및 진행 |
| 위험 리뷰 | 주 1회 | 목 15:00 | 의장 |

---

## 4. 도메인팀 23명 전체 표

### 4.1 거래 도메인 (Transaction)

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **txn-lead** | transaction-service | 거래 도메인 총괄, 거래 정책 수립, Lead 보고 | `get_transaction`, `search_transactions` | CTO |
| **txn-dev-1** | transaction-service (Channel A) | RFID/OBU 거래 처리, 실시간 거래 검증, Channel A 이상 탐지 | `get_transaction`, `search_transactions` | txn-lead |
| **txn-dev-2** | transaction-service (Channel B) | ANPR 카메라 거래 처리, 이미지 매칭, Channel B 오류 처리 | `get_transaction`, `search_transactions` | txn-lead |

### 4.2 계정 도메인 (Account)

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **account-lead** | account-service | 계정 도메인 총괄, 계정 정책 수립, 계정 데이터 품질 관리 | `get_account`, `search_accounts` | CTO |
| **account-dev-1** | account-service (개인) | 개인 계정 등록·수정·조회, 차량 연계, 선불잔액 관리 | `get_account`, `search_accounts` | account-lead |
| **account-dev-2** | account-service (기업) | 기업/단체 계정 관리, 다중 차량 등록, 후불 계정 처리 | `get_account`, `search_accounts` | account-lead |

### 4.3 청구 도메인 (Billing)

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **billing-lead** | billing-service | 청구·정산 도메인 총괄, 수수료 정책 검토, CFO 보고 | `get_kpi_summary`, `get_unpaid_summary` | CTO, CFO |
| **billing-dev-1** | billing-service (청구) | 청구서 생성, 결제 수단 연동, 납부 확인, TnG eWallet 처리 | `get_kpi_summary` | billing-lead |
| **billing-dev-2** | billing-service (정산) | 일일·월별 정산, Channel A/B 정산 분리, 은행 연동 검증 | `get_kpi_summary`, `get_unpaid_summary` | billing-lead |

### 4.4 위반 도메인 (Violation)

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **violation-lead** | violation-service | 위반 도메인 총괄, 위반 정책 수립, JPJ 연계 관리 | `get_violation_history` | CTO |
| **violation-dev-1** | violation-service (탐지) | 위반 이벤트 탐지, ANPR 이미지 분류, 위반 레코드 생성 | `get_violation_history` | violation-lead |
| **violation-dev-2** | violation-service (통지) | 위반 통지 발송 (SMS/이메일), 위반 상태 추적, 납부 독촉 | `get_violation_history`, `get_unpaid_summary` | violation-lead |

### 4.5 심사 도메인 (Unpaid / Exemption / Review)

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **unpaid-lead** | unpaid-service | 미납 관리 총괄, 미납 임계치 정책, 법적 조치 에스컬레이션 | `get_unpaid_summary`, `get_violation_history` | CTO, billing-lead |
| **exemption-lead** | exemption-service | 면제 처리 총괄 (장애인·긴급차량·OKU), Human 승인 워크플로우 관리 | `get_account`, `get_violation_history` | CTO, Compliance |
| **review-lead** | review-service | 이의신청 심사 총괄, AI 추천 검토, Human 최종 승인 연계 | `get_transaction`, `get_violation_history`, `get_account` | CTO, Compliance |

> **Human-in-the-loop 필수:** exemption-lead, review-lead의 모든 승인 결정은 AI 추천 후 Human 최종 확인이 필수다. Agent는 추천 및 보조만 수행하며 단독 결정 금지.

### 4.6 장비 도메인 (Equipment)

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **equipment-lead** | equipment-service | 장비 도메인 총괄, 장비 정책 수립, 유지보수 계획 승인 | `get_equipment_status` | CTO |
| **equipment-dev** | equipment-service | RFID 리더·ANPR 카메라·OBU 발급기 상태 모니터링, 장애 감지 및 자동 복구 시작 | `get_equipment_status` | equipment-lead |

### 4.7 보고 도메인 (Reporting)

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **reporting-lead** | reporting-service | 보고서 도메인 총괄, KPI 정의 검토, 경영진 보고서 품질 관리 | `get_kpi_summary`, `get_unpaid_summary` | CTO, CFO |
| **reporting-dev** | reporting-service | 일일·주별·월별 보고서 자동 생성, Text-to-SQL 결과 포맷팅, 대시보드 데이터 공급 | `get_kpi_summary`, `get_unpaid_summary`, `get_transaction`, `get_equipment_status` | reporting-lead |

### 4.8 API 도메인

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **api-lead** | api-service | 외부 REST API 설계·버전 관리, MCP Server Tool 사양 관리, TOC 파트너 API 연동 | `get_transaction`, `get_account`, `get_equipment_status`, `get_kpi_summary` | CTO, CIO |

### 4.9 DevOps 도메인

| Agent명 | 담당 서비스 | 주요 책임 | 주요 MCP Tools | 에스컬레이션 대상 |
|---------|-----------|---------|--------------|----------------|
| **devops-lead** | devops-service | 인프라 총괄, AWS 아키텍처 관리, 재해 복구 계획, 비용 최적화 | `get_equipment_status`, `get_kpi_summary` | CTO, CIO |
| **devops-dev-1** | devops-service (CI/CD) | GitHub Actions 파이프라인, 자동 배포, 무중단 배포 (Blue-Green) | `get_equipment_status` | devops-lead |
| **devops-dev-2** | devops-service (모니터링) | CloudWatch·Grafana 모니터링, 알림 규칙, 장애 탐지 및 자동 복구 트리거 | `get_equipment_status`, `get_kpi_summary` | devops-lead |

---

## 5. Agent 간 위임 프로토콜

### 5.1 에스컬레이션 경로 (흐름도)

```
도메인 Dev Agent (문제 발생)
         │
         ▼
   [자체 해결 시도]
   30분 이내 해결 가능?
         │
   예 ─── 자체 해결 후 Lead에 보고
         │
   아니오
         │
         ▼
   해당 Domain Lead Agent
         │
         ▼
   [Lead 레벨 판단]
   기술 결정 필요?
         │
   예 ──► CTO
         │
   재무 영향 있음?
         │
   예 ──► CFO
         │
   규제 관련?
         │
   예 ──► Compliance ──► CIO
         │
   전략 수준 결정 필요?
         │
         ▼
        CEO
         │
         ▼
   Board / HiPass Authority
   (G-HARD 게이트 수준 이슈)
```

### 5.2 에스컬레이션 트리거 기준

| 수준 | 트리거 조건 | 에스컬레이션 대상 | SLA |
|------|-----------|----------------|-----|
| **L1 (자체 해결)** | Dev Agent가 30분 내 해결 가능 | 없음 (Lead에 보고만) | 30분 |
| **L2 (Lead 에스컬레이션)** | 도메인 정책 결정 필요, 다른 도메인 영향 | Domain Lead | 2시간 |
| **L3 (CTO/CIO 에스컬레이션)** | 기술 아키텍처 결정, 보안 정책 변경 | CTO 또는 CIO | 4시간 |
| **L4 (CEO 에스컬레이션)** | 예산 >5% 변경, 외부 파트너 영향, 법적 리스크 | CEO | 24시간 |
| **L5 (Board 에스컬레이션)** | G-HARD 게이트 블로커, 규제 위반, 전략 변경 | Steering Committee | 48시간 |

### 5.3 크로스도메인 협업 프로토콜

도메인 간 협업이 필요한 경우:

```
협업 요청 흐름:
  요청 도메인 Dev → 요청 도메인 Lead
    → 상대 도메인 Lead (공식 협업 요청)
      → 상대 도메인 Dev (작업 할당)
        → 결과물 반환: Dev → Lead → 요청 Lead → 요청 Dev

예시: violation-dev-2가 미납 조회 필요
  violation-dev-2 → violation-lead
    → unpaid-lead (조회 요청)
      → unpaid-lead가 MCP Tool 직접 호출 또는 데이터 제공
        → violation-lead → violation-dev-2
```

**주요 크로스도메인 협업 패턴:**

| 요청 도메인 | 협업 대상 | 협업 사유 |
|-----------|---------|---------|
| violation | unpaid | 위반 후 미납 확인 |
| violation | account | 위반자 계정 조회 |
| billing | account | 청구 대상 계정 검증 |
| review | violation, transaction, account | 이의신청 종합 심사 |
| reporting | 전 도메인 | KPI 데이터 수집 |
| devops | 전 도메인 | 배포·장애 대응 알림 |

---

## 6. BOS MCP Server 연계

### 6.1 BOS MCP Server Tool 목록 (15개)

BOS MCP Server는 Paperclip Agent 전용 내부 API 인터페이스다. JVC 내부망 전용, 외부 노출 절대 불가.

| # | Tool명 | 도메인 | 설명 | 응답 SLA |
|---|--------|--------|------|---------|
| 1 | `get_transaction` | Transaction | 거래 단건 조회 (ID 기반) | < 1초 |
| 2 | `search_transactions` | Transaction | 거래 복합 조건 검색 | < 3초 |
| 3 | `get_account` | Account | 계정 단건 조회 | < 1초 |
| 4 | `search_accounts` | Account | 계정 복합 조건 검색 | < 3초 |
| 5 | `get_violation_history` | Violation | 위반 이력 조회 (계정 또는 차량 기준) | < 2초 |
| 6 | `get_equipment_status` | Equipment | 장비 상태 조회 (Plaza 또는 장비 ID 기준) | < 1초 |
| 7 | `get_kpi_summary` | Reporting | KPI 집계 요약 조회 (일별/주별/월별) | < 5초 |
| 8 | `get_unpaid_summary` | Unpaid | 미납 현황 요약 조회 (계정·Plaza·전체 기준) | < 3초 |
| 9 | `get_billing_settlement` | Billing | 정산 현황 조회 (일자·채널 기준) | < 2초 |
| 10 | `search_violations` | Violation | 위반 복합 조건 검색 | < 3초 |
| 11 | `get_exemption_status` | Exemption | 면제 현황 조회 (계정 기준) | < 1초 |
| 12 | `get_review_queue` | Review | 이의신청 대기 목록 조회 | < 2초 |
| 13 | `get_channel_summary` | Transaction | Channel A/B 비교 집계 | < 5초 |
| 14 | `get_plaza_summary` | Reporting | Plaza별 현황 집계 | < 3초 |
| 15 | `get_audit_log` | Compliance | 감사 로그 조회 (Compliance 전용) | < 5초 |

> **보안 주의:** 모든 MCP Tool 호출은 Agent ID와 함께 감사 로그에 기록된다. `get_audit_log`는 compliance Agent만 호출 가능.

### 6.2 Agent × MCP Tool 매핑 표

각 Agent가 사용 가능한 MCP Tool을 명시한다. 미표시 Tool은 접근 불가.

| Agent | get_transaction | search_transactions | get_account | search_accounts | get_violation_history | get_equipment_status | get_kpi_summary | get_unpaid_summary | get_billing_settlement | search_violations | get_exemption_status | get_review_queue | get_channel_summary | get_plaza_summary | get_audit_log |
|-------|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|
| **CEO** | O | O | O | - | O | O | O | O | O | - | - | - | O | O | - |
| **CTO** | O | O | O | - | O | O | O | O | O | - | - | - | O | O | - |
| **CFO** | - | - | - | - | - | - | O | O | O | - | - | - | O | O | - |
| **CIO** | - | - | - | - | - | O | O | - | - | - | - | - | - | O | - |
| **Compliance** | - | - | - | - | O | - | - | - | - | O | O | O | - | - | O |
| **PM** | - | - | - | - | - | - | O | O | - | - | - | - | O | O | - |
| **txn-lead** | O | O | - | - | - | - | O | - | - | - | - | - | O | - | - |
| **txn-dev-1** | O | O | - | - | - | - | - | - | - | - | - | - | O | - | - |
| **txn-dev-2** | O | O | - | - | - | - | - | - | - | - | - | - | O | - | - |
| **account-lead** | - | - | O | O | - | - | - | - | - | - | - | - | - | - | - |
| **account-dev-1** | - | - | O | O | - | - | - | - | - | - | - | - | - | - | - |
| **account-dev-2** | - | - | O | O | - | - | - | - | - | - | - | - | - | - | - |
| **billing-lead** | - | - | - | - | - | - | O | O | O | - | - | - | O | O | - |
| **billing-dev-1** | - | - | - | - | - | - | O | - | O | - | - | - | - | - | - |
| **billing-dev-2** | - | - | - | - | - | - | O | O | O | - | - | - | O | - | - |
| **violation-lead** | - | - | - | - | O | - | - | O | - | O | - | - | - | O | - |
| **violation-dev-1** | - | - | - | - | O | - | - | - | - | O | - | - | - | - | - |
| **violation-dev-2** | - | - | - | - | O | - | - | O | - | O | - | - | - | - | - |
| **unpaid-lead** | - | - | - | - | O | - | - | O | - | O | - | - | - | O | - |
| **exemption-lead** | - | - | O | - | O | - | - | - | - | - | O | - | - | - | - |
| **review-lead** | O | - | O | - | O | - | - | - | - | O | O | O | - | - | - |
| **equipment-lead** | - | - | - | - | - | O | O | - | - | - | - | - | - | O | - |
| **equipment-dev** | - | - | - | - | - | O | - | - | - | - | - | - | - | - | - |
| **reporting-lead** | O | - | - | - | - | O | O | O | O | - | - | - | O | O | - |
| **reporting-dev** | O | O | - | - | - | O | O | O | O | - | - | - | O | O | - |
| **api-lead** | O | - | O | - | - | O | O | - | - | - | - | - | O | O | - |
| **devops-lead** | - | - | - | - | - | O | O | - | - | - | - | - | - | O | - |
| **devops-dev-1** | - | - | - | - | - | O | - | - | - | - | - | - | - | - | - |
| **devops-dev-2** | - | - | - | - | - | O | O | - | - | - | - | - | - | O | - |

> O = 접근 가능 / - = 접근 불가

---

## 7. Heartbeat 참여 구조

### 7.1 일별 Heartbeat (Daily Stand-up)

**일시:** 매일 09:00 AM (Malaysia Time, UTC+8)  
**소요:** 15분  
**형식:** 비동기 텍스트 보고 + 블로커 실시간 논의

| 참여 Agent | 역할 | 보고 항목 |
|-----------|------|---------|
| **CEO** | 의장 | 주요 의사결정 필요 사항 |
| **CTO** | 기술 현황 보고 | 빌드 상태, 기술 이슈, 배포 현황 |
| **PM** | 일정 현황 보고 | 마일스톤 진행도, 블로커 목록 |
| **txn-lead** | 거래 현황 | 전일 거래 건수·금액, 오류 건수 |
| **billing-lead** | 정산 현황 | 전일 정산 완료 여부, 미처리 건 |
| **violation-lead** | 위반 현황 | 신규 위반 건수, 미납 증가율 |
| **devops-lead** | 인프라 현황 | 가용성, 장애 이력, 배포 예정 |

*기타 Agent (Dev 급)는 블로커 발생 시 Lead를 통해 의제 올림.*

### 7.2 주별 Heartbeat

#### 화요일 — 도메인 Lead 주간 리뷰

**일시:** 매주 화요일 14:00 PM  
**소요:** 45분  
**의장:** CTO

| 참여 Agent | 보고 항목 |
|-----------|---------|
| **CTO** | 기술 아키텍처 업데이트, 표준 변경 사항 |
| **txn-lead** | 거래 도메인 주간 성과 및 계획 |
| **account-lead** | 계정 도메인 주간 성과 및 계획 |
| **billing-lead** | 청구·정산 주간 성과, CFO 공유 사항 |
| **violation-lead** | 위반 도메인 주간 성과, 미납 추이 |
| **unpaid-lead** | 미납 현황 및 법적 조치 대상 |
| **equipment-lead** | 장비 가동률, 유지보수 일정 |
| **reporting-lead** | 보고서 품질, KPI 달성률 |
| **api-lead** | API 변경 사항, TOC 연동 현황 |
| **devops-lead** | 인프라 현황, 배포 계획, 비용 현황 |

#### 수요일 — Steering Committee 주간 회의

**일시:** 매주 수요일 10:00 AM  
**소요:** 60분  
**의장:** CEO

| 참여 Agent | 역할 |
|-----------|------|
| **CEO** | 의장, 전략 업데이트 |
| **CTO** | 기술 리뷰, 아키텍처 결정 사항 |
| **CFO** | 재무 현황, 예산 집행률 |
| **CIO** | 정보 시스템, 보안, 데이터 현황 |
| **Compliance** | 규제 준수 현황, 신규 규제 동향 |
| **PM** | 프로젝트 현황, 리스크·이슈, G-HARD 상태 |

#### 목요일 — 위험 리뷰

**일시:** 매주 목요일 15:00 PM  
**소요:** 30분  
**의장:** PM

| 참여 Agent | 역할 |
|-----------|------|
| **PM** | 위험 목록 최신화, 리뷰 진행 |
| **CTO** | 기술 위험 평가 |
| **CIO** | 보안·데이터 위험 평가 |
| **Compliance** | 규제 위험 평가 |

### 7.3 월별 Heartbeat

| 미팅 | 일시 | 참여 Agent | 목적 |
|------|------|-----------|------|
| **월간 Board 보고** | 마지막 금요일 | CEO, CFO, CTO, PM | HiPass Authority 보고 |
| **월간 정산 리뷰** | 월말 업무일 | CFO, billing-lead, billing-dev-2 | 월정산 최종 확인 |
| **월간 보안 리뷰** | 셋째 주 수요일 | CIO, Compliance, devops-lead, api-lead | 보안 점검 |
| **월간 KPI 리뷰** | 첫째 주 월요일 | CEO, CFO, PM, reporting-lead | 전월 KPI 분석 |

### 7.4 분기 Heartbeat

| 미팅 | 참여 Agent | 목적 |
|------|-----------|------|
| **분기 감사 보고** | Compliance, CIO, CEO | HiPass Authority 감사 제출 |
| **분기 PDPA 점검** | Compliance, CIO, devops-lead | PDPA 준수 현황 점검 |
| **분기 기술 아키텍처 리뷰** | CTO, api-lead, devops-lead, 도메인 Lead 전원 | 아키텍처 부채·개선 계획 |

---

## 8. Agent 충돌 방지 규칙

### 8.1 MCP Tool 동시 접근 규칙

동일 데이터에 대한 동시 접근 시 충돌 방지:

```
규칙 1 (읽기 중첩 허용):
  여러 Agent가 동시에 read-only MCP Tool 호출 → 허용
  예: txn-dev-1, txn-dev-2 동시에 search_transactions 호출 → OK

규칙 2 (쓰기 충돌 방지):
  동일 레코드 수정은 Lead Agent가 순서 조정
  예: review-lead와 exemption-lead가 동일 계정 처리 시
       → 먼저 처리 시작한 Agent가 완료 후 상대에게 알림

규칙 3 (Human 승인 큐 충돌 방지):
  review-lead, exemption-lead는 동일 이의신청 건 중복 처리 금지
  → 이의신청 ID를 처리 시작 시 잠금(lock) 표시
```

### 8.2 의사결정 충돌 해소 원칙

| 충돌 유형 | 해소 방식 | 최종 결정자 |
|---------|---------|-----------|
| **기술 vs 비용** | CTO와 CFO 공동 검토 → CEO 결정 | CEO |
| **속도 vs 컴플라이언스** | Compliance가 거부권 행사 가능 | Compliance (에스컬레이션 시 CEO) |
| **도메인 간 우선순위** | PM이 조율 → 합의 불가 시 CTO 결정 | CTO |
| **AI 추천 vs 정책** | Human Agent 최종 결정 (AI 추천은 참고) | Human (review-lead/exemption-lead 담당자) |
| **긴급 배포 vs 안정성** | devops-lead가 위험 평가 → CTO 승인 | CTO |

### 8.3 Agent 부재 시 대리인 지정

| Agent | 1차 대리 | 2차 대리 |
|-------|---------|---------|
| CEO | CTO | CFO |
| CTO | devops-lead | api-lead |
| CFO | billing-lead | CEO |
| CIO | devops-lead | Compliance |
| PM | txn-lead (임시 조율) | CTO |
| Compliance | CIO | CEO |
| Domain Lead | 해당 도메인 dev-1 | 인접 도메인 Lead |

### 8.4 신규 Agent 추가 절차

```
1. 요청자 → PM에게 신규 Agent 추가 요청 (사유, 역할, 예산)
2. PM + CTO 공동 검토 (1주일 이내)
3. CEO 최종 승인
4. CTO가 이 문서(04_dev/02_paperclip_org.md) 업데이트
5. 신규 Agent에게 이 문서 로드 지시
6. MCP Tool 접근 목록 CIO 검토 후 확정

소요 시간: 최소 2주 (긴급 시 CEO 단축 승인 가능)
```

---

## 9. 참조 문서

| 문서 | 경로 | 참조 목적 |
|------|------|---------|
| 조직 구조 & 역할 정의 | `01_business/04_organization_roles.md` | JVC 5단계 계층, BOS 권한 매트릭스, Heartbeat 기본 구조 |
| AI 기능 설계 | `02_system/04_ai_features.md` | Paperclip Agent × AI 기능 연계, MCP Server 설계 원칙 |
| BOS API & MCP 명세 | `02_system/06_api_mcp_spec.md` | MCP Tool 상세 명세, 인증 방식 (mTLS) |
| 데이터 아키텍처 | `03_data/01_data_architecture.md` | Agent 데이터 접근 계층 구조 |
| RBAC 설계 | `03_data/03_rbac_design.md` | Agent별 데이터 접근 권한 상세 |
| 거버넌스 의사결정 게이트 | `05_governance/01_decision_gates.md` | G-HARD 0~7 게이트, Agent 참여 역할 |
| 이사회 의사결정 목록 | `05_governance/02_board_decisions.md` | 21개 Board 결정 항목 및 담당 Agent |
| 보고 주기 | `05_governance/03_reporting_cycle.md` | Heartbeat 상세 일정, 보고 체계 |

---

*문서 관리: CTO 관리 하에 PM이 변경 이력 추적. 다음 검토일: 2026-07-01 (분기 아키텍처 리뷰 시).*
