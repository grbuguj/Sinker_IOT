"""
센서 클라이언트 - 데이터 수집 및 서버 전송
"""

import time
import requests
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import sys
import signal

from sensor_manager import SensorManager
from config import (
    SERVER_URL,
    SEND_INTERVAL,
    MAX_RETRIES,
    RETRY_DELAY,
    CONNECTION_TIMEOUT,
    LOG_FILE,
    LOG_LEVEL,
    LOG_MAX_SIZE,
    LOG_BACKUP_COUNT
)


class SensorClient:
    """
    센서 데이터 수집 및 서버 전송 클라이언트
    """
    
    def __init__(self):
        """
        클라이언트 초기화
        """
        # 로깅 설정
        self.setup_logging()
        
        self.logger.info("=" * 60)
        self.logger.info("🚀 센서 클라이언트 시작")
        self.logger.info("=" * 60)
        self.logger.info(f"서버 URL: {SERVER_URL}")
        self.logger.info(f"전송 간격: {SEND_INTERVAL}초")
        
        # 센서 매니저 초기화
        try:
            self.sensor_manager = SensorManager()
            self.logger.info("✅ 센서 매니저 초기화 완료")
        except Exception as e:
            self.logger.error(f"❌ 센서 매니저 초기화 실패: {e}")
            sys.exit(1)
        
        # 통계
        self.total_sent = 0
        self.total_failed = 0
        self.running = True
        
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def setup_logging(self):
        """
        로깅 설정
        """
        self.logger = logging.getLogger("SensorClient")
        self.logger.setLevel(getattr(logging, LOG_LEVEL))
        
        # 파일 핸들러 (회전)
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_SIZE * 1024 * 1024,
            backupCount=LOG_BACKUP_COUNT
        )
        file_handler.setLevel(logging.INFO)
        
        # 콘솔 핸들러
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        
        # 포맷 설정
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def signal_handler(self, signum, frame):
        """
        시그널 핸들러 (Ctrl+C 등)
        """
        self.logger.info("\n\n🛑 종료 신호 수신")
        self.running = False
    
    def collect_data(self):
        """
        센서 데이터 수집
        Returns: dict
        """
        try:
            data = self.sensor_manager.read_all()
            data['timestamp'] = datetime.now().isoformat()
            return data
        except Exception as e:
            self.logger.error(f"⚠️ 센서 데이터 수집 실패: {e}")
            return None
    
    def send_data(self, data):
        """
        서버로 데이터 전송
        Returns: bool (성공 여부)
        """
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.post(
                    SERVER_URL,
                    json=data,
                    timeout=CONNECTION_TIMEOUT
                )
                
                if response.status_code == 200:
                    result = response.json()
                    risk_level = result.get('risk_level', 'N/A')
                    risk_text = self.get_risk_text(risk_level)
                    
                    self.logger.info(
                        f"✅ 전송 성공 [{self.total_sent + 1}] - "
                        f"위험도: {risk_text}"
                    )
                    return True
                else:
                    self.logger.warning(
                        f"⚠️ 서버 응답 오류 (시도 {attempt}/{MAX_RETRIES}): "
                        f"Status {response.status_code}"
                    )
            
            except requests.exceptions.Timeout:
                self.logger.warning(
                    f"⏱️ 타임아웃 (시도 {attempt}/{MAX_RETRIES})"
                )
            
            except requests.exceptions.ConnectionError:
                self.logger.warning(
                    f"🔌 연결 실패 (시도 {attempt}/{MAX_RETRIES})"
                )
            
            except Exception as e:
                self.logger.error(
                    f"❌ 전송 오류 (시도 {attempt}/{MAX_RETRIES}): {e}"
                )
            
            # 재시도 전 대기
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
        
        return False
    
    def get_risk_text(self, risk_level):
        """
        위험도 텍스트 변환
        """
        risk_map = {
            0: "✅ 정상",
            1: "⚠️ 주의",
            2: "🚨 위험",
            "N/A": "❓ 알 수 없음"
        }
        return risk_map.get(risk_level, "❓ 알 수 없음")
    
    def print_statistics(self):
        """
        통계 출력
        """
        success_rate = 0
        if self.total_sent + self.total_failed > 0:
            success_rate = (self.total_sent / (self.total_sent + self.total_failed)) * 100
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("📊 통계")
        self.logger.info("=" * 60)
        self.logger.info(f"총 전송 성공: {self.total_sent}회")
        self.logger.info(f"총 전송 실패: {self.total_failed}회")
        self.logger.info(f"성공률: {success_rate:.1f}%")
        self.logger.info("=" * 60)
    
    def run(self):
        """
        메인 루프 실행
        """
        self.logger.info("\n▶️ 데이터 수집 및 전송 시작\n")
        
        try:
            while self.running:
                # 센서 데이터 수집
                data = self.collect_data()
                
                if data:
                    # 데이터 로깅
                    self.logger.info(
                        f"📡 수분: {data['moisture']:.1f} | "
                        f"진동: {data['vibration_raw']:.3f} | "
                        f"가속도 Z: {data['accel']['z']:.3f}"
                    )
                    
                    # 서버로 전송
                    if self.send_data(data):
                        self.total_sent += 1
                    else:
                        self.total_failed += 1
                        self.logger.error("❌ 최대 재시도 횟수 초과, 다음 사이클에서 재시도")
                
                # 대기
                time.sleep(SEND_INTERVAL)
        
        except Exception as e:
            self.logger.error(f"❌ 예상치 못한 오류: {e}")
        
        finally:
            self.logger.info("\n🛑 센서 클라이언트 종료")
            self.print_statistics()


def main():
    """
    메인 함수
    """
    client = SensorClient()
    client.run()


if __name__ == "__main__":
    main()
