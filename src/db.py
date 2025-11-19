from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DB_URL = "mysql+pymysql://root:1234@localhost:3306/sinker_iot"

engine = create_engine(
    DB_URL,
    echo=True,        # SQL 출력 (개발 단계에서 유용)
    future=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
