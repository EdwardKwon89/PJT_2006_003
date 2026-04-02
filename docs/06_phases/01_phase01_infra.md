# Phase 1: 공통 인프라 구축
## 06_phases/01_phase01_infra.md
## v1.0 | 2026-04 | 참조: 02_system/03_tech_stack.md, 04_dev/01_toolchain.md

---

> **Agent 사용 지침**
> DevOps Lead Agent가 인프라 구축 시 로드. 모든 후속 Phase의 기반.
> Terraform 코드 변경 전 `terraform plan` 결과를 반드시 CTO에게 공유.
> 비용 초과 위험이 있는 리소스 추가 시 CFO 사전 승인 필수.

---

## 1. Phase 개요

| 항목 | 내용 |
| ---- | ---- |
| **Phase 번호** | Phase 0 (06_phases/00_phase_overview.md의 순서 기준) |
| **Phase명** | 공통 인프라 구축 (Common Infrastructure Setup) |
| **목적** | 모든 후속 Phase (Phase 1~11)가 공통으로 사용하는 AWS 기반 클라우드 인프라를 Terraform IaC로 구성하고 검증 |
| **예상 기간** | 3주 (2026-04-22 ~ 2026-05-12) |
| **선행 Phase** | 없음 (독립 시작 가능) |
| **후행 Phase** | Phase 1~11 전부 (모든 Phase의 기반) |
| **G-HARD 진입 게이트** | Gate 1 통과 필수 (Technical Architecture Review) |
| **담당 Lead** | devops-lead Agent |
| **예상 Agent 호출** | 120~160회 |
| **예상 비용** | USD $48~64 |

### 1.1 Phase 목표

1. **IaC 완전 자동화**: 모든 리소스를 Terraform으로 선언, 수동 콘솔 조작 Zero
2. **고가용성 기반**: Multi-AZ 구성으로 단일 장애점(SPOF) 제거
3. **보안 우선**: VPC 격리, IAM 최소 권한, Vault 시크릿 관리 Day-0 적용
4. **관찰 가능성 확보**: Prometheus + Grafana + Jaeger를 인프라 레이어부터 적용
5. **DR 준비**: Primary(ap-southeast-1) + DR(ap-southeast-3) 이중화 기반 구성

### 1.2 인프라 아키텍처 개요

```
┌─────────────────────────── AWS ap-southeast-1 (Primary) ──────────────────────────┐
│                                                                                     │
│  ┌─── VPC 10.0.0.0/16 ──────────────────────────────────────────────────────────┐  │
│  │                                                                               │  │
│  │  Public Subnet (10.0.1.0/24, 10.0.2.0/24)                                   │  │
│  │  ├── ALB (Internet-facing)                                                   │  │
│  │  └── NAT Gateway × 2                                                         │  │
│  │                                                                               │  │
│  │  Private Subnet (10.0.10.0/24, 10.0.11.0/24)                                │  │
│  │  ├── EKS Node Group (t3.xlarge × 3 → auto-scale 최대 20)                    │  │
│  │  ├── RDS PostgreSQL 16 Multi-AZ (db.r6g.xlarge)                             │  │
│  │  ├── MSK Kafka 3.7 (3 Broker, kafka.m5.large)                               │  │
│  │  └── ElastiCache Redis 7 Cluster (cache.r6g.large × 3)                      │  │
│  │                                                                               │  │
│  │  Isolated Subnet (10.0.20.0/24)                                              │  │
│  │  └── HashiCorp Vault (vault.eks.internal)                                    │  │
│  │                                                                               │  │
│  └───────────────────────────────────────────────────────────────────────────── ┘  │
│                                                                                     │
│  S3 Buckets: terraform-state, delta-lake-raw, delta-lake-processed, anpr-images    │
│  CloudFront: BOS Admin SPA CDN (정적 자산)                                         │
│  Route 53: bos.internal.malaysia-tolling.com                                        │
│  API Gateway: api.malaysia-tolling.com                                              │
│  WAF: OWASP Core Rule Set + Malaysia IP Allowlist                                  │
│                                                                                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
           │ VPC Peering / AWS Global Accelerator
           ▼
┌─────────────── AWS ap-southeast-3 (DR Region) ──────────────────────────────────────┐
│  RDS Read Replica → Promote on failover                                             │
│  S3 Cross-Region Replication (delta-lake, anpr-images)                              │
│  EKS Standby Cluster (최소 구성, failover 시 스케일업)                              │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. 담당 Agent 구성

| Agent | 역할 | 책임 영역 |
| ----- | ---- | --------- |
| **devops-lead** | Phase 리드 | 전체 IaC 설계, CTO 보고, 완료 기준 검증 |
| **devops-dev-1** | 컴퓨팅 담당 | EKS 클러스터, Node Group, HPA, Namespace |
| **devops-dev-2** | 데이터 담당 | RDS, MSK, ElastiCache, S3, Delta Lake |
| **CTO** | 승인자 | 아키텍처 리뷰, Gate 1 사인오프 |

**에스컬레이션 경로:**
```
devops-dev-{1,2}  →  devops-lead  →  CTO  →  Steering Committee
```

**회의 주기:**
- 일일 스탠드업: 09:00 (15분, devops-lead 주재)
- 주간 기술 리뷰: 수요일 14:00 (CTO 참석)

---

## 3. 주요 태스크 체크리스트

모든 태스크는 `terraform apply` 또는 `kubectl apply` 후 검증 명령어로 완료를 확인한다.

### 3.1 AWS EKS 클러스터 구성 (Terraform IaC)

- [ ] Terraform 워킹 디렉토리 `infra/terraform/eks/` 초기화
- [ ] EKS 클러스터 `malaysia-bos-prod` 생성 (K8s 1.30)
- [ ] Managed Node Group `general` (t3.xlarge × 3, min 3, max 20)
- [ ] Managed Node Group `spot` (t3.large Spot, max 30, 비용 최적화)
- [ ] Cluster Autoscaler 배포 및 IAM 역할 연결 (IRSA)
- [ ] EKS Add-ons: CoreDNS, kube-proxy, vpc-cni, aws-ebs-csi-driver
- [ ] `kubeconfig` 생성 및 CI/CD 서비스 계정 연결

**검증:**
```bash
kubectl get nodes -o wide
# NAME                          STATUS   ROLES   AGE   VERSION
# ip-10-0-10-x.ec2.internal    Ready    <none>  1m    v1.30.x
# ip-10-0-11-x.ec2.internal    Ready    <none>  1m    v1.30.x
# ip-10-0-10-y.ec2.internal    Ready    <none>  1m    v1.30.x
```

### 3.2 RDS PostgreSQL 16 Multi-AZ 구성

- [ ] RDS 파라미터 그룹 생성 (`bos-pg16-params`: shared_preload_libraries = pg_stat_statements)
- [ ] RDS 서브넷 그룹 생성 (Private Subnet 2개 AZ)
- [ ] RDS 인스턴스 `bos-prod-db` 생성
  - Engine: PostgreSQL 16.2
  - Instance: db.r6g.xlarge (4 vCPU, 32 GB RAM)
  - Storage: gp3 500 GB, IOPS 6,000, 자동 증설 ON (최대 2 TB)
  - Multi-AZ: 활성화 (ap-southeast-1a, 1b)
  - 백업: 자동 7일 보존, 스냅샷 암호화 (KMS)
  - 유지보수 윈도우: 일요일 03:00 ~ 04:00 KST
- [ ] RDS Proxy 구성 (커넥션 풀링, IAM 인증)
- [ ] Failover 테스트: Primary 강제 재부팅 후 Replica 승격 확인

**검증:**
```bash
aws rds describe-db-instances \
  --db-instance-identifier bos-prod-db \
  --query 'DBInstances[0].{Status:DBInstanceStatus,MultiAZ:MultiAZ}'
# {
#   "Status": "available",
#   "MultiAZ": true
# }
```

### 3.3 MSK Kafka 3-Broker 구성

- [ ] MSK 서브넷 그룹 생성 (3 AZ, Private Subnet)
- [ ] MSK 클러스터 `bos-kafka` 생성
  - Kafka 버전: 3.7.x
  - Broker: kafka.m5.large × 3 (AZ당 1개)
  - 스토리지: 1 TB (gp3) per broker, 자동 증설 ON
  - 암호화: TLS + KMS at rest
  - 인증: SASL/SCRAM (Secret Manager 연동)
- [ ] Kafka 토픽 초기 생성:
  - `toll-event-raw` (partitions: 12, replication: 3, retention: 7d)
  - `toll-event-validated` (partitions: 12, replication: 3, retention: 30d)
  - `transaction-created` (partitions: 6, replication: 3, retention: 30d)
  - `settlement-batch` (partitions: 3, replication: 3, retention: 90d)
  - `violation-detected` (partitions: 6, replication: 3, retention: 90d)
  - `equipment-heartbeat` (partitions: 6, replication: 3, retention: 3d)
- [ ] Schema Registry (Confluent Schema Registry OSS) K8s 배포
- [ ] Kafka UI (Kowl) K8s 배포 (내부 접근 전용)

**검증:**
```bash
# MSK 상태 확인
aws kafka describe-cluster --cluster-arn $MSK_CLUSTER_ARN \
  --query 'ClusterInfo.State'
# "ACTIVE"

# 토픽 확인
kafka-topics.sh --bootstrap-server $MSK_BOOTSTRAP --list
```

### 3.4 ElastiCache Redis 7 Cluster 구성

- [ ] ElastiCache 서브넷 그룹 생성 (Private Subnet, 2 AZ)
- [ ] Redis 7 Cluster `bos-redis` 생성
  - Node Type: cache.r6g.large (2 vCPU, 13 GB)
  - Cluster Mode: ON (3 샤드 × 2 노드 = 6 노드)
  - 암호화: TLS + AUTH Token (Vault 관리)
  - 자동 장애 조치: 활성화
  - 백업: 일 1회 02:00, 보존 3일
- [ ] Redis 키 네임스페이스 정의:
  - `session:{userId}` — TTL 30분
  - `rate_limit:{ip}` — TTL 1분
  - `toll_fee_cache:{plazaId}:{vehicleClass}` — TTL 1시간
  - `user_balance:{userId}` — TTL 5분 (채널 A 잔액)

**검증:**
```bash
redis-cli -h $REDIS_ENDPOINT -a $AUTH_TOKEN \
  --tls PING
# PONG
redis-cli -h $REDIS_ENDPOINT -a $AUTH_TOKEN \
  --tls CLUSTER INFO | grep cluster_state
# cluster_state:ok
```

### 3.5 S3 버킷 + Delta Lake 초기화

- [ ] S3 버킷 생성 (모든 버킷: 버전 관리 ON, 공개 접근 차단)

  | 버킷명 | 목적 | 수명 주기 정책 |
  |--------|------|----------------|
  | `bos-terraform-state` | Terraform 상태 파일 | 보존 (삭제 없음) |
  | `bos-delta-lake-raw` | 원시 거래 데이터 (Bronze) | 90일 → Glacier |
  | `bos-delta-lake-processed` | 정제 데이터 (Silver·Gold) | 365일 → Glacier |
  | `bos-anpr-images` | ANPR 이미지 증거 | 30일 자동 삭제 (PDPA) |
  | `bos-backups` | DB·Config 백업 | 90일 → 삭제 |
  | `bos-admin-spa` | React Admin SPA 정적 파일 | 무기한 |
  | `bos-artifacts` | CI/CD 빌드 아티팩트 | 30일 → 삭제 |

- [ ] DynamoDB 테이블 `bos-terraform-locks` 생성 (Terraform State Lock)
- [ ] Delta Lake 폴더 구조 초기화:
  ```
  s3://bos-delta-lake-raw/
  ├── toll_events/year={YYYY}/month={MM}/day={DD}/
  ├── transactions/year={YYYY}/month={MM}/day={DD}/
  └── violations/year={YYYY}/month={MM}/day={DD}/

  s3://bos-delta-lake-processed/
  ├── silver/
  │   ├── toll_sessions/
  │   ├── account_balances/
  │   └── settlement_daily/
  └── gold/
      ├── revenue_by_plaza/
      ├── traffic_by_hour/
      └── violation_by_category/
  ```
- [ ] S3 Event Notification → MSK `toll-event-raw` 토픽 연결 (신규 파일 업로드 시)

### 3.6 VPC / 보안 그룹 / IAM 역할 설정

- [ ] VPC `bos-vpc` 생성 (CIDR: 10.0.0.0/16)
  - 퍼블릭 서브넷: 10.0.1.0/24 (AZ-a), 10.0.2.0/24 (AZ-b)
  - 프라이빗 서브넷: 10.0.10.0/24 (AZ-a), 10.0.11.0/24 (AZ-b)
  - 격리 서브넷: 10.0.20.0/24 (Vault, AZ-a 전용)
  - NAT Gateway: 퍼블릭 서브넷 각각 (고가용성)
  - VPC Flow Logs: CloudWatch Logs 그룹 `/aws/vpc/bos-flow-logs`

- [ ] 보안 그룹 생성:

  | 보안 그룹 | 인바운드 허용 | 아웃바운드 |
  |-----------|--------------|------------|
  | `sg-alb-public` | 0.0.0.0/0:443 | EKS Node:8080 |
  | `sg-eks-nodes` | ALB:8080, Vault:8200 | 0.0.0.0/0 |
  | `sg-rds` | EKS Node:5432 | 없음 |
  | `sg-msk` | EKS Node:9096 (SASL/TLS) | 없음 |
  | `sg-redis` | EKS Node:6379 | 없음 |
  | `sg-vault` | EKS Node:8200,8201 | 0.0.0.0/0 |

- [ ] IAM 역할 생성 (최소 권한 원칙):

  | 역할명 | 사용 주체 | 권한 범위 |
  |--------|-----------|-----------|
  | `bos-eks-cluster-role` | EKS Control Plane | AmazonEKSClusterPolicy |
  | `bos-eks-node-role` | EKS Node Group | EKS Worker + ECR Read |
  | `bos-rds-proxy-role` | RDS Proxy | SecretsManager Read |
  | `bos-msk-producer-role` | Kafka Producer (IRSA) | MSK DescribeCluster + Connect |
  | `bos-s3-delta-role` | Spark Jobs (IRSA) | S3:GetObject·PutObject on delta-lake/* |
  | `bos-vault-role` | Vault Server | KMS Decrypt, SecretsManager Read |
  | `bos-cicd-role` | GitHub Actions OIDC | ECR Push, EKS Deploy, S3 artifacts |

### 3.7 HashiCorp Vault 배포

- [ ] Vault Helm Chart 배포 (K8s `vault` Namespace)
  ```bash
  helm repo add hashicorp https://helm.releases.hashicorp.com
  helm install vault hashicorp/vault \
    --namespace vault \
    --values infra/helm/vault-values.yaml
  ```
- [ ] Vault 초기화 및 Unseal (5 key share, 3 threshold)
  - Unseal Key → AWS Secrets Manager 암호화 저장
  - Root Token → 1회 사용 후 폐기, Admin Token 재발급
- [ ] Vault Auto-unseal → AWS KMS 키 설정 (재시작 시 자동 해제)
- [ ] Vault Secrets Engine 활성화:
  - `database` 엔진: PostgreSQL 동적 시크릿 (90일 TTL)
  - `kv-v2` 엔진: 애플리케이션 설정값 저장 (`secret/bos/*`)
  - `pki` 엔진: 내부 TLS 인증서 발급
  - `aws` 엔진: AWS 임시 자격증명 발급
- [ ] Vault Policy 생성:
  - `bos-app-policy`: `secret/bos/*` read
  - `bos-db-policy`: `database/creds/bos-app` read
  - `bos-admin-policy`: 전체 경로 관리

**검증:**
```bash
kubectl exec -it vault-0 -n vault -- vault status
# Key             Value
# ---             -----
# Seal Type       awskms
# Initialized     true
# Sealed          false
# Total Shares    5
# Threshold       3
# Version         1.17.x
```

### 3.8 Prometheus + Grafana + Jaeger 모니터링 스택

- [ ] `monitoring` Namespace 생성
- [ ] Prometheus Operator (kube-prometheus-stack Helm) 배포
  ```bash
  helm install monitoring prometheus-community/kube-prometheus-stack \
    --namespace monitoring \
    --values infra/helm/monitoring-values.yaml
  ```
- [ ] Prometheus 설정:
  - 스크레이프 인터벌: 15초
  - 데이터 보존: 30일 (로컬), 90일 (S3 Thanos 연동)
  - AlertManager: Slack + PagerDuty 연동
- [ ] Grafana 대시보드 Import:
  - Kubernetes Cluster Overview (ID: 315)
  - Spring Boot 2.1+ Statistics (ID: 11378)
  - Kafka Lag Exporter (ID: 14012)
  - PostgreSQL Database (ID: 9628)
  - Redis Sentinel / Cluster (ID: 763)
  - BOS Custom Dashboard (infra/grafana/bos-overview.json)
- [ ] Jaeger Operator 배포 (`tracing` Namespace)
  - 스토리지: Elasticsearch (or OpenSearch) 백엔드
  - 샘플링률: 프로덕션 1%, 개발 100%
- [ ] AlertManager 알림 규칙 설정:
  - EKS Node CPU > 80% (5분 지속) → P2 경고
  - RDS 연결 수 > 80% → P2 경고
  - Kafka Consumer Lag > 10,000 → P1 경고
  - Vault Sealed → P0 긴급

**검증:**
```bash
# Grafana 접근 확인
kubectl port-forward svc/monitoring-grafana 3000:80 -n monitoring
curl -s http://localhost:3000/api/health | jq '.database'
# "ok"

# Jaeger 접근 확인
kubectl port-forward svc/jaeger-query 16686:16686 -n tracing
curl -s http://localhost:16686/api/services | jq '.data'
```

### 3.9 GitHub Actions OIDC CI/CD 파이프라인

- [ ] GitHub OIDC Provider AWS IAM 등록
  ```bash
  aws iam create-open-id-connect-provider \
    --url https://token.actions.githubusercontent.com \
    --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1 \
    --client-id-list sts.amazonaws.com
  ```
- [ ] OIDC 신뢰 관계 설정 (bos-cicd-role)
  - 조건: `repo:your-org/malaysia-bos:*` 만 허용
- [ ] GitHub Actions 워크플로우 구성:
  - `.github/workflows/ci.yml` — PR 빌드·테스트
  - `.github/workflows/deploy-staging.yml` — main 브랜치 → Staging
  - `.github/workflows/deploy-prod.yml` — Tag v*.*.* → Production
- [ ] ECR 리포지토리 생성 (서비스별):
  - `bos/transaction-service`
  - `bos/account-service`
  - `bos/billing-service`
  - `bos/violation-service`
  - `bos/equipment-service`
  - `bos/api-gateway`
- [ ] ArgoCD 배포 (K8s `argocd` Namespace) — GitOps 방식 배포 관리

**검증:**
```bash
# 테스트 워크플로우 실행
gh workflow run ci.yml --repo your-org/malaysia-bos

# ArgoCD 상태 확인
kubectl get applications -n argocd
```

### 3.10 DR Region (ap-southeast-3) 설정

- [ ] DR VPC 생성 (CIDR: 10.1.0.0/16)
- [ ] RDS Read Replica `bos-dr-db` 생성 (ap-southeast-3)
  - 자동 승격 대기 상태 유지
  - Replica Lag 모니터링 알림 (<5분 유지)
- [ ] S3 Cross-Region Replication 설정:
  - Source: `bos-delta-lake-raw` → Destination: `bos-delta-lake-raw-dr`
  - Source: `bos-anpr-images` → Destination: `bos-anpr-images-dr`
- [ ] EKS 스탠바이 클러스터 `malaysia-bos-dr` (최소 구성: 2 노드)
  - Failover 시 Node Group 자동 스케일업
- [ ] Route 53 Health Check 설정:
  - Primary: `api.malaysia-tolling.com` → ap-southeast-1 ALB
  - DR: Failover Record → ap-southeast-3 ALB (Health Check 실패 시 자동 전환)
- [ ] DR 훈련 스케줄: 분기 1회 (각 분기 마지막 토요일 03:00 KST)

**Failover RTO/RPO 목표:**
- RTO (Recovery Time Objective): ≤ 4시간
- RPO (Recovery Point Objective): ≤ 1시간

---

## 4. 핵심 IaC 코드 예시 — Terraform EKS 모듈 발췌

```hcl
# infra/terraform/eks/main.tf

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "malaysia-bos-prod"
  cluster_version = "1.30"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = false   # 퍼블릭 API 엔드포인트 비활성화

  # 클러스터 암호화
  cluster_encryption_config = {
    resources        = ["secrets"]
    provider_key_arn = aws_kms_key.eks.arn
  }

  # EKS 관리형 노드 그룹
  eks_managed_node_groups = {
    general = {
      name           = "general-workers"
      instance_types = ["t3.xlarge"]
      capacity_type  = "ON_DEMAND"

      min_size     = 3
      max_size     = 20
      desired_size = 3

      labels = {
        workload = "general"
        env      = "production"
      }

      taints = []

      block_device_mappings = {
        xvda = {
          device_name = "/dev/xvda"
          ebs = {
            volume_size           = 100
            volume_type           = "gp3"
            iops                  = 3000
            throughput            = 125
            encrypted             = true
            kms_key_id            = aws_kms_key.ebs.arn
            delete_on_termination = true
          }
        }
      }
    }

    spot_workers = {
      name           = "spot-workers"
      instance_types = ["t3.large", "t3a.large", "t3.xlarge"]
      capacity_type  = "SPOT"

      min_size     = 0
      max_size     = 30
      desired_size = 0

      labels = {
        workload       = "batch"
        "spot-worker"  = "true"
      }

      taints = [
        {
          key    = "spot"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      ]
    }
  }

  # IRSA를 위한 OIDC Provider 자동 생성
  enable_irsa = true

  # EKS Add-ons
  cluster_addons = {
    coredns = {
      most_recent = true
    }
    kube-proxy = {
      most_recent = true
    }
    vpc-cni = {
      most_recent    = true
      before_compute = true
      configuration_values = jsonencode({
        env = {
          ENABLE_PREFIX_DELEGATION = "true"
          WARM_PREFIX_TARGET       = "1"
        }
      })
    }
    aws-ebs-csi-driver = {
      most_recent              = true
      service_account_role_arn = aws_iam_role.ebs_csi.arn
    }
  }

  tags = {
    Project     = "malaysia-bos"
    Environment = "production"
    ManagedBy   = "terraform"
    Owner       = "devops-lead"
  }
}

# Cluster Autoscaler IRSA
module "cluster_autoscaler_irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.0"

  role_name                        = "bos-cluster-autoscaler"
  attach_cluster_autoscaler_policy = true
  cluster_autoscaler_cluster_names = [module.eks.cluster_name]

  oidc_providers = {
    ex = {
      provider_arn               = module.eks.oidc_provider_arn
      namespace_service_accounts = ["kube-system:cluster-autoscaler"]
    }
  }
}
```

```hcl
# infra/terraform/rds/main.tf

module "db" {
  source  = "terraform-aws-modules/rds/aws"
  version = "~> 6.0"

  identifier = "bos-prod-db"

  engine               = "postgres"
  engine_version       = "16.2"
  family               = "postgres16"
  major_engine_version = "16"
  instance_class       = "db.r6g.xlarge"

  allocated_storage     = 500
  max_allocated_storage = 2000
  storage_type          = "gp3"
  storage_throughput    = 500
  iops                  = 6000
  storage_encrypted     = true
  kms_key_id            = aws_kms_key.rds.arn

  db_name  = "bosdb"
  username = "bosadmin"
  # 패스워드는 Vault에서 동적 관리 (초기 생성 후 Vault 위임)
  manage_master_user_password = true

  multi_az               = true
  db_subnet_group_name   = aws_db_subnet_group.rds.name
  vpc_security_group_ids = [module.security_group_rds.security_group_id]

  maintenance_window              = "Sun:20:00-Sun:21:00"  # KST 일요일 새벽 3시
  backup_window                   = "18:00-19:00"          # KST 새벽 1-2시
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  backup_retention_period         = 7
  skip_final_snapshot             = false
  deletion_protection             = true

  performance_insights_enabled          = true
  performance_insights_retention_period = 7
  create_monitoring_role                = true
  monitoring_interval                   = 60

  parameters = [
    { name = "shared_preload_libraries", value = "pg_stat_statements" },
    { name = "log_statement",            value = "ddl" },
    { name = "log_min_duration_statement", value = "1000" },  # 1초 이상 쿼리 로그
  ]

  tags = {
    Project     = "malaysia-bos"
    Environment = "production"
  }
}
```

---

## 5. K8s 기본 설정 (Namespace, RBAC, NetworkPolicy)

### 5.1 Namespace 구성

```yaml
# infra/k8s/namespaces.yaml
---
apiVersion: v1
kind: Namespace
metadata:
  name: bos-core
  labels:
    app.kubernetes.io/part-of: malaysia-bos
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: bos-data
  labels:
    app.kubernetes.io/part-of: malaysia-bos
    environment: production
---
apiVersion: v1
kind: Namespace
metadata:
  name: monitoring
  labels:
    app.kubernetes.io/part-of: malaysia-bos
---
apiVersion: v1
kind: Namespace
metadata:
  name: vault
  labels:
    app.kubernetes.io/part-of: malaysia-bos
---
apiVersion: v1
kind: Namespace
metadata:
  name: tracing
  labels:
    app.kubernetes.io/part-of: malaysia-bos
---
apiVersion: v1
kind: Namespace
metadata:
  name: argocd
  labels:
    app.kubernetes.io/part-of: malaysia-bos
```

### 5.2 RBAC 기본 설정

```yaml
# infra/k8s/rbac/developer-role.yaml
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: bos-developer
rules:
  - apiGroups: [""]
    resources: ["pods", "pods/log", "services", "configmaps"]
    verbs: ["get", "list", "watch"]
  - apiGroups: ["apps"]
    resources: ["deployments", "replicasets"]
    verbs: ["get", "list", "watch"]
  # 개발자는 exec 불가 (보안 정책)
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: bos-devops
rules:
  - apiGroups: ["*"]
    resources: ["*"]
    verbs: ["*"]
  # devops-lead Agent만 해당 역할 부여
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: bos-devops-binding
subjects:
  - kind: ServiceAccount
    name: devops-lead-sa
    namespace: bos-core
roleRef:
  kind: ClusterRole
  name: bos-devops
  apiGroup: rbac.authorization.k8s.io
```

### 5.3 NetworkPolicy 기본 설정

```yaml
# infra/k8s/network-policy/default-deny.yaml
---
# 기본 정책: 모든 Ingress/Egress 차단 후 명시적 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: bos-core
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
---
# bos-core → RDS 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-rds-egress
  namespace: bos-core
spec:
  podSelector:
    matchLabels:
      needs-db: "true"
  policyTypes:
    - Egress
  egress:
    - ports:
        - protocol: TCP
          port: 5432
      to:
        - ipBlock:
            cidr: 10.0.10.0/24  # RDS Private Subnet
---
# bos-core → Kafka MSK 허용
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-kafka-egress
  namespace: bos-core
spec:
  podSelector:
    matchLabels:
      needs-kafka: "true"
  policyTypes:
    - Egress
  egress:
    - ports:
        - protocol: TCP
          port: 9096  # SASL_SSL
      to:
        - ipBlock:
            cidr: 10.0.10.0/23  # MSK Subnets
```

### 5.4 ResourceQuota (Namespace 리소스 제한)

```yaml
# infra/k8s/quotas/bos-core-quota.yaml
---
apiVersion: v1
kind: ResourceQuota
metadata:
  name: bos-core-quota
  namespace: bos-core
spec:
  hard:
    requests.cpu: "40"
    requests.memory: "80Gi"
    limits.cpu: "80"
    limits.memory: "160Gi"
    pods: "100"
    services: "30"
    persistentvolumeclaims: "20"
---
apiVersion: v1
kind: LimitRange
metadata:
  name: bos-core-limits
  namespace: bos-core
spec:
  limits:
    - type: Container
      defaultRequest:
        cpu: "100m"
        memory: "128Mi"
      default:
        cpu: "500m"
        memory: "512Mi"
      max:
        cpu: "4"
        memory: "8Gi"
```

---

## 6. 완료 기준 체크리스트

모든 항목이 체크된 후 devops-lead Agent가 CTO에게 Phase 0 완료 보고를 제출한다.

### 6.1 인프라 프로비저닝 완료

- [ ] `terraform apply` 실행 시 오류 없음, exit code 0
- [ ] Terraform State가 S3 `bos-terraform-state` 버킷에 정상 저장
- [ ] AWS Console에서 모든 리소스 `Available`/`Active` 상태 확인

### 6.2 EKS 클러스터

- [ ] `kubectl get nodes` → 3개 이상 노드 `Ready` 상태
- [ ] `kubectl get pods -n kube-system` → CoreDNS, kube-proxy 모두 `Running`
- [ ] Cluster Autoscaler Pod `Running`, 로그에서 오류 없음
- [ ] `kubectl auth can-i "*" "*"` → `devops-lead-sa` 계정에서 yes

### 6.3 데이터 레이어

- [ ] RDS: `psql -h $RDS_PROXY_ENDPOINT -U bosadmin bosdb` 접속 성공
- [ ] RDS Multi-AZ Failover: 강제 재부팅 후 30초 이내 자동 복구
- [ ] Kafka: `kafka-topics.sh --list` → 6개 토픽 모두 확인
- [ ] Redis: `CLUSTER INFO | cluster_state:ok`, 6개 노드 모두 확인

### 6.4 보안 & Vault

- [ ] Vault `Sealed: false`, Auto-unseal KMS 동작 확인
- [ ] Vault `database` 엔진: `vault read database/creds/bos-app` → 임시 자격증명 발급
- [ ] 보안 그룹: 외부에서 RDS/MSK/Redis 직접 접근 불가 (telnet 테스트)
- [ ] VPC Flow Logs CloudWatch에서 수신 확인

### 6.5 모니터링

- [ ] Prometheus: `http://localhost:9090/targets` → 모든 Target `UP`
- [ ] Grafana: Kubernetes 대시보드 정상 표시, 데이터 수신 확인
- [ ] Jaeger: `http://localhost:16686` 접근 가능, 서비스 목록 표시
- [ ] AlertManager: 테스트 알림 Slack 채널 `#ops-alert` 수신 확인

### 6.6 CI/CD

- [ ] GitHub Actions OIDC: `aws sts get-caller-identity` → `bos-cicd-role` ARN 확인
- [ ] ECR 이미지 Push 테스트: `docker push $ECR_REPO/bos/test:latest` 성공
- [ ] ArgoCD: `kubectl get applications -n argocd` → 동기화 상태 확인

### 6.7 DR 구성

- [ ] DR Region RDS Replica Lag < 5분 확인
- [ ] S3 Cross-Region Replication: 테스트 파일 업로드 후 DR 버킷에서 확인 (15분 이내)
- [ ] Route 53 Health Check: Primary 비활성화 시 DR로 트래픽 전환 확인

### 6.8 문서화

- [ ] `infra/docs/architecture-diagram.png` 업데이트
- [ ] `infra/docs/runbook.md` — 장애 대응 절차 작성 완료
- [ ] Terraform 모듈 README 갱신
- [ ] 모든 리소스 비용 추정값 업데이트 (AWS Cost Explorer 기준)

---

## 7. 리스크 & 대응 방안

| 리스크 | 발생 확률 | 영향도 | 대응 방안 | 담당 |
| ------ | --------- | ------ | --------- | ---- |
| AWS ap-southeast-3 서비스 미지원 (특정 인스턴스) | 중 (30%) | 높음 | 대체 인스턴스 타입 사전 확인, ap-southeast-1 임시 사용 | devops-lead |
| Terraform State 충돌 (동시 실행) | 낮 (10%) | 중간 | DynamoDB State Lock 필수 설정, CI/CD에서만 apply | devops-lead |
| EKS 버전 1.30 미지원 Add-on | 낮 (15%) | 낮음 | EKS Add-on 버전 호환성 매트릭스 선 검토 | devops-dev-1 |
| RDS 스토리지 용량 초과 (성장 예측 오류) | 낮 (20%) | 중간 | 자동 증설 ON, CloudWatch 80% 알림 설정 | devops-dev-2 |
| MSK Kafka 버전 지원 종료 | 낮 (10%) | 중간 | 관리형 버전 자동 패치 정책 활성화 | devops-dev-2 |
| Vault Auto-unseal KMS 키 삭제 | 매우낮 (5%) | 매우높음 | KMS Key 삭제 방지(DeletionWindow 30일), 정기 백업 | devops-lead |
| GitHub Actions OIDC 설정 오류 | 중 (25%) | 중간 | 로컬 테스트 환경 구성 후 검증 | devops-dev-1 |
| 비용 예상 초과 (Spot 인스턴스 제거) | 중 (30%) | 중간 | AWS Budget 알림 ($500 임계값), CFO 주간 보고 | devops-lead |

---

## 8. GSD 실행 명령어

```bash
# Phase 0 계획 검토
/gsd:discuss-phase 0

# Phase 0 상세 계획 수립
/gsd:plan-phase 0

# Phase 0 실행 (devops-lead Agent 활성화)
/gsd:execute-phase 0

# 진행 상황 확인
/gsd:progress

# Phase 0 완료 검증 (체크리스트 항목 자동 검사)
/gsd:verify-work 0

# 완료 후 마일스톤 기록
/gsd:complete-milestone "Phase 0: 공통 인프라 구축 완료 — EKS/RDS/Kafka/Vault 배포"
```

**단계별 실행 순서 (추천):**

```bash
# Step 1: VPC + 보안 그룹 먼저
/gsd:do "infra/terraform/vpc/ Terraform apply 실행"

# Step 2: EKS 클러스터 (VPC 완료 후)
/gsd:do "infra/terraform/eks/ Terraform apply 실행"

# Step 3: 데이터 레이어 (병렬 실행 가능)
/gsd:do "infra/terraform/rds/ + msk/ + redis/ Terraform apply 병렬"

# Step 4: S3 + DynamoDB
/gsd:do "infra/terraform/s3/ Terraform apply 실행"

# Step 5: Vault + 모니터링 (K8s 배포)
/gsd:do "K8s: Vault Helm + monitoring Helm 배포"

# Step 6: CI/CD + DR
/gsd:do "GitHub OIDC 설정 + DR Region 구성"

# Step 7: 완료 검증
/gsd:verify-work 0
```

---

## 9. 참조 문서

| 문서 | 경로 | 설명 |
| ---- | ---- | ---- |
| 기술 스택 | [02_system/03_tech_stack.md](../02_system/03_tech_stack.md) | AWS 서비스 버전·설정 기준 |
| 툴체인 가이드 | [04_dev/01_toolchain.md](../04_dev/01_toolchain.md) | Terraform, kubectl 설치 방법 |
| GSD 워크플로우 | [04_dev/05_gsd_workflow.md](../04_dev/05_gsd_workflow.md) | Phase 실행 명령어 |
| Phase 전체 개요 | [06_phases/00_phase_overview.md](./00_phase_overview.md) | 12개 Phase 의존성 |
| G-HARD 게이트 | [05_governance/01_decision_gates.md](../05_governance/01_decision_gates.md) | Gate 1 진입 조건 |
| 보안 컴플라이언스 | [03_data/05_security_compliance.md](../03_data/05_security_compliance.md) | PDPA, ISO 27001 요건 |
| RBAC 설계 | [03_data/03_rbac_design.md](../03_data/03_rbac_design.md) | IAM 역할 매핑 |
| 시스템 개요 | [02_system/01_system_overview.md](../02_system/01_system_overview.md) | 3-Layer 아키텍처 기준 |
| 예산 모델 | [04_dev/06_budget_model.md](../04_dev/06_budget_model.md) | Agent 비용 추정 방법론 |

---

*문서 생성: 2026-04-02*
*버전: v1.0*
*다음 검토: Phase 0 착수 시 (2026-04-22)*
