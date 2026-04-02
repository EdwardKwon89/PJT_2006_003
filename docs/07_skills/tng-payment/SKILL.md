---
name: tng-payment
description: TnG eWallet Channel B batch settlement, TnG API authentication, ISO 20022 reconciliation
use_when:
  - TnG Channel B 배치 정산 로직을 구현할 때
  - TnG API mTLS 인증 설정 시
  - ISO 20022 pain.001 XML 생성 또는 파싱이 필요할 때
  - Phase 5 빌링 & 정산 개발 시
dont_use_when:
  - Channel A (직접 수납) 정산이 필요할 때 (clearing-center-operations 사용)
  - JPJ 연동이 필요할 때 (jpj-integration 사용)
---

# TnG 결제 연동

## 1. 개요

**TnG Digital (Touch 'n Go)** — 말레이시아 최대 디지털 지갑 및 RFID 결제 플랫폼. BOS는 TnG Channel B (eWallet) 트랜잭션을 매일 23:00에 배치 정산하고, ISO 20022 형식으로 Clearing API를 호출한다.

---

## 2. 핵심 내용

### 2.1 Channel B 결제 흐름

```
[차량 통과] → RFID 태그 인식
      │ TnG eWallet 잔액 차감 (TnG 시스템)
      │
      ▼
[BOS: raw.rfid.events] → 트랜잭션 생성 (channel='B')
      │
      ▼ (매일 23:00 배치)
[TnG Clearing API 호출] → ACK 수신 → 정산 완료
```

### 2.2 TnG API 인증

```yaml
# TnG API 연결 설정
endpoint: https://api.tngd.my/clearing/v1/batch
auth:
  type: mTLS
  client_cert: /certs/bos-tng-client.crt  # Vault에서 런타임 로드
  client_key:  /certs/bos-tng-client.key
  ca_cert:     /certs/tngd-ca.crt
timeout_seconds: 30
retry_max: 3
retry_backoff_base_ms: 300000  # 30분 간격
```

### 2.3 ISO 20022 pain.001.001.09 XML 구조

```xml
<?xml version="1.0" encoding="UTF-8"?>
<Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.09">
  <CstmrCdtTrfInitn>
    <GrpHdr>
      <MsgId>BOS-{batch_id}</MsgId>
      <CreDtTm>2026-04-02T23:00:00</CreDtTm>
      <NbOfTxs>15423</NbOfTxs>
      <CtrlSum>98450.20</CtrlSum>
      <InitgPty><Nm>JVC-BOS</Nm></InitgPty>
    </GrpHdr>
    <PmtInf>
      <PmtInfId>PMTINF-{date}-001</PmtInfId>
      <PmtMtd>TRF</PmtMtd>
      <CdtTrfTxInf>
        <!-- 개별 트랜잭션 목록 -->
        <PmtId><EndToEndId>{txn_id}</EndToEndId></PmtId>
        <Amt><InstdAmt Ccy="MYR">5.70</InstdAmt></Amt>
      </CdtTrfTxInf>
    </PmtInf>
  </CstmrCdtTrfInitn>
</Document>
```

### 2.4 배치 정산 Airflow DAG 스케줄

```python
# 매일 23:00 MYT 실행
schedule_interval = "0 23 * * *"

# DAG 태스크 순서
collect_tng_txns  ➜  build_iso20022_xml  ➜  submit_to_tng  ➜  verify_ack
```

### 2.5 ACK 검증 및 불일치 처리

```python
def verify_tng_ack(batch_id: str, ack: dict) -> None:
    bos_total = db.query("SELECT SUM(amount) FROM ... WHERE batch_id=?", batch_id)
    tng_total = ack["total_amount"]

    diff = abs(bos_total - tng_total)
    if diff > Decimal("1.00"):  # RM 1 초과 불일치
        alert_billing_lead_and_cfo(
            f"TnG ACK 불일치: BOS={bos_total}, TnG={tng_total}, 차이={diff}"
        )
        raise AckMismatchError(f"Amount mismatch: {diff}")
```

---

## 3. 예시 시나리오

**시나리오: TnG Clearing API 23:00 타임아웃 → 자동 재시도**
1. 23:00 배치 실행 → TnG API 30초 타임아웃
2. Airflow 자동 재시도: 23:30, 00:00 (최대 3회)
3. 00:00 재시도 성공 → ACK 수신 → 정산 완료
4. 실패 시: PagerDuty P1 + `billing-lead`/CFO 알림
5. 수동 재처리: `POST /api/v1/billing/tng-batch/{batchId}/retry`

---

## 4. 주의사항 & 함정

- **중복 배치 방지**: `tng_settlement_batch` 테이블에서 당일 `batch_id` 존재 여부 확인 후 실행 (Idempotent)
- **XML 금액 형식**: `Ccy="MYR"` 속성 필수. 형식 오류 시 TnG API 4xx 오류
- **배치 실패 후 재처리**: 원본 `batch_id`로 재시도 (새 ID 생성 금지 — 중복 청구 위험)

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 정산 센터 운영 | [`../clearing-center-operations/SKILL.md`](../clearing-center-operations/SKILL.md) |
| 결제 아키텍처 | [`../../docs/01_business/05_payment_architecture.md`](../../docs/01_business/05_payment_architecture.md) |
| Phase 5 빌링 | [`../../docs/06_phases/05_phase05_billing.md`](../../docs/06_phases/05_phase05_billing.md) |
