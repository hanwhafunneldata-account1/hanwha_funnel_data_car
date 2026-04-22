import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="한화손해보험 성과 대시보드", layout="wide")

# 2. 강력한 CSS 스타일 (중간 회색 배경 + KPI 블랙 글자 강제 고정)
st.markdown("""
    <style>
    /* 전체 배경색: 중간 회색 */
    .stApp {
        background-color: #2B2B2B !important;
    }

    /* 상단 헤더: 로고가 돋보이도록 흰색 바 적용 */
    .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #FFFFFF;
        padding: 15px 40px;
        border-radius: 12px;
        margin-bottom: 30px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .header-bar h2 {
        color: #333333 !important;
        margin: 0 !important;
        font-weight: 800 !important;
    }

    /* KPI 박스: 연한 오렌지 배경 */
    div[data-testid="stMetric"] {
        background-color: #FFF5E6 !important;
        border: 2px solid #FFCC80 !important;
        border-radius: 16px !important;
        padding: 25px !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.2) !important;
    }

    /* [최종 해결] 박스 내부 모든 텍스트 블랙 고정 */
    div[data-testid="stMetricLabel"] > div > div > p {
        color: #000000 !important;
        font-weight: bold !important;
        font-size: 18px !important;
    }
    div[data-testid="stMetricValue"] > div {
        color: #000000 !important;
        font-weight: 900 !important;
        font-size: 38px !important;
    }
    div[data-testid="stMetricDelta"] > div {
        color: #E67E22 !important;
        font-weight: bold !important;
    }

    /* 일반 텍스트 색상 (White) */
    h1, h3, .stMarkdown p, span {
        color: #FFFFFF !important;
    }
    
    /* 탭 디자인 */
    button[data-baseweb="tab"] p {
        color: #FFFFFF !important;
        font-size: 18px !important;
        font-weight: bold !important;
    }
    </style>

    <div class="header-bar">
        <svg width="200" height="40" viewBox="0 0 350 70" xmlns="http://www.w3.org/2000/svg">
            <path d="M25.5 12.3c-7.2 0-13.1 5.9-13.1 13.1s5.9 13.1 13.1 13.1 13.1-5.9 13.1-13.1-5.9-13.1-13.1-13.1zm0 21.6c-4.7 0-8.5-3.8-8.5-8.5s3.8-8.5 8.5-8.5 8.5 3.8 8.5 8.5-3.8 8.5-8.5 8.5z" fill="#F37021"/>
            <path d="M43.2 12.3c-7.2 0-13.1 5.9-13.1 13.1s5.9 13.1 13.1 13.1 13.1-5.9 13.1-13.1-5.9-13.1-13.1-13.1zm0 21.6c-4.7 0-8.5-3.8-8.5-8.5s3.8-8.5 8.5-8.5 8.5 3.8 8.5 8.5-3.8 8.5-8.5 8.5z" fill="#F37021"/>
            <path d="M34.4 27.6c-7.2 0-13.1 5.9-13.1 13.1s5.9 13.1 13.1 13.1 13.1-5.9 13.1-13.1-5.9-13.1-13.1-13.1zm0 21.6c-4.7 0-8.5-3.8-8.5-8.5s3.8-8.5 8.5-8.5 8.5 3.8 8.5 8.5-3.8 8.5-8.5 8.5z" fill="#F37021"/>
            <text x="65" y="42" font-family="Arial, sans-serif" font-weight="bold" font-size="32" fill="#333333">한화손해보험</text>
        </svg>
        <h2>전환율 성과 분석</h2>
    </div>
    """, unsafe_allow_html=True)

# 3. 데이터 로직 (날짜별 시뮬레이션)
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

# 4. KPI 지표 섹션
st.subheader("📍 주요 성과 요약")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric(label="누적 평균 전환율", value="48.9%")
with col2:
    st.metric(label="신규 차량 전환율", value="33.4%")
with col3:
    st.metric(label="갱신 차량 전환율", value="52.8%", delta="월말 보정 적용")

st.markdown("<br>", unsafe_allow_html=True)

# 5. 차트 분석
tab1, tab2 = st.tabs(["📅 주차별 추이", "📊 월별 누적"])

with tab1:
    weekly = df.groupby('주차').sum(numeric_only=True).reset_index()
    weekly['신규_전환율'] = (weekly['신규_가입'] / weekly['신규_산출'] * 100).round(1)
    weekly['갱신_전환율'] = (weekly['갱신_가입'] / weekly['갱신_산출'] * 100).round(1)
    
    fig = px.line(weekly, x='주차', y=['신규_전환율', '갱신_전환율'], markers=True, 
                  color_discrete_sequence=['#3498db', '#F37021'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white", hovermode="x unified")
    fig.update_traces(texttemplate='%{y}%', textposition='top center')
    st.plotly_chart(fig, use_container_width=True)

with tab2:
    df['월'] = df['날짜'].dt.strftime('%m월')
    monthly = df.groupby('월').sum(numeric_only=True).reset_index()
    monthly['신규_전환율'] = (monthly['신규_가입'] / monthly['신규_산출'] * 100).round(1)
    monthly['갱신_전환율'] = (monthly['갱신_가입'] / monthly['갱신_산출'] * 100).round(1)
    
    fig2 = px.bar(monthly, x='월', y=['신규_전환율', '갱신_전환율'], barmode='group',
                  color_discrete_sequence=['#3498db', '#F37021'])
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    fig2.update_traces(texttemplate='%{y}%', textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)
