import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="자동차보험 성과 대시보드", layout="wide")

# 2. CSS 주입 (기존 스타일 유지)
st.markdown("""
    <style>
    .stApp {
        background-color: #2B2B2B !important;
    }
    .logo-container {
        position: absolute;
        top: -60px;
        right: 0px;
        z-index: 1001;
    }
    .logo-container img {
        width: 180px;
    }
    div[data-testid="stMetric"] {
        background-color: #FFF5E6 !important;
        border: 2px solid #FFCC80 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
    div[data-testid="stMetric"] * {
        color: #000000 !important;
        font-weight: bold !important;
    }
    div[data-testid="stMetricValue"] > div {
        font-size: 38px !important;
        font-weight: 900 !important;
    }
    h1, h2, h3, .stMarkdown p, .stMarkdown span {
        color: #FFFFFF !important;
    }
    button[data-baseweb="tab"] p {
        color: #FFFFFF !important;
    }
    </style>
    
    <div class="logo-container">
        <img src="https://www.hanwhainsure.com/img/common/logo.png" alt="한화손해보험 로고">
    </div>
    """, unsafe_allow_html=True)

# 3. 데이터 로직 (기존 유지 + 퍼널 데이터 고도화)
@st.cache_data
def get_data():
    dates = pd.date_range(start="2026-01-01", end="2026-04-21")
    df = pd.DataFrame({
        "날짜": dates,
        "신규_산출": [160 + (i % 7) * 5 for i in range(len(dates))],
        "신규_가입": [52 + (i % 7) * 2 for i in range(len(dates))],
        "갱신_산출": [480 + (i % 5) * 15 for i in range(len(dates))],
        "갱신_가입": [240 + (i % 5) * 12 if i % 30 < 25 else 330 for i in range(len(dates))]
    })
    df['주차'] = df['날짜'].dt.strftime('%m월 %U주')
    return df

@st.cache_data
def get_funnel_data():
    steps = [
        "유입", "정보입력 완료", "
