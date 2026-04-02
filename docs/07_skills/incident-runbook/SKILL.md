---
name: incident-runbook
description: P1~P4 severity classification, 5-minute ownership checklist, post-mortem template with blameless culture
use_when:
  - 프로덕션 인시던트 발생 시 대응 절차가 필요할 때
  - PagerDuty 알림을 받고 대응 방법을 참조할 때
  - 포스트모템 문서를 작성해야 할 때
  - 새 팀원이 온콜을 배우는 경우
dont_use_when:
  - AI 자동 복구 로직 구현이 필요할 때 (ai-fault-detection 사용)
  - 일상적인 모니터링 설정이 필요할 때 (Phase 7 참조)
---

# 인시던트 런북

## 1. 개요

BOS 인시던트 대응 표준 절차. P1(최심각)부터 P4(정보성)까지 분류하고, 5분 내 소유권 확보를 목표로 한다. 모든 포스트모템은 **비난 없는 문화(Blameless Culture)**를 원칙으로 한다.

---

## 2. 핵심 내용

### 2.1 심각도 분류

| 심각도 | 정의 | 예시 | 대응 시간 | 알림 대상 |
|------|------|------|---------|---------|
| **P1** | 프로덕션 완전 중단 | 모든 거래 처리 불가, DB 다운 | 5분 내 | 온콜 + 팀장 + CTO |
| **P2** | 주요 기능 저하 | 정산 배치 실패, API 지연 > 2배 | 15분 내 | 온콜 팀장 |
| **P3** | 부분 기능 영향 | 특정 콘세셔네어 리포트 오류 | 4시간 내 | 해당 팀 |
| **P4** | 정보성 이슈 | 로그 경고 증가, 비핵심 서비스 지연 | 다음 영업일 | 담당자 |

### 2.2 P1 인시던트 5분 체크리스트

```markdown
## T+0: PagerDuty 알림 수신
- [ ] PagerDuty 알림 Acknowledge
- [ ] #bos-incidents Slack 채널 인시던트 스레드 시작:
      "P1 인시던트 발생: [증상 요약]. IC: [이름]. 상황 업데이트 이 스레드에 계속."

## T+1분: 초기 진단
- [ ] 영향 범위 확인: 어떤 서비스? 어떤 지역?
- [ ] Grafana 대시보드 스크린샷 캡처
- [ ] 최근 배포 또는 변경 사항 확인: `git log --oneline -20`

## T+2분: 에스컬레이션
- [ ] 팀장/CTO에게 SMS + Slack DM 전송
- [ ] 관련 팀(DB팀, 인프라팀) 호출 여부 판단

## T+5분: 복구 시작
- [ ] 롤백 가능한 경우: 즉시 이전 버전 배포
- [ ] 서비스 격리: 영향 서비스 트래픽 전환

## T+15분: 첫 번째 상태 업데이트
- [ ] 인시던트 스레드에 현황 공유 (영향 범위, 진행 상황, ETA)
```

### 2.3 자주 사용하는 진단 명령어

```bash
# 서비스 상태 확인
kubectl get pods -n bos-prod | grep -v Running
kubectl top pods -n bos-prod --sort-by=memory

# 최근 로그 (에러 필터)
kubectl logs -n bos-prod -l app=txn-service --tail=100 | grep -i error

# DB 연결 확인
psql $DB_URL -c "SELECT count(*), state FROM pg_stat_activity GROUP BY state;"

# Kafka 소비 지연 확인
kafka-consumer-groups.sh --bootstrap-server $KAFKA_BROKER \
  --group bos-consumers --describe | grep -v STABLE

# 최근 배포 확인
kubectl rollout history deployment/txn-service -n bos-prod
```

### 2.4 포스트모템 템플릿

```markdown
# 포스트모템: [인시던트 제목]

**날짜**: YYYY-MM-DD
**심각도**: P1/P2
**총 영향 시간**: X시간 Y분
**인시던트 코디네이터(IC)**: [이름]

## 타임라인

| 시각 (MYT) | 이벤트 |
|-----------|--------|
| HH:MM | 최초 알림 수신 |
| HH:MM | 원인 식별 |
| HH:MM | 복구 조치 시작 |
| HH:MM | 서비스 정상화 확인 |

## 근본 원인 (Root Cause)
[비난 없이 시스템·프로세스 문제에 집중]

## 영향 범위
- 영향 받은 트랜잭션: X건
- 영향 받은 금액: RM X
- 영향 받은 콘세셔네어: X곳

## 조치 사항 (Action Items)

| # | 내용 | 담당자 | 기한 |
|---|------|--------|------|
| 1 | 재발 방지 조치 | | |
| 2 | 모니터링 개선 | | |
| 3 | 런북 업데이트 | | |

## 잘 된 점 (What Went Well)
## 개선할 점 (What Can Be Improved)
```

---

## 3. 주의사항 & 함정

- **항상 5분 내 Acknowledge**: SLA 위반 방지. 이후 진단 시간이 충분하더라도 우선 수신 확인
- **포스트모템 48시간 내 초안 완성**: 기억이 생생할 때 작성. Claude AI가 초안 자동 생성 지원
- **비난 없는 문화 유지**: 포스트모템에 개인 이름 비난 금지. "엔지니어가 실수" → "시스템이 안전장치 없이 허용"

---

## 4. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| AI 장애 탐지 & 자동 복구 | [`../ai-fault-detection/SKILL.md`](../ai-fault-detection/SKILL.md) |
| Phase 7 모니터링 | [`../../docs/06_phases/07_phase07_monitoring.md`](../../docs/06_phases/07_phase07_monitoring.md) |
| 운영 거버넌스 | [`../../docs/05_governance/01_settlement_governance.md`](../../docs/05_governance/01_settlement_governance.md) |
