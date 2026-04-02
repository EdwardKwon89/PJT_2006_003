---
name: agent-workflow-patterns
description: Multi-agent orchestration, async task delegation, baton-passing between Claude agents
use_when:
  - 여러 Claude Agent 간 협업 워크플로우를 설계할 때
  - 비동기 태스크 위임 패턴이 필요할 때
  - Agent 간 바통 패싱(Baton-Passing) 흐름을 구현할 때
  - 새 Agent Task를 설계하거나 기존 패턴을 참조할 때
dont_use_when:
  - 단일 Agent 결정 정책이 필요할 때 (ai-decision-policy 사용)
  - AI 이상 탐지 알고리즘이 필요할 때 (ai-fault-detection 사용)
---

# Agent 워크플로우 패턴

## 1. 개요

BOS는 **8개 전문 Agent**가 협업하는 Multi-Agent 아키텍처를 사용한다. 각 Agent는 전문 도메인(정산, 위반, 모니터링 등)에 집중하며, 바통 패싱(Baton-Passing) 방식으로 복잡한 업무를 분산 처리한다.

---

## 2. 핵심 내용

### 2.1 8개 Agent 역할 정의

| Agent ID | 역할 | 주요 MCP Tool | 자동 결정 권한 |
|---------|------|------------|------------|
| `txn-agent` | 트랜잭션 수신·검증 | `bos_query_transaction` | ANPR 매칭 자동 승인 (신뢰도 ≥ 0.95) |
| `billing-agent` | 정산 집계·검증 | `bos_query_settlement` | 불일치 < RM 0.50 자동 승인 |
| `violation-agent` | 미납·위반 탐지 | `bos_query_violation` | Tier 1~2 알림 자동 발송 |
| `dispute-agent` | 이의신청 처리 | `bos_update_dispute` | 신뢰도 > 95% 자동 기각 |
| `account-agent` | 차량·계정 관리 | `bos_get_vehicle_info` | JPJ 조회 (RM 0.10 과금) |
| `monitoring-agent` | 시스템 헬스 모니터링 | `bos_get_equipment_status` | Auto-healing 3단계 |
| `analytics-agent` | KPI·리포트 생성 | `bos_run_text_to_sql` | Text-to-SQL 실행 |
| `compliance-agent` | 컴플라이언스 감사 | `bos_get_audit_log` | 없음 (조회만) |

### 2.2 바통 패싱 (Baton-Passing) 패턴

```
[Orchestrator Agent]
        │
        ├─── 정산 집계 태스크 ──→ [billing-agent]
        │                              │ 완료 후 결과 반환
        │
        ├─── 미납 탐지 태스크 ──→ [violation-agent]
        │                              │
        │                    불일치 감지 시
        │                              │
        │                    ──→ [dispute-agent] (바통 패스)
        │
        └─── 리포트 생성 ────→ [analytics-agent]
```

### 2.3 비동기 태스크 위임 구현

```python
import asyncio

class BillingAgent:
    async def run_daily_settlement(self, business_date: str):
        # 1. 집계 태스크 실행
        aggregation_result = await self.aggregate_transactions(business_date)

        # 2. 불일치 감지 시 dispute-agent에 바통 패스
        if aggregation_result.has_discrepancy:
            await self.delegate_to(
                target_agent="dispute-agent",
                task={
                    "type": "SETTLEMENT_DISCREPANCY",
                    "data": aggregation_result.discrepancy,
                    "priority": "HIGH",
                    "deadline": datetime.utcnow() + timedelta(hours=4)
                }
            )

        # 3. 정산 완료 후 analytics-agent에 리포트 생성 위임
        await self.delegate_to(
            target_agent="analytics-agent",
            task={
                "type": "GENERATE_DAILY_REPORT",
                "data": {"business_date": business_date},
                "priority": "NORMAL"
            }
        )
```

### 2.4 Agent 간 메시지 스키마 (표준화)

```json
// Agent 간 태스크 메시지 (Kafka topic: agent.tasks)
{
  "task_id": "uuid",
  "from_agent": "billing-agent",
  "to_agent": "dispute-agent",
  "task_type": "SETTLEMENT_DISCREPANCY",
  "priority": "HIGH",       // HIGH / NORMAL / LOW
  "deadline": "ISO 8601",
  "payload": {
    // 태스크별 데이터
  },
  "context": {
    "initiated_by": "billing-agent",
    "root_task_id": "uuid",    // 원점 태스크 추추적
    "parent_task_id": "uuid"
  },
  "created_at": "ISO 8601"
}
```

### 2.5 Agent 상태 모니터링

```yaml
# agent-health Prometheus 메트릭
agent_task_queue_depth{agent="billing-agent"}: 0
agent_task_processing_rate{agent="violation-agent"}: 45.2  # tasks/min
agent_task_error_rate{agent="dispute-agent"}: 0.002
agent_decision_auto_rate{agent="txn-agent"}: 0.98  # 98% 자동 처리율
```

---

## 3. 예시 시나리오

**시나리오: TnG ACK 불일치 → 다중 Agent 협업**
1. `billing-agent`: TnG ACK 검증 시 RM 150 불일치 감지
2. `billing-agent` → `dispute-agent` 바통 패스 (4시간 SLA)
3. `dispute-agent`: 불일치 원인 분석 (Claude Sonnet 활용)
4. `dispute-agent`: 원인 = TnG 배치 중복 청구 확인 → 증거 수집
5. `compliance-agent`: 감사 로그 기록
6. 인간 에스컬레이션: `billing-lead` Slack 알림 + 수정 작업 지시

---

## 4. 주의사항 & 함정

- **데드락 방지**: Agent A → B → A 순환 참조 금지. Orchestrator가 최상위 조율자 역할
- **태스크 중복 실행 방지**: `task_id` 기반 Idempotency 키 필수. Kafka 컨슈머 중복 처리 가능성 있음
- **Agent 간 데이터 전달 크기 제한**: Kafka 메시지 최대 1MB. 대용량 데이터는 S3에 저장 후 경로만 전달

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| AI 의사결정 정책 | [`../ai-decision-policy/SKILL.md`](../ai-decision-policy/SKILL.md) |
| Phase 9 AI 통합 | [`../../docs/06_phases/09_phase09_ai.md`](../../docs/06_phases/09_phase09_ai.md) |
| Agent 명세 | [`../../docs/04_dev/02_agent_design.md`](../../docs/04_dev/02_agent_design.md) |
