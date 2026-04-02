# 01. Data Architecture & Strategy

**Document ID:** WAVE3A-01  
**Maintained By:** Data Architect / Chief Data Officer  
**Last Updated:** 2026-04-01  
**Status:** Draft for Review

---

## Executive Summary

Malaysia SLFF/MLFF 프로젝트의 **데이터 아키텍처**는 고속도로 통행료 징수 시스템의 모든 거래, 정산, 운영 데이터를 관리하는 체계다. 이 문서는 **데이터 역할 및 책임**, **5단계 계층 참조 구조**, **ERD 설계 방향**, **메타데이터 관리**, 그리고 **데이터 거버넌스**를 정의한다.

**핵심 원칙:**
- 데이터는 **적응 가능하고 확장 가능**한 계층 구조로 조직
- **감사성(Auditability)**과 **규제 준수(Compliance)** 우선
- **마이크로서비스** 기반 독립적 데이터 도메인 지원
- **메타데이터 중심**의 데이터 거버넌스 체계

---

## 1. 데이터 역할 및 책임 (Data Roles & Responsibilities)

### 1.1 데이터 조직 구조

```
┌────────────────────────────────────────────────────┐
│   Chief Data Officer (CDO)                         │
│   └─ 데이터 전략, 거버넌스, 규정 준수               │
├────────────────────────────────────────────────────┤
│                                                    │
├─ Data Architecture Lead                           │
│  └─ ERD 설계, 데이터 모델, 스키마 관리             │
│                                                    │
├─ Data Governance Officer                          │
│  └─ 메타데이터 관리, 데이터 품질, 접근 제어        │
│                                                    │
├─ Data Engineer (Platform)                         │
│  └─ 데이터 파이프라인, ETL/ELT, 저장소 운영       │
│                                                    │
├─ Data Analyst (Insights)                          │
│  └─ 리포팅, BI, 데이터 분석, 성능 모니터링        │
│                                                    │
└─ Database Administrator (DBA)                      │
   └─ 백업, 복구, 성능 튜닝, 보안 감사              │
└────────────────────────────────────────────────────┘
```

### 1.2 역할별 책임 정의

| 역할 | 주요 책임 | 기술 스택 | 보고처 |
|------|---------|---------|--------|
| **CDO** | 데이터 전략 수립, 거버넌스 정책 수립, 규제 감시 | Metadata Registry, Governance Tool | CIO/CEO |
| **Architecture Lead** | ERD 설계, 정규화, 데이터 모델 검증 | PostgreSQL, Prisma, DrawIO | CDO |
| **Governance Officer** | 데이터 카탈로그, 접근 제어, 감사 로그 관리 | Apache Atlas, Collibra | CDO |
| **Data Engineer** | 파이프라인 구축, 데이터 품질 검증 | Apache Kafka, Airflow, Python | CDO |
| **Data Analyst** | BI 리포트, 성능 분석, 예측 모델 | Tableau, Power BI, SQL | CPO |
| **DBA** | 인덱싱, 백업 전략, 재해 복구 | PostgreSQL, AWS RDS, Terraform | CIO |

---

## 2. 5단계 계층 데이터 참조 구조 (5-Tier Hierarchical Data Architecture)

Malaysia 통행료 징수 시스템의 **조직 계층**과 **데이터 계층**은 일대일 대응된다. 이는 권한 제어, 정산 관리, 보고 체계를 단순화한다.

### 2.1 계층 맵핑

```
┌─────────────────────────────────────────────────────────┐
│ Level 1: Line (국가 운영 정책)                          │
├─────────────────────────────────────────────────────────┤
│ • Scope: 전국 거래 데이터, 정책 마스터                 │
│ • Owner: Operations Director                           │
│ • Data Access: R++ (전체), W++ (정책만)                │
│ • 주요 테이블: config_master, policy, aggregated_kpi   │
└──────────────────────┬──────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
┌─────────────────┐  ┌──────────────┐  ┌──────────────┐
│ Level 2: Plaza  │  │              │  │              │
│ (10~15개)      │  │  Plaza(N)   │  │  Plaza(N)   │
├─────────────────┤  └──────────────┘  └──────────────┘
│ • Scope: 해당   │
│   요금소 거래   │
│ • Owner: Toll   │
│   Manager       │
│ • Data Access:  │
│   R, W (local)  │
│ • 주요 테이블:  │
│   trip_record,  │
│   lane_config   │
└────────┬────────┘
         │
┌────────┴────────────────────────────────────────┐
│ Level 3: Toll Center (3~4개 지역 센터)          │
├──────────────────────────────────────────────────┤
│ • Scope: 지역별 정산, 보고, 감시                │
│ • Owner: Regional Manager                       │
│ • Data Access: R+, W+ (지역만)                  │
│ • 주요 테이블: settlement, regional_report      │
└────────┬────────────────────────────────────────┘
         │
┌────────┴──────────────────────────────────────┐
│ Level 4: Clearing Center (1개)                │
├────────────────────────────────────────────────┤
│ • Scope: 전국 정산, 은행 연동                  │
│ • Owner: Finance Manager                      │
│ • Data Access: R++, W++ (전체)                │
│ • 주요 테이블: financial_transaction,         │
│   bank_settlement, fee_ledger                 │
└────────┬──────────────────────────────────────┘
         │
┌────────┴──────────────────────────────────────┐
│ Level 5: TOC (레거시 시스템 연계)             │
├────────────────────────────────────────────────┤
│ • Scope: 기존 HiPass 데이터 동기              │
│ • Owner: Integration Manager                  │
│ • Data Access: R- (읽기만), API 입력           │
│ • 주요 테이블: toc_sync_log, legacy_mapping   │
└────────────────────────────────────────────────┘
```

### 2.2 계층별 데이터 도메인

| 계층 | 데이터 도메인 | 예시 테이블 | 갱신 주기 | 감사 대상 |
|------|-------------|-----------|---------|---------|
| **Level 1** | 정책, 설정, KPI | config_master, policy_rule, kpi_target | 월 1회 | O (변경) |
| **Level 2** | 거래, 차량, 장비 | trip_record, vehicle_tag, lane_status | 실시간 | O (일일) |
| **Level 3** | 정산, 보고, 송금 | settlement, regional_report, transfer_log | 일 1회 | O (매일) |
| **Level 4** | 금융, 수수료, 계정 | financial_transaction, fee_ledger, bank_account | 실시간 | O (필수) |
| **Level 5** | 동기, 매핑, 로그 | toc_sync_log, legacy_mapping, interface_audit | 매시간 | O (변경) |

---

## 3. ERD 설계 방향 (Entity-Relationship Design)

### 3.1 주요 엔티티 및 관계

```
┌──────────────────────┐
│   config_master      │
│  (정책/설정)         │
├──────────────────────┤
│ PK: config_id        │
│ - config_type        │ (LINE, PLAZA, TOLL_RATE)
│ - config_value       │
│ - effective_date     │
│ - created_by         │
│ - created_at         │
│ - audit_log (JSON)   │
└───────────┬──────────┘
            │ 1:N
            ▼
┌──────────────────────┐        ┌──────────────────────┐
│   plaza_config       │────────│   lane_config        │
│  (요금소 설정)       │ 1:N    │  (차선 설정)         │
├──────────────────────┤        ├──────────────────────┤
│ PK: plaza_id         │        │ PK: lane_id          │
│ FK: level_1_id       │        │ FK: plaza_id         │
│ - name               │        │ - name               │
│ - region             │        │ - status             │
│ - contact           │        │ - equipment_type     │
└────────┬─────────────┘        └──────────┬───────────┘
         │ 1:N                             │ 1:N
         └─────────────────┬───────────────┘
                           │
                    ┌──────▼─────────────────┐
                    │  trip_record           │
                    │  (통행 거래)           │
                    ├───────────────────────┤
                    │ PK: trip_id            │
                    │ FK: lane_id            │
                    │ FK: vehicle_tag_id     │
                    │ - timestamp            │
                    │ - toll_amount          │
                    │ - payment_status       │
                    │ - channel (A/B)        │
                    │ - trip_hash (감사용)   │
                    └──────┬────────────────┘
                           │ 1:N
         ┌─────────────────┴──────────────────┐
         │                                    │
    ┌────▼──────────────┐            ┌───────▼─────────┐
    │ payment_attempt   │            │ vehicle_tag     │
    │  (결제 시도)      │            │  (차량 태그)    │
    ├───────────────────┤            ├─────────────────┤
    │ PK: attempt_id    │            │ PK: vehicle_tag_id
    │ FK: trip_id       │            │ - plate_number  │
    │ - amount          │            │ - rfid_tag      │
    │ - status          │            │ - vehicle_type  │
    │ - attempt_no      │            │ - owner_id      │
    │ - created_at      │            │ - active_flag   │
    └───────────────────┘            └─────────────────┘
                                            │
                                     ┌──────┴──────────┐
                                     │ vehicle_owner   │
                                     │  (차량 소유자)  │
                                     ├─────────────────┤
                                     │ PK: owner_id    │
                                     │ - name          │
                                     │ - email         │
                                     │ - phone         │
                                     │ - address       │
                                     │ - kyc_status    │
                                     └─────────────────┘
```

### 3.2 ERD 상세 설명

**핵심 테이블:**

1. **config_master** — 시스템 전체 설정 (통행료, 정책, 요금)
   - 변경 이력 추적 (audit_log 컬럼)
   - 버전 관리 (effective_date, end_date)
   - Level 1에서만 수정 가능

2. **trip_record** — 모든 거래의 중심 (실시간 생성)
   - 거래 고유성 보장 (trip_hash)
   - 감시 계층(Level 2~4) 모두 참조
   - 상태 머신: INITIATED → PROCESSING → PAID/UNPAID → RECONCILED

3. **payment_attempt** — 결제 시도 기록 (감사/추적용)
   - 동일 trip에 대한 재시도 추적 (attempt_no)
   - 외부 게이트웨이 응답 저장 (status, response_code)
   - 실패 시 Tier 관리로 연결

4. **vehicle_tag & vehicle_owner** — 차량 등록 및 소유자 관리
   - KYC 준수 (kyc_status)
   - 미결제 거래와의 추적성 확보

5. **settlement & financial_transaction** — 정산 및 금융 거래
   - 일 1회/주 1회 집계
   - 은행 계좌와 매핑 (bank_account_id)
   - 수수료 계산 이력

### 3.3 정규화 원칙

- **3NF (3rd Normal Form)** 적용
  - 중복 최소화 (settlement은 trip_record를 집계해서 생성)
  - 이상(anomaly) 방지 (deletion, insertion anomaly 없음)

- **감사 추적성 (Auditability)**
  - 모든 변경에 `created_at`, `updated_at`, `created_by`, `updated_by` 컬럼 필수
  - 중요 테이블(payment, settlement)은 `audit_log` JSON 컬럼으로 이력 보존

- **확장성 (Extensibility)**
  - JSON 컬럼으로 유연한 속성 추가 (metadata, context)
  - 미래 채널(C, D) 추가 시 수정 최소화

---

## 4. 메타데이터 관리 (Metadata Management)

### 4.1 메타데이터 체계

**메타데이터 분류:**

```
┌───────────────────────────────────────────────────────┐
│         Metadata Categories                           │
├───────────────────────────────────────────────────────┤
│                                                       │
│ 1. Structural Metadata                              │
│    ├─ 테이블 정의: 컬럼명, 데이터 타입, 제약       │
│    ├─ 관계: FK, 1:N 매핑                           │
│    └─ 인덱스: PRIMARY KEY, UNIQUE, FOREIGN KEY    │
│                                                     │
│ 2. Operational Metadata                            │
│    ├─ 데이터 품질: NULL 비율, 유효성 범위          │
│    ├─ 처리 현황: 파이프라인 실행, 지연, 실패       │
│    └─ 성능: 테이블 크기, 조회 응답시간             │
│                                                     │
│ 3. Business Metadata                               │
│    ├─ 데이터 소유자: 담당 팀, 연락처                │
│    ├─ 비즈니스 정의: 용어, 계산식                   │
│    └─ 규제 요구사항: GDPR, PDPA, PCI-DSS 준수     │
│                                                     │
│ 4. Technical Metadata                              │
│    ├─ 저장소: 데이터베이스, 스키마, 파일 경로      │
│    ├─ 파이프라인: ETL/ELT 프로세스, 실행 일정     │
│    └─ 보안: 암호화, 접근 정책                      │
│                                                     │
└───────────────────────────────────────────────────────┘
```

### 4.2 메타데이터 저장소 (Data Catalog)

**권장 도구:** Apache Atlas, Collibra, or AWS Glue Catalog

**핵심 정보:**

| 메타데이터 | 저장 위치 | 관리자 | 갱신 주기 |
|-----------|---------|--------|---------|
| 테이블/컬럼 정의 | Data Catalog | Data Architect | 분기 1회 |
| 데이터 소유자 | CMDB / Slack | Data Governance | 월 1회 |
| 데이터 계보 (Lineage) | Atlas | Data Engineer | 실시간 |
| 품질 SLA | DQ Tool | DBA | 주 1회 |
| 접근 정책 | IAM / Keycloak | Security Officer | 변경 시 |

### 4.3 데이터 계보 (Data Lineage)

```
┌─────────────────────┐
│   TOC (Legacy)      │
│  (HiPass 기존 DB)   │
└──────────┬──────────┘
           │ API / ETL
           ▼
┌─────────────────────┐
│  toc_sync_log       │
│  (동기 로그)        │
└──────────┬──────────┘
           │ Kafka
           ▼
┌─────────────────────┐
│  trip_record (raw)  │
│  (원본 거래)        │
└──────────┬──────────┘
           │ Spark / Airflow
           ├─────────────┬─────────────┐
           ▼             ▼             ▼
    ┌─────────┐    ┌────────────┐    ┌──────────┐
    │settlement│   │payment_     │    │kpi_      │
    │(정산)    │   │attempt      │    │metrics   │
    │          │   │(결제 시도)  │    │(성과)    │
    └─────────┘    └────────────┘    └──────────┘
           │             │                 │
           └─────────────┼─────────────────┘
                         │ Reporting
                         ▼
                    ┌──────────┐
                    │BI Report │
                    │(대시보드)│
                    └──────────┘
```

---

## 5. 데이터 거버넌스 (Data Governance)

### 5.1 거버넌스 원칙

**5대 원칙:**

1. **Accountability (책임성)**
   - 모든 데이터는 명확한 소유자(owner)를 가짐
   - 소유자는 데이터 품질, 정확성, 보안 책임

2. **Transparency (투명성)**
   - 데이터 계보, 접근 정책 공개
   - 변경 이력 추적 가능

3. **Compliance (규제 준수)**
   - PDPA (Personal Data Protection Act 2010)
   - PCI-DSS (결제 데이터 보안)
   - ISO 27001 (정보보안)

4. **Quality (품질)**
   - 데이터 정확성 검증 (SLA 정의)
   - NULL 비율, 유효성 범위 모니터링

5. **Security (보안)**
   - 역할 기반 접근 제어 (RBAC)
   - 암호화 (전송 중, 저장 중)
   - 감사 로그 (모든 읽기/쓰기 기록)

### 5.2 데이터 소유자 및 책임

| 데이터 도메인 | 소유자 | 책임 | 주요 테이블 |
|-------------|--------|------|-----------|
| **Transaction** | Finance Manager | 거래 정확성, 정산 검증 | trip_record, payment_attempt |
| **Settlement** | Clearing Manager | 정산 완결, 은행 연동 | settlement, financial_transaction |
| **Reporting** | Data Analyst | 리포트 정확성, 성능 | aggregated_kpi, report_* |
| **Configuration** | Operations Director | 정책 변경 관리, 버전 제어 | config_master, policy_rule |
| **Integration** | Integration Manager | TOC 동기, 데이터 품질 | toc_sync_log, legacy_mapping |

### 5.3 데이터 접근 정책

**RBAC (Role-Based Access Control):**

```
┌─────────────────────────────────────────────────┐
│   Role: Toll Manager                            │
│   - 읽기: 해당 Plaza의 trip_record, lane_config│
│   - 쓰기: 없음                                   │
│   - 삭제: 없음                                   │
│   - 암호화: 데이터 마스킹 (민감 정보)           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│   Role: Regional Manager                        │
│   - 읽기: 지역 내 모든 Plaza + settlement       │
│   - 쓰기: settlement (승인)                      │
│   - 삭제: 없음                                   │
│   - 암호화: PII 마스킹                           │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│   Role: Finance Manager                         │
│   - 읽기: 모든 테이블 (R++)                      │
│   - 쓰기: settlement, financial_transaction     │
│   - 삭제: 승인 후 감사 로그 유지                │
│   - 암호화: 없음 (필요시 마스킹)                │
└─────────────────────────────────────────────────┘
```

### 5.4 데이터 품질 (DQ) 체계

**SLA 정의:**

| 메트릭 | 목표값 | 모니터링 | 위반 시 조치 |
|--------|--------|---------|-----------|
| **Completeness** | NULL < 0.5% | 일 1회 | 데이터 엔지니어 알림 |
| **Accuracy** | 거래 정확률 > 99.9% | 실시간 | 자동 재검증 트리거 |
| **Timeliness** | 데이터 지연 < 5분 | 매 10분 | 파이프라인 재실행 |
| **Consistency** | 테이블 간 동기 오류 < 10 | 시간 1회 | 수동 조정 |
| **Uniqueness** | 중복 거래 0 | 일 1회 | 감사 로그 기록 |

### 5.5 감사 및 규제 보고

**감시 체계:**

```
┌─────────────────────────────────────────────┐
│   Audit & Compliance                        │
├─────────────────────────────────────────────┤
│                                             │
│ 1. Change Audit                            │
│    - 모든 update/delete 기록 (audit_log)   │
│    - 변경자, 변경 시간, 이전값 저장         │
│    - 매월 변경 리뷰                         │
│                                             │
│ 2. Access Audit                            │
│    - 데이터 접근 로그 (read, write)         │
│    - 비정상 접근 탐지 (anomaly detection)   │
│    - 분기 1회 보고                          │
│                                             │
│ 3. Financial Audit                         │
│    - 결제 거래 감사 (SOX/PDPA)              │
│    - 미결제 추적 (Tier 1~4)                 │
│    - 분기별 외부 감시                       │
│                                             │
│ 4. Security Audit                          │
│    - 암호화 상태 점검                       │
│    - 접근 정책 검증                         │
│    - 연 2회 보안 감사                       │
│                                             │
└─────────────────────────────────────────────┘
```

---

## 6. 데이터 전략 로드맵

### 6.1 단계별 구현 계획

| Phase | 기간 | 목표 | 산출물 |
|-------|------|------|--------|
| **Phase 1** | M 1-3 | 핵심 ERD 설계 & 구현 | PostgreSQL 스키마, 메타데이터 카탈로그 구축 |
| **Phase 2** | M 4-6 | 파이프라인 & 품질 체계 | Airflow DAG, DQ Rules, 감사 로그 |
| **Phase 3** | M 7-9 | 확장성 & 성능 | 샤딩 계획, 캐싱 전략, 인덱스 최적화 |
| **Phase 4** | M 10-12 | 고가용성 & 재해복구 | 백업 전략, PITR, 이중화 구성 |

### 6.2 기술 스택

| 계층 | 도구 | 이유 |
|------|------|------|
| **OLTP** | PostgreSQL 14+ | 강력한 ACID, JSON 지원, 확장성 |
| **OLAP** | ClickHouse | 대용량 분석, 빠른 쿼리 |
| **ETL** | Apache Airflow | 복잡한 의존성 관리, 모니터링 |
| **Message Queue** | Kafka | 실시간 이벤트 스트림, 고처리량 |
| **Catalog** | Apache Atlas | 계보 추적, 메타데이터 관리 |
| **Monitoring** | Prometheus + Grafana | 실시간 성능 모니터링 |

---

## 7. 참고 문서

- `04_organization_roles.md` — 5단계 계층 및 BOS 권한
- `05_payment_architecture.md` — 결제 흐름 및 미결제 관리
- `02_system_architecture.md` — 시스템 아키텍처 (관계도)
- `03_technical_design.md` — 기술 설계 (구현 상세)

---

*Last updated: 2026-04-01 | Next review: 2026-05-01*
