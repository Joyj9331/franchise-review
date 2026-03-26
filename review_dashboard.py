import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# ⚙️ 1. 페이지 기본 설정 및 공식 브랜드 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 평판관리", page_icon="🐟", layout="wide")

# (주)새모양에프앤비 - 프리미엄 B2B 어드민 UI 적용
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
        color: #111111 !important;
    }
    
    /* 전체 배경: 깨끗하고 전문적인 라이트 그레이 */
    .stApp {
        background-color: #F4F6F8;
    }
    
    /* 사이드바: 깨끗한 화이트로 변경하여 로고와 자연스럽게 어우러지게 함 */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #EAEAEA;
    }
    [data-testid="stSidebar"] * {
        color: #333333 !important; /* 글씨를 진한 회색/검정으로 변경 */
    }
    
    /* 상단 요약 카드 디자인 */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border-left: 5px solid #D32F2F; 
    }
    
    /* 💡 완벽하게 비율이 조정된 프리미엄 로그인 박스 */
    .login-wrapper {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 8vh;
        margin-bottom: 2vh;
    }
    .login-container {
        background-color: #FFFFFF;
        padding: 40px 50px; 
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.06);
        text-align: center;
        border-top: 5px solid #D32F2F;
        width: 100%;
    }
    .brand-title {
        color: #111111;
        font-size: 24px;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    .brand-subtitle {
        color: #888888;
        font-size: 13px;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    /* 버튼 통합 디자인 (고급스러운 레드) */
    .stButton > button {
        background-color: #D32F2F !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 6px !important;
        border: none !important;
        height: 42px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 5px rgba(211,47,47,0.2);
    }
    .stButton > button:hover {
        background-color: #B71C1C !important;
        box-shadow: 0 4px 8px rgba(211,47,47,0.3);
    }
    
    /* 데이터프레임 테두리 깔끔하게 */
    [data-testid="stDataFrame"] {
        border-radius: 8px;
        overflow: hidden;
        border: 1px solid #EAEAEA;
        background-color: #FFFFFF;
    }

    /* 💡 To-Do 리스트 전용 프리미엄 카드 UI (촌스러운 노란 박스 제거) */
    .review-card {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        border-left: 4px solid #D32F2F;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 15px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
    }
    .review-card-header {
        font-weight: 700;
        color: #111111;
        font-size: 16px;
        margin-bottom: 8px;
    }
    .review-card-date {
        font-weight: 400;
        color: #888888;
        font-size: 13px;
        margin-left: 10px;
    }
    .review-card-body {
        color: #444444;
        font-size: 15px;
        line-height: 1.6;
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
        # 로그인 창 폭을 최적화
        col1, col2, col3 = st.columns([1, 1.2, 1])
        with col2:
            st.markdown("""
            <div class="login-wrapper">
                <div class="login-container">
                    <!-- 💡 로고와 텍스트의 황금 비율 적용 -->
                    <img src="https://dalbitgo.com/images/main_logo.png" style="height: 55px; object-fit: contain;">
                    <div class="brand-title">본사 통합 평판관리</div>
                    <div class="brand-subtitle">프리미엄 450°C 화덕 생선구이 전문점</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.text_input("🔑 본사 직원 인증 코드 (비밀번호)를 입력하십시오.", type="password", on_change=password_entered, key="password", placeholder="여기를 클릭하여 입력하세요")
            
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
# 조치 완료된 리뷰를 기억하는 세션 상태 초기화
if 'resolved_reviews' not in st.session_state:
    st.session_state.resolved_reviews = []

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
            "매장명": ["달빛에구운고등어 어양점", "달빛에구운고등어 첨단점", "달빛에구운고등어 군산미장점"],
            "작성일": ["2026-03-26", "2026-03-26", "2026-03-26"],
            "리뷰내용": ["화덕에 구워서 육즙이 살아있어요!", "웨이팅이 너무 길어서 화가 났습니다.", "직원분이 불친절했어요."],
            "감정분석": ["긍정", "부정", "부정"]
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

# 💡 사이드바: 화이트 톤으로 변경하여 로고 원본 색상이 완벽하게 표현됨
st.sidebar.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 80%;">
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #666666 !important; font-weight: 500;'>가맹관리팀 슈퍼바이저 패널</p>", unsafe_allow_html=True)
st.sidebar.divider()

menu = st.sidebar.radio("🔎 데이터 분석 메뉴", ["전체 브랜드 평판 현황", "개별 가맹점 집중 분석"])
st.sidebar.divider()

if st.sidebar.button("🔄 최신 데이터 동기화", use_container_width=True):
    st.rerun()

st.sidebar.write("")
st.sidebar.info("💡 **슈퍼바이저 업무 팁**\n\n'위험 감지' 리스트에 노출된 매장은 익일 오전 해피콜 및 식자재 발주 확인 시 우선 점검하십시오.")

st.sidebar.divider()
st.sidebar.markdown("""
<div style='font-size: 11px; color: #888888; text-align: center; line-height: 1.5;'>
    <b>(주)새모양에프앤비</b><br>
    사업자등록번호: 418-81-51015<br>
    전북특별자치도 전주시 덕진구 사거리길49<br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ------------------------------------------
# 메뉴 1. 전체 브랜드 평판
# ------------------------------------------
if menu == "전체 브랜드 평판 현황":
    st.markdown("<h1>전체 가맹점 평판 리포트 <span style='font-size: 18px; color: #999;'>| Daily Dashboard</span></h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='margin-top: 30px; color: #111111 !important;'>🚨 즉각 조치 요망 매장 (To-Do List)</h3>", unsafe_allow_html=True)
    
    # 부정 리뷰 추출 및 조치 완료된 항목 필터링
    negative_df = df[df['감정분석'] == '부정'].copy()
    active_negative_df = negative_df[~negative_df.index.isin(st.session_state.resolved_reviews)]
    
    if not active_negative_df.empty:
        st.markdown(f"<div style='color: #D32F2F; font-size: 15px; margin-bottom: 15px;'>⚠️ <b>총 {len(active_negative_df)}건</b>의 부정/불만 리뷰가 남아있습니다. 해피콜 조치 후 '완료' 버튼을 눌러주십시오.</div>", unsafe_allow_html=True)
        
        # 💡 촌스러운 노란 박스(st.warning)를 버리고, CSS로 만든 프리미엄 카드 UI 적용
        for idx, row in active_negative_df.iterrows():
            with st.container():
                col_text, col_btn = st.columns([0.88, 0.12])
                with col_text:
                    st.markdown(f"""
                    <div class="review-card">
                        <div class="review-card-header">
                            [{row['매장명']}] <span class="review-card-date">{row['작성일']}</span>
                        </div>
                        <div class="review-card-body">💬 {row['리뷰내용']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    st.write("") 
                    st.write("") 
                    if st.button("✅ 조치 완료", key=f"resolve_{idx}", use_container_width=True):
                        st.session_state.resolved_reviews.append(idx)
                        st.rerun() 
    else:
        st.success("🎉 현재 조치가 필요한 부정/불만 리뷰가 없습니다. 가맹점 관리가 완벽하게 이루어지고 있습니다!")
        
    st.divider()
    
    st.markdown("<h3 style='margin-top: 30px;'>📊 누적 고객 반응 모니터링</h3>", unsafe_allow_html=True)
    review_counts = df['매장명'].value_counts().reset_index()
    review_counts.columns = ['매장명', '누적 리뷰 수']
    
    col_top, col_bottom = st.columns(2)
    with col_top:
        st.markdown("<b style='font-size: 16px; color: #2E7D32;'>🔥 고객 반응 우수 매장 (리뷰 활성화)</b>", unsafe_allow_html=True)
        st.dataframe(review_counts.head(5), use_container_width=True)
    with col_bottom:
        st.markdown("<b style='font-size: 16px; color: #D32F2F;'>❄️ 리뷰 관리 필요 매장 (온라인 홍보 저조)</b>", unsafe_allow_html=True)
        st.dataframe(review_counts.tail(5).sort_values(by='누적 리뷰 수', ascending=True).reset_index(drop=True), use_container_width=True)

# ------------------------------------------
# 메뉴 2. 개별 가맹점 분석
# ------------------------------------------
else:
    st.markdown("<h1>가맹점 상세 분석 <span style='font-size: 18px; color: #999;'>| Store Details</span></h1>", unsafe_allow_html=True)
    
    # 검색 기능
    st.markdown("<div style='margin-top: 20px; margin-bottom: -15px;'><b style='font-size: 14px; color: #666;'>🔍 매장명 검색</b></div>", unsafe_allow_html=True)
    search_query = st.text_input(" ", placeholder="예: 첨단, 어양 (검색 즉시 아래 목록이 필터링됩니다)")
    
    if search_query:
        # 띄어쓰기 무시하고 검색어 포함 여부 확인
        filtered_stores = [store for store in full_store_list if search_query.replace(" ", "") in store.replace(" ", "")]
    else:
        filtered_stores = full_store_list
        
    if not filtered_stores:
        st.warning(f"'{search_query}'에 해당하는 매장이 없습니다. 검색어를 다시 확인해주세요.")
    else:
        selected_store = st.selectbox("📌 조회할 매장을 선택하십시오", filtered_stores)
        
        store_df = df[df['매장명'] == selected_store]
        
        if store_df.empty:
            st.info(f"ℹ️ 아직 [{selected_store}]에 수집된 누적 리뷰 데이터가 없습니다.")
        else:
            st.markdown(f"<h3 style='margin-top: 30px; margin-bottom: 20px;'>[{selected_store}] 고객 반응 요약</h3>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1: st.metric("누적 전체 리뷰", f"{len(store_df)}건")
            with col2: st.metric("긍정 평가 (맛/서비스 만족)", f"{len(store_df[store_df['감정분석'] == '긍정'])}건")
            with col3: st.metric("부정 평가 (개선 필요)", f"{len(store_df[store_df['감정분석'] == '부정'])}건")
            
            st.divider()
            
            col_chart, col_list = st.columns([1, 2])
            
            with col_chart:
                st.markdown("<b style='font-size: 16px;'>누적 감정 비율</b>", unsafe_allow_html=True)
                sentiment_counts = store_df['감정분석'].value_counts().reset_index()
                sentiment_counts.columns = ['감정', '비율']
                fig = px.pie(sentiment_counts, values='비율', names='감정', color='감정', color_discrete_map={'긍정':'#111111', '부정':'#D32F2F', '중립':'#AAAAAA'})
                fig.update_layout(margin=dict(t=20, b=0, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig, use_container_width=True)
                
            with col_list:
                st.markdown("<b style='font-size: 16px;'>최신 리뷰 상세 내역</b>", unsafe_allow_html=True)
                display_df = store_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False).reset_index(drop=True)
                st.dataframe(display_df, use_container_width=True)
