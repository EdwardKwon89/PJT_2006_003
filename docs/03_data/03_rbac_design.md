# RBAC 설계: HiPass ETCS 플랫폼 역할 기반 접근 제어

**문서 버전**: 1.0  
**작성일**: 2026-04-01  
**상태**: Draft  
**담당자**: Security & Architecture Team

---

## 1. RBAC 개요

### 1.1 목적
HiPass ETCS 플랫폼의 데이터 접근을 역할 기반으로 제어하여 보안, 규제 준수, 운영 효율성을 확보합니다.

### 1.2 설계 원칙
- **최소 권한의 원칙 (Principle of Least Privilege)**: 각 역할은 업무 수행에 필요한 최소 권한만 보유
- **분리 원칙**: 상충되는 역할은 동시에 할당 불가 (예: 승인자 ≠ 결제 처리자)
- **감사 가능성**: 모든 접근 및 변경사항 기록
- **확장성**: 신규 역할/권한 추가 시 기존 시스템 영향 최소화

### 1.3 아키텍처 계층
```
┌─────────────────────────────────────────┐
│  Application Layer                      │  API 레벨 권한 검증
├─────────────────────────────────────────┤
│  Database Layer (RLS Policy)            │  Row Level Security
├─────────────────────────────────────────┤
│  PostgreSQL Role & Permission           │  데이터베이스 레벨 접근
└─────────────────────────────────────────┘
```

---

## 2. 30개 역할 정의

### 2.1 관리 역할 (Admin Roles) - 8개

| ID | 역할명 | 설명 | 부서 | 권한 범위 |
|---|---|---|---|---|
| ADM001 | Super Admin | 시스템 최고 관리자 | IT | 전체 시스템 |
| ADM002 | System Admin | 시스템 운영 관리자 | IT | 시스템 설정, 사용자 관리 |
| ADM003 | Security Admin | 보안 담당자 | IT | 보안 정책, 감시, 감사 |
| ADM004 | Finance Admin | 재무 관리자 | Finance | 재무 설정, 정산 구성 |
| ADM005 | Compliance Admin | 규제 준수 담당자 | Compliance | 규제 보고, 감사 추적 |
| ADM006 | Data Admin | 데이터 관리자 | IT | 데이터 백업, 복구, 정제 |
| ADM007 | Audit Admin | 감사 관리자 | Internal Audit | 감시, 보고서 생성 |
| ADM008 | Operations Admin | 운영 관리자 | Operations | 운영 설정, 모니터링 |

### 2.2 금융 역할 (Finance Roles) - 6개

| ID | 역할명 | 설명 | 부서 | 권한 범위 |
|---|---|---|---|---|
| FIN001 | Finance Manager | 재무 관리 책임자 | Finance | 결제 승인, 정산 검토 |
| FIN002 | Settlement Officer | 정산 담당자 | Finance | 정산 처리, 기록 관리 |
| FIN003 | Payment Processor | 결제 처리자 | Finance | 결제 트랜잭션 처리 |
| FIN004 | Auditor | 회계감시자 | Finance | 결제 감시, 보고서 생성 |
| FIN005 | Revenue Officer | 수익 관리자 | Finance | 수익 분배, 요금 설정 |
| FIN006 | Billing Clerk | 청구 담당자 | Finance | 인보이스 생성, 관리 |

### 2.3 운영 역할 (Operations Roles) - 7개

| ID | 역할명 | 설명 | 부서 | 권한 범위 |
|---|---|---|---|---|
| OPS001 | Operations Manager | 운영 관리 책임자 | Operations | 운영 계획, 모니터링 |
| OPS002 | Technical Support | 기술 지원팀 | Support | 고객 지원, 문제 해결 |
| OPS003 | Traffic Controller | 교통 컨트롤러 | Operations | 실시간 교통 관리 |
| OPS004 | Toll Gate Operator | 요금소 운영자 | Operations | 요금소 운영, 기록 |
| OPS005 | Customer Service Rep | 고객 서비스 담당자 | Customer Service | 고객 문의 처리 |
| OPS006 | System Operator | 시스템 운영자 | IT | 시스템 상태 모니터링 |
| OPS007 | Incident Manager | 사고 관리자 | Operations | 사고 대응, 보고 |

### 2.4 데이터 분석 역할 (Analytics Roles) - 4개

| ID | 역할명 | 설명 | 부서 | 권한 범위 |
|---|---|---|---|---|
| ANL001 | Analytics Manager | 분석 팀 리더 | Analytics | 모든 분석 데이터 접근 |
| ANL002 | Data Analyst | 데이터 분석가 | Analytics | 분석 데이터 조회, 보고서 생성 |
| ANL003 | Business Analyst | 비즈니스 분석가 | Analytics | 비즈니스 메트릭 조회 |
| ANL004 | Report Generator | 보고서 생성자 | Analytics | 정기 보고서 생성 |

### 2.5 고객 역할 (Customer Roles) - 3개

| ID | 역할명 | 설명 | 부서 | 권한 범위 |
|---|---|---|---|---|
| CUS001 | Account Owner | 계정 소유자 (기업) | Customer | 자신의 계정 관리 |
| CUS002 | Account Manager | 계정 담당자 (기업) | Customer | 계정 관리자 (기업) |
| CUS003 | End User | 일반 사용자 | Customer | 본인 데이터만 접근 |

### 2.6 파트너 역할 (Partner Roles) - 2개

| ID | 역할명 | 설명 | 부서 | 권한 범위 |
|---|---|---|---|---|
| PRT001 | Partner Admin | 파트너 관리자 | Partners | 파트너 시스템 관리 |
| PRT002 | Partner Operator | 파트너 운영자 | Partners | 파트너 기능 운영 |

---

## 3. 데이터 접근 권한 매트릭스

### 3.1 Core Tables CRUD 권한

| 역할 | Transactions | Users | Accounts | Settlement | Audit Log |
|---|:---:|:---:|:---:|:---:|:---:|
| ADM001 | CRUD | CRUD | CRUD | CRUD | R |
| ADM002 | R | CRUD | CRUD | RU | R |
| ADM003 | R | RU | R | R | CRUD |
| ADM004 | R | R | R | CRUD | R |
| ADM005 | R | R | R | R | R |
| ADM006 | CU | CU | CU | CU | R |
| ADM007 | R | R | R | R | R |
| ADM008 | R | RU | RU | R | RU |
| FIN001 | R | - | R | CRUD | R |
| FIN002 | R | - | - | CRUD | R |
| FIN003 | CU | - | - | RU | R |
| FIN004 | R | - | - | R | R |
| FIN005 | R | - | R | RU | R |
| FIN006 | R | - | R | R | R |
| OPS001 | R | - | R | - | R |
| OPS002 | R | - | R | - | R |
| OPS003 | R | - | - | - | - |
| OPS004 | CR | - | - | - | - |
| OPS005 | R | - | R | - | R |
| OPS006 | R | - | - | - | R |
| OPS007 | R | - | - | - | CRUD |
| ANL001 | R | R | R | R | R |
| ANL002 | R | - | R | - | - |
| ANL003 | R | - | R | - | - |
| ANL004 | R | - | R | - | - |
| CUS001 | R (own) | R (own) | RU (own) | R | - |
| CUS002 | R (corp) | RU (corp) | CRUD (corp) | R | - |
| CUS003 | R (own) | R (own) | - | - | - |
| PRT001 | R | RU | R | R | RU |
| PRT002 | R | - | R | - | R |

**범례**: C=Create, R=Read, U=Update, D=Delete, "-"=No Access

### 3.2 특수 데이터 필드 접근

| 역할 | 민감정보<br>(SSN, Card) | 금융정보<br>(Account #) | 개인정보<br>(Contact) | 감사정보<br>(Logs) |
|---|:---:|:---:|:---:|:---:|
| ADM001 | R | R | R | R |
| ADM003 | R | R | - | R |
| FIN001 | R | R | - | R |
| FIN003 | - | R | - | - |
| OPS002 | - | - | R | - |
| CUS001 | R (own) | R (own) | R (own) | - |
| CUS003 | - | - | R (own) | - |

---

## 4. PostgreSQL Row Level Security (RLS) 정책

### 4.1 기본 정책 구조

```sql
-- 정책 1: 사용자는 자신의 거래만 조회 가능
CREATE POLICY user_transactions_policy ON transactions
FOR SELECT
USING (
  user_id = current_user_id() 
  OR user_role_id() IN (SELECT id FROM roles WHERE access_level >= 5)
);

-- 정책 2: 관리자만 거래 수정 가능
CREATE POLICY admin_update_policy ON transactions
FOR UPDATE
WITH CHECK (
  user_role_id() IN (SELECT id FROM roles WHERE is_admin = true)
  AND NOT (status = 'completed' AND transaction_date < now() - '30 days'::interval)
);

-- 정책 3: 감시자는 모든 거래 조회 가능
CREATE POLICY auditor_read_policy ON transactions
FOR SELECT
USING (
  user_role_id() IN (SELECT id FROM roles WHERE can_audit = true)
);
```

### 4.2 테이블별 RLS 설정

#### Transactions 테이블
```sql
CREATE TABLE transactions (
  id UUID PRIMARY KEY,
  user_id UUID NOT NULL REFERENCES users(id),
  account_id UUID NOT NULL REFERENCES accounts(id),
  amount DECIMAL(15,2),
  status VARCHAR(20),
  transaction_date TIMESTAMP,
  created_by UUID,
  updated_by UUID,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

ALTER TABLE transactions ENABLE ROW LEVEL SECURITY;

-- 정책 1: SELECT - 자신의 거래 또는 권한이 있는 경우
CREATE POLICY transactions_select ON transactions
FOR SELECT
USING (
  user_id = auth.uid()  -- 자신의 거래
  OR EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission = 'view_all_transactions'
  )
);

-- 정책 2: INSERT - 자신 또는 권한자만 생성 가능
CREATE POLICY transactions_insert ON transactions
FOR INSERT
WITH CHECK (
  user_id = auth.uid()
  OR EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission = 'create_transactions'
  )
);

-- 정책 3: UPDATE - 권한자만 수정 가능
CREATE POLICY transactions_update ON transactions
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission = 'update_transactions'
  )
)
WITH CHECK (
  -- 완료된 거래는 30일 이후 수정 불가
  NOT (status = 'completed' AND transaction_date < now() - '30 days'::interval)
);

-- 정책 4: DELETE - Super Admin만 가능
CREATE POLICY transactions_delete ON transactions
FOR DELETE
USING (
  EXISTS (
    SELECT 1 FROM user_roles ur
    WHERE ur.user_id = auth.uid()
    AND ur.role_id = (SELECT id FROM roles WHERE name = 'Super Admin')
  )
);
```

#### Users 테이블
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE,
  name VARCHAR(255),
  department VARCHAR(100),
  phone VARCHAR(20),
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now(),
  is_active BOOLEAN DEFAULT true
);

ALTER TABLE users ENABLE ROW LEVEL SECURITY;

-- 정책 1: 자신의 정보 조회
CREATE POLICY users_select_self ON users
FOR SELECT
USING (
  id = auth.uid()
  OR EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission = 'manage_users'
  )
);

-- 정책 2: 자신의 정보만 수정
CREATE POLICY users_update_self ON users
FOR UPDATE
USING (id = auth.uid())
WITH CHECK (id = auth.uid());

-- 정책 3: 권한자만 다른 사용자 수정
CREATE POLICY users_update_admin ON users
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission = 'manage_users'
  )
);
```

#### Settlement 테이블
```sql
CREATE TABLE settlement (
  id UUID PRIMARY KEY,
  settlement_date DATE,
  period_start DATE,
  period_end DATE,
  total_amount DECIMAL(15,2),
  status VARCHAR(20),
  created_by UUID REFERENCES users(id),
  approved_by UUID REFERENCES users(id),
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

ALTER TABLE settlement ENABLE ROW LEVEL SECURITY;

-- 정책 1: 기본 조회 권한
CREATE POLICY settlement_select ON settlement
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission IN ('view_settlement', 'manage_settlement')
  )
);

-- 정책 2: 정산 생성
CREATE POLICY settlement_insert ON settlement
FOR INSERT
WITH CHECK (
  created_by = auth.uid()
  AND EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission = 'create_settlement'
  )
);

-- 정책 3: 정산 승인 (권한자만)
CREATE POLICY settlement_approve ON settlement
FOR UPDATE
USING (
  EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission = 'approve_settlement'
  )
)
WITH CHECK (
  -- 완료된 정산은 수정 불가
  status != 'completed'
);
```

#### Audit Log 테이블
```sql
CREATE TABLE audit_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  table_name VARCHAR(100),
  operation VARCHAR(10),  -- INSERT, UPDATE, DELETE
  record_id UUID,
  old_values JSONB,
  new_values JSONB,
  changed_by UUID REFERENCES users(id),
  changed_at TIMESTAMP DEFAULT now(),
  ip_address INET
);

ALTER TABLE audit_log ENABLE ROW LEVEL SECURITY;

-- 정책: 감사자만 읽기 가능
CREATE POLICY audit_log_select ON audit_log
FOR SELECT
USING (
  EXISTS (
    SELECT 1 FROM user_roles ur
    JOIN role_permissions rp ON ur.role_id = rp.role_id
    WHERE ur.user_id = auth.uid()
    AND rp.permission = 'view_audit_log'
  )
);

-- 쓰기는 시스템만 가능 (트리거)
CREATE POLICY audit_log_insert ON audit_log
FOR INSERT
WITH CHECK (
  auth.uid() = 'system-user-id'
);
```

---

## 5. 기능 권한 매트릭스

### 5.1 주요 기능별 권한

| 기능 | ADM001 | FIN001 | OPS001 | ANL001 | CUS001 |
|---|:---:|:---:|:---:|:---:|:---:|
| 사용자 관리 | ✓ | ✗ | ✗ | ✗ | ✗ |
| 역할 설정 | ✓ | ✗ | ✗ | ✗ | ✗ |
| 거래 생성 | ✓ | ✓ | △ | ✗ | ✓ |
| 거래 조회 | ✓ | ✓ | ✓ | ✓ | ✓* |
| 거래 수정 | ✓ | ✓ | ✗ | ✗ | ✓* |
| 거래 삭제 | ✓ | ✗ | ✗ | ✗ | ✗ |
| 정산 생성 | ✓ | ✓ | ✗ | ✗ | ✗ |
| 정산 승인 | ✓ | ✓ | ✗ | ✗ | ✗ |
| 보고서 생성 | ✓ | ✓ | ✓ | ✓ | ✗ |
| 감시 로그 조회 | ✓ | ✗ | ✗ | ✗ | ✗ |
| 규제 보고서 | ✓ | ✗ | ✗ | ✗ | ✗ |

**범례**: ✓=Full, △=Limited, ✗=None, *=Own Data Only

### 5.2 API 엔드포인트별 권한

```json
{
  "POST /api/transactions": {
    "required_roles": ["ADM001", "FIN003", "OPS004", "CUS001"],
    "required_permissions": ["create_transactions"],
    "audit": true
  },
  "GET /api/transactions": {
    "required_roles": ["*"],
    "required_permissions": ["view_transactions"],
    "audit": true,
    "filters": {
      "user_id": "own_only"
    }
  },
  "PUT /api/transactions/:id": {
    "required_roles": ["ADM001", "ADM002", "FIN001"],
    "required_permissions": ["update_transactions"],
    "audit": true,
    "restrictions": [
      "cannot_update_completed_transaction_after_30days"
    ]
  },
  "DELETE /api/transactions/:id": {
    "required_roles": ["ADM001"],
    "required_permissions": ["delete_transactions"],
    "audit": true,
    "restrictions": [
      "cannot_delete_completed_transaction"
    ]
  },
  "GET /api/settlement": {
    "required_roles": ["ADM001", "ADM002", "ADM004", "FIN001"],
    "required_permissions": ["view_settlement"],
    "audit": true
  },
  "POST /api/settlement": {
    "required_roles": ["ADM001", "ADM004", "FIN001"],
    "required_permissions": ["create_settlement"],
    "audit": true
  },
  "POST /api/settlement/:id/approve": {
    "required_roles": ["ADM001", "FIN001"],
    "required_permissions": ["approve_settlement"],
    "audit": true
  }
}
```

---

## 6. API 레벨 필터

### 6.1 요청 검증 미들웨어

```typescript
// 예시: Node.js/Express
async function roleBasedAccessControl(req, res, next) {
  const user = req.user;
  const endpoint = req.path;
  const method = req.method;
  
  // 사용자 역할 조회
  const userRoles = await getUserRoles(user.id);
  const permissions = await getRolePermissions(userRoles);
  
  // 엔드포인트 권한 확인
  const requiredPerms = await getEndpointPermissions(endpoint, method);
  
  if (!hasRequiredPermissions(permissions, requiredPerms)) {
    return res.status(403).json({
      error: 'Insufficient permissions',
      required: requiredPerms,
      granted: permissions
    });
  }
  
  // 데이터 필터링
  req.dataFilter = buildDataFilter(user, userRoles);
  next();
}

// 데이터 필터링 규칙
function buildDataFilter(user, roles) {
  const filters = {};
  
  // 고객은 자신의 데이터만
  if (roles.includes('CUS001') || roles.includes('CUS003')) {
    filters.user_id = user.id;
    filters.account_id = user.account_id;
  }
  
  // 법인 계정 담당자는 회사 계정만
  if (roles.includes('CUS002')) {
    filters.account_id = user.corporate_account_id;
  }
  
  // 관리자는 필터 없음
  if (roles.some(r => r.startsWith('ADM'))) {
    return null;
  }
  
  return filters;
}
```

### 6.2 응답 필드 마스킹

```typescript
function maskResponseData(data, userRole) {
  const sensitiveFields = {
    'ssn': true,
    'card_number': true,
    'bank_account': true,
    'password': true
  };
  
  // 감시자/관리자는 민감정보 허용
  if (['ADM001', 'ADM003', 'FIN001'].includes(userRole)) {
    return data;
  }
  
  // 다른 역할은 마스킹
  const masked = JSON.parse(JSON.stringify(data));
  
  for (const field of Object.keys(sensitiveFields)) {
    if (masked[field]) {
      masked[field] = '***REDACTED***';
    }
  }
  
  return masked;
}
```

### 6.3 시간 기반 접근 제한

```typescript
function checkTimeBasedAccess(user, action) {
  const restrictions = {
    'approve_settlement': {
      allowed_hours: '08:00-18:00',
      allowed_days: 'MON-FRI',
      timezone: 'Asia/Kuala_Lumpur'
    },
    'delete_transactions': {
      allowed_hours: '09:00-17:00',
      allowed_days: 'MON-FRI'
    }
  };
  
  const rule = restrictions[action];
  if (!rule) return true;
  
  const now = moment().tz(rule.timezone);
  const [start, end] = rule.allowed_hours.split('-');
  
  if (!isBetweenHours(now, start, end)) {
    return false;
  }
  
  if (!rule.allowed_days.includes(now.format('ddd').toUpperCase())) {
    return false;
  }
  
  return true;
}
```

---

## 7. 접근 제어 구현 체크리스트

### 7.1 데이터베이스 레벨
- [ ] RLS 정책 생성 및 테스트
- [ ] 역할별 권한 설정
- [ ] 감시 트리거 구현
- [ ] 데이터 마스킹 함수 생성
- [ ] 접근 제어 테스트 케이스 작성

### 7.2 애플리케이션 레벨
- [ ] 권한 검증 미들웨어 구현
- [ ] 역할 기반 라우팅 설정
- [ ] 응답 필터링 로직 구현
- [ ] 감시 로깅 구현
- [ ] 권한 캐싱 전략 수립

### 7.3 보안 감시
- [ ] 접근 거부 로깅
- [ ] 권한 상승 탐지
- [ ] 비정상 접근 패턴 모니터링
- [ ] 정기 권한 감시 보고서

---

## 8. 마이그레이션 계획

### 8.1 Phase 1: 기초 설정 (Week 1-2)
- 역할 및 권한 테이블 생성
- 기존 사용자 매핑
- RLS 정책 구현

### 8.2 Phase 2: 애플리케이션 통합 (Week 3-4)
- 미들웨어 구현
- 데이터 필터링 적용
- API 엔드포인트 보안

### 8.3 Phase 3: 검증 및 배포 (Week 5-6)
- 통합 테스트
- 보안 감사
- 프로덕션 배포

---

## 9. 참고사항

- 모든 권한 변경은 감시 로그에 기록됩니다
- 역할 할당은 Manager 이상만 가능합니다
- 민감 데이터는 암호화되어 저장됩니다
- 정기적인 권한 감시 검토 필요 (월 1회)

---

**문서 이력**

| 버전 | 일자 | 변경 사항 | 작성자 |
|---|---|---|---|
| 1.0 | 2026-04-01 | 초안 작성 | Security Team |
