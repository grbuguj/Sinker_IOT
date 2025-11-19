"""
WebSocket 연결 관리
"""
from fastapi import WebSocket
from typing import Set
import json


class ConnectionManager:
    """
    WebSocket 연결을 관리하는 클래스
    """
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        """
        새로운 WebSocket 연결 수락
        """
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        """
        WebSocket 연결 종료
        """
        self.active_connections.discard(websocket)
    
    async def broadcast(self, message: dict):
        """
        모든 연결된 클라이언트에게 메시지 브로드캐스트
        """
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"WebSocket 전송 실패: {e}")
                disconnected.add(connection)
        
        # 연결 실패한 클라이언트 제거
        for conn in disconnected:
            self.disconnect(conn)


# 전역 ConnectionManager 인스턴스
manager = ConnectionManager()
