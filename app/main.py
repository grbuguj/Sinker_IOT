"""
FastAPI 메인 애플리케이션
"""
from fastapi import FastAPI, Depends, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, List
import io
import csv
import pytz

from app.database import engine, get_db, Base
from app.models import SensorData, Threshold
from app.schemas import (
    SensorDataCreate, SensorDataRead, 
    ThresholdRead, ThresholdUpdate
)
from app.crud import (
    create_sensor_data, get_latest_sensor_data,
    get_sensor_history, get_all_thresholds, upsert_threshold
)
from app.websocket_manager import manager
from app.config import DEFAULT_THRESHOLDS, TIMEZONE

# FastAPI 앱 생성
app = FastAPI(
    title="IoT 기반 소규모 싱크홀 조기 경보 시스템",
    description="센서 데이터 수집 및 실시간 모니터링 시스템",
    version="1.0.0"
)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# 데이터베이스 초기화
@app.on_event("startup")
async def startup_event():
    """
    서버 시작 시 실행
    - 테이블 생성
    - 기본 임계값 설정
    """
    # 테이블 생성
    Base.metadata.create_all(bind=engine)
    
    # 기본 임계값 초기화
    db = next(get_db())
    try:
        for name, value in DEFAULT_THRESHOLDS.items():
            existing = db.query(Threshold).filter(Threshold.name == name).first()
            if not existing:
                threshold = Threshold(name=name, value=value)
                db.add(threshold)
        db.commit()
        print("✅ 데이터베이스 초기화 완료")
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        db.rollback()
    finally:
        db.close()


# ============================================
# 웹 페이지 라우트
# ============================================

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """실시간 대시보드 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/history_page", response_class=HTMLResponse)
async def history_page(request: Request):
    """이력 조회 페이지"""
    return templates.TemplateResponse("history.html", {"request": request})


@app.get("/config_page", response_class=HTMLResponse)
async def config_page(request: Request):
    """임계값 설정 페이지"""
    return templates.TemplateResponse("config.html", {"request": request})


# ============================================
# REST API 엔드포인트
# ============================================

@app.post("/sensor", response_model=dict)
async def receive_sensor_data(data: SensorDataCreate, db: Session = Depends(get_db)):
    """
    센서 데이터 수신 및 저장
    - 위험도 계산
    - DB 저장
    - WebSocket 브로드캐스트
    """
    try:
        # 데이터 저장
        db_data = create_sensor_data(db, data)
        
        # WebSocket으로 브로드캐스트 (Pydantic v2 호환)
        sensor_read = SensorDataRead.model_validate(db_data)
        await manager.broadcast(sensor_read.model_dump(mode='json'))
        
        return {"status": "ok", "id": db_data.id, "risk_level": db_data.risk_level}
    
    except Exception as e:
        print(f"❌ 센서 데이터 저장 실패: {e}")
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}


@app.get("/latest", response_model=Optional[SensorDataRead])
async def get_latest(db: Session = Depends(get_db)):
    """
    최신 센서 데이터 1건 조회
    """
    data = get_latest_sensor_data(db)
    return data


@app.get("/api/history", response_model=List[SensorDataRead])
async def get_history(
    minutes: Optional[int] = Query(None, description="최근 N분 데이터"),
    start: Optional[str] = Query(None, description="시작 시각 (ISO 8601)"),
    end: Optional[str] = Query(None, description="종료 시각 (ISO 8601)"),
    db: Session = Depends(get_db)
):
    """
    센서 데이터 이력 조회
    """
    start_dt = None
    end_dt = None
    
    if start:
        start_dt = datetime.fromisoformat(start)
    if end:
        end_dt = datetime.fromisoformat(end)
    
    data_list = get_sensor_history(db, minutes=minutes, start=start_dt, end=end_dt)
    return data_list


@app.get("/api/history/csv")
async def download_history_csv(
    minutes: Optional[int] = Query(None, description="최근 N분 데이터"),
    start: Optional[str] = Query(None, description="시작 시각 (ISO 8601)"),
    end: Optional[str] = Query(None, description="종료 시각 (ISO 8601)"),
    db: Session = Depends(get_db)
):
    """
    센서 데이터 이력 CSV 다운로드
    """
    start_dt = None
    end_dt = None
    
    if start:
        start_dt = datetime.fromisoformat(start)
    if end:
        end_dt = datetime.fromisoformat(end)
    
    data_list = get_sensor_history(db, minutes=minutes, start=start_dt, end=end_dt, limit=10000)
    
    # CSV 생성
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 헤더
    writer.writerow([
        "created_at", "moisture", 
        "accel_x", "accel_y", "accel_z",
        "gyro_x", "gyro_y", "gyro_z",
        "vibration_raw", "risk_level"
    ])
    
    # 데이터 행
    for data in reversed(data_list):  # 오래된 것부터
        writer.writerow([
            data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            data.moisture,
            data.accel_x, data.accel_y, data.accel_z,
            data.gyro_x, data.gyro_y, data.gyro_z,
            data.vibration_raw,
            data.risk_level
        ])
    
    output.seek(0)
    
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=sensor_history.csv"}
    )


# ============================================
# 임계값 관리 API
# ============================================

@app.get("/config/api/thresholds", response_model=List[ThresholdRead])
async def get_thresholds(db: Session = Depends(get_db)):
    """
    모든 임계값 조회
    """
    return get_all_thresholds(db)


@app.post("/config/api/thresholds", response_model=ThresholdRead)
async def update_threshold(threshold: ThresholdUpdate, db: Session = Depends(get_db)):
    """
    임계값 업데이트 또는 생성
    """
    return upsert_threshold(db, threshold.name, threshold.value)


# ============================================
# WebSocket 엔드포인트
# ============================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    실시간 데이터 스트리밍을 위한 WebSocket 엔드포인트
    """
    await manager.connect(websocket)
    
    try:
        while True:
            # 클라이언트로부터 메시지 대기 (연결 유지)
            await websocket.receive_text()
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("WebSocket 연결 종료")


# ============================================
# 헬스체크
# ============================================

@app.get("/health")
async def health_check():
    """
    서버 상태 확인
    """
    return {"status": "healthy", "service": "sinkhole-warning-system"}
