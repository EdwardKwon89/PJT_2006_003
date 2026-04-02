# 비용 모델 & 최적화
## 04_dev/06_budget_model.md
## v1.0 | 2026-04 | 참조: 04_dev/02_paperclip_org.md, 02_system/04_ai_features.md

---

> **Agent 사용 지침**
> CFO Agent가 월간 AI 비용 검토 또는 예산 초과 경고 시 로드.
> 모델 선택 결정 전 이 문서의 라우팅 전략 참조.

---

## 목차

1. [Executive Summary](#1-executive-summary)
2. [Claude API 가격 모델](#2-claude-api-가격-모델)
3. [현재 구독형 플랜 비용 구조](#3-현재-구독형-플랜-비용-구조)
4. [Paperclip 29-Agent 운영 비용 시나리오](#4-paperclip-29-agent-운영-비용-시나리오)
5. [모델 선택 전략](#5-모델-선택-전략)
6. [비용 최적화 기법](#6-비용-최적화-기법)
7. [예산 알림 & 초과 대응 절차](#7-예산-알림--초과-대응-절차)
8. [ROI 분석](#8-roi-분석)
9. [참조 문서](#9-참조-문서)

---

## 1. Executive Summary

Malaysia SLFF/MLFF Tolling BOS는 **Claude Code 구독형 플랜**(OAuth 인증, 토큰 단위 과금 없음)을 기본으로 운영하며, 대규모 트래픽 발생 시 API 종량제 전환 기준을 명확히 정의한다. 29개 Paperclip Agent의 모델 라우팅 최적화를 통해 동등한 품질을 유지하면서 API 전환 시 비용을 최대 **62% 절감**할 수 있다.

### 1.1 비용 구조 전체 현황

| 항목 | 모델 | 월간 예상 사용량 (API 기준) | 비고 |
|------|------|----------------------------|------|
| **[현재] Claude Code 구독** | — | 정액 | OAuth 인증, 토큰 무제한 |
| Text-to-SQL | Sonnet 4.6 | ~500K input / ~50K output tokens | 쿼리당 평균 1,000 tokens |
| 업무 판단 AI (이의신청·면제) | Sonnet 4.6 | ~200K input / ~30K output tokens | 건당 평균 1,500 tokens |
| 스마트 커스터마이징 | Haiku 4.5 | ~2M input / ~300K output tokens | 요청당 평균 200 tokens |
| AI 장애 탐지·자동 복구 | Rule-based + Sonnet | ~100K input / ~20K output tokens | 장애 발생 시에만 호출 |
| Layer 3 Analytics AI (Phase 8/9) | Sonnet 4.6 | ~300K input / ~60K output tokens | 배치 분석 중심 |
| **Paperclip 29-Agent 운영** | Sonnet 4.6 (기본) | ~10M input / ~2M output tokens | 문서 생성·분석 포함 |
| **프롬프트 캐싱 절감** | — | 캐시 읽기 70% 적용 시 | 공통 컨텍스트 재사용 |

### 1.2 핵심 지침

```
┌──────────────────────────────────────────────────────────────┐
│               비용 관리 핵심 원칙 (BOS)                       │
├──────────────────┬───────────────────────────────────────────┤
│ 고빈도·저복잡도  │ Haiku 4.5 → 스마트 커스터마이징, Skills   │
│                  │ 파일 생성, 간단한 분류·요약               │
├──────────────────┼───────────────────────────────────────────┤
│ 저빈도·고복잡도  │ Sonnet 4.6 → 아키텍처 결정, 복잡한 분석  │
│                  │ 문서 생성, Text-to-SQL, 업무 판단         │
├──────────────────┼───────────────────────────────────────────┤
│ 전략적 의사결정  │ Opus 4.5 → 최소화. G-HARD 게이트 검토    │
│                  │ 월 2회 이내 사용 원칙                     │
├──────────────────┼───────────────────────────────────────────┤
│ 캐싱 우선        │ 공통 컨텍스트(시스템 프롬프트, 스키마)는  │
│                  │ ephemeral 캐시 필수 적용                  │
└──────────────────┴───────────────────────────────────────────┘
```

---

## 2. Claude API 가격 모델

> **참고:** 현재 Claude Code 구독형 플랜을 사용 중이므로 이 섹션은 **API 종량제 전환 시 참고용**이다. 트래픽 임계값 초과 또는 구독 외 서비스 연동 시 적용.

### 2.1 모델별 공식 가격표

| 모델 | Input (per 1M tokens) | Output (per 1M tokens) | 특성 |
|------|-----------------------|------------------------|------|
| **claude-haiku-4-5** | $0.80 | $4.00 | 최저 비용, 빠른 응답 (~1초) |
| **claude-sonnet-4-6** | $3.00 | $15.00 | 균형형, 최우선 개발 모델 |
| **claude-opus-4-5** | $15.00 | $75.00 | 최고 성능, 최고 비용 |

### 2.2 프롬프트 캐싱 가격 (Sonnet 4.6 기준)

| 캐싱 유형 | 배율 | 실제 단가 (Input 기준) | 설명 |
|-----------|------|-----------------------|------|
| 캐시 없음 (기본) | 1.0× | $3.00 / 1M | 매 요청마다 전체 토큰 과금 |
| 캐시 쓰기 (Write) | 1.25× | $3.75 / 1M | 첫 번째 요청 시 캐시 생성 비용 |
| 캐시 읽기 (Read) | 0.1× | $0.30 / 1M | 캐시 히트 시 90% 절감 |

### 2.3 캐싱 손익분기점 계산

```
캐시 비용이 이익이 되는 조건:
  캐시 쓰기 비용 < (캐시 없는 비용 - 캐시 읽기 비용) × 반복 횟수

공식:
  BEP = 1.25 / (1.0 - 0.1) = 1.39 회

  → 같은 컨텍스트를 2회 이상 재사용하면 캐싱이 항상 유리

BOS 적용 케이스:
  시스템 프롬프트 (5,000 tokens) × 1,000 요청/일:
  - 캐싱 없음:  5,000 × 1,000 × $3.00/1M = $15.00/일
  - 캐싱 적용:  쓰기 1회 + 읽기 999회
                = (5,000 × $3.75 + 5,000 × 999 × $0.30) / 1M
                = ($18.75 + $1,498.50) / 1M
                = $0.0015/일 → 99.99% 절감
```

### 2.4 Context Window 스펙

| 모델 | Context Window | Max Output | 비고 |
|------|----------------|------------|------|
| claude-haiku-4-5 | 200K tokens | 8,192 tokens | 대부분 작업 충분 |
| claude-sonnet-4-6 | 200K tokens | 64,000 tokens | 대규모 문서 생성 적합 |
| claude-opus-4-5 | 200K tokens | 32,000 tokens | 전략적 분석용 |

---

## 3. 현재 구독형 플랜 비용 구조

### 3.1 Claude Code Max 플랜 특징

| 구분 | 내용 |
|------|------|
| **인증 방식** | OAuth (계정 기반, API Key 불필요) |
| **과금 방식** | 정액 구독 (토큰 단위 과금 없음) |
| **사용 범위** | Claude Code CLI + Agentic 워크플로우 |
| **Rate Limit** | 시간당 요청 수 제한 (모델별 상이) |
| **장점** | 비용 예측 가능, 개발 단계 비용 최소화 |
| **한계** | Rate Limit 도달 시 대기 필요, 대규모 배치 부적합 |

### 3.2 Rate Limit 관리 전략

```
Rate Limit 발생 시 대응 순서:

1. 즉시 대응 (0~5분)
   ├── 현재 실행 중인 Agent 작업 일시 중단
   ├── 진행 상황 STATE.md에 저장
   └── Rate Limit 해제 시각 확인 (보통 ~1시간 후)

2. 단기 최적화 (5~60분 대기 중)
   ├── 배치 가능한 작업은 Queue에 적재
   ├── Rate Limit 영향 없는 Rule-based 작업 계속
   └── Haiku 모델로 전환 가능한 작업 식별

3. 재개 시 (Rate Limit 해제 후)
   ├── Queue 작업 우선순위 재정렬
   ├── 병렬 실행 가능 범위 재확인
   └── STATE.md 갱신 후 재개
```

### 3.3 구독형 → API 종량제 전환 기준

아래 조건 중 하나라도 해당하면 CFO Agent가 전환 검토 보고서를 작성한다.

| 전환 검토 기준 | 임계값 | 측정 주기 |
|----------------|--------|-----------|
| Rate Limit 도달 빈도 | 주 5회 이상 | 주간 |
| 대기 누적 시간 | 월 10시간 이상 | 월간 |
| 배치 작업 지연 | SLA 초과 3회 이상 | 월간 |
| 동시 Agent 수 | 29개 초과 예정 | 프로젝트 계획 시 |
| Phase 진입 (자동) | Phase 8 (운영 단계) 진입 시 | Phase 전환 시 |

---

## 4. Paperclip 29-Agent 운영 비용 시나리오

> 이 섹션은 API 종량제 전환 시 예상 비용을 산출한다.  
> 현재 구독형 플랜 사용 시에는 참고용으로 활용.

### 4.1 Agent별 일평균 호출 수 추정

| Agent 그룹 | 대표 Agent | 모델 | 일평균 호출 수 | 호출당 평균 토큰 (input/output) |
|------------|-----------|------|---------------|-------------------------------|
| **경영진** | CEO, CFO, CTO, COO | Sonnet 4.6 | 10~20회 | 3,000 / 500 |
| **도메인 리드** | tolling-lead, payment-lead 등 6개 | Sonnet 4.6 | 20~40회 | 2,000 / 400 |
| **운영 분석** | reporting-lead, data-analyst 등 | Sonnet 4.6 | 30~60회 | 2,500 / 600 |
| **개발 팀** | dev-lead, backend-dev 등 5개 | Sonnet 4.6 | 50~100회 | 4,000 / 800 |
| **품질·보안** | qa-lead, security-lead 등 4개 | Sonnet 4.6 | 20~40회 | 3,000 / 500 |
| **지원·운영** | it-ops, helpdesk 등 | Sonnet 4.6 | 40~80회 | 1,500 / 300 |
| **문서·커뮤니케이션** | doc-writer, translator 등 | Haiku 4.5 | 30~60회 | 5,000 / 2,000 |
| **AI 기능 직접 호출** | Text-to-SQL, 업무판단 | Sonnet 4.6 | 200~500회 | 1,200 / 300 |
| **스마트 커스터마이징** | UI 개인화 | Haiku 4.5 | 500~2,000회 | 300 / 100 |

### 4.2 Phase별 예상 총 비용 (API 종량제 기준)

| Phase | 기간 | 주요 활동 | Sonnet 비용/월 | Haiku 비용/월 | Opus 비용/월 | **총 비용/월** |
|-------|------|-----------|----------------|----------------|--------------|----------------|
| Phase 1~2 | 2025 Q4 | 기반 구조 구축, 문서 생성 | $45 | $8 | $5 | **~$58** |
| Phase 3~4 | 2026 Q1 | SLFF/MLFF 핵심 개발 | $120 | $20 | $8 | **~$148** |
| Phase 5~6 | 2026 Q2 | AI 기능 개발, 통합 테스트 | $200 | $35 | $10 | **~$245** |
| Phase 7 | 2026 Q3 | UAT, 성능 최적화 | $150 | $25 | $5 | **~$180** |
| Phase 8~9 | 2026 Q4+ | 운영 단계, Analytics AI | $350 | $60 | $15 | **~$425** |

> **주의:** 위 금액은 추정치이며, 실제 사용량에 따라 ±30% 변동 가능.  
> Phase 8 이후 운영 트래픽 증가 시 구독형 플랜 → API 종량제 전환 검토 필수.

### 4.3 모델 라우팅 시 절감 효과

전체 Agent를 Sonnet 4.6으로만 운용할 경우 대비, 최적 라우팅 적용 시:

| 시나리오 | Sonnet 비율 | Haiku 비율 | Opus 비율 | 월 비용 (Phase 5 기준) | 절감률 |
|---------|-------------|------------|-----------|----------------------|--------|
| 전체 Sonnet | 100% | 0% | 0% | ~$520 | 기준 |
| 최소 최적화 | 70% | 30% | 0% | ~$340 | 35% 절감 |
| **권장 최적화** | **55%** | **43%** | **2%** | **~$245** | **53% 절감** |
| 공격적 최적화 | 40% | 58% | 2% | ~$200 | 62% 절감 |

---

## 5. 모델 선택 전략

### 5.1 의사결정 트리

```
새 AI 작업 요청 시:

                  ┌─────────────────────────────────┐
                  │    작업 복잡도 평가               │
                  └─────────────┬───────────────────┘
                                │
          ┌─────────────────────┼─────────────────────┐
          │                     │                     │
          ▼                     ▼                     ▼
   [단순 / 반복]         [중간 복잡도]          [전략적 / 고복잡도]
          │                     │                     │
          ▼                     ▼                     ▼
   호출 빈도 확인        Sonnet 4.6 사용        Opus 4.5 사용
          │             (기본값)               (CFO 사전 승인 필요)
    ┌─────┴─────┐
    │           │
    ▼           ▼
 고빈도       저빈도
 (>50회/일) (<50회/일)
    │           │
    ▼           ▼
Haiku 4.5   Sonnet 4.6
```

### 5.2 Haiku 4.5 적용 대상

빈도가 높고 복잡도가 낮은 작업에 우선 적용:

| 작업 유형 | 예시 | 이유 |
|-----------|------|------|
| **Skills 파일 생성** | 단순 문서 템플릿 작성 | 반복적, 낮은 추론 필요 |
| **스마트 커스터마이징** | UI 개인화 추천 | 고빈도 (사용자별 요청) |
| **간단한 분류** | 민원 카테고리 분류 | 분류 기준 명확 |
| **코드 요약** | 함수 설명 자동 생성 | 반복 패턴 |
| **번역 (BM/EN/KO)** | 공지사항 다국어 변환 | 도메인 어휘 고정 |
| **로그 파싱** | 에러 로그 구조화 | Rule 기반 가능 |
| **FAQ 응답** | 헬프데스크 1차 응답 | 답변 DB 기반 |

### 5.3 Sonnet 4.6 적용 대상

품질과 비용의 균형이 필요한 핵심 작업:

| 작업 유형 | 예시 | 이유 |
|-----------|------|------|
| **Text-to-SQL** | 자연어 → 복잡한 JOIN 쿼리 | SQL 정확도 중요 |
| **업무 판단 AI** | 이의신청 초안 작성 | 법적 정확성 필요 |
| **아키텍처 결정** | 서비스 분리 방안 도출 | 다각도 분석 필요 |
| **복잡한 문서 생성** | 시스템 설계서, 기술 문서 | 긴 구조적 출력 필요 |
| **코드 리뷰** | PR 검토, 보안 취약점 분석 | 정밀도 필요 |
| **데이터 분석** | 수익 패턴 분석, 이상 탐지 | 복잡한 추론 필요 |
| **통합 테스트 설계** | E2E 시나리오 작성 | 시스템 전체 이해 필요 |

### 5.4 Opus 4.5 적용 대상 (최소화 원칙)

비용이 높으므로 전략적·고부가가치 작업에만 사용:

| 작업 유형 | 예시 | 승인 요건 |
|-----------|------|-----------|
| **G-HARD 게이트 검토** | Phase 전환 Go/No-Go 분석 | CFO 사전 승인 |
| **Board 의사결정 지원** | 21개 Board 결정 초안 분석 | CTO + CFO 승인 |
| **보안 취약점 심층 분석** | Critical 보안 감사 | Security Lead 요청 |
| **계약 구조 분석** | JVC 파트너 계약 검토 | CEO 요청 |

> **월 사용 제한:** Opus 4.5는 월 **10회 이내** 사용 원칙. 초과 시 CFO Agent에 자동 알림.

---

## 6. 비용 최적화 기법

### 6.1 프롬프트 캐싱 적용 패턴

공통 컨텍스트(시스템 프롬프트, 스키마, 규정 문서)를 ephemeral 캐시로 유지하여 토큰 비용을 최소화한다.

**Python SDK 코드 예시 (API 종량제 전환 후 적용):**

```python
import anthropic

client = anthropic.Anthropic()

# BOS 공통 시스템 컨텍스트 (캐시 대상)
BOS_SYSTEM_CONTEXT = """
당신은 Malaysia SLFF/MLFF Tolling BOS 시스템의 AI 어시스턴트입니다.
[... 5,000 tokens 수준의 공통 컨텍스트 ...]
"""

# 데이터베이스 스키마 컨텍스트 (캐시 대상)
DB_SCHEMA_CONTEXT = """
-- transactions 테이블
CREATE TABLE transactions (
    id BIGSERIAL PRIMARY KEY,
    toll_plaza_id INTEGER NOT NULL,
    vehicle_class VARCHAR(10) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    channel VARCHAR(20) NOT NULL,  -- 'A' or 'B'
    created_at TIMESTAMPTZ NOT NULL
);
[... 4,000 tokens 수준의 스키마 정의 ...]
"""

def query_with_caching(user_query: str) -> str:
    """
    프롬프트 캐싱을 적용한 Text-to-SQL 쿼리 실행.
    시스템 컨텍스트와 스키마는 캐시에서 읽어 비용 절감.
    """
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=[
            {
                "type": "text",
                "text": BOS_SYSTEM_CONTEXT,
                "cache_control": {"type": "ephemeral"}  # 캐시 대상 마킹
            },
            {
                "type": "text",
                "text": DB_SCHEMA_CONTEXT,
                "cache_control": {"type": "ephemeral"}  # 캐시 대상 마킹
            }
        ],
        messages=[
            {
                "role": "user",
                "content": f"다음 질문에 대한 SQL을 생성해 주세요: {user_query}"
            }
        ]
    )

    # 캐시 사용 현황 로깅 (비용 추적용)
    usage = response.usage
    print(f"[캐시 통계] 입력: {usage.input_tokens}, "
          f"캐시 생성: {usage.cache_creation_input_tokens}, "
          f"캐시 읽기: {usage.cache_read_input_tokens}, "
          f"출력: {usage.output_tokens}")

    return response.content[0].text


def batch_document_generation(topics: list[str]) -> list[str]:
    """
    문서 대량 생성 시 공통 컨텍스트 캐싱 적용.
    첫 번째 요청에서 캐시 쓰기, 이후 요청은 캐시 읽기.
    """
    results = []
    for topic in topics:
        response = client.messages.create(
            model="claude-haiku-4-5",  # 문서 생성은 Haiku 적용
            max_tokens=4096,
            system=[
                {
                    "type": "text",
                    "text": BOS_SYSTEM_CONTEXT,
                    "cache_control": {"type": "ephemeral"}
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": f"다음 주제로 BOS 문서를 작성해 주세요: {topic}"
                }
            ]
        )
        results.append(response.content[0].text)

    return results
```

### 6.2 불필요한 컨텍스트 전달 방지

| 안티패턴 | 문제점 | 개선 방안 |
|---------|--------|----------|
| 전체 DB 스키마 매 요청 전달 | 불필요한 토큰 소비 | 관련 테이블만 동적 선택 후 주입 |
| 이전 대화 전체 포함 | 컨텍스트 창 낭비 | 최근 5~10 메시지만 유지 |
| 대용량 로그 파일 직접 전달 | 토큰 폭증 | 요약 후 전달 또는 청킹 |
| 이미지·첨부파일 불필요 포함 | 멀티모달 비용 발생 | 텍스트 추출 후 전달 |
| 중복 시스템 프롬프트 | 매 요청마다 재과금 | 캐싱 적용 필수 |

**컨텍스트 최적화 원칙:**

```
토큰 절감 우선순위:
  1. 캐싱 적용 (90% 절감 가능)
  2. 관련 컨텍스트만 선택적 주입
  3. 출력 토큰 제한 (max_tokens 명시)
  4. Temperature=0 (재시도 최소화)
  5. 작업 분해 (복잡한 1개 → 단순한 N개)
```

### 6.3 배치 처리 병렬화

순차 실행 대비 병렬 실행 시 시간 비용을 절감한다 (토큰 비용은 동일).

```python
import asyncio
import anthropic

async def parallel_agent_execution(tasks: list[dict]) -> list[str]:
    """
    29개 Agent의 독립적 작업을 병렬로 실행.
    순차 실행 대비 최대 N배 처리 속도 향상 (N = 병렬 작업 수).
    Rate Limit 고려: 동시 요청 수 제한 필요.
    """
    client = anthropic.AsyncAnthropic()
    semaphore = asyncio.Semaphore(5)  # 동시 최대 5개 요청 (Rate Limit 방지)

    async def execute_single(task: dict) -> str:
        async with semaphore:
            response = await client.messages.create(
                model=task.get("model", "claude-sonnet-4-6"),
                max_tokens=task.get("max_tokens", 2048),
                messages=[{"role": "user", "content": task["prompt"]}]
            )
            return response.content[0].text

    results = await asyncio.gather(*[execute_single(t) for t in tasks])
    return list(results)


# 사용 예시: Wave 3 문서 병렬 생성
wave3_tasks = [
    {"model": "claude-haiku-4-5", "prompt": "03_data/01_data_architecture.md 초안 작성"},
    {"model": "claude-haiku-4-5", "prompt": "03_data/02_data_model.md 초안 작성"},
    {"model": "claude-sonnet-4-6", "prompt": "03_data/03_rbac_design.md 작성 (보안 중요)"},
    {"model": "claude-haiku-4-5", "prompt": "03_data/04_metadata_glossary.md 초안 작성"},
]

# asyncio.run(parallel_agent_execution(wave3_tasks))
```

### 6.4 모델 Fallback 체인

품질 요구사항에 따라 자동으로 모델을 전환:

```
Fallback 체인 (비용 최소화 방향):

  요청 → Haiku 4.5 시도
           │
           ├── 성공 (품질 기준 충족) → 반환
           │
           └── 실패 (품질 기준 미달) → Sonnet 4.6 재시도
                    │
                    ├── 성공 → 반환 + CFO 로그 기록
                    │
                    └── 실패 → Opus 4.5 최종 시도
                              (CFO Agent 자동 알림)
```

**품질 기준 예시:**
- Text-to-SQL: SQL 문법 유효성 + SELECT 전용 검증 통과
- 분류 작업: 신뢰도 점수 0.85 이상
- 문서 생성: 최소 길이 요건 (100 tokens) 충족

---

## 7. 예산 알림 & 초과 대응 절차

### 7.1 구독형 플랜 모니터링 지표

| 지표 | 정상 범위 | 경고 임계값 | 위험 임계값 |
|------|-----------|-------------|-------------|
| 일간 Rate Limit 도달 횟수 | 0~1회 | 2~4회 | 5회 이상 |
| 평균 대기 시간 (Rate Limit) | 0분 | 5~30분 | 30분 초과 |
| Wave 작업 지연율 | <5% | 5~20% | 20% 초과 |
| 미완료 Queue 항목 수 | <10개 | 10~50개 | 50개 초과 |

### 7.2 API 종량제 전환 후 예산 알림 체계

```
예산 소비 임계값별 알림 & 대응:

  ■ 50% 소비 (정기 보고)
    → CFO Agent: 월간 소비 현황 리포트 생성
    → 이상 패턴 없으면 정상 진행

  ■ 70% 소비 (경고)
    → CFO Agent: CTO에 자동 알림 전송
    → 불필요한 Opus 사용 점검
    → Haiku 전환 가능 작업 목록 생성

  ■ 85% 소비 (긴급)
    → CFO Agent: CEO + CTO에 즉시 알림
    → 신규 Opus 호출 전면 중단
    → 비핵심 Sonnet 작업 → Haiku 강제 전환
    → 배치 작업 다음 달로 연기 검토

  ■ 100% 소비 (초과)
    → 자동 긴급 차단: Opus 호출 비활성화
    → CFO Agent: 초과 원인 분석 보고서 작성
    → CEO 승인 하에 추가 예산 편성 또는 기능 제한
```

### 7.3 초과 대응 Runbook

**Step 1: 원인 파악 (0~30분)**

```bash
# 당월 모델별 사용량 조회 (API 종량제 시)
# anthropic.usage.list() 또는 대시보드 확인

# 상위 비용 발생 Agent 식별
SELECT agent_name, model, SUM(tokens_used) as total_tokens
FROM ai_usage_log
WHERE created_at >= date_trunc('month', NOW())
GROUP BY agent_name, model
ORDER BY total_tokens DESC
LIMIT 10;
```

**Step 2: 즉각 조치 (30분~2시간)**

| 조치 | 담당 | 예상 절감 |
|------|------|-----------|
| Opus → Sonnet 강제 전환 | CFO Agent | 80% 절감 |
| Sonnet → Haiku 전환 (저복잡도 작업) | CTO Agent | 74% 절감 |
| 배치 작업 스케줄 변경 (야간 집중) | DevOps Agent | 피크 분산 |
| 캐싱 미적용 엔드포인트 캐싱 활성화 | Backend Dev | 30~90% 절감 |

**Step 3: 사후 관리 (익월 시작 전)**
- CFO Agent: 초과 원인 분석 보고서 → Board 보고
- CTO Agent: 모델 라우팅 규칙 업데이트
- Phase 계획 재검토 (예산 내 범위 조정)

---

## 8. ROI 분석

### 8.1 Paperclip 29-Agent 투입 대비 절감 효과

Agent 도입 전후 비교를 통해 AI 투자 수익률을 산출한다.

| 업무 영역 | Agent 도입 전 (인력 비용/월) | Agent 도입 후 (AI 비용/월) | 절감액/월 | 절감률 |
|-----------|------------------------------|---------------------------|-----------|--------|
| 문서 생성 (67개 문서) | $8,000 (기술 작가 1명) | $150 (Haiku 기반) | $7,850 | 98% |
| 데이터 분석 & 리포팅 | $6,000 (분석가 0.5 FTE) | $200 (Sonnet 기반) | $5,800 | 97% |
| 코드 리뷰 & QA | $10,000 (시니어 개발자 0.5 FTE) | $300 (Sonnet 기반) | $9,700 | 97% |
| 민원·이의신청 처리 | $4,000 (운영 담당 0.5 FTE) | $250 (Sonnet 기반) | $3,750 | 94% |
| 보안 감사 지원 | $5,000 (보안 컨설턴트) | $100 (Sonnet 기반) | $4,900 | 98% |
| **합계** | **$33,000/월** | **$1,000/월** | **$32,000/월** | **97%** |

> **참고:** 인력 비용은 말레이시아 KL 기준 시장 단가 추정치. AI는 인력 대체가 아닌 **증강(Augmentation)** 목적으로 사용.

### 8.2 투자 회수 기간 (Payback Period)

```
초기 투자:
  - Paperclip Agent 설계·구축: 약 $15,000 (개발 공수 기준)
  - 문서·Skills 파일 생성 비용: 약 $500 (Claude Code 구독)
  - 총 초기 투자: ~$15,500

월간 순절감:
  - 인건비 절감: $33,000
  - AI 운영 비용: -$1,000
  - 순절감: $32,000/월

투자 회수 기간 = $15,500 / $32,000 = 0.48개월 (~15일)
```

### 8.3 Phase별 누적 ROI 전망

| Phase | 누적 투자 | 누적 절감 | 누적 순이익 | ROI |
|-------|-----------|-----------|-------------|-----|
| Phase 1~2 (3개월) | $15,500 | $96,000 | $80,500 | 519% |
| Phase 3~4 (6개월) | $16,500 | $192,000 | $175,500 | 1,064% |
| Phase 5~6 (9개월) | $18,000 | $288,000 | $270,000 | 1,500% |
| Phase 7 (12개월) | $19,000 | $384,000 | $365,000 | 1,921% |
| Phase 8~9 (18개월) | $22,000 | $576,000 | $554,000 | 2,518% |

### 8.4 비정량적 효과

| 효과 | 설명 |
|------|------|
| **일관성** | 29개 Agent가 동일한 기준으로 문서 생성 → 품질 편차 제거 |
| **속도** | 문서 생성 시간 10분 → 2분 단축 (80% 개선) |
| **가용성** | 24/7 운영 가능 (인력 의존도 감소) |
| **확장성** | 추가 Agent 배치 시 한계 비용 거의 없음 |
| **추적 가능성** | 모든 AI 결정에 감사 로그 자동 생성 |

---

## 9. 참조 문서

| 문서 | 경로 | 관련 섹션 |
|------|------|-----------|
| Paperclip 29-Agent 조직도 | `04_dev/02_paperclip_org.md` | Agent 역할·책임 정의 |
| AI 기능 설계 | `02_system/04_ai_features.md` | 모델 선택 기준, Fallback 패턴 |
| 데이터 거버넌스 | `05_governance/01_decision_gates.md` | G-HARD 게이트 (Opus 사용 기준) |
| 보안 준수 | `03_data/05_security_compliance.md` | AI 감사 로그 요건 |
| Phase 계획 | `06_phases/` | Phase별 AI 기능 도입 시점 |

### 9.1 외부 참조

| 리소스 | URL | 용도 |
|--------|-----|------|
| Anthropic 공식 가격 | https://www.anthropic.com/pricing | 최신 모델별 단가 확인 |
| Prompt Caching 가이드 | https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching | 캐싱 구현 레퍼런스 |
| Claude Code 구독 정책 | https://claude.ai/code | Rate Limit 정책 확인 |
| Token 사용량 계산기 | https://platform.anthropic.com/settings/usage | 실시간 사용량 모니터링 |

---

*비용 모델은 Anthropic 가격 정책 변경 시 즉시 업데이트. CFO Agent가 분기별 검토 수행.*
