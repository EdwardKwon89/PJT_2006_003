# Phase 11: 컴플라이언스 & 외부 감사
## 06_phases/11_phase11_compliance.md
## v1.0 | 2026-04 | 참조: 03_data/05_security_compliance.md, 05_governance/04_supplement_items.md

---

> **Agent 사용 지침**
> `Compliance`, `CTO` Agent가 컴플라이언스 & 감사 준비 시 반드시 로드.
> 본 문서는 Phase 11 실행의 유일한 정식 기준 문서이며, PDPA 준수, PCI-DSS 점검, 외부 감사 대응의 구현 기준으로 사용된다.
> 모든 컴플라이언스 변경은 반드시 `Compliance` + `CTO` 공동 승인 후 머지한다.

---

## 1. Phase 개요

### 1.1 목적 및 범위

Phase 11은 Malaysia SLFF/MLFF Tolling BOS의 **컴플라이언스 & 외부 감사 준비** 단계다. PDPA (Personal Data Protection Act 2010), PCI-DSS Level 1, Bank Negara Malaysia (BNM) 지불결제 규정 준수를 점검하고, TOC (Toll Operator Certificate) 취득을 위한 외부 API 공개, 제3자 보안 감사 준비를 완성한다.

**핵심 목표:**
- PDPA 준수 점검 및 DPA (Data Protection Assessment) 완료
- PCI-DSS Level 1 Self Assessment Questionnaire (SAQ) 제출
- BNM 지불결제 지침 준수 확인
- TOC 취득을 위한 외부 API 공개 (PUSH/PULL)
- 보안 인증 취득 (ISO 27001 준비)
- 제3자 침투 테스트 (Penetration Test) 실행

### 1.2 Phase 연계

| 구분 | 내용 |
|------|------|
| **선행 Phase** | Phase 3 — 트랜잭션 (데이터 처리 로직 확정) / Phase 5 — 빌링 (결제 데이터 완성) |
| **병행 Phase** | Phase 10 (분석)과 병행 가능 |
| **후행 Phase** | Phase 12 — 인수인계 & 운영 이관 |
| **예상 기간** | **4주** (Sprint 25~28) |

---

## 2. 담당 Agent 및 역할

| Agent | 역할 | 주요 책임 |
|-------|------|---------|
| `Compliance` | 컴플라이언스 리드 | PDPA/PCI-DSS 점검, 외부 감사 대응 총괄 |
| `CTO` | 기술 책임 | 보안 아키텍처 검토, 침투 테스트 결과 대응 |
| `security-lead` | 보안 담당 | 취약점 점검, 침투 테스트 협력, 보안 패치 |
| `api-lead` | API 담당 | TOC 외부 API 공개, OpenAPI 스펙 작성 |

---

## 3. 주요 태스크 체크리스트

### 3.1 PDPA (Personal Data Protection Act 2010) 준수

- [ ] **개인정보 처리 현황 매핑 (Data Mapping)**
  - 수집하는 개인정보 항목 전수 조사: 이름, 차량 번호판, 전화번호, 이메일, 결제 정보
  - 처리 목적, 보관 기간, 제3자 제공 현황 문서화
- [ ] **정보 주체 권리 처리 API 구현**
  - 개인정보 열람 요청: `GET /api/v1/gdpr/subject-access-request`
  - 개인정보 삭제 요청: `DELETE /api/v1/gdpr/right-to-erasure`
  - 처리 제한 요청, 정정 요청
  - SLA: 요청 접수 후 21 영업일 내 처리
- [ ] **개인정보 보호 영향 평가 (DPIA)**
  - 고위험 처리 활동 식별 (AI 프로파일링, 대규모 처리)
  - DPIA 보고서 작성 및 PDPD 제출

### 3.2 PCI-DSS Level 1 준수

- [ ] **SAQ (Self Assessment Questionnaire) 완성**
  - SAQ D (서비스 제공업체용) — 전체 400+ 문항 점검
  - 카드 데이터 비보관 확인 (Tokenization으로 원본 미저장)
  - 네트워크 분리 (Card Data Environment 격리)
- [ ] **ASV (Approved Scanning Vendor) 취약점 스캔**
  - 분기별 외부 IP 취약점 스캔
  - 모든 High/Critical 취약점 패치 완료 확인
- [ ] **침투 테스트 (Penetration Test)**
  - 외부 제3자 보안 업체 계약
  - 범위: 외부 API, 웹 포털, 내부 네트워크 (선택)
  - 발견 취약점 30일 내 패치 완료

### 3.3 TOC 외부 API 공개

- [ ] **OpenAPI 3.0 스펙 완성** (`/docs/api/bos-public-api.yaml`)
  - 콘세셔네어용 PUSH API: 트랜잭션 데이터 실시간 수신
  - 콘세셔네어용 PULL API: 일별 정산 데이터 조회
  - TnG용 API: 잔액 조회, 차단 상태 확인
  - JPJ용 API: 미납 차량 목록 (배치)
- [ ] **API 보안 강화**
  - OAuth 2.0 Client Credentials (서버-서버 인증)
  - API Rate Limiting (콘세셔네어별 1,000 req/min)
  - mTLS (정부 기관용 API)
- [ ] **API 개발자 포털 구성**
  - Swagger UI 자동 배포 (`https://api.bos.jvc.my/docs`)
  - Sandbox 환경 제공 (테스트 데이터)
  - API 키 셀프 발급 포털

### 3.4 BNM 지불결제 규정 준수

- [ ] BNM 지불결제 지침 (2023) 적용 현황 점검
  - 결제 서비스 라이선스 확인 (JVC 보유 여부)
  - 결제 데이터 현지 보관 요건 (Malaysia 내 데이터 센터)
  - 장애 보고 의무: 관련 중단 4시간 이내 BNM 보고
- [ ] 장애 보고 자동화 시스템
  - 주요 장애 감지 → 자동 BNM 보고 이메일 초안 생성
  - 보고서 양식: BNM 요구 형식 준수

### 3.5 ISO 27001 준비

- [ ] **정보보호 정책 문서화**
  - 정보보호 정책, 사고대응 절차, 접근 제어 정책
  - BCP (Business Continuity Plan), DRP (Disaster Recovery Plan)
- [ ] **내부 감사 실시** (ISO 27001 클로즈 루프)
  - 통제 항목 114개 점검 (ISO 27001:2022 Annex A)
  - GAP 분석 및 개선 계획 수립
- [ ] **인증 심사 일정 수립** (외부 CB와 협의)

---

## 4. 규제 준수 체크리스트

| 규제 | 점검 항목 | 상태 |
|------|---------|------|
| PDPA 2010 | 개인정보 처리 동의 획득 | ⏳ |
| PDPA 2010 | 정보 주체 권리 처리 API | ⏳ |
| PDPA 2010 | DPIA 완성 | ⏳ |
| PCI-DSS | 카드 데이터 Tokenization | ⏳ |
| PCI-DSS | SAQ D 완성 | ⏳ |
| PCI-DSS | ASV 스캔 (분기별) | ⏳ |
| BNM | 데이터 현지화 확인 | ⏳ |
| BNM | 장애 보고 자동화 | ⏳ |
| ISO 27001 | GAP 분석 완료 | ⏳ |
| TOC | 외부 API 공개 완료 | ⏳ |

---

## 5. 완료 기준

| 영역 | 기준 항목 | 검증 방법 |
|------|---------|---------|
| PDPA | DPIA 보고서 완성 및 승인 | 규제 담당자 서명 |
| PCI-DSS | SAQ D 제출 완료 | 제출 확인서 |
| 침투 테스트 | High 취약점 0건 | 침투 테스트 결과 보고서 |
| TOC API | OpenAPI 스펙 완성 및 Sandbox 제공 | 외부 파트너 연동 테스트 |

---

## 6. 참조 문서

| 문서 | 경로 |
|------|------|
| 보안 & 컴플라이언스 設計 | [`03_data/05_security_compliance.md`](../03_data/05_security_compliance.md) |
| 거버넌스 부록 | [`05_governance/04_supplement_items.md`](../05_governance/04_supplement_items.md) |
| API MCP 명세 | [`02_system/06_api_mcp_spec.md`](../02_system/06_api_mcp_spec.md) |
| 외부 연동 명세 | [`02_system/05_external_integration.md`](../02_system/05_external_integration.md) |
| 리포팅 주기 | [`05_governance/03_reporting_cycle.md`](../05_governance/03_reporting_cycle.md) |

---

*Malaysia SLFF/MLFF Tolling BOS — Phase 11 컴플라이언스 & 외부 감사 v1.0*
*생성일: 2026-04 | 담당: Compliance, CTO, security-lead, api-lead*
