# 18개 보완 항목 — Agent 담당 배정 & 처리 계획
## 05_governance/04_supplement_items.md
## v1.0 | 2026-04 | 참조: 00_MASTER.md, 04_dev/02_paperclip_org.md

---
> **Agent 사용 지침**
> PM·CEO Agent가 보완 항목 진행 상황 점검 시 로드.
> 각 항목 담당 Agent가 작업 착수 시 해당 섹션 참조.
> Board는 02_board_decisions.md와 함께 읽을 것.

---

## 전체 현황 요약

```
총 18개 보완 항목
  기존 조직 처리 가능: 16개 (89%)
  Board 직접 결정 필요: 1개 (법적 계약 구조)
  외부 전문가 필수: 1개 (법무법인)

처리 시점별 분류:
  Week 1~2 즉시: 4개
  G-HARD 1 전:   3개
  G-HARD 3 전:   4개
  Phase 진행 중: 4개
  Phase 8 후:    3개
```

---

## 영역 1: 즉시 착수 (Week 1~2)

### [필수-1] 수주·영업 전략

```
담당 Agent: CEO (총괄) + CIO (분석)
처리 방법:
  CIO → 6개 컨소시엄 공개 정보 분석
       → 타겟 콘세셔네어 우선순위 매트릭스 작성
       → 말레이시아 시장 진입 전략 초안
  CEO → Board에 G-HARD 0 전략 보고서 제출
       → 1순위 콘세셔네어 Board 결정 요청

산출물: 콘세셔네어 우선순위 보고서
계획 반영: G-HARD 0 헌장 승인 내용 포함
Board 필요: 1순위 콘세셔네어 선정 결정

한계(Agent 불가):
  실제 현지 담당자 접촉·미팅·계약 협상
  → Board(사람)가 직접 수행, Agent는 자료 지원
```

### [필수-2] Mock 테스트 환경

```
담당 Agent: DevOps (주관) + Comm App Lead + Integration
처리 방법:
  DevOps: Mock 인프라 설계 (Docker Compose 기반)
  Comm: RFID/ANPR 이벤트 시뮬레이터 구현
  Integration: JPJ·TnG·FPX API Mock 서버 구현

구현 대상:
  ① JPJ API Mock (Wiremock)
     차량 조회 응답, 번호판 클론 시나리오, 오류 케이스

  ② TnG API Mock
     정산 요청 성공/실패, 타임아웃, BL 케이스

  ③ RFID 이벤트 시뮬레이터
     SLFF 단건, MLFF Entry/Exit 쌍, 오류 이벤트
     10,000 TPS 부하 생성기 포함

  ④ ANPR 이벤트 시뮬레이터
     번호판 인식 성공/실패, 신뢰도 변동

GSD 실행:
  /gsd:quick "테스트 환경 Mock 서버 전체 구축"
활성화 시점: Phase 1 착수와 동시 (Week 1)
산출물: Mock 서버 Docker Compose + README
계획 반영: Phase 1 구현 태스크 포함
```

### [필수-3] 수수료 구조 & BEP 분석

```
담당 Agent: CIO (주관) + Innovation Planner
처리 방법:
  Innovation Planner: 수수료 시나리오 3종 분석

  시나리오 A: 통행료 %별 수익
    - 3%·5%·8%·12% 각각
    - PLUS 일일 180만 건 × 평균 RM 2.5 기준
    - 월 추산 수익: 3% → ~RM 4M, 12% → ~RM 16M

  시나리오 B: 처리 건당 정액
    - 건당 RM 0.05·0.10·0.15

  BEP 분석:
    투자 비용 = 개발비(Agent $720×12) + 인프라 + 법무
    회수 기간 = 투자 비용 ÷ 월 수수료 수입

산출물: 수수료 구조 분석 보고서 (시나리오별 BEP 표)
계획 반영: G-HARD 0 헌장 포함
Board 필요: 협상 하한선 결정
```

### [필수-4] 법적 계약 구조

```
담당 Agent: Compliance (주관) + CEO
처리 방법 (Agent 가능 범위):
  ① 말레이시아 회사법 요건 조사 (공개 정보)
  ② JVC 설립 일반 요건 문서화
  ③ 콘세셔네어 계약 필수 조항 체크리스트
  ④ IP 귀속 조항 옵션 정리
  ⑤ TnG 서비스 계약 필수 조항 분석

★ Agent 불가 — Board 직접 수행:
  말레이시아 현지 법무법인 선임 (Week 2 내 필수)
  이유: 실제 법적 구속력 있는 계약서 검토 불가
  Compliance가 요건 초안 → 법무법인에 검토 의뢰
  → 검토 결과를 다시 Compliance가 문서화

산출물: 계약 요건 체크리스트, 법무법인 브리핑 자료
계획 반영: G-HARD 0 Board 결정 포함
Board 필요: 법무법인 선임 즉시 결정
```

---

## 영역 2: G-HARD 1 전 완료 (M1 2~3주)

### [중요-1] 결제 실패 시나리오 정의

```
담당 Agent: Transaction Engine (주관) + Billing + Integration
처리 방법:
  전체 결제 실패 유형별 처리 흐름 정의:

  Channel A 실패:
    잔액 부족 → 즉시 미납 Tier 1 진입 + 통지
    계정 미등록 → JPJ 조회 → 통지서 발행

  Channel B (TnG) 실패:
    잔액 부족 → TNG_UNPAID_CASE 격리 저장
    BL 등재 → 격리 저장 + 알림
    API 타임아웃 → 3회 재시도 → 격리 저장
    TnG 시스템 점검 → 임시 후불 허용 모드
    (임시 후불 전환 권한: Board 결정 필요)

  ANPR 실패:
    OCR 인식 실패 → 수동 심사 큐 이동
    미등록 번호판 → JPJ 조회 → 통지서

산출물: 결제 실패 처리 명세서 (모든 케이스 망라)
계획 반영: G-HARD 1 FRD 포함, Phase 3 구현 기준
Board 필요: TnG 장애 시 후불 전환 권한 기준
```

### [중요-2] AI 결정 책임 귀속 기준

```
담당 Agent: Compliance (주관) + AI Lead
처리 방법:
  AI 자동 결정 3단계 분류:

  Level 1 (완전 자동 허용):
    위반 유형 분류 (V001~V006)
    미납 Tier 분류 (1~4단계)
    이상 거래 1차 플래그
    → 오류 시: 자동 보정 + 감사 로그

  Level 2 (AI 권고 → 담당자 확인):
    정산 이상 탐지
    번호판 클론 의심
    → 오류 시: JVC 담당자 조정

  Level 3 (AI 제안 → 사람 최종 승인):
    JPJ 도로세 차단
    법적 조치 개시
    고액 면제·할인 처리
    → 오류 시: Board 개입 → 즉각 철회

  XAI 기능:
    AI 결정 이유 자동 설명
    "이 차량이 Tier 3인 이유: 90일 이상 미납 3건..."

산출물: AI 결정 책임 정책서
계획 반영: G-HARD 1 FRD + G-HARD 2 프로세스 확정 포함
Board 필요: Level 1 최대 허용 범위 확정
```

### [보완-1] ANPR 이미지 보존·파기 정책

```
담당 Agent: Compliance (주관) + DA Lead + DBA
처리 방법:
  PDPA 기준 보존 정책:
    정상 통행 이미지:       30일 → 자동 파기
    위반 관련 이미지:       위반 종결 후 90일
    법적 분쟁 관련:         분쟁 종결 시까지
    번호판 클론 의심:       조사 완료 후 1년

  DA Lead: 파기 정책 DB 스키마 반영
           (image_retention_policy 테이블)
  DBA: 자동 파기 배치 Job (Spring Batch, 매일 자정)
  Compliance: PDPA 준수 감사 문서

산출물: 개인정보 처리 방침 (ANPR 이미지)
계획 반영: G-HARD 1 NFR + G-HARD 3 기술 규약
```

---

## 영역 3: G-HARD 3 전 완료 (M2 말)

### [중요-3] 재해복구(DR) / BCP

```
담당 Agent: DevOps (주관) + Security & BC + DBA
처리 방법:
  DR 아키텍처:
    Primary: AWS ap-southeast-1 (싱가포르)
    DR Site: AWS ap-southeast-3 (자카르타)
    RPO 목표: < 1시간
    RTO 목표: < 4시간

  DBA: PostgreSQL Streaming Replication 설계
       Redis Sentinel 구성
       Kafka MirrorMaker 2.0 설정
  Security & BC: Hyperledger Fabric 노드 지역 분산
  DevOps: K8s 멀티 리전 Failover 설계

산출물: DR 설계 문서
계획 반영: G-HARD 3 기술 규약 포함, Phase 1 인프라 구현
```

### [중요-4] API 버전 관리 전략

```
담당 Agent: CTO (주관) + Backend Lead + Integration
처리 방법:
  버전 관리 정책:
    URI 방식: /api/v1/, /api/v2/
    하위 호환 유지 기간: 최소 12개월
    Deprecation 공지: 6개월 전 사전 통보
    Breaking Change: Major 버전 업

  외부 API (TnG·JPJ) 변경 모니터링:
    Integration Agent: 주기적 API 스펙 변경 감지
    변경 감지 시: CTO 에스컬레이션 → 영향도 분석

산출물: API 버전 관리 가이드라인
계획 반영: G-HARD 3 기술 규약, Phase 11 External API
```

### [중요-5] 보안 인증 취득 로드맵

```
담당 Agent: Security & BC (주관) + Compliance
처리 방법:
  말레이시아 정부 납품 인증 요건 조사:
    ISO 27001: 정보보안 관리 (가능성 높음)
    PCI-DSS:   TnG·FPX 결제 연동 시 필요
    ISMS-P:    말레이시아 버전 요건 조사
    LLM 자체 보안 요건: 고속도로청 규격

  GAP 분석: 현 설계 vs 각 인증 요건
  인증 취득 일정: 납품 전 6개월 착수 권장

산출물: 보안 인증 GAP 분석 + 취득 로드맵
계획 반영: G-HARD 3 기술 규약, Phase 11 보안 강화
Board 필요: 인증 종류·시점·예산 결정
```

### [선택-1] 오픈소스 라이선스 관리

```
담당 Agent: Security & BC (주관) + DevOps
처리 방법:
  라이선스 인벤토리:
    MIT:        Paperclip, GSD → 상업 사용 자유
    Apache 2.0: Spring Boot, Kafka → 상업 사용 가능
    GPL:        사용 여부 전수 확인 필요

  자동화:
    GitHub Actions에 FOSSA 또는 License Checker 추가
    신규 의존성 추가 시 자동 라이선스 검사

산출물: 오픈소스 라이선스 정책서
계획 반영: Phase 1 CI/CD 파이프라인 구축 시 포함
```

---

## 영역 4: Phase 진행 중 (M3~M10)

### [중요-6] 데이터 마이그레이션 전략

```
담당 Agent: DA Lead (주관) + DBA + DevOps
처리 방법:
  DA Lead: 레거시 → 신규 스키마 매핑 룰 설계
           무중단 마이그레이션 전략 (Blue-Green)
  DBA: 마이그레이션 스크립트 (Liquibase)
       롤백 스크립트 필수 포함
       사전·사후 검증 쿼리 세트
  DevOps: 마이그레이션 자동화 파이프라인
          실패 시 자동 롤백

산출물: 마이그레이션 실행 계획서
계획 반영: Phase 12 운영 이관 섹션
활성화 시점: Phase 10 시작 시 착수
```

### [보완-2] Paperclip Agent 간 충돌 방지

```
담당 Agent: PM (주관) + CEO
처리 방법:
  충돌 방지 운영 규칙:
    동일 모듈 작업: Backend Lead가 태스크 분배
                   Paperclip Atomic Checkout 활용
    설계 충돌: CTO 최종 결정권
    우선순위 충돌: PM 조정 → 해결 불가 시 CEO
    예산 소진 충돌: CEO → Board 에스컬레이션

  GSD 활용:
    /gsd:pause-work: 충돌 발생 시 작업 중단
    /gsd:forensics:  충돌 원인 분석

산출물: Paperclip 운영 규칙서
        → Skills 파일 등록: paperclip-operation-rules.md
계획 반영: Phase 1 착수 전 Skills 파일로 등록
```

### [보완-3] AI Agent 코드 품질 기준

```
담당 Agent: CTO (주관) + QA Lead
처리 방법:
  AI 생성 코드 품질 기준:
    단위 테스트 커버리지: 80% 이상
    Cyclomatic Complexity: ≤ 10
    정적 분석: SonarQube (GitHub Actions 연동)
    보안 취약점: SAST 자동 스캔
    하드코딩 탐지: 환경변수 강제 사용

  QA Lead: Phase별 품질 지표 리포트 자동 생성
  Backend Lead: 주간 코드 품질 지표 CEO 보고

산출물: 코드 품질 기준서
        → Skills 파일: code-quality-standards.md
계획 반영: Phase 1 CI/CD 구축 시 즉시 적용
```

### [보완-4] 변경 관리 프로세스

```
담당 Agent: PM (주관) + CTO + CEO
처리 방법:
  변경 유형별 처리:
    소규모 (1 태스크 내): PM 자체 처리
    중규모 (Phase 내):    CTO 승인
    대규모 (Phase 계획):  G-HARD 재수행
    긴급:                 CEO → Board 긴급 보고

  영향도 분석:
    /gsd:quick "변경 영향도 분석: {변경 내용}"

산출물: 변경 관리 절차서
        → Skills 파일: change-management.md
계획 반영: 운영 즉시 적용 (1단계 착수 시)
```

---

## 영역 5: Phase 8 이후 (Innovation Division 활성화)

### [중요-7] 고객 지원 체계

```
담당 Agent: CPO (주관) + PM + Compliance
처리 방법:
  대상별 지원 채널:
    TOC·Plaza 운영자: 전용 운영자 포털 + 이메일
    개인 이용자:      셀프서비스 포털 + AI 챗봇
    장비 기술 이슈:   현장 모바일 앱 직접 접수

  SLA 정의:
    Critical (시스템 장애):     1시간 내 응답
    High (오결제·위반 이의):    4시간 내 응답
    Normal (일반 문의):         24시간 내 응답

  PM: Jira MCP 연동 헬프데스크 워크플로
  Compliance: PDPA 관련 민원 처리 절차

산출물: 고객 지원 운영 매뉴얼
계획 반영: Phase 12 문서화 포함
```

### [보완-5] Paperclip 개발 완료 후 운영팀 전환

```
담당 Agent: CEO + PM + CPO
처리 방법:
  JVC 실운영 전환 계획:
    AI Agent 유지보수 담당 엔지니어 채용 계획
    말레이시아 현지 운영팀 구성 방안
    Agent 모델 업그레이드 체계
    온콜 운영 체계 (24×7)

  CPO: 콘세셔네어 온보딩 절차 표준화
  PM: 인수인계 체크리스트 작성

산출물: 운영 전환 계획서
계획 반영: Phase 12 운영 이관 섹션
활성화 시점: Phase 10 시작 시 착수
```

### [중요-8] 혁신 서비스 수익화 모델

```
담당 Agent: CIO (주관) + Innovation Planner + BigData SvcDesigner
처리 방법:
  서비스별 수익 모델:

  요금 시뮬레이션 서비스:
    무료 (BOS 계약 번들) or
    유료: RM 5,000~20,000/분석 건 or
    구독: RM 50,000~100,000/년

  빅데이터 분석 서비스:
    내부 운영 최적화: 무료
    외부 데이터 판매 (물류사·보험사·도시계획):
      건당 API 과금 or 월정액 구독

  교통 데이터 API:
    Waze·Google Maps 파트너십 모델 검토

산출물: 혁신 서비스 수익 모델 보고서
계획 반영: G-HARD 7 사업화 승인
Board 필요: 외부 데이터 판매 허용 범위·가격 정책
```

---

## 전체 타임라인 요약

| 시점 | 항목 수 | 담당 |
|---|---|---|
| Week 1~2 즉시 | 4개 | CEO·CIO·DevOps·Compliance |
| G-HARD 1 전 (M1 3주) | 3개 | TXN·Billing·Compliance·AI Lead |
| G-HARD 3 전 (M2 말) | 4개 | DevOps·CTO·Security·DA Lead |
| Phase 진행 중 (M3~M10) | 4개 | DA·PM·CTO·QA Lead |
| Phase 8 후 | 3개 | CPO·CEO·CIO |
| **합계** | **18개** | |
