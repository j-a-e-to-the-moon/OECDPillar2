# OECD Pillar 2 계산 API

OECD Pillar 2 관련 세율 및 세액 계산을 위한 FastAPI 기반 RESTful API 서비스입니다.

## 🚀 주요 기능

[Input]
- **direct ownership ratio**
- **direct controller**
- **entities information**
- **jurisdictional pillar 2 implementation information**
[Output]
- **Direct Controller Recommendation**
- **Safe Harbours Calculation Group Classification**
- **ETR Calculation Group Classification**
- **IIR Parent Type Classification**
- **Income Inclusion Ratio**: 법인별 유효세율 계산 및 저세율 여부 판단
- **UTPR taxed Ratio**

[Input]
- **Income Inclusion Ratio**
- **UTPR taxed Ratio**
- **Net GloBE Income of ETR Calculation Groups**
- **Adjusted Covered Taxes of ETR Calculation Groups**
- **Jurisdictional UTPR Information**
- **QDMTT calculation amount by ETR Groups**

[Output]
- **topup tax amount paid by parent entities by IIR**
- **topup tax amount paid by each entities by UTPR**

- **API 문서화**: Swagger UI 자동 생성

## 📋 API 엔드포인트

### 계산 서비스 (Calculations)
- `POST /api/calculate-structure` - Pillar 2 Calculation Structure(Grouping,IIR,UTPR)
- `POST /api/topup-tax-amount` - Calculate and distribute topup tax by IIR and UTPR

## 🛠️ 설치 및 실행

### 1. 패키지 설치
```bash
pip install -r requirements.txt
```

### 2. 서버 실행
```bash
# 방법 1: run.py 사용 (권장)
python run.py

# 방법 2: uvicorn 직접 사용
uvicorn app.api:app --host 0.0.0.0 --port 8000 --reload

# 방법 3: main.py 사용
python main.py
```

### 3. API 문서 확인
서버 실행 후 다음 URL에서 API 문서를 확인할 수 있습니다:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📊 사용 예시

### 1. 유효세율 계산
```bash
curl -X POST "http://localhost:8000/api/effective-tax-rate" \
     -H "Content-Type: application/json" \
     -d '{
       "entities": [
         {
           "name": "법인A",
           "country": "한국",
           "entity_type": "subsidiary",
           "revenue": 1000000,
           "profit": 100000,
           "tax_paid": 10000,
           "employees": 50
         }
       ],
       "minimum_tax_rate": 0.15
     }'
```

### 2. 소득 포함 비율 계산
```bash
curl -X POST "http://localhost:8000/api/income-inclusion-ratio" \
     -H "Content-Type: application/json" \
     -d '{
       "low_taxed_income": 50000,
       "total_income": 200000,
       "ownership_percentage": 0.7
     }'
```

### 3. UTPR 계산
```bash
curl -X POST "http://localhost:8000/api/utpr-calculation" \
     -H "Content-Type: application/json" \
     -d '{
       "entity_name": "법인B",
       "utpr_percentage": 0.3,
       "qualifying_income": 80000
     }'
```

## 📁 프로젝트 구조

```
OECDPillar2/
├── app/
│   ├── __init__.py
│   ├── api.py              # FastAPI 앱 설정
│   ├── config.py           # 환경 설정
│   ├── models.py           # Pydantic 모델 (계산 관련)
│   └── routers/
│       ├── __init__.py
│       └── calculations.py # 계산 관련 라우터
├── main.py                 # 서버 진입점
├── run.py                  # 서버 실행 스크립트
├── requirements.txt        # 의존성 패키지
└── README.md              # 프로젝트 문서
```

## 🧮 계산 공식

### Refer to Calculation Logic.md

## 🌏 OECD Pillar 2 개요

OECD Pillar 2는 글로벌 다국적 기업의 최소세율을 15%로 보장하는 국제 조세 규칙입니다:

- **시행일**: 2024년 1월 1일
- **적용 대상**: 연간 수익 7억 5천만 유로 이상의 다국적 기업
- **최소세율**: 15%
- **주요 구성요소**:
  - GloBE Rules (Global Anti-Base Erosion Rules)
  - Income Inclusion Rule (IIR)
  - Under-Taxed Payments Rule (UTPR)

## 📝 라이선스

이 프로젝트는 MIT 라이선스를 따릅니다.
