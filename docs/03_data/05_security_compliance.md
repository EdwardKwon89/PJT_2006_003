# 보안 준수 체계 및 데이터 거버넌스

**문서 버전**: 1.0  
**작성일**: 2026-04-01  
**상태**: Draft  
**담당자**: Chief Information Security Officer (CISO), Data Governance Team  
**대상**: HiPass ETCS 기반 SLFF/MLFF 플랫폼

---

## 1. 개인정보보호(PDPA) 준수 체계

### 1.1 규제 환경

| 관할 지역 | 법규 | 적용 범위 | 주요 요구사항 |
|----------|------|---------|------------|
| **말레이시아** | PDPA (2010) | 모든 데이터 처리 | 고객동의, 보안, 투명성 |
| **우즈벡** | Data Privacy Law (개발 중) | 개인정보 처리 | 로컬 데이터 저장 의무 |
| **필리핀** | Data Privacy Act (2012) | 모든 PII 처리 | 등록, 보안, 감시 |
| **브라질** | LGPD (2020) | 개인정보 처리 | 명확한 동의, DPIA 필수 |
| **국제** | ISO/IEC 27001 | 정보보안 관리 | ISMS 인증 대상 |

### 1.2 개인정보 분류 및 처리 기준

```
┌─────────────────────────────────────────────────┐
│          개인정보 분류 체계 (PII Classification) │
└─────────────────────────────────────────────────┘

1. 최고 민감 (Critical PII)
   ├─ 차량번호판(ANPR 이미지 기반)
   ├─ 운전면허번호
   ├─ 신원확인번호(ID number)
   ├─ 금융 계좌정보
   └─ 생체 정보 (향후 추가 가능)

2. 고민감 (Sensitive PII)
   ├─ 이름, 주소
   ├─ 전화번호, 이메일
   ├─ 결제 거래 내역
   ├─ GPS/위치 정보
   └─ 차량 운행 기록

3. 일반 (General PII)
   ├─ 집계 통계
   ├─ 차량 유형, 클래스
   ├─ 통행료 카테고리
   └─ 시간대별 통행 빈도
```

### 1.3 PDPA 준수 정책

| 정책 영역 | 요구사항 | 구현 방법 | 책임자 |
|----------|---------|---------|--------|
| **개인정보 수집** | 명확한 목적 고지, 동의 획득 | 웹 폼 동의, 앱 권한 요청 | Legal, Product |
| **저장 기간** | 필요한 기간만 보유 | 자동 삭제 정책 적용 | Data Ops |
| **데이터 최소화** | 필요한 정보만 수집 | 필드 검증, 선택적 수집 | Engineering |
| **접근 제어** | 최소 권한 원칙(PoLP) | RBAC, ABAC 구현 | Security |
| **암호화** | 전송 및 저장 시 암호화 | TLS 1.3, AES-256-GCM | Infra |
| **감시/감독** | 정기적 감시 및 보고 | 월간 감사 로그 검토 | Audit |
| **개인권리 보장** | 접근권, 수정권, 삭제권 | Self-service 데이터 포탈 | Legal, Eng |

---

## 2. ANPR 이미지 데이터 보존 및 삭제 정책

### 2.1 보존 정책 개요

ANPR(Automatic Number Plate Recognition) 이미지는 차량 식별의 핵심 자산이나 개인정보 침해 위험이 높음.

```
┌──────────────────────────────────────────────────┐
│   ANPR 이미지 생명주기 (Lifecycle Management)    │
└──────────────────────────────────────────────────┘

수집 → 처리 → 저장 → 보관 → 삭제/익명화
(캡처)  (추출)  (활성)  (기간)  (자동/수동)
```

### 2.2 보존 기간 스케줄

| 데이터 유형 | 보존 기간 | 삭제 방식 | 예외 사항 | 규제 근거 |
|-----------|---------|---------|---------|---------|
| **원본 ANPR 이미지** | 7일 | 자동 삭제 | 미납 통행료(60일 연장) | PDPA Sec 70 |
| **차량번호판 추출본** | 30일 | 자동 삭제 | 분쟁/감시(90일) | PDPA, Malaysia ETCS |
| **통행 거래 기록** | 90일 | 아카이브 → 삭제 | 법적 분쟁(3년) | 국제 기준 |
| **결제 거래 로그** | 180일 | 암호화 저장 후 삭제 | 세무/감사(7년) | Malaysia Tax Act |
| **감시/분석 로그** | 30일 | 일일 집계 후 삭제 | 보안 사건(1년) | PDPA Sec 95 |
| **고객 이름, 연락처** | 동의 유효 기간 | 고객 요청 시 즉시 | 미납금(3개월 추가) | PDPA Sec 61 |

### 2.3 자동화된 보존/삭제 기술

```yaml
# 보존 정책 구성 예시
storage:
  ANPR_IMAGES:
    retention_days: 7
    archive_days: 30
    deletion_policy: "automatic_purge"
    encryption_before_delete: true
    audit_trail: "immutable_log"
    
  TRANSACTION_RECORDS:
    retention_days: 90
    archive_location: "cold_storage_s3"
    compression: "gzip"
    retention_rule:
      - condition: "overdue_payment"
        extend_days: 60
      - condition: "legal_hold"
        indefinite: true
    deletion_trigger: "cron_based"
    time_zone: "UTC+8"
```

### 2.4 삭제 확인 및 감사

- **삭제 인증서**: 각 배치 삭제 후 해시값 기록
- **감시 로그**: 삭제 작업 timestamp, user_id, record_count 기록
- **콜드스토리지 아카이빙**: 삭제 전 60일 이상 콜드 스토리지에 백업
- **감사 리포트**: 월간 보존/삭제 현황 보고

---

## 3. 개인정보 마스킹 기준 및 기술

### 3.1 마스킹 전략

개인정보 노출을 최소화하기 위해 데이터 접근 계층별로 다른 마스킹 정책 적용.

```
┌────────────────────────────────────────────┐
│   마스킹 계층 (Data Masking Layers)        │
└────────────────────────────────────────────┘

데이터베이스 계층:
  ├─ 민감 열 암호화 (컬럼 레벨)
  ├─ 토큰화 (Tokenization)
  └─ 난수 대체 (Random Substitution)

애플리케이션 계층:
  ├─ 마스킹 필터 (Masking Filter)
  ├─ 조건부 노출 (Conditional Display)
  └─ 검색어 필터링

사용자 UI 계층:
  ├─ 부분 표시 (Partial Display)
  ├─ 뷰 권한 제어
  └─ 감시 기반 마스킹
```

### 3.2 마스킹 규칙 상세

| 데이터 필드 | 민감도 | 마스킹 방식 | 예시 | 예외 권한 |
|-----------|--------|-----------|------|---------|
| **차량번호판** | Critical | 처음/끝 2글자만 표시 | `AB12***Z` | Admin, 법무 |
| **운전자 이름** | Sensitive | 성(性) + 이름 첫글자 | `김*` | 고객, 관리자 |
| **ID Number** | Critical | 마지막 4자리만 표시 | `XXXXXX1234` | 본인, 법무 |
| **휴대폰번호** | Sensitive | 중간 4자리 마스킹 | `010-****-5678` | 본인, 콜센터 |
| **이메일** | Sensitive | 첫 2자 + 도메인 | `ab****@email.com` | 본인 |
| **GPS 좌표** | Sensitive | 소수점 2자리 | `3.14**, 101.68**` | 기술 팀만 |
| **결제 계좌** | Critical | 마지막 4자리만 | `****3456` | 본인, 재무 |
| **거주지 주소** | Sensitive | 도시 레벨만 표시 | `쿠알라룸푸르, ****` | 본인, 배송팀 |

### 3.3 마스킹 구현 코드 패턴

```python
# 마스킹 유틸리티 예시
class DataMaskingService:
    @staticmethod
    def mask_license_plate(plate: str) -> str:
        """차량번호판 마스킹: AB12ABC -> AB12***C"""
        if len(plate) < 4:
            return "****"
        return f"{plate[:2]}{plate[2:-1].replace(plate[2:-1], '*' * len(plate[2:-1]))}{plate[-1]}"
    
    @staticmethod
    def mask_identity_number(id_num: str) -> str:
        """신원확인번호 마스킹: 6자리-7자리 -> XXXXXX-***1234"""
        return f"{'X' * 6}-{'*' * 3}{id_num[-4:]}"
    
    @staticmethod
    def mask_phone(phone: str) -> str:
        """휴대폰 마스킹: 010-1234-5678 -> 010-****-5678"""
        parts = phone.split('-')
        return f"{parts[0]}-****-{parts[2]}" if len(parts) == 3 else "****"
    
    @staticmethod
    def apply_role_based_masking(data: dict, user_role: str) -> dict:
        """사용자 역할에 따른 조건부 마스킹"""
        if user_role == "ADMIN":
            return data  # 마스킹 안 함
        elif user_role == "CUSTOMER_SERVICE":
            return {k: self.mask_phone(v) if k == "phone" else v for k, v in data.items()}
        else:  # 일반 사용자
            return {k: self._apply_strict_masking(k, v) for k, v in data.items()}
```

---

## 4. Blockchain 기반 감시 및 감사 로그

### 4.1 감사 로그 아키텍처

블록체인 기술을 통해 감사 로그의 변조 불가능성(immutability) 보장.

```
┌──────────────────────────────────────────────────┐
│   감사 로그 흐름 (Audit Log Flow)                 │
└──────────────────────────────────────────────────┘

이벤트 발생
    │
    ├─→ 로그 생성 (JSON)
    │
    ├─→ 해시 계산 (SHA-256)
    │
    ├─→ 타임스탐프 기록 (UTC)
    │
    ├─→ 디지털 서명 (RSA-2048)
    │
    ├─→ Blockchain 기록
    │   ├─ Hyperledger Fabric (Enterprise)
    │   └─ Private Ethereum (옵션)
    │
    ├─→ 분산 검증 (피어 노드)
    │
    └─→ 감시 알림 (실시간)
```

### 4.2 감사 로그 이벤트 타입 및 기록 기준

| 이벤트 카테고리 | 이벤트 유형 | 기록 정보 | 보존 기간 | 알림 조건 |
|--------------|-----------|---------|---------|---------|
| **인증** | Login/Logout | user_id, timestamp, IP, 성공/실패 | 1년 | 실패 3회 이상 |
| **접근** | Data Access | resource_id, user_id, action, 마스킹 여부 | 2년 | 민감 데이터 접근 |
| **수정** | Data Modification | field_name, old_value, new_value, user_id | 3년 | 모든 수정 사항 |
| **삭제** | Data Deletion | deleted_records, reason, user_id, 승인자 | 무제한 | 모든 삭제 사항 |
| **권한 변경** | Role Change | old_role, new_role, user_id, 승인자 | 3년 | 모든 권한 변경 |
| **시스템** | Config Change | 설정항목, 변경값, user_id, 영향도 | 2년 | 보안 관련 설정 |
| **보안** | Security Event | 이벤트 유형, severity, 대응 조치 | 무제한 | 중대 사건 |
| **규정** | Compliance Event | 규정 검사 결과, 불일치 항목, 해결 조치 | 1년 | 불일치 발견 시 |

### 4.3 Blockchain 기반 감사 로그 구현

```json
{
  "audit_log_entry": {
    "id": "AUD-2026-04-001-000001",
    "timestamp": "2026-04-01T10:30:45.123Z",
    "event_type": "data_access",
    "user_id": "USR-12345",
    "user_role": "CUSTOMER_SERVICE",
    "action": "viewed_vehicle_record",
    "resource_id": "VEH-ABC1234",
    "resource_type": "anpr_image",
    "access_method": "web_dashboard",
    "ip_address": "192.168.1.100",
    "status": "success",
    "data_fields_accessed": ["license_plate", "timestamp"],
    "masked_fields": ["license_plate"],
    "decision": "approved",
    "approval_reason": "customer_inquiry",
    "blockchain": {
      "hash": "0xf7a3f8c9e2d1b4a6c7e8f9a0b1c2d3e4",
      "prev_hash": "0xe6a2f7b8d1c0a3b4c5d6e7f8a9b0c1d2",
      "nonce": "12345",
      "miner": "node-security-prod-03",
      "timestamp_block": "2026-04-01T10:31:00Z"
    },
    "digital_signature": "MEUCIQD5f4g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7a8b9c0...",
    "sign_algorithm": "RSA-2048-SHA256",
    "sign_key_id": "SK-AUDIT-001"
  }
}
```

### 4.4 Blockchain 노드 구성

```yaml
# Hyperledger Fabric 감사 로그 채널 구성
blockchain_config:
  type: "hyperledger_fabric"
  network_name: "audit-network"
  
  orderers:
    - name: "orderer-1.audit.local"
      port: 7050
      region: "Malaysia"
    - name: "orderer-2.audit.local"
      port: 7050
      region: "Singapore (DR)"
  
  peers:
    - name: "peer-audit-1"
      org: "Security"
      endorsement: true
    - name: "peer-audit-2"
      org: "Compliance"
      endorsement: false
    - name: "peer-audit-3"
      org: "External-Auditor"
      endorsement: false
  
  chaincodes:
    - name: "audit_logger"
      version: "1.0"
      language: "go"
      policy: "endorsement_majority"
  
  retention:
    cold_storage_days: 90
    archive_location: "blockchain_archival_service"
    backup_frequency: "daily"
```

### 4.5 감사 로그 조회 및 검증

```python
# Blockchain 감사 로그 검증 서비스
class AuditLogVerificationService:
    
    def verify_log_integrity(self, log_id: str) -> bool:
        """블록체인 상의 로그 무결성 검증"""
        log = self.fetch_from_blockchain(log_id)
        current_hash = self.calculate_hash(log)
        
        # 현재 해시값과 블록체인 기록된 값 비교
        return current_hash == log['blockchain']['hash']
    
    def verify_chain_continuity(self, log_id: str) -> bool:
        """감사 로그 체인 연속성 검증"""
        log = self.fetch_from_blockchain(log_id)
        prev_log = self.fetch_previous_log(log['blockchain']['prev_hash'])
        
        # 이전 로그의 해시가 현재 로그의 prev_hash와 일치하는지 확인
        prev_hash_calculated = self.calculate_hash(prev_log)
        return prev_hash_calculated == log['blockchain']['prev_hash']
    
    def generate_compliance_report(self, date_from: str, date_to: str):
        """기간별 감사 로그 컴플라이언스 리포트"""
        logs = self.fetch_logs_by_date_range(date_from, date_to)
        report = {
            "period": f"{date_from} ~ {date_to}",
            "total_events": len(logs),
            "integrity_verified": sum(1 for log in logs if self.verify_log_integrity(log['id'])),
            "integrity_rate": sum(1 for log in logs if self.verify_log_integrity(log['id'])) / len(logs) * 100,
            "critical_events": [l for l in logs if l['event_type'] in ['security_event', 'data_deletion']],
            "unauthorized_access_attempts": len([l for l in logs if l['status'] == 'failed' and l['event_type'] == 'data_access'])
        }
        return report
```

---

## 5. 보안 인증 로드맵

### 5.1 인증 목표 및 일정

```
┌─────────────────────────────────────────────────────────┐
│         보안 인증 로드맵 (Security Certification Roadmap) │
└─────────────────────────────────────────────────────────┘

Phase 1: 기초 구축 (기간: 2026년 4-6월)
  ├─ ISO/IEC 27001:2022 기초 평가
  ├─ PDPA 정책 문서화 및 프로세스 수립
  └─ 정보보안관리체계(ISMS) 초기 구성

Phase 2: 중간 강화 (기간: 2026년 7-9월)
  ├─ ISO/IEC 27001:2022 인증 신청
  ├─ PCI-DSS v3.2.1 자체 평가 (Self-Assessment)
  └─ Blockchain 감시 시스템 구축 완료

Phase 3: 국가 인증 (기간: 2026년 10-12월)
  ├─ Malaysia ISMS-P (Information Security Management System Program) 신청
  ├─ PCI-DSS v3.2.1 Level 2 승인
  └─ PDPA 정책 검증 및 승인

Phase 4: 확장 인증 (기간: 2027년 1-3월)
  ├─ 우즈벡 데이터 보호법 준수 인증
  ├─ 필리핀 NPC 등록 및 승인
  └─ GDPR 유럽 일반 데이터 보호규정 준비
```

### 5.2 주요 인증 기준 상세

#### 5.2.1 ISO/IEC 27001:2022

| 통제 영역 | 요구사항 | HiPass 구현 | 검증 방법 |
|---------|---------|-----------|---------|
| **조직 컨텍스트** | 정보보안 정책, 역할 정의 | 문서화, 조직도 | 문서 검토, 인터뷰 |
| **자산 관리** | 자산 인벤토리, 분류 | 데이터 분류 체계 | 자산 등록부 확인 |
| **접근 제어** | 사용자 인증, 권한 관리 | RBAC, MFA 구현 | 로그 검토, 접근 테스트 |
| **암호화** | 전송/저장 시 암호화 | TLS 1.3, AES-256 | 통신 스니핑, 저장소 검사 |
| **물리 보안** | 데이터센터 보안 | 접근 제어, CCTV | 현장 점검 |
| **사고 대응** | 사고 관리 계획 | 플레이북, 테스트 | 소방 훈련 |
| **사업 연속성** | 재해복구 계획, RTO/RPO | DR 체계, 테스트 | 백업 검증, 페일오버 테스트 |
| **공급업체 관리** | 제3자 위험 관리 | 계약, 감시 | SLA 검토, 감사 |

**예상 인증 일자**: 2026년 9월  
**유지 감시**: 연 1회 (3년 주기)

#### 5.2.2 PCI-DSS v3.2.1

| 요구사항 | 설명 | HiPass 적용 | 준수 상태 |
|---------|------|-----------|---------|
| **Req 1** | 방화벽 구성 | 네트워크 세분화, WAF | 구현 중 |
| **Req 2** | 기본값 미사용 | 암호 변경, 불필요 서비스 비활성화 | 완료 |
| **Req 3** | 데이터 보호 | 암호화 저장, 토큰화 | 구현 예정 |
| **Req 4** | 암호화 전송 | TLS 1.2 이상 | 완료 |
| **Req 5** | 맬웨어 방어 | 안티바이러스, 패치 관리 | 진행 중 |
| **Req 6** | 보안 개발 | SAST, DAST, 코드 검토 | 구현 중 |
| **Req 7** | 접근 제한 | 최소 권한 원칙 | 진행 중 |
| **Req 8** | 사용자 인증 | MFA, 암호 정책 | 완료 |
| **Req 9** | 물리 접근 | 데이터센터 접근 제어 | 완료 |
| **Req 10** | 로깅 모니터링 | 감시 로그, 실시간 알림 | 구현 완료 |
| **Req 11** | 테스트 | 침투 테스트, 취약점 스캔 | 연 2회 예정 |
| **Req 12** | 정책 관리 | 정책 문서, 교육 | 진행 중 |

**평가 수준**: Level 2 (연간 거래액 기준)  
**자체 평가 제출**: 2026년 12월  
**승인 예상**: 2027년 1월

#### 5.2.3 Malaysia ISMS-P (Information Security Management System Program)

Malaysia Information Security Manual (ISM) 기반의 국가 보안 인증.

| 영역 | 요구사항 | HiPass 체계 |
|-----|--------|-----------|
| **거버넌스** | CISO 임명, 정보보안위원회 구성 | Chief Information Security Officer 지정 |
| **정책** | 정보보안 정책, 절차 문서화 | 주요 정책 10개, 절차서 30개 |
| **리스크 관리** | 연간 정보보안 위험 평가 | 분기별 위험 평가, 관리 |
| **기술 통제** | 적절한 기술 보안 조치 | 암호화, 접근 제어, 로깅 |
| **교육 훈련** | 모든 직원 연 2회 이상 | 신입 교육 + 연 2회 재교육 |
| **감사 검증** | 연 1회 내부 감사 | 분기별 내부 감사 |

**신청 일정**: 2026년 10월  
**승인 예상**: 2026년 12월

### 5.3 인증별 예산 및 리소스

| 인증 | 비용 | 소요 기간 | 필요 리소스 |
|-----|------|---------|----------|
| **ISO 27001** | RM 150,000 | 6개월 | CISO, 감시자, 컨설턴트 3명 |
| **PCI-DSS** | RM 80,000 | 4개월 | QSA(자격 심사자), 개발팀 |
| **ISMS-P** | RM 100,000 | 3개월 | CISO, 부설 담당자 2명 |
| **합계** | RM 330,000 | 12개월 | 전담 팀 6명 |

---

## 6. 기술 통제 (Technical Controls)

### 6.1 데이터 암호화 기준

```yaml
encryption_standards:
  in_transit:
    protocol: "TLS 1.3"
    cipher_suite: "TLS_AES_256_GCM_SHA384"
    certificate: "SHA-256 (2048-bit RSA minimum)"
    validation: "HSTS enabled, OCSP stapling"
    
  at_rest:
    algorithm: "AES-256-GCM"
    key_derivation: "PBKDF2 with SHA-256, 100000 iterations"
    key_management: "AWS KMS (Malaysia region)"
    field_level: "Critical PII columns encrypted"
    backup_encryption: "Yes, same standard"
    
  key_rotation:
    schedule: "quarterly"
    process: "automated with zero-downtime migration"
    audit_trail: "all rotations logged to blockchain"
```

### 6.2 접근 제어 모델

```python
# 역할 기반 접근 제어 (RBAC) + 속성 기반 접근 제어 (ABAC)
access_control_policy = {
    "ADMIN": {
        "permissions": ["read", "write", "delete", "audit"],
        "data_scope": "all",
        "masked": False,
        "ip_restriction": None
    },
    "ANALYST": {
        "permissions": ["read", "write"],
        "data_scope": ["aggregated", "historical"],
        "masked": True,
        "ip_restriction": ["office_network"]
    },
    "CUSTOMER_SERVICE": {
        "permissions": ["read"],
        "data_scope": ["own_customer_only"],
        "masked": True,
        "ip_restriction": ["office_network", "vpn"],
        "time_restriction": "business_hours_only"
    },
    "SYSTEM_AUDIT": {
        "permissions": ["read"],
        "data_scope": ["audit_logs_only"],
        "masked": False,
        "ip_restriction": ["audit_workstation"]
    }
}
```

### 6.3 침해 탐지 및 대응 시스템

```
실시간 모니터링 (SIEM)
  ├─ 비정상 로그인 탐지
  ├─ 대량 데이터 조회 감시
  ├─ 권한 외 접근 시도 감지
  └─ 악성 코드/침입 신호 탐지
    │
    └─ 자동 알림 → 90초 내 대응팀 호출
```

---

## 7. 거버넌스 및 책임

### 7.1 역할 및 책임

| 역할 | 책임 | 관련 부서 |
|-----|------|---------|
| **CISO** | 전반 보안 전략 수립, 인증 감시, 위험 보고 | 보안팀 |
| **데이터 보호 담당자** | PDPA 정책 이행, 개인정보 요청 처리 | 법무팀 |
| **감시 담당자** | 감시 로그 관리, 블록체인 검증 | 감시팀 |
| **기술 담당자** | 암호화, 접근 제어 기술 구현 | 엔지니어링팀 |
| **규정 담당자** | 외부 인증 대응, 문서화 | 컴플라이언스팀 |

### 7.2 정기적 검토 일정

- **월간**: 감시 로그 검토, 삭제 정책 확인
- **분기별**: 보안 사건 검토, 접근 로그 감시
- **반기별**: PDPA 준수 평가, 마스킹 정책 검증
- **연간**: 전체 정보보안 평가, 인증 갱신 준비

---

## 8. 참고문헌

- Personal Data Protection Act (PDPA), Malaysia 2010
- ISO/IEC 27001:2022 Information Security Management Systems
- PCI-DSS v3.2.1 (Payment Card Industry Data Security Standard)
- Malaysia Information Security Manual (ISM)
- ETCS Best Practices for Data Privacy (Asian ETCS Forum)

**문서 이력**:
- v1.0 (2026-04-01): 초안 작성
