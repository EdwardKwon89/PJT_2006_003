# 메타데이터 용어 사전 (Metadata Glossary)

**Document ID:** WAVE2-METADATA-04  
**Version:** 1.0  
**Date:** 2026-04-01  
**Status:** DRAFT  
**Owner:** Data Governance Team  
**Languages:** Korean (KO) / English (EN) / Malay (BM)

---

## 목차 (Table of Contents)

1. [개요](#개요)
2. [데이터 정의서](#데이터-정의서-data-definitions)
3. [용어 사전 (300+ 항목)](#용어-사전)
4. [코드 마스터 (Code Master)](#코드-마스터)
5. [검증 규칙](#검증-규칙)
6. [메타데이터 카탈로그](#메타데이터-카탈로그)

---

## 개요

Malaysia BOS(Back-Office System)의 모든 데이터 요소를 **정의, 분류, 검증**하기 위한 중앙 집중식 메타데이터 저장소. 3언어(KO/EN/BM) 지원으로 국제 팀 협력을 가능하게 한다.

### 적용 대상

- **데이터 모델링**: 엔티티, 속성, 관계 정의
- **API 설계**: 요청/응답 스키마 표준화
- **데이터베이스**: 테이블, 컬럼, 인덱스 명세
- **데이터 품질**: 유효성 검사, 데이터 정제
- **규정 준수**: 감사 추적, 데이터 거버넌스

---

## 데이터 정의서 (Data Definitions)

### 1. 핵심 데이터 엔티티

| 코드 | 한글명 | English | Bahasa Melayu | 설명 | 주 데이터베이스 |
|------|--------|---------|----------------|------|----------------|
| VEH | 차량 | Vehicle | Kenderaan | 통행 차량 기본 정보 | VEHICLE |
| TAG | 전자태그 | RFID Tag | Tag RFID | 차량에 장착된 RFID 태그 | TAG_MASTER |
| TXN | 거래 | Transaction | Transaksi | 통행 요금 거래 기록 | TRANSACTION_LOG |
| ACC | 계정 | Account | Akaun | 사용자/차주 계정 정보 | ACCOUNT |
| PAY | 결제 | Payment | Pembayaran | 요금 결제 이력 | PAYMENT |
| TOLL | 요금 | Toll Charge | Caj Jalan Tol | 요금 구간/금액 | TOLL_RATE |
| LANE | 차선 | Lane | Lorong | 요금소 차선 | TOLL_LANE |
| GTE | 게이트 | Gate | Pintu Gerbang | 요금소 게이트 센서 | TOLL_GATE |
| PLAZA | 요금소 | Toll Plaza | Plaza Tol | 요금 징수소 | TOLL_PLAZA |
| JVC | 사업체 | Joint Venture Co. | Syarikat Usaha Sama | 도로사업 시행사 | JVC_MASTER |
| TOC | 운영사 | Toll Operator | Pengoperasi Tol | 요금소 운영 회사 | TOC_MASTER |
| SCC | 정산사 | Settlement Center | Pusat Penyelesaian | 요금 정산 기관 | SCC_MASTER |
| VIOLATION | 미납 | Violation | Pelanggaran | 미납 요금 기록 | VIOLATION_LOG |
| INVOICE | 청구 | Invoice | Invois | 정산 청구서 | INVOICE |
| REPORT | 보고서 | Report | Laporan | 정산 보고서 | REPORT_MASTER |

### 2. 데이터 도메인 (Domains)

| 도메인 | 설명 | 범위 | 담당팀 |
|--------|------|------|--------|
| **Customer** | 고객/차주 | ACCOUNT, VEHICLE, CONTACT | Customer Service |
| **Transaction** | 거래/통행 | TXN, TAG, TOLL, VIOLATION | Operations |
| **Payment** | 결제/청구 | PAY, INVOICE, SCC, REPORT | Finance |
| **Infrastructure** | 기반시설 | PLAZA, GTE, LANE, TOLL_RATE | Infrastructure Ops |
| **Governance** | 거버넌스 | JVC, TOC, SCC_MASTER | Executive |
| **Compliance** | 규정 | AUDIT_LOG, POLICY, RULE | Compliance & Risk |

---

## 용어 사전

### 섹션 A: 계정 및 고객 (Account & Customer) - 50 항목

| # | 한글명 | English | Bahasa Melayu | 정의 | 데이터타입 |
|---|--------|---------|----------------|------|-----------|
| 1 | 계정 번호 | Account ID | ID Akaun | 고객 계정의 고유 식별자 | CHAR(20) |
| 2 | 계정 상태 | Account Status | Status Akaun | ACTIVE, INACTIVE, SUSPENDED, CLOSED | VARCHAR(20) |
| 3 | 계정 유형 | Account Type | Jenis Akaun | INDIVIDUAL, CORPORATE, FLEET, GOVERNMENT | VARCHAR(20) |
| 4 | 차주명 | Vehicle Owner | Pemilik Kenderaan | 차량 등록 소유자 이름 | VARCHAR(100) |
| 5 | 생년월일 | Date of Birth | Tarikh Lahir | YYYY-MM-DD 형식 | DATE |
| 6 | 신분증 번호 | Identity Card No | No. Kad Pengenalan | IC/Passport 번호 | VARCHAR(30) |
| 7 | 전화번호 | Phone Number | Nombor Telefon | 국가번호 포함 (예: +60) | VARCHAR(20) |
| 8 | 이메일 | Email Address | Alamat E-mel | 유효한 이메일 형식 | VARCHAR(100) |
| 9 | 배송 주소 | Mailing Address | Alamat Surat-menyurat | 송장/통지 배송처 | VARCHAR(255) |
| 10 | 우편번호 | Postal Code | Kod Pos | Malaysia 5자리 형식 | CHAR(5) |
| 11 | 도시 | City | Bandaraya | KL, SELANGOR, JOHOR, ... | VARCHAR(50) |
| 12 | 주/도 | State | Negeri | 13개 주(Negeri) | CHAR(2) |
| 13 | 국가 | Country | Negara | ISO 3166-1 코드 (예: MY) | CHAR(2) |
| 14 | 계정 개설일 | Account Open Date | Tarikh Membuka Akaun | 계정 생성 날짜 | DATETIME |
| 15 | 계정 종료일 | Account Close Date | Tarikh Menutup Akaun | NULL이면 활성 계정 | DATETIME |
| 16 | 마지막 활동일 | Last Activity Date | Tarikh Aktiviti Terakhir | 마지막 로그인/거래 | DATETIME |
| 17 | 선호 언어 | Preferred Language | Bahasa Pilihan | EN, KO, BM | CHAR(2) |
| 18 | 통지 방식 | Notification Channel | Saluran Pemberitahuan | SMS, EMAIL, PUSH, POSTAL | VARCHAR(20) |
| 19 | 신용 한도 | Credit Limit | Had Kredit | 선금/외상 최대 한도 (MYR) | DECIMAL(12,2) |
| 20 | 사용 잔액 | Used Balance | Baki Terpakai | 현재 누적 사용액 (MYR) | DECIMAL(12,2) |
| 21 | 선금 잔액 | Prepaid Balance | Baki Prabayar | 선납금 잔액 (MYR) | DECIMAL(12,2) |
| 22 | 담당자명 | Account Manager | Pengurus Akaun | 할당된 담당 직원 | VARCHAR(50) |
| 23 | VIP 여부 | VIP Status | Status VIP | Y/N (우대 고객 여부) | CHAR(1) |
| 24 | 자동 충전 여부 | Auto-Recharge | Auto-cas Ulang | Y/N (자동 충전 설정) | CHAR(1) |
| 25 | 자동 충전 금액 | Auto-Recharge Amount | Jumlah Auto-cas Ulang | MYR 단위 | DECIMAL(8,2) |
| 26 | 자동 충전 임계값 | Recharge Threshold | Nilai Ambang Cas Ulang | 잔액 이하일 때 자동 충전 | DECIMAL(8,2) |
| 27 | 할인율 | Discount Rate | Kadar Diskon | % (0~100) | DECIMAL(5,2) |
| 28 | 할인 시작일 | Discount Start Date | Tarikh Mula Diskon | YYYY-MM-DD | DATE |
| 29 | 할인 종료일 | Discount End Date | Tarikh Akhir Diskon | YYYY-MM-DD | DATE |
| 30 | 회원 등급 | Membership Tier | Peringkat Keahlian | BRONZE, SILVER, GOLD, PLATINUM | VARCHAR(20) |
| 31 | 등급 업그레이드일 | Tier Upgrade Date | Tarikh Naik Peringkat | 마지막 업그레이드 날짜 | DATE |
| 32 | 누적 거래액 | Lifetime Spending | Jumlah Perbelanjaan Seumur Hidup | 계정 개설 이후 총액 (MYR) | DECIMAL(15,2) |
| 33 | 월간 거래액 | Monthly Spending | Jumlah Perbelanjaan Bulanan | 현재 달 누적 (MYR) | DECIMAL(12,2) |
| 34 | 연간 거래액 | Annual Spending | Jumlah Perbelanjaan Tahunan | 현재 연도 누적 (MYR) | DECIMAL(15,2) |
| 35 | 블랙리스트 여부 | Blacklist Status | Status Senarai Hitam | Y/N (사기/위반 기록) | CHAR(1) |
| 36 | 블랙리스트 사유 | Blacklist Reason | Sebab Senarai Hitam | FRAUD, NONPAYMENT, ABUSE, ... | VARCHAR(50) |
| 37 | 블랙리스트 등재일 | Blacklist Date | Tarikh Senarai Hitam | 등재 날짜 | DATE |
| 38 | 블랙리스트 해제일 | Blacklist Removal Date | Tarikh Pemulihan Senarai Hitam | NULL이면 현재 등재 중 | DATE |
| 39 | 규정 동의 여부 | Terms Acceptance | Penerimaan Syarat | Y/N | CHAR(1) |
| 40 | 규정 동의일 | Terms Acceptance Date | Tarikh Penerimaan Syarat | YYYY-MM-DD HH:MM:SS | DATETIME |
| 41 | 개인정보 동의 | Privacy Consent | Persetujuan Privasi | Y/N | CHAR(1) |
| 42 | 마케팅 동의 | Marketing Consent | Persetujuan Pemasaran | Y/N | CHAR(1) |
| 43 | 계약 번호 | Contract Number | Nombor Kontrak | 해당 계약서 식별자 | VARCHAR(30) |
| 44 | 계약 시작일 | Contract Start Date | Tarikh Mula Kontrak | YYYY-MM-DD | DATE |
| 45 | 계약 종료일 | Contract End Date | Tarikh Tamat Kontrak | NULL이면 무기한 | DATE |
| 46 | 계약 유형 | Contract Type | Jenis Kontrak | STANDARD, CORPORATE, GOVERNMENT | VARCHAR(20) |
| 47 | 세금 식별번호 | Tax ID | ID Cukai | 기업용 세금번호 | VARCHAR(30) |
| 48 | 은행 계좌 | Bank Account | Akaun Bank | 자동 이체용 계좌 | VARCHAR(50) |
| 49 | 은행명 | Bank Name | Nama Bank | BNM 공시 은행명 | VARCHAR(50) |
| 50 | 등록일 | Registration Date | Tarikh Pendaftaran | 시스템 등록 타임스탬프 | DATETIME |

### 섹션 B: 차량 및 태그 (Vehicle & Tag) - 35 항목

| # | 한글명 | English | Bahasa Melayu | 정의 | 데이터타입 |
|---|--------|---------|----------------|------|-----------|
| 51 | 차량 번호판 | License Plate | Plat Nombor | 국가별 형식 | VARCHAR(20) |
| 52 | 차량 식별번호 | VIN | VIN | 17자 국제 표준 | CHAR(17) |
| 53 | 차량 유형 | Vehicle Class | Kelas Kenderaan | CAR, MOTORCYCLE, TRUCK, BUS, ... | VARCHAR(20) |
| 54 | 차량 등급 | Vehicle Category | Kategori Kenderaan | CAT-A, CAT-B, CAT-C, ... | VARCHAR(10) |
| 55 | 제조사 | Manufacturer | Pembuat | PROTON, PERODUA, TOYOTA, ... | VARCHAR(50) |
| 56 | 모델명 | Model | Model | PERSONA, MYVI, CAMRY, ... | VARCHAR(50) |
| 57 | 연식 | Year | Tahun | YYYY (예: 2023) | YEAR |
| 58 | 색상 | Color | Warna | RED, BLUE, WHITE, BLACK, ... | VARCHAR(20) |
| 59 | 등록일 | Registration Date | Tarikh Pendaftaran | YYYY-MM-DD | DATE |
| 60 | 등록 만료일 | Registration Expiry | Tarikh Tamat Pendaftaran | YYYY-MM-DD (JPJ 갱신) | DATE |
| 61 | 엔진 번호 | Engine Number | Nombor Enjin | 차량 엔진 일련번호 | VARCHAR(30) |
| 62 | 무게 | Curb Weight | Berat Kerb | kg 단위 | DECIMAL(8,2) |
| 63 | 최대 총 중량 | Gross Weight | Berat Kasar | kg 단위 | DECIMAL(8,2) |
| 64 | 차축 수 | Number of Axles | Bilangan Paksi | SLFF:1, MLFF:2 이상 | TINYINT |
| 65 | 태그 번호 | Tag ID | ID Tag | RFID 칩 고유 식별자 | CHAR(20) |
| 66 | 태그 상태 | Tag Status | Status Tag | ACTIVE, INACTIVE, LOST, DAMAGED | VARCHAR(20) |
| 67 | 태그 발급일 | Tag Issue Date | Tarikh Pengeluaran Tag | YYYY-MM-DD | DATE |
| 68 | 태그 종료일 | Tag Expiry Date | Tarikh Tamat Tag | YYYY-MM-DD (5년 유효) | DATE |
| 69 | 태그 제조사 | Tag Manufacturer | Pembuat Tag | INVENGO, SENSORMATIC, ... | VARCHAR(50) |
| 70 | 태그 배송 주소 | Tag Mailing Address | Alamat Pengiriman Tag | 태그 발급 배송처 | VARCHAR(255) |
| 71 | 태그 배송일 | Tag Delivery Date | Tarikh Pengiriman Tag | YYYY-MM-DD HH:MM:SS | DATETIME |
| 72 | 태그 수령일 | Tag Received Date | Tarikh Diterima Tag | YYYY-MM-DD | DATE |
| 73 | 태그 교체 횟수 | Tag Replacement Count | Bilangan Penggantian Tag | 누적 교체 횟수 | TINYINT |
| 74 | 이전 태그 ID | Previous Tag ID | ID Tag Sebelumnya | 교체 시 연결 정보 | CHAR(20) |
| 75 | 보험 제공자 | Insurance Provider | Penyedia Insurans | ALLIANZ, AXA, ... | VARCHAR(50) |
| 76 | 보험 정책 번호 | Insurance Policy No | No. Polisi Insurans | 차량 보험 정책번호 | VARCHAR(30) |
| 77 | 보험 만료일 | Insurance Expiry | Tarikh Tamat Insurans | YYYY-MM-DD | DATE |
| 78 | 로드 택스 번호 | Road Tax No | No. Cukai Jalan | 도로세 납부 번호 | VARCHAR(30) |
| 79 | 로드 택스 만료일 | Road Tax Expiry | Tarikh Tamat Cukai Jalan | YYYY-MM-DD | DATE |
| 80 | 차량 상태 | Vehicle Status | Status Kenderaan | ACTIVE, INACTIVE, REPORTED_STOLEN | VARCHAR(20) |
| 81 | 도난 신고 여부 | Stolen Report | Laporan Pencurian | Y/N | CHAR(1) |
| 82 | 도난 신고일 | Stolen Report Date | Tarikh Laporan Pencurian | YYYY-MM-DD | DATE |
| 83 | 수리 이력 | Repair History | Sejarah Pembaikan | 최근 수리 기록 요약 | TEXT |
| 84 | 사고 이력 | Accident History | Sejarah Kemalangan | 최근 사고 기록 | TEXT |
| 85 | 차량 공동소유자 | Co-Owner | Pemilik Bersama | 다중 소유자 지원 | VARCHAR(100) |

### 섹션 C: 거래 및 통행 (Transaction & Toll) - 45 항목

| # | 한글명 | English | Bahasa Melayu | 정의 | 데이터타입 |
|---|--------|---------|----------------|------|-----------|
| 86 | 거래 ID | Transaction ID | ID Transaksi | 고유 거래 식별자 | CHAR(30) |
| 87 | 거래 시간 | Transaction Time | Waktu Transaksi | YYYY-MM-DD HH:MM:SS.mmm | DATETIME |
| 88 | 거래 상태 | Transaction Status | Status Transaksi | PENDING, COMPLETED, FAILED, DISPUTED | VARCHAR(20) |
| 89 | 통행 시각 | Toll Time | Waktu Tol | 통행료소 통과 시각 | DATETIME |
| 90 | 통행 요금 | Toll Amount | Jumlah Tol | MYR 단위 | DECIMAL(10,2) |
| 91 | 할인금 | Discount Amount | Jumlah Diskon | MYR 단위 | DECIMAL(10,2) |
| 92 | 최종 청구액 | Final Charge | Caj Akhir | = Toll Amount - Discount | DECIMAL(10,2) |
| 93 | 지불 방식 | Payment Method | Kaedah Pembayaran | CASH, CARD, E_WALLET, TAG, ... | VARCHAR(20) |
| 94 | 태그 판독 여부 | Tag Read Status | Status Pembacaan Tag | SUCCESS, FAILED, NO_TAG | VARCHAR(20) |
| 95 | ANPR 판독 여부 | ANPR Read Status | Status Bacaan ANPR | SUCCESS, FAILED, NO_PLATE | VARCHAR(20) |
| 96 | 차선 번호 | Lane Number | Nombor Lorong | 통행한 게이트 차선 | TINYINT |
| 97 | 게이트 번호 | Gate ID | ID Pintu | 물리 게이트 식별자 | VARCHAR(10) |
| 98 | 요금소 코드 | Toll Plaza Code | Kod Plaza Tol | TKL01, PHG02, ... | VARCHAR(10) |
| 99 | 요금소명 | Toll Plaza Name | Nama Plaza Tol | 요금소 공식명 | VARCHAR(100) |
| 100 | 진입 지점 | Entry Point | Titik Masuk | 폐쇄식 시스템에서 진입소 | VARCHAR(50) |
| 101 | 진입 시간 | Entry Time | Waktu Masuk | YYYY-MM-DD HH:MM:SS | DATETIME |
| 102 | 퇴출 지점 | Exit Point | Titik Keluar | 폐쇄식 시스템에서 퇴출소 | VARCHAR(50) |
| 103 | 퇴출 시간 | Exit Time | Waktu Keluar | YYYY-MM-DD HH:MM:SS | DATETIME |
| 104 | 통행 거리 | Distance | Jarak | km 단위 | DECIMAL(8,2) |
| 105 | 통행 구간 | Route Segment | Segmen Rute | 요금 계산 구간 코드 | VARCHAR(20) |
| 106 | 기계 오류 코드 | Error Code | Kod Kesalahan | 센서/게이트 오류 코드 | VARCHAR(20) |
| 107 | 기계 오류 설명 | Error Description | Penerangan Kesalahan | 오류 상세 설명 | VARCHAR(255) |
| 108 | 운영자 개입 | Operator Intervention | Campur Tangan Pengendali | Y/N (수동 처리) | CHAR(1) |
| 109 | 운영자 ID | Operator ID | ID Pengendali | 처리한 운영자 직원번호 | VARCHAR(10) |
| 110 | 운영자 코멘트 | Operator Comment | Ulasan Pengendali | 처리 이유/메모 | VARCHAR(500) |
| 111 | 거래 일련번호 | Receipt Number | Nombor Resit | POS/카드 영수증 번호 | VARCHAR(30) |
| 112 | 카드 번호 (마스킹) | Card Number (Masked) | Nombor Kad (Tersembunyi) | 마지막 4자리만 (****1234) | VARCHAR(20) |
| 113 | 카드 발급사 | Card Issuer | Pengeluar Kad | VISA, MASTERCARD, AMEX, ... | VARCHAR(20) |
| 114 | 포인트 적립 | Points Earned | Poin Diperoleh | 거래 포인트 적립액 | DECIMAL(10,2) |
| 115 | 거래 증거 파일 | Receipt File | Fail Resit | 영수증 PDF/이미지 경로 | VARCHAR(255) |
| 116 | 분쟁 여부 | Disputed | Dipertikaikan | Y/N | CHAR(1) |
| 117 | 분쟁 사유 | Dispute Reason | Sebab Pertikaian | DOUBLE_CHARGE, TAG_MALFUNCTION, ... | VARCHAR(50) |
| 118 | 분쟁 제출일 | Dispute Date | Tarikh Pertikaian | YYYY-MM-DD | DATE |
| 119 | 분쟁 상태 | Dispute Status | Status Pertikaian | OPEN, UNDER_REVIEW, RESOLVED, REJECTED | VARCHAR(20) |
| 120 | 환불 여부 | Refund | Pengembalian Dana | Y/N | CHAR(1) |
| 121 | 환불액 | Refund Amount | Jumlah Pengembalian Dana | MYR 단위 | DECIMAL(10,2) |
| 122 | 환불일 | Refund Date | Tarikh Pengembalian Dana | YYYY-MM-DD | DATE |
| 123 | 환불 방식 | Refund Method | Kaedah Pengembalian Dana | ORIGINAL_CARD, BANK_TRANSFER | VARCHAR(20) |
| 124 | 이중 거래 여부 | Duplicate Transaction | Transaksi Berganda | Y/N (중복 감지) | CHAR(1) |
| 125 | 원본 거래 ID | Original Transaction ID | ID Transaksi Asal | 이중 거래 참조 | CHAR(30) |
| 126 | 감시 플래그 | Suspicious Flag | Bendera Mencurigakan | Y/N (사기/이상 거래) | CHAR(1) |
| 127 | 감시 점수 | Risk Score | Skor Risiko | 0~100 (높을수록 고위험) | DECIMAL(5,2) |
| 128 | 감시 사유 | Suspicious Reason | Sebab Mencurigakan | UNUSUAL_PATTERN, HIGH_AMOUNT, ... | VARCHAR(100) |
| 129 | 벌금 적용 | Penalty Applied | Penalti Dikenakan | Y/N | CHAR(1) |
| 130 | 벌금액 | Penalty Amount | Jumlah Penalti | MYR 단위 | DECIMAL(10,2) |

### 섹션 D: 결제 및 정산 (Payment & Settlement) - 40 항목

| # | 한글명 | English | Bahasa Melayu | 정의 | 데이터타입 |
|---|--------|---------|----------------|------|-----------|
| 131 | 결제 ID | Payment ID | ID Pembayaran | 결제 거래 고유번호 | CHAR(30) |
| 132 | 결제 일시 | Payment Time | Waktu Pembayaran | YYYY-MM-DD HH:MM:SS | DATETIME |
| 133 | 결제 상태 | Payment Status | Status Pembayaran | PENDING, AUTHORIZED, CAPTURED, FAILED | VARCHAR(20) |
| 134 | 결제 금액 | Payment Amount | Jumlah Pembayaran | MYR 단위 | DECIMAL(15,2) |
| 135 | 통화 | Currency | Mata Uang | ISO 4217 (MYR, SGD, ...) | CHAR(3) |
| 136 | 환율 | Exchange Rate | Kadar Pertukaran | 다중 통화 시 환율 | DECIMAL(10,6) |
| 137 | 결제 게이트웨이 | Payment Gateway | Gerbang Pembayaran | MAYBANK, CIMB, PUBLIC_BANK, ... | VARCHAR(50) |
| 138 | 인증 코드 | Authorization Code | Kod Otorisasi | 결제 게이트웨이 인증번호 | VARCHAR(20) |
| 139 | 참조 번호 | Reference Number | Nombor Rujukan | 은행/게이트웨이 참조 | VARCHAR(30) |
| 140 | 거래 수수료 | Transaction Fee | Yuran Transaksi | MYR 단위 | DECIMAL(8,2) |
| 141 | 수수료율 | Fee Rate | Kadar Yuran | % | DECIMAL(5,3) |
| 142 | 결제 방법 | Payment Method | Kaedah Pembayaran | CASH, CARD, BANK_TRANSFER, E_WALLET | VARCHAR(20) |
| 143 | 카드 유형 | Card Type | Jenis Kad | DEBIT, CREDIT, PREPAID | VARCHAR(20) |
| 144 | 이체은행 | Receiving Bank | Bank Penerima | 송금받는 은행명 | VARCHAR(50) |
| 145 | 이체계좌 | Receiving Account | Akaun Penerima | 송금받는 계좌번호 | VARCHAR(50) |
| 146 | 환불 처리 | Refund Processed | Pengembalian Dana Diproses | Y/N | CHAR(1) |
| 147 | 수령 확인 | Confirmation Receipt | Resit Pengesahan | 결제 확인 영수증 | VARCHAR(255) |
| 148 | 청구서 ID | Invoice ID | ID Invois | 청구서 고유번호 | VARCHAR(30) |
| 149 | 청구일 | Invoice Date | Tarikh Invois | YYYY-MM-DD | DATE |
| 150 | 청구액 | Invoice Amount | Jumlah Invois | MYR 단위 | DECIMAL(15,2) |
| 151 | 청구 기간 | Billing Period | Tempoh Pengebilan | YYYY-MM (예: 2026-04) | VARCHAR(7) |
| 152 | 청구 주기 | Billing Cycle | Kitaran Pengebilan | MONTHLY, QUARTERLY, ANNUAL | VARCHAR(20) |
| 153 | 정산 ID | Settlement ID | ID Penyelesaian | 정산 배치 고유번호 | VARCHAR(30) |
| 154 | 정산 일자 | Settlement Date | Tarikh Penyelesaian | YYYY-MM-DD | DATE |
| 155 | 정산 기간 | Settlement Period | Tempoh Penyelesaian | 거래 포함 기간 (From~To) | VARCHAR(30) |
| 156 | 정산 금액 | Settlement Amount | Jumlah Penyelesaian | MYR 단위 | DECIMAL(18,2) |
| 157 | 정산 거래수 | Settlement Transaction Count | Bilangan Transaksi Penyelesaian | 정산 포함 거래 건수 | INT |
| 158 | 정산 상태 | Settlement Status | Status Penyelesaian | PENDING, PROCESSED, PAID, DISPUTED | VARCHAR(20) |
| 159 | 정산사 | Settlement Center | Pusat Penyelesaian | SCC 명칭 | VARCHAR(100) |
| 160 | 정산사 코드 | Settlement Center Code | Kod Pusat Penyelesaian | SCC 약칭 | VARCHAR(10) |
| 161 | 수익배분 | Revenue Share | Pembagian Pendapatan | JVC, TOC 간 배분율 | VARCHAR(100) |
| 162 | JVC 배분액 | JVC Share | Bagian JVC | MYR 단위 | DECIMAL(15,2) |
| 163 | TOC 배분액 | TOC Share | Bagian TOC | MYR 단위 | DECIMAL(15,2) |
| 164 | SCC 수수료 | SCC Fee | Yuran SCC | 정산센터 수수료 | DECIMAL(12,2) |
| 165 | 지급 상태 | Payment Submission Status | Status Penyerahan Pembayaran | SUBMITTED, VERIFIED, PAID | VARCHAR(20) |
| 166 | 지급일 | Payment Submission Date | Tarikh Penyerahan Pembayaran | YYYY-MM-DD | DATE |
| 167 | 은행 입금일 | Bank Deposit Date | Tarikh Deposit Bank | YYYY-MM-DD | DATE |
| 168 | 입금 증명 | Deposit Proof | Bukti Deposit | 은행 거래 명세 파일 | VARCHAR(255) |
| 169 | 미납 금액 | Outstanding Amount | Jumlah Belum Dibayar | 미지불 잔액 | DECIMAL(15,2) |
| 170 | 미납 기한 | Payment Due Date | Tarikh Jatuh Tempo Pembayaran | YYYY-MM-DD | DATE |
| 171 | 미납 일수 | Days Overdue | Hari Terjambak | 기한 경과 일수 | INT |

### 섹션 E: 인프라 및 운영 (Infrastructure & Operations) - 35 항목

| # | 한글명 | English | Bahasa Melayu | 정의 | 데이터타입 |
|---|--------|---------|----------------|------|-----------|
| 172 | 요금소 코드 | Plaza Code | Kod Plaza | 2자 주 + 2자 시퀀스 (예: TKL01) | VARCHAR(10) |
| 173 | 요금소명 | Plaza Name | Nama Plaza | 요금소 공식명 | VARCHAR(100) |
| 174 | 요금소 유형 | Plaza Type | Jenis Plaza | GANTRY, CONVENTIONAL, HYBRID | VARCHAR(20) |
| 175 | 운영 방식 | Operation Mode | Mod Operasi | OPEN, CLOSED, HYBRID, MLFF, SLFF | VARCHAR(20) |
| 176 | 위치 좌표 | Coordinates | Koordinat | GPS 위도/경도 | VARCHAR(50) |
| 177 | 위치 거리 | Distance to KL | Jarak ke KL | KL 기준 km 단위 | DECIMAL(8,2) |
| 178 | 운영 JVC | Operating JVC | JVC Pengoperasi | 운영 담당 사업체 | VARCHAR(50) |
| 179 | 운영 TOC | Operating TOC | TOC Pengoperasi | 운영 담당 회사 | VARCHAR(50) |
| 180 | 시설 상태 | Facility Status | Status Fasilitas | OPERATIONAL, MAINTENANCE, CLOSED | VARCHAR(20) |
| 181 | 마지막 점검일 | Last Inspection Date | Tarikh Pemeriksaan Terakhir | YYYY-MM-DD | DATE |
| 182 | 점검 주기 | Inspection Frequency | Kekerapan Pemeriksaan | DAILY, WEEKLY, MONTHLY | VARCHAR(20) |
| 183 | 차선 수 | Number of Lanes | Bilangan Lorong | 총 통행 차선 수 | TINYINT |
| 184 | 게이트 수 | Number of Gates | Bilangan Pintu | 총 게이트 센서 수 | TINYINT |
| 185 | 게이트 코드 | Gate Code | Kod Pintu | GTE001, GTE002, ... | VARCHAR(10) |
| 186 | 게이트 유형 | Gate Type | Jenis Pintu | RFID, ANPR, HYBRID, MANUAL | VARCHAR(20) |
| 187 | 게이트 상태 | Gate Status | Status Pintu | OPERATIONAL, FAULTY, MAINTENANCE | VARCHAR(20) |
| 188 | RFID 판독기 | RFID Reader | Pembaca RFID | READER_001, ... | VARCHAR(20) |
| 189 | ANPR 카메라 | ANPR Camera | Kamera ANPR | CAM_001, ... | VARCHAR(20) |
| 190 | 신호등 | Traffic Light | Lampu Isyarat | Y/N (있는지 여부) | CHAR(1) |
| 191 | 결제 단말기 | Payment Terminal | Terminal Pembayaran | POS 또는 카드 리더기 | VARCHAR(30) |
| 192 | 백업 전원 | Backup Power | Kuasa Sandaran | UPS, Generator 보유 여부 | CHAR(1) |
| 193 | 운영 직원 수 | Operating Staff Count | Bilangan Kakitangan Operasi | 상근 운영원 수 | TINYINT |
| 194 | 교대 근무 | Shift Pattern | Corak Syif | 24H, 12H_SPLIT, 8H_TRIPLE | VARCHAR(20) |
| 195 | 우천 폐쇄 여부 | Weather Closure | Penutupan Cuaca | Y/N (악천후 폐쇄 가능) | CHAR(1) |
| 196 | 소음 레벨 | Noise Level | Aras Kebisingan | dB 단위 | DECIMAL(5,1) |
| 197 | 환기 시스템 | Ventilation System | Sistem Pengudaraan | 지하/터널 시설 여부 | VARCHAR(50) |
| 198 | CCTV 카메라 수 | CCTV Cameras | Kamera CCTV | 보안 카메라 수량 | TINYINT |
| 199 | 보안 인력 | Security Personnel | Petugas Keamanan | Y/N (24시간 보안) | CHAR(1) |
| 200 | 비상 버튼 | Emergency Button | Butang Kecemasan | 비상 정지 장치 | CHAR(1) |
| 201 | 요금 테이블 코드 | Toll Rate Table | Jadual Kadar Tol | 해당 요금 정책 코드 | VARCHAR(20) |
| 202 | 기본 요금 | Base Toll | Tol Asas | 기본 단위 요금 | DECIMAL(8,2) |
| 203 | 시간대 요금 | Time-Based Rate | Kadar Berasaskan Waktu | 피크/비피크 요금 | DECIMAL(8,2) |
| 204 | 차량 유형별 요금 | Vehicle Class Rate | Kadar Mengikut Kelas | CAT별 요금 | VARCHAR(100) |
| 205 | 할인 정책 | Discount Policy | Kebijakan Diskon | 적용 할인율 규칙 | VARCHAR(255) |
| 206 | 요금 유효 기간 | Rate Effective Period | Tempoh Berkuatkuasa Kadar | From~To (YYYY-MM-DD) | VARCHAR(30) |

### 섹션 F: 거버넌스 및 규정 (Governance & Compliance) - 25 항목

| # | 한글명 | English | Bahasa Melayu | 정의 | 데이터타입 |
|---|--------|---------|----------------|------|-----------|
| 207 | JVC 코드 | JVC Code | Kod JVC | JVC 약칭 | VARCHAR(10) |
| 208 | JVC명 | JVC Name | Nama JVC | 사업 시행사 공식명 | VARCHAR(100) |
| 209 | JVC 등록번호 | JVC Registration No | No. Pendaftaran JVC | 회사 등록번호 | VARCHAR(30) |
| 210 | JVC 설립일 | JVC Establishment Date | Tarikh Penubuhan JVC | YYYY-MM-DD | DATE |
| 211 | TOC 코드 | TOC Code | Kod TOC | TOC 약칭 | VARCHAR(10) |
| 212 | TOC명 | TOC Name | Nama TOC | 운영사 공식명 | VARCHAR(100) |
| 213 | TOC 등록번호 | TOC Registration No | No. Pendaftaran TOC | 회사 등록번호 | VARCHAR(30) |
| 214 | SCC 코드 | SCC Code | Kod SCC | SCC 약칭 | VARCHAR(10) |
| 215 | SCC명 | SCC Name | Nama SCC | 정산센터 공식명 | VARCHAR(100) |
| 216 | SCC 은행 계좌 | SCC Bank Account | Akaun Bank SCC | 정산금 수령 계좌 | VARCHAR(50) |
| 217 | 콘세션 수여자 | Concessionaire | Pemegang Konsesi | 국가/정부 기관 | VARCHAR(100) |
| 218 | 콘세션 계약 번호 | Concession Contract No | No. Kontrak Konsesi | 계약서 식별자 | VARCHAR(50) |
| 219 | 콘세션 시작일 | Concession Start Date | Tarikh Mula Konsesi | YYYY-MM-DD | DATE |
| 220 | 콘세션 종료일 | Concession End Date | Tarikh Akhir Konsesi | YYYY-MM-DD | DATE |
| 221 | 규정 코드 | Regulation Code | Kod Peraturan | 적용 법률/규정 | VARCHAR(30) |
| 222 | 규정명 | Regulation Name | Nama Peraturan | 규정 공식명 | VARCHAR(100) |
| 223 | 감시 수준 | Audit Level | Aras Audit | STATUTORY, INTERNAL, VENDOR | VARCHAR(20) |
| 224 | 감시 빈도 | Audit Frequency | Kekerapan Audit | MONTHLY, QUARTERLY, ANNUAL | VARCHAR(20) |
| 225 | 마지막 감시일 | Last Audit Date | Tarikh Audit Terakhir | YYYY-MM-DD | DATE |
| 226 | 감시 결과 | Audit Result | Hasil Audit | PASS, PASS_WITH_NOTES, FAIL | VARCHAR(20) |
| 227 | 데이터 보호 정책 | Data Protection Policy | Kebijakan Perlindungan Data | PDPA 준수 여부 | CHAR(1) |
| 228 | 감사 로그 보관 기간 | Audit Log Retention | Tempoh Penyimpanan Log Audit | 일수 단위 | INT |
| 229 | 규정 위반 여부 | Compliance Violation | Pelanggaran Kepatuhan | Y/N | CHAR(1) |
| 230 | 위반 기록 | Violation Record | Rekod Pelanggaran | 위반 사항 기술 | TEXT |
| 231 | 시정 조치 | Corrective Action | Tindakan Perbaikan | 시정 계획 | TEXT |

---

## 코드 마스터 (Code Master)

### A. 거래 상태 코드 (Transaction Status)

| 코드 | 한글명 | English | Bahasa Melayu | 설명 |
|------|--------|---------|----------------|------|
| TXN001 | 대기중 | Pending | Tertunda | 게이트에서 인식, 미결제 |
| TXN002 | 완료 | Completed | Selesai | 결제 성공, 통행 허가 |
| TXN003 | 실패 | Failed | Gagal | 결제 거절 또는 기술 오류 |
| TXN004 | 취소 | Cancelled | Dibatalkan | 사용자 또는 운영자 취소 |
| TXN005 | 분쟁중 | Disputed | Dipertikaikan | 고객 분쟁 신청 |
| TXN006 | 환불 | Refunded | Dikembalikan | 환불 처리 완료 |
| TXN007 | 기한만료 | Expired | Kedaluwarsa | 결제 기한 초과 |
| TXN008 | 보류 | Held | Ditahan | 사기 위험으로 보류 |

### B. 계정 상태 코드 (Account Status)

| 코드 | 한글명 | English | Bahasa Melayu |
|------|--------|---------|----------------|
| ACC001 | 활성 | Active | Aktif |
| ACC002 | 비활성 | Inactive | Tidak Aktif |
| ACC003 | 일시중지 | Suspended | Ditangguhkan |
| ACC004 | 폐쇄 | Closed | Ditutup |
| ACC005 | 미검증 | Unverified | Tidak Disahkan |

### C. 차량 유형 코드 (Vehicle Class)

| 코드 | 한글명 | English | Bahasa Melayu | 예시 |
|------|--------|---------|----------------|------|
| CAT-A | 1축 소형 | 2-Axle Car | Kereta 2 Paksi | Sedan, Hatchback |
| CAT-B | 2축 중형 | 2-Axle Truck | Lori 2 Paksi | Pickup, Van |
| CAT-C | 3축 화물 | 3-Axle Truck | Lori 3 Paksi | Heavy Truck |
| CAT-D | 버스 | Bus | Bas | 버스, 미니버스 |
| CAT-E | 오토바이 | Motorcycle | Motosikal | 스쿠터, 바이크 |
| CAT-F | 특수 | Special | Khas | 트레일러, 크레인 차 |

### D. 결제 방식 코드 (Payment Method)

| 코드 | 한글명 | English | Bahasa Melayu |
|------|--------|---------|----------------|
| PAY001 | 현금 | Cash | Wang Tunai |
| PAY002 | 카드 | Card | Kad |
| PAY003 | 태그 | RFID Tag | Tag RFID |
| PAY004 | 은행이체 | Bank Transfer | Pindahan Bank |
| PAY005 | 전자지갑 | E-Wallet | Dompet E |
| PAY006 | 수표 | Cheque | Cek |
| PAY007 | 선금 | Prepaid | Prabayar |

### E. 상태/행동 플래그 (Status Flags)

| 코드 | 의미 | 용도 |
|------|------|------|
| Y | 예 / 참 | 이진 조건 (블랙리스트, VIP, ...) |
| N | 아니오 / 거짓 | 이진 조건 (기본값) |
| P | 대기중 | 처리 대기 상태 |
| A | 승인 | 승인됨 |
| R | 거절 | 거절됨 |
| H | 보류 | 잠시 보류 |

---

## 검증 규칙 (Validation Rules)

### 계정 및 고객

| 필드 | 검증 규칙 | 예시 |
|------|---------|------|
| **계정 번호** | 20자 영숫자, 고유 | ACCT20260401001234 |
| **신분증** | 길이 6~30, 유효한 IC/Passport | 123456789123 |
| **전화번호** | +60으로 시작, 9~15자 | +601234567890 |
| **이메일** | 유효한 이메일 형식 | user@domain.com |
| **우편번호** | Malaysia 5자리 | 50000 |
| **주/도 코드** | 2자 코드 (KL, SLG, JHR, ...) | KL, SLG |
| **생년월일** | 18세 이상 (대원칙) | 1990-01-15 |

### 차량 및 태그

| 필드 | 검증 규칙 | 예시 |
|------|---------|------|
| **차량 번호판** | Malaysia 형식 (3자+4숫자 또는 변형) | KL123ABC, AAA1234 |
| **VIN** | 17자 고유 영숫자 | WBADW5444GF279481 |
| **태그 번호** | 20자 고유 코드 | TG-202604-001-ABC |
| **태그 상태** | ACTIVE, INACTIVE, LOST, DAMAGED | ACTIVE |
| **태그 만료일** | >= 발급일 + 5년 | 2031-04-01 |
| **차량 무게** | 500~50,000 kg | 1500 |
| **차축 수** | 1~6 | 2 |

### 거래 및 통행

| 필드 | 검증 규칙 | 예시 |
|------|---------|------|
| **거래 ID** | 30자 고유, 타임스탬프 포함 | TXN20260401123456789ABCDE |
| **거래 시간** | YYYY-MM-DD HH:MM:SS.mmm | 2026-04-01 14:30:45.123 |
| **거래 금액** | 0.01~99,999.99 MYR | 12.50 |
| **할인율** | 0~100% | 10.00 |
| **차선 번호** | 1~20 | 1 |
| **요금소 코드** | 2자+2숫자 | TKL01 |
| **거리** | 0.1~999.9 km | 45.5 |

### 결제 및 정산

| 필드 | 검증 규칙 | 예시 |
|------|---------|------|
| **결제 금액** | > 0, 최대 999,999.99 | 500.00 |
| **카드 번호** | 마스킹됨, 마지막 4자리만 표시 | ****1234 |
| **카드 유효기간** | MM/YY, 미래 날짜 | 06/28 |
| **CVV** | 비저장 (절대 저장 금지) | - |
| **청구서 ID** | 고유, 형식: INV-YYYYMM-##### | INV-202604-00001 |
| **정산 기간** | YYYY-MM 형식 | 2026-04 |
| **미납 기한** | >= 청구일 + 14일 | 2026-04-15 |

### 인프라 및 운영

| 필드 | 검증 규칙 | 예시 |
|------|---------|------|
| **요금소 코드** | 2자(주) + 2숫자 + 선택: A/B/C | TKL01, SLG02A |
| **게이트 코드** | GTE + 3숫자 | GTE001 |
| **GPS 좌표** | 위도(-90~90), 경도(-180~180) | 3.1357,101.6880 |
| **차선 수** | 1~20 | 8 |
| **게이트 수** | 1~100 | 12 |
| **기본 요금** | 0.50~50.00 MYR | 3.50 |

---

## 메타데이터 카탈로그 (Metadata Catalog)

### 데이터 엔티티 맵핑

| 엔티티 | 테이블명 | 레코드 수 (Est.) | 주 키 | 업데이트 빈도 | 소유팀 |
|--------|----------|----------------|-------|----------------|--------|
| Account | ACCOUNT | 5M+ | ACCT_ID | DAILY | Customer Service |
| Vehicle | VEHICLE | 8M+ | VEH_ID | DAILY | Vehicle Registry |
| RFID Tag | TAG_MASTER | 8M+ | TAG_ID | WEEKLY | Operations |
| Transaction | TRANSACTION_LOG | 100M+/month | TXN_ID | REALTIME | Operations |
| Payment | PAYMENT | 50M+/month | PAY_ID | REALTIME | Finance |
| Toll Rate | TOLL_RATE | 500+ | RATE_ID | MONTHLY | Revenue |
| Toll Plaza | TOLL_PLAZA | 50+ | PLAZA_ID | QUARTERLY | Infrastructure |
| Toll Gate | TOLL_GATE | 500+ | GATE_ID | QUARTERLY | Operations |
| Toll Lane | TOLL_LANE | 5,000+ | LANE_ID | QUARTERLY | Operations |
| Violation Log | VIOLATION_LOG | 10M+/year | VIOL_ID | REALTIME | Compliance |
| Invoice | INVOICE | 100K+/month | INV_ID | DAILY | Finance |
| Settlement | SETTLEMENT | 1K+/month | SETTLE_ID | MONTHLY | Finance |
| JVC Master | JVC_MASTER | 5~10 | JVC_ID | ANNUALLY | Executive |
| TOC Master | TOC_MASTER | 20~30 | TOC_ID | SEMI-ANNUALLY | Operations |
| SCC Master | SCC_MASTER | 3~5 | SCC_ID | ANNUALLY | Finance |

### 데이터 품질 메트릭

| 메트릭 | 목표 | 빈도 | 책임팀 |
|--------|------|------|--------|
| 완성도 (Completeness) | 99.5% | DAILY | Data Governance |
| 정확도 (Accuracy) | 99.8% | WEEKLY | Operations |
| 일관성 (Consistency) | 100% | REALTIME | Database Team |
| 적시성 (Timeliness) | <5초 | REALTIME | Infrastructure |
| 고유성 (Uniqueness) | 100% | DAILY | Database Team |

### 통합 포인트 (Integration Points)

| 시스템 | 데이터 흐름 | 형식 | 빈도 |
|--------|-----------|------|------|
| RFID Reader | TXN 수신 | JSON | REALTIME |
| ANPR Camera | VEH 인식 | JSON | REALTIME |
| Payment Gateway | PAY 처리 | XML/JSON | REALTIME |
| Banking System | SETTLE 입금 | SWIFT/SFTP | DAILY |
| Reporting System | 분석 데이터 | CSV/XLSX | MONTHLY |

---

## 참고 (Reference)

**문서 관련 연락처:**
- Data Governance Lead: [Team Lead Name]
- Metadata Steward: [Steward Name]
- Technical Data Architect: [Architect Name]

**개정 이력:**
- v1.0 (2026-04-01): Initial Release

**다음 단계:**
- 추가 용어 확장 (250+ → 500+)
- 데이터 딕셔너리 통합
- API 스키마 매핑
- 데이터 계보(Lineage) 정의
