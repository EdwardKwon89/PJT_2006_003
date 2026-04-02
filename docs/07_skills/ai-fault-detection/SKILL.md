---
name: ai-fault-detection
description: Prometheus metrics anomaly detection, 3-stage auto-recovery, Claude-assisted incident analysis
use_when:
  - AI 기반 이상 탐지 로직을 설계하거나 구현할 때
  - 자동 복구 3단계 워크플로우를 구성할 때
  - Prometheus 메트릭 기반 알림 임계값 설정 시
  - Phase 7 모니터링 또는 Phase 9 AI 기능 개발 시
dont_use_when:
  - Grafana 대시보드 UI 구성이 필요할 때 (monitoring Phase 7 참조)
  - Text-to-SQL 기능이 필요할 때 (text-to-sql-engine 사용)
---

# AI 장애 탐지

## 1. 개요

BOS는 통계 기반 이상 탐지와 **Claude Sonnet 기반 AI 분석**을 결합하여 장애를 조기 탐지하고, 3단계 자동 복구를 실행한다. 인간 개입 없이 해결 가능한 장애는 자동으로 처리된다.

---

## 2. 핵심 내용

### 2.1 이상 탐지 아키텍처

```
[Prometheus 메트릭] ← 모든 서비스
        │ (15초 scrape 간격)
        ▼
[통계 기반 탐지 (단기)]
  - 롤링 5분 평균 ± 3σ 이탈 탐지
  - Error Rate > 5% (2분 지속)
  - P99 Latency > SLO × 2배
        │ 이상 감지
        ▼
[Claude Sonnet 분석 (복잡한 이상)]
  - 입력: 최근 15분 메트릭 시계열 JSON
  - 출력: 이상 여부, 원인 추정, 권장 조치
        │
        ▼
[자동 복구 실행 (3단계)]
```

### 2.2 자동 복구 3단계

```
1단계: Pod 자동 재시작
   조건: 단일 Pod 에러율 > 10% (5분 지속)
   실행: kubectl rollout restart deployment/{service}
   평가: 5분 후 에러율 < 5%? → 해결 완료 / 아니면 2단계

2단계: Circuit Breaker Open (트래픽 전환)
   조건: 서비스 전체 에러율 > 20% (3분 지속)
   실행: Istio VirtualService weight 조정 (정상 인스턴스로 100% 전환)
   평가: 5분 후 정상화? → 해결 완료 / 아니면 3단계

3단계: 인간 개입 요청
   조건: 2단계 후 5분 경과, 미해결
   실행:
     - PagerDuty P1 알림 (담당 엔지니어)
     - Slack #bos-alerts @channel
     - Claude 포스트모템 초안 자동 생성 시작
```

### 2.3 Claude 기반 이상 분석 프롬프트

```python
def analyze_anomaly_with_claude(metrics_snapshot: dict) -> AnomalyAnalysis:
    prompt = f"""
You are a Site Reliability Engineer for Malaysia BOS tolling system.
Analyze the following 15-minute metrics snapshot and determine:
1. Is this an anomaly? (YES/NO with confidence 0-100%)
2. Most likely root cause (max 2 sentences)
3. Recommended action (specific kubectl/query commands if applicable)

Metrics snapshot:
{json.dumps(metrics_snapshot, indent=2)}

Output as JSON:
{{
  "is_anomaly": true/false,
  "confidence": 0-100,
  "root_cause": "...",
  "recommended_action": "...",
  "auto_recoverable": true/false
}}
"""
    response = claude_client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return AnomalyAnalysis.parse(response.content[0].text)
```

### 2.4 핵심 알림 임계값

| 메트릭 | 경고(P2) | 심각(P1) | 계산식 |
|-------|---------|---------|-------|
| 에러율 | > 2% | > 5% | `rate(http_requests_total{status=~"5.."}[5m]) / rate(http_requests_total[5m])` |
| P99 지연 | > SLO×1.5 | > SLO×3 | `histogram_quantile(0.99, rate(http_request_duration_seconds_bucket[5m]))` |
| Kafka Lag | > 5,000 | > 50,000 | `kafka_consumer_group_lag` |
| DB 연결 수 | > 80% | > 95% | `pg_stat_activity_count / pg_settings{name="max_connections"}` |

---

## 3. 예시 시나리오

**시나리오: txn-service 에러율 급증 (15% → 자동 Pod 재시작)**
1. Prometheus: `txn-service` 에러율 15% 감지 (5분 지속)
2. 1단계 자동 복구: `kubectl rollout restart deployment/txn-service`
3. 재시작 후 2분: 에러율 1.2% → 정상화
4. Slack 알림: "txn-service 자동 복구 완료 (에러율 15%→1.2%)"
5. 포스트모템 초안 자동 생성 (원인: OOM, 재발 방지: Heap 설정 증가)

---

## 4. 주의사항 & 함정

- **Claude 분석 비용**: 15분마다 API 호출 비용 발생. 이상 감지 시에만 호출 (통계 기반 사전 필터링 필수)
- **자동 재시작 루프 방지**: 동일 Pod가 10분 내 3회 이상 재시작 시 자동 복구 중단 → 수동 대응 전환
- **Circuit Breaker 해제**: Istio weight 조정은 자동 해제되지 않음 → 수동 확인 후 해제

---

## 5. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| AI 의사결정 정책 | [`../ai-decision-policy/SKILL.md`](../ai-decision-policy/SKILL.md) |
| Phase 7 모니터링 | [`../../docs/06_phases/07_phase07_monitoring.md`](../../docs/06_phases/07_phase07_monitoring.md) |
| AI 기능 설계 | [`../../docs/02_system/04_ai_features.md`](../../docs/02_system/04_ai_features.md) |
