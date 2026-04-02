# BOS API & MCP Server 명세
## 02_system/06_api_mcp_spec.md
## v1.0 | 2026-04 | 참조: 01_system_overview.md, 02_service_domains.md, 05_external_integration.md

---

> **Agent 사용 지침**
> API Architect, Paperclip Agent가 API 설계 또는 MCP Tool 사용 시 반드시 로드.
> 엔드포인트 추가·변경 전 이 문서의 네이밍 정책 및 버전 관리 규칙 준수 필수.
> MCP Tool은 JVC 내부망 전용 — 외부 노출 절대 불가.

---

## 1. Executive Summary

BOS는 두 가지 독립적인 API 인터페이스를 제공한다.

| 항목 | External REST API | BOS MCP Server |
|------|-------------------|----------------|
| **대상** | TOC (유료도로 운영사) | Paperclip 29개 AI Agent |
| **방향** | 외부 → BOS (읽기 전용) | 내부 Agent → BOS |
| **인증** | X-API-Key + IP Whitelist | mTLS (JVC 내부망) |
| **범위** | 트랜잭션·계정·정산·장비·보고서 조회 | 전체 10개 도메인 조회 + 심사 요청 |
| **응답 SLA** | < 200ms P99 | < 5초 |
| **Rate Limit** | 1,000 RPM | 없음 (내부) |
| **버전** | /api/v1/ (12개월 하위 호환) | 내부 버전 관리 |
| **보안** | AWS WAF + API Gateway | JVC 내부망 전용 |

---

## 2. 공통 설계 원칙

### 2.1 RESTful 네이밍 정책

```
규칙:
  - 리소스명: 복수형 명사 (transactions, accounts, violations)
  - 동사 사용 금지: /getTransaction (X) → /transactions/{id} (O)
  - 계층 구조: /api/v1/{resource}/{id}/{sub-resource}
  - 쿼리 파라미터: camelCase (startDate, concessionaireId)
  - 응답 필드: camelCase (transactionId, vehiclePlate)

예시:
  GET  /api/v1/transactions                     — 트랜잭션 목록
  GET  /api/v1/transactions/{id}                — 트랜잭션 단건
  GET  /api/v1/accounts/{id}/summary            — 계정 요약
  GET  /api/v1/violations                       — 위반 목록
  GET  /api/v1/billings/settlements             — 정산 현황
  GET  /api/v1/equipments/{id}/status           — 장비 상태
```

### 2.2 공통 응답 Envelope

모든 API 응답은 아래 형식을 따른다.

```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "meta": {
    "timestamp": "2026-04-02T09:00:00+08:00",
    "requestId": "req-uuid-1234",
    "version": "v1"
  }
}
```

**오류 응답 예시:**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "TXN_NOT_FOUND",
    "message": "Transaction not found",
    "details": "transaction_id: TXN-2026-001234"
  },
  "meta": {
    "timestamp": "2026-04-02T09:00:00+08:00",
    "requestId": "req-uuid-5678",
    "version": "v1"
  }
}
```

### 2.3 공통 에러 코드

| HTTP 상태 | 에러 코드 | 설명 |
|-----------|-----------|------|
| 400 | INVALID_REQUEST | 요청 파라미터 오류 |
| 401 | UNAUTHORIZED | 인증 실패 (API Key 없음) |
| 403 | FORBIDDEN | 권한 없음 (IP Whitelist 미포함) |
| 404 | NOT_FOUND | 리소스 없음 |
| 429 | TOO_MANY_REQUESTS | Rate Limit 초과 |
| 500 | INTERNAL_ERROR | 서버 내부 오류 |
| 503 | SERVICE_UNAVAILABLE | Circuit Breaker Open |

### 2.4 페이지네이션 (Cursor 기반)

```json
GET /api/v1/transactions?limit=50&cursor=eyJpZCI6MTAwfQ==

응답:
{
  "success": true,
  "data": {
    "items": [ ... ],
    "pagination": {
      "cursor": "eyJpZCI6MTUwfQ==",
      "hasMore": true,
      "limit": 50,
      "total": 1200
    }
  }
}
```

---

## 3. External REST API 명세 (TOC용)

### 3.1 기본 정보

```
Base URL:    https://api.bos.jvc.my/api/v1
인증:        X-API-Key: {key} 헤더 + IP Whitelist
Content-Type: application/json
Charset:     UTF-8
Rate Limit:  1,000 RPM per API Key
SLA:         < 200ms P99
```

### 3.2 인증 방식

```http
GET /api/v1/transactions HTTP/1.1
Host: api.bos.jvc.my
X-API-Key: bos_toc_key_abc123xyz
X-Concessionaire-Id: TOC-001
Accept: application/json
```

**IP Whitelist 설정:**
- TOC별로 허용 IP 대역 사전 등록 (AWS API Gateway Resource Policy)
- 미등록 IP → 403 FORBIDDEN 즉시 반환

**Rate Limit 응답 헤더:**
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 987
X-RateLimit-Reset: 1743555600
Retry-After: 60
```

### 3.3 엔드포인트 목록

#### 3.3.1 Transactions

**GET /api/v1/transactions**
트랜잭션 목록 조회 (TOC 소속 콘세셔네어 범위 내)

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| startDate | string | ✓ | 시작일 (YYYY-MM-DD) |
| endDate | string | ✓ | 종료일 (YYYY-MM-DD, 최대 7일 범위) |
| plazaId | string | - | 플라자 ID 필터 |
| channel | string | - | A 또는 B |
| status | string | - | SUCCESS, FAILED, PENDING |
| limit | integer | - | 기본 50, 최대 200 |
| cursor | string | - | 페이지네이션 커서 |

```json
응답 예시:
{
  "success": true,
  "data": {
    "items": [
      {
        "transactionId": "TXN-2026-001234",
        "plazaId": "PLUS-001",
        "laneId": "LANE-03",
        "vehiclePlate": "WXY1234A",
        "channel": "A",
        "amount": 2.50,
        "currency": "MYR",
        "status": "SUCCESS",
        "processedAt": "2026-04-02T08:30:00+08:00"
      }
    ],
    "pagination": {
      "cursor": "eyJpZCI6MTAwfQ==",
      "hasMore": true,
      "limit": 50,
      "total": 5420
    }
  }
}
```

**GET /api/v1/transactions/{transactionId}**
트랜잭션 단건 상세 조회

```json
응답 예시:
{
  "success": true,
  "data": {
    "transactionId": "TXN-2026-001234",
    "plazaId": "PLUS-001",
    "laneId": "LANE-03",
    "vehiclePlate": "WXY1234A",
    "rfidTagId": "TAG-ABC-9876",
    "channel": "A",
    "tollClass": 1,
    "amount": 2.50,
    "currency": "MYR",
    "status": "SUCCESS",
    "anprConfidence": 0.98,
    "processedAt": "2026-04-02T08:30:00+08:00",
    "entryPlaza": null,
    "exitPlaza": null,
    "isMlff": false
  }
}
```

#### 3.3.2 Accounts

**GET /api/v1/accounts/{accountId}/summary**
계정 요약 조회 (잔액, 차량 수, 최근 거래)

```json
응답 예시:
{
  "success": true,
  "data": {
    "accountId": "ACC-001234",
    "accountType": "INDIVIDUAL",
    "balance": 45.20,
    "currency": "MYR",
    "vehicleCount": 2,
    "lastTransactionAt": "2026-04-02T08:30:00+08:00",
    "status": "ACTIVE"
  }
}
```

#### 3.3.3 Violations

**GET /api/v1/violations**
위반 목록 조회

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| startDate | string | ✓ | 시작일 |
| endDate | string | ✓ | 종료일 |
| violationType | string | - | NO_TAG, UNPAID, BLACKLIST |
| status | string | - | OPEN, RESOLVED, ESCALATED |
| limit | integer | - | 기본 50, 최대 200 |

```json
응답 예시:
{
  "success": true,
  "data": {
    "items": [
      {
        "violationId": "VIO-2026-005678",
        "vehiclePlate": "XYZ9876B",
        "violationType": "NO_TAG",
        "amount": 50.00,
        "currency": "MYR",
        "status": "OPEN",
        "detectedAt": "2026-04-01T14:20:00+08:00",
        "plazaId": "PLUS-002",
        "anprImageAvailable": true
      }
    ]
  }
}
```

**GET /api/v1/violations/{violationId}**
위반 단건 상세 조회

#### 3.3.4 Billing & Settlement

**GET /api/v1/billings/settlements**
정산 현황 조회

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| month | string | ✓ | YYYY-MM |
| concessionaireId | string | - | 콘세셔네어 ID |

```json
응답 예시:
{
  "success": true,
  "data": {
    "month": "2026-03",
    "concessionaireId": "TOC-001",
    "grossRevenue": 1250000.00,
    "jvcFee": 62500.00,
    "netPayable": 1187500.00,
    "currency": "MYR",
    "status": "FINALIZED",
    "settledAt": "2026-04-05T00:00:00+08:00"
  }
}
```

**GET /api/v1/billings/daily-summary**
일별 수납 요약

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| date | string | ✓ | YYYY-MM-DD |
| concessionaireId | string | - | 콘세셔네어 ID |

#### 3.3.5 Equipment

**GET /api/v1/equipments**
장비 목록 조회 (플라자별)

**GET /api/v1/equipments/{equipmentId}/status**
장비 상태 단건 조회

```json
응답 예시:
{
  "success": true,
  "data": {
    "equipmentId": "EQ-PLUS001-L03-RFID",
    "plazaId": "PLUS-001",
    "laneId": "LANE-03",
    "equipmentType": "RFID_READER",
    "status": "OPERATIONAL",
    "lastHeartbeatAt": "2026-04-02T08:59:45+08:00",
    "uptimePercent": 99.97
  }
}
```

#### 3.3.6 Reports

**GET /api/v1/reports/daily**
일별 운영 보고서

| 파라미터 | 타입 | 필수 | 설명 |
|----------|------|------|------|
| date | string | ✓ | YYYY-MM-DD |
| concessionaireId | string | - | 콘세셔네어 ID |
| format | string | - | json (기본), csv |

**GET /api/v1/reports/monthly**
월별 운영 보고서

---

## 4. BOS MCP Server 명세 (Paperclip Agent용)

### 4.1 개요

BOS MCP Server는 [Model Context Protocol](https://spec.modelcontextprotocol.io)을 기반으로 구현된 내부 전용 AI Agent 인터페이스다. Paperclip 29개 Agent가 BOS 데이터를 조회하고 운영 작업을 수행할 때 사용한다.

```
목적:    Paperclip Agent의 BOS 데이터 접근 인터페이스
대상:    JVC 내부 AI Agent 전용 (외부 노출 불가)
Transport: SSE (Server-Sent Events, HTTP/2)
보안:    mTLS + JVC 내부망 (VPC Private Subnet)
SLA:     < 5초 응답
구현:    api-service (Spring Boot MCP SDK)
```

### 4.2 Transport: SSE

```
Server URL: https://mcp.bos.jvc.internal/mcp
Protocol:   MCP over SSE
TLS:        mTLS (클라이언트 인증서 필수)

연결 흐름:
  1. Agent → SSE 연결 수립 (GET /mcp/sse)
  2. Server → capabilities 전송
  3. Agent → Tool 호출 (POST /mcp/messages)
  4. Server → 결과 반환 (SSE event)
  5. 연결 유지 (Heartbeat 30초)
```

### 4.3 15개 MCP Tool 상세

---

#### Tool 1: get_transaction

```json
{
  "name": "get_transaction",
  "description": "특정 트랜잭션 ID로 거래 상세 정보를 조회합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "transaction_id": {
        "type": "string",
        "description": "트랜잭션 ID (예: TXN-2026-001234)"
      }
    },
    "required": ["transaction_id"]
  }
}
```

**출력 예시:**
```json
{
  "transactionId": "TXN-2026-001234",
  "vehiclePlate": "WXY1234A",
  "channel": "A",
  "amount": 2.50,
  "status": "SUCCESS",
  "processedAt": "2026-04-02T08:30:00+08:00",
  "plazaId": "PLUS-001",
  "laneId": "LANE-03"
}
```

---

#### Tool 2: search_transactions

```json
{
  "name": "search_transactions",
  "description": "다양한 필터 조건으로 트랜잭션 목록을 검색합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "date_range": {
        "type": "object",
        "properties": {
          "start": { "type": "string", "format": "date" },
          "end": { "type": "string", "format": "date" }
        },
        "required": ["start", "end"]
      },
      "concessionaire_id": { "type": "string" },
      "vehicle_id": { "type": "string" },
      "vehicle_plate": { "type": "string" },
      "status": {
        "type": "string",
        "enum": ["SUCCESS", "FAILED", "PENDING", "REVIEWED"]
      },
      "channel": { "type": "string", "enum": ["A", "B"] },
      "limit": { "type": "integer", "default": 50, "maximum": 500 }
    },
    "required": ["date_range"]
  }
}
```

---

#### Tool 3: get_account

```json
{
  "name": "get_account",
  "description": "계정 ID로 계정 상세 정보를 조회합니다. 잔액, 차량 목록, 최근 거래 포함.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "account_id": { "type": "string", "description": "계정 ID (예: ACC-001234)" }
    },
    "required": ["account_id"]
  }
}
```

---

#### Tool 4: search_accounts

```json
{
  "name": "search_accounts",
  "description": "이름, 차량 번호판, 계정 유형으로 계정을 검색합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "name": { "type": "string", "description": "계정주 이름 (부분 일치)" },
      "vehicle_plate": { "type": "string", "description": "차량 번호판" },
      "account_type": {
        "type": "string",
        "enum": ["INDIVIDUAL", "CORPORATE", "FLEET", "GOVERNMENT"]
      },
      "status": { "type": "string", "enum": ["ACTIVE", "SUSPENDED", "CLOSED"] },
      "limit": { "type": "integer", "default": 20, "maximum": 100 }
    }
  }
}
```

---

#### Tool 5: get_violation_history

```json
{
  "name": "get_violation_history",
  "description": "특정 차량의 위반 이력을 조회합니다. Tier 1~4 미납 이력 포함.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "vehicle_id": { "type": "string" },
      "vehicle_plate": { "type": "string" },
      "date_range": {
        "type": "object",
        "properties": {
          "start": { "type": "string", "format": "date" },
          "end": { "type": "string", "format": "date" }
        }
      },
      "include_resolved": { "type": "boolean", "default": false }
    }
  }
}
```

---

#### Tool 6: get_equipment_status

```json
{
  "name": "get_equipment_status",
  "description": "플라자 또는 레인의 장비 상태를 조회합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "plaza_id": { "type": "string", "description": "플라자 ID" },
      "lane_id": { "type": "string", "description": "레인 ID (선택)" },
      "equipment_type": {
        "type": "string",
        "enum": ["RFID_READER", "ANPR_CAMERA", "BARRIER", "DISPLAY", "ALL"],
        "default": "ALL"
      }
    },
    "required": ["plaza_id"]
  }
}
```

---

#### Tool 7: get_lane_status

```json
{
  "name": "get_lane_status",
  "description": "플라자 전체 레인의 운영 현황을 조회합니다. 실시간 처리량 포함.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "plaza_id": { "type": "string", "description": "플라자 ID" }
    },
    "required": ["plaza_id"]
  }
}
```

**출력 예시:**
```json
{
  "plazaId": "PLUS-001",
  "totalLanes": 12,
  "operationalLanes": 11,
  "lanes": [
    {
      "laneId": "LANE-01",
      "status": "OPERATIONAL",
      "type": "SLFF",
      "tpsLast5min": 42.3
    }
  ],
  "alertCount": 1
}
```

---

#### Tool 8: get_kpi_summary

```json
{
  "name": "get_kpi_summary",
  "description": "콘세셔네어별 또는 전체 KPI 요약을 조회합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "concessionaire_id": { "type": "string", "description": "생략 시 전체" },
      "period": {
        "type": "string",
        "enum": ["TODAY", "WEEK", "MONTH", "QUARTER"],
        "default": "TODAY"
      }
    }
  }
}
```

---

#### Tool 9: get_unpaid_summary

```json
{
  "name": "get_unpaid_summary",
  "description": "미납 현황 요약. Tier별 건수와 금액 포함.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "concessionaire_id": { "type": "string" },
      "tier": {
        "type": "string",
        "enum": ["TIER1", "TIER2", "TIER3", "TIER4", "ALL"],
        "default": "ALL"
      },
      "as_of_date": { "type": "string", "format": "date" }
    }
  }
}
```

---

#### Tool 10: get_billing_status

```json
{
  "name": "get_billing_status",
  "description": "특정 월의 정산 상태를 조회합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "concessionaire_id": { "type": "string" },
      "month": { "type": "string", "description": "YYYY-MM 형식" }
    },
    "required": ["month"]
  }
}
```

---

#### Tool 11: get_exemption_list

```json
{
  "name": "get_exemption_list",
  "description": "면제 승인된 차량 또는 계정 목록을 조회합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "concessionaire_id": { "type": "string" },
      "exemption_type": {
        "type": "string",
        "enum": ["GOVERNMENT", "DISABLED", "EMERGENCY", "PROMO", "ALL"],
        "default": "ALL"
      },
      "date_range": {
        "type": "object",
        "properties": {
          "start": { "type": "string", "format": "date" },
          "end": { "type": "string", "format": "date" }
        }
      }
    }
  }
}
```

---

#### Tool 12: trigger_review

```json
{
  "name": "trigger_review",
  "description": "트랜잭션을 수동 심사 큐에 등록합니다. Human-in-the-loop 처리.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "transaction_id": { "type": "string" },
      "reason": {
        "type": "string",
        "enum": [
          "ANPR_LOW_CONFIDENCE",
          "MLFF_MATCH_FAILED",
          "AMOUNT_DISPUTE",
          "VEHICLE_MISMATCH",
          "MANUAL_REQUEST"
        ]
      },
      "notes": { "type": "string", "description": "추가 메모 (선택)" },
      "priority": {
        "type": "string",
        "enum": ["LOW", "NORMAL", "HIGH", "URGENT"],
        "default": "NORMAL"
      }
    },
    "required": ["transaction_id", "reason"]
  }
}
```

---

#### Tool 13: get_daily_report

```json
{
  "name": "get_daily_report",
  "description": "특정 날짜의 일별 운영 보고서를 조회합니다.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "concessionaire_id": { "type": "string" },
      "date": { "type": "string", "format": "date" }
    },
    "required": ["date"]
  }
}
```

---

#### Tool 14: get_monthly_report

```json
{
  "name": "get_monthly_report",
  "description": "월별 종합 운영 보고서를 조회합니다. 정산·위반·장비 포함.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "concessionaire_id": { "type": "string" },
      "year_month": { "type": "string", "description": "YYYY-MM 형식" }
    },
    "required": ["year_month"]
  }
}
```

---

#### Tool 15: get_alert_list

```json
{
  "name": "get_alert_list",
  "description": "시스템 알림 목록을 조회합니다. 장비 장애, 임계값 초과 등 포함.",
  "inputSchema": {
    "type": "object",
    "properties": {
      "severity": {
        "type": "string",
        "enum": ["CRITICAL", "HIGH", "MEDIUM", "LOW", "ALL"],
        "default": "ALL"
      },
      "status": {
        "type": "string",
        "enum": ["OPEN", "ACKNOWLEDGED", "RESOLVED", "ALL"],
        "default": "OPEN"
      },
      "limit": { "type": "integer", "default": 50 }
    }
  }
}
```

---

### 4.4 MCP Resources (읽기 전용 정적 데이터)

MCP Resources는 자주 참조되는 마스터 데이터를 노출한다.

| Resource URI | 설명 | 업데이트 주기 |
|-------------|------|--------------|
| `bos://masters/plazas` | 전체 플라자 목록 | 일 1회 |
| `bos://masters/toll-classes` | 요금 클래스 정의 | 변경 시 |
| `bos://masters/concessionaires` | 콘세셔네어 목록 | 변경 시 |
| `bos://masters/exemption-types` | 면제 유형 코드 | 변경 시 |
| `bos://masters/violation-types` | 위반 유형 코드 | 변경 시 |

### 4.5 Paperclip Agent 사용 시나리오

#### 시나리오 1: 미납 현황 일일 점검 (CFO Agent)

```
1. get_unpaid_summary(tier="ALL", as_of_date="2026-04-02")
   → Tier별 미납 건수·금액 확인

2. search_transactions(
     date_range={start:"2026-04-02", end:"2026-04-02"},
     status="FAILED"
   )
   → 당일 실패 트랜잭션 확인

3. get_kpi_summary(period="TODAY")
   → 전체 KPI 현황 확인

4. → Heartbeat 보고서 자동 생성
```

#### 시나리오 2: 장비 장애 대응 (DevOps Agent)

```
1. get_alert_list(severity="CRITICAL", status="OPEN")
   → 장애 알림 목록 확인

2. get_lane_status(plaza_id="PLUS-001")
   → 플라자 전체 레인 현황

3. get_equipment_status(plaza_id="PLUS-001", lane_id="LANE-03")
   → 특정 레인 장비 상세

4. → 장애 리포트 생성 및 Field Technician Agent 위임
```

#### 시나리오 3: 이의신청 처리 (Compliance Agent)

```
1. get_transaction(transaction_id="TXN-2026-001234")
   → 트랜잭션 상세 확인

2. get_account(account_id="ACC-001234")
   → 계정 이력 확인

3. get_violation_history(vehicle_plate="WXY1234A")
   → 위반 이력 확인

4. trigger_review(
     transaction_id="TXN-2026-001234",
     reason="AMOUNT_DISPUTE",
     priority="HIGH"
   )
   → 수동 심사 큐 등록

5. → 이의신청 담당자 알림 발송
```

---

## 5. API 거버넌스

### 5.1 버전 Deprecation 정책

```
현재 지원 버전: v1
신규 버전 출시 시:
  1. v2 출시 → v1 Deprecated 공지 (API 응답 헤더 Deprecation 추가)
  2. 12개월 병행 운영 (v1 + v2 동시 지원)
  3. 12개월 후 v1 Sunset (503 응답)

Deprecation 헤더:
  Deprecation: true
  Sunset: Mon, 01 Apr 2028 00:00:00 GMT
  Link: <https://api.bos.jvc.my/api/v2>; rel="successor-version"
```

### 5.2 Breaking Change 기준

| 구분 | Breaking | Non-Breaking |
|------|----------|--------------|
| 필드 삭제 | ✓ Breaking | — |
| 필드 타입 변경 | ✓ Breaking | — |
| 필수 파라미터 추가 | ✓ Breaking | — |
| Enum 값 제거 | ✓ Breaking | — |
| 필드 추가 | — | Non-Breaking |
| 선택 파라미터 추가 | — | Non-Breaking |
| Enum 값 추가 | — | Non-Breaking |
| 성능 개선 | — | Non-Breaking |

### 5.3 API 변경 승인 프로세스

```
변경 요청 접수
    │
    ▼
API Architect 검토 (1일)
  - Breaking 여부 판단
  - 영향 범위 분석
    │
    ▼
Breaking Change?
  ├── Yes → CTO 승인 (1일)
  │         │
  │         ▼
  │       Board 통보 (BD-17 준수)
  │         │
  │         ▼
  │       v2 계획 수립
  │
  └── No → 즉시 반영 가능
           Changelog 업데이트
```

### 5.4 Changelog 관리

```
파일: docs/02_system/CHANGELOG_API.md (별도 관리)
형식:
  ## [v1.x.y] - YYYY-MM-DD
  ### Added
  - GET /api/v1/... 추가 (사유)
  ### Changed
  - ...
  ### Deprecated
  - ...
  ### Removed
  - ...
```

---

## 6. 성능 SLA 매트릭스

| 엔드포인트 그룹 | P50 | P95 | P99 | 비고 |
|----------------|-----|-----|-----|------|
| GET /transactions | 50ms | 120ms | 200ms | DB 인덱스 최적화 |
| GET /accounts/{id} | 30ms | 80ms | 150ms | Redis 캐시 |
| GET /violations | 60ms | 150ms | 200ms | 기간 최대 7일 |
| GET /billings/* | 80ms | 180ms | 200ms | 집계 쿼리 |
| GET /equipments/* | 20ms | 60ms | 100ms | Redis 캐시 |
| GET /reports/* | 500ms | 2s | 5s | 대용량 쿼리 |
| MCP Tools (단건) | 200ms | 1s | 5s | LLM 포함 아님 |
| MCP trigger_review | 500ms | 2s | 5s | DB Write 포함 |

---

## 7. 참조 문서

| 문서 | 내용 |
|------|------|
| [01_system_overview.md](./01_system_overview.md) | 시스템 아키텍처 개요 |
| [02_service_domains.md](./02_service_domains.md) | 10개 서비스 도메인 상세 |
| [05_external_integration.md](./05_external_integration.md) | 외부 API 연동 (JPJ/TnG/FPX) |
| [04_ai_features.md](./04_ai_features.md) | AI 기능 설계 (MCP 사용 시나리오) |
| [../03_data/03_rbac_design.md](../03_data/03_rbac_design.md) | RBAC 30개 역할 정의 |
| [../05_governance/01_decision_gates.md](../05_governance/01_decision_gates.md) | API 변경 승인 게이트 |
| [../04_dev/05_gsd_workflow.md](../04_dev/05_gsd_workflow.md) | GSD 워크플로우 (Agent 운영) |

---

*작성일: 2026-04*
*버전: v1.0*
*담당 Agent: API Architect (총괄), Backend Lead, Paperclip Architect*
