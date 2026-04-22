import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정
st.set_page_config(page_title="자동차보험 성과 대시보드", layout="wide")

# 2. 커스텀 CSS (상단 KPI 박스 디자인)
st.markdown("""
    <style>
    [data-testid="stMetric"] {
        background-color: #ffffff;
        padding: 15px 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
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
    # 주차 계산 (월-주차 형태)
    df['주차'] = df['날짜'].dt.strftime('%m월 %U주')
    return df

df = load_data()

# 4. 상단 KPI 섹션 (박스 처리 적용)
st.subheader("📍 핵심 요약")
col1, col2, col3 = st.columns(3)

# 누적 전환율 계산
total_new_rate = round((df['신규_가입'].sum() / df['신규_산출'].sum()) * 100, 1)
total_renew_rate = round((df['갱신_가입'].sum() / df['갱신_산출'].sum()) * 100, 1)
avg_total = round(((df['신규_가입'].sum() + df['갱신_가입'].sum()) / (df['신규_산출'].sum() + df['갱신_산출'].sum())) * 100, 1)

with col1:
    st.metric("누적 평균 전환율", f"{avg_total}%")
with col2:
    st.metric("신규 차량 전환율", f"{total_new_rate}%")
with col3:
    st.metric("갱신 차량 전환율", f"{total_renew_rate}%", "월말 보정 반영")

st.markdown("---")

# 5. 차트 섹션
tab1, tab2 = st.tabs(["📅 주별 추이 (평균)", "📊 월별 누적 현황"])

with tab1:
    st.subheader("주차별 평균 전환율 (데이터 레이블 포함)")
    # 주차별 평균 계산
    weekly_df = df.groupby('주차').agg({
        '신규_산출': 'sum', '신규_가입': 'sum',
        '갱신_산출': 'sum', '갱신_가입': 'sum'
    }).reset_index()
    weekly_df['신규_전환율'] = round((weekly_df['신규_가입'] / weekly_df['신규_산출']) * 100, 1)
    weekly_df['갱신_전환율'] = round((weekly_df['갱신_가입'] / weekly_df['갱신_산출']) * 100, 1)

    fig_week = go.Figure()
    # 신규 라인
    fig_week.add_trace(go.Scatter(
        x=weekly_df['주차'], y=weekly_df['신규_전환율'],
        name='신규 차량', mode='lines+markers+text',
        text=weekly_df['신규_전환율'].astype(str) + '%',
        textposition="top center",
        line=dict(color='#3498db', width=2)
    ))
    # 갱신 라인
    fig_week.add_trace(go.Scatter(
        x=weekly_df['주차'], y=weekly_df['갱신_전환율'],
        name='갱신 차량', mode='lines+markers+text',
        text=weekly_df['갱신_전환율'].astype(str) + '%',
        textposition="bottom center",
        line=dict(color='#e67e22', width=3)
    ))
    
    fig_week.update_layout(hovermode="x unified", yaxis_title="전환율 (%)", template="plotly_white", height=500)
    st.plotly_chart(fig_week, use_container_width=True)

with tab2:
    st.subheader("월별 누적 성과 (데이터 레이블 포함)")
    df['월'] = df['날짜'].dt.strftime('%m월')
    monthly_df = df.groupby('월').agg({
        '신규_산출': 'sum', '신규_가입': 'sum',
        '갱신_산출': 'sum', '갱신_가입': 'sum'
    }).reset_index()
    monthly_df['신규_전환율'] = round((monthly_df['신규_가입'] / monthly_df['신규_산출']) * 100, 1)
    monthly_df['갱신_전환율'] = round((monthly_df['갱신_가입'] / monthly_df['갱신_산출']) * 100, 1)

    fig_month = px.bar(
        monthly_df, x='월', y=['신규_전환율', '갱신_전환율'],
        barmode='group',
        text_auto='.1f', # 자동으로 레이블 표시
        title="월간 평균 전환율 비교",
        color_discrete_map={'신규_전환율': '#3498db', '갱신_전환율': '#e67e22'}
    )
    fig_month.update_traces(textsuffix="%", textposition="outside")
    fig_month.update_layout(yaxis_title="전환율 (%)", template="plotly_white")
    st.plotly_chart(fig_month, use_container_width=True)

# 6. 사이드바
st.sidebar.markdown("### ⚙️ 설정")
if st.sidebar.button("데이터 새로고침"):
    st.cache_data.clear()
    st.rerun()
