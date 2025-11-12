import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# ✅ 한글 폰트 설정 (macOS / Windows 자동대응)
plt.rc('font', family='AppleGothic')
plt.rc('axes', unicode_minus=False)

# ✅ 기본 경로 설정
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "학생식당 예상식수 및 원가율(비즈메카 기준).xlsx")

# ✅ 시트 불러오기
df = pd.read_excel(file_path, sheet_name="제1기숙사식당 메뉴 데이터")

# ✅ 숫자형 변환
numeric_cols = ['판매가', '원가', '예상식수', '실제식수']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# ✅ 결측값 제거
df = df.dropna(subset=['년', '월', '일', '메뉴명'])

# ✅ 이상치 제거
df = df[(df['예상식수'] > 0) & (df['판매가'] > 0) & (df['실제식수'] > 5)]

# ✅ 기본 컬럼 정리
df['끼니'] = df['중식/석식']
# ✅ 날짜 컬럼 합치기 → datetime 변환
df['날짜'] = pd.to_datetime(
    df.rename(columns={'년': 'year', '월': 'month', '일': 'day'})[['year', 'month', 'day']],
    errors='coerce'
)


# ✅ 계산 컬럼
df['원가율'] = (df['원가'] / df['판매가']) * 100
df['식수달성률'] = (df['실제식수'] / df['예상식수']) * 100



# ✅ 컬럼 정리
df = df[['날짜', '식당명', '끼니', '메뉴명', '판매가', '원가', '원가율', '예상식수', '실제식수', '식수달성률']]

# ✅ 2023~2025년 필터
df = df[df['날짜'].dt.year.between(2023, 2025)]


# --------------------------------------------------
# 함수 정의
# --------------------------------------------------


# 메뉴명별 등장 횟수 정리
menu_counts = df.groupby('메뉴명').size().reset_index(name='등장횟수')

print(menu_counts)

# 등장횟수 많은 순으로 정렬
menu_counts = menu_counts.sort_values('등장횟수', ascending=False)

# 상위 20개 예시 출력
print(menu_counts.head(20))

# 전체 출력 원하면 아래처럼
for idx, row in menu_counts.iterrows():
    print(f"{row['메뉴명']} - {row['등장횟수']}회")

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


print(df.head(10))

import matplotlib.pyplot as plt

# 메뉴별 등장 횟수 계산
menu_counts = df['메뉴명'].value_counts()

import pandas as pd
import matplotlib.pyplot as plt

# -------------------------------------------------------
# 1️⃣ 날짜 변환
# -------------------------------------------------------
df['날짜'] = pd.to_datetime(df['날짜'])

# -------------------------------------------------------
# 2️⃣ 학기별 개강일 설정
# -------------------------------------------------------
semester_starts = {
    ('2023', '1학기'): pd.Timestamp('2023-03-02'),
    ('2023', '2학기'): pd.Timestamp('2023-09-01'),
    ('2024', '1학기'): pd.Timestamp('2024-03-04'),
    ('2024', '2학기'): pd.Timestamp('2024-09-02'),
    ('2025', '1학기'): pd.Timestamp('2025-03-03'),
    ('2025', '2학기'): pd.Timestamp('2025-09-01')   # 예측값 (필요 시 조정)
}

# -------------------------------------------------------
# 3️⃣ 학기 및 주차 계산 함수
# -------------------------------------------------------
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

    # 주차 계산
    week = ((date - start).days // 7) + 1
    return f"{year} {sem}", week

# -------------------------------------------------------
# 4️⃣ 학기 & 주차 컬럼 추가
# -------------------------------------------------------
df[['학기', '주차']] = df['날짜'].apply(lambda d: pd.Series(get_semester_info(d)))

# 유효한 주차(1~16)만 유지
df = df[df['주차'].between(1, 16)]

# -------------------------------------------------------
# 5️⃣ 주차별 평균 식수달성률 계산
# -------------------------------------------------------
weekly_trend = (
    df.groupby(['학기', '주차'])['식수달성률']
    .mean()
    .reset_index()
    .sort_values(['학기', '주차'])
)

import matplotlib.pyplot as plt
import seaborn as sns

# 학기별 색상 매핑 (연도별로 구분)
color_map = {
    '2023': '#1f77b4',  # 파란색
    '2024': '#ff7f0e',  # 주황색
    '2025': '#2ca02c'   # 초록색
}

# 1학기, 2학기 나누기
sem1 = weekly_trend[weekly_trend['학기'].str.contains('1학기')]
sem2 = weekly_trend[weekly_trend['학기'].str.contains('2학기')]

# ------------------------------------------------------------
# 1️⃣ 1학기 그래프 (2023, 2024, 2025)
# ------------------------------------------------------------
plt.figure(figsize=(10, 5))
for year in ['2023', '2024', '2025']:
    temp = sem1[sem1['학기'].str.contains(year)]
    if len(temp) > 0:
        plt.plot(temp['주차'], temp['식수달성률'], marker='o',
                 label=f'{year} 1학기', color=color_map[year])

plt.title('1학기 주차별 평균 식수달성률 (2023~2025)')
plt.xlabel('주차')
plt.ylabel('평균 식수달성률(%)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# ------------------------------------------------------------
# 2️⃣ 2학기 그래프 (2023, 2024)
# ------------------------------------------------------------
plt.figure(figsize=(10, 5))
for year in ['2023', '2024']:
    temp = sem2[sem2['학기'].str.contains(year)]
    if len(temp) > 0:
        plt.plot(temp['주차'], temp['식수달성률'], marker='o',
                 label=f'{year} 2학기', color=color_map[year])

plt.title('2학기 주차별 평균 식수달성률 (2023~2024)')
plt.xlabel('주차')
plt.ylabel('평균 식수달성률(%)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

import os
import pandas as pd
import matplotlib.pyplot as plt

# ✅ 한글 폰트 설정 (macOS / Windows 자동대응)
plt.rc('font', family='AppleGothic')
plt.rc('axes', unicode_minus=False)

# ✅ 데이터 로드
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "학생식당 예상식수 및 원가율(비즈메카 기준).xlsx")
df = pd.read_excel(file_path, sheet_name="제1기숙사식당 메뉴 데이터")

# ✅ 숫자형 변환
numeric_cols = ['판매가', '원가', '예상식수', '실제식수']
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

# ✅ 결측치 및 이상치 제거
df = df.dropna(subset=['년', '월', '일', '메뉴명'])
df = df[(df['예상식수'] > 0) & (df['판매가'] > 0) & (df['실제식수'] > 5)]

# ✅ 날짜 통합
df['날짜'] = pd.to_datetime(
    df.rename(columns={'년': 'year', '월': 'month', '일': 'day'})[['year', 'month', 'day']],
    errors='coerce'
)

# ✅ 기본 지표 계산
df['원가율'] = (df['원가'] / df['판매가']) * 100
df['식수달성률'] = (df['실제식수'] / df['예상식수']) * 100

# ✅ 2023~2025 필터
df = df[df['날짜'].dt.year.between(2023, 2025)]

# --------------------------------------------------
# 학기 및 주차 계산
# --------------------------------------------------

semester_starts = {
    ('2023', '1학기'): pd.Timestamp('2023-03-02'),
    ('2023', '2학기'): pd.Timestamp('2023-09-01'),
    ('2024', '1학기'): pd.Timestamp('2024-03-04'),
    ('2024', '2학기'): pd.Timestamp('2024-09-02'),
    ('2025', '1학기'): pd.Timestamp('2025-03-03'),
    ('2025', '2학기'): pd.Timestamp('2025-09-01')  # 추정치
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

# --------------------------------------------------
# 주차별 평균 식수달성률 / 예상식수 계산
# --------------------------------------------------
weekly_rate = df.groupby(['학기', '주차'])['식수달성률'].mean().reset_index()
weekly_expected = df.groupby(['학기', '주차'])['예상식수'].mean().reset_index()

# --------------------------------------------------
# 색상 매핑
# --------------------------------------------------
color_map = {'2023': '#1f77b4', '2024': '#ff7f0e', '2025': '#2ca02c'}

# --------------------------------------------------
# 1️⃣ 1학기 & 2학기 식수달성률 그래프
# --------------------------------------------------
def plot_by_semester(data, metric, ylabel, title_prefix):
    sem1 = data[data['학기'].str.contains('1학기')]
    sem2 = data[data['학기'].str.contains('2학기')]

    # 1학기
    plt.figure(figsize=(10, 5))
    for year in ['2023', '2024', '2025']:
        temp = sem1[sem1['학기'].str.contains(year)]
        if len(temp) > 0:
            plt.plot(temp['주차'], temp[metric], marker='o',
                     label=f'{year} 1학기', color=color_map[year])
    plt.title(f'1학기 주차별 평균 {title_prefix} (2023~2025)')
    plt.xlabel('주차')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

    # 2학기
    plt.figure(figsize=(10, 5))
    for year in ['2023', '2024']:
        temp = sem2[sem2['학기'].str.contains(year)]
        if len(temp) > 0:
            plt.plot(temp['주차'], temp[metric], marker='o',
                     label=f'{year} 2학기', color=color_map[year])
    plt.title(f'2학기 주차별 평균 {title_prefix} (2023~2024)')
    plt.xlabel('주차')
    plt.ylabel(ylabel)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# --------------------------------------------------
# 1️⃣ 식수달성률 그래프
# --------------------------------------------------
plot_by_semester(weekly_rate, '식수달성률', '평균 식수달성률(%)', '식수달성률')

# --------------------------------------------------
# 2️⃣ 예상식수 그래프
# --------------------------------------------------
plot_by_semester(weekly_expected, '예상식수', '평균 예상식수(명)', '예상식수')

import matplotlib.pyplot as plt


def plot_dual_axis(df_rate, df_expected, year, semester):
    # 해당 학기 데이터 필터링
    rate_data = df_rate[df_rate['학기'] == f"{year} {semester}"]
    exp_data = df_expected[df_expected['학기'] == f"{year} {semester}"]

    fig, ax1 = plt.subplots(figsize=(10, 5))

    # 왼쪽 y축: 식수달성률
    ax1.plot(rate_data['주차'], rate_data['식수달성률'], color='#1f77b4', marker='o', label='식수달성률(%)')
    ax1.set_xlabel('주차')
    ax1.set_ylabel('식수달성률(%)', color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')

    # 오른쪽 y축: 예상식수
    ax2 = ax1.twinx()
    ax2.plot(exp_data['주차'], exp_data['예상식수'], color='#ff7f0e', marker='s', label='예상식수(명)')
    ax2.set_ylabel('예상식수(명)', color='#ff7f0e')
    ax2.tick_params(axis='y', labelcolor='#ff7f0e')

    plt.title(f"{year} {semester} 주차별 식수달성률 vs 예상식수")
    fig.tight_layout()
    plt.grid(True, alpha=0.3)
    plt.show()


# --------------------------------------------------
# ✅ 예시 실행 (원하는 학기 선택)
# --------------------------------------------------
plot_dual_axis(weekly_rate, weekly_expected, 2023, '1학기')
plot_dual_axis(weekly_rate, weekly_expected, 2023, '2학기')
plot_dual_axis(weekly_rate, weekly_expected, 2024, '1학기')
plot_dual_axis(weekly_rate, weekly_expected, 2024, '2학기')
plot_dual_axis(weekly_rate, weekly_expected, 2025, '1학기')

# 기본 통계
print(df.describe())

# 식수달성률 분포
plt.figure(figsize=(8,4))
sns.histplot(df['식수달성률'], bins=30, kde=True, color='skyblue')
plt.title('식수달성률 분포')
plt.xlabel('식수달성률 (%)')
plt.show()

# 원가율 분포
plt.figure(figsize=(8,4))
sns.histplot(df['원가율'], bins=30, kde=True, color='orange')
plt.title('원가율 분포')
plt.xlabel('원가율 (%)')
plt.show()

plt.figure(figsize=(8,5))
sns.boxplot(data=df, x='끼니', y='식수달성률')
plt.title('끼니별 식수달성률 분포')
plt.show()



print(df.columns)
