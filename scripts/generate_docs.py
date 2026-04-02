"""
BOS Documentation Generator — Cost-Aware LLM Pipeline
======================================================
Malaysia SLFF/MLFF Tolling BOS 문서 자동 생성 스크립트.

모델 라우팅:
  - claude-haiku-4-5-20251001  : 07_skills/ (간단, 템플릿화, ~300줄)
  - claude-sonnet-4-6          : 04_dev/, 06_phases/ (복잡, 아키텍처 결정)

비용 절감 전략:
  1. 복잡도 기반 모델 라우팅 (Haiku는 Sonnet 대비 ~4배 저렴)
  2. 프로젝트 컨텍스트 프롬프트 캐싱 (매 호출마다 재전송 방지)
  3. 불변 CostTracker (누적 비용 추적, 예산 초과 시 중단)
  4. 재시도: 네트워크/Rate Limit 오류만, 인증/파라미터 오류는 즉시 실패

사용법:
  python scripts/generate_docs.py --phase 4          # Phase 4 (04_dev/)
  python scripts/generate_docs.py --phase 5          # Phase 5 (06_phases/)
  python scripts/generate_docs.py --phase 6          # Phase 6 (07_skills/)
  python scripts/generate_docs.py --phase 4 --dry-run  # 모델 라우팅만 확인
  python scripts/generate_docs.py --phase 4 --budget 2.0  # 예산 $2.00
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path

import anthropic
from anthropic import (
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    InternalServerError,
    RateLimitError,
)

# ---------------------------------------------------------------------------
# 상수 및 모델 설정
# ---------------------------------------------------------------------------

MODEL_SONNET = "claude-sonnet-4-6"
MODEL_HAIKU  = "claude-haiku-4-5-20251001"

# 구독형 플랜: 모든 Phase에 Sonnet 사용 (품질 우선)
# API 종량제 사용 시 --force-model haiku 옵션으로 비용 절감 가능
DEFAULT_MODEL = MODEL_SONNET

# 출력 예상 줄 수 기준 (API 종량제 시 라우팅 기준, 구독형에서는 무시)
SONNET_LINE_THRESHOLD = 400

# 가격 ($/1M tokens, 2025-2026) — API 종량제 사용 시 참고
PRICING = {
    MODEL_HAIKU:  {"input": 0.80,  "output": 4.00},
    MODEL_SONNET: {"input": 3.00,  "output": 15.00},
}

BASE_DIR = Path(__file__).parent.parent          # c:\WorkSpaces\PJT_2026_002
DOCS_DIR = BASE_DIR / "docs"
CONTEXT_FILES = [                                # 캐시할 공통 컨텍스트
    BASE_DIR / ".planning" / "PROJECT.md",
    BASE_DIR / ".planning" / "REQUIREMENTS.md",
    DOCS_DIR / "01_business" / "01_project_charter.md",
    DOCS_DIR / "02_system" / "01_system_overview.md",
]

RETRYABLE = (APIConnectionError, RateLimitError, InternalServerError)
MAX_RETRIES = 3

# ---------------------------------------------------------------------------
# 데이터 모델
# ---------------------------------------------------------------------------

@dataclass(frozen=True, slots=True)
class DocTask:
    """문서 생성 작업 정의."""
    phase: int
    output_path: Path       # 생성할 파일 경로
    title: str              # 문서 제목
    prompt: str             # 생성 지시 프롬프트
    expected_lines: int     # 예상 줄 수 (모델 라우팅 기준)
    lead_agent: str         # 담당 Agent (문서화용)


@dataclass(frozen=True, slots=True)
class CostRecord:
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    cost_usd: float
    file_path: str


@dataclass(frozen=True, slots=True)
class CostTracker:
    budget_limit: float = 5.00
    records: tuple[CostRecord, ...] = ()

    def add(self, record: CostRecord) -> CostTracker:
        return CostTracker(
            budget_limit=self.budget_limit,
            records=(*self.records, record),
        )

    @property
    def total_cost(self) -> float:
        return sum(r.cost_usd for r in self.records)

    @property
    def over_budget(self) -> bool:
        return self.total_cost > self.budget_limit

    def summary(self) -> str:
        sonnet_count = sum(1 for r in self.records if MODEL_SONNET in r.model)
        haiku_count  = sum(1 for r in self.records if MODEL_HAIKU in r.model)
        cache_savings = sum(r.cache_read_tokens for r in self.records)
        lines = [
            f"  총 비용:       ${self.total_cost:.4f} / ${self.budget_limit:.2f}",
            f"  Sonnet 호출:   {sonnet_count}회",
            f"  Haiku 호출:    {haiku_count}회",
            f"  캐시 절약:     {cache_savings:,} tokens",
            f"  처리 파일:     {len(self.records)}개",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 비용 계산
# ---------------------------------------------------------------------------

def calc_cost(model: str, usage) -> float:
    p = PRICING[model]
    input_cost  = usage.input_tokens  * p["input"]  / 1_000_000
    output_cost = usage.output_tokens * p["output"] / 1_000_000
    # 캐시 읽기는 입력 가격의 10%
    cache_read_cost = getattr(usage, "cache_read_input_tokens", 0) * p["input"] * 0.1 / 1_000_000
    return input_cost + output_cost + cache_read_cost


# ---------------------------------------------------------------------------
# 모델 라우팅
# ---------------------------------------------------------------------------

def select_model(task: DocTask, force_model: str | None = None) -> str:
    if force_model:
        return force_model
    # 구독형: 항상 Sonnet (품질 우선)
    # API 종량제로 전환 시 아래 주석을 해제하면 Haiku 라우팅 활성화:
    # if task.phase == 6 or task.expected_lines < SONNET_LINE_THRESHOLD:
    #     return MODEL_HAIKU
    return DEFAULT_MODEL


# ---------------------------------------------------------------------------
# 공통 컨텍스트 로드 (프롬프트 캐싱용)
# ---------------------------------------------------------------------------

def load_context() -> str:
    """공통 프로젝트 컨텍스트를 하나의 문자열로 합산."""
    parts = []
    for path in CONTEXT_FILES:
        if path.exists():
            parts.append(f"=== {path.name} ===\n{path.read_text(encoding='utf-8')[:3000]}")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# 재시도 로직
# ---------------------------------------------------------------------------

def call_with_retry(func, *, max_retries: int = MAX_RETRIES):
    for attempt in range(max_retries):
        try:
            return func()
        except RETRYABLE as e:
            if attempt == max_retries - 1:
                raise
            wait = 2 ** attempt
            print(f"  ⚠ 재시도 {attempt+1}/{max_retries} ({type(e).__name__}) — {wait}초 대기...")
            time.sleep(wait)
        except (AuthenticationError, BadRequestError):
            raise  # 즉시 실패


# ---------------------------------------------------------------------------
# 문서 생성 핵심 함수
# ---------------------------------------------------------------------------

def generate_doc(
    client: anthropic.Anthropic,
    task: DocTask,
    context: str,
    tracker: CostTracker,
    force_model: str | None = None,
    dry_run: bool = False,
) -> tuple[bool, CostTracker]:
    """단일 문서 파일을 생성하고 비용을 추적한다."""

    model = select_model(task, force_model)
    rel_path = task.output_path.relative_to(BASE_DIR)

    print(f"\n{'─'*60}")
    print(f"  파일: {rel_path}")
    print(f"  모델: {model.split('-')[1].upper()} ({model})")
    print(f"  예상 줄 수: ~{task.expected_lines}줄")

    if tracker.over_budget:
        print(f"  ❌ 예산 초과 — 건너뜀 (${tracker.total_cost:.4f} / ${tracker.budget_limit:.2f})")
        return False, tracker

    if task.output_path.exists():
        print(f"  ⏭ 이미 존재 — 건너뜀")
        return True, tracker

    if dry_run:
        print(f"  🔍 Dry-run — 실제 생성 생략")
        return True, tracker

    # 부모 디렉토리 생성
    task.output_path.parent.mkdir(parents=True, exist_ok=True)

    system_prompt = f"""당신은 Malaysia SLFF/MLFF Tolling BOS 프로젝트의 {task.lead_agent}입니다.
아래 프로젝트 컨텍스트를 기반으로 고품질 기술 문서를 작성하세요.

규칙:
- 작성 언어: 한국어 (기술 용어·코드·API는 영어)
- 형식: GitHub Flavored Markdown
- 코드 블록, 표, ASCII 다이어그램을 적극 활용
- self-contained: 이 파일만 읽어도 이해 가능해야 함
- Kafka 토픽: raw.* 패턴 사용 (toll.* 사용 금지)
- API 엔드포인트: 복수형 명사 사용

=== 프로젝트 컨텍스트 ===
{context}"""

    user_message = task.prompt

    def _call():
        return client.messages.create(
            model=model,
            max_tokens=8192,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": system_prompt,
                            "cache_control": {"type": "ephemeral"},  # 캐시 적용
                        },
                        {
                            "type": "text",
                            "text": user_message,
                        },
                    ],
                }
            ],
        )

    try:
        response = call_with_retry(_call)
    except Exception as e:
        print(f"  ❌ API 오류: {e}")
        return False, tracker

    content = response.content[0].text
    usage   = response.usage
    cost    = calc_cost(model, usage)

    record = CostRecord(
        model=model,
        input_tokens=usage.input_tokens,
        output_tokens=usage.output_tokens,
        cache_read_tokens=getattr(usage, "cache_read_input_tokens", 0),
        cache_write_tokens=getattr(usage, "cache_creation_input_tokens", 0),
        cost_usd=cost,
        file_path=str(rel_path),
    )
    tracker = tracker.add(record)

    # 파일 저장
    task.output_path.write_text(content, encoding="utf-8")
    line_count = content.count("\n")

    print(f"  ✅ 생성 완료 ({line_count}줄)")
    print(f"     토큰: in={usage.input_tokens:,} out={usage.output_tokens:,}"
          f" cache_read={record.cache_read_tokens:,}")
    print(f"     비용: ${cost:.4f}  누적: ${tracker.total_cost:.4f}")

    return True, tracker


# ---------------------------------------------------------------------------
# Phase별 태스크 정의
# ---------------------------------------------------------------------------

def phase4_tasks() -> list[DocTask]:
    """Phase 4 (Wave 5): 04_dev/ 6개 파일"""
    base = DOCS_DIR / "04_dev"
    return [
        DocTask(
            phase=4,
            output_path=base / "01_toolchain.md",
            title="개발 도구체인 설정",
            expected_lines=450,
            lead_agent="DevOps Lead Agent",
            prompt="""# 개발 도구체인 설정
## 04_dev/01_toolchain.md
## v1.0 | 2026-04 | 참조: 02_system/03_tech_stack.md

파일 헤더 포함하여 작성. Agent 사용 지침 블록(DevOps Agent용) 포함.

내용 구성 (450~520줄):
1. Executive Summary — 전체 도구체인 표 (도구명, 버전, 용도, 설치 방법)
2. 필수 도구 설치 (Java 21, Node 20, Python 3.11+, Docker, kubectl, helm)
3. AWS CLI + EKS kubeconfig 설정
4. 로컬 개발 환경 (docker-compose.yml 예시 — PostgreSQL, Redis, Kafka)
5. IDE 설정 (IntelliJ IDEA, VS Code 권장 플러그인)
6. CI/CD 파이프라인 (GitHub Actions 워크플로우 YAML)
7. 코드 품질 도구 (SonarQube, CheckStyle, ESLint)
8. 시크릿 관리 (HashiCorp Vault 로컬 설정)
9. 참조 문서

기술 스택 기준: Spring Boot 3.x (Java 21), React 18 (TypeScript), AWS EKS
""",
        ),
        DocTask(
            phase=4,
            output_path=base / "02_paperclip_org.md",
            title="Paperclip 29-Agent 조직도",
            expected_lines=500,
            lead_agent="Paperclip Architect Agent",
            prompt="""# Paperclip 29-Agent 조직도
## 04_dev/02_paperclip_org.md
## v1.0 | 2026-04 | 참조: 01_business/04_organization_roles.md, 02_system/04_ai_features.md

파일 헤더 포함하여 작성. Agent 사용 지침 블록 포함.

내용 구성 (500~580줄):
1. Executive Summary — Paperclip 29-Agent 조직 철학
2. 조직 계층도 (ASCII 다이어그램)
3. 운영팀 6명 상세:
   - CEO Agent: 전략·의사결정·Heartbeat 보고
   - CTO Agent: 기술 아키텍처·시스템 설계 감독
   - CFO Agent: 비용·예산·정산 감독
   - CIO Agent: 데이터·보안·인프라 감독
   - Compliance Agent: PDPA·규정 준수
   - PM Agent: 일정·리스크·진행 관리
4. 도메인팀 23명 상세 표 (Agent명, 담당 도메인, 주요 책임, 사용 MCP Tools):
   txn-lead/dev×2, account-lead/dev×2, billing-lead/dev×2,
   violation-lead/dev×2, unpaid-lead, exemption-lead, review-lead,
   equipment-lead/dev, reporting-lead/dev, api-lead,
   devops-lead/dev×2
5. Agent 간 위임 프로토콜 (에스컬레이션 경로)
6. BOS MCP Server 연계 (각 Agent가 주로 사용하는 MCP Tools)
7. Heartbeat 참여 구조 (일별/주별/월별 보고 참여 Agent)
8. 참조 문서
""",
        ),
        DocTask(
            phase=4,
            output_path=base / "03_agent_roles.md",
            title="Agent 역할 정의",
            expected_lines=480,
            lead_agent="PM Agent",
            prompt="""# Agent 역할 정의
## 04_dev/03_agent_roles.md
## v1.0 | 2026-04 | 참조: 04_dev/02_paperclip_org.md, 03_data/03_rbac_design.md

파일 헤더 포함하여 작성. Agent 사용 지침 블록 포함.

내용 구성 (480~550줄):
1. Executive Summary — Agent 역할 원칙 (단일 책임, 최소 권한)
2. Agent 역할 카드 (29개 각각):
   각 카드: Agent명 | 레벨 | 주요 책임 | 결정 권한 | 에스컬레이션 대상 | 주요 Skills
3. RBAC 연계 (03_data/03_rbac_design.md의 30개 역할과 Agent 매핑)
4. Agent 간 협업 패턴:
   - Request-Response (동기)
   - Publish-Subscribe (비동기 이벤트)
   - Delegation (위임 후 결과 수신)
5. 금지 사항 (Agent가 직접 수행할 수 없는 작업 목록)
6. Agent 성과 지표 (KPI per Agent)
7. 참조 문서
""",
        ),
        DocTask(
            phase=4,
            output_path=base / "04_skills_index.md",
            title="21개 Skills 파일 인덱스",
            expected_lines=400,
            lead_agent="Knowledge Architect Agent",
            prompt="""# 21개 Skills 파일 인덱스
## 04_dev/04_skills_index.md
## v1.0 | 2026-04 | 참조: 04_dev/03_agent_roles.md, .planning/ROADMAP.md

파일 헤더 포함하여 작성. Agent 사용 지침 블록 포함.

내용 구성 (400~460줄):
1. Executive Summary — Skills 파일 목적 및 구조
2. Skills 파일 표준 포맷:
   ```yaml
   name: skill-name
   description: 한 줄 설명
   use_when: [적용 상황 목록]
   dont_use_when: [제외 상황 목록]
   content: |
     ...실제 내용...
   ```
3. 21개 Skills 전체 인덱스 표:
   (번호, 파일 경로, 제목, 담당 Agent, 관련 Phase, 설명)
   Round 1: malaysia-tolling-domain, traditional-tolling-roles, rfid-anpr-interface,
             mlff-session-matching, clearing-center-operations, payment-failure-scenarios
   Round 2: jpj-integration, tng-payment, external-api-mcp,
             data-architecture-standards, metadata-management, rbac-data-boundary
   Round 3: aggregation-units, text-to-sql-engine, ai-fault-detection,
             rpa-workflows, ai-decision-policy, simulation-design
   Round 4: bigdata-service-framework, code-quality-standards, change-management
4. Skills 사용 가이드 (Agent가 Skills 로드하는 방법)
5. 교차 참조 매트릭스 (Skills × Phase 매핑)
6. 참조 문서
""",
        ),
        DocTask(
            phase=4,
            output_path=base / "05_gsd_workflow.md",
            title="GSD 워크플로우 & 명령어",
            expected_lines=460,
            lead_agent="GSD Expert Agent",
            prompt="""# GSD 워크플로우 & 명령어
## 04_dev/05_gsd_workflow.md
## v1.0 | 2026-04 | 참조: 04_dev/02_paperclip_org.md, 05_governance/03_reporting_cycle.md

파일 헤더 포함하여 작성. Agent 사용 지침 블록 포함.

내용 구성 (460~530줄):
1. Executive Summary — GSD(Get Shit Done) 워크플로우 개요
2. 핵심 GSD 명령어 레퍼런스 표:
   /gsd:progress, /gsd:plan-phase, /gsd:execute-phase, /gsd:verify-work,
   /gsd:check-todos, /gsd:pause-work, /gsd:resume-work, /gsd:health,
   /gsd:note, /gsd:do, /gsd:review
3. Phase 실행 표준 절차:
   plan-phase → execute-phase → verify-work → commit
4. Heartbeat 워크플로우 (일별/주별 체크인):
   - 일별: Agent 상태 보고 → PM 집계 → CEO 보고
   - 주별: G-HARD 점수 갱신 → Gate 심사
5. Agent 충돌 방지 프로토콜 (/gsd:pause-work 활용)
6. 예산 초과 대응 절차
7. GSD 상태 파일 구조 (.planning/STATE.md)
8. 자주 쓰는 시나리오별 명령어 예시 (5개)
9. 참조 문서
""",
        ),
        DocTask(
            phase=4,
            output_path=base / "06_budget_model.md",
            title="비용 모델 & 최적화",
            expected_lines=440,
            lead_agent="CFO Agent",
            prompt="""# 비용 모델 & 최적화
## 04_dev/06_budget_model.md
## v1.0 | 2026-04 | 참조: 04_dev/02_paperclip_org.md, 02_system/04_ai_features.md

파일 헤더 포함하여 작성. Agent 사용 지침 블록 포함.

내용 구성 (440~510줄):
1. Executive Summary — 비용 구조 전체 표
2. Claude API 비용 모델:
   - 모델별 가격표 (Haiku 4.5, Sonnet 4.6, Opus 4.5)
   - 프롬프트 캐싱 절감 효과 (캐시 읽기 = 입력 10%)
3. Paperclip 29-Agent 월간 비용 추정:
   - Agent별 평균 호출 수 × 토큰 × 가격
   - Phase별 예상 총 비용 표
4. 모델 라우팅 전략:
   - Haiku: Skills, 단순 조회, 빈도 높은 경량 작업
   - Sonnet: 아키텍처 결정, 복잡한 분석
   - Opus: 최고 난이도 전략 결정 (희소 사용)
5. 비용 최적화 기법:
   - 프롬프트 캐싱 (시스템 프롬프트 > 1024 토큰)
   - 배치 처리 (독립적 작업 병렬화)
   - 응답 길이 제어 (max_tokens 적절히 설정)
6. 예산 관리 & 알림 임계값
7. ROI 분석 (Agent 투입 대비 절감 효과)
8. 참조 문서

가격 기준: Haiku $0.80/$4.00, Sonnet $3.00/$15.00 per 1M tokens (input/output)
""",
        ),
    ]


def phase5_tasks() -> list[DocTask]:
    """Phase 5 (Wave 6): 06_phases/ 13개 파일"""
    base = DOCS_DIR / "06_phases"
    tasks = []

    phase_defs = [
        ("00_phase_overview.md", "전체 Phase 개요", 500,
         "00_phase_overview.md — 전체 13개 Phase 개요, 의존성 다이어그램, 예산 배분표, 각 Phase 한 줄 요약"),
        ("01_phase01_infra.md", "Phase 1: 공통 인프라", 480,
         "01_phase01_infra.md — AWS EKS 클러스터, RDS PostgreSQL, MSK Kafka, Redis, S3 인프라 구축. IaC(Terraform), K8s 기본 설정, 네트워크/보안 그룹"),
        ("02_phase02_comm.md", "Phase 2: 커뮤니케이션 레이어", 460,
         "02_phase02_comm.md — RFID/ANPR 이벤트 수신기(gRPC), Kafka 토픽 구성, 이벤트 스키마(raw.rfid.events 등), 처리 파이프라인"),
        ("03_phase03_txn.md", "Phase 3: 트랜잭션 처리", 480,
         "03_phase03_txn.md — txn-service 구현, SLFF/MLFF 과금 로직, Entry-Exit 매칭, Redis 세션, Channel A/B 처리"),
        ("04_phase04_account.md", "Phase 4: 계정 관리", 460,
         "04_phase04_account.md — account-service, 개인/법인/플릿 계정, 차량 등록, RFID 태그 발급, JPJ 연동"),
        ("05_phase05_billing.md", "Phase 5: 빌링 & 정산", 470,
         "05_phase05_billing.md — billing-service, 일별/월별 집계, JVC 수수료 차감, TnG Channel B 정산, Clearing Center 연동"),
        ("06_phase06_violation.md", "Phase 6: 위반 & 미납", 480,
         "06_phase06_violation.md — violation/unpaid/exemption/review-service, Tier 1~4 미납 추적, JPJ 도로세 차단, 면제 처리"),
        ("07_phase07_equipment.md", "Phase 7: 장비 모니터링", 450,
         "07_phase07_equipment.md — equipment-service, 레인별 장비 상태, 장애 감지, AI 자동 복구, 현장 Mobile App 연동"),
        ("08_phase08_bigdata.md", "Phase 8: 빅데이터 & 분석", 490,
         "08_phase08_bigdata.md — reporting-service + Layer 3, Delta Lake Bronze/Silver/Gold, Spark 배치, Airflow DAG, 요금 시뮬레이션, TOC 운영 분석"),
        ("09_phase09_ai.md", "Phase 9: AI 고도화", 480,
         "09_phase09_ai.md — Text-to-SQL, 업무 판단 AI, 수익 예측 모델, 이상 탐지(사기/클론), AI 장애 탐지 고도화"),
        ("10_phase10_app.md", "Phase 10: 웹/모바일 앱", 470,
         "10_phase10_app.md — BOS Admin Web(React 18), 현장 Mobile App(React Native), 다국어 BM/EN, KPI 대시보드, 오프라인 지원"),
        ("11_phase11_api.md", "Phase 11: 외부 API & MCP", 460,
         "11_phase11_api.md — api-service, External REST API 퍼블리시, BOS MCP Server, TOC 연동, Rate Limiting, 버전 관리"),
        ("12_phase12_deploy.md", "Phase 12: 운영 이관", 470,
         "12_phase12_deploy.md — DR 구성, 성능 테스트(10K TPS), 보안 감사, 사용자 교육, Go-Live 체크리스트, 운영 이관 절차"),
    ]

    for filename, title, lines, prompt_hint in phase_defs:
        tasks.append(DocTask(
            phase=5,
            output_path=base / filename,
            title=title,
            expected_lines=lines,
            lead_agent="PM Agent + Phase Lead",
            prompt=f"""# {title}
## 06_phases/{filename}
## v1.0 | 2026-04 | 참조: 04_dev/05_gsd_workflow.md, 02_system/02_service_domains.md

파일 헤더 포함하여 작성. Agent 사용 지침 블록 포함.

이 파일의 주제: {prompt_hint}

내용 구성 ({lines}~{lines+70}줄):
1. Phase 개요 (목적, 선행 Phase, 후속 Phase, 예상 기간)
2. 담당 Agent 목록 (Lead + 팀원)
3. 주요 태스크 목록 (체크리스트 형식)
4. 기술 구현 상세 (핵심 코드 패턴, 설정 예시)
5. 완료 기준 (테스트 가능한 체크리스트)
6. 리스크 & 대응 방안
7. GSD 실행 명령어 (/gsd:plan-phase, /gsd:execute-phase 등)
8. 참조 문서

Kafka 토픽: raw.* 패턴 사용. API 엔드포인트: 복수형 명사.
""",
        ))

    return tasks


def phase6_tasks() -> list[DocTask]:
    """Phase 6 (Wave 7): 07_skills/ 21개 파일 — Haiku 사용"""
    base = DOCS_DIR / "07_skills"

    skill_defs = [
        # Round 1
        ("malaysia-tolling-domain", "말레이시아 톨링 도메인 지식",
         "SLFF/MLFF 구조, TnG/PLUS 경쟁 환경, JPJ 규제, Channel A/B, 콘세셔네어 체계"),
        ("traditional-tolling-roles", "전통 톨링 운영 역할",
         "플라자 관리자, 현장 기술자, 슈퍼바이저, 컴플라이언스 역할 정의와 권한"),
        ("rfid-anpr-interface", "RFID/ANPR 인터페이스",
         "gRPC 이벤트 수신, 신뢰도 점수 처리, Kafka 토픽(raw.rfid.events, raw.anpr.events), PDPA 준수"),
        ("mlff-session-matching", "MLFF Entry-Exit 매칭",
         "진입/진출 페어링 알고리즘, Redis TTL 세션, 타임아웃 처리, ANPR 재시도, 수동 심사 큐"),
        ("clearing-center-operations", "정산 센터 운영",
         "Clearing Center 역할, 일별/월별 집계, JVC 수수료 차감, 대사(Reconciliation), 차액 조정"),
        ("payment-failure-scenarios", "결제 실패 시나리오",
         "Tier 1~4 미납 처리 흐름, 재시도 정책, JPJ 도로세 차단, Write-off 기준"),
        # Round 2
        ("jpj-integration", "JPJ 연동",
         "차량 등록 조회 API, 도로세 차단 API, OAuth 2.0, 타임아웃 3초, Exponential Backoff, RM 0.10/조회 비용"),
        ("tng-payment", "TnG 결제 연동",
         "Channel B 배치 정산, TnG API 인증, Reconciliation 프로세스, 장애 시 수동 대사"),
        ("external-api-mcp", "외부 API & MCP 설계",
         "External REST API(TOC용), BOS MCP Server(Paperclip용), 15개 Tool 활용 패턴, 버전 관리"),
        ("data-architecture-standards", "데이터 아키텍처 표준",
         "5단계 집계 구조, Bronze/Silver/Gold, Delta Lake ACID, Airflow DAG 패턴"),
        ("metadata-management", "메타데이터 관리",
         "300+ 용어 사전(KO/EN/BM), 코드 값 표준, 데이터 소유자/생명주기/민감도 분류"),
        ("rbac-data-boundary", "RBAC & 데이터 경계",
         "30개 역할, PostgreSQL RLS 패턴, API 레벨 필터링, 콘세셔네어 격리, 감사 로그"),
        # Round 3
        ("aggregation-units", "집계 단위 설계",
         "시간별/일별/월별/분기별 집계, 파티셔닝 전략, 집계 테이블 DDL 패턴"),
        ("text-to-sql-engine", "Text-to-SQL 엔진",
         "Claude Sonnet 프롬프트 설계, 스키마 컨텍스트 주입, SELECT 전용, Dry-run 검증, SLA <10초"),
        ("ai-fault-detection", "AI 장애 탐지",
         "Prometheus 메트릭 기반, Error Rate 임계값, 자동 복구 3단계, DevOps 에스컬레이션"),
        ("rpa-workflows", "RPA 워크플로우",
         "반복 업무 자동화, Agent 트리거, Airflow DAG, 수동 심사 큐 처리"),
        ("ai-decision-policy", "AI 의사결정 정책",
         "Human-in-the-loop 패턴, 이의신청 권고 로직, 면제 승인 기준, 감사 로그 스키마"),
        ("simulation-design", "시뮬레이션 설계",
         "요금 시뮬레이션 모델, 수익 예측 알고리즘, 교통 패턴 분석, 시나리오 설계"),
        # Round 4
        ("bigdata-service-framework", "빅데이터 서비스 프레임워크",
         "Spark 작업 패턴, Airflow DAG 설계, Delta Lake 읽기/쓰기, reporting-service 연동"),
        ("code-quality-standards", "코드 품질 표준",
         "Java 21 체크스타일, React ESLint, SonarQube 설정, 테스트 커버리지 80%+, PR 체크리스트"),
        ("change-management", "변경 관리",
         "G-HARD 게이트 절차, Board 결정 추적, API Breaking Change 정책, 롤백 전략"),
    ]

    tasks = []
    for skill_name, title, description in skill_defs:
        tasks.append(DocTask(
            phase=6,
            output_path=base / skill_name / "SKILL.md",
            title=title,
            expected_lines=300,   # Skills는 짧음 → Haiku
            lead_agent="Knowledge Architect Agent",
            prompt=f"""# {title}
## 07_skills/{skill_name}/SKILL.md
## v1.0 | 2026-04 | Malaysia SLFF/MLFF Tolling BOS

YAML 프론트매터 포함하여 작성:
```yaml
name: {skill_name}
description: {description}
use_when:
  - (3~5개 적용 상황)
dont_use_when:
  - (2~3개 제외 상황)
```

이후 본문 (280~360줄):
1. 개요 — 이 Skills의 핵심 개념
2. 핵심 내용 — 구체적 절차, 규칙, 코드 예시
3. 예시 시나리오 (2~3개)
4. 주의사항 & 함정
5. 관련 Skills & 참조 문서

주제: {description}
한국어 작성, 기술 용어는 영어 혼용.
""",
        ))

    return tasks


# ---------------------------------------------------------------------------
# 메인 실행
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="BOS 문서 생성 (Cost-Aware)")
    parser.add_argument("--phase", type=int, required=True, choices=[4, 5, 6],
                        help="생성할 Phase (4=04_dev, 5=06_phases, 6=07_skills)")
    parser.add_argument("--budget", type=float, default=5.0,
                        help="예산 한도 USD (기본 $5.00)")
    parser.add_argument("--dry-run", action="store_true",
                        help="실제 API 호출 없이 모델 라우팅만 확인")
    parser.add_argument("--force-model", choices=[MODEL_HAIKU, MODEL_SONNET],
                        help="모델 강제 지정 (라우팅 무시)")
    parser.add_argument("--only", type=str, default=None,
                        help="특정 파일만 생성 (파일명 일부 포함 시 매칭)")
    args = parser.parse_args()

    # API 키 확인
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key and not args.dry_run:
        print("❌ ANTHROPIC_API_KEY 환경변수가 설정되지 않았습니다.")
        print("   set ANTHROPIC_API_KEY=sk-ant-...")
        sys.exit(1)

    # 클라이언트 초기화
    client = anthropic.Anthropic(api_key=api_key) if api_key else None

    # 태스크 로드
    phase_loaders = {4: phase4_tasks, 5: phase5_tasks, 6: phase6_tasks}
    tasks = phase_loaders[args.phase]()

    # --only 필터
    if args.only:
        tasks = [t for t in tasks if args.only.lower() in str(t.output_path).lower()]
        if not tasks:
            print(f"❌ --only '{args.only}'에 매칭되는 태스크 없음")
            sys.exit(1)

    # 컨텍스트 로드 (캐싱용)
    context = load_context()

    # 실행 계획 출력
    print(f"\n{'='*60}")
    print(f"  BOS Documentation Generator - Phase {args.phase}")
    print(f"  태스크 수: {len(tasks)}개")
    print(f"  예산 한도: ${args.budget:.2f}")
    print(f"  Dry-run: {args.dry_run}")
    print(f"{'='*60}")

    for t in tasks:
        model = select_model(t, args.force_model)
        status = "✅ 존재" if t.output_path.exists() else "⏳ 생성 예정"
        print(f"  {status} [{model.split('-')[1].upper():6}] {t.output_path.relative_to(BASE_DIR)}")

    print(f"{'='*60}\n")

    if args.dry_run:
        print("Dry-run 완료. 실제 생성하려면 --dry-run 제거 후 실행하세요.")
        return

    # 실행
    tracker = CostTracker(budget_limit=args.budget)
    success_count = 0

    for task in tasks:
        ok, tracker = generate_doc(
            client=client,
            task=task,
            context=context,
            tracker=tracker,
            force_model=args.force_model,
            dry_run=args.dry_run,
        )
        if ok:
            success_count += 1
        if tracker.over_budget:
            print(f"\n⚠ 예산 초과! 중단합니다.")
            break

    # 최종 요약
    print(f"\n{'='*60}")
    print(f"  완료: {success_count}/{len(tasks)}개")
    print(tracker.summary())
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
