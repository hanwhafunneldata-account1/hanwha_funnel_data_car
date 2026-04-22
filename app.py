import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="한화손해보험 대시보드", layout="wide")

# 2. 배경색 및 지표 박스 강제 스타일링 (다크 회색 테마)
st.markdown("""
    <style>
    /* 전체 배경을 중간 회색톤으로 변경 */
    .stApp {
        background-color: #2B2B2B !important;
    }
    
    /* 사이드바 배경색 조정 */
    [data-testid="stSidebar"] {
        background-color: #1E1E1E !important;
    }

    /* 사이드바 한화 로고 박스 */
    .hanwha-header {
        background-color: #FF6600 !important;
        color: white !important;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 10px;
    }
    
    /* KPI 메트릭 박스 (연한 오렌지 배경 - 회색 배경 위에서 눈에 띄게) */
    div[data-testid="stMetric"] {
        background-color: #FFF5E6 !important;
        border: 1px solid #FFCC80 !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
    }
    
    /* KPI 내 모든 텍스트를 검정색으로 강제 (배경이 연한 오렌지이므로) */
    div[data-testid="stMetricLabel"] > div {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 16px !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
        font-weight: 800 !important;
        font-size: 32px !important;
    }
    
    /* 일반 텍스트 및 제목 색상 (회색 배경에 맞게 흰색/연회색으로) */
    h1, h2, h3, p, .stMarkdown {
        color: #FFFFFF !important;
    }
    
    /* 탭 메뉴 텍스트 색상 */
    button[data-baseweb="tab"] p {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 사이드바 구성
st.sidebar.markdown('<div class="hanwha-header">HANWHA</div>', unsafe_allow_html=True)
st.sidebar.info("자동차보험 전환율 분석 시스템")

# 4. 데이터 로직
@st.cache_data
def get_data():
    import pandas as pd
    import numpy as np
    dates = pd.date_range(start="2026-01-01", end="2026-04-21")
    df = pd.DataFrame({
        "날짜": dates,
        "신규_산출": [150 + (i % 7) * 10 for i in range(len(dates))],
        "신규_가입": [50 + (i % 7) * 4 for i in range(len(dates))],
        "갱신_산출": [450 + (i % 5) * 20 for i in range(len(dates))],
        "갱신_가입": [200 + (i % 5) * 15 if i % 30 < 25 else 280 for i in range(len(dates))]
    })
    df['주차'] = df['날짜'].dt.strftime('%m월 %U주')
    return df

df = get_data()

# 5. 메인 화면
st.title("🚗 자동차보험 전환율 성과 분석")
st.markdown("### 주요 지표 요약")

# 핵심 지표 박스 섹션
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("전체 평균 전환율", "48.2%")
with c2:
    st.metric("신규 차량 전환율", "32.5%")
with c3:
    st.metric("갱신 차량 전환율", "50.3%", "월말 보정")

st.markdown("---")

# 6. 차트 (다크 테마에 어울리는 차트 설정)
t1, t2 = st.tabs(["📅 주별 추이", "📊 월별 현황"])

with t1:
    weekly = df.groupby('주차').sum(numeric_only=True).reset_index()
    weekly['신규_전환율'] = (weekly['신규_가입'] / weekly['신규_산출'] * 100).round(1)
    weekly['갱신_전환율'] = (weekly['갱신_가입'] / weekly['갱신_산출'] * 100).round(1)
    
    fig = px.line(weekly, x='주차', y=['신규_전환율', '갱신_전환율'], markers=True, 
                  color_discrete_sequence=['#3498db', '#FF6600'])
    
    # 차트 내부 배경도 어둡게 설정
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color="white", title_font_color="white",
        legend_title_font_color="white"
    )
    fig.update_traces(texttemplate='%{y}%', textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

with t2:
    df['월'] = df['날짜'].dt.strftime('%m월')
    monthly = df.groupby('월').sum(numeric_only=True).reset_index()
    monthly['신규_전환율'] = (monthly['신규_가입'] / monthly['신규_산출'] * 100).round(1)
    monthly['갱신_전환율'] = (monthly['갱신_가입'] / monthly['갱신_산출'] * 100).round(1)
    
    fig2 = px.bar(monthly, x='월', y=['신규_전환율', '갱신_전환율'], barmode='group',
                  color_discrete_sequence=['#3498db', '#FF6600'])
    
    fig2.update_layout(
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        font_color="white"
    )
    fig2.update_traces(texttemplate='%{y}%', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)
