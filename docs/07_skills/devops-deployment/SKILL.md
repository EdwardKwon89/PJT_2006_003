---
name: devops-deployment
description: Blue-green deployment on EKS, ArgoCD GitOps, zero-downtime Flyway DB migration patterns
use_when:
  - Kubernetes EKS 배포 전략이 필요할 때
  - ArgoCD GitOps 배포 파이프라인을 설정할 때
  - Flyway 마이그레이션 무중단 적용 방법이 필요할 때
  - Phase 3 인프라 또는 Phase 12 핸드오버 준비 시
dont_use_when:
  - 인시던트 대응이 필요할 때 (incident-runbook 사용)
  - 모니터링 대시보드 설정이 필요할 때 (Phase 7 참조)
---

# DevOps & 배포 전략

## 1. 개요

BOS는 **Blue-Green 배포**, **ArgoCD GitOps**, **Flyway 무중단 DB 마이그레이션**으로 프로덕션 무중단 배포를 보장한다. 평균 배포 시간: 12분.

---

## 2. 핵심 내용

### 2.1 Blue-Green 배포 구조 (EKS)

```
                    [Route53 / Istio]
                          │
              ┌───────────┴────────────┐
     (Active 100%)                (Inactive 0%)
   [Blue: txn-service v1.2]   [Green: txn-service v1.3]
         │ EKS Pods                   │ EKS Pods
         ▼                            ▼
   [RDS Read/Write]            [RDS Read/Write]
         ▼
    [배포 완료 후]
Green → Active (100%), Blue → Standby → 24시간 후 제거
```

### 2.2 배포 파이프라인 (ArgoCD GitOps)

```yaml
# ArgoCD Application 정의
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: bos-txn-service
  namespace: argocd
spec:
  project: bos-prod
  source:
    repoURL: https://github.com/JVC/bos-infra
    targetRevision: main
    path: k8s/txn-service
  destination:
    server: https://eks.bos.jvc.my
    namespace: bos-prod
  syncPolicy:
    automated:
      prune: true       # 불필요한 리소스 자동 제거
      selfHeal: true    # 드리프트 자동 복구
    syncOptions:
      - CreateNamespace=true
```

### 2.3 무중단 DB 마이그레이션 (Flyway)

**3단계 안전 롤아웃 패턴**:
```sql
-- 단계 1: 새 컬럼 추가 (nullable, 기본값 있음)
-- V20260403_001__add_dispute_type.sql
ALTER TABLE unpaid_cases
ADD COLUMN dispute_type VARCHAR(50) DEFAULT 'STANDARD';

-- → 배포 후 7일 관찰
-- → 문제 없으면 단계 2 진행

-- 단계 2: 애플리케이션 코드에서 새 컬럼 쓰기 시작

-- 단계 3: NOT NULL 제약 추가 (데이터 채워진 후)
-- V20260410_001__constraint_dispute_type.sql
ALTER TABLE unpaid_cases
ALTER COLUMN dispute_type SET NOT NULL;
```

### 2.4 배포 롤백 절차

```bash
# 자동 롤백 조건: 배포 후 5분 내 에러율 > 5%

# 수동 롤백 (ArgoCD)
argocd app rollback bos-txn-service --revision {이전_빌드_번호}

# 즉시 롤백 (kubectl)
kubectl rollout undo deployment/txn-service -n bos-prod

# DB 마이그레이션 롤백 (사전 준비된 경우)
flyway -url=$DB_URL -user=$DB_USER undo
```

### 2.5 배포 SLA

| 단계 | 아키텍처 | 소요 시간 |
|------|---------|---------|
| 코드 빌드 + 테스트 | CI (GitHub Actions) | 8분 |
| Docker 이미지 빌드 | CI | 3분 |
| ArgoCD Sync | CD | 2분 |
| Green 환경 Health Check | Kubernetes | 3분 |
| 트래픽 전환 (Istio) | Immediate | < 30초 |
| **총 배포 시간** | | **~12분** |

---

## 3. 주의사항 & 함정

- **롤백 후 DB 마이그레이션**: 애플리케이션 롤백 후 DB 마이그레이션은 별도 판단 필요 (데이터 손실 위험)
- **Blue 환경 즉시 제거 금지**: 24시간 대기 후 제거 (프로덕션 이슈 발생 시 빠른 복구용)
- **Flyway `repair` 명령 주의**: 체크섬 불일치 시만 사용. 일반 상황에서 사용 금지

---

## 4. 관련 Skills & 참조 문서

| 참조 | 경로 |
|------|------|
| 인시던트 런북 | [`../incident-runbook/SKILL.md`](../incident-runbook/SKILL.md) |
| Phase 3 인프라 구축 | [`../../docs/06_phases/03_phase03_infra.md`](../../docs/06_phases/03_phase03_infra.md) |
| Phase 12 핸드오버 | [`../../docs/06_phases/12_phase12_handover.md`](../../docs/06_phases/12_phase12_handover.md) |
