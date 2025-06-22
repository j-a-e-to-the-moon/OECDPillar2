from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import calculations

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="OECD Pillar 2 계산 API",
    description="OECD Pillar 2 관련 세율 및 세액 계산을 위한 RESTful API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 실제 배포 시에는 특정 도메인으로 제한
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(calculations.router, prefix="/api", tags=["calculations"])

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "OECD Pillar 2 계산 API에 오신 것을 환영합니다!",
        "description": "유효세율, 소득포함비율, UTPR 계산 서비스를 제공합니다",
        "docs": "/docs",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "message": "계산 API가 정상적으로 동작 중입니다."} 