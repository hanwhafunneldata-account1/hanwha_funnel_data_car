import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="자동차보험 성과 대시보드", layout="wide")

# 2. 커스텀 CSS (상단 KPI 박스: 연한 오렌지 배경 + 검정 글씨)
st.markdown("""
    <style>
    /* 지표 박스 스타일 */
    [data-testid="stMetric"] {
        background-color: #FFF5E6; /* 연한 오렌지색 */
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #FFE0B2;
        text-align: center;
    }
    /* 라벨(글씨) 색상을 강제로 검정색으로 설정 */
    [data-testid="stMetricLabel"] {
        color: #333333 !important;
        font-weight: bold !important;
    }
    /* 수치 색상을 강제로 검정색으로 설정 */
    [data-testid="stMetricValue"] {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("🚗 자동차보험 전환율 성과 분석")
st.markdown("### 주요 지표 및 주차별/월별 추이")

# 3. 데이터 로드 (주차별 계산 포함)
@st.cache_data
def load_data():
    dates = pd.date_range(start="2026-01-01", end="2026-04-21")
    data = []
    for date in dates:
        is_month_end = date.day >= 25
        renewal_base = 0.55 if is_month_end else 0.42
        row = {
            "날짜": date,
            "신규_산출": 150 + (date.day % 10) * 5,
            "신규_가입": 50 + (date.day % 10) * 2,
            "갱신_산출": 450 + (date.day % 5) * 10,
            "갱신_가입": int((450 + (date.day % 5) * 10) * (renewal_base + (date.day % 3) * 0.02))
        }
        data.append(row)
    df = pd.DataFrame(data)
    df['주차'] = df['날짜'].dt.strftime('%m월 %U주')
    return df

df = load_data()

# 4. 상단 KPI 섹션 (연한 오렌지 박스 적용)
st.subheader("📍 핵심 요약")
col1, col2, col3 = st.columns(3)

total_new_rate = round((df['신규_가입'].sum() / df
