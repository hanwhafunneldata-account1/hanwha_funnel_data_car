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
        "유입", "정보입력 완료", "설계동의", "본인인증", "차량선택", 
        "보험료 산출", "사진등록", "피보험자 정보확인", 
        "청약내용 확인", "결제화면 진입", "전자서명 진입", "가입완료"
    ]
    counts = [10000, 8500, 7800, 7200, 6500, 5000, 4200, 3800, 3500, 3200, 3000, 2850]
    return pd.DataFrame({"단계": steps, "사용자수": counts})

df = get_data()
funnel_df = get_funnel_data()

# 4. 타이틀
st.title("🚗 자동차보험 전환율 성과 분석")

# 5. 메인 탭 구성
tab_trend, tab_monthly, tab_funnel = st.tabs(["📅 주차별 추이 분석", "📊 월별 누적 현황", "🌪️ 청약 프로세스 퍼널 분석"])

# --- TAB 1 & 2: 기존 내용 유지 ---
with tab_trend:
    st.subheader("📍 핵심 요약 (주차별)")
    col1, col2, col3 = st.columns(3)
    with col1: st.metric(label="누적 평균 전환율", value="49.2%")
    with col2: st.metric(label="신규 차량 전환율", value="33.8%")
    with col3: st.metric(label="갱신 차량 전환율", value="53.1%", delta="보정 완료")
    
    weekly = df.groupby('주차').sum(numeric_only=True).reset_index()
    weekly['신규_전환율'] = (weekly['신규_가입'] / weekly['신규_산출'] * 100).round(1)
    weekly['갱신_전환율'] = (weekly['갱신_가입'] / weekly['갱신_산출'] * 100).round(1)
    
    fig = px.line(weekly, x='주차', y=['신규_전환율', '갱신_전환율'], markers=True, 
                  color_discrete_sequence=['#3498db', '#FF6600'])
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig, use_container_width=True)

with tab_monthly:
    df['월'] = df['날짜'].dt.strftime('%m월')
    monthly = df.groupby('월').sum(numeric_only=True).reset_index()
    monthly['신규_전환율'] = (monthly['신규_가입'] / monthly['신규_산출'] * 100).round(1)
    monthly['갱신_전환율'] = (monthly['갱신_가입'] / monthly['갱신_산출'] * 100).round(1)
    
    fig2 = px.bar(monthly, x='월', y=['신규_전환율', '갱신_전환율'], barmode='group',
                  color_discrete_sequence=['#3498db', '#FF6600'])
    fig2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
    st.plotly_chart(fig2, use_container_width=True)

# --- TAB 3: 개선된 생키 다이어그램 ---
with tab_funnel:
    st.subheader("🕵️ 상세 청약 프로세스 분석 (12단계)")
    
    # 상단 핵심 전환율 3종 (기존 유지)
    c1, c2, c3 = st.columns(3)
    inflow = funnel_df.iloc[0]['사용자수']
    calc = funnel_df[funnel_df['단계'] == "보험료 산출"]['사용자수'].values[0]
    complete = funnel_df.iloc[-1]['사용자수']
    
    with c1: st.metric(label="유입 대비 산출", value=f"{(calc/inflow*100):.1f}%")
    with c2: st.metric(label="유입 대비 가입", value=f"{(complete/inflow*100):.1f}%")
    with c3: st.metric(label="산출 대비 가입", value=f"{(complete/calc*100):.1f}%")
    
    st.markdown("---")
    
    # 생키 데이터 가공
    labels = [f"{row['단계']}<br>({row['사용자수']:,}명)" for _, row in funnel_df.iterrows()]
    source = list(range(len(labels) - 1))
    target = list(range(1, len(labels)))
    values = funnel_df['사용자수'].tolist()[1:] 
    
    # 잔존율(%) 계산하여 링크 라벨로 사용
    link_labels = []
    for i in range(len(funnel_df) - 1):
        retention = (funnel_df.iloc[i+1]['사용자수'] / funnel_df.iloc[i]['사용자수']) * 100
        link_labels.append(f"{retention:.1f}% 전환")

    # 생키 다이어그램 시각화
    fig_sankey = go.Figure(data=[go.Sankey(
        node = dict(
          pad = 20,
          thickness = 30,
          line = dict(color = "white", width = 1),
          label = labels,
          color = "#FF6600", # 한화 오렌지
          customdata = funnel_df['사용자수'],
          hovertemplate = '%{label}<extra></extra>'
        ),
        link = dict(
          source = source,
          target = target,
          value = values,
          label = link_labels, # 선 위에 마우스 올릴 때 보이는 라벨
          color = "rgba(255, 102, 0, 0.3)",
          hovertemplate = '이전 단계에서 <b>%{label}</b>하여<br>총 <b>%{value:,}명</b>이 진입했습니다.<extra></extra>'
      ))])

    fig_sankey.update_layout(
        title_text="단계별 진입자 수 및 전환율 흐름 (Sankey)",
        font_size=13, 
        font_color="white", 
        paper_bgcolor='rgba(0,0,0,0)',
        height=600 # 가시성을 위해 높이 조절
    )
    
    st.plotly_chart(fig_sankey, use_container_width=True)
    
    # 하단 상세 이탈 데이터 (기존 유지)
    with st.expander("📊 화면별 이탈률 상세 데이터 보기"):
        funnel_df['이탈률'] = funnel_df['사용자수'].diff().abs() / funnel_df['사용자수'].shift(1) * 100
        funnel_df['이탈률'] = funnel_df['이탈률'].fillna(0).round(1).astype(str) + "%"
        st.table(funnel_df.set_index('단계').T)
