import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="한화손해보험 성과 대시보드", layout="wide")

# 2. 강력한 CSS 스타일 (중간 회색 배경 + 우측 상단 로고 + KPI 블랙 글자)
st.markdown("""
    <style>
    /* 전체 배경색: 중간 회색 */
    .stApp {
        background-color: #2B2B2B !important;
    }

    /* 우측 상단 로고 배치 */
    .logo-container {
        position: absolute;
        top: -60px;
        right: 0px;
        z-index: 1001;
    }
    .logo-container img {
        width: 180px; /* 적당한 로고 크기 */
    }

    /* KPI 박스: 연한 오렌지 배경 */
    div[data-testid="stMetric"] {
        background-color: #FFF5E6 !important;
        border: 2px solid #FFCC80 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
    }

    /* 박스 내부 모든 텍스트 블랙 강제 고정 */
    div[data-testid="stMetricLabel"] p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 32px !important;
    }
    div[data-testid="stMetricDelta"] > div {
        color: #E67E22 !important;
        font-weight: bold !important;
    }

    /* 메인 타이틀 및 텍스트 색상 (White) */
    h1, h2, h3, .stMarkdown p, span {
        color: #FFFFFF !important;
    }
    
    /* 탭 디자인 */
    button[data-baseweb="tab"] p {
        color: #FFFFFF !important;
        font-size: 16px !important;
    }
    </style>
    
    <div class="logo-container">
        <img src="https://www.hanwhainsure.com/img/common/logo.png" alt="한화손해보험 로고">
    </div>
    """, unsafe_allow_html=True)

# 3. 메인 타이틀 (원래 구조 유지)
st.title("🚗 자동차보험 전환율 성과 분석")
st.markdown("### 주요 지표 및 주차별/월별 추이")

# 4. 데이터 로직
@st.cache_data
def get_data():
    dates = pd.date_range(start="2026-01-01", end="2026-04-21")
    df = pd.DataFrame({
        "날짜": dates,
        "신규_산출": [160 + (i % 7) * 5 for i in range(len(dates))],
        "신규_가입": [52 + (i % 7) * 2 for i in range(len(dates))],
        "갱신_산출": [480 + (i % 5) * 15 for i in range(len(dates))],
        "갱신_가입": [235 + (i % 5) * 12 if i % 30 < 25 else 320 for i in range(len(dates))]
    })
    df['주차'] = df['날짜'].dt.strftime('%m월 %U주')
    return df

df = get_data()

# 5. KPI 지표 섹션 (연한 오렌지 박스 + 블랙 글씨)
st.subheader("📍 핵심 요약")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="누적 평균 전환율", value="48.9%")
with col2:
    st.metric(label="신규 차량 전환율", value="33.4%")
with col3:
    st.metric(label="갱신 차량 전환율", value="52.8%", delta="보정 반영")

st.markdown("---")

# 6. 차트 분석 섹션
tab1, tab2 = st.tabs(["📅 주차별 추이", "📊 월별 현황"])

with tab1:
    weekly = df.groupby('주차').sum(numeric_only=True).reset_index()
    weekly['신규_전환율'] = (weekly['신규_가입'] / weekly['신규_산출'] * 100).round(1)
    weekly['갱신_전환율'] = (weekly['갱신_가입'] / weekly['갱신_산출'] * 100).round(1)
    
    fig = px.line(weekly, x='주차', y=['신규_전환율', '갱신_전환율'], markers=True, 
                  color_discrete_sequence=['#3498db', '#FF6600'])
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', 
        font_color="white", hovermode="x unified"
    )
    fig.update_traces(texttemplate='%{y}%', textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df['월'] = df['날짜'].dt.strftime('%m월')
    monthly = df.groupby('월').sum(numeric_only=True).reset_index()
    monthly['신규_전환율'] = (monthly['신규_가입'] / monthly['신규_산출'] * 100).round(1)
    monthly['갱신_전환율'] = (monthly['갱신_가입'] / monthly['갱신_산출'] * 100).round(1)
    
    fig2 = px.bar(monthly, x='월', y=['신규_전환율', '갱신_전환율'], barmode='group',
                  color_discrete_sequence=['#3498db', '#FF6600'])
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    fig2.update_traces(texttemplate='%{y}%', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)
