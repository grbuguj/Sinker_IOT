from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.db import SessionLocal
from src.models.sensor import SensorData

router = APIRouter()

# DB 세션 가져오기
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/sensor")
def receive_sensor(moisture: float, tilt: float, vibration: float, db: Session = Depends(get_db)):
    data = SensorData(
        moisture=moisture,
        tilt=tilt,
        vibration=vibration
    )
    db.add(data)
    db.commit()
    db.refresh(data)

    return {"status": "OK", "inserted_id": data.id}
