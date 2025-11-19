"""
데이터베이스 설정 및 세션 관리
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DB_URL

engine = create_engine(
    DB_URL,
    echo=True,        # SQL 출력 (개발 단계에서 유용)
    future=True,
    pool_pre_ping=True,  # 연결 상태 확인
    pool_recycle=3600    # 1시간마다 연결 재생성
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI Dependency로 사용할 DB 세션 생성 함수
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
