/**
 * 이력 조회 페이지 JavaScript
 */

let currentMinutes = null;

// 이력 데이터 로드
async function loadHistory(minutes = null) {
    const loading = document.getElementById('loading');
    const historyBody = document.getElementById('historyBody');
    const dataCount = document.getElementById('dataCount');
    
    // 로딩 표시
    loading.style.display = 'block';
    historyBody.innerHTML = '<tr><td colspan="10" style="text-align: center;">로딩 중...</td></tr>';
    
    currentMinutes = minutes;
    
    try {
        let url = '/history';
        if (minutes) {
            url += `?minutes=${minutes}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        loading.style.display = 'none';
        
        if (data.length === 0) {
            historyBody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 40px; color: #6c757d;">데이터가 없습니다</td></tr>';
            dataCount.textContent = '';
            return;
        }
        
        // 테이블 생성
        historyBody.innerHTML = data.map(item => {
            const timestamp = new Date(item.created_at);
            const riskBadge = getRiskBadgeHTML(item.risk_level);
            
            return `
                <tr>
                    <td>${timestamp.toLocaleString('ko-KR')}</td>
                    <td>${item.moisture.toFixed(1)}</td>
                    <td>${item.vibration_raw.toFixed(2)}</td>
                    <td>${item.accel_x.toFixed(3)}</td>
                    <td>${item.accel_y.toFixed(3)}</td>
                    <td>${item.accel_z.toFixed(3)}</td>
                    <td>${item.gyro_x.toFixed(3)}</td>
                    <td>${item.gyro_y.toFixed(3)}</td>
                    <td>${item.gyro_z.toFixed(3)}</td>
                    <td>${riskBadge}</td>
                </tr>
            `;
        }).join('');
        
        // 데이터 개수 표시
        dataCount.textContent = `총 ${data.length}개 데이터`;
        
    } catch (error) {
        console.error('데이터 로드 실패:', error);
        loading.style.display = 'none';
        historyBody.innerHTML = '<tr><td colspan="10" style="text-align: center; padding: 40px; color: #dc3545;">데이터 로드 실패</td></tr>';
    }
}

// 위험도 배지 HTML 생성
function getRiskBadgeHTML(riskLevel) {
    if (riskLevel === 0) {
        return '<span class="status-badge status-normal">정상</span>';
    } else if (riskLevel === 1) {
        return '<span class="status-badge status-warning">주의</span>';
    } else if (riskLevel === 2) {
        return '<span class="status-badge status-danger">위험</span>';
    }
    return '<span>-</span>';
}

// CSV 다운로드
function downloadCSV() {
    let url = '/history/csv';
    if (currentMinutes) {
        url += `?minutes=${currentMinutes}`;
    }
    
    window.open(url, '_blank');
}

// 페이지 로드 시 기본 데이터 로드 (최근 1시간)
document.addEventListener('DOMContentLoaded', () => {
    loadHistory(60);
});
