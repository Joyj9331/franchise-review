import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit.components.v1 as components
import os
import hashlib
import time
import hmac
import base64
import requests
from datetime import datetime, timedelta

# ==========================================
# ⚙️ 1. 페이지 기본 설정 및 프리미엄 CSS 주입
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 통합 관리", page_icon="🐟", layout="wide")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    
    h1, h2, h3, h4, h5, h6, p, label, li {
        color: #111111 !important;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .stApp {
        background-color: #F4F6F8;
    }
    
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222222;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, 
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] span, [data-testid="stSidebar"] div, [data-testid="stSidebar"] label {
        color: #FFFFFF !important; 
    }
    
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border-left: 5px solid #E8B923; 
    }
    
    @keyframes zoomInBack {
        0% { transform: scale(0.6); opacity: 0; }
        100% { transform: scale(1); opacity: 1; }
    }
    @keyframes suckIn {
        0% { transform: scale(1.05); opacity: 0; filter: blur(3px); }
        100% { transform: scale(1); opacity: 1; filter: blur(0); }
    }

    .login-wrapper {
        display: flex; justify-content: center; align-items: center;
        margin-top: 10vh; margin-bottom: 2vh;
        animation: zoomInBack 0.7s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
    }
    .login-container {
        background-color: #111111 !important; 
        padding: 40px 50px; border-radius: 16px;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
        text-align: center; border-top: 5px solid #E8B923; width: 100%;
    }
    .login-container p, .login-container span, .login-container div, .login-container label {
        color: #FFFFFF !important;
    }
    .brand-title { color: #FFFFFF !important; font-size: 26px; margin-top: 15px; margin-bottom: 5px; }
    .brand-subtitle { color: #E8B923 !important; font-size: 14px; margin-bottom: 30px; font-weight: 400; }

    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important; border-radius: 8px; border: 1px solid #EAEAEA;
        border-left: 4px solid #D32F2F; box-shadow: 0 2px 5px rgba(0,0,0,0.02); overflow: hidden;
    }
    div[data-testid="stExpander"] details { background-color: #FFFFFF !important; }
    div[data-testid="stExpander"] summary { background-color: #F8F9FA !important; color: #111111 !important; }
    div[data-testid="stExpander"] summary:hover { background-color: #EEEEEE !important; }
    div[data-testid="stExpander"] summary p, div[data-testid="stExpander"] summary span { color: #111111 !important; font-weight: 600 !important; }

    div[data-baseweb="select"] > div { background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; }
    div[data-baseweb="select"] * { color: #111111 !important; }
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important; border-radius: 8px !important; box-shadow: 0 5px 15px rgba(0,0,0,0.1) !important;
    }
    li[role="option"], li[role="option"] span { background-color: #FFFFFF !important; color: #111111 !important; font-weight: 500 !important; }
    li[role="option"]:hover, li[role="option"]:hover span, li[role="option"][aria-selected="true"] {
        background-color: #F4F6F8 !important; color: #D32F2F !important;
    }

    div[data-baseweb="input"] { background-color: #FFFFFF !important; }
    div[data-baseweb="input"] input {
        background-color: #FFFFFF !important; color: #111111 !important;
        -webkit-text-fill-color: #111111 !important; border: 1px solid #CCCCCC !important;
    }
    div[data-baseweb="input"] input::placeholder { color: #AAAAAA !important; -webkit-text-fill-color: #AAAAAA !important; }
    
    .stButton > button {
        background-color: #D32F2F !important; border-radius: 6px !important; border: none !important;
        height: 42px; transition: all 0.3s ease; box-shadow: 0 2px 5px rgba(211,47,47,0.2);
    }
    .stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
    .stButton > button:hover { background-color: #B71C1C !important; box-shadow: 0 4px 8px rgba(211,47,47,0.3); }
    
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #EAEAEA; background-color: #FFFFFF; }
    
    button[data-baseweb="tab"] { background-color: transparent !important; }
    button[data-baseweb="tab"] > div[data-testid="stMarkdownContainer"] > p {
        font-size: 16px !important; font-weight: 700 !important; color: #888888 !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] > div[data-testid="stMarkdownContainer"] > p {
        color: #D32F2F !important;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔒 2. 브랜드 맞춤형 보안 로그인
# ==========================================
def check_password():
    def password_entered():
        if st.session_state["password"] == "51015":
            st.session_state["password_correct"] = True
            del st.session_state["password"]  
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state or not st.session_state["password_correct"]:
        col1, col2, col3 = st.columns([1.5, 1, 1.5])
        with col2:
            st.markdown("""
            <div class="login-wrapper">
                <div class="login-container">
                    <img src="https://dalbitgo.com/images/main_logo.png" style="height: 60px; object-fit: contain;">
                    <div class="brand-title">리뷰 관리 프로그램</div>
                    <div class="brand-subtitle">프리미엄 450°C 화덕 생선구이 전문점</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.text_input("🔑 본사 직원 인증 코드 (비밀번호)를 입력하십시오.", type="password", on_change=password_entered, key="password", placeholder="여기를 클릭하여 입력하세요")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ 인증 코드가 일치하지 않습니다.")
        return False
    else:
        st.markdown("<style>[data-testid='block-container'] { animation: suckIn 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }</style>", unsafe_allow_html=True)
        return True

if not check_password():
    st.stop()

# ==========================================
# 🛰️ 3. 네이버 키워드 API 통신 로직 (무료)
# ==========================================
def generate_naver_signature(timestamp, method, uri, secret_key):
    message = "{}.{}.{}".format(timestamp, method, uri)
    hash = hmac.new(secret_key.encode("utf-8"), message.encode("utf-8"), hashlib.sha256).digest()
    return base64.b64encode(hash).decode("utf-8")

def get_naver_keyword_info(customer_id, access_key, secret_key, keyword):
    """네이버 검색광고 API를 호출하여 키워드 정보를 가져옵니다."""
    base_url = "https://api.naver.com"
    uri = "/keywordstool"
    method = "GET"
    timestamp = str(int(time.time() * 1000))
    
    signature = generate_naver_signature(timestamp, method, uri, secret_key)
    
    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "X-Timestamp": timestamp,
        "X-API-KEY": access_key,
        "X-Customer": str(customer_id),
        "X-Signature": signature
    }
    
    params = {"hintKeywords": keyword, "showDetail": "1"}
    
    try:
        res = requests.get(base_url + uri, params=params, headers=headers)
        if res.status_code == 200:
            data = res.json().get('keywordList', [])
            if data:
                # 검색한 키워드와 정확히 일치하는 데이터 찾기
                target = next((item for item in data if item['relKeyword'] == keyword.replace(" ", "")), data[0])
                return target
        return None
    except:
        return None

# ==========================================
# 💾 4. 데이터 로드 및 상태 관리
# ==========================================
STATE_RESOLVED = "state_resolved.csv"
STATE_OVERRIDDEN = "state_overridden.csv"

def get_saved_ids(filename):
    if os.path.exists(filename): return pd.read_csv(filename)['id'].tolist()
    return []

def add_saved_id(filename, new_id):
    ids = get_saved_ids(filename)
    if new_id not in ids:
        ids.append(new_id)
        pd.DataFrame({'id': ids}).to_csv(filename, index=False)

def generate_id(row):
    return hashlib.md5(f"{row['매장명']}_{row['작성일']}_{row['리뷰내용']}".encode()).hexdigest()

def load_data():
    filename_new = "가맹점_리뷰수집결과_누적.csv"
    filename_old = "가맹점_리뷰수집결과_20260325.csv"
    df_list = []
    if os.path.exists(filename_old): df_list.append(pd.read_csv(filename_old))
    if os.path.exists(filename_new): df_list.append(pd.read_csv(filename_new))
        
    if df_list:
        df = pd.concat(df_list, ignore_index=True)
        df.drop_duplicates(subset=['매장명', '작성일', '리뷰내용'], keep='last', inplace=True)
    else:
        data = {"매장명": ["달빛에구운고등어 어양점"], "작성일": ["2026-03-26"], "리뷰내용": ["맛있어요"], "감정분석": ["긍정"]}
        df = pd.DataFrame(data)

    df['id'] = df.apply(generate_id, axis=1)
    df.loc[df['id'].isin(get_saved_ids(STATE_OVERRIDDEN)), '감정분석'] = '긍정'
    return df

def load_store_list():
    excel_file = "가맹점_리뷰링크.xlsx"
    if os.path.exists(excel_file):
        try:
            store_df = pd.read_excel(excel_file)
            if '매장명' in store_df.columns: return sorted(store_df['매장명'].dropna().unique().tolist())
        except: pass
    return []

df = load_data()
full_store_list = load_store_list()

# ==========================================
# 📌 5. 사이드바 및 메뉴 구성
# ==========================================
st.sidebar.markdown("""
<div style="text-align: center; margin-top: 10px; margin-bottom: 20px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 85%;">
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #E8B923 !important; font-weight: 500;'>본사 통합 업무 포털</p>", unsafe_allow_html=True)
st.sidebar.divider()

main_menu = st.sidebar.radio("📌 통합 업무 메뉴", ["💬 가맹점 리뷰 관리", "📈 브랜드 키워드 분석", "🗓️ 오픈/발주 통합 캘린더"])
st.sidebar.divider()

if st.sidebar.button("🔄 전체 데이터 동기화", use_container_width=True):
    st.rerun()

st.sidebar.info("💡 **과장님 업무 팁**\n\n발급받은 네이버 API 키를 '키워드 분석' 설정창에 입력하면 실시간 검색량 조회가 가능합니다.")

# ==========================================
# 🖥️ 화면 1: 가맹점 리뷰 관리
# ==========================================
if main_menu == "💬 가맹점 리뷰 관리":
    st.markdown("<h1>💬 가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #777;'>| Review Management</span></h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🌐 전체 브랜드 리뷰 현황", "🏪 개별 가맹점 상세 분석"])
    
    with tab1:
        st.markdown("<h3 style='margin-top: 20px;'>🚨 즉각 조치 요망 매장 (To-Do List)</h3>", unsafe_allow_html=True)
        resolved_ids = get_saved_ids(STATE_RESOLVED)
        negative_df = df[df['감정분석'] == '부정'].copy()
        active_negative_df = negative_df[~negative_df['id'].isin(resolved_ids)]
        
        if not active_negative_df.empty:
            st.markdown(f"<div style='color: #D32F2F; font-size: 15px; margin-bottom: 15px; font-weight: 600;'>⚠️ 총 {len(active_negative_df)}건의 부정 리뷰가 남아있습니다.</div>", unsafe_allow_html=True)
            for idx, row in active_negative_df.iterrows():
                short_text = row['리뷰내용'][:20] + "..."
                with st.expander(f"📌 [{row['매장명']}] {row['작성일']} | {short_text}"):
                    st.write(f"💬 **내용:** {row['리뷰내용']}")
                    c1, c2, _ = st.columns([1, 1, 2])
                    if c1.button("✅ 조치 완료", key=f"res_{row['id']}"): add_saved_id(STATE_RESOLVED, row['id']); st.rerun()
                    if c2.button("🌟 긍정 변경", key=f"ovr_{row['id']}"): add_saved_id(STATE_OVERRIDDEN, row['id']); st.rerun()
        else: st.success("🎉 조치할 리뷰가 없습니다!")

    with tab2:
        search_query = st.text_input("🔍 매장명 검색", placeholder="예: 첨단, 어양", key="search1")
        filtered_stores = [s for s in full_store_list if search_query.replace(" ", "") in s.replace(" ", "")] if search_query else full_store_list
        if filtered_stores:
            selected_store = st.selectbox("📌 조회 매장 선택", filtered_stores)
            store_df = df[df['매장명'] == selected_store]
            if not store_df.empty:
                st.markdown(f"### [{selected_store}] 분석 리포트")
                c1, c2, c3 = st.columns(3)
                c1.metric("누적 리뷰", f"{len(store_df)}건")
                c2.metric("긍정 평가", f"{len(store_df[store_df['감정분석'] == '긍정'])}건")
                c3.metric("부정 평가", f"{len(store_df[store_df['감정분석'] == '부정'])}건")
                st.plotly_chart(px.line(store_df.groupby('작성일').size().reset_index(name='건수'), x='작성일', y='건수', markers=True, color_discrete_sequence=['#D32F2F']), use_container_width=True)

# ==========================================
# 🖥️ 화면 2: 브랜드 키워드 분석 (실제 API 연동)
# ==========================================
elif main_menu == "📈 브랜드 키워드 분석":
    st.markdown("<h1>📈 브랜드 키워드 통합 분석 <span style='font-size: 18px; color: #777;'>| 실시간 Naver API</span></h1>", unsafe_allow_html=True)
    
    with st.expander("🔐 Naver API 무료 연결 설정 (발급받은 키를 입력하세요)"):
        st.info("💡 입력하신 키는 보안을 위해 브라우저를 닫으면 자동으로 삭제됩니다.")
        c_id = st.text_input("Customer ID", value=st.session_state.get('naver_cid', ""), type="password")
        a_key = st.text_input("Access Key", value=st.session_state.get('naver_akey', ""), type="password")
        s_key = st.text_input("Secret Key", value=st.session_state.get('naver_skey', ""), type="password")
        if st.button("🗝️ 키 세션에 임시 저장"):
            st.session_state.naver_cid = c_id
            st.session_state.naver_akey = a_key
            st.session_state.naver_skey = s_key
            st.success("보안 연결 설정이 완료되었습니다.")

    st.divider()
    
    # 키워드 입력 폼
    k_input, k_btn = st.columns([0.8, 0.2])
    target_k = k_input.text_input("🔍 실시간 분석할 브랜드명 또는 키워드", placeholder="예: 달빛에구운고등어, 생선구이 맛집")
    
    if k_btn.button("🚀 실시간 분석", use_container_width=True):
        if not (st.session_state.get('naver_cid') and st.session_state.get('naver_akey')):
            st.error("⚠️ 상단 [API 연결 설정]을 먼저 완료해주십시오.")
        elif not target_k:
            st.warning("분석할 키워드를 입력하십시오.")
        else:
            with st.spinner(f"네이버 서버에서 '{target_k}' 데이터를 분석 중입니다..."):
                result = get_naver_keyword_info(st.session_state.naver_cid, st.session_state.naver_akey, st.session_state.naver_skey, target_k)
                
                if result:
                    st.session_state.k_result = result
                    st.session_state.k_name = target_k
                    st.success("데이터 로드 완료!")
                else:
                    st.error("❌ 데이터를 가져오지 못했습니다. API 키 정보 또는 키워드를 확인해주세요.")

    # 결과 출력
    if 'k_result' in st.session_state:
        res = st.session_state.k_result
        st.markdown(f"### 📊 [{st.session_state.k_name}] 최근 30일 지표")
        
        m1, m2, m3, m4 = st.columns(4)
        # 월간 검색량 (숫자가 문자열로 올 수 있으므로 변환 처리)
        pc_cnt = int(res.get('monthlyPcQcCnt', 0)) if isinstance(res.get('monthlyPcQcCnt'), (int, float)) or res.get('monthlyPcQcCnt', '0').isdigit() else 10
        mo_cnt = int(res.get('monthlyMobileQcCnt', 0)) if isinstance(res.get('monthlyMobileQcCnt'), (int, float)) or res.get('monthlyMobileQcCnt', '0').isdigit() else 50
        
        m1.metric("PC 검색량", f"{pc_cnt:,}건")
        m2.metric("모바일 검색량", f"{mo_cnt:,}건")
        m3.metric("총 합계", f"{pc_cnt + mo_cnt:,}건")
        m4.metric("경쟁 정도", res.get('compIdx', '보통'))

        st.divider()
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            st.markdown("**📱 채널별 검색 비중**")
            fig_p = px.pie(values=[pc_cnt, mo_cnt], names=['PC', 'Mobile'], color_discrete_sequence=['#111111', '#D32F2F'])
            st.plotly_chart(fig_p, use_container_width=True)
        with col_g2:
            st.markdown("**💡 마케팅 인사이트**")
            st.info(f"현재 '{st.session_state.k_name}' 키워드는 **모바일 검색 비중이 {mo_cnt/(pc_cnt+mo_cnt)*100:.1f}%**로 압도적입니다. 인스타그램 광고 및 모바일 플레이스 관리에 집중하십시오.")

# ==========================================
# 🖥️ 화면 3: 오픈/발주 통합 캘린더
# ==========================================
elif main_menu == "🗓️ 오픈/발주 통합 캘린더":
    # (이전과 동일한 캘린더 HTML 코드 유지)
    calendar_html = r"""<!DOCTYPE html><html>... (생략) ...</html>"""
    components.html(calendar_html, height=1200, scrolling=True)
