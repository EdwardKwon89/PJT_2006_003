---
name: ai-decision-policy
description: Human-in-the-loop thresholds, settlement auto-approve rules, dispute escalation, AI audit trail
use_when:
  - AI(Agent)가 자동으로 결정할 수 있는 범위를 정의해야 할 때
  - 정산 자동 승인 또는 이의신청 자동 기각 로직을 구현할 때
  - AI 의사결정 감사 추적(Audit Trail)이 필요할 때
  - AI 기능 설계 또는 리뷰 시
dont_use_when:
  - AI 이상 탐지 알고리즘이 필요할 때 (ai-fault-detection 사용)
  - Text-to-SQL 기능이 필요할 때 (text-to-sql-engine 사용)
---

# AI 의사결정 정책

## 1. 개요

BOS AI Agent는 **정해진 임계값 내에서만 자동 결정**을 실행하며, 임계값 초과 또는 불확실한 사례는 반드시 인간에게 에스컬레이션한다. 모든 AI 결정은 감사 추적(Audit Trail)에 기록된다.

---

## 2. 핵심 내용

### 2.1 자동 결정 vs 인간 검토 기준표

| 결정 유형 | 자동 결정 조건 | 인간 검토 조건 | Fallback |
|---------|------------|------------|---------|
| 정산 집계 승인 | 불일치 < RM 0.50 | 불일치 ≥ RM 0.50 | `billing-lead` 검토 |
| 이의신청 자동 기각 | 중복 기록 명확, 신뢰도 > 95% | 신뢰도 95% 미만 | `violation-lead` 심사 |
| JPJ 차단 실행 | Tier 3 도달 + 고객 통보 완료 확인 후 | 통보 기록 누락 시 | 수동 검토 후 실행 |
| Write-off 실행 | 불가 (항상 CFO 승인 필요) | 항상 | CFO + 감사팀 이중 승인 |
| ANPR 매칭 자동 승인 | 신뢰도 ≥ 0.95 | 0.80~0.95 | 0.80 미만: 수동 |
| TnG ACK 불일치 | 불일치 < RM 1.00 | 불일치 ≥ RM 1.00 | CFO 알림 |

### 2.2 자동 결정 코드 패턴

```python
class AiDecisionEngine:
    def approve_settlement(self, batch_id: str, bos_total: Decimal, partner_total: Decimal) -> Decision:
        diff = abs(bos_total - partner_total)

        if diff < Decimal("0.50"):
            # 자동 승인
            self._record_ai_decision(
                decision_type="SETTLEMENT_AUTO_APPROVE",
                resource_id=batch_id,
                confidence=1.0,
                rationale=f"Difference RM {diff} < threshold RM 0.50",
                approved_by="ai-billing-agent"
            )
            return Decision.AUTO_APPROVED

        else:
            # 인간 에스컬레이션
            self._escalate_to_human(
                resource_id=batch_id,
                reason=f"Difference RM {diff} >= threshold",
                assignee="billing-lead",
                sla_hours=4
            )
            return Decision.ESCALATED_TO_HUMAN

    def _record_ai_decision(self, **kwargs):
        # 감사 추적 필수 기록
        AiAuditLog.create(**kwargs, timestamp=datetime.utcnow())
```

### 2.3 이의신청 자동 기각 흐름

```
이의신청 접수
    │
    ▼
[증거 분석 — Claude Sonnet]
  입력: RFID 로그, ANPR 이미지, TnG 결제 기록
    │
    ├── 신뢰도 > 95% + 이중 기록 명확 → 자동 기각
    │       └── 고객 자동 이메일 발송 (14일 항소 안내)
    │
    └── 신뢰도 ≤ 95% → violation-lead 24시간 SLA 심사
```

### 2.4 AI 감사 추적 스키마

```sql
CREATE TABLE ai_audit_log (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    decision_type   VARCHAR(100) NOT NULL,  -- 'SETTLEMENT_AUTO_APPROVE', 'DISPUTE_AUTO_REJECT'
    resource_id     UUID NOT NULL,
    agent_id        VARCHAR(100) NOT NULL,  -- 어떤 AI Agent가 결정
    model_version   VARCHAR(50),            -- 'claude-sonnet-4-5-20261001'
    confidence      NUMERIC(5,4),           -- 0.0000 ~ 1.0000
    rationale       TEXT NOT NULL,
    input_snapshot  JSONB,                  -- 결정 당시 입력 데이터 스냅샷
    output          JSONB,                  -- 결정 결과
    human_override  BOOLEAN DEFAULT FALSE,  -- 인간이 AI 결정을 뒤집었는가
    override_reason TEXT,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
-- 보관: 7년 (금융 감사 요건)
-- 삭제 불가 (append-only table)
```

### 2.5 인간 에스컬레이션 SLA

| 결정 유형 | SLA | 알림 채널 | 에스컬레이션 대상 |
|---------|-----|---------|-------------|
| 정산 불일치 | 4시간 | Slack + Email | `billing-lead` |
| 이의신청 심사 | 24시간 | Task Queue + Email | `violation-lead` |
| JPJ 차단 검토 | 48시간 | Slack + Jira | `compliance-officer` |
| Write-off 승인 | 5영업일 | Email + DocuSign | CFO + 감사팀 |

---

## 3. 주의사항 & 함정

- **임계값은 코드가 아닌 설정 테이블에 관리**: DB `ai_decision_thresholds` 테이블에서 조회. 하드코딩 금지
- **AI 결정 번복 추적**: 인간이 AI 결정을 뒤집을 경우 `human_override=TRUE` + `override_reason` 필수 기록
- **자동 차단 실행 전 통보 완료 확인**: JPJ 차단은 자동 실행이지만 고객 통보 기록 누락 시 즉시 중단

---

## 4. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| AI 이상 탐지 | [`../ai-fault-detection/SKILL.md`](../ai-fault-detection/SKILL.md) |
| AI 기능 설계 | [`../../docs/02_system/04_ai_features.md`](../../docs/02_system/04_ai_features.md) |
| Phase 9 AI 통합 | [`../../docs/06_phases/09_phase09_ai.md`](../../docs/06_phases/09_phase09_ai.md) |
