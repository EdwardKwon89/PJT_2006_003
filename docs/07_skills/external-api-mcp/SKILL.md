---
name: external-api-mcp
description: External REST API design for TOC partners, MCP 15-tool usage patterns for Claude agents
use_when:
  - TOC(Toll Operator Certificate) 외부 API 설계 또는 구현 시
  - MCP Tool 활용 패턴을 참조해야 할 때
  - OpenAPI 3.0 스펙을 작성할 때
  - Phase 11 컴플라이언스 & 외부 API 공개 개발 시
dont_use_when:
  - 내부 마이크로서비스 간 통신이 필요할 때 (gRPC 또는 Kafka 패턴 사용)
  - JPJ/TnG 특정 API가 필요할 때 (각 전용 Skill 사용)
---

# 외부 API & MCP 설계

## 1. 개요

BOS는 두 가지 유형의 외부 인터페이스를 제공한다:
1. **REST API**: TOC 파트너사가 BOS 데이터를 PUSH/PULL 방식으로 접근하는 외부 API
2. **MCP (Model Context Protocol)**: Claude Agent가 BOS 도구를 직접 호출하는 AI 네이티브 인터페이스

---

## 2. 핵심 내용

### 2.1 외부 REST API 구조

| API 유형 | 대상 사용자 | 인증 | 설명 |
|---------|-----------|------|------|
| PUSH API | TOC 파트너 수신 서버 | Webhook + Signature | BOS→외부 데이터 실시간 전송 |
| PULL API | TOC 파트너 앱 | OAuth 2.0 Client Credentials | 외부→BOS 데이터 조회 |
| Admin API | JVC 내부 시스템 | mTLS + API Key | 관리 기능 (콘세셔네어 관리 등) |

### 2.2 주요 PULL API 엔드포인트

```yaml
# 콘세셔네어용 PULL API
GET /external/v1/settlements/daily?date={YYYY-MM-DD}&concessionaire_id={id}
GET /external/v1/violations/active?concessionaire_id={id}
GET /external/v1/transactions?from={datetime}&to={datetime}&lane_id={id}

# TOC 전용 API
GET /external/v1/toc/traffic-flow?plaza_id={id}&period=hourly
POST /external/v1/toc/incident-report
```

### 2.3 인증 구현 (OAuth 2.0)

```python
# 토큰 발급
POST /oauth/token
Content-Type: application/x-www-form-urlencoded
grant_type=client_credentials
&client_id={client_id}
&client_secret={client_secret}
&scope=settlements:read violations:read transactions:read

# 응답
{
  "access_token": "eyJ...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "settlements:read violations:read"
}
```

### 2.4 Rate Limiting 정책

| 사용자 유형 | 기본 한도 | 버스트 허용 |
|-----------|---------|----------|
| 콘세셔네어 | 1,000 req/min | 2,000 req/min (5분 이내) |
| TOC 파트너 | 500 req/min | 1,000 req/min |
| JVC 내부 | 무제한 | — |

### 2.5 MCP 15개 Tool 목록

BOS Agent가 사용하는 MCP Tool:

| # | Tool 이름 | 설명 |
|---|-----------|------|
| 1 | `bos_query_transaction` | 트랜잭션 조회 (날짜/차선/태그) |
| 2 | `bos_query_settlement` | 정산 집계 조회 |
| 3 | `bos_query_violation` | 미납/위반 케이스 조회 |
| 4 | `bos_update_dispute` | 이의신청 상태 업데이트 |
| 5 | `bos_get_vehicle_info` | 차량 정보 조회 (JPJ 연동) |
| 6 | `bos_block_vehicle` | JPJ 차단 요청 |
| 7 | `bos_unblock_vehicle` | JPJ 해제 요청 |
| 8 | `bos_run_text_to_sql` | 자연어 SQL 쿼리 실행 |
| 9 | `bos_get_dashboard_kpi` | 대시보드 KPI 조회 |
| 10 | `bos_send_notification` | 고객 알림 발송 |
| 11 | `bos_create_writeoff` | Write-off 요청 생성 |
| 12 | `bos_get_audit_log` | 감사 로그 조회 |
| 13 | `bos_get_equipment_status` | 현장 장비 상태 조회 |
| 14 | `bos_run_simulation` | 요금 수익 시뮬레이션 실행 |
| 15 | `bos_generate_report` | 정산 리포트 즉시 생성 |

---

## 3. 예시 시나리오

**시나리오: TOC 파트너가 PULL API로 어제 일별 정산 데이터 조회**
```bash
curl -H "Authorization: Bearer {token}" \
  "https://api.bos.jvc.my/external/v1/settlements/daily?date=2026-04-02&concessionaire_id=PLUS-001"

# 응답
{
  "date": "2026-04-02",
  "concessionnaire_id": "PLUS-001",
  "total_gross_amount": 2854000.50,
  "jvc_fee_amount": 142700.03,
  "net_amount": 2711300.47,
  "channel_a_amount": 1980000.00,
  "channel_b_amount": 874000.50
}
```

---

## 4. 주의사항 & 함정

- **콘세셔네어 격리**: PULL API에서 `concessionaire_id`는 토큰 scope에 바인딩 → 타사 ID로 조회 시 403
- **PUSH Webhook 서명 검증**: `X-BOS-Signature: sha256={hmac}` 헤더 필수 (수신 측 검증 의무)
- **OpenAPI 스펙 자동 생성**: Spring Boot `springdoc-openapi` 사용 → `/docs` 경로 자동 배포

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| API MCP 명세 | [`../../docs/02_system/06_api_mcp_spec.md`](../../docs/02_system/06_api_mcp_spec.md) |
| Phase 11 컴플라이언스 | [`../../docs/06_phases/11_phase11_compliance.md`](../../docs/06_phases/11_phase11_compliance.md) |
| RBAC & 접근 제어 | [`../rbac-data-boundary/SKILL.md`](../rbac-data-boundary/SKILL.md) |
