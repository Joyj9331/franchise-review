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
import json
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
    
    /* 다크모드/라이트모드 통합 가시성 확보 */
    h1, h2, h3, h4, h5, h6, p, label, li, span {
        color: #111111 !important;
    }
    
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
    }
    
    .stApp {
        background-color: #F4F6F8;
    }
    
    /* 사이드바 전용 (다크 유지) */
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: 1px solid #222222;
    }
    [data-testid="stSidebar"] * {
        color: #FFFFFF !important; 
    }
    
    /* 메트릭 카드 */
    div[data-testid="metric-container"] {
        background-color: #FFFFFF;
        border: 1px solid #EAEAEA;
        padding: 20px 25px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03);
        border-left: 5px solid #E8B923; 
    }
    
    /* 애니메이션 */
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
    .login-container * { color: #FFFFFF !important; }
    .brand-title { font-size: 26px; margin-top: 15px; margin-bottom: 5px; }
    .brand-subtitle { color: #E8B923 !important; font-size: 14px; margin-bottom: 30px; }

    /* 입력창 및 드롭다운 화이트 강제 고정 (다크모드 충돌 방어) */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, .stTextInput input {
        background-color: #FFFFFF !important;
        color: #111111 !important;
        -webkit-text-fill-color: #111111 !important;
        border: 1px solid #CCCCCC !important;
    }
    
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #FFFFFF !important;
    }
    li[role="option"] {
        color: #111111 !important;
    }
    li[role="option"]:hover {
        background-color: #F4F6F8 !important;
        color: #D32F2F !important;
    }

    /* Expander 디자인 */
    div[data-testid="stExpander"] {
        background-color: #FFFFFF !important; border-radius: 8px; border: 1px solid #EAEAEA;
        border-left: 4px solid #D32F2F; box-shadow: 0 2px 5px rgba(0,0,0,0.02);
    }
    div[data-testid="stExpander"] summary { background-color: #F8F9FA !important; }
    div[data-testid="stExpander"] summary p { color: #111111 !important; font-weight: 600 !important; }

    /* 버튼 디자인 */
    .stButton > button {
        background-color: #D32F2F !important; border-radius: 6px !important; border: none !important;
        height: 42px; transition: all 0.3s ease;
    }
    .stButton > button * { color: #FFFFFF !important; font-weight: 700 !important; }
    
    /* 데이터프레임 */
    [data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #EAEAEA; background-color: #FFFFFF; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 🔒 2. 보안 로그인 시스템
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
            st.text_input("🔑 본사 직원 인증 코드 (비밀번호)를 입력하십시오.", type="password", on_change=password_entered, key="password", placeholder="입력 후 엔터를 누르세요")
            if "password_correct" in st.session_state and not st.session_state["password_correct"]:
                st.error("❌ 인증 코드가 일치하지 않습니다.")
        return False
    else:
        st.markdown("<style>[data-testid='block-container'] { animation: suckIn 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) forwards; }</style>", unsafe_allow_html=True)
        return True

if not check_password():
    st.stop()

# ==========================================
# 💾 3. 리뷰 및 키워드 데이터 상태 관리 
# ==========================================
STATE_RESOLVED = "state_resolved.csv"
STATE_OVERRIDDEN = "state_overridden.csv"
STATE_NAVER_CONFIG = "state_naver_config.csv"
CALENDAR_DB_FILE = "calendar_data.json" # 💡 캘린더 전용 데이터베이스

def get_saved_ids(filename):
    if os.path.exists(filename): return pd.read_csv(filename)['id'].astype(str).tolist()
    return []

def add_saved_id(filename, new_id):
    ids = get_saved_ids(filename)
    if str(new_id) not in ids:
        ids.append(str(new_id))
        pd.DataFrame({'id': ids}).to_csv(filename, index=False)

def save_naver_config(cid, akey, skey):
    pd.DataFrame({'key': ['customer_id', 'access_key', 'secret_key'], 'value': [cid, akey, skey]}).to_csv(STATE_NAVER_CONFIG, index=False)

def load_naver_config():
    if os.path.exists(STATE_NAVER_CONFIG):
        df_c = pd.read_csv(STATE_NAVER_CONFIG)
        return dict(zip(df_c['key'], df_c['value']))
    return {}

def generate_id(row):
    return hashlib.md5(f"{row['매장명']}_{row['작성일']}_{row['리뷰내용']}".encode()).hexdigest()

def load_data():
    filename = "가맹점_리뷰수집결과_누적.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df.drop_duplicates(subset=['매장명', '작성일', '리뷰내용'], keep='last', inplace=True)
    else:
        df = pd.DataFrame({"매장명": ["데이터 없음"], "작성일": ["2026-03-26"], "리뷰내용": ["수집기 실행 필요"], "감정분석": ["중립"]})
    
    df['id'] = df.apply(generate_id, axis=1)
    overridden_ids = get_saved_ids(STATE_OVERRIDDEN)
    df.loc[df['id'].isin(overridden_ids), '감정분석'] = '긍정'
    return df

def load_store_list():
    if os.path.exists("가맹점_리뷰링크.xlsx"):
        try:
            sdf = pd.read_excel("가맹점_리뷰링크.xlsx")
            return sorted(sdf['매장명'].dropna().unique().tolist())
        except: pass
    return []

df = load_data()
full_store_list = load_store_list() or sorted(df['매장명'].unique().tolist())
saved_config = load_naver_config()

# 💡 캘린더 전용 데이터 로드 및 저장 함수
def load_calendar_data():
    if os.path.exists(CALENDAR_DB_FILE):
        with open(CALENDAR_DB_FILE, "r", encoding="utf-8") as f:
            try: return json.load(f)
            except: pass
    return {"schedules": [], "settings": {}}

def save_calendar_data(data):
    with open(CALENDAR_DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ==========================================
# 🛰️ 4. 네이버 API 로직
# ==========================================
def get_naver_keyword_info(cid, akey, skey, keyword):
    timestamp = str(int(time.time() * 1000))
    uri = "/keywordstool"
    method = "GET"
    sig = base64.b64encode(hmac.new(str(skey).encode("utf-8"), f"{timestamp}.{method}.{uri}".encode("utf-8"), hashlib.sha256).digest()).decode("utf-8")
    headers = {"X-Timestamp": timestamp, "X-API-KEY": akey, "X-Customer": str(cid), "X-Signature": sig}
    try:
        res = requests.get(f"https://api.naver.com{uri}", params={"hintKeywords": keyword, "showDetail": "1"}, headers=headers)
        if res.status_code == 200:
            data = res.json().get('keywordList', [])
            return next((i for i in data if i['relKeyword'] == keyword.replace(" ", "")), data[0]) if data else None
    except: return None
    return None

# ==========================================
# 📌 5. 사이드바 메뉴
# ==========================================
st.sidebar.markdown('<div style="text-align: center; margin-bottom: 20px;"><img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 80%;"></div>', unsafe_allow_html=True)
st.sidebar.markdown("<p style='text-align: center; font-size: 13px; color: #E8B923 !important;'>본사 통합 업무 포털</p>", unsafe_allow_html=True)
st.sidebar.divider()
main_menu = st.sidebar.radio("📌 통합 업무 메뉴", ["💬 가맹점 리뷰 관리", "📈 브랜드 키워드 분석", "🗓️ 오픈/발주 통합 캘린더"])
st.sidebar.divider()
if st.sidebar.button("🔄 전체 데이터 동기화", use_container_width=True): st.rerun()

# ==========================================
# 🖥️ 화면 1: 가맹점 리뷰 관리 (빅데이터 검증형)
# ==========================================
if main_menu == "💬 가맹점 리뷰 관리":
    st.markdown("<h1>💬 가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #777;'>| Big Data Verification</span></h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🌐 전체 브랜드 현황", "🏪 개별 매장 상세분석(데이터 검증)"])
    
    with tab1:
        st.markdown("<h3 style='margin-top: 20px;'>🚨 즉각 조치 요망 매장 (To-Do)</h3>", unsafe_allow_html=True)
        resolved_ids = get_saved_ids(STATE_RESOLVED)
        active_neg = df[(df['감정분석'] == '부정') & (~df['id'].isin(resolved_ids))]
        if not active_neg.empty:
            st.error(f"⚠️ 총 {len(active_neg)}건의 미조치 부정 리뷰가 있습니다.")
            for _, row in active_neg.iterrows():
                with st.expander(f"📌 [{row['매장명']}] {row['작성일']} | {row['리뷰내용'][:30]}..."):
                    st.write(f"💬 **내용:** {row['리뷰내용']}")
                    c1, c2, _ = st.columns([1, 1, 2])
                    if c1.button("✅ 조치 완료", key=f"re_{row['id']}"): add_saved_id(STATE_RESOLVED, row['id']); st.rerun()
                    if c2.button("🌟 긍정 변경", key=f"ov_{row['id']}"): add_saved_id(STATE_OVERRIDDEN, row['id']); st.rerun()
        else: st.success("🎉 모든 부정 리뷰에 대한 조치가 완료되었습니다.")
        
        st.divider()
        st.markdown("<h3>📊 매장별 누적 리뷰 랭킹</h3>", unsafe_allow_html=True)
        counts = df['매장명'].value_counts().reset_index(); counts.columns = ['매장명', '리뷰수']
        col_l, col_r = st.columns(2)
        with col_l: st.info("🔥 리뷰 활성화 TOP 5"); st.dataframe(counts.head(5), use_container_width=True)
        with col_r: st.warning("❄️ 관리 필요 BOTTOM 5"); st.dataframe(counts.tail(5), use_container_width=True)

    with tab2:
        st.markdown("<b style='font-size: 14px; color: #666;'>🔍 매장 검색 및 선택</b>", unsafe_allow_html=True)
        q = st.text_input(" ", placeholder="매장명을 입력하세요 (예: 첨단, 어양)", key="s_store")
        f_stores = [s for s in full_store_list if q.replace(" ","") in s.replace(" ","")] if q else full_store_list
        if f_stores:
            sel_store = st.selectbox("📌 조회할 매장을 선택하십시오", f_stores)
            s_df = df[df['매장명'] == sel_store]
            if not s_df.empty:
                st.markdown(f"### [{sel_store}] 빅데이터 분석 리포트")
                m1, m2, m3 = st.columns(3)
                m1.metric("누적 리뷰", f"{len(s_df)}건")
                m2.metric("긍정 평가", f"{len(s_df[s_df['감정분석'] == '긍정'])}건")
                m3.metric("부정 평가", f"{len(s_df[s_df['감정분석'] == '부정'])}건")
                
                st.markdown("**📈 일별 리뷰 발생 추이**")
                st.plotly_chart(px.line(s_df.groupby('작성일').size().reset_index(name='건수'), x='작성일', y='건수', markers=True, color_discrete_sequence=['#D32F2F']), use_container_width=True)
                
                st.divider()
                st.markdown("### 🔍 수집 데이터 전수 검증 (원본 내역)")
                st.write("봇이 수집한 원본 리뷰 텍스트입니다. 인공지능 분류가 정확한지 확인해 보십시오.")
                st.dataframe(s_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False), use_container_width=True)
            else: st.info("수집된 데이터가 없습니다.")

# ==========================================
# 🖥️ 화면 2: 브랜드 키워드 분석
# ==========================================
elif main_menu == "📈 브랜드 키워드 분석":
    st.markdown("<h1>📈 브랜드 키워드 분석 <span style='font-size: 18px; color: #777;'>| Naver Real-time API</span></h1>", unsafe_allow_html=True)
    with st.expander("🔐 Naver API 영구 연결 설정"):
        cid_v = saved_config.get('customer_id', ""); akey_v = saved_config.get('access_key', ""); skey_v = saved_config.get('secret_key', "")
        c_id = st.text_input("Customer ID", value=cid_v, type="password"); a_key = st.text_input("Access Key", value=akey_v, type="password"); s_key = st.text_input("Secret Key", value=skey_v, type="password")
        if st.button("🗝️ 키 정보 영구 저장"): save_naver_config(c_id, a_key, s_key); st.success("저장 완료!"); time.sleep(1); st.rerun()

    st.divider()
    k_in, k_bt = st.columns([0.8, 0.2]); target_k = k_in.text_input("🔍 실시간 분석 키워드", placeholder="예: 달빛에구운고등어")
    if k_bt.button("🚀 분석 시작", use_container_width=True):
        if not (c_id and a_key): st.error("API 키를 먼저 등록하세요.")
        else:
            with st.spinner("네이버 서버 통신 중..."):
                res = get_naver_keyword_info(c_id, a_key, s_key, target_k)
                if res: st.session_state.kr = res; st.session_state.kn = target_k; st.success("성공!")
                else: st.error("키워드 또는 API 설정 오류")
    
    if 'kr' in st.session_state:
        r = st.session_state.kr; st.markdown(f"### 📊 [{st.session_state.kn}] 최근 30일 지표")
        p_c = int(r.get('monthlyPcQcCnt', 0)) if str(r.get('monthlyPcQcCnt')).isdigit() else 10
        m_c = int(r.get('monthlyMobileQcCnt', 0)) if str(r.get('monthlyMobileQcCnt')).isdigit() else 100
        c1, c2, c3 = st.columns(3)
        c1.metric("PC 검색량", f"{p_c:,}건"); c2.metric("모바일 검색량", f"{m_c:,}건"); c3.metric("경쟁 정도", r.get('compIdx', '보통'))
        st.plotly_chart(px.pie(values=[p_c, m_c], names=['PC', 'Mobile'], color_discrete_sequence=['#111111', '#D32F2F']), use_container_width=True)

# ==========================================
# 🖥️ 화면 3: 오픈/발주 통합 캘린더 (양방향 데이터 저장형 ERP)
# ==========================================
elif main_menu == "🗓️ 오픈/발주 통합 캘린더":
    st.markdown("<h1>🗓️ 가맹점 통합 캘린더 <span style='font-size: 18px; color: #777;'>| Server-Synced Calendar</span></h1>", unsafe_allow_html=True)
    
    # 💡 캘린더 UI의 HTML 및 Streamlit 양방향 통신 로직
    calendar_html = r"""
    <!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <link href="https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap" rel="stylesheet">
    
    <!-- Streamlit 양방향 통신을 위한 필수 라이브러리 추가 -->
    <script src="https://cdn.jsdelivr.net/npm/streamlit-component-lib@1.3.0/dist/streamlit.js"></script>

    <script>tailwind.config={theme:{extend:{colors:{brand:{dark:'#111111',red:'#D32F2F',gold:'#E8B923'}},fontFamily:{sans:['"Noto Sans KR"','sans-serif'],heading:['"Gowun Dodum"','sans-serif']}}}}</script>
    <style>
        body{font-family:'Noto Sans KR',sans-serif;background-color:#F4F6F8;margin:0;padding:0}
        h1,h2,h3{font-family:'Gowun Dodum',sans-serif;font-weight:700;color:#111111}
        ::-webkit-scrollbar{width:6px;height:6px}::-webkit-scrollbar-track{background:#f1f1f1;border-radius:4px}::-webkit-scrollbar-thumb{background:#c1c1c1;border-radius:4px}::-webkit-scrollbar-thumb:hover{background:#a8a8a8}
        #toast{visibility:hidden;min-width:250px;background-color:#111111;color:#fff;text-align:center;border-radius:8px;padding:12px;position:fixed;z-index:1000;left:50%;transform:translateX(-50%);bottom:30px;opacity:0;transition:opacity .3s,visibility .3s;box-shadow:0 4px 6px -1px rgba(0,0,0,.1)}
        #toast.show{visibility:visible;opacity:1}
        .draggable-item{cursor:grab;user-select:none}.draggable-item:active{cursor:grabbing;opacity:.8}
        .drag-over{background-color:#fff1f2!important;outline:2px dashed #D32F2F;outline-offset:-2px}
        .bg-blue-600{background-color:#D32F2F!important}.hover\:bg-blue-700:hover{background-color:#111111!important;color:#FFF!important}.text-blue-600{color:#D32F2F!important}.focus\:ring-blue-500:focus{border-color:#D32F2F!important;box-shadow:0 0 0 3px rgba(211,47,47,.2)!important}.border-blue-400{border-color:#D32F2F!important}.bg-blue-50{background-color:#fff1f2!important}.bg-gray-800{background-color:#111111!important}.hover\:bg-gray-900:hover{background-color:#333!important}
    </style></head>
    <body class="text-gray-900 font-sans" id="mainBody">
    <div class="p-2 w-full mx-auto space-y-4">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center bg-white p-5 rounded-xl border border-gray-200 shadow-sm gap-4">
            <div><h1 class="text-2xl font-bold flex items-center gap-2"><i class="fas fa-calendar-check text-brand-red"></i> 가맹점 오픈 및 발주 통합 캘린더</h1><p class="text-gray-500 mt-1 text-sm">일정 드래그 시 화면 양끝으로 가져가면 달력이 자동으로 넘어갑니다.</p></div>
            <div class="flex flex-wrap gap-2"><button id="btnOpenTeamModal" class="flex items-center gap-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 px-3 py-2 rounded-lg font-medium text-sm"><i class="fas fa-cog"></i> 팀 세팅</button><button id="btnOpenStoreModal" class="flex items-center gap-1.5 bg-brand-red text-white px-4 py-2 rounded-lg font-medium text-sm shadow-sm"><i class="fas fa-plus"></i> 신규 매장 등록</button></div>
        </div>
        <div class="flex justify-between items-center px-2"><button id="btnPrevMonth" class="bg-white border p-2 rounded-lg"><i class="fas fa-chevron-left"></i> 이전 달</button><div class="text-sm font-bold text-brand-red">※ 모바일은 스와이프를 지원합니다.</div><button id="btnNextMonth" class="bg-white border p-2 rounded-lg">다음 달 <i class="fas fa-chevron-right"></i></button></div>
        <div id="calendarContainer" class="flex flex-col xl:flex-row gap-4 select-none"></div>
        <div class="bg-white p-4 rounded-xl border shadow-sm mt-6"><div id="teamSummaryContainer" class="grid grid-cols-1 sm:grid-cols-3 gap-3"></div></div>
        <div class="bg-white rounded-xl border shadow-sm overflow-hidden mt-6">
            <div class="p-4 border-b bg-gray-50 flex items-center gap-4"><h3 class="font-bold">매장별 상세 일정표</h3><div class="flex bg-gray-200 rounded-lg p-1" id="tableTabs"><button class="tab-btn px-4 py-1 bg-white rounded shadow text-sm" data-tab="active">진행중 매장 <span id="cntActive">0</span></button><button class="tab-btn px-4 py-1 text-sm" data-tab="completed">오픈 완료 <span id="cntCompleted">0</span></button></div></div>
            <div class="overflow-x-auto"><table class="w-full text-left whitespace-nowrap text-[13px]"><thead><tr class="bg-gray-100 border-b"><th></th><th>호점</th><th>가맹점명</th><th>팀</th><th>공사형태</th><th>주방</th><th>공사시작</th><th>공사완료</th><th>화덕</th><th>화구</th><th>초도</th><th>교육</th><th>오픈예정</th><th>관리</th></tr></thead><tbody id="tableBody"></tbody></table></div>
        </div>
    </div>
    
    <!-- 매장 등록/수정 모달 (사내 코드 구조 그대로 사용) -->
    <div id="storeModal" class="hidden fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-xl shadow-2xl w-full max-w-4xl max-h-[95vh] flex flex-col">
            <div class="bg-white border-b border-gray-200 px-6 py-4 flex justify-between items-center rounded-t-xl shrink-0">
                <h2 id="storeModalTitle" class="text-xl font-bold flex items-center gap-2"><i class="fas fa-store text-brand-red"></i> 가맹점 일정 등록</h2>
                <button id="btnCloseStoreModal" class="text-gray-400 hover:text-gray-700"><i class="fas fa-times text-xl"></i></button>
            </div>
            <div class="overflow-y-auto flex-1">
                <form id="storeForm" class="p-6 space-y-6">
                    <input type="hidden" id="formId">
                    <div class="bg-gray-50 p-4 rounded-lg border border-gray-200">
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div><label class="block text-xs font-semibold text-gray-600 mb-1">호점</label><input type="text" id="formStoreNumber" class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-brand-red text-sm"></div>
                            <div class="col-span-1 md:col-span-1"><label class="block text-xs font-semibold text-gray-600 mb-1">가맹점명 *</label><input type="text" id="formStoreName" required class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-brand-red text-sm"></div>
                            <div><label class="block text-xs font-semibold text-gray-600 mb-1">담당 팀 *</label><select id="formTeam" class="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-brand-red text-sm font-bold text-white bg-brand-dark"><option value="A" class="bg-white text-black">A팀</option><option value="B" class="bg-white text-black">B팀</option><option value="C" class="bg-white text-black">C팀</option></select></div>
                            <div><label class="block text-xs font-semibold text-gray-600 mb-1">고정 담당자</label><input type="text" id="formSupervisor" readonly class="w-full p-2 border border-gray-200 bg-gray-100 text-gray-500 rounded text-sm font-bold"></div>
                        </div>
                    </div>
                    <div class="border-t border-gray-200 pt-4"><h3 class="text-sm font-bold text-gray-700 mb-4 flex items-center gap-2"><i class="fas fa-hammer text-gray-500"></i> 공사 형태</h3><div id="formConstructionTypes" class="flex gap-4 flex-wrap"></div></div>
                    <div class="border-t border-gray-200 pt-4">
                        <div class="flex justify-between items-center mb-4"><h3 class="text-sm font-bold text-gray-700 flex items-center gap-2"><i class="fas fa-calendar-alt text-gray-500"></i> 자동 산출 및 상세 일정</h3><span class="text-xs text-brand-red bg-red-50 px-2 py-1 rounded border border-red-200 font-bold tracking-wide"><i class="fas fa-magic"></i> 기준일 입력시 자동 계산됨</span></div>
                        <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
                            <div><label class="block text-xs font-bold text-brand-red mb-1">공사 시작 (기준일)</label><input type="date" id="formConstructionStart" class="w-full p-2 border border-red-400 bg-red-50 rounded text-sm"></div>
                            <div><label class="block text-xs text-gray-600 mb-1">공사 완료 (+40일)</label><input type="date" id="formConstructionEnd" class="w-full p-2 border border-gray-300 rounded text-sm"></div>
                            <div class="col-span-2 md:col-span-2"><label class="block text-xs text-gray-600 mb-1">화덕 입고 (+21영업일, 2일간)</label><div class="flex items-center gap-2"><input type="date" id="formOvenIn" class="w-full p-2 border border-gray-300 rounded text-sm"><span class="text-gray-400">~</span><input type="date" id="formOvenEnd" class="w-full p-2 border border-gray-300 rounded text-sm"></div></div>
                            <div><label class="block text-xs text-gray-600 mb-1">화구류 입고 (+22영업일)</label><input type="date" id="formBurnerIn" class="w-full p-2 border border-gray-300 rounded text-sm"></div>
                            <div class="col-span-2 md:col-span-3"><label class="block text-xs text-gray-600 mb-1">초도 입고 (공사완료 +1일, 2일간)</label><div class="flex items-center gap-2 w-1/2 pr-2"><input type="date" id="formInitialStockIn" class="w-full p-2 border border-gray-300 rounded text-sm"><span class="text-gray-400">~</span><input type="date" id="formInitialStockEnd" class="w-full p-2 border border-gray-300 rounded text-sm"></div></div>
                            <div class="col-span-2 md:col-span-2"><label class="block text-xs text-gray-600 mb-1">교육 일정 (공사완료 +3일, 5일간)</label><div class="flex items-center gap-2"><input type="date" id="formTrainingStart" class="w-full p-2 border border-gray-300 rounded text-sm"><span class="text-gray-400">~</span><input type="date" id="formTrainingEnd" class="w-full p-2 border border-gray-300 rounded text-sm"></div></div>
                            <div class="col-span-2 md:col-span-1"><label class="block text-xs font-bold text-brand-red mb-1">오픈 예정일</label><input type="date" id="formOpenDate" required class="w-full p-2 border border-red-300 bg-red-50 rounded text-sm"></div>
                            <div class="col-span-2 md:col-span-4 bg-gray-50 p-3 rounded border border-gray-200 mt-0 mb-2"><div class="flex flex-col md:flex-row gap-4 w-full"><div class="w-full md:w-1/2"><label class="block text-xs font-bold text-gray-700 mb-1">사전 교육 (시작~종료)</label><div class="flex items-center gap-2"><input type="date" id="formPreTrainingStart" class="w-full p-2 border border-gray-300 rounded text-sm bg-white"><span class="text-gray-400">~</span><input type="date" id="formPreTrainingEnd" class="w-full p-2 border border-gray-300 rounded text-sm bg-white"></div></div><div class="w-full md:w-1/2"><label class="block text-xs font-bold text-gray-700 mb-1">사전 교육 내용 및 장소</label><input type="text" id="formPreTrainingMemo" class="w-full p-2 border border-gray-300 rounded text-sm bg-white"></div></div></div>
                        </div>
                    </div>
                    <div class="border-t border-gray-200 pt-5"><div class="flex justify-between items-center mb-3"><h3 class="text-sm font-bold text-gray-700 flex items-center gap-2"><i class="fas fa-plus-circle text-gray-500"></i> 기타 추가 일정</h3></div><div class="flex gap-2 items-end mb-4 bg-white p-3 rounded border border-gray-200 shadow-sm"><div class="flex-1"><label class="block text-xs text-gray-600 mb-1">일정명</label><input type="text" id="customScheduleName" class="w-full p-2 border border-gray-300 rounded text-sm"></div><div class="flex-1"><label class="block text-xs text-gray-600 mb-1">날짜</label><input type="date" id="customScheduleDate" class="w-full p-2 border border-gray-300 rounded text-sm"></div><button type="button" id="btnAddCustomSchedule" class="px-5 py-2 bg-brand-dark text-white rounded text-sm font-bold shadow-sm hover:bg-gray-800 transition-colors h-[38px] shrink-0">추가</button></div><ul id="customSchedulesList" class="space-y-2 mb-2"></ul></div>
                    <div class="border-t border-gray-200 pt-5"><div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4"><div><label class="block text-xs text-gray-600 mb-1">주방 업체</label><select id="formKitchenVendor" class="w-full p-2 border border-gray-300 rounded text-sm"><option value="형제">형제</option><option value="신광">신광</option><option value="주원">주원</option></select></div><div><label class="block text-xs text-gray-600 mb-1">가스 종류</label><select id="formGasType" class="w-full p-2 border border-gray-300 rounded text-sm"><option value="LNG">LNG (도시가스)</option><option value="LPG">LPG (가스통)</option></select></div></div><div><label class="block text-xs text-gray-600 mb-1">비고 (직접입력)</label><textarea id="formNotes" rows="2" class="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none"></textarea></div></div>
                </form>
            </div>
            <div class="flex justify-between items-center px-6 py-4 border-t border-gray-200 bg-gray-50 shrink-0 rounded-b-xl">
                <div><button type="button" id="btnDeleteStoreModal" class="hidden flex items-center gap-1 px-4 py-2 text-red-600 bg-red-100 hover:bg-red-200 rounded-lg font-medium text-sm transition-colors"><i class="fas fa-trash-alt"></i> 영구 삭제</button></div>
                <div class="flex gap-2"><button type="button" id="btnCancelStoreModal" class="px-5 py-2 border border-gray-300 rounded-lg text-gray-700 bg-white hover:bg-gray-50 text-sm font-medium transition-colors">취소</button><button type="button" id="btnSaveStoreModal" class="flex items-center gap-1 px-5 py-2 bg-brand-red text-white rounded-lg font-medium text-sm shadow-sm hover:bg-red-800 transition-colors"><i class="fas fa-save"></i> 저장</button></div>
            </div>
        </div>
    </div>

    <!-- 팀 세팅 모달 -->
    <div id="teamModal" class="hidden fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
        <div class="bg-white rounded-xl shadow-xl w-full max-w-lg flex flex-col max-h-[90vh]">
            <div class="border-b border-gray-200 px-6 py-4 flex justify-between items-center shrink-0"><h2 class="text-lg font-bold flex items-center gap-2"><i class="fas fa-users text-gray-600"></i> 슈퍼바이저 팀 구성</h2><button id="btnCloseTeamModal" class="text-gray-400 hover:text-gray-700"><i class="fas fa-times text-lg"></i></button></div>
            <div class="p-6 overflow-y-auto flex-1"><div class="flex gap-2 mb-4" id="teamTabs"></div><div id="teamSupervisorUI"></div><div id="addMemberUI" class="hidden flex gap-2 mb-4 bg-gray-50 p-3 rounded-lg border border-gray-200"><input type="text" id="newMemberName" class="flex-1 p-2 border border-gray-300 rounded text-sm" placeholder="신규 팀원 이름 입력"><button type="button" id="btnAddMember" class="px-4 py-2 bg-brand-dark text-white rounded text-sm font-bold">추가</button></div><div class="grid grid-cols-2 sm:grid-cols-3 gap-3 mt-4" id="teamMembersGrid"></div></div>
            <div class="flex justify-between items-center p-4 border-t border-gray-200 bg-gray-50 rounded-b-xl shrink-0"><div><button type="button" id="btnToggleTeamManage" class="flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg text-sm font-bold shadow-sm"><i class="fas fa-user-cog"></i> 인원 관리</button></div><div class="flex justify-end gap-2"><button id="btnCancelTeamModal" class="px-5 py-2 border border-gray-300 rounded-lg bg-white text-gray-700 text-sm font-medium">취소</button><button id="btnSaveTeamModal" class="px-5 py-2 bg-brand-red text-white rounded-lg text-sm font-medium shadow-sm">저장</button></div></div>
        </div>
    </div>
    
    <div id="confirmModal" class="hidden fixed inset-0 bg-black/60 flex items-center justify-center z-[100] p-4"><div class="bg-white rounded-xl shadow-xl w-full max-w-sm p-6 text-center"><i class="fas fa-exclamation-triangle text-brand-red text-3xl mb-4"></i><h3 class="text-lg font-bold text-gray-900 mb-2">확인</h3><p id="confirmMessage" class="text-gray-600 text-sm mb-6"></p><div class="flex justify-center gap-3"><button id="btnConfirmCancel" class="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition">취소</button><button id="btnConfirmOk" class="px-4 py-2 bg-brand-red text-white rounded-lg text-sm font-medium hover:bg-red-800 transition">확인 진행</button></div></div></div>
    <div id="toast"></div>

    <script>
        // 💡 Python <-> JavaScript 통신 핵심 (Local Storage 대신 서버(Python) DB 사용)
        const TEAM_COLORS={'A':{bg:'bg-[#111111]',text:'text-white',border:'border-gray-800'},'B':{bg:'bg-[#D32F2F]',text:'text-white',border:'border-red-800'},'C':{bg:'bg-[#E8B923]',text:'text-black',border:'border-yellow-600'}};
        const CONSTRUCTION_TYPES = ['감리', '더원', '동영', '간판직'];
        let schedules=[], allMembers=[], memberTeams={}, tempTeams={}, teamSupervisors={}, tempSupervisors={};
        let selectedTeamTab='A', editingRowId=null, inlineEditData={}, currentViewTab='active', currentCustomSchedules=[], isTeamManageMode=false;
        let currentDate = new Date(); currentDate.setDate(1);

        // Date Utils
        function addCalendarDays(dateStr, days) { if(!dateStr) return ''; let d = new Date(dateStr + 'T12:00:00'); d.setDate(d.getDate() + days); return d.toISOString().split('T')[0]; }
        function addBusinessDays(dateStr, days) { if(!dateStr) return ''; let d = new Date(dateStr + 'T12:00:00'); let added = 0; while (added < days) { d.setDate(d.getDate() + 1); if (d.getDay() !== 0 && d.getDay() !== 6) added++; } return d.toISOString().split('T')[0]; }
        function calculateAutoDates(S) { if (!S) return {}; const E = addCalendarDays(S, 40), O = addBusinessDays(S, 21), O_E = addCalendarDays(O, 1), B = addBusinessDays(S, 22), IS_S = addCalendarDays(E, 1), IS_E = addCalendarDays(IS_S, 1), T_S = addCalendarDays(E, 3), T_E = addCalendarDays(T_S, 4), OpenD = addCalendarDays(T_S, 1); return { constructionStart: S, constructionEnd: E, ovenIn: O, ovenEnd: O_E, burnerIn: B, initialStockIn: IS_S, initialStockEnd: IS_E, trainingStart: T_S, trainingEnd: T_E, openDate: OpenD }; }
        function showToast(message) { const toast = document.getElementById("toast"); if(toast) { toast.innerText = message; toast.className = "show"; setTimeout(() => { toast.className = toast.className.replace("show", ""); }, 3000); } }

        // Render Functions
        function renderTeamSummary() {
            const list = { A: [], B: [], C: [] };
            allMembers.forEach(m => { if (memberTeams[m]) list[memberTeams[m]].push(m); });
            ['A', 'B', 'C'].forEach(team => { const supervisor = teamSupervisors[team]; if (supervisor && list[team].includes(supervisor)) { list[team] = list[team].filter(m => m !== supervisor); list[team].unshift(supervisor); } });
            const container = document.getElementById('teamSummaryContainer');
            if(!container) return;
            container.innerHTML = `
                <div class="px-3 py-2 rounded-lg bg-gray-100 border border-gray-300 flex flex-col justify-center"><span class="font-bold text-[#111111] text-sm">A팀 (담당: ${teamSupervisors['A'] || '-'})</span><span class="text-xs text-gray-700 mt-0.5">${list.A.join(', ') || '-'}</span></div>
                <div class="px-3 py-2 rounded-lg bg-red-50 border border-red-200 flex flex-col justify-center"><span class="font-bold text-[#D32F2F] text-sm">B팀 (담당: ${teamSupervisors['B'] || '-'})</span><span class="text-xs text-red-900 mt-0.5">${list.B.join(', ') || '-'}</span></div>
                <div class="px-3 py-2 rounded-lg bg-yellow-50 border border-yellow-200 flex flex-col justify-center"><span class="font-bold text-[#E8B923] text-sm">C팀 (담당: ${teamSupervisors['C'] || '-'})</span><span class="text-xs text-yellow-900 mt-0.5">${list.C.join(', ') || '-'}</span></div>
            `;
        }

        function getCalendarEvents() {
            const events = [];
            const addRangeEvent = (store, sField, eField, typeKey, typeName) => { let start = store[sField]; let end = store[eField]; if (!start && !end) return; if (!start) start = end; if (!end) end = start; let d = new Date(start + 'T12:00:00'); let e = new Date(end + 'T12:00:00'); if (e < d) e = new Date(start + 'T12:00:00'); while(d <= e) { let curr = d.toISOString().split('T')[0]; events.push({ id: store.id, date: curr, title: store.storeName, type: typeName, team: store.team, typeKey: typeKey, isRange: true, isStart: (curr === start), isEnd: (curr === end), draggedDate: curr }); d.setDate(d.getDate() + 1); } };
            const addSingleEvent = (store, field, typeKey, typeName) => { if (store[field]) events.push({ id: store.id, date: store[field], title: store.storeName, type: typeName, team: store.team, typeKey: typeKey, isRange: false, draggedDate: store[field] }); };
            schedules.filter(s => s.status !== '완료' && s.showInCalendar !== false).forEach(s => {
                addSingleEvent(s, 'constructionStart', 'constructionStart', '공사시작'); addSingleEvent(s, 'constructionEnd', 'constructionEnd', '공사완료'); addRangeEvent(s, 'ovenIn', 'ovenEnd', 'oven', '화덕입고'); addRangeEvent(s, 'initialStockIn', 'initialStockEnd', 'initialStock', '초도입고'); addRangeEvent(s, 'preTrainingStart', 'preTrainingEnd', 'preTraining', '사전교육'); addRangeEvent(s, 'trainingStart', 'trainingEnd', 'training', '교육'); addSingleEvent(s, 'burnerIn', 'burnerIn', '화구입고'); addSingleEvent(s, 'openDate', 'openDate', '오픈');
                let customArr = s.customSchedules || []; if(typeof customArr === 'string') { try { customArr = JSON.parse(customArr); } catch(e) { customArr = []; } }
                customArr.forEach((cs, idx) => { if (cs.date) events.push({ id: s.id, date: cs.date, title: s.storeName, type: cs.name, team: s.team, typeKey: `custom_${idx}`, isRange: false, draggedDate: cs.date }); });
            });
            return events.sort((a,b) => String(a.id).localeCompare(String(b.id)));
        }

        function renderMonthBlock(year, month, evts) {
            const daysInMonth = new Date(year, month + 1, 0).getDate(), firstDay = new Date(year, month, 1).getDay();
            let html = ''; for (let i = 0; i < firstDay; i++) html += `<div class="min-h-[120px] bg-gray-50/50 border-b border-r border-gray-200"></div>`;
            const todayStr = new Date().toISOString().split('T')[0];
            for (let day = 1; day <= daysInMonth; day++) {
                const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                const dayEvts = evts.filter(e => e.date === dateStr);
                const colorClass = ((firstDay + day - 1) % 7 === 0) ? 'text-red-600' : ((firstDay + day - 1) % 7 === 6) ? 'text-blue-600' : 'text-gray-800';
                const isToday = (dateStr === todayStr);
                let evtsHtml = dayEvts.map(evt => {
                    const c = TEAM_COLORS[evt.team] || TEAM_COLORS['A']; const isSunday = ((firstDay + day - 1) % 7 === 0); const showText = !evt.isRange || evt.isStart || isSunday;
                    let shapeCls = 'rounded border border-white/20 mx-1.5'; let contentHtml = showText ? `<div class="w-full truncate text-center px-0.5"><span class="text-[11px] font-bold tracking-tight">${evt.title}-${evt.type}</span></div>` : '&nbsp;';
                    if (evt.isRange) { if (evt.isStart && !evt.isEnd) shapeCls = 'rounded-l border border-white/20 border-r-0 ml-1.5 mr-0 z-10 relative'; else if (!evt.isStart && evt.isEnd) shapeCls = 'rounded-r border border-white/20 border-l-0 mr-1.5 ml-0 z-10 relative'; else if (!evt.isStart && !evt.isEnd) shapeCls = 'rounded-none border-t border-b border-white/20 border-l-0 border-r-0 mx-0 z-10 relative'; }
                    return `<div draggable="true" ondragstart="window.handleDragStart(event, '${evt.id}', '${evt.typeKey}', '${evt.draggedDate}')" class="draggable-item px-1 flex items-center overflow-hidden h-[26px] shadow-sm mt-[2px] ${c.bg} ${c.text} ${c.border} hover:brightness-110 ${shapeCls}" onclick="window.handleEventClick(event, '${evt.id}')" title="${evt.title}-${evt.type}">${contentHtml}</div>`;
                }).join('');
                html += `<div class="min-h-[120px] p-0 border-b border-r border-gray-200 bg-white hover:bg-gray-50 transition-colors ${isToday ? 'bg-yellow-50' : ''}" ondragover="event.preventDefault(); this.classList.add('drag-over');" ondragleave="this.classList.remove('drag-over');" ondrop="this.classList.remove('drag-over'); window.handleDrop(event, '${dateStr}')" onclick="if(event.target === this || event.target.closest('.day-header')) window.handleDateClick('${dateStr}')"><div class="day-header flex justify-end items-center p-1.5 pb-1 cursor-pointer">${isToday ? `<span class="bg-[#D32F2F] text-white text-[9px] px-1.5 py-0.5 rounded mr-1 shadow-sm font-bold">오늘</span>` : ''}<span class="text-xs font-bold ${colorClass}">${day}</span></div><div class="space-y-0 pb-1.5 flex flex-col">${evtsHtml}</div></div>`;
            }
            return `<div class="month-wrapper bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden flex-1"><div class="bg-[#111111] p-3 text-center border-b border-gray-200 text-white"><h3 class="text-lg font-bold text-white">${year}년 ${month + 1}월</h3></div><div class="grid grid-cols-7 border-b border-gray-200 bg-gray-50">${['일','월','화','수','목','금','토'].map((d,i)=>`<div class="py-2 text-center text-xs font-bold border-r last:border-r-0 ${i===0?'text-red-600':i===6?'text-blue-600':'text-gray-800'}">${d}</div>`).join('')}</div><div class="grid grid-cols-7">${html}</div></div>`;
        }

        function renderCalendarGrid() {
            const evts = getCalendarEvents(); const y1 = currentDate.getFullYear(), m1 = currentDate.getMonth(); const d2 = new Date(y1, m1 + 1, 1);
            const container = document.getElementById('calendarContainer');
            if(container) container.innerHTML = renderMonthBlock(y1, m1, evts) + renderMonthBlock(d2.getFullYear(), d2.getMonth(), evts);
        }

        function renderTable() {
            const body = document.getElementById('tableBody'); if (!body) return;
            const countActive = schedules.filter(s => s.status !== '완료').length; const countCompleted = schedules.filter(s => s.status === '완료').length;
            document.getElementById('cntActive').innerText = countActive; document.getElementById('cntCompleted').innerText = countCompleted;
            document.querySelectorAll('.tab-btn').forEach(btn => { if(btn.getAttribute('data-tab') === currentViewTab) { btn.classList.add('bg-white', 'text-gray-800', 'shadow-sm'); btn.classList.remove('text-gray-500'); } else { btn.classList.remove('bg-white', 'text-gray-800', 'shadow-sm'); btn.classList.add('text-gray-500'); } });
            const viewSchedules = schedules.filter(s => currentViewTab === 'active' ? (s.status !== '완료') : (s.status === '완료'));
            if (!viewSchedules.length) return body.innerHTML = `<tr><td colspan="14" class="p-8 text-center text-gray-500">해당 목록에 매장이 없습니다.</td></tr>`;

            body.innerHTML = [...viewSchedules].sort((a,b)=>String(a.id).localeCompare(String(b.id))).map(s => {
                const isEd = editingRowId === String(s.id); const d = isEd ? inlineEditData : s;
                const cOriginal = TEAM_COLORS[s.team] || TEAM_COLORS['A']; const isVis = s.showInCalendar !== false;
                const formatRange = (start, end) => { if (!start && !end) return '-'; if (start && end && start === end) return start; if (!start && end) return `~ ${end}`; if (start && !end) return `${start}`; return `${start} ~ ${end}`; };
                let ctsArray = typeof d.constructionType === 'string' ? JSON.parse(d.constructionType || '[]') : (d.constructionType || []);
                let ctsH = isEd ? `<div class="flex gap-2 flex-wrap max-w-[140px]">` + CONSTRUCTION_TYPES.map(t=>`<label class="flex items-center gap-1 cursor-pointer text-xs"><input type="checkbox" class="inline-ctype-chk w-3 h-3" value="${t}" ${ctsArray.includes(t)?'checked':''}> ${t}</label>`).join('') + `</div>` : `<div class="flex gap-1 flex-wrap max-w-[140px]">${ctsArray.length ? ctsArray.map(t=>`<span class="bg-gray-100 px-1.5 py-0.5 rounded text-[11px] border">${t}</span>`).join('') : '-'}</div>`;
                let actionBtnsHtml = isEd ? `<div class="flex justify-center gap-1"><button class="btn-inline-save p-1 bg-green-600 text-white rounded" title="저장"><i class="fas fa-check"></i></button><button class="btn-inline-cancel p-1 bg-gray-400 text-white rounded" title="취소"><i class="fas fa-times"></i></button><button class="btn-inline-delete p-1 bg-red-500 text-white rounded" title="삭제"><i class="fas fa-trash-alt"></i></button></div>` : (currentViewTab === 'active' ? `<div class="flex flex-col gap-1 items-center"><button class="btn-inline-edit w-full px-2 py-1 bg-white border border-gray-300 text-gray-700 rounded text-[11px] font-medium shadow-sm hover:bg-gray-50"><i class="fas fa-pen"></i> 수정</button><button class="btn-action-complete w-full px-2 py-1 bg-gray-100 border border-gray-300 text-[#111111] rounded text-[11px] font-bold shadow-sm hover:bg-gray-200"><i class="fas fa-check-double"></i> 완료</button></div>` : `<div class="flex flex-col gap-1 items-center"><button class="btn-inline-edit w-full px-2 py-1 bg-white border border-gray-300 text-gray-700 rounded text-[11px] font-medium shadow-sm hover:bg-gray-50"><i class="fas fa-pen"></i> 수정</button><button class="btn-action-restore w-full px-2 py-1 bg-orange-50 border border-orange-200 text-orange-700 rounded text-[11px] font-bold shadow-sm hover:bg-orange-100"><i class="fas fa-undo"></i> 복구</button></div>`);

                return `<tr class="hover:bg-gray-50/50 ${isEd ? 'bg-red-50/30' : ''} ${!isVis ? 'opacity-50' : ''}" data-id="${s.id}">
                    <td class="p-2 text-center border-r border-gray-100"><button class="btn-toggle-vis"><i class="fas ${isVis ? 'fa-eye text-brand-red' : 'fa-eye-slash text-gray-400'} text-lg hover:opacity-70 transition-opacity"></i></button></td>
                    <td class="p-2 text-center font-bold border-r border-gray-100">${isEd?`<input type="text" data-field="storeNumber" value="${d.storeNumber||''}" class="w-12 p-1 border rounded text-xs text-center">`: (s.storeNumber?s.storeNumber+'호':'-')}</td>
                    <td class="p-2 font-bold border-r border-gray-100">${isEd?`<input type="text" data-field="storeName" value="${d.storeName||''}" class="w-24 p-1 border rounded text-xs">`: s.storeName}</td>
                    <td class="p-2 border-r border-gray-100">${isEd?`<div class="flex gap-1"><select data-field="team" class="p-1 border rounded text-xs w-14 font-bold focus:ring-2 focus:ring-brand-red outline-none"><option value="A" ${d.team==='A'?'selected':''}>A팀</option><option value="B" ${d.team==='B'?'selected':''}>B팀</option><option value="C" ${d.team==='C'?'selected':''}>C팀</option></select><input type="text" data-field="supervisor" value="${d.supervisor||''}" readonly class="w-16 p-1 border rounded text-xs bg-gray-100 text-gray-700 font-bold opacity-80 cursor-not-allowed"></div>` : `<button class="btn-show-team px-2 py-0.5 rounded text-xs border font-bold ${cOriginal.bg} ${cOriginal.text} ${cOriginal.border} hover:opacity-80 transition-opacity" data-team="${s.team}">${s.team} | ${s.supervisor} <i class="fas fa-users ml-0.5"></i></button>`}</td>
                    <td class="p-2 border-r border-gray-100">${ctsH}</td>
                    <td class="p-2 border-r border-gray-100">${isEd?`<select data-field="kitchenVendor" class="p-1 border rounded text-xs w-16"><option value="형제" ${d.kitchenVendor==='형제'?'selected':''}>형제</option><option value="신광" ${d.kitchenVendor==='신광'?'selected':''}>신광</option><option value="주원" ${d.kitchenVendor==='주원'?'selected':''}>주원</option></select>` : d.kitchenVendor||'-'}</td>
                    <td class="p-2 text-brand-red font-bold border-r border-gray-100">${isEd?`<input type="date" data-field="constructionStart" value="${d.constructionStart||''}" class="p-1 border rounded text-xs w-24 bg-red-50">`: (d.constructionStart||'-')}</td>
                    <td class="p-2 text-gray-600 border-r border-gray-100">${isEd?`<input type="date" data-field="constructionEnd" value="${d.constructionEnd||''}" class="p-1 border rounded text-xs w-24">`: (d.constructionEnd||'-')}</td>
                    <td class="p-2 text-gray-600 border-r border-gray-100">${isEd?`<div class="flex flex-col gap-1"><input type="date" data-field="ovenIn" value="${d.ovenIn||''}" class="p-1 border rounded text-xs w-24"><input type="date" data-field="ovenEnd" value="${d.ovenEnd||''}" class="p-1 border rounded text-xs w-24"></div>` : `<div class="flex flex-col text-xs font-medium"><span>${formatRange(s.ovenIn, s.ovenEnd)}</span></div>`}</td>
                    <td class="p-2 text-gray-600 border-r border-gray-100">${isEd?`<input type="date" data-field="burnerIn" value="${d.burnerIn||''}" class="p-1 border rounded text-xs w-24">`: (d.burnerIn||'-')}</td>
                    <td class="p-2 text-gray-600 border-r border-gray-100">${isEd?`<div class="flex flex-col gap-1"><input type="date" data-field="initialStockIn" value="${d.initialStockIn||''}" class="p-1 border rounded text-xs w-24"><input type="date" data-field="initialStockEnd" value="${d.initialStockEnd||''}" class="p-1 border rounded text-xs w-24"></div>` : `<div class="flex flex-col text-xs font-medium"><span>${formatRange(s.initialStockIn, s.initialStockEnd)}</span></div>`}</td>
                    <td class="p-2 border-r border-gray-100">${isEd?`<div class="flex flex-col gap-1"><div class="flex gap-1"><input type="date" data-field="preTrainingStart" value="${d.preTrainingStart||''}" class="p-1 border rounded text-xs w-24">~<input type="date" data-field="preTrainingEnd" value="${d.preTrainingEnd||''}" class="p-1 border rounded text-xs w-24"></div><input type="text" data-field="preTrainingMemo" value="${d.preTrainingMemo||''}" class="p-1 border rounded text-xs w-full"></div>` : `<div class="flex flex-col text-xs"><span class="font-medium">${formatRange(s.preTrainingStart, s.preTrainingEnd)}</span>${s.preTrainingMemo ? `<span class="text-gray-500 break-words whitespace-normal mt-0.5">${s.preTrainingMemo}</span>` : ''}</div>`}</td>
                    <td class="p-2 font-bold text-brand-red">${isEd?`<input type="date" data-field="openDate" value="${d.openDate||''}" class="p-1 border border-red-300 bg-red-50 rounded text-xs w-24">`: (d.openDate||'-')}</td>
                    <td class="p-2 text-center align-middle">${actionBtnsHtml}</td>
                </tr>`;
            }).join('');
        }

        function renderCustomSchedulesList() {
            const list = document.getElementById('customSchedulesList'); if(!list) return;
            list.innerHTML = currentCustomSchedules.map((cs, idx) => `
                <li class="flex justify-between items-center bg-gray-50 border border-gray-200 px-3 py-2 rounded shadow-sm text-sm">
                    <div><span class="font-bold text-gray-700">${cs.name}</span> <span class="text-brand-red ml-2 text-xs font-medium">${cs.date}</span></div>
                    <div class="flex gap-3">
                        <button type="button" class="text-gray-500 hover:text-brand-red transition-colors" onclick="window.editCustomSchedule(${idx})" title="수정"><i class="fas fa-pen"></i></button>
                        <button type="button" class="text-gray-500 hover:text-red-600 transition-colors" onclick="window.deleteCustomSchedule(${idx})" title="삭제"><i class="fas fa-trash-alt"></i></button>
                    </div>
                </li>
            `).join('');
        }

        function renderAll() { renderTeamSummary(); renderCalendarGrid(); renderTable(); }

        // 💡 Streamlit 양방향 통신 모듈 (영구 보존 데이터베이스 역할)
        function processSchedulesData(rawSchedules) {
            return rawSchedules.map(s => {
                if(typeof s.constructionType === 'string') { try { s.constructionType = JSON.parse(s.constructionType || '[]'); } catch (e) { s.constructionType = []; } }
                s.status = s.status || '진행중'; if(s.showInCalendar === undefined) s.showInCalendar = true;
                if (s.status !== '완료') s.supervisor = teamSupervisors[s.team] || s.supervisor;
                return s;
            });
        }

        function onRender(event) {
            if (!window.isInitialized) {
                const data = event.detail.args.initial_data;
                schedules = processSchedulesData(data.schedules || []);
                const settings = data.settings || {};
                memberTeams = settings.memberTeams || {};
                allMembers = settings.allMembers || ['이현채', '김성중', '김우진', '이선구', '최병재', '조영준', '신동주', '김구수', '이병인', '임현민'];
                teamSupervisors = settings.teamSupervisors || { 'A': '이현채', 'B': '조영준', 'C': '최병재' };
                renderAll();
                window.isInitialized = true;
            }
            Streamlit.setFrameHeight(1600); // 넉넉한 고정 높이 확보
        }

        Streamlit.events.addEventListener(Streamlit.RENDER_EVENT, onRender);
        Streamlit.setComponentReady();

        // 💡 저장 시 Python 쪽에 데이터를 던져서 영구 저장함
        async function saveData(docId, payload, isSchedule = true) {
            if(isSchedule) {
                const idx = schedules.findIndex(s => String(s.id) === String(docId));
                if (idx > -1) schedules[idx] = payload; else schedules.push(payload);
            } else {
                memberTeams = payload.memberTeams || payload; allMembers = payload.allMembers || allMembers; teamSupervisors = payload.teamSupervisors || teamSupervisors;
            }
            // Streamlit으로 데이터 전송
            Streamlit.setComponentValue({ schedules: schedules, settings: { memberTeams, allMembers, teamSupervisors } });
            renderAll();
        }

        async function deleteData(docId) {
            schedules = schedules.filter(s => String(s.id) !== String(docId));
            Streamlit.setComponentValue({ schedules: schedules, settings: { memberTeams, allMembers, teamSupervisors } });
            renderAll();
        }

        window.handleDragStart = (e, id, typeKey, draggedDate) => { e.dataTransfer.setData('text/plain', JSON.stringify({ id, typeKey, draggedDate })); e.dataTransfer.effectAllowed = 'move'; };
        window.handleDrop = (e, targetDateStr) => {
            e.preventDefault(); const dataStr = e.dataTransfer.getData('text/plain'); if (!dataStr) return; const data = JSON.parse(dataStr);
            const store = schedules.find(s => String(s.id) === String(data.id)); if (!store) return;
            const deltaDays = Math.round((new Date(targetDateStr + 'T12:00:00') - new Date(data.draggedDate + 'T12:00:00')) / 86400000); if (deltaDays === 0) return;
            let updated = { ...store };
            if (data.typeKey === 'oven') { updated.ovenIn = addCalendarDays(updated.ovenIn, deltaDays); updated.ovenEnd = addCalendarDays(updated.ovenEnd, deltaDays); }
            else if (data.typeKey === 'initialStock') { updated.initialStockIn = addCalendarDays(updated.initialStockIn, deltaDays); updated.initialStockEnd = addCalendarDays(updated.initialStockEnd, deltaDays); }
            else if (data.typeKey === 'preTraining') { updated.preTrainingStart = addCalendarDays(updated.preTrainingStart, deltaDays); updated.preTrainingEnd = addCalendarDays(updated.preTrainingEnd, deltaDays); }
            else if (data.typeKey === 'training') { updated.trainingStart = addCalendarDays(updated.trainingStart, deltaDays); updated.trainingEnd = addCalendarDays(updated.trainingEnd, deltaDays); }
            else if (data.typeKey.startsWith('custom_')) {
                const idx = parseInt(data.typeKey.split('_')[1]); let customArr = typeof updated.customSchedules === 'string' ? JSON.parse(updated.customSchedules || '[]') : (updated.customSchedules || []);
                if (customArr[idx]) { customArr[idx].date = addCalendarDays(customArr[idx].date, deltaDays); updated.customSchedules = JSON.stringify(customArr); }
            } else { updated[data.typeKey] = addCalendarDays(updated[data.typeKey], deltaDays); }
            saveData(store.id, updated).then(() => showToast("캘린더 일정이 변경되었습니다."));
        };

        function renderFormCheckboxes(checked) { document.getElementById('formConstructionTypes').innerHTML = CONSTRUCTION_TYPES.map(t => `<label class="flex items-center gap-2 cursor-pointer bg-white border px-3 py-2 rounded-lg hover:bg-gray-50"><input type="checkbox" value="${t}" class="w-4 h-4 text-brand-red form-ctype-chk" ${checked.includes(t)?'checked':''}><span class="text-sm font-medium text-gray-700">${t}</span></label>`).join(''); }
        window.updateModalTeamColor = function(team) { const c = TEAM_COLORS[team] || TEAM_COLORS['A']; const select = document.getElementById('formTeam'); if (select) select.className = `w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-brand-red text-sm font-bold ${c.bg} ${c.text}`; };

        function renderTM() {
            document.getElementById('teamTabs').innerHTML = ['A','B','C'].map(t => `<button type="button" class="team-tab-btn flex-1 py-2 font-bold rounded-lg border ${selectedTeamTab===t?'bg-[#111111] text-white':'bg-white text-gray-600'}" data-team="${t}">${t}팀</button>`).join('');
            document.querySelectorAll('.team-tab-btn').forEach(b => b.onclick = () => { selectedTeamTab = b.getAttribute('data-team'); renderTM(); });

            document.getElementById('teamSupervisorUI').innerHTML = `<div class="flex items-center gap-2 mb-4 bg-gray-100 p-2 rounded-lg border border-gray-200"><label class="text-sm font-bold text-gray-700 whitespace-nowrap ml-2">현재 팀장(담당자):</label><select id="selectSupervisor" class="flex-1 p-1.5 border border-gray-300 rounded text-sm focus:ring-2 focus:ring-brand-red bg-white"><option value="">지정 안 됨</option>${allMembers.map(m => `<option value="${m}" ${tempSupervisors[selectedTeamTab] === m ? 'selected' : ''}>${m}</option>`).join('')}</select></div>`;
            document.getElementById('selectSupervisor').onchange = (e) => { const sm = e.target.value; const pm = tempSupervisors[selectedTeamTab]; if (pm && tempTeams[pm] === selectedTeamTab) delete tempTeams[pm]; tempSupervisors[selectedTeamTab] = sm; if (sm) tempTeams[sm] = selectedTeamTab; renderTM(); };

            const addMemberUI = document.getElementById('addMemberUI');
            if (addMemberUI) { if (isTeamManageMode) addMemberUI.classList.remove('hidden'); else addMemberUI.classList.add('hidden'); }

            const btnToggle = document.getElementById('btnToggleTeamManage');
            if (btnToggle) {
                if (isTeamManageMode) { btnToggle.innerHTML = '<i class="fas fa-check"></i> 관리 완료'; btnToggle.className = "flex items-center gap-1.5 px-4 py-2 bg-red-50 border border-red-200 text-brand-red hover:bg-red-100 rounded-lg text-sm font-bold shadow-sm"; }
                else { btnToggle.innerHTML = '<i class="fas fa-user-cog"></i> 인원 관리'; btnToggle.className = "flex items-center gap-1.5 px-4 py-2 bg-white border border-gray-300 text-gray-700 hover:bg-gray-50 rounded-lg text-sm font-bold shadow-sm"; }
            }

            document.getElementById('teamMembersGrid').innerHTML = allMembers.map(m => {
                const mt = tempTeams[m], isS = mt === selectedTeamTab;
                let bc = 'bg-gray-100 text-gray-500';
                if(mt==='A') bc = 'bg-gray-200 text-[#111111] border-gray-400';
                else if(mt==='B') bc = 'bg-red-100 text-[#D32F2F] border-red-300';
                else if(mt==='C') bc = 'bg-yellow-100 text-[#E8B923] border-yellow-300';
                let actionButtons = isTeamManageMode ? `<div class="absolute -top-2 -right-2 flex gap-1"><button type="button" class="bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs shadow-md btn-delete-member" data-member="${m}"><i class="fas fa-times"></i></button></div>` : '';
                let sb = '';
                if (tempSupervisors['A'] === m) sb = `<span class="text-[9px] px-1.5 py-0.5 rounded mr-1 shadow-sm bg-[#111111] text-white font-bold border border-gray-600">팀장</span>`;
                else if (tempSupervisors['B'] === m) sb = `<span class="text-[9px] px-1.5 py-0.5 rounded mr-1 shadow-sm bg-[#D32F2F] text-white font-bold border border-red-600">팀장</span>`;
                else if (tempSupervisors['C'] === m) sb = `<span class="text-[9px] px-1.5 py-0.5 rounded mr-1 shadow-sm bg-[#E8B923] text-black font-bold border border-yellow-600">팀장</span>`;
                return `<div class="relative"><button type="button" class="w-full member-btn p-3 border rounded-xl flex flex-col items-center gap-1 ${isS && !isTeamManageMode ? 'ring-2 ring-gray-800' : ''} ${mt?bc:'bg-white'} ${isTeamManageMode?'cursor-default':'cursor-pointer hover:brightness-95'}" data-member="${m}" ${isTeamManageMode ? 'disabled' : ''}><div class="flex items-center justify-center"><span class="font-semibold text-sm flex items-center">${sb}${m}</span></div><span class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-white/70">${mt?mt+'팀':'미배정'}</span></button>${actionButtons}</div>`;
            }).join('');

            if (!isTeamManageMode) { document.querySelectorAll('.member-btn').forEach(b => { b.onclick = () => { const m = b.getAttribute('data-member'); if(tempTeams[m] === selectedTeamTab) delete tempTeams[m]; else tempTeams[m] = selectedTeamTab; renderTM(); }; }); }
            else { document.querySelectorAll('.btn-delete-member').forEach(b => { b.onclick = (e) => { e.stopPropagation(); const m = b.getAttribute('data-member'); window.showCnf(`[${m}] 팀원을 명단에서 삭제하시겠습니까?`, () => { allMembers = allMembers.filter(x => x !== m); delete tempTeams[m]; renderTM(); }); }; }); }
        }

        window.showCnf = function(msg, cb) { document.getElementById('confirmMessage').innerText = msg; document.getElementById('confirmModal').classList.remove('hidden'); window.confirmCbk = cb; }
        document.getElementById('btnConfirmCancel').onclick = () => document.getElementById('confirmModal').classList.add('hidden');
        document.getElementById('btnConfirmOk').onclick = () => { document.getElementById('confirmModal').classList.add('hidden'); if(window.confirmCbk) window.confirmCbk(); };
        window.deleteCustomSchedule = (idx) => { currentCustomSchedules.splice(idx, 1); renderCustomSchedulesList(); };
        window.editCustomSchedule = (idx) => { const cs = currentCustomSchedules[idx]; document.getElementById('customScheduleName').value = cs.name; document.getElementById('customScheduleDate').value = cs.date; currentCustomSchedules.splice(idx, 1); renderCustomSchedulesList(); document.getElementById('customScheduleName').focus(); };

        document.addEventListener('DOMContentLoaded', () => {
            document.getElementById('btnToggleTeamManage').onclick = () => { isTeamManageMode = !isTeamManageMode; renderTM(); };
            document.getElementById('btnAddMember').onclick = () => { const n = document.getElementById('newMemberName').value.trim(); if (!n) return; if (allMembers.includes(n)) return; allMembers.push(n); document.getElementById('newMemberName').value = ''; renderTM(); };
            document.getElementById('btnAddCustomSchedule').onclick = () => { const n = document.getElementById('customScheduleName').value.trim(); const d = document.getElementById('customScheduleDate').value; if (!n || !d) return; currentCustomSchedules.push({ name: n, date: d }); document.getElementById('customScheduleName').value = ''; document.getElementById('customScheduleDate').value = ''; renderCustomSchedulesList(); };
            document.getElementById('btnPrevMonth').onclick = () => { currentDate.setMonth(currentDate.getMonth() - 1); renderCalendarGrid(); };
            document.getElementById('btnNextMonth').onclick = () => { currentDate.setMonth(currentDate.getMonth() + 1); renderCalendarGrid(); };
            
            window.handleDateClick = (dStr) => { document.getElementById('storeForm').reset(); document.getElementById('formId').value = ''; document.getElementById('formTeam').value = 'A'; window.updateModalTeamColor('A'); document.getElementById('formSupervisor').value = teamSupervisors['A'] || ''; document.getElementById('formOpenDate').value = dStr; renderFormCheckboxes([]); currentCustomSchedules = []; renderCustomSchedulesList(); document.getElementById('btnDeleteStoreModal').classList.add('hidden'); document.getElementById('storeModalTitle').innerHTML = '<i class="fas fa-store text-brand-red"></i> 가맹점 일정 등록'; document.getElementById('storeModal').classList.remove('hidden'); };
            window.handleEventClick = (e, id) => {
                e.stopPropagation(); const s = schedules.find(x => String(x.id) === String(id));
                if (s) {
                    document.getElementById('formId').value = s.id; document.getElementById('formStoreNumber').value = s.storeNumber || ''; document.getElementById('formStoreName').value = s.storeName || ''; document.getElementById('formTeam').value = s.team || 'A'; window.updateModalTeamColor(s.team || 'A'); document.getElementById('formSupervisor').value = s.supervisor || '';
                    renderFormCheckboxes(typeof s.constructionType === 'string' ? JSON.parse(s.constructionType || '[]') : (s.constructionType || []));
                    currentCustomSchedules = typeof s.customSchedules === 'string' ? JSON.parse(s.customSchedules || '[]') : (s.customSchedules || []); renderCustomSchedulesList();
                    document.getElementById('formKitchenVendor').value = s.kitchenVendor || '형제'; document.getElementById('formGasType').value = s.gasType || 'LNG'; document.getElementById('formNotes').value = s.notes || '';
                    ['constructionStart','constructionEnd','ovenIn','ovenEnd','burnerIn','initialStockIn','initialStockEnd','preTrainingStart','preTrainingEnd','preTrainingMemo','trainingStart','trainingEnd','openDate'].forEach(f => { const el = document.getElementById('form' + f.charAt(0).toUpperCase() + f.slice(1)); if(el) el.value = s[f] || ''; });
                    document.getElementById('btnDeleteStoreModal').classList.remove('hidden'); document.getElementById('storeModal').classList.remove('hidden');
                }
            };
            
            document.getElementById('btnOpenStoreModal').onclick = () => window.handleDateClick('');
            document.getElementById('btnCloseStoreModal').onclick = () => document.getElementById('storeModal').classList.add('hidden');
            document.getElementById('btnCancelStoreModal').onclick = () => document.getElementById('storeModal').classList.add('hidden');
            document.getElementById('formTeam').onchange = (e) => { window.updateModalTeamColor(e.target.value); const fId = document.getElementById('formId').value; const es = schedules.find(s => String(s.id) === String(fId)); if (!(es && es.status === '완료')) document.getElementById('formSupervisor').value = teamSupervisors[e.target.value] || ''; };
            document.getElementById('formConstructionStart').addEventListener('change', (e) => {
                const val = e.target.value; if(!val) return; const d = calculateAutoDates(val);
                document.getElementById('formConstructionEnd').value = d.constructionEnd; document.getElementById('formOvenIn').value = d.ovenIn; document.getElementById('formOvenEnd').value = d.ovenEnd; document.getElementById('formBurnerIn').value = d.burnerIn; document.getElementById('formInitialStockIn').value = d.initialStockIn; document.getElementById('formInitialStockEnd').value = d.initialStockEnd; document.getElementById('formTrainingStart').value = d.trainingStart; document.getElementById('formTrainingEnd').value = d.trainingEnd; document.getElementById('formOpenDate').value = d.openDate; showToast("자동 세팅이 완료되었습니다.");
            });
            
            document.getElementById('btnSaveStoreModal').onclick = () => {
                const docId = document.getElementById('formId').value || String(Date.now());
                const payload = {
                    id: docId, storeNumber: document.getElementById('formStoreNumber').value.trim(), storeName: document.getElementById('formStoreName').value,
                    team: document.getElementById('formTeam').value, supervisor: document.getElementById('formSupervisor').value,
                    constructionType: JSON.stringify(Array.from(document.querySelectorAll('.form-ctype-chk:checked')).map(el=>el.value)), customSchedules: JSON.stringify(currentCustomSchedules),
                    kitchenVendor: document.getElementById('formKitchenVendor').value, gasType: document.getElementById('formGasType').value, notes: document.getElementById('formNotes').value,
                    status: (schedules.find(s => String(s.id) === String(docId)) || {}).status || '진행중'
                };
                ['constructionStart','constructionEnd','ovenIn','ovenEnd','burnerIn','initialStockIn','initialStockEnd','preTrainingStart','preTrainingEnd','preTrainingMemo','trainingStart','trainingEnd','openDate'].forEach(f => payload[f] = document.getElementById('form' + f.charAt(0).toUpperCase() + f.slice(1)).value);
                saveData(docId, payload).then(() => { document.getElementById('storeModal').classList.add('hidden'); showToast("저장되었습니다."); });
            };
            
            document.getElementById('btnDeleteStoreModal').onclick = () => window.showCnf('일정을 영구 삭제하시겠습니까?', () => deleteData(document.getElementById('formId').value).then(() => document.getElementById('storeModal').classList.add('hidden')));
            
            document.getElementById('tableTabs').addEventListener('click', e => { const btn = e.target.closest('.tab-btn'); if(btn) { currentViewTab = btn.getAttribute('data-tab'); editingRowId = null; renderTable(); } });
            document.getElementById('tableBody').addEventListener('change', e => {
                if(!editingRowId) return;
                if (e.target.getAttribute('data-field') === 'team') { inlineEditData.team = e.target.value; if (inlineEditData.status !== '완료') inlineEditData.supervisor = teamSupervisors[e.target.value] || ''; renderTable(); return; }
                if(e.target.classList.contains('inline-ctype-chk')) {
                    const v = e.target.value; let cts = inlineEditData.constructionType || []; if(typeof cts === 'string') { try { cts = JSON.parse(cts); } catch(err) { cts = []; } }
                    if(e.target.checked) cts.push(v); else { const ix = cts.indexOf(v); if(ix>-1) cts.splice(ix,1); } inlineEditData.constructionType = JSON.stringify(cts);
                }
            });
            document.getElementById('tableBody').addEventListener('input', e => {
                if(!editingRowId) return; const f = e.target.getAttribute('data-field');
                if(f && f !== 'team') {
                    inlineEditData[f] = e.target.value;
                    if(f === 'constructionStart') { const d = calculateAutoDates(e.target.value); if(d.constructionEnd) { inlineEditData = { ...inlineEditData, ...d }; renderTable(); showToast("기준일 변경으로 후속 일정이 자동 재조정되었습니다."); } }
                }
            });
            document.getElementById('tableBody').addEventListener('click', e => {
                const tr = e.target.closest('tr'); if(!tr) return; const id = tr.getAttribute('data-id');
                if (e.target.closest('.btn-toggle-vis')) { const s = schedules.find(x => String(x.id) === String(id)); if(s) saveData(id, { ...s, showInCalendar: s.showInCalendar === false ? true : false }, true); return; }
                if (e.target.closest('.btn-action-complete')) { const s = schedules.find(x => String(x.id) === String(id)); if(s) saveData(id, { ...s, status: '완료', showInCalendar: false }, true).then(() => showToast("오픈 완료 처리되었습니다.")); return; }
                if (e.target.closest('.btn-action-restore')) { const s = schedules.find(x => String(x.id) === String(id)); if(s) saveData(id, { ...s, status: '진행중', showInCalendar: true }, true).then(() => showToast("진행중 목록으로 복구되었습니다.")); return; }
                if (e.target.closest('.btn-inline-edit')) { const s = schedules.find(x => String(x.id) === String(id)); if(s) { editingRowId = String(id); inlineEditData = JSON.parse(JSON.stringify(s)); renderTable(); } }
                else if (e.target.closest('.btn-inline-cancel')) { editingRowId = null; renderTable(); }
                else if (e.target.closest('.btn-inline-save')) { const payload = {...inlineEditData}; saveData(id, payload).then(() => { editingRowId = null; showToast("저장되었습니다."); }); }
                else if (e.target.closest('.btn-inline-delete')) { window.showCnf('정말 삭제하시겠습니까?', () => deleteData(id).then(() => { editingRowId = null; })); }
            });
            
            document.getElementById('btnOpenTeamModal').onclick = () => { tempTeams = {...memberTeams}; tempSupervisors = {...teamSupervisors}; selectedTeamTab = 'A'; isTeamManageMode = false; renderTM(); document.getElementById('teamModal').classList.remove('hidden'); };
            document.getElementById('btnCloseTeamModal').onclick = () => { document.getElementById('teamModal').classList.add('hidden'); }
            document.getElementById('btnCancelTeamModal').onclick = () => { document.getElementById('teamModal').classList.add('hidden'); }
            document.getElementById('btnSaveTeamModal').onclick = () => { saveData(null, { memberTeams: tempTeams, allMembers: allMembers, teamSupervisors: tempSupervisors }, false).then(() => { teamSupervisors = {...tempSupervisors}; document.getElementById('teamModal').classList.add('hidden'); showToast("팀 세팅이 저장되었습니다."); }); };
        });
    </script>
    </body></html>
    """
    
    # 💡 영구 저장 디렉토리 및 파일 셋업
    frontend_dir = os.path.join(os.getcwd(), "calendar_frontend")
    os.makedirs(frontend_dir, exist_ok=True)
    with open(os.path.join(frontend_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(calendar_html)
        
    # Streamlit Component 양방향 브릿지 생성
    calendar_comp = components.declare_component("calendar_comp", path=frontend_dir)
    initial_data = load_calendar_data()
    
    new_data = calendar_comp(initial_data=initial_data, key="calendar_app")
    if new_data is not None:
        save_calendar_data(new_data)
