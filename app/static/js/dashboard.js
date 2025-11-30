/**
 * 실시간 대시보드 JavaScript
 */

// 전역 변수
let ws = null;
let moistureChart = null;
let vibrationChart = null;
let tiltChart = null;
let riskScoreChart = null;
let currentMinutes = 0;

// 최대 데이터 포인트 수 (최근 50개)
const MAX_DATA_POINTS = 50;

// 위험도 임계값 (config.py와 동일)
const RISK_THRESHOLDS = {
    TILT_NORMAL: 6.0,
    TILT_DANGER: 8.0,
    MOISTURE_NORMAL: 800,
    MOISTURE_WARNING: 750,
    WEIGHT_TILT: 0.5,
    WEIGHT_MOISTURE: 0.3,
    WEIGHT_VIBRATION: 0.2,
    RISK_NORMAL_MAX: 0.3,
    RISK_WARNING_MAX: 0.6
};

// WebSocket 연결
function connectWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log('WebSocket 연결됨');
        updateConnectionStatus(true);
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        updateDashboard(data);
    };
    
    ws.onerror = (error) => {
        console.error('WebSocket 에러:', error);
        updateConnectionStatus(false);
    };
    
    ws.onclose = () => {
        console.log('WebSocket 연결 종료');
        updateConnectionStatus(false);
        
        // 3초 후 재연결 시도
        setTimeout(connectWebSocket, 3000);
    };
}

// 연결 상태 업데이트
function updateConnectionStatus(connected) {
    const statusEl = document.getElementById('connectionStatus');
    if (connected) {
        statusEl.className = 'connection-status connected';
        statusEl.textContent = '🟢 연결됨';
    } else {
        statusEl.className = 'connection-status disconnected';
        statusEl.textContent = '🔴 연결 끊김';
    }
}

// 최종 위험도 점수 계산 (프론트엔드에서 재계산)
function calculateRiskScore(moisture, accel_x, accel_y, vibration_raw) {
    // 1. 기울기 점수
    const tiltMagnitude = Math.sqrt(accel_x * accel_x + accel_y * accel_y);
    let tiltScore = 0.0;
    
    if (tiltMagnitude < RISK_THRESHOLDS.TILT_NORMAL) {
        tiltScore = 0.0;
    } else if (tiltMagnitude < RISK_THRESHOLDS.TILT_DANGER) {
        tiltScore = (tiltMagnitude - RISK_THRESHOLDS.TILT_NORMAL) / 
                    (RISK_THRESHOLDS.TILT_DANGER - RISK_THRESHOLDS.TILT_NORMAL);
    } else {
        tiltScore = 1.0;
    }
    
    // 2. 수분 점수 (역방향)
    let moistureScore = 0.0;
    
    if (moisture > RISK_THRESHOLDS.MOISTURE_NORMAL) {
        moistureScore = 0.0;
    } else if (moisture > RISK_THRESHOLDS.MOISTURE_WARNING) {
        moistureScore = (RISK_THRESHOLDS.MOISTURE_NORMAL - moisture) / 
                       (RISK_THRESHOLDS.MOISTURE_NORMAL - RISK_THRESHOLDS.MOISTURE_WARNING);
    } else {
        moistureScore = 1.0;
    }
    
    // 3. 진동 점수
    const vibrationScore = vibration_raw >= 1.0 ? 1.0 : 0.0;
    
    // 4. 최종 점수
    const finalScore = (
        RISK_THRESHOLDS.WEIGHT_TILT * tiltScore +
        RISK_THRESHOLDS.WEIGHT_MOISTURE * moistureScore +
        RISK_THRESHOLDS.WEIGHT_VIBRATION * vibrationScore
    );
    
    return finalScore;
}

// 점수로 위험도 레벨 판정
function getRiskLevelFromScore(score) {
    if (score < RISK_THRESHOLDS.RISK_NORMAL_MAX) {
        return 0; // 정상
    } else if (score < RISK_THRESHOLDS.RISK_WARNING_MAX) {
        return 1; // 주의
    } else {
        return 2; // 위험
    }
}

// 대시보드 업데이트
function updateDashboard(data) {
    // 센서 값 업데이트
    document.getElementById('moistureValue').textContent = data.moisture.toFixed(1);
    document.getElementById('vibrationValue').textContent = data.vibration_raw.toFixed(2);
    document.getElementById('accelXValue').textContent = data.accel_x.toFixed(3);
    document.getElementById('accelYValue').textContent = data.accel_y.toFixed(3);
    document.getElementById('accelZValue').textContent = data.accel_z.toFixed(3);
    document.getElementById('gyroXValue').textContent = data.gyro_x.toFixed(3);
    document.getElementById('gyroYValue').textContent = data.gyro_y.toFixed(3);
    document.getElementById('gyroZValue').textContent = data.gyro_z.toFixed(3);
    
    // 타임스탬프 업데이트
    const timestamp = new Date(data.created_at);
    document.getElementById('timestampValue').textContent = timestamp.toLocaleString('ko-KR');
    
    // 기울기 magnitude 계산 (sqrt(x^2 + y^2))
    const tiltMagnitude = Math.sqrt(
        data.accel_x * data.accel_x + 
        data.accel_y * data.accel_y
    );
    
    // 최종 위험도 점수 계산
    const riskScore = calculateRiskScore(
        data.moisture,
        data.accel_x,
        data.accel_y,
        data.vibration_raw
    );
    
    // 점수로 위험도 레벨 판정 (프론트엔드에서!)
    const riskLevel = getRiskLevelFromScore(riskScore);
    
    // 위험도 배지 업데이트 (프론트 계산값 사용!)
    updateStatusBadge(riskLevel);
    
    // 그래프 업데이트
    addDataToChart(moistureChart, timestamp, data.moisture);
    addDataToChart(vibrationChart, timestamp, data.vibration_raw);
    addDataToChart(tiltChart, timestamp, tiltMagnitude);
    addDataToChart(riskScoreChart, timestamp, riskScore);
}

// 위험도 배지 업데이트
function updateStatusBadge(riskLevel) {
    const statusEl = document.getElementById('currentStatus');
    
    if (riskLevel === 0) {
        statusEl.className = 'status-badge status-normal';
        statusEl.textContent = '✅ 정상';
    } else if (riskLevel === 1) {
        statusEl.className = 'status-badge status-warning';
        statusEl.textContent = '⚠️ 주의';
    } else if (riskLevel === 2) {
        statusEl.className = 'status-badge status-danger';
        statusEl.textContent = '🚨 위험';
    }
}

// 차트에 데이터 추가
function addDataToChart(chart, timestamp, value) {
    const timeStr = timestamp.toLocaleTimeString('ko-KR');
    
    chart.data.labels.push(timeStr);
    chart.data.datasets[0].data.push(value);
    
    // 최대 데이터 포인트 수 유지
    if (chart.data.labels.length > MAX_DATA_POINTS) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }
    
    chart.update('none'); // 애니메이션 없이 업데이트
}

// 차트 초기화
function initCharts() {
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: true,
        aspectRatio: 2,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            x: {
                display: true,
                ticks: {
                    maxTicksLimit: 10
                }
            },
            y: {
                beginAtZero: false
            }
        },
        animation: {
            duration: 0
        }
    };
    
    // 토양 수분 차트
    const moistureCtx = document.getElementById('moistureChart').getContext('2d');
    moistureChart = new Chart(moistureCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '토양 수분',
                data: [],
                borderColor: 'rgb(75, 192, 192)',
                backgroundColor: 'rgba(75, 192, 192, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: commonOptions
    });
    
    // 진동 차트
    const vibrationCtx = document.getElementById('vibrationChart').getContext('2d');
    vibrationChart = new Chart(vibrationCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '진동',
                data: [],
                borderColor: 'rgb(255, 99, 132)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: commonOptions
    });
    
    // 기울기 차트
    const tiltCtx = document.getElementById('tiltChart').getContext('2d');
    tiltChart = new Chart(tiltCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '기울기 변화',
                data: [],
                borderColor: 'rgb(153, 102, 255)',
                backgroundColor: 'rgba(153, 102, 255, 0.1)',
                tension: 0.4,
                fill: true
            }]
        },
        options: commonOptions
    });
    
    // 최종 위험도 점수 차트
    const riskScoreCtx = document.getElementById('riskScoreChart').getContext('2d');
    riskScoreChart = new Chart(riskScoreCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: '위험도 점수',
                data: [],
                borderColor: 'rgb(255, 159, 64)',
                backgroundColor: 'rgba(255, 159, 64, 0.1)',
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            aspectRatio: 2,
            plugins: {
                legend: {
                    display: false
                },
                annotation: {
                    annotations: {
                        normalZone: {
                            type: 'box',
                            yMin: 0,
                            yMax: 0.3,
                            backgroundColor: 'rgba(75, 192, 192, 0.1)',
                            borderWidth: 0
                        },
                        warningZone: {
                            type: 'box',
                            yMin: 0.3,
                            yMax: 0.6,
                            backgroundColor: 'rgba(255, 206, 86, 0.1)',
                            borderWidth: 0
                        },
                        dangerZone: {
                            type: 'box',
                            yMin: 0.6,
                            yMax: 1.0,
                            backgroundColor: 'rgba(255, 99, 132, 0.1)',
                            borderWidth: 0
                        },
                        warningLine: {
                            type: 'line',
                            yMin: 0.3,
                            yMax: 0.3,
                            borderColor: 'rgb(255, 206, 86)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {
                                display: true,
                                content: '주의 (0.3)',
                                position: 'start',
                                backgroundColor: 'rgba(255, 206, 86, 0.8)',
                                color: '#000'
                            }
                        },
                        dangerLine: {
                            type: 'line',
                            yMin: 0.6,
                            yMax: 0.6,
                            borderColor: 'rgb(255, 99, 132)',
                            borderWidth: 2,
                            borderDash: [5, 5],
                            label: {
                                display: true,
                                content: '위험 (0.6)',
                                position: 'start',
                                backgroundColor: 'rgba(255, 99, 132, 0.8)',
                                color: '#fff'
                            }
                        }
                    }
                }
            },
            scales: {
                x: {
                    display: true,
                    ticks: {
                        maxTicksLimit: 10
                    }
                },
                y: {
                    beginAtZero: true,
                    min: 0,
                    max: 1.0,
                    ticks: {
                        stepSize: 0.1
                    }
                }
            },
            animation: {
                duration: 0
            }
        }
    });
}

// 최신 데이터 로드
async function loadLatestData() {
    try {
        const response = await fetch('/latest');
        const data = await response.json();
        
        if (data) {
            updateDashboard(data);
        }
    } catch (error) {
        console.error('최신 데이터 로드 실패:', error);
    }
}

// 초기화
document.addEventListener('DOMContentLoaded', () => {
    initCharts();
    loadLatestData();
    connectWebSocket();
});
