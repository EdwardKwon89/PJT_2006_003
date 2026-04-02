---
name: metadata-management
description: 300+ term glossary (KO/EN/BM), code value standards, data ownership and PDPA sensitivity classification
use_when:
  - 용어 정의 또는 코드 값 표준을 참조해야 할 때
  - 신규 데이터 항목의 민감도 분류가 필요할 때
  - 다국어(KO/EN/BM) 비즈니스 용어를 통일해야 할 때
  - 데이터 소유자 매핑이 필요할 때
dont_use_when:
  - 데이터 파이프라인 구현이 필요할 때 (data-architecture-standards 사용)
  - RBAC 접근 제어 구현이 필요할 때 (rbac-data-boundary 사용)
---

# 메타데이터 관리

## 1. 개요

BOS는 300+ 비즈니스 용어와 코드 값을 **표준 용어 사전**으로 관리한다. 모든 Agent, 문서, API는 이 표준을 따른다. 3개 언어 (한국어/영어/말레이어) 지원.

---

## 2. 핵심 내용

### 2.1 핵심 비즈니스 용어 (발췌)

| 한국어 | 영어 | 말레이어 (BM) | 정의 |
|--------|------|-------------|------|
| 콘세셔네어 | Concessionaire | Konsesi | JPJ로부터 고속도로 운영 면허를 받은 사업자 |
| 정산 | Settlement | Penyelesaian | 수납 데이터 집계 및 지급액 확정 |
| 미납 | Unpaid | Tidak Dibayar | 통과 후 정해진 기간 내 결제되지 않은 톨 요금 |
| 위반 | Violation | Pelanggaran | 유효하지 않은 방법으로 통과한 사례 |
| 대사 | Reconciliation | Penyesuaian | BOS 집계와 외부 시스템 데이터 비교·확인 |
| 면제 | Exemption | Pengecualian | 특정 차량/통행에 대한 요금 면제 처리 |
| 이의신청 | Dispute | Bantahan | 미납·위반 처분에 대한 이의 제기 |
| 도로세 | Road Tax | Cukai Jalan | 말레이시아 차량 연간 세금 |

### 2.2 표준 코드 값

#### 트랜잭션 상태 코드

| 코드 | 한국어 | 설명 |
|------|--------|------|
| `COMPLETED` | 완료 | 정상 수납·대사 완료 |
| `PENDING` | 대기 | 처리 중 |
| `UNPAID` | 미납 | 수납 미완료 |
| `DISPUTED` | 이의신청 | 이의신청 처리 중 |
| `EXEMPTED` | 면제 | 요금 면제 사유 적용 |
| `WRITTEN_OFF` | 상각 | Write-off 처리 완료 |

#### 채널 코드

| 코드 | 의미 |
|------|------|
| `A` | Channel A — 콘세셔네어 직접 수납 (RFID 태그) |
| `B` | Channel B — TnG eWallet |
| `C` | Channel C — 현금 (SLFF 전용, MLFF 해당 없음) |
| `GOV` | 정부 차량 면제 채널 |

#### 미납 Tier 코드

| 코드 | 의미 | 기간 |
|------|------|------|
| `TIER_1` | 알림 단계 | D+1~D+7 |
| `TIER_2` | 연체 수수료 단계 | D+8~D+30 |
| `TIER_3` | JPJ 차단 단계 | D+31~D+90 |
| `TIER_4` | Write-off 후보 | D+91 이후 |

### 2.3 데이터 민감도 분류 (PDPA 기준)

| 레벨 | 분류 | 예시 항목 | 처리 방법 |
|------|------|---------|---------|
| P1 | 매우 민감 | 주민등록번호(IC), 은행 계좌, 결제 카드 번호 | Tokenization, Vault 암호화, 로그 마스킹 필수 |
| P2 | 민감 | 이름, 전화번호, 이메일, 차량 번호판 | 암호화 저장, API 응답 마스킹 |
| P3 | 일반 개인정보 | 차량 등급, 통과 시각, 요금소 ID | 표준 DB 보호 (TLS at rest) |
| P4 | 비개인정보 | 집계 통계, KPI 지표, 시스템 로그 | 일반 보호 |

### 2.4 데이터 소유자 매핑

| 도메인 | 데이터 소유자 (Agent) | 예시 데이터 |
|-------|-------------------|---------|
| 트랜잭션 | `txn-lead` | trip_records, payment_attempts |
| 정산 | `billing-lead` | daily_settlement_summary |
| 미납·위반 | `violation-lead` | unpaid_cases, dispute_cases |
| 계정·차량 | `account-lead` | vehicle_tags, owner_profiles |
| 분석·KPI | `reporting-lead` | agg_*, gold_kpi_* |

---

## 3. 주의사항 & 함정

- **코드 값은 반드시 DB 마스터 테이블에서 조회**: 코드 값 하드코딩 금지 (`code_master` 테이블 참조)
- **용어 추가 시 이 Skill 업데이트 필수**: 새 용어 추가 PR에 이 SKILL.md 업데이트 포함 필수 (PR 체크리스트 항목)
- **P1 데이터 로그 출력 금지**: 로그에 IC, 카드 번호, 은행 계좌 절대 출력 금지

---

## 4. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| RBAC & 접근 제어 | [`../rbac-data-boundary/SKILL.md`](../rbac-data-boundary/SKILL.md) |
| 메타데이터 용어 사전 전체 | [`../../docs/03_data/04_metadata_glossary.md`](../../docs/03_data/04_metadata_glossary.md) |
| 보안 & 컴플라이언스 | [`../../docs/03_data/05_security_compliance.md`](../../docs/03_data/05_security_compliance.md) |
