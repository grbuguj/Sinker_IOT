/**
 * 임계값 설정 페이지 JavaScript
 */

// 임계값 한글 이름 매핑
const thresholdNames = {
    'moisture_warning': '토양 수분 - 주의',
    'moisture_danger': '토양 수분 - 위험',
    'vibration_warning': '진동 - 주의',
    'vibration_danger': '진동 - 위험',
    'accel_delta_warning': '가속도 변화량 - 주의',
    'accel_delta_danger': '가속도 변화량 - 위험',
    'gyro_delta_warning': '자이로 변화량 - 주의',
    'gyro_delta_danger': '자이로 변화량 - 위험'
};

// 임계값 로드
async function loadThresholds() {
    const loading = document.getElementById('loading');
    const thresholdList = document.getElementById('thresholdList');
    
    loading.style.display = 'block';
    
    try {
        const response = await fetch('/config/api/thresholds');
        const data = await response.json();
        
        loading.style.display = 'none';
        
        // 임계값 목록 생성
        thresholdList.innerHTML = data.map(item => {
            const displayName = thresholdNames[item.name] || item.name;
            
            return `
                <div class="threshold-item">
                    <label>${displayName}</label>
                    <input 
                        type="number" 
                        step="0.1" 
                        value="${item.value}" 
                        id="threshold-${item.id}"
                        data-name="${item.name}"
                    >
                    <button 
                        class="btn btn-success" 
                        onclick="updateThreshold(${item.id}, '${item.name}')"
                    >
                        저장
                    </button>
                </div>
            `;
        }).join('');
        
    } catch (error) {
        console.error('임계값 로드 실패:', error);
        loading.style.display = 'none';
        thresholdList.innerHTML = '<p style="text-align: center; color: #dc3545;">데이터 로드 실패</p>';
    }
}

// 임계값 업데이트
async function updateThreshold(id, name) {
    const input = document.getElementById(`threshold-${id}`);
    const value = parseFloat(input.value);
    
    if (isNaN(value)) {
        showToast('유효한 숫자를 입력해주세요', 'error');
        return;
    }
    
    try {
        const response = await fetch('/config/api/thresholds', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                name: name,
                value: value
            })
        });
        
        if (response.ok) {
            showToast('✅ 임계값이 업데이트되었습니다', 'success');
        } else {
            showToast('❌ 업데이트 실패', 'error');
        }
        
    } catch (error) {
        console.error('임계값 업데이트 실패:', error);
        showToast('❌ 업데이트 실패', 'error');
    }
}

// 토스트 알림 표시
function showToast(message, type = 'success') {
    const toast = document.createElement('div');
    toast.className = 'toast';
    toast.textContent = message;
    
    if (type === 'error') {
        toast.style.background = '#dc3545';
    }
    
    document.body.appendChild(toast);
    
    // 3초 후 제거
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 3000);
}

// 페이지 로드 시 임계값 로드
document.addEventListener('DOMContentLoaded', () => {
    loadThresholds();
});
