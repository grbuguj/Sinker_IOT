from fastapi import FastAPI
from .db import Base, engine
from .models import SensorData

app = FastAPI()

# DB 테이블 자동 생성
Base.metadata.create_all(bind=engine)

@app.get("/")
def home():
    return {"message": "Sinker IoT Server Running"}
