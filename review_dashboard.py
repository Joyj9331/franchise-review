import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# ⚙️ 1. 페이지 기본 설정 및 브랜드 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 평판관리", page_icon="🌙", layout="wide")

# 브랜드 맞춤형 CSS (네이비 & 골드 테마)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700;900&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    /* 전체 배경색 (아주 옅은 웜그레이) */
    .stApp {
        background-color: #F8F9FA;
    }
    
    /* 사이드바 테마 (밤하늘 네이비) */
    [data-testid="stSidebar"] {
        background-color: #152238 !important;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important;
    }
    
    /* 제목 및 강조 텍스트 (네이비) */
    h1, h2, h3 {
        color: #152238 !important;
        font-weight: 800 !important;
    }
    
    /* 메트릭(숫자 요약) 카드 디자인 */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-left: 6px solid #E8B923; /* 달빛 골드 포인트 */
    }
    
    /* 로그인 박스 전용 디자인 */
    .login-container {
        background-color: #FFFFFF;
        padding: 50px;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        text-align: center;
        border-top: 8px solid #E8B923;
        margin-top: 50px;
    }
    .brand-title {
        color: #152238;
        font-size: 32px;
        font-weight: 900;
        margin-bottom: 10px;
    }
    .brand-subtitle {
        color: #666666;
        font-size: 16px;
        margin-bottom: 30px;
    }
    
    /* 버튼 디자인 (골드) */
    .stButton > button {
        background-color: #E8B923 !important;
        color: #152238 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        height: 45px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #152238 !important;
        color: #E8B923 !important;
    }
    
    /* 데이터프레임 테두리 둥글게 */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 🔒 2. 브랜드 맞춤형 보안 로그인 시스템
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == "51015":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown("""
            <div class="login-container">
                <div class="brand-title">🌙 달빛에구운고등어</div>
                <div class="brand-subtitle">가맹점 통합 평판관리 시스템 (본사 전용)</div>
            </div>
            """, unsafe_allow_html=True)
            st.write("")
            st.text_input("본사 직원 인증 코드를 입력하십시오.", type="password", on_change=password_entered, key="password")
            
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ 인증 코드가 일치하지 않습니다.")
        return False
    else:
        return True

if not check_password():
    st.stop()


# ==========================================
# 📊 3. 대시보드 본문 (인증된 직원 전용)
# ==========================================
def load_data():
    filename_new = "가맹점_리뷰수집결과_누적.csv"
    filename_old = "가맹점_리뷰수집결과_20260325.csv"
    
    df_list = []
    if os.path.exists(filename_old):
        df_list.append(pd.read_csv(filename_old))
    if os.path.exists(filename_new):
        df_list.append(pd.read_csv(filename_new))
        
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        df.drop_duplicates(subset=['매장명', '작성일', '리뷰내용'], keep='last', inplace=True)
        return df
    else:
        # 데이터가 없을 때의 UI용 샘플
        data = {
            "매장명": ["달빛에구운고등어 심학산점", "달빛에구운고등어 강남점"],
            "작성일": ["2026-03-26", "2026-03-26"],
            "리뷰내용": ["고등어가 겉바속촉 너무 맛있어요!", "직원분 응대가 조금 아쉬웠습니다."],
            "감정분석": ["긍정", "부정"]
        }
        return pd.DataFrame(data)

def load_store_list():
    excel_file = "가맹점_리뷰링크.xlsx"
    if os.path.exists(excel_file):
        try:
            store_df = pd.read_excel(excel_file)
            if '매장명' in store_df.columns:
                return sorted(store_df['매장명'].dropna().unique().tolist())
        except: pass
    return []

df = load_data()
full_store_list = load_store_list()
if not full_store_list:
    full_store_list = sorted(df['매장명'].unique().tolist()) if not df.empty else ["매장 없음"]

# 사이드바 (메뉴)
st.sidebar.markdown("<h2 style='color: #E8B923 !important; text-align: center;'>🌙 달빛 비서</h2>", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 14px; opacity: 0.8;'>가맹관리팀 전용 패널</p>", unsafe_allow_html=True)
st.sidebar.divider()

menu = st.sidebar.radio("🔎 분석 메뉴 선택", ["전체 브랜드 평판 현황", "개별 가맹점 집중 분석"])
st.sidebar.divider()

if st.sidebar.button("🔄 최신 데이터 동기화"):
    st.rerun()
    
st.sidebar.info("💡 **슈퍼바이저 업무 팁**\n\n'위험 감지' 리스트에 노출된 매장은 익일 오전 해피콜 및 신규 발주 확인 시 우선순위로 배정하십시오.")

# ------------------------------------------
# 메뉴 1. 전체 브랜드 평판
# ------------------------------------------
if menu == "전체 브랜드 평판 현황":
    st.markdown("<h1>전체 가맹점 평판 리포트 <span style='font-size: 20px; color: #888;'>| Daily Dashboard</span></h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 30px; color: #D32F2F !important;'>🚨 즉각 조치 요망 매장 (CS 리스크 감지)</h3>", unsafe_allow_html=True)
    negative_df = df[df['감정분석'] == '부정']
    
    if not negative_df.empty:
        st.error(f"⚠️ **총 {len(negative_df)}건**의 부정/불만 리뷰가 감지되었습니다. 아래 내역을 확인하고 해당 점주님께 연락해 주십시오.")
        st.dataframe(negative_df[['매장명', '리뷰내용', '작성일']].sort_values(by='작성일', ascending=False).reset_index(drop=True), use_container_width=True)
    else:
        st.success("🎉 현재 감지된 부정/불만 리뷰가 없습니다. 전체 가맹점의 서비스 품질이 우수하게 유지되고 있습니다.")
        
    st.divider()
    
    st.markdown("<h3 style='margin-top: 30px;'>📊 누적 고객 반응 모니터링</h3>", unsafe_allow_html=True)
    review_counts = df['매장명'].value_counts().reset_index()
    review_counts.columns = ['매장명', '누적 리뷰 수']
    
    col_top, col_bottom = st.columns(2)
    with col_top:
        st.info("🔥 고객 반응 우수 매장 (리뷰 활성화)")
        st.dataframe(review_counts.head(5), use_container_width=True)
    with col_bottom:
        st.warning("❄️ 리뷰 관리 필요 매장 (온라인 홍보 저조)")
        st.dataframe(review_counts.tail(5).sort_values(by='누적 리뷰 수', ascending=True).reset_index(drop=True), use_container_width=True)

# ------------------------------------------
# 메뉴 2. 개별 가맹점 분석
# ------------------------------------------
else:
    st.markdown("<h1>가맹점 상세 분석 <span style='font-size: 20px; color: #888;'>| Store Details</span></h1>", unsafe_allow_html=True)
    selected_store = st.selectbox("📌 집중 분석할 매장을 선택하십시오", full_store_list)
    
    store_df = df[df['매장명'] == selected_store]
    
    if store_df.empty:
        st.info(f"ℹ️ 아직 [{selected_store}]에 수집된 누적 리뷰 데이터가 없습니다.")
    else:
        st.markdown(f"<h3 style='margin-top: 20px; color: #152238;'>[{selected_store}] 고객 반응 요약</h3>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("누적 전체 리뷰", f"{len(store_df)}건")
        with col2: st.metric("긍정 평가 (맛/서비스 만족)", f"{len(store_df[store_df['감정분석'] == '긍정'])}건")
        with col3: st.metric("부정 평가 (개선 필요)", f"{len(store_df[store_df['감정분석'] == '부정'])}건")
            
        st.divider()
        col_chart, col_list = st.columns([1, 2])
        
        with col_chart:
            st.markdown("<b style='color: #152238; font-size: 18px;'>누적 감정 비율</b>", unsafe_allow_html=True)
            sentiment_counts = store_df['감정분석'].value_counts().reset_index()
            sentiment_counts.columns = ['감정', '비율']
            # 차트 색상: 긍정(안정적인 초록), 부정(명확한 경고 빨강), 중립(회색)
            fig = px.pie(sentiment_counts, values='비율', names='감정', color='감정', color_discrete_map={'긍정':'#2E7D32', '부정':'#D32F2F', '중립':'#9E9E9E'})
            fig.update_layout(margin=dict(t=20, b=0, l=0, r=0))
            st.plotly_chart(fig, use_container_width=True)
            
        with col_list:
            st.markdown("<b style='color: #152238; font-size: 18px;'>최신 리뷰 상세 내역</b>", unsafe_allow_html=True)
            display_df = store_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False).reset_index(drop=True)
            st.dataframe(display_df, use_container_width=True)
