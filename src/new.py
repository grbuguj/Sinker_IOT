import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from sklearn.preprocessing import LabelEncoder

# ---------------------------------------------------------
# ✅ 기본 설정
# ---------------------------------------------------------
plt.rc('font', family='AppleGothic')
plt.rc('axes', unicode_minus=False)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
file_path = os.path.join(BASE_DIR, "data", "학생식당 예상식수 및 원가율(비즈메카 기준).xlsx")

# ---------------------------------------------------------
# ✅ 데이터 불러오기 및 정제
# ---------------------------------------------------------
df = pd.read_excel(file_path, sheet_name="제1기숙사식당 메뉴 데이터")

# 숫자형 변환
num_cols = ['판매가', '원가', '예상식수', '실제식수']
for col in num_cols:
    df[col] = pd.to_numeric(df[col], errors='coerce')

df['판매가'] = df['판매가'].replace(4300, 4500)

# 결측치 / 이상치 제거
df = df.dropna(subset=['년', '월', '일', '메뉴명'])
df = df[(df['예상식수'] > 0) & (df['판매가'] > 0) & (df['실제식수'] > 5)]

# 날짜 생성
df['날짜'] = pd.to_datetime(
    df.rename(columns={'년': 'year', '월': 'month', '일': 'day'})[['year', 'month', 'day']],
    errors='coerce'
)

# 기본 KPI
df['원가율'] = (df['원가'] / df['판매가']) * 100
df['식수달성률'] = (df['실제식수'] / df['예상식수']) * 100
df['끼니'] = df['중식/석식'].str.strip()
df = df[df['날짜'].dt.year.between(2023, 2025)]

# ---------------------------------------------------------
# ✅ 메뉴 카테고리 분류
# ---------------------------------------------------------
def categorize_menu(name):
    if any(k in name for k in ['돈까스', '까스', '카츠', '고구마치즈', '핫도그']):
        return '돈까스류'
    elif any(k in name for k in ['덮밥', '오므라이스', '라이스', '볶음밥', '짜장밥', '나시고랭', '에비동', '알밥', '밥', '죽', '나주', '살라푸']):
        return '덮밥/라이스류'
    elif any(k in name for k in ['우동', '칼국수', '파스타', '스파게티', '라멘', '면', '모밀', '누들', '짬뽕', '짜장', '떡볶이']):
        return '면류'
    elif any(k in name for k in ['찌개', '국', '탕', '수제비', '찌게', '육개']):
        return '찌개/국/탕류'
    elif any(k in name for k in ['비빔', '볶음', '잡채', '버섯밥', '고추참치']):
        return '비빔/볶음류'
    elif any(k in name for k in ['돼지', '돈육', '스팸','제육', '돈삼겹', '돈불고기', '짜글이', '두루치기', '목살', '스테이크', '함박', '까츠', '베이컨', '보쌈']):
        return '돈육류'
    elif any(k in name for k in ['닭', '치킨', '찜닭', '닭갈비', '닭볶음', '가라아게']):
        return '닭육류'
    elif any(k in name for k in ['소고기', '차돌', '우삼겹', '불고기', '육개장', '장조림']):
        return '소고기류'


df['메뉴카테고리'] = df['메뉴명'].apply(categorize_menu)
# 각 메뉴카테고리별 개수 출력
category_counts = df['메뉴카테고리'].value_counts()

print("메뉴카테고리별 개수:")
print(category_counts)

# 보기 좋게 비율도 함께 보고 싶다면
print("\n(비율 포함)")
print(df['메뉴카테고리'].value_counts(normalize=True).round(3) * 100)




# ---------------------------------------------------------
# ✅ 학기 / 주차 계산
# ---------------------------------------------------------
semester_starts = {
    ('2023', '1학기'): pd.Timestamp('2023-03-02'),
    ('2023', '2학기'): pd.Timestamp('2023-09-01'),
    ('2024', '1학기'): pd.Timestamp('2024-03-04'),
    ('2024', '2학기'): pd.Timestamp('2024-09-02'),
    ('2025', '1학기'): pd.Timestamp('2025-03-03'),
    ('2025', '2학기'): pd.Timestamp('2025-09-01')
}

def get_semester_info(date):
    y = str(date.year)
    if y not in ['2023', '2024', '2025']:
        return None, None
    if pd.Timestamp(f"{y}-03-01") <= date < pd.Timestamp(f"{y}-08-01"):
        sem, start = '1학기', semester_starts[(y, '1학기')]
    else:
        sem, start = '2학기', semester_starts[(y, '2학기')]
    week = ((date - start).days // 7) + 1
    return f"{y} {sem}", week

df[['학기', '주차']] = df['날짜'].apply(lambda d: pd.Series(get_semester_info(d)))
df = df[df['주차'].between(1, 16)]
df['연도'] = df['날짜'].dt.year
df['요일'] = df['날짜'].dt.day_name()

# ---------------------------------------------------------
# ✅ EDA 1: 실제식수 분포 및 이상치 탐색
# ---------------------------------------------------------
plt.figure(figsize=(8,5))
sns.histplot(df['실제식수'], bins=40, kde=True, color='lightgreen')
plt.axvline(df['실제식수'].mean(), color='red', linestyle='--', label='평균값')
plt.title("실제식수 분포 및 이상치 탐색 (2023~2025)")
plt.xlabel("실제식수(명)")
plt.legend(); plt.show()

# ---------------------------------------------------------
# ✅ EDA 2: 끼니·요일·메뉴유형별 패턴
# ---------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(18,5))
sns.boxplot(x='끼니', y='실제식수', data=df, ax=axes[0])
axes[0].set_title("끼니별 실제식수 분포")

sns.barplot(x='요일', y='실제식수', data=df, estimator=np.mean,
            order=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'], ax=axes[1])
axes[1].set_title("요일별 평균 실제식수")

sns.barplot(x='메뉴카테고리', y='실제식수', data=df, estimator=np.mean, ax=axes[2])
axes[2].set_title("메뉴카테고리별 평균 실제식수")
axes[2].tick_params(axis='x', rotation=45)
plt.tight_layout(); plt.show()

# ---------------------------------------------------------
# ✅ EDA 3: 시계열 패턴 (1학기 / 2학기 → 연도별 + 평균선)
# ---------------------------------------------------------
import matplotlib.pyplot as plt
import seaborn as sns

weekly = df.groupby(['학기', '주차'])['실제식수'].mean().reset_index()

# 학기 구분
sem1 = weekly[weekly['학기'].str.contains('1학기')]
sem2 = weekly[weekly['학기'].str.contains('2학기')]

# 학기별 평균선 추가
sem1_mean = sem1.groupby('주차')['실제식수'].mean().reset_index()
sem2_mean = sem2.groupby('주차')['실제식수'].mean().reset_index()

# 1학기 그래프
plt.figure(figsize=(10,5))
sns.lineplot(data=sem1, x='주차', y='실제식수', hue='학기', marker='o', alpha=0.6)
sns.lineplot(data=sem1_mean, x='주차', y='실제식수', color='navy', linewidth=3, label='1학기 전체 평균')
plt.title("1학기 주차별 평균 실제식수 추이 (연도별 + 평균)")
plt.xlabel("주차"); plt.ylabel("실제식수(명)")
plt.legend(); plt.grid(True)
plt.show()

# 2학기 그래프
plt.figure(figsize=(10,5))
sns.lineplot(data=sem2, x='주차', y='실제식수', hue='학기', marker='o', alpha=0.6)
sns.lineplot(data=sem2_mean, x='주차', y='실제식수', color='darkorange', linewidth=3, label='2학기 전체 평균')
plt.title("2학기 주차별 평균 실제식수 추이 (연도별 + 평균)")
plt.xlabel("주차"); plt.ylabel("실제식수(명)")
plt.legend(); plt.grid(True)
plt.show()

# ---------------------------------------------------------
# ✅ EDA 4: 가격·원가율과의 관계
# ---------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(12,5))
sns.scatterplot(x='판매가', y='실제식수', data=df, ax=axes[0])
axes[0].set_title("판매가와 실제식수의 관계")

sns.scatterplot(x='원가율', y='실제식수', data=df, ax=axes[1])
axes[1].set_title("원가율과 실제식수의 관계")
plt.tight_layout(); plt.show()
price_counts = df['판매가'].value_counts().sort_index()

print("판매가별 메뉴 개수:")
for price, count in price_counts.items():
    print(f"{price}원 : {count}개")

# ---------------------------------------------------------
# ✅ EDA 6: 수치형 변수 간 상관관계 Heatmap
# ---------------------------------------------------------

num_cols = ['실제식수', '예상식수', '판매가', '원가', '원가율', '식수달성률']

plt.figure(figsize=(8,6))
sns.heatmap(df[num_cols].corr(), annot=True, fmt=".2f", cmap='coolwarm', vmin=-1, vmax=1)
plt.title("수치형 변수 간 상관관계 Heatmap")
plt.show()


# ---------------------------------------------------------
# ✅ 데이터 요약 + 인사이트
# ---------------------------------------------------------
summary = {
    "평균 실제식수": round(df['실제식수'].mean(), 2),
    "실제식수 표준편차": round(df['실제식수'].std(), 2),
    "평균 원가율": round(df['원가율'].mean(), 2),
    "데이터 기간": f"{df['날짜'].min().date()} ~ {df['날짜'].max().date()}",
    "데이터 건수": len(df)
}

print("\n=== 데이터 요약 ===")
for k, v in summary.items():
    print(f"{k}: {v}")

print("\n=== 주요 인사이트 ===")
print("1️⃣ 실제식수는 약 1000~2500명 구간에 집중되어 있음.")
print("2️⃣ 중식이 가장 높고 석식은 절반 이하 규모.")
print("3️⃣ 월~수 식수량이 높고, 금요일 이후 감소 경향.")
print("4️⃣ 덮밥/찌개류 메뉴가 상대적으로 높은 수요 유지.")
print("5️⃣ 판매가↑ → 식수↓, 주차가 높을수록 식수 감소 경향.")
print("6️⃣ 예상식수와 실제식수는 0.8 이상의 높은 상관관계.")
