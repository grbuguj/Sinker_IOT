#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
센서 클라이언트 - 서버로 데이터 전송
동료의 정상 작동 코드 기준으로 리팩토링

실행 방법:
    python3 sensor_client.py
    
종료:
    Ctrl+C
"""

import time
import requests
from datetime import datetime
from sensor_manager import SensorManager
from config import (
    SERVER_URL,
    SEND_INTERVAL,
    MAX_RETRIES,
    RETRY_DELAY,
    CONNECTION_TIMEOUT
)


class SensorClient:
    """센서 데이터 수집 및 서버 전송 클라이언트"""
    
    def __init__(self):
        """클라이언트 초기화"""
        print("=" * 60)
        print("🚀 센서 클라이언트 시작")
        print("=" * 60)
        print(f"서버 URL: {SERVER_URL}")
        print(f"전송 간격: {SEND_INTERVAL}초")
        print(f"최대 재시도: {MAX_RETRIES}회")
        print("=" * 60)
        
        # 센서 매니저 초기화
        self.sensor_manager = SensorManager()
        
        # 통계
        self.total_sent = 0
        self.total_failed = 0
        self.running = True
    
    def collect_data(self):
        """
        센서 데이터 수집
        Returns:
            dict: 센서 데이터
        """
        data = self.sensor_manager.read_all()
        data['timestamp'] = datetime.now().isoformat()
        return data
    
    def send_data(self, data):
        """
        서버로 데이터 전송 (재시도 로직 포함)
        Args:
            data: 전송할 센서 데이터
        Returns:
            bool: 성공 여부
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
                    
                    # 전송 성공 로그
                    print(f"✅ [{self.total_sent + 1}] 전송 성공 - 위험도: {risk_level}")
                    
                    # 진동 감지 시 즉시 경고
                    if data.get('vibration', 0) == 1:
                        print("\n🚨🚨 [즉시 경고] 진동이 감지되었습니다! 🚨🚨\n")
                    
                    return True
                else:
                    print(f"⚠️ 서버 오류 (시도 {attempt}/{MAX_RETRIES}): Status {response.status_code}")
            
            except requests.exceptions.Timeout:
                print(f"⏱️ 타임아웃 (시도 {attempt}/{MAX_RETRIES})")
            
            except requests.exceptions.ConnectionError:
                print(f"🔌 연결 실패 (시도 {attempt}/{MAX_RETRIES}) - 서버가 실행 중인지 확인하세요")
            
            except Exception as e:
                print(f"❌ 전송 오류 (시도 {attempt}/{MAX_RETRIES}): {e}")
            
            # 재시도 전 대기
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
        
        return False
    
    def print_statistics(self):
        """통계 출력"""
        total = self.total_sent + self.total_failed
        success_rate = (self.total_sent / total * 100) if total > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 전송 통계")
        print("=" * 60)
        print(f"총 전송 성공: {self.total_sent}회")
        print(f"총 전송 실패: {self.total_failed}회")
        print(f"성공률: {success_rate:.1f}%")
        print("=" * 60)
    
    def run(self):
        """메인 루프 실행"""
        print("\n▶️ 데이터 수집 및 전송 시작\n")
        
        try:
            while self.running:
                # 센서 데이터 수집
                data = self.collect_data()
                
                # 간단한 로그 출력
                print(
                    f"📡 수분: {data['moisture']} | "
                    f"진동: {data['vibration']} | "
                    f"가속도 Z: {data['accel']['z']:.2f}",
                    end=" "
                )
                
                # 서버로 전송
                if self.send_data(data):
                    self.total_sent += 1
                else:
                    self.total_failed += 1
                    print("❌ 최대 재시도 초과")
                
                # 대기
                time.sleep(SEND_INTERVAL)
        
        except KeyboardInterrupt:
            print("\n\n🛑 사용자가 종료를 요청했습니다")
        
        except Exception as e:
            print(f"\n❌ 예상치 못한 오류: {e}")
        
        finally:
            print("\n🛑 센서 클라이언트 종료")
            self.sensor_manager.cleanup()
            self.print_statistics()


def main():
    """메인 함수"""
    client = SensorClient()
    client.run()


if __name__ == "__main__":
    main()
