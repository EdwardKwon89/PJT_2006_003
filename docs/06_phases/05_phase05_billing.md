# Phase 5: 빌링 & 정산
## 06_phases/05_phase05_billing.md
## v1.0 | 2026-04 | 참조: 02_system/02_service_domains.md, 01_business/05_payment_architecture.md

---

> **Agent 사용 지침**
> `billing-lead`, `billing-dev` Agent가 정산 및 빌링 구현 시 반드시 로드.
> 본 문서는 Phase 5 실행의 유일한 정식 기준 문서이며, 수수료 계산·배치 정산·리포트 생성의 구현 기준으로 사용된다.
> 금액 산출 로직 및 정산 배치 코드는 반드시 `billing-lead` + `CFO` 검토 후 머지한다.

---

## 1. Phase 개요

### 1.1 목적 및 범위

Phase 5는 Malaysia SLFF/MLFF Tolling BOS의 **빌링 & 정산 도메인**을 구축하는 단계다. Phase 3의 트랜잭션 엔진이 발행한 `processed.txn.events`와 Phase 4의 계정·잔액 정보를 기반으로, 콘세셔네어별 일별 수납 집계, JVC 수수료 차감, TnG Channel B 배치 정산, Clearing Center Reconciliation, 정산 리포트 자동 생성, FPX 온라인 결제 연동을 완성한다.

**핵심 목표:**
- 콘세셔네어별 일별 수납 집계 자동화 (T+1 23:59 완료)
- JVC 수수료 3~12% 정확 차감 및 감사 추적
- TnG Channel B 배치 정산 (매일 23:00, 야간 배치)
- Clearing Center Reconciliation 자동화
- 법인·플릿 계정 자동 인보이스 생성
- FPX 실시간 결제 게이트웨이 연동

### 1.2 Phase 연계

| 구분 | 내용 |
|------|------|
| **선행 Phase** | Phase 3 — 트랜잭션 처리 엔진 (`processed.txn.events` 토픽 완료 필수) / Phase 4 — 계정 서비스 (계정·잔액 API 완료 필수) |
| **후행 Phase** | Phase 6 — 위반 & 미납 관리 (정산 완료 상태 기반 미납 탐지) |
| **예상 기간** | **3주** (Sprint 10~12) |
| **병렬 가능 작업** | 일별 집계 배치 개발 ↔ FPX 결제 연동 개발 (독립 진행 후 통합) |

### 1.3 아키텍처 포지션

```
[Kafka: processed.txn.events]
          │
          ▼
┌──────────────────────────────────────┐
│            billing-service           │  ← Phase 5 구현 영역
│                                      │
│  ┌──────────────────────────────┐   │
│  │  Daily Aggregation Engine    │   │  콘세셔네어별 일별 집계
│  ├──────────────────────────────┤   │
│  │  JVC Fee Calculator          │   │  수수료 3~12% 차감
│  ├──────────────────────────────┤   │
│  │  TnG Settlement Batch        │   │  Channel B 배치 정산
│  ├──────────────────────────────┤   │
│  │  Clearing Reconciliation     │   │  Clearing Center 대사
│  ├──────────────────────────────┤   │
│  │  Invoice Generator           │   │  법인·플릿 인보이스
│  ├──────────────────────────────┤   │
│  │  FPX Payment Gateway         │   │  온라인 결제 연동
│  └──────────────────────────────┘   │
│                                      │
│  [PostgreSQL: billing_*]             │
│  [Apache Airflow: DAG 관리]          │
│  [S3: 리포트 아카이브]               │
└──────────────────────────────────────┘
          │
    ┌─────┴──────┐
    ▼            ▼
[Phase 6]   [JVC CFO Dashboard]
[violation]  (정산 현황 실시간 조회)
```

### 1.4 수수료 정책 요약

| 콘세셔네어 유형 | JVC 수수료율 | 정산 주기 | 비고 |
|--------------|------------|---------|------|
| 소규모 운영사 (월 <RM 1M) | 12% | 월 1회 | 후불 청구 |
| 중규모 운영사 (월 RM 1M~5M) | 8% | 15일 1회 | |
| 대규모 운영사 (월 >RM 5M) | 5% | 주 1회 | |
| TnG eWallet (Channel B) | 3% | 일 1회 배치 | 별도 정산 계약 |
| 정부 기관 (GOV) | 0% | 월말 청구 | 후불 |

---

## 2. 담당 Agent 및 역할 분담

### 2.1 Phase 5 참여 Agent

| Agent | 역할 | 주요 책임 |
|-------|------|---------|
| `billing-lead` | 기술 리드 | 아키텍처 설계, 수수료 계산 로직 설계, 코드 리뷰 총괄 |
| `billing-dev-1` | 개발 담당 1 | Daily Aggregation Engine, JVC Fee Calculator, Airflow DAG |
| `billing-dev-2` | 개발 담당 2 | TnG Settlement Batch, Clearing Reconciliation, FPX 연동 |
| `CFO` | 비즈니스 검토 | 수수료율 정책 확인, 정산 리포트 형식 승인, 인보이스 양식 검토 |

### 2.2 협업 인터페이스

| 협업 대상 Agent | 협업 내용 |
|---------------|---------|
| `txn-lead` | `processed.txn.events` 스키마 최종 확정, 집계 키 필드 검증 |
| `account-lead` | 계정별 정산 그룹핑 키, 법인·플릿 인보이스 수신처 정보 |
| `violation-lead` | 정산 완료/미완료 기준 공유, 미납 탐지 조건 정의 |
| `devops-lead` | Airflow 환경 구성, S3 버킷 IAM 정책, FPX 크리덴셜 Vault 관리 |

---

## 3. 주요 태스크 체크리스트

### 3.1 billing-service 구현

#### 3.1.1 서비스 기본 구조

- [ ] `billing-service` Spring Boot 프로젝트 초기화
  - 의존성: Spring Kafka, Spring Data JPA, Resilience4j, Airflow REST Client
  - PostgreSQL 스키마: `billing_*` 테이블 (Flyway 마이그레이션)
- [ ] Kafka Consumer 설정 (`processed.txn.events` 구독)
  - Consumer Group: `billing-aggregation-group`
  - `enable.auto.commit: false` (수동 커밋)
  - 처리 실패 시 Dead Letter Topic 발행 (`billing.dlq`)
- [ ] API 게이트웨이 등록 (`/api/v1/billing/**`)
- [ ] Health Check & Actuator 엔드포인트 구성

#### 3.1.2 주요 API 엔드포인트

| 메서드 | 경로 | 설명 |
|-------|------|------|
| GET | `/api/v1/billing/daily-summary` | 일별 수납 집계 조회 |
| GET | `/api/v1/billing/invoices/{id}` | 인보이스 상세 조회 |
| POST | `/api/v1/billing/invoices/{id}/resend` | 인보이스 재발송 |
| GET | `/api/v1/billing/reconciliation/status` | Clearing 대사 현황 |
| POST | `/api/v1/billing/topup/fpx/initiate` | FPX 결제 시작 |
| GET | `/api/v1/billing/topup/fpx/{sessionId}/status` | FPX 결제 상태 조회 |

---

### 3.2 일별 수납 집계 (콘세셔네어별)

- [ ] `DailyAggregationConsumer` 구현 — Kafka 이벤트 소비 및 실시간 집계
  - 키: `(concessionaire_id, business_date, vehicle_class, channel)`
  - 집계 항목: `txn_count`, `gross_amount`, `jvc_fee_amount`, `net_amount`
  - Redis 임시 집계 후 자정 PostgreSQL Flush
- [ ] `daily_settlement_summary` 테이블 설계 및 마이그레이션
  ```sql
  CREATE TABLE daily_settlement_summary (
      id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
      concessionaire_id UUID NOT NULL,
      business_date   DATE NOT NULL,
      vehicle_class   SMALLINT NOT NULL,  -- 1~5
      channel         VARCHAR(10) NOT NULL, -- 'A', 'B'
      txn_count       INTEGER NOT NULL DEFAULT 0,
      gross_amount    NUMERIC(15,2) NOT NULL DEFAULT 0,
      jvc_fee_rate    NUMERIC(5,4) NOT NULL,
      jvc_fee_amount  NUMERIC(15,2) NOT NULL DEFAULT 0,
      net_amount      NUMERIC(15,2) NOT NULL DEFAULT 0,
      status          VARCHAR(20) NOT NULL DEFAULT 'DRAFT',
      created_at      TIMESTAMPTZ DEFAULT now(),
      finalized_at    TIMESTAMPTZ,
      UNIQUE (concessionaire_id, business_date, vehicle_class, channel)
  );
  ```
- [ ] 일별 집계 Finalize 배치 (매일 01:00 — 전일 집계 확정)
  - 상태 `DRAFT` → `FINALIZED` 전이
  - 수정 불가 Lock 적용
- [ ] 집계 수정 요청 워크플로우 (예외 처리, 감사 로그 필수)

---

### 3.3 JVC 수수료 차감 (3~12%)

- [ ] `JvcFeeCalculator` 구현
  - 콘세셔네어별 수수료율 조회 (DB 마스터 테이블)
  - 수수료율 변경 이력 관리 (이력 테이블 + 유효 기간 관리)
  - 반올림 정책: HALF_UP, 소수점 2자리
- [ ] 수수료율 변경 API (`PUT /api/v1/billing/fee-rates/{concessionaireId}`)
  - 변경 예약 (미래 적용일 지정 가능)
  - `CFO` 승인 필수 (2단계 승인)
- [ ] 수수료 감사 추적
  - 모든 수수료 계산 결과 `jvc_fee_audit_log` 테이블 기록
  - Hyperledger Fabric 감사 로그 발행 (금액 변경 이벤트)
- [ ] 월말 JVC 수수료 정산서 자동 생성 (PDF, 콘세셔네어별)

---

### 3.4 TnG Channel B 배치 정산 (일 1회 23:00)

- [ ] `TngSettlementBatch` Airflow DAG 구현
  - 스케줄: `0 23 * * *` (매일 23:00 MYT)
  - 처리 대상: 당일 Channel B (`TNG_EWALLET`) 트랜잭션 전체
- [ ] TnG Clearing API 연동
  - 엔드포인트: `https://api.tngd.my/clearing/v1/batch`
  - 인증: mTLS (클라이언트 인증서)
  - 요청 형식: ISO 20022 XML (pain.001.001.09)
  - 응답 처리: ACK 수신 후 `batch_id` 기록
- [ ] 배치 결과 저장 (`tng_settlement_batch` 테이블)
  - `batch_id`, `business_date`, `total_txn_count`, `total_amount`, `status`, `ack_received_at`
- [ ] 배치 실패 처리
  - 자동 재시도: 최대 3회 (30분 간격)
  - 3회 실패 시: `billing-lead` + `CFO` 즉시 알림 (PagerDuty)
  - 수동 재처리 API: `POST /api/v1/billing/tng-batch/{batchId}/retry`
- [ ] TnG ACK 불일치 탐지 (당사 집계 ↔ TnG 응답 금액 차이 > RM 1 시 알림)

---

### 3.5 Clearing Center Reconciliation

- [ ] `ClearingReconciliationJob` 구현 (매일 02:00 배치)
  - 처리 흐름: BOS 집계 데이터 vs Clearing Center 수신 데이터 대사
  - 대사 기준: `txn_id`, `amount`, `processed_at`
- [ ] 대사 결과 분류
  - `MATCHED`: 완전 일치
  - `AMOUNT_MISMATCH`: 금액 불일치
  - `MISSING_IN_CLEARING`: BOS 기록 있음, Clearing 없음
  - `MISSING_IN_BOS`: Clearing 기록 있음, BOS 없음
- [ ] 불일치 건 예외 처리 워크플로우
  - 불일치 건 `reconciliation_exceptions` 테이블 기록
  - `review-lead` Agent 수동 심사 큐 자동 등록
  - SLA: 불일치 발생 후 2 영업일 내 해결
- [ ] Reconciliation 대시보드 API
  - `GET /api/v1/billing/reconciliation/summary?date={YYYY-MM-DD}`
  - 일치율, 불일치 건수, 불일치 금액 집계 반환

---

### 3.6 정산 리포트 자동 생성

- [ ] 리포트 생성 Airflow DAG (`billing_report_generator`)
  - 일별 리포트: 매일 03:00 생성 (전일 집계 기반)
  - 월별 리포트: 매월 1일 04:00 생성 (전월 집계 기반)
- [ ] 리포트 형식
  - PDF: 콘세셔네어용 정산서 (인보이스 첨부)
  - CSV: JVC 내부용 원장 데이터
  - Excel: CFO 경영 보고용
- [ ] 리포트 저장 및 배포
  - S3 버킷 저장 (`s3://bos-reports/{concessionaire_id}/{year}/{month}/`)
  - 이메일 자동 발송 (콘세셔네어 담당자, JVC CFO)
  - Portal 다운로드 링크 (서명된 URL, 유효기간 7일)
- [ ] 법인·플릿 계정 인보이스 생성
  - GST 포함 세금계산서 (GST 6%)
  - 자동 이메일 발송 (등록된 법인 담당자)
  - 인보이스 번호 형식: `INV-{YYYYMM}-{concessionaireCode}-{sequence}`

---

### 3.7 FPX 온라인 결제 연동

- [ ] FPX Payment Gateway 설정
  - 제공사: PayNet Malaysia (FPX)
  - 지원 은행: Maybank2u, CIMB Clicks, RHB Now, HLB Connect 등 (28개 은행)
  - 최소 결제 금액: RM 1
  - 최대 결제 금액: 개인 RM 30,000 / 법인 RM 1,000,000
- [ ] FPX 결제 시작 API (`POST /api/v1/billing/topup/fpx/initiate`)
  - 입력: `accountId`, `amount`, `bankCode`, `callbackUrl`
  - 출력: `sessionId`, `fpxTransactionId`, `redirectUrl` (은행 페이지)
- [ ] FPX 콜백 처리 엔드포인트 (`POST /api/v1/billing/topup/fpx/callback`)
  - FPX 전자서명 검증 (SHA-256 HMAC)
  - 결제 성공 시 잔액 충전 이벤트 발행 (`account.balance.topup` 토픽)
  - Idempotency: `fpx_txn_id` 기준 중복 처리 방지
- [ ] FPX 결제 상태 조회 API (`GET /api/v1/billing/topup/fpx/{sessionId}/status`)
  - 상태: `PENDING`, `SUCCESS`, `FAILED`, `TIMEOUT`
  - 타임아웃: 15분 (콜백 미수신 시 자동 `TIMEOUT` 처리)
- [ ] FPX 거래 내역 저장 (`fpx_transactions` 테이블)
  - 7년 보관 (금융 감사 규정 준수)

---

## 4. 정산 플로우 다이어그램

```
매일 자정 (00:00 MYT)
         │
         ▼
[Redis 임시 집계] ─── Flush ──► [daily_settlement_summary: DRAFT]
         │
         │ 01:00 Airflow DAG: daily_finalize
         ▼
[DRAFT → FINALIZED] ──► JVC Fee 계산 적용
         │
         │ 02:00 Airflow DAG: clearing_reconciliation
         ▼
[BOS 집계 vs Clearing Center 대사]
    │            │
  MATCHED    MISMATCH
    │            │
    ▼            ▼
 OK 기록    예외 큐 등록 → review-lead 심사
         │
         │ 03:00 Airflow DAG: billing_report_generator
         ▼
[일별 정산 리포트 생성]
  ├── PDF (콘세셔네어용 정산서)
  ├── CSV (JVC 내부 원장)
  └── Excel (CFO 경영 보고)
         │
         ▼
  [S3 저장] + [이메일 발송]

별도 스케줄: 23:00 Airflow DAG: tng_settlement_batch
         │
         ▼
[TnG Channel B 당일 트랜잭션 집계]
         │
         ▼
[TnG Clearing API 호출 (ISO 20022 XML)]
         │
    ┌────┴────┐
   ACK       NACK / 실패
    │            │
    ▼            ▼
  완료 기록    재시도(최대 3회) → 실패 시 PagerDuty
```

---

## 5. 배치 집계 Airflow DAG 예시

### 5.1 일별 집계 Finalize DAG

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pendulum

LOCAL_TZ = pendulum.timezone("Asia/Kuala_Lumpur")

default_args = {
    "owner": "billing-dev-1",
    "depends_on_past": False,
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": ["billing-alerts@bos.jvc.my"],
}

with DAG(
    dag_id="daily_settlement_finalize",
    default_args=default_args,
    description="일별 수납 집계 확정 및 JVC 수수료 계산",
    schedule_interval="0 1 * * *",  # 매일 01:00 MYT
    start_date=datetime(2026, 4, 1, tzinfo=LOCAL_TZ),
    catchup=False,
    tags=["billing", "settlement"],
) as dag:

    def flush_redis_to_postgres(**context):
        """Redis 임시 집계 → PostgreSQL Flush"""
        business_date = context["ds"]  # YYYY-MM-DD (전날)
        hook = PostgresHook(postgres_conn_id="bos_billing_db")
        hook.run(
            """
            INSERT INTO daily_settlement_summary
                (concessionaire_id, business_date, vehicle_class, channel,
                 txn_count, gross_amount, jvc_fee_rate, jvc_fee_amount, net_amount, status)
            SELECT
                r.concessionaire_id,
                %(business_date)s::DATE,
                r.vehicle_class,
                r.channel,
                r.txn_count,
                r.gross_amount,
                fr.fee_rate,
                ROUND(r.gross_amount * fr.fee_rate, 2) AS jvc_fee_amount,
                r.gross_amount - ROUND(r.gross_amount * fr.fee_rate, 2) AS net_amount,
                'DRAFT'
            FROM redis_daily_aggregate r
            JOIN jvc_fee_rates fr
                ON fr.concessionaire_id = r.concessionaire_id
                AND fr.effective_date <= %(business_date)s::DATE
                AND (fr.end_date IS NULL OR fr.end_date > %(business_date)s::DATE)
            WHERE r.business_date = %(business_date)s::DATE
            ON CONFLICT (concessionaire_id, business_date, vehicle_class, channel)
            DO NOTHING;
            """,
            parameters={"business_date": business_date},
        )

    def finalize_daily_summary(**context):
        """DRAFT → FINALIZED 상태 전이"""
        business_date = context["ds"]
        hook = PostgresHook(postgres_conn_id="bos_billing_db")
        hook.run(
            """
            UPDATE daily_settlement_summary
            SET status = 'FINALIZED', finalized_at = now()
            WHERE business_date = %(business_date)s::DATE
              AND status = 'DRAFT';
            """,
            parameters={"business_date": business_date},
        )

    def verify_finalization(**context):
        """집계 확정 검증 — DRAFT 잔존 건 알림"""
        business_date = context["ds"]
        hook = PostgresHook(postgres_conn_id="bos_billing_db")
        records = hook.get_records(
            """
            SELECT COUNT(*) FROM daily_settlement_summary
            WHERE business_date = %(business_date)s::DATE
              AND status = 'DRAFT';
            """,
            parameters={"business_date": business_date},
        )
        draft_count = records[0][0]
        if draft_count > 0:
            raise ValueError(
                f"[ALERT] {business_date} 집계 중 DRAFT 상태 잔존: {draft_count}건"
            )

    t1 = PythonOperator(
        task_id="flush_redis_to_postgres",
        python_callable=flush_redis_to_postgres,
    )

    t2 = PythonOperator(
        task_id="finalize_daily_summary",
        python_callable=finalize_daily_summary,
    )

    t3 = PythonOperator(
        task_id="verify_finalization",
        python_callable=verify_finalization,
    )

    t1 >> t2 >> t3
```

### 5.2 TnG Channel B 배치 정산 DAG

```python
with DAG(
    dag_id="tng_channel_b_settlement",
    default_args=default_args,
    description="TnG Channel B 일별 배치 정산 (ISO 20022)",
    schedule_interval="0 23 * * *",  # 매일 23:00 MYT
    start_date=datetime(2026, 4, 1, tzinfo=LOCAL_TZ),
    catchup=False,
    tags=["billing", "tng", "settlement"],
) as tng_dag:

    def collect_tng_transactions(**context):
        """당일 Channel B 트랜잭션 수집"""
        business_date = context["ds"]
        hook = PostgresHook(postgres_conn_id="bos_billing_db")
        rows = hook.get_records(
            """
            SELECT txn_id, account_id, amount, processed_at
            FROM processed_transactions
            WHERE channel = 'B'
              AND business_date = %(business_date)s::DATE
              AND tng_batch_id IS NULL
            ORDER BY processed_at;
            """,
            parameters={"business_date": business_date},
        )
        context["ti"].xcom_push(key="tng_txns", value=rows)

    def build_iso20022_xml(**context):
        """ISO 20022 pain.001.001.09 XML 생성"""
        txns = context["ti"].xcom_pull(key="tng_txns")
        # XML 생성 로직 (별도 유틸리티 함수)
        xml_payload = _build_pain001_xml(txns)
        context["ti"].xcom_push(key="xml_payload", value=xml_payload)

    def submit_to_tng_clearing(**context):
        """TnG Clearing API 호출"""
        import requests
        xml_payload = context["ti"].xcom_pull(key="xml_payload")
        response = requests.post(
            "https://api.tngd.my/clearing/v1/batch",
            data=xml_payload,
            cert=("/certs/bos-client.crt", "/certs/bos-client.key"),
            timeout=30,
        )
        response.raise_for_status()
        ack = response.json()
        context["ti"].xcom_push(key="batch_id", value=ack["batchId"])

    t_collect = PythonOperator(
        task_id="collect_tng_transactions",
        python_callable=collect_tng_transactions,
    )
    t_xml = PythonOperator(
        task_id="build_iso20022_xml",
        python_callable=build_iso20022_xml,
    )
    t_submit = PythonOperator(
        task_id="submit_to_tng_clearing",
        python_callable=submit_to_tng_clearing,
    )

    t_collect >> t_xml >> t_submit
```

---

## 6. 완료 기준 체크리스트

### 6.1 기능 완료 기준

| 영역 | 기준 항목 | 검증 방법 |
|------|---------|---------|
| 일별 집계 | 전일 데이터 T+1 01:30 이전 FINALIZED | Airflow DAG 실행 이력 확인 |
| JVC 수수료 | 수수료율별 계산 정확도 | 수동 산출값과 대조 테스트 (100건) |
| TnG 배치 | 23:00 배치 실행 → ACK 수신 | TnG 테스트 환경 연동 시뮬레이션 |
| Clearing 대사 | 불일치 건 자동 예외 큐 등록 | 의도적 불일치 데이터 주입 테스트 |
| 리포트 생성 | 일별 PDF·CSV·Excel 생성 및 S3 업로드 | 생성 파일 형식·내용 검증 |
| FPX 결제 | 결제 시작 → 콜백 → 잔액 반영 E2E | FPX 테스트 환경 실거래 시뮬레이션 |

### 6.2 성능 기준

| 지표 | 목표값 |
|------|-------|
| 일별 집계 처리 시간 (100만 건 기준) | < 20분 |
| TnG 배치 전송 시간 (10만 건 XML) | < 5분 |
| Clearing 대사 처리 시간 | < 10분 |
| 리포트 생성 시간 (전체 콘세셔네어) | < 30분 |
| FPX 결제 시작 API P99 | < 500ms |

### 6.3 테스트 커버리지 기준

- [ ] 단위 테스트 커버리지 ≥ 80% (billing-service 전 모듈)
- [ ] JVC 수수료 계산 경계값 테스트 (최소·최대 요금, 반올림 정책)
- [ ] TnG ISO 20022 XML 형식 검증 테스트
- [ ] FPX 콜백 전자서명 검증 단위 테스트
- [ ] Clearing 대사 4가지 결과 분류 시나리오 테스트
- [ ] Airflow DAG 단위 테스트 (각 Task 독립 실행 검증)

---

## 7. 리스크 & 대응

### 7.1 주요 리스크

| 리스크 | 가능성 | 영향 | 대응 방안 |
|-------|-------|------|---------|
| TnG Clearing API 야간 다운타임 | 중간 | 높음 | 자동 재시도 3회 (30분 간격), 실패 시 PagerDuty 알림 + 수동 재처리 API |
| 수수료율 오류 적용 (대규모 과금 오류) | 낮음 | 매우 높음 | 수수료율 변경 시 `CFO` 2단계 승인 필수, 이력 테이블 + 롤백 API |
| 집계 중복 처리 (Kafka 재처리) | 중간 | 높음 | Idempotency Key (`txn_id` 기준) + UPSERT ON CONFLICT DO NOTHING |
| FPX 콜백 위변조 | 낮음 | 매우 높음 | SHA-256 HMAC 서명 검증, IP 화이트리스트 (PayNet IP 대역) |
| S3 리포트 파일 접근 권한 유출 | 낮음 | 높음 | 서명된 URL (TTL 7일), 버킷 퍼블릭 액세스 전면 차단 |
| Airflow DAG 실패 후 재처리 중복 | 중간 | 중간 | 모든 DAG Task에 멱등성 보장 (UPSERT 패턴), 재처리 로그 기록 |

### 7.2 재무 리스크 대응

| 리스크 | 대응 |
|-------|------|
| 집계 금액 오류 → 콘세셔네어 손실 | 수정 요청 워크플로우 + 24시간 내 조정 정산 |
| TnG ACK 불일치 → 이중 청구 | 대사 결과 불일치 > RM 1 시 즉시 `billing-lead` + `CFO` 알림 |
| 수수료 과소 차감 → JVC 손실 | 월말 수수료 총액 검증 배치 (집계 합계 vs 실제 차감 비교) |

---

## 8. GSD 명령어 / 참조 문서

### 8.1 GSD 실행 명령어

```bash
# Phase 5 시작
/gsd:execute-phase phase=5 agents="billing-lead,billing-dev-1,billing-dev-2,CFO"

# Phase 5 진행 상황 확인
/gsd:progress phase=5

# Phase 5 완료 검증
/gsd:verify-work phase=5

# 정산 배치 UAT 실행
/gsd:audit-uat scenario="billing-batch-uat" phase=5

# FPX 결제 연동 시뮬레이션
/gsd:audit-uat scenario="fpx-payment-simulation" phase=5
```

### 8.2 참조 문서

| 문서 | 경로 | 참조 목적 |
|------|------|---------|
| 결제 아키텍처 | `01_business/05_payment_architecture.md` | Channel A/B 구조, 수수료 정책, TnG 정산 계약 |
| 서비스 도메인 설계 | `02_system/02_service_domains.md` | billing-service 도메인 경계, API 설계 |
| 데이터 모델 | `03_data/02_data_model.md` | billing_*, fpx_transactions 테이블 구조 |
| 메타데이터 용어 사전 | `03_data/04_metadata_glossary.md` | 정산 관련 코드 값 표준 (상태 코드 등) |
| 외부 연동 명세 | `02_system/05_external_integration.md` | TnG API, FPX PayNet API 사양 |
| Phase 3 트랜잭션 처리 | `06_phases/03_phase03_txn.md` | `processed.txn.events` 스키마, Outbox Pattern |
| Phase 4 계정 관리 | `06_phases/04_phase04_account.md` | 계정별 정산 그룹핑, 잔액 충전 API |

---

*Malaysia SLFF/MLFF Tolling BOS — Phase 5 빌링 & 정산 v1.0*
*생성일: 2026-04 | 담당: billing-lead, billing-dev×2, CFO*
