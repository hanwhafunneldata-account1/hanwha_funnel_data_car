import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# 1. 페이지 설정 및 제목
st.set_page_config(page_title="자동차보험 전환율 분석 대시보드", layout="wide")
st.title("🚗 자동차보험 산출 대비 가입 전환율 대시보드")
st.markdown("### 1월 ~ 4월(누적) 성과 분석 및 월말 보정 추이 트래킹")

# 2. 예시 데이터 생성 (질문자님이 요청하신 구조)
@st.cache_data
def load_data():
    dates = pd.date_range(start="2026-01-01", end="2026-04-21")
    data = []
    for date in dates:
        # 월말(25일 이후)로 갈수록 갱신 가입율이 높아지는 비즈니스 로직 반영
        is_month_end = date.day >= 25
        renewal_base = 0.55 if is_month_end else 0.42
        
        row = {
            "날짜": date,
            "신규_산출": 150 + (date.day % 10) * 5,
            "신규_가입": 50 + (date.day % 10) * 2,
            "갱신_산출": 450 + (date.day % 5) * 10,
            "갱신_가입": int((450 + (date.day % 5) * 10) * (renewal_base + (date.day % 3) * 0.02))
        }
        # 전환율 계산
        row["신규_전환율(%)"] = round((row["신규_가입"] / row["신규_산출"]) * 100, 2)
        row["갱신_전환율(%)"] = round((row["갱신_가입"] / row["갱신_산출"]) * 100, 2)
        data.append(row)
    return pd.DataFrame(data)

df = load_data()

# 3. 상단 주요 지표 (KPI)
latest_data = df.iloc[-1]
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("오늘 신규 전환율", f"{latest_data['신규_전환율(%)']}%")
with col2:
    st.metric("오늘 갱신 전환율", f"{latest_data['갱신_전환율(%)']}%", "보정 중")
with col3:
    total_renewal_rate = round((df['갱신_가입'].sum() / df['갱신_산출'].sum()) * 100, 2)
    st.metric("누적 갱신 전환율", f"{total_renewal_rate}%")
with col4:
    st.info("💡 월말로 갈수록 갱신 데이터가 보정됩니다.")

# 4. 탭 구성 (일별 추이 / 월별 요약)
tab1, tab2 = st.tabs(["📅 일별 추이 분석", "📊 월별 누적 현황"])

with tab1:
    st.subheader("일별 전환율 변동 추이")
    # 멀티 셀렉트 필터
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df['날짜'], y=df['신규_전환율(%)'], name='신규 차량', line=dict(color='#3498db', width=2)))
    fig.add_trace(go.Scatter(x=df['날짜'], y=df['갱신_전환율(%)'], name='갱신 차량', line=dict(color='#e67e22', width=3)))
    
    fig.update_layout(hovermode="x unified", yaxis_title="전환율 (%)", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)
    
    st.write("👉 **분석 포인트:** 갱신 차량의 경우 매월 25일 이후 전환율이 급격히 상승하는 '월말 효과'가 관찰됩니다.")

with tab2:
    st.subheader("월별 집계 데이터")
    df['월'] = df['날짜'].dt.strftime('%m월')
    monthly_df = df.groupby('월').agg({
        '신규_산출': 'sum', '신규_가입': 'sum',
        '갱신_산출': 'sum', '갱신_가입': 'sum'
    }).reset_index()
    monthly_df['신규_전환율(%)'] = round((monthly_df['신규_가입'] / monthly_df['신규_산출']) * 100, 2)
    monthly_df['갱신_전환율(%)'] = round((monthly_df['갱신_가입'] / monthly_df['갱신_산출']) * 100, 2)
    
    st.table(monthly_df)
    
    # 월별 비교 바 차트
    fig_month = px.bar(monthly_df, x='월', y=['신규_전환율(%)', '갱신_전환율(%)'], barmode='group', title="월별 신규 vs 갱신 전환율 비교")
    st.plotly_chart(fig_month, use_container_width=True)

# 5. 데이터 업로드 기능 (나중에 실제 엑셀을 넣을 수 있게 미리 구현)
st.sidebar.header("📁 데이터 업데이트")
uploaded_file = st.sidebar.file_uploader("GA4 엑셀 파일을 업로드하세요", type=["xlsx", "csv"])
if uploaded_file:
    st.sidebar.success("성공적으로 업로드되었습니다! (기능 연결 예정)")
