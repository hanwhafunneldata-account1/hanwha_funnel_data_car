import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="한화손해보험 성과 대시보드", layout="wide")

# 2. 강력한 CSS 주입 (다크 회색 배경 + KPI 블랙 글자 고정)
st.markdown("""
    <style>
    /* 전체 배경: 중간 회색 */
    .stApp {
        background-color: #2B2B2B !important;
    }

    /* 상단 헤더 영역 */
    .custom-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #1E1E1E;
        padding: 15px 25px;
        border-radius: 12px;
        margin-bottom: 30px;
        border: 1px solid #3D3D3D;
    }
    
    .hanwha-logo-box {
        background-color: #FF6600;
        color: white !important;
        padding: 8px 25px;
        border-radius: 4px;
        font-weight: 900;
        font-size: 20px;
        letter-spacing: 2px;
        font-family: 'Arial Black', sans-serif;
    }

    /* KPI 박스 스타일: 연한 오렌지 배경 */
    div[data-testid="stMetric"] {
        background-color: #FFF5E6 !important;
        border: 2px solid #FFCC80 !important;
        border-radius: 16px !important;
        padding: 20px !important;
    }

    /* KPI 내부 텍스트 색상 강제 고정 (Black) */
    /* 수치 부분 */
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
        font-weight: 800 !important;
    }
    /* 라벨 부분 (여러 계층 대응) */
    div[data-testid="stMetricLabel"] p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 17px !important;
    }
    /* 델타(증감) 부분 */
    div[data-testid="stMetricDelta"] > div {
        color: #D35400 !important; /* 약간 진한 오렌지색으로 가독성 확보 */
    }

    /* 메인 텍스트 색상 (White) */
    h1, h2, h3, p, span, li {
        color: #FFFFFF !important;
    }
    
    /* 탭 메뉴 텍스트 */
    button[data-baseweb="tab"] p {
        color: #FFFFFF !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 3. 상단 헤더 (로고 포함)
st.markdown("""
    <div class="custom-header">
        <h2 style='margin:0; font-weight:700;'>🚗 자동차보험 전환율 성과 대시보드</h2>
        <div class="hanwha-logo-box">HANWHA</div>
    </div>
    """, unsafe_allow_html=True)

# 4. 데이터 로직
@st.cache_data
def get_data():
    dates = pd.date_range(start="2026-01-01", end="2026-04-21")
    df = pd.DataFrame({
        "날짜": dates,
        "신규_산출": [150 + (i % 7) * 8 for i in range(len(dates))],
        "신규_가입": [50 + (i % 7) * 3 for i in range(len(dates))],
        "갱신_산출": [450 + (i % 5) * 20 for i in range(len(dates))],
        "갱신_가입": [210 + (i % 5) * 12 if i % 30 < 25 else 290 for i in range(len(dates))]
    })
    df['주차'] = df['날짜'].dt.strftime('%m월 %U주')
    return df

df = get_data()

# 5. 핵심 KPI 섹션
st.subheader("📍 성과 요약")
c1, c2, c3 = st.columns(3)

with c1:
    st.metric(label="누적 평균 전환율", value="48.5%")
with c2:
    st.metric(label="신규 차량 전환율", value="32.8%")
with c3:
    st.metric(label="갱신 차량 전환율", value="51.2%", delta="보정 완료")

st.markdown("<br>", unsafe_allow_html=True)

# 6. 차트 분석 섹션
tab1, tab2 = st.tabs(["📅 주별 추이 분석", "📊 월별 누적 현황"])

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
