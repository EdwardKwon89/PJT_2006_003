# 개발 도구체인 설정
## 04_dev/01_toolchain.md
## v1.0 | 2026-04 | 참조: 02_system/03_tech_stack.md, 04_dev/05_gsd_workflow.md

---

> **Agent 사용 지침**
> DevOps Lead Agent가 신규 개발자 온보딩 또는 환경 구성 시 로드.
> 도구 버전 변경 시 이 문서 먼저 업데이트.

---

## 1. Executive Summary — 전체 도구체인 표

Malaysia SLFF/MLFF Tolling BOS 개발에 필요한 모든 도구의 공식 버전과 설치 명령을 정의한다. 신규 개발자는 이 표를 기준으로 환경을 구성하고, 버전 불일치 시 이 문서를 우선 기준으로 삼는다.

| 카테고리 | 도구명 | 버전 | 용도 | 설치 명령 |
|---|---|---|---|---|
| **JVM** | Eclipse Temurin (Java) | 21 LTS | 백엔드 런타임 | `sdk install java 21.0.3-tem` |
| **빌드** | Gradle | 8.7 | 백엔드 빌드 | 프로젝트 내 Gradle Wrapper 사용 |
| **Node.js** | Node.js | 20.14 LTS | 프론트엔드 런타임 | `nvm install 20.14` |
| **패키지** | npm | 10.x | JS 패키지 관리 | Node.js 번들 포함 |
| **패키지** | Yarn | 4.x (Berry) | 대안 패키지 관리 | `npm install -g yarn` |
| **Python** | Python | 3.11+ | Airflow DAG, 스크립트 | `pyenv install 3.11.9` |
| **컨테이너** | Docker Desktop | 4.30+ | 로컬 컨테이너 | [docs.docker.com](https://docs.docker.com) |
| **컨테이너** | docker-compose | v2.27+ | 로컬 서비스 오케스트레이션 | Docker Desktop 번들 포함 |
| **K8s CLI** | kubectl | 1.30 | 쿠버네티스 제어 | `brew install kubectl` |
| **Helm** | Helm | 3.15 | K8s 패키지 관리 | `brew install helm` |
| **AWS** | AWS CLI | v2.15+ | AWS 리소스 제어 | [aws.amazon.com/cli](https://aws.amazon.com/cli) |
| **AWS** | eksctl | 0.180+ | EKS 클러스터 관리 | `brew tap weaveworks/tap && brew install eksctl` |
| **비밀** | HashiCorp Vault CLI | 1.17 | 시크릿 조회 | `brew install vault` |
| **코드 품질** | SonarScanner CLI | 5.x | 코드 품질 분석 | `brew install sonar-scanner` |
| **IDE** | IntelliJ IDEA | 2024.1+ | 백엔드 개발 | [jetbrains.com](https://www.jetbrains.com) |
| **IDE** | VS Code | 최신 안정 | 프론트엔드 개발 | [code.visualstudio.com](https://code.visualstudio.com) |
| **버전 관리** | Git | 2.44+ | 소스 관리 | `brew install git` |
| **SDK 관리** | SDKMAN! | 최신 | Java/Gradle 버전 관리 | `curl -s "https://get.sdkman.io" \| bash` |
| **Node 관리** | nvm | 0.39+ | Node 버전 관리 | `brew install nvm` |
| **Python 관리** | pyenv | 2.4+ | Python 버전 관리 | `brew install pyenv` |

> **Windows 사용자 주의:** Windows 환경에서는 WSL 2 (Ubuntu 22.04 LTS)를 필수로 사용한다. 모든 설치 명령은 WSL 2 터미널 기준이다.

---

## 2. 필수 도구 설치

### 2.1 SDKMAN! 및 Java 21 (Eclipse Temurin)

SDKMAN!을 통해 Java 버전을 관리한다. 팀 전체가 동일한 JDK 벤더(Eclipse Temurin)를 사용해야 빌드 결과의 일관성이 보장된다.

```bash
# SDKMAN! 설치
curl -s "https://get.sdkman.io" | bash
source "$HOME/.sdkman/bin/sdkman-init.sh"

# Eclipse Temurin Java 21 설치 및 기본값 설정
sdk install java 21.0.3-tem
sdk default java 21.0.3-tem

# 설치 확인
java -version
# openjdk version "21.0.3" 2024-04-16 LTS
# OpenJDK Runtime Environment Temurin-21.0.3+9 (build 21.0.3+9-LTS)
```

**Gradle Wrapper (권장):** 각 프로젝트에는 `gradlew` Wrapper가 포함되어 있으므로, 시스템에 Gradle을 별도 설치할 필요 없다. 항상 `./gradlew` 명령을 사용한다.

```bash
# Gradle Wrapper 권한 부여 (최초 1회)
chmod +x ./gradlew

# Gradle 버전 확인
./gradlew --version
# Gradle 8.7
```

### 2.2 Node.js 20 LTS (nvm)

프론트엔드 개발 및 빌드 도구 실행에 필요하다. nvm으로 버전을 관리하여 프로젝트별 Node 버전 충돌을 방지한다.

```bash
# nvm 설치 (Linux/macOS)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc  # 또는 ~/.zshrc

# Node.js 20 LTS 설치
nvm install 20.14
nvm use 20.14
nvm alias default 20.14

# 설치 확인
node --version  # v20.14.0
npm --version   # 10.x.x

# Yarn 설치 (선택)
npm install -g yarn
yarn --version  # 4.x.x
```

`.nvmrc` 파일이 프로젝트 루트에 있으면 `nvm use` 명령으로 자동 전환된다.

```
# .nvmrc 내용
20.14
```

### 2.3 Python 3.11+ (pyenv)

Apache Airflow DAG 개발 및 데이터 처리 스크립트에 필요하다.

```bash
# pyenv 설치 (Linux)
curl https://pyenv.run | bash

# ~/.bashrc 또는 ~/.zshrc에 추가
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init -)"
source ~/.bashrc

# Python 3.11.9 설치
pyenv install 3.11.9
pyenv global 3.11.9

# 설치 확인
python --version  # Python 3.11.9

# 가상환경 설정 (프로젝트별)
python -m venv .venv
source .venv/bin/activate

# Airflow 의존성 설치
pip install apache-airflow==2.9.3 apache-airflow-providers-amazon
```

### 2.4 Docker Desktop 및 docker-compose

로컬 개발 환경에서 PostgreSQL, Redis, Kafka 등을 컨테이너로 실행한다.

```bash
# Docker 설치 확인
docker --version        # Docker version 26.x.x
docker compose version  # Docker Compose version v2.27.x

# Docker 데몬 실행 확인
docker info | grep "Server Version"

# 로컬 개발용 네트워크 생성 (최초 1회)
docker network create bos-local-network
```

### 2.5 kubectl 및 Helm 3

EKS 클러스터 접근 및 Helm 차트 배포에 사용한다.

```bash
# kubectl 설치 (Linux)
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
chmod +x kubectl
sudo mv kubectl /usr/local/bin/

# kubectl 설치 확인
kubectl version --client  # v1.30.x

# Helm 3 설치
curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
helm version  # version.BuildInfo{Version:"v3.15.x"}
```

### 2.6 AWS CLI v2 및 EKS kubeconfig 설정

AWS 리소스 제어 및 EKS 클러스터 인증에 필요하다. GitHub Actions OIDC 방식을 사용하므로 로컬에서는 SSO 또는 IAM 역할을 통해 인증한다.

```bash
# AWS CLI v2 설치 (Linux)
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# AWS CLI 버전 확인
aws --version  # aws-cli/2.15.x

# AWS SSO 설정 (개발자별 1회)
aws configure sso
# SSO start URL: https://YOUR-ORG.awsapps.com/start
# SSO Region: ap-southeast-1
# 이후 브라우저 인증 완료

# EKS kubeconfig 업데이트 (개발 클러스터)
aws eks update-kubeconfig \
  --name bos-eks-dev \
  --region ap-southeast-1 \
  --profile bos-dev

# 연결 확인
kubectl get nodes
kubectl get namespaces

# eksctl 설치 (클러스터 관리자 전용)
curl --silent --location \
  "https://github.com/weaveworks/eksctl/releases/latest/download/eksctl_$(uname -s)_amd64.tar.gz" | \
  tar xz -C /tmp
sudo mv /tmp/eksctl /usr/local/bin
eksctl version
```

**kubeconfig 프로파일 구성:**

| 프로파일 | 클러스터 | 리전 | 용도 |
|---|---|---|---|
| `bos-dev` | `bos-eks-dev` | `ap-southeast-1` | 개발 환경 |
| `bos-staging` | `bos-eks-staging` | `ap-southeast-1` | 스테이징 환경 |
| `bos-prod` | `bos-eks-prod` | `ap-southeast-1` | 운영 환경 (제한) |

---

## 3. 로컬 개발 환경 (docker-compose)

다음 `docker-compose.yml`을 프로젝트 루트의 `infra/local/` 디렉토리에 위치시킨다. 이 파일로 PostgreSQL 16, Redis 7, Kafka + Zookeeper를 로컬에서 실행한다.

```yaml
# infra/local/docker-compose.yml
version: "3.9"

services:
  # ─────────────────────────────────────────────
  # PostgreSQL 16 — 주요 데이터 저장소
  # ─────────────────────────────────────────────
  postgres:
    image: postgres:16-alpine
    container_name: bos-postgres
    restart: unless-stopped
    environment:
      POSTGRES_USER: bos_user
      POSTGRES_PASSWORD: bos_local_pw_change_me
      POSTGRES_DB: bos_dev
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init-scripts/postgres:/docker-entrypoint-initdb.d
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U bos_user -d bos_dev"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bos-local-network

  # ─────────────────────────────────────────────
  # Redis 7 — 캐시 및 세션 관리
  # ─────────────────────────────────────────────
  redis:
    image: redis:7-alpine
    container_name: bos-redis
    restart: unless-stopped
    command: >
      redis-server
      --requirepass bos_redis_pw_change_me
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --appendonly yes
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "-a", "bos_redis_pw_change_me", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - bos-local-network

  # ─────────────────────────────────────────────
  # Zookeeper — Kafka 클러스터 코디네이터
  # ─────────────────────────────────────────────
  zookeeper:
    image: confluentinc/cp-zookeeper:7.6.1
    container_name: bos-zookeeper
    restart: unless-stopped
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
      ZOOKEEPER_SYNC_LIMIT: 2
    ports:
      - "2181:2181"
    volumes:
      - zookeeper_data:/var/lib/zookeeper/data
      - zookeeper_logs:/var/lib/zookeeper/log
    networks:
      - bos-local-network

  # ─────────────────────────────────────────────
  # Apache Kafka 3.7 — 이벤트 스트리밍
  # ─────────────────────────────────────────────
  kafka:
    image: confluentinc/cp-kafka:7.6.1
    container_name: bos-kafka
    restart: unless-stopped
    depends_on:
      zookeeper:
        condition: service_started
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:29092,PLAINTEXT_HOST://localhost:9092
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
      KAFKA_LOG_RETENTION_HOURS: 168
      KAFKA_LOG_SEGMENT_BYTES: 1073741824
    ports:
      - "9092:9092"
      - "29092:29092"
    volumes:
      - kafka_data:/var/lib/kafka/data
    healthcheck:
      test: ["CMD-SHELL", "kafka-topics --bootstrap-server localhost:9092 --list"]
      interval: 30s
      timeout: 10s
      retries: 10
    networks:
      - bos-local-network

  # ─────────────────────────────────────────────
  # Kafka UI — 로컬 Kafka 모니터링 (선택)
  # ─────────────────────────────────────────────
  kafka-ui:
    image: provectuslabs/kafka-ui:latest
    container_name: bos-kafka-ui
    restart: unless-stopped
    depends_on:
      - kafka
    environment:
      KAFKA_CLUSTERS_0_NAME: bos-local
      KAFKA_CLUSTERS_0_BOOTSTRAPSERVERS: kafka:29092
      KAFKA_CLUSTERS_0_ZOOKEEPER: zookeeper:2181
    ports:
      - "8090:8080"
    networks:
      - bos-local-network

  # ─────────────────────────────────────────────
  # HashiCorp Vault — 로컬 시크릿 관리 (dev 모드)
  # ─────────────────────────────────────────────
  vault:
    image: hashicorp/vault:1.17
    container_name: bos-vault
    restart: unless-stopped
    command: server -dev -dev-root-token-id="bos-vault-root-token"
    environment:
      VAULT_DEV_ROOT_TOKEN_ID: bos-vault-root-token
      VAULT_DEV_LISTEN_ADDRESS: 0.0.0.0:8200
    ports:
      - "8200:8200"
    cap_add:
      - IPC_LOCK
    networks:
      - bos-local-network

# ─────────────────────────────────────────────
# 볼륨 정의
# ─────────────────────────────────────────────
volumes:
  postgres_data:
    name: bos-postgres-data
  redis_data:
    name: bos-redis-data
  zookeeper_data:
    name: bos-zookeeper-data
  zookeeper_logs:
    name: bos-zookeeper-logs
  kafka_data:
    name: bos-kafka-data

# ─────────────────────────────────────────────
# 네트워크 정의
# ─────────────────────────────────────────────
networks:
  bos-local-network:
    name: bos-local-network
    driver: bridge
```

**로컬 환경 시작/종료:**

```bash
# 로컬 환경 전체 시작
cd infra/local
docker compose up -d

# 서비스 상태 확인
docker compose ps

# 로그 확인 (특정 서비스)
docker compose logs -f kafka
docker compose logs -f postgres

# 로컬 환경 종료 (데이터 유지)
docker compose down

# 로컬 환경 초기화 (데이터 포함 삭제)
docker compose down -v
```

---

## 4. IDE 설정

### 4.1 IntelliJ IDEA (백엔드 개발)

**필수 플러그인 목록:**

| 플러그인 | 용도 | 설치 방법 |
|---|---|---|
| `Lombok` | @Data, @Builder 등 어노테이션 지원 | Settings → Plugins → Lombok |
| `Spring Boot` | Spring 개발 지원 (번들) | 기본 포함 |
| `Kubernetes` | K8s YAML 지원 | Settings → Plugins → Kubernetes |
| `Docker` | Dockerfile, compose 지원 | Settings → Plugins → Docker |
| `SonarLint` | 실시간 코드 품질 검사 | Settings → Plugins → SonarLint |
| `CheckStyle-IDEA` | Google Java Style 강제 | Settings → Plugins → CheckStyle-IDEA |
| `HashiCorp Vault` | Vault 통합 | Settings → Plugins → Vault |
| `.env files support` | .env 파일 하이라이팅 | Settings → Plugins → .env |
| `GitToolBox` | Git 브랜치 정보 인라인 표시 | Settings → Plugins → GitToolBox |
| `Rainbow Brackets` | 중괄호 색상 구분 | Settings → Plugins → Rainbow |

**Code Style 설정 (Google Java Style 기반):**

```bash
# Google Java Style 설정 파일 다운로드
curl -o intellij-java-google-style.xml \
  https://raw.githubusercontent.com/google/styleguide/gh-pages/intellij-java-google-style.xml

# IntelliJ에서 적용:
# Settings → Editor → Code Style → Java → [톱니바퀴] → Import Scheme
# → intellij-java-google-style.xml 선택
```

**핵심 IntelliJ 설정:**

```
# Settings → Build, Execution, Deployment → Compiler → Annotation Processors
✅ Enable annotation processing (Lombok 필수)

# Settings → Editor → General → Auto Import
✅ Add unambiguous imports on the fly
✅ Optimize imports on the fly

# Settings → Build, Execution, Deployment → Build Tools → Gradle
Gradle JVM: 프로젝트 SDK (Java 21 Temurin)
Build and run using: Gradle
Run tests using: Gradle
```

**JVM 메모리 설정 (`idea.vmoptions`):**

```
-Xms512m
-Xmx4096m
-XX:ReservedCodeCacheSize=512m
-XX:+UseG1GC
```

### 4.2 VS Code (프론트엔드 개발)

**권장 Extension 목록 (`.vscode/extensions.json`):**

```json
{
  "recommendations": [
    "esbenp.prettier-vscode",
    "dbaeumer.vscode-eslint",
    "ms-vscode.vscode-typescript-next",
    "bradlc.vscode-tailwindcss",
    "formulahendry.auto-rename-tag",
    "christian-kohler.path-intellisense",
    "ms-vscode-remote.remote-containers",
    "ms-azuretools.vscode-docker",
    "ms-kubernetes-tools.vscode-kubernetes-tools",
    "hashicorp.terraform",
    "streetsidesoftware.code-spell-checker",
    "usernamehw.errorlens",
    "eamodio.gitlens",
    "github.copilot",
    "vitest.explorer"
  ]
}
```

**VS Code 워크스페이스 설정 (`.vscode/settings.json`):**

```json
{
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": "explicit",
    "source.organizeImports": "explicit"
  },
  "typescript.preferences.importModuleSpecifier": "relative",
  "typescript.tsdk": "node_modules/typescript/lib",
  "tailwindCSS.experimental.classRegex": [
    ["cva\\(([^)]*)\\)", "[\"'`]([^\"'`]*).*?[\"'`]"],
    ["cx\\(([^)]*)\\)", "(?:'|\"|`)([^']*)(?:'|\"|`)"]
  ],
  "eslint.validate": ["javascript", "javascriptreact", "typescript", "typescriptreact"],
  "files.exclude": {
    "**/.git": true,
    "**/node_modules": true,
    "**/dist": true,
    "**/.next": true
  }
}
```

---

## 5. CI/CD 파이프라인 (GitHub Actions)

### 5.1 백엔드 CI 워크플로우

OIDC(OpenID Connect)를 사용하여 AWS 자격증명을 하드코딩 없이 안전하게 취득한다.

```yaml
# .github/workflows/backend-ci.yml
name: Backend CI

on:
  push:
    branches: [main, develop]
    paths:
      - "backend/**"
      - ".github/workflows/backend-ci.yml"
  pull_request:
    branches: [main, develop]
    paths:
      - "backend/**"

permissions:
  id-token: write   # OIDC 토큰 발급 필수
  contents: read
  checks: write

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    timeout-minutes: 30

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Java 21 (Temurin)
        uses: actions/setup-java@v4
        with:
          java-version: "21"
          distribution: "temurin"
          cache: gradle

      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-bos-role
          aws-region: ap-southeast-1

      - name: Validate Gradle Wrapper
        uses: gradle/actions/wrapper-validation@v3

      - name: Build with Gradle
        working-directory: backend
        run: ./gradlew build --no-daemon --parallel

      - name: Run Unit Tests
        working-directory: backend
        run: ./gradlew test --no-daemon

      - name: Run Integration Tests
        working-directory: backend
        run: ./gradlew integrationTest --no-daemon
        env:
          SPRING_PROFILES_ACTIVE: test

      - name: SonarQube Analysis
        working-directory: backend
        run: ./gradlew sonar --no-daemon
        env:
          SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
          SONAR_HOST_URL: ${{ secrets.SONAR_HOST_URL }}

      - name: Publish Test Results
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Backend Test Results
          path: backend/**/build/test-results/**/*.xml
          reporter: java-junit

      - name: Build Docker Image
        working-directory: backend
        run: |
          IMAGE_TAG="${{ github.sha }}"
          docker build -t bos-backend:${IMAGE_TAG} .

      - name: Push to ECR
        if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
        run: |
          aws ecr get-login-password --region ap-southeast-1 | \
            docker login --username AWS --password-stdin \
            ${{ secrets.ECR_REGISTRY }}
          docker tag bos-backend:${{ github.sha }} \
            ${{ secrets.ECR_REGISTRY }}/bos-backend:${{ github.sha }}
          docker push ${{ secrets.ECR_REGISTRY }}/bos-backend:${{ github.sha }}
```

### 5.2 프론트엔드 CI 워크플로우

```yaml
# .github/workflows/frontend-ci.yml
name: Frontend CI

on:
  push:
    branches: [main, develop]
    paths:
      - "frontend/**"
      - ".github/workflows/frontend-ci.yml"
  pull_request:
    branches: [main, develop]
    paths:
      - "frontend/**"

permissions:
  id-token: write
  contents: read

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    timeout-minutes: 20

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Node.js 20
        uses: actions/setup-node@v4
        with:
          node-version: "20.14"
          cache: "npm"
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        working-directory: frontend
        run: npm ci --prefer-offline

      - name: Type check
        working-directory: frontend
        run: npm run type-check

      - name: Lint
        working-directory: frontend
        run: npm run lint

      - name: Unit Tests (Vitest)
        working-directory: frontend
        run: npm run test:coverage

      - name: Build
        working-directory: frontend
        run: npm run build
        env:
          VITE_API_BASE_URL: ${{ secrets.VITE_API_BASE_URL }}

      - name: Configure AWS credentials (OIDC)
        if: github.ref == 'refs/heads/main' || github.ref == 'refs/heads/develop'
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::${{ secrets.AWS_ACCOUNT_ID }}:role/github-actions-bos-role
          aws-region: ap-southeast-1

      - name: Deploy to S3 (develop only)
        if: github.ref == 'refs/heads/develop'
        working-directory: frontend
        run: |
          aws s3 sync dist/ s3://${{ secrets.S3_BUCKET_DEV }} \
            --delete \
            --cache-control "max-age=31536000,immutable" \
            --exclude "index.html"
          aws s3 cp dist/index.html s3://${{ secrets.S3_BUCKET_DEV }}/index.html \
            --cache-control "no-cache,no-store,must-revalidate"
          aws cloudfront create-invalidation \
            --distribution-id ${{ secrets.CF_DISTRIBUTION_DEV }} \
            --paths "/*"
```

---

## 6. 코드 품질 도구

### 6.1 SonarQube 설정

프로젝트 루트의 `sonar-project.properties` 파일로 SonarQube를 구성한다.

```properties
# sonar-project.properties (백엔드)
sonar.projectKey=bos-backend
sonar.projectName=Malaysia BOS Backend
sonar.projectVersion=1.0

sonar.sources=src/main/java
sonar.tests=src/test/java
sonar.java.binaries=build/classes
sonar.java.libraries=build/libs/*.jar

sonar.coverage.jacoco.xmlReportPaths=build/reports/jacoco/test/jacocoTestReport.xml
sonar.junit.reportPaths=build/test-results/test

# 품질 게이트 기준
sonar.qualitygate.wait=true

# 제외 경로
sonar.exclusions=**/generated/**,**/config/**/*Config.java
sonar.coverage.exclusions=**/dto/**,**/entity/**,**/*Application.java
```

**Gradle SonarQube 플러그인 설정 (`build.gradle`):**

```groovy
plugins {
    id "org.sonarqube" version "5.0.0.4638"
    id "jacoco"
}

sonar {
    properties {
        property "sonar.host.url", System.getenv("SONAR_HOST_URL") ?: "http://localhost:9000"
        property "sonar.token", System.getenv("SONAR_TOKEN")
    }
}

jacocoTestReport {
    dependsOn test
    reports {
        xml.required = true
        html.required = true
    }
}

test {
    finalizedBy jacocoTestReport
    useJUnitPlatform()
    jvmArgs = [
        "--add-opens", "java.base/java.lang=ALL-UNNAMED"
    ]
}
```

### 6.2 CheckStyle (Google Java Style)

```xml
<!-- config/checkstyle/checkstyle.xml -->
<?xml version="1.0"?>
<!DOCTYPE module PUBLIC
  "-//Checkstyle//DTD Checkstyle Configuration 1.3//EN"
  "https://checkstyle.org/dtds/configuration_1_3.dtd">
<module name="Checker">
  <property name="charset" value="UTF-8"/>
  <property name="severity" value="error"/>
  <property name="fileExtensions" value="java"/>

  <module name="TreeWalker">
    <module name="OuterTypeFilename"/>
    <module name="IllegalTokenText"/>
    <module name="AvoidEscapedUnicodeCharacters"/>
    <module name="LineLength">
      <property name="max" value="120"/>
    </module>
    <module name="MissingOverride"/>
    <module name="NeedBraces"/>
    <module name="LeftCurly"/>
    <module name="RightCurly"/>
    <module name="EmptyBlock"/>
    <module name="FallThrough"/>
    <module name="MultipleVariableDeclarations"/>
    <module name="ModifiedControlVariable"/>
    <module name="UnnecessaryParentheses"/>
    <module name="UnusedImports"/>
  </module>
</module>
```

### 6.3 ESLint 및 Prettier (프론트엔드)

```json
// frontend/.eslintrc.json
{
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:react/recommended",
    "plugin:react-hooks/recommended",
    "plugin:jsx-a11y/recommended",
    "prettier"
  ],
  "plugins": ["@typescript-eslint", "react", "react-hooks", "jsx-a11y"],
  "rules": {
    "no-console": ["warn", { "allow": ["warn", "error"] }],
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unused-vars": ["error", { "argsIgnorePattern": "^_" }],
    "react/react-in-jsx-scope": "off",
    "react/prop-types": "off"
  },
  "settings": {
    "react": { "version": "detect" }
  }
}
```

```json
// frontend/.prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2,
  "endOfLine": "lf"
}
```

---

## 7. HashiCorp Vault 로컬 개발 설정

로컬 개발 시 Vault는 `dev` 모드(인메모리, 자동 Unseal)로 실행된다. 운영 환경 Vault 설정은 `02_system/03_tech_stack.md`를 참조한다.

### 7.1 Vault CLI 설정 및 시크릿 초기화

```bash
# Vault CLI 환경 변수 설정 (~/.bashrc 또는 ~/.zshrc)
export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="bos-vault-root-token"

# 설정 확인
vault status

# KV 시크릿 엔진 활성화 (v2)
vault secrets enable -path=bos kv-v2

# 개발 환경 시크릿 등록
vault kv put bos/dev/database \
  url="jdbc:postgresql://localhost:5432/bos_dev" \
  username="bos_user" \
  password="bos_local_pw_change_me"

vault kv put bos/dev/redis \
  host="localhost" \
  port="6379" \
  password="bos_redis_pw_change_me"

vault kv put bos/dev/kafka \
  bootstrap-servers="localhost:9092"

# 등록된 시크릿 확인
vault kv get bos/dev/database
vault kv list bos/dev/
```

### 7.2 Spring Boot Vault 통합 설정

```yaml
# backend/src/main/resources/application-local.yml
spring:
  config:
    import: vault://
  cloud:
    vault:
      host: localhost
      port: 8200
      scheme: http
      authentication: TOKEN
      token: bos-vault-root-token
      kv:
        enabled: true
        backend: bos
        default-context: dev
```

```groovy
// build.gradle 의존성 추가
dependencies {
    implementation 'org.springframework.cloud:spring-cloud-starter-vault-config:4.1.2'
}
```

### 7.3 Vault 정책 정의 (개발용)

```hcl
# vault/policies/bos-dev-policy.hcl
path "bos/data/dev/*" {
  capabilities = ["read", "list"]
}

path "bos/metadata/dev/*" {
  capabilities = ["read", "list"]
}
```

```bash
# 정책 등록
vault policy write bos-dev vault/policies/bos-dev-policy.hcl

# 개발용 앱 토큰 발급 (30일 TTL)
vault token create \
  -policy="bos-dev" \
  -ttl="720h" \
  -display-name="bos-backend-dev"
```

---

## 8. 자주 쓰는 개발 명령어 모음

### 8.1 백엔드 (Spring Boot / Gradle)

```bash
# ── 빌드 ──────────────────────────────────────────────
# 전체 빌드 (컴파일 + 테스트 + JAR)
./gradlew build

# 테스트 없이 빌드 (빠른 확인용)
./gradlew build -x test

# 병렬 빌드 (멀티 모듈)
./gradlew build --parallel --no-daemon

# ── 실행 ──────────────────────────────────────────────
# 로컬 프로파일로 실행
./gradlew bootRun --args='--spring.profiles.active=local'

# Docker 이미지 빌드
./gradlew bootBuildImage --imageName=bos-backend:local

# ── 테스트 ────────────────────────────────────────────
# 전체 단위 테스트
./gradlew test

# 통합 테스트 (별도 태스크)
./gradlew integrationTest

# 특정 테스트 클래스만 실행
./gradlew test --tests "com.bos.toll.service.TollServiceTest"

# 테스트 리포트 확인
open build/reports/tests/test/index.html

# 코드 커버리지 리포트
./gradlew jacocoTestReport
open build/reports/jacoco/test/html/index.html

# ── 코드 품질 ──────────────────────────────────────────
# CheckStyle 검사
./gradlew checkstyleMain checkstyleTest

# SonarQube 분석
./gradlew sonar

# 의존성 확인
./gradlew dependencies
./gradlew dependencyUpdates

# ── 클린업 ────────────────────────────────────────────
./gradlew clean
```

### 8.2 프론트엔드 (React / npm)

```bash
# ── 의존성 ────────────────────────────────────────────
npm ci                     # 의존성 설치 (CI 방식, package-lock.json 기준)
npm install <package>      # 패키지 추가
npm uninstall <package>    # 패키지 제거

# ── 개발 서버 ─────────────────────────────────────────
npm run dev                # Vite 개발 서버 시작 (HMR 포함)
npm run dev -- --port 3001 # 포트 변경

# ── 빌드 ──────────────────────────────────────────────
npm run build              # 프로덕션 빌드
npm run preview            # 빌드 결과 미리보기

# ── 코드 품질 ──────────────────────────────────────────
npm run type-check         # TypeScript 타입 검사
npm run lint               # ESLint 검사
npm run lint:fix           # ESLint 자동 수정
npm run format             # Prettier 포맷팅
npm run format:check       # Prettier 검사만 (수정 없음)

# ── 테스트 ────────────────────────────────────────────
npm test                   # Vitest 단위 테스트
npm run test:coverage      # 커버리지 포함 테스트
npm run test:ui            # Vitest UI (브라우저)
npm run test:watch         # Watch 모드

# ── E2E 테스트 ────────────────────────────────────────
npm run e2e                # Playwright E2E 실행
npm run e2e:ui             # Playwright UI 모드
```

### 8.3 Kubernetes / Helm

```bash
# ── 클러스터 컨텍스트 ─────────────────────────────────
kubectl config get-contexts
kubectl config use-context bos-dev

# ── 네임스페이스 확인 ─────────────────────────────────
kubectl get namespaces
kubectl get pods -n bos-backend
kubectl get svc -n bos-backend

# ── Helm 배포 ─────────────────────────────────────────
# 개발 환경 배포
helm upgrade --install bos-backend charts/bos-backend \
  --namespace bos-backend \
  --create-namespace \
  --values charts/bos-backend/values-dev.yaml \
  --set image.tag=$IMAGE_TAG

# 배포 상태 확인
helm list -n bos-backend
helm status bos-backend -n bos-backend

# 롤백
helm rollback bos-backend 1 -n bos-backend

# ── 디버깅 ────────────────────────────────────────────
kubectl logs -f deploy/bos-backend -n bos-backend
kubectl exec -it deploy/bos-backend -n bos-backend -- /bin/bash
kubectl describe pod <pod-name> -n bos-backend
kubectl top pods -n bos-backend
```

### 8.4 Docker Compose (로컬 환경)

```bash
# 로컬 서비스 전체 시작
cd infra/local && docker compose up -d

# 특정 서비스만 시작
docker compose up -d postgres redis

# 서비스 상태 확인
docker compose ps
docker compose top

# 특정 서비스 재시작
docker compose restart kafka

# 로그 확인
docker compose logs -f postgres
docker compose logs --tail=100 kafka

# PostgreSQL 접속
docker compose exec postgres psql -U bos_user -d bos_dev

# Redis CLI 접속
docker compose exec redis redis-cli -a bos_redis_pw_change_me

# Kafka 토픽 목록 확인
docker compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 --list

# Kafka 토픽 생성
docker compose exec kafka kafka-topics \
  --bootstrap-server localhost:9092 \
  --create --topic toll.events \
  --partitions 6 \
  --replication-factor 1

# 환경 초기화 (볼륨 포함)
docker compose down -v
```

### 8.5 Vault (시크릿 관리)

```bash
# 환경 변수 설정
export VAULT_ADDR="http://localhost:8200"
export VAULT_TOKEN="bos-vault-root-token"

# 시크릿 읽기
vault kv get bos/dev/database
vault kv get -format=json bos/dev/redis | jq '.data.data'

# 시크릿 업데이트
vault kv patch bos/dev/database password="new_password"

# 시크릿 버전 이력 확인
vault kv metadata get bos/dev/database

# 특정 버전 시크릿 읽기
vault kv get -version=2 bos/dev/database
```

---

## 9. 참조 문서

| 문서 | 경로 | 설명 |
|---|---|---|
| 기술 스택 상세 | `02_system/03_tech_stack.md` | 전체 기술 스택 및 버전 호환성 |
| GSD 워크플로우 | `04_dev/05_gsd_workflow.md` | 개발 프로세스 및 브랜치 전략 |
| 시스템 개요 | `02_system/01_system_overview.md` | BOS 아키텍처 전체 구조 |
| 외부 연계 | `02_system/05_external_integration.md` | 외부 시스템 연동 스펙 |
| RBAC 설계 | `03_data/03_rbac_design.md` | 역할 기반 접근 제어 |
| 보안 컴플라이언스 | `03_data/05_security_compliance.md` | PDPA 준수 및 보안 요구사항 |
| API MCP 스펙 | `02_system/06_api_mcp_spec.md` | API 설계 및 MCP Agent 스펙 |

---

*문서 버전: v1.0 | 최종 수정: 2026-04 | 작성자: DevOps Lead Agent*
*다음 검토 예정: 도구 버전 변경 시 또는 분기별*
