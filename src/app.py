import os
import pandas as pd
import numpy as np
import streamlit as st
import joblib

# ============================================================
# 1) 기본 설정
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "학생식당 예상식수 및 원가율(비즈메카 기준).xlsx")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

st.set_page_config(page_title="학생식당 예상식수 예측", layout="centered")
st.title("제1기숙사식당 식수예측 시스템 ver0")
st.write("입력값을 기반으로 Ridge 회귀 모델이 식수를 예측합니다. by 재웅")

# 예측 이력 초기화
if "history" not in st.session_state:
    st.session_state["history"] = []

# 모델 로드
model = joblib.load(MODEL_PATH)

# ============================================================
# 2) 데이터 로드 + 기본 전처리
# ============================================================
df = pd.read_excel(DATA_PATH, sheet_name="제1기숙사식당 메뉴 데이터")
df["끼니"] = df["중식/석식"]

# 숫자형 컬럼 캐스팅
numeric_cols = ["판매가", "원가", "예상식수", "실제식수"]
for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 필터링
df = df.dropna(subset=["년", "월", "일", "메뉴명"])
df = df[(df["예상식수"] > 0) & (df["판매가"] > 0) & (df["실제식수"] > 5)]

# 날짜 생성
df["날짜"] = pd.to_datetime(
    df.rename(columns={"년": "year", "월": "month", "일": "day"})[["year", "month", "day"]],
    errors="coerce"
)


# ============================================================
# 3) 메뉴 카테고리 함수
# ============================================================
def categorize_menu(name: str) -> str:
    if any(k in name for k in ["돈까스", "까스", "카츠"]):
        return "돈까스류"
    if any(k in name for k in ["덮밥", "오므라이스", "라이스", "볶음밥"]):
        return "덮밥/라이스류"
    if any(k in name for k in ["우동", "칼국수", "파스타", "스파게티", "라멘", "면"]):
        return "면류"
    if any(k in name for k in ["찌개", "국", "탕", "수제비"]):
        return "찌개/국/탕류"
    if any(k in name for k in ["돼지", "돈육", "제육", "돈삼겹", "돈불고기", "짜글이"]):
        return "돈육류"
    if any(k in name for k in ["닭", "치킨", "찜닭", "닭갈비", "닭볶음"]):
        return "닭육류"
    if any(k in name for k in ["소고기", "차돌", "우삼겹", "불고기", "육개장"]):
        return "소고기류"
    if any(k in name for k in ["비빔", "볶음", "잡채"]):
        return "비빔/볶음류"
    return "기타"


df["메뉴카테고리"] = df["메뉴명"].apply(categorize_menu)

# ============================================================
# 4) 학기 / 주차 계산
# ============================================================
semester_starts = {
    ("2023", "1학기"): pd.Timestamp("2023-03-02"),
    ("2023", "2학기"): pd.Timestamp("2023-09-01"),
    ("2024", "1학기"): pd.Timestamp("2024-03-04"),
    ("2024", "2학기"): pd.Timestamp("2024-09-02"),
    ("2025", "1학기"): pd.Timestamp("2025-03-03"),
    ("2025", "2학기"): pd.Timestamp("2025-09-01"),
}


def get_semester_info(date):
    year = str(date.year)
    if year not in ["2023", "2024", "2025"]:
        return None, None

    sem_key = "1학기" if date < pd.Timestamp(f"{year}-08-01") else "2학기"
    start = semester_starts[(year, sem_key)]
    week = ((date - start).days // 7) + 1
    return f"{year} {sem_key}", week


df[["학기", "주차"]] = df["날짜"].apply(lambda d: pd.Series(get_semester_info(d)))
df = df[df["주차"].between(1, 16)]

# ============================================================
# 5) 매핑값 기반 자동 특징 생성
# ============================================================
menu_mean_map = df.groupby("메뉴명")["실제식수"].mean()
cate_mean_map = df.groupby("메뉴카테고리")["실제식수"].mean()
global_mean = float(df["실제식수"].mean())
freq_map = df["메뉴명"].value_counts(normalize=True)

# 모델이 요구하는 feature 순서
features = [
    "학기", "주차", "요일", "주중주말", "공휴일", "시험주",
    "메뉴명", "메뉴카테고리", "끼니",
    "메뉴평균식수", "카테고리평균식수", "메뉴재등장빈도",
    "판매가", "원가율"
]


# ============================================================
# 6) 입력값 → 모델 입력 변환
# ============================================================
def prepare_input(sample_dict):
    s = sample_dict.copy()

    # 원가율 자동 계산
    s["원가율"] = (float(s["원가"]) / float(s["판매가"])) * 100

    # 자동 보완
    s["메뉴평균식수"] = float(menu_mean_map.get(s["메뉴명"], cate_mean_map.get(s["메뉴카테고리"], global_mean)))
    s["카테고리평균식수"] = float(cate_mean_map.get(s["메뉴카테고리"], global_mean))
    s["메뉴재등장빈도"] = int(df[df["메뉴명"] == s["메뉴명"]].shape[0])

    # DataFrame 변환
    X_one = pd.DataFrame([s])

    # 메뉴명 → 빈도 인코딩(log1p)
    X_one["메뉴명"] = np.log1p(X_one["메뉴명"].map(freq_map).fillna(0))

    # feature 순서 맞춤
    for col in features:
        if col not in X_one.columns:
            X_one[col] = 0

    return X_one[features]


unique_menus = sorted(df["메뉴명"].dropna().unique().tolist())

# ============================================================
# 7) UI 구성
# ============================================================
st.subheader("입력값 설정")

left, right = st.columns(2)

# ---------- LEFT ----------
with left:
    학기 = st.selectbox("학기", sorted(df["학기"].dropna().unique()))
    주차 = st.number_input("주차(1~16)", min_value=1, max_value=16, value=3)
    요일 = st.selectbox("요일", ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    주중주말 = st.selectbox("주중/주말", ["주중", "주말"])
    공휴일 = st.selectbox("공휴일 여부 (0/1)", [0, 1])
    시험주 = st.selectbox("시험주 여부 (0/1)", [0, 1])

# ---------- RIGHT ----------
with right:
    메뉴명 = st.selectbox("메뉴명", options=unique_menus,
                       index=unique_menus.index("제육볶음") if "제육볶음" in unique_menus else 0)

    메뉴카테고리 = categorize_menu(메뉴명)
    st.write(f"자동 분류: **{메뉴카테고리}**")

    끼니 = st.selectbox("끼니", sorted(set(k.strip() for k in df["끼니"].dropna())))
    판매가 = st.number_input("판매가", min_value=4000, max_value=6000, value=5000)
    원가 = st.number_input("원가", min_value=0, max_value=8000, value=2500)

# ============================================================
# 8) 예측하기
# ============================================================
st.markdown("<br>", unsafe_allow_html=True)
_, mid, _ = st.columns([1, 2, 1])

with mid:
    if st.button("예측하기", key="predict", type="primary"):
        sample = {
            "학기": 학기, "주차": 주차, "요일": 요일, "주중주말": 주중주말,
            "공휴일": 공휴일, "시험주": 시험주,
            "메뉴명": 메뉴명, "메뉴카테고리": 메뉴카테고리, "끼니": 끼니,
            "판매가": 판매가, "원가": 원가
        }

        X_input = prepare_input(sample)
        pred = model.predict(X_input)[0]

        st.success(f"예상 식수: {pred:.1f} 명")

        # 기록 저장
        record = sample.copy()
        record["예측값"] = round(pred, 1)
        st.session_state["history"].append(record)

# ============================================================
# 9) 예측 이력
# ============================================================
st.markdown("## 예측 이력")

if len(st.session_state["history"]) == 0:
    st.info("아직 예측 기록이 없습니다.")
else:
    st.dataframe(pd.DataFrame(st.session_state["history"]))
