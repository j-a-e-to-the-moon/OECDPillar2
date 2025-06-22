#!/usr/bin/env python3
"""
OECD Pillar2 FastAPI 서버 실행 스크립트
"""

import uvicorn
from app.config import settings

if __name__ == "__main__":
    print(f"🚀 OECD Pillar2 API 서버를 시작합니다...")
    print(f"📍 서버 주소: http://{settings.API_HOST}:{settings.API_PORT}")
    print(f"📚 API 문서: http://{settings.API_HOST}:{settings.API_PORT}/docs")
    print(f"🔧 디버그 모드: {settings.DEBUG}")
    
    uvicorn.run(
        "app.api:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info"
    ) 