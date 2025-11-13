import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# ------------------------------------------------------------
# 1️⃣ 기본 설정
# ------------------------------------------------------------
plt.rc('font', family='AppleGothic')
plt.rc('axes', unicode_minus=False)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "학생식당 예상식수 및 원가율(비즈메카 기준).xlsx")

# ------------------------------------------------------------
# 2️⃣ 데이터 로드 및 정리
# ------------------------------------------------------------
df = pd.read_excel(file_path, sheet_name="제1기숙사식당 메뉴 데이터")

numeric_cols = ['판매가', '원가', '예상식수', '실제식수']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df = df.dropna(subset=['년', '월', '일', '메뉴명'])
df = df[(df['예상식수'] > 0) & (df['판매가'] > 0) & (df['실제식수'] > 5)]

# ✅ 날짜 생성
df['날짜'] = pd.to_datetime(
    df.rename(columns={'년': 'year', '월': 'month', '일': 'day'})[['year', 'month', 'day']],
    errors='coerce'
)


# ✅ 끼니 컬럼 추가
df['끼니'] = df['중식/석식']

# ✅ 기본 지표 계산
df['원가율'] = (df['원가'] / df['판매가']) * 100
df['식수달성률'] = (df['실제식수'] / df['예상식수']) * 100

# ✅ 2023~2025 필터
df = df[df['날짜'].dt.year.between(2023, 2025)]

# ✅ 극단치 제거
df = df[df['실제식수'] < 2000]

# ------------------------------------------------------------
# 3️⃣ 메뉴 카테고리 분류
# ------------------------------------------------------------
def categorize_menu(name):
    if any(k in name for k in ['돈까스', '까스', '카츠']):
        return '돈까스류'
    elif any(k in name for k in ['덮밥', '오므라이스', '라이스', '볶음밥']):
        return '덮밥/라이스류'
    elif any(k in name for k in ['우동', '칼국수', '파스타', '스파게티', '라멘', '면']):
        return '면류'
    elif any(k in name for k in ['찌개', '국', '탕', '수제비']):
        return '찌개/국/탕류'
    elif any(k in name for k in ['돼지', '돈육', '제육', '돈삼겹', '돈불고기', '짜글이']):
        return '돈육류'
    elif any(k in name for k in ['닭', '치킨', '찜닭', '닭갈비', '닭볶음']):
        return '닭육류'
    elif any(k in name for k in ['소고기', '차돌', '우삼겹', '불고기', '육개장']):
        return '소고기류'
    elif any(k in name for k in ['비빔', '볶음', '잡채']):
        return '비빔/볶음류'
    else:
        return '기타'

df['메뉴카테고리'] = df['메뉴명'].apply(categorize_menu)

# ------------------------------------------------------------
# 4️⃣ 학기 및 주차 계산
# ------------------------------------------------------------
semester_starts = {
    ('2023', '1학기'): pd.Timestamp('2023-03-02'),
    ('2023', '2학기'): pd.Timestamp('2023-09-01'),
    ('2024', '1학기'): pd.Timestamp('2024-03-04'),
    ('2024', '2학기'): pd.Timestamp('2024-09-02'),
    ('2025', '1학기'): pd.Timestamp('2025-03-03'),
    ('2025', '2학기'): pd.Timestamp('2025-09-01')
}

def get_semester_info(date):
    year = str(date.year)
    if year == '2023':
        if pd.Timestamp('2023-03-02') <= date < pd.Timestamp('2023-08-01'):
            sem, start = '1학기', semester_starts[(year, '1학기')]
        else:
            sem, start = '2학기', semester_starts[(year, '2학기')]
    elif year == '2024':
        if pd.Timestamp('2024-03-04') <= date < pd.Timestamp('2024-08-01'):
            sem, start = '1학기', semester_starts[(year, '1학기')]
        else:
            sem, start = '2학기', semester_starts[(year, '2학기')]
    elif year == '2025':
        if pd.Timestamp('2025-03-03') <= date < pd.Timestamp('2025-08-01'):
            sem, start = '1학기', semester_starts[(year, '1학기')]
        else:
            sem, start = '2학기', semester_starts[(year, '2학기')]
    else:
        return None, None
    week = ((date - start).days // 7) + 1
    return f"{year} {sem}", week

df[['학기', '주차']] = df['날짜'].apply(lambda d: pd.Series(get_semester_info(d)))
df = df[df['주차'].between(1, 16)]

# ------------------------------------------------------------
# 5️⃣ Feature Engineering
# ------------------------------------------------------------
df['요일'] = df['날짜'].dt.day_name()
df['주중주말'] = df['요일'].apply(lambda x: '주말' if x in ['Saturday', 'Sunday'] else '주중')


import holidays

# 한국 공휴일 자동 생성
kr_holidays = holidays.KR(years=[2023, 2024, 2025])

# 날짜가 공휴일이면 1, 아니면 0
df['공휴일'] = df['날짜'].apply(lambda d: 1 if d in kr_holidays else 0)

df['시험주'] = df['주차'].apply(lambda x: 1 if x in [8, 15] else 0)

df['메뉴평균식수'] = df.groupby('메뉴명')['실제식수'].transform('mean')
df['카테고리평균식수'] = df.groupby('메뉴카테고리')['실제식수'].transform('mean')
df['메뉴재등장빈도'] = df.groupby('메뉴명')['메뉴명'].transform('count')

# ------------------------------------------------------------
# 6️⃣ Feature / Target 분리
# ------------------------------------------------------------
target = '실제식수'
features = [
    '학기', '주차', '요일', '주중주말', '공휴일', '시험주',
    '메뉴명', '메뉴카테고리', '끼니',
    '메뉴평균식수', '카테고리평균식수', '메뉴재등장빈도',
    '판매가', '원가율'
]

X = df[features].copy()
y = df[target]

# ------------------------------------------------------------
# 7️⃣ 인코딩 & 모델링
# ------------------------------------------------------------
categorical_features = ['학기', '요일', '주중주말', '공휴일', '시험주', '메뉴카테고리', '끼니']
numeric_features = ['주차', '판매가', '원가율', '메뉴평균식수', '카테고리평균식수', '메뉴재등장빈도']

# ✅ 메뉴명 → 빈도 인코딩 (로그 안정화)
freq_map = df['메뉴명'].value_counts(normalize=True)

# 명시적으로 시리즈로 캐스팅 후 log1p 적용
menu_freq_series = pd.Series(X['메뉴명'].map(freq_map).fillna(0).astype(float))
X.loc[:, '메뉴명'] = np.log1p(menu_freq_series)




categorical_transformer = OneHotEncoder(drop="first", handle_unknown="ignore")
numeric_transformer = StandardScaler()

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", categorical_transformer, categorical_features),
        ("num", numeric_transformer, numeric_features)
    ]
)

# ✅ Ridge 회귀로 변경 (L2 정규화)
model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("regressor", Ridge(alpha=1.0))
])

# ------------------------------------------------------------
# 8️⃣ 학습 및 평가
# ------------------------------------------------------------
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model.fit(X_train, y_train)
y_pred = model.predict(X_test)

r2 = r2_score(y_test, y_pred)
mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print(f"R² Score: {r2:.3f}")
print(f"MAE: {mae:.2f}")
print(f"RMSE: {rmse:.2f}")

# ------------------------------------------------------------
# 9️⃣ 예측 테스트: 단일 샘플 입력
# ------------------------------------------------------------
# 입력 스펙 안내
# - 학기: 'YYYY 1학기' 또는 'YYYY 2학기' 형식. 예) '2024 1학기'
#         허용값 예: list(df['학기'].dropna().unique())
# - 주차: 1 ~ 16의 정수
# - 요일: Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
#         허용값 예: list(df['요일'].dropna().unique())
# - 주중주말: '주중' 또는 '주말'
# - 공휴일: 0(아님) / 1(맞음)
# - 시험주: 0(아님) / 1(맞음)  (예: 8, 15주차 등 네가 규칙 정한 값)
# - 메뉴명: 문자열 (훈련 데이터에 없을 수 있음)
# - 메뉴카테고리: '덮밥/라이스류', '찌개/국/탕류', '면류', '비빔/볶음류',
#                 '돈육류', '닭육류', '소고기류', '돈까스류' 등
#         허용값 예: list(df['메뉴카테고리'].dropna().unique())
# - 끼니: '조식'/'중식'/'석식' 등 네 데이터에 들어있는 그대로
#         허용값 예: list(df['끼니'].dropna().unique())
# - 메뉴평균식수: 수치. [옵션] 새 메뉴면 비워도 됨(자동 보완)
# - 카테고리평균식수: 수치. [옵션] 비워도 됨(자동 보완)
# - 메뉴재등장빈도: 수치. [옵션] 새 메뉴면 0으로 자동 설정
# - 판매가: 정수 (예: 4500, 5000, 5500)
# - 원가율: 실수 (예: 47.2)

sample_input = {
    '학기': '2024 2학기',
    '주차': 1,
    '요일': 'Tuesday',
    '주중주말': '주중',
    '공휴일': 0,
    '시험주': 0,
    '메뉴명': '왕만두떡국',
    '메뉴카테고리': '찌개/국/탕류',
    '끼니': '중식',
    '메뉴평균식수': 500,
    '카테고리평균식수': 300,
    '메뉴재등장빈도': 10,
    '판매가': 4500,
    '원가율': 35
}

# dict → DataFrame 변환
sample_df = pd.DataFrame([sample_input])

# 동일한 변환 적용 (메뉴명 인코딩 + log)
freq_map = df['메뉴명'].value_counts(normalize=True)
sample_df['메뉴명'] = sample_df['메뉴명'].map(freq_map).fillna(0).astype(float)
sample_df['메뉴명'] = np.log1p(sample_df['메뉴명'])

menu_mean_map = df.groupby('메뉴명')['실제식수'].mean()
cate_mean_map = df.groupby('메뉴카테고리')['실제식수'].mean()
global_mean = float(df['실제식수'].mean())

def _prepare_single_input(sample_dict: dict) -> pd.DataFrame:
    """
    사용자가 넣은 dict를 모델 입력 형태로 정제.
    - 새 메뉴(훈련에 없던 메뉴)인 경우:
      메뉴평균식수 -> 카테고리평균식수 -> 전체평균 순으로 보완
      메뉴재등장빈도 -> 0
    - 타입/스케일 정리 후, 훈련 파이프라인과 동일 컬럼(features) 순서로 반환
    """
    s = sample_dict.copy()

    # 기본 보정
    s['공휴일'] = int(s.get('공휴일', 0))
    s['시험주'] = int(s.get('시험주', 0))
    s['주차'] = int(s['주차'])
    s['판매가'] = int(s['판매가'])
    s['원가율'] = float(s['원가율'])

    # 메뉴평균식수 자동 보완
    if ('메뉴평균식수' not in s) or (s['메뉴평균식수'] is None):
        if s.get('메뉴명') in menu_mean_map.index:
            s['메뉴평균식수'] = float(menu_mean_map[s['메뉴명']])
        else:
            # 카테고리 평균 → 전체 평균 순으로 백업
            s['메뉴평균식수'] = float(cate_mean_map.get(s.get('메뉴카테고리'), global_mean))

    # 카테고리평균식수 자동 보완
    if ('카테고리평균식수' not in s) or (s['카테고리평균식수'] is None):
        s['카테고리평균식수'] = float(cate_mean_map.get(s.get('메뉴카테고리'), global_mean))

    # 메뉴재등장빈도 자동 보완 (새 메뉴면 0)
    if ('메뉴재등장빈도' not in s) or (s['메뉴재등장빈도'] is None):
        s['메뉴재등장빈도'] = int(df[df['메뉴명'] == s.get('메뉴명')].shape[0])

    # DataFrame화 후, 메뉴명 → 빈도 인코딩(log1p) 적용
    X_one = pd.DataFrame([s])

    # 메뉴명 빈도 매핑 + log1p
    # 메뉴명 빈도 매핑 + log1p
    X_one.loc[:, '메뉴명'] = X_one['메뉴명'].map(freq_map).fillna(0.0).astype(float)
    X_one.loc[:, '메뉴명'] = np.log1p(np.array(X_one['메뉴명'], dtype=float))

    # 모델이 기대하는 컬럼 순서(features)에 맞춤
    # 누락 컬럼이 있다면 KeyError가 날 수 있으므로 미리 채워주기
    for col in features:
        if col not in X_one.columns:
            # 범주형은 가장 흔한 값으로 채울 수도 있지만, 여기서는 단순 NA → 안전 기본값 처리
            if col in ['학기','요일','주중주말','메뉴카테고리','끼니']:
                X_one[col] = df[col].mode().iloc[0]  # 최빈값
            elif col in ['공휴일','시험주']:
                X_one[col] = 0
            else:
                X_one[col] = 0

    # 최종 컬럼 순서 맞추기
    X_one = X_one[features].copy()
    return X_one



def predict_demand(sample_dict: dict) -> float:
    """
    단일 샘플 dict를 받아 예상식수(모델 예측값)를 반환.
    """
    X_one = _prepare_single_input(sample_dict)
    y_hat = model.predict(X_one)[0]
    return float(y_hat)

# ------------------------------------------------------------
# 10) 예측 예시 - 입력값 템플릿 (주석으로 허용값 안내)
# ------------------------------------------------------------
example_input = {
    # 학기: 'YYYY 1학기' / 'YYYY 2학기' (df['학기']에서 사용한 값과 동일하게)
    '학기': '2024 1학기',
    # 주차: 1~16
    '주차': 7,
    # 요일: Monday/Tuesday/Wednesday/Thursday/Friday/Saturday/Sunday
    '요일': 'Tuesday',
    # 주중주말: '주중' 또는 '주말'
    '주중주말': '주중',
    # 공휴일, 시험주: 0/1
    '공휴일': 0,
    '시험주': 1,
    # 메뉴명: 문자열 (새 메뉴 가능)
    '메뉴명': '제육볶음',
    # 메뉴카테고리: df에서 사용한 카테고리명 그대로
    # 예: '덮밥/라이스류','찌개/국/탕류','면류','비빔/볶음류','돈육류','닭육류','소고기류','돈까스류'
     '메뉴카테고리': '돈육류',
    # 끼니: df에서 사용한 값 그대로 (예: '중식', '석식' 등)
    '끼니': '석식',
    # 아래 3개는 [옵션] — 안 넣으면 자동 보완됨
    '메뉴평균식수': 500,
    '카테고리평균식수': 400,
    #'메뉴재등장빈도': 0,
    # 판매가/원가율
    '판매가': 5000,
    '원가율': 47.2
}

pred = predict_demand(example_input)
print(f"[예측] 예상식수: {pred:.1f}명")




# ------------------------------------------------------------
# 11️⃣ 모델 저장
# ------------------------------------------------------------
import joblib
save_path = os.path.join(BASE_DIR, "model.pkl")
joblib.dump(model, save_path)
print(f"[저장 완료] 모델이 저장되었습니다 → {save_path}")

