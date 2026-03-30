import streamlit as st
import pandas as pd
import plotly.express as px
import os
import hashlib
from datetime import datetime, timedelta
import numpy as np
import re

# ==========================================
# 1. 페이지 기본 설정 및 상태 초기화
# ==========================================
st.set_page_config(page_title="달빛에구운고등어 본사 인트라넷", layout="wide")

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

# ==========================================
# 2. 공통 CSS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Gowun+Dodum&family=Noto+Sans+KR:wght@400;500;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Noto Sans KR', sans-serif !important;
    }
    h1, h2, h3, .brand-title {
        font-family: 'Gowun Dodum', sans-serif !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] {
        background-color: #111111 !important;
        border-right: none !important;
    }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] span, 
    [data-testid="stSidebar"] div {
        color: #FFFFFF !important; 
    }
    div[data-testid="InputInstructions"] { display: none !important; }
    [data-testid="stForm"] { border: none !important; padding: 0 !important; background-color: transparent !important; }
    div[data-testid="column"] { padding: 0 4px !important; }
    [data-testid="baseButton-primary"] {
        border-radius: 4px !important;
        height: 42px !important;
        transition: all 0.2s ease;
    }
    [data-testid="baseButton-primary"] p, [data-testid="baseButton-primary"] span {
        font-weight: 700 !important;
        color: #FFFFFF !important;
    }
    .top-theme-marker + div button {
        border-radius: 50% !important;
        width: 40px !important; height: 40px !important;
        padding: 0 !important; float: right !important; margin-top: 10px !important;
        display: flex !important; justify-content: center !important; align-items: center !important;
        transition: all 0.3s ease;
    }
    .top-theme-marker + div button p, .top-theme-marker + div button span { font-size: 16px !important; line-height: 1 !important; }
    
    /* 분석 리포트 박스 스타일 */
    .ai-report-box {
        padding: 25px;
        border-radius: 8px;
        border-left: 5px solid #D32F2F;
        background-color: #222222;
        margin-top: 10px;
        margin-bottom: 20px;
    }
    .ai-report-title { font-weight: 700; color: #deff9a; font-size: 18px; margin-bottom: 12px; }
    .ai-report-content { color: #f5f5f5; line-height: 1.6; font-size: 15px; }
    .suggested-keywords { font-weight: 700; color: #4CAF50; margin-top: 10px; display: block; }
</style>
""", unsafe_allow_html=True)

if st.session_state.theme == "dark":
    st.markdown("""
    <style>
        .stApp { background-color: #1A1A1A !important; }
        h1, h2, h3, h4, h5, h6, p, label, span { color: #F0F0F0 !important; }
        div[data-testid="metric-container"] {
            background-color: #222222 !important; border: 1px solid #333333 !important;
            padding: 20px 25px; border-radius: 4px; border-left: 4px solid #D32F2F !important; 
        }
        .main-content div[data-baseweb="select"] > div, .main-content div[data-baseweb="input"] > div, .main-content .stTextInput input {
            background-color: #222222 !important; color: #FFFFFF !important;
            -webkit-text-fill-color: #FFFFFF !important; border: 1px solid #444444 !important; border-radius: 4px !important;
        }
        div[data-testid="stExpander"] { background-color: #222222 !important; border-radius: 4px; border: 1px solid #333333 !important; border-left: 3px solid #D32F2F !important; }
        div[data-testid="stExpander"] summary p { font-weight: 600 !important; color: #F0F0F0 !important; }
        [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #333333 !important; background-color: #222222 !important; }
        [data-testid="baseButton-primary"] { background-color: #333333 !important; border: 1px solid #555555 !important; }
        .top-theme-marker + div button { background-color: #222222 !important; border: 1px solid #444444 !important; }
        .top-theme-marker + div button p { color: #888888 !important; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #F8F9FA !important; }
        h1, h2, h3, h4, h5, h6, p, label, span { color: #111111 !important; }
        div[data-testid="metric-container"] {
            background-color: #FFFFFF !important; border: 1px solid #E0E0E0 !important;
            padding: 20px 25px; border-radius: 4px; border-left: 4px solid #D32F2F !important; 
        }
        .main-content div[data-baseweb="select"] > div, .main-content div[data-baseweb="input"] > div, .main-content .stTextInput input {
            background-color: #FFFFFF !important; color: #111111 !important;
            -webkit-text-fill-color: #111111 !important; border: 1px solid #CCCCCC !important; border-radius: 4px !important;
        }
        div[data-testid="stExpander"] { background-color: #FFFFFF !important; border-radius: 4px; border: 1px solid #E0E0E0 !important; border-left: 3px solid #D32F2F !important; }
        div[data-testid="stExpander"] summary p { font-weight: 600 !important; color: #111111 !important; }
        [data-testid="stDataFrame"] { border-radius: 4px; overflow: hidden; border: 1px solid #E0E0E0 !important; background-color: #FFFFFF !important; }
        [data-testid="baseButton-primary"] { background-color: #111111 !important; border: 1px solid #000000 !important; }
        .top-theme-marker + div button { background-color: #FFFFFF !important; border: 1px solid #CCCCCC !important; }
        .top-theme-marker + div button p { color: #888888 !important; }
        .ai-report-box { background-color: #FFFFFF; border: 1px solid #E0E0E0; border-left: 5px solid #D32F2F; }
        .ai-report-title { color: #D32F2F; }
        .ai-report-content { color: #111111; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 4. 보안 로그인 시스템
# ==========================================
def check_password():
    if "password_correct" in st.session_state and st.session_state["password_correct"]: return True
    st.markdown("""
    <style>
        .stApp { background-color: #000000 !important; }
        [data-testid="stHeader"], [data-testid="stSidebar"] { display: none !important; }
        @keyframes logoZoomIn { 0% { transform: scale(3.5); opacity: 0; } 100% { transform: scale(1); opacity: 1; } }
        .animated-logo { animation: logoZoomIn 1.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; max-width: 280px; margin: 0 auto 30px auto; display: block; }
        [data-testid="stForm"] { max-width: 280px !important; margin: 0 auto !important; background-color: transparent !important; border: none !important; }
        div[data-baseweb="input"] > div { background-color: #111111 !important; border: 1px solid #444444 !important; border-radius: 4px !important; height: 42px !important; }
        input[type="password"] { color: #FFFFFF !important; -webkit-text-fill-color: #FFFFFF !important; text-align: center !important; font-size: 13px !important; letter-spacing: 2px; background-color: transparent !important; }
        [data-testid="stFormSubmitButton"] > button { background-color: #444444 !important; border: 1px solid #666666 !important; border-radius: 4px !important; height: 42px !important; width: 100% !important; padding: 0 !important; }
        [data-testid="stFormSubmitButton"] > button p { color: #FFFFFF !important; font-size: 11px !important; font-weight: 700 !important; letter-spacing: 1px; margin: 0 !important; }
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='margin-top: 25vh; text-align: center;'>", unsafe_allow_html=True)
        st.markdown('<img src="https://dalbitgo.com/images/main_logo.png" class="animated-logo">', unsafe_allow_html=True)
        with st.form("login_form", clear_on_submit=True):
            c_in, c_btn = st.columns([2.5, 1])
            with c_in: pwd = st.text_input("auth", type="password", placeholder="인증코드", label_visibility="collapsed")
            with c_btn: submit = st.form_submit_button("LOGIN")
            if submit:
                if pwd == "51015":
                    st.session_state["password_correct"] = True
                    st.rerun()
                elif pwd: st.error("인증 코드가 일치하지 않습니다.")
        st.markdown("</div>", unsafe_allow_html=True)
    return False

if not check_password(): st.stop()

# ==========================================
# 5. 데이터 로드 및 정제
# ==========================================
STATE_RESOLVED  = "state_resolved.csv"
STATE_OVERRIDDEN = "state_overridden.csv"

def get_saved_ids(filename):
    if os.path.exists(filename): return pd.read_csv(filename)['id'].astype(str).tolist()
    return []

def add_saved_id(filename, new_id):
    ids = get_saved_ids(filename)
    if str(new_id) not in ids:
        ids.append(str(new_id))
        pd.DataFrame({'id': ids}).to_csv(filename, index=False)

def generate_id(row):
    return hashlib.md5(f"{row['매장명']}_{row['작성일']}_{row['리뷰내용']}".encode()).hexdigest()

def load_data():
    filename = "가맹점_리뷰수집결과_누적.csv"
    if os.path.exists(filename):
        df = pd.read_csv(filename)
        df.drop_duplicates(subset=['매장명', '작성일', '리뷰내용'], keep='last', inplace=True)
    else:
        df = pd.DataFrame(columns=["매장명", "작성일", "리뷰내용", "감정분석"])
    if not df.empty:
        df['id'] = df.apply(generate_id, axis=1)
        overridden_ids = get_saved_ids(STATE_OVERRIDDEN)
        df.loc[df['id'].isin(overridden_ids), '감정분석'] = '긍정'
    return df

df = load_data()
full_store_list = sorted(df['매장명'].unique().tolist()) if not df.empty else []

# ==========================================
# 6. 사이드바
# ==========================================
st.sidebar.markdown("""
<div style="padding: 10px; text-align: center; margin-top: 20px; margin-bottom: 30px;">
    <img src="https://dalbitgo.com/images/main_logo.png" style="max-width: 90%;"
        onerror="this.onerror=null; this.style.display='none'; this.insertAdjacentHTML('afterend', '<span style=\\'color:#FFFFFF; font-size:15px; font-weight:700;\\'>달빛에 구운 고등어</span>');">
</div>
""", unsafe_allow_html=True)
st.sidebar.markdown("<p style='font-size: 15px; font-weight: 700; text-align: center;'>가맹점 리뷰 통합 관리</p>", unsafe_allow_html=True)
st.sidebar.divider()
st.sidebar.markdown("<div style='height: 45vh;'></div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style='text-align: center; font-size: 11px; line-height: 1.6; color: #666666 !important; border-top: 1px solid #333333; padding-top: 15px;'>
    <b>(주)새모양에프앤비</b><br>
    COPYRIGHT © 달빛에 구운 고등어
</div>
""", unsafe_allow_html=True)

# ==========================================
# 7. 메인 화면
# ==========================================
st.markdown('<div class="main-content">', unsafe_allow_html=True)

col_title, col_theme = st.columns([10, 1])
with col_title:
    st.markdown("<h1 style='margin-bottom: 30px;'>가맹점 리뷰 통합 관리 <span style='font-size: 18px; color: #888 !important; font-weight: 500;'>| Review Management</span></h1>", unsafe_allow_html=True)
with col_theme:
    st.markdown('<div class="top-theme-marker"></div>', unsafe_allow_html=True)
    theme_icon = "○" if st.session_state.theme == "light" else "●"
    if st.button(theme_icon, key="top_theme_btn", help="다크/라이트 모드 변경"):
        st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"
        st.rerun()

tab1, tab2, tab3 = st.tabs(["전체 브랜드 현황", "개별 매장 상세분석", "키워드 마케팅 성과 (ROI)"])

# ── 탭1: 전체 브랜드 현황 ─────────────────
with tab1:
    st.markdown("<h3 style='margin-top: 25px; margin-bottom: 15px;'>즉각 조치 요망 매장 리스트 (영구 보존)</h3>", unsafe_allow_html=True)
    if df.empty:
        st.info("아직 수집된 리뷰 데이터가 없습니다.")
    else:
        total_neg_df = df[df['감정분석'] == '부정']
        resolved_ids = get_saved_ids(STATE_RESOLVED)
        active_neg = total_neg_df[~total_neg_df['id'].isin(resolved_ids)].sort_values(by='작성일', ascending=False)
        
        if total_neg_df.empty: st.success("누적된 수집 리뷰 중 부정 키워드가 감지된 내역이 없습니다.")
        elif not active_neg.empty:
            st.error(f"총 {len(active_neg)}건의 미조치 부정 리뷰가 남아있습니다.")
            for _, row in active_neg.iterrows():
                with st.expander(f"[{row['매장명']}] {row['작성일']} | {str(row['리뷰내용'])[:35]}..."):
                    st.write(f"**상세 내용:** {row['리뷰내용']}")
                    c1, c2, _ = st.columns([1.5, 1.5, 3])
                    if c1.button("해피콜 조치 완료", key=f"re_{row['id']}", use_container_width=True, type="primary"):
                        add_saved_id(STATE_RESOLVED, row['id']); st.rerun()
                    if c2.button("긍정 분류 예외 처리", key=f"ov_{row['id']}", use_container_width=True, type="primary"):
                        add_saved_id(STATE_OVERRIDDEN, row['id']); st.rerun()
        else: st.success(f"부정 리뷰 {len(total_neg_df)}건 조치 완료되었습니다.")
        
        st.divider()
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        st.markdown(f"<h3 style='margin-bottom: 15px;'>매장별 활성도 랭킹 (어제 기준: {yesterday_str})</h3>", unsafe_allow_html=True)
        
        all_counts = pd.DataFrame({'매장명': full_store_list, '리뷰수': 0})
        yesterday_df = df[df['작성일'] == yesterday_str]
        if not yesterday_df.empty:
            y_counts = yesterday_df['매장명'].value_counts().reset_index(name='리뷰수')
            merged_counts = pd.merge(all_counts, y_counts, on='매장명', how='left').fillna(0)
            merged_counts['리뷰수'] = merged_counts['리뷰수_x'] + merged_counts['리뷰수_y']
            merged_counts.drop(columns=['리뷰수_x', '리뷰수_y'], inplace=True)
            all_counts = merged_counts
        all_counts['리뷰수'] = all_counts['리뷰수'].astype(int)
        all_counts = all_counts.sort_values(by=['리뷰수', '매장명'], ascending=[False, True]).reset_index(drop=True)
        col_l, col_r = st.columns(2)
        with col_l: st.info("리뷰 활성화 우수 매장 (TOP 5)"); st.dataframe(all_counts.head(5), use_container_width=True)
        with col_r: st.warning("리뷰 관리 필요 매장 (BOTTOM 5)"); st.dataframe(all_counts.tail(5), use_container_width=True)

# ── 탭2: 개별 매장 상세분석 ───────────────
with tab2:
    st.markdown("<b style='font-size: 14px; display: block; margin-bottom: 8px;'>매장 검색 및 선택</b>", unsafe_allow_html=True)
    q = st.text_input(" ", placeholder="매장명을 입력하세요 (예: 첨단, 어양)", key="s_store_tab2", label_visibility="collapsed")
    f_stores = [s for s in full_store_list if q.replace(" ","") in s.replace(" ","")] if q else full_store_list
    
    if f_stores:
        sel_store = st.selectbox("조회할 매장을 선택하십시오", f_stores, key="sb_tab2", label_visibility="collapsed")
        if not df.empty:
            s_df = df[df['매장명'] == sel_store]
            if not s_df.empty:
                st.markdown(f"<h3 style='margin-top: 30px; margin-bottom: 20px;'>[{sel_store}] 리뷰 분석 리포트</h3>", unsafe_allow_html=True)
                unique_days = s_df['작성일'].nunique()
                daily_average = round(len(s_df) / unique_days, 1) if unique_days > 0 else 0
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("누적 수집 리뷰", f"{len(s_df)}건")
                m2.metric("일평균 작성량", f"{daily_average}건")
                m3.metric("긍정 평가", f"{len(s_df[s_df['감정분석'] == '긍정'])}건")
                m4.metric("부정 평가", f"{len(s_df[s_df['감정분석'] == '부정'])}건")
                
                st.markdown("<div style='margin-top: 35px; margin-bottom: 10px;'><b>일자별 리뷰 감정 추이</b></div>", unsafe_allow_html=True)
                trend_df = s_df.groupby(['작성일', '감정분석']).size().reset_index(name='건수').sort_values(by='작성일')
                chart_font_color = "#E0E0E0" if st.session_state.theme == "dark" else "#111111"
                chart_grid_color = "#333333" if st.session_state.theme == "dark" else "#EAEAEA"
                color_map = {'긍정': '#4CAF50', '부정': '#E53935', '중립': '#9E9E9E'}
                fig_bar = px.bar(trend_df, x='작성일', y='건수', color='감정분석', text='건수', color_discrete_map=color_map, barmode='stack')
                fig_bar.update_layout(margin=dict(t=20, b=20, l=0, r=0), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color=chart_font_color, family="Noto Sans KR"), xaxis=dict(title="", type='category', showgrid=False), yaxis=dict(title="건수", showgrid=True, gridcolor=chart_grid_color, dtick=1), legend=dict(title="", orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
                st.plotly_chart(fig_bar, use_container_width=True)
                
                st.dataframe(s_df[['작성일', '감정분석', '리뷰내용']].sort_values(by='작성일', ascending=False), use_container_width=True)
            else: st.info("선택하신 매장의 수집된 데이터가 없습니다.")

# ── 탭3: 키워드 마케팅 성과 ───────────────
with tab3:
    st.markdown("<h3 style='margin-top: 25px; margin-bottom: 15px;'>가맹점별 네이버 키워드 마케팅 ROI 분석</h3>", unsafe_allow_html=True)
    
    roi_file = "가맹점_키워드_ROI_분석결과.csv"
    
    if os.path.exists(roi_file):
        roi_df = pd.read_csv(roi_file)
        
        def parse_rate(x):
            try: return float(str(x).replace('%', '').replace('분석 불가 (리뷰 없음)', '0'))
            except: return 0.0
        def parse_vol(x):
            try: return int(str(x).replace('회', '').replace(',', ''))
            except: return 0
            
        roi_df['적중률_num'] = roi_df['키워드_적중률'].apply(parse_rate)
        roi_df['검색량_num'] = roi_df['네이버_월간_총검색량'].apply(parse_vol)
        roi_df['미등록_플래그'] = roi_df['세팅된_키워드'].apply(lambda x: True if str(x) in ["키워드 미설정", "키워드 없음", "nan"] else False)
        
        avg_rate = round(roi_df[roi_df['적중률_num'] > 0]['적중률_num'].mean(), 1) if not roi_df[roi_df['적중률_num'] > 0].empty else 0
        total_vol = roi_df['검색량_num'].sum()
        
        c1, c2, c3 = st.columns(3)
        c1.metric("분석 완료 매장", f"{len(roi_df)}개 지점")
        c2.metric("전국 평균 키워드 적중률", f"{avg_rate}%")
        c3.metric("브랜드 총 확보 월간검색량", f"{total_vol:,}회")
        st.divider()
        
        st.markdown("<h3 style='margin-bottom: 20px;'>개별 매장 키워드 정밀 진단 및 AI 추천</h3>", unsafe_allow_html=True)
        
        # 원본 성적표 데이터를 먼저 역순으로 정렬
        sorted_raw_df = roi_df.sort_values(
            by=['미등록_플래그', '적중률_num', '검색량_num'], 
            ascending=[False, True, True]
        ).reset_index(drop=True)
        
        # 하단 표 클릭 감지 로직 (스크롤 없이 선택 연동만 유지)
        if "prev_selection" not in st.session_state:
            st.session_state.prev_selection = []

        current_selection = []
        if "roi_table" in st.session_state:
            current_selection = st.session_state.roi_table.get("selection", {}).get("rows", [])

        if current_selection != st.session_state.prev_selection:
            st.session_state.prev_selection = current_selection

        selected_store_from_table = None
        if current_selection:
            selected_store_from_table = sorted_raw_df.iloc[current_selection[0]]['매장명']

        # 매장 검색창
        k_query = st.text_input("분석할 매장명을 검색하세요 (예: 첨단, 어양)", key="s_store_tab3")
        all_roi_stores = roi_df['매장명'].tolist()
        
        if k_query:
            k_query_clean = k_query.replace(" ", "")
            k_stores = [s for s in all_roi_stores if k_query_clean in s.replace(" ", "")]
        else:
            k_stores = all_roi_stores
            
        if k_stores:
            default_idx = 0
            if selected_store_from_table and selected_store_from_table in k_stores:
                default_idx = k_stores.index(selected_store_from_table)
                
            selected_k_store = st.selectbox("진단할 매장 선택", k_stores, index=default_idx, label_visibility="collapsed")
            
            store_k_data = roi_df[roi_df['매장명'] == selected_k_store].iloc[0]
            s_rate = store_k_data['적중률_num']
            s_vol = store_k_data['검색량_num']
            s_kw = str(store_k_data['세팅된_키워드'])
            is_empty = store_k_data['미등록_플래그']
            raw_details = str(store_k_data['상세_분석내역'])
            
            if raw_details == 'nan' or raw_details == 'None':
                raw_details = "분석 내역 없음"
            
            r1, r2, r3 = st.columns(3)
            r1.metric("현재 세팅된 키워드", "미등록 상태" if is_empty else f"{len(s_kw.split(','))}개 단어 사용")
            r2.metric("고객 리뷰 적중률 (ROI)", f"{s_rate}%")
            r3.metric("키워드 총 월간 검색량", f"{s_vol:,}회")
            
            st.markdown(f"<br><b style='font-size: 16px;'>[{selected_k_store}] 현재 사용 중인 키워드 성과 상세</b>", unsafe_allow_html=True)
            parsed_details = []
            
            if raw_details not in ["분석 내역 없음", "-"]:
                matches = re.findall(r'\[(.*?)\]', raw_details)
                for match in matches:
                    if ":" in match:
                        kw_part, stats_part = match.split(":", 1)
                        kw = kw_part.strip()
                        rev_cnt = "0회"
                        vol_cnt = "0회"
                        
                        if "|" in stats_part:
                            r_part, v_part = stats_part.split("|", 1)
                            rev_cnt = r_part.replace("리뷰", "").strip()
                            vol_cnt = v_part.replace("검색량", "").strip()
                        else:
                            rev_cnt = stats_part.replace("리뷰", "").strip()
                            
                        parsed_details.append({"등록 키워드": kw, "고객 리뷰 적중(언급)": rev_cnt, "네이버 월간 검색량": vol_cnt})
            
            if parsed_details:
                st.dataframe(pd.DataFrame(parsed_details), use_container_width=True, hide_index=True)
            else:
                st.info("등록된 키워드가 없거나 세부 성과 데이터가 없습니다.")

            store_positive_reviews = df[(df['매장명'] == selected_k_store) & (df['감정분석'] == '긍정')]['리뷰내용'].dropna().tolist()
            suggested_text = ""
            if store_positive_reviews:
                candidate_keywords = ['가성비', '가족', '모임', '깔끔', '주차', '반찬', '친절', '회식', '아이', '부모님', '신선', '푸짐', '청결', '분위기', '넓은', '단체']
                found_words = []
                for kw in candidate_keywords:
                    cnt = sum(1 for text in store_positive_reviews if kw in str(text))
                    if cnt > 0: found_words.append((kw, cnt))
                
                found_words.sort(key=lambda x: x[1], reverse=True)
                top_suggested = [f"{w}({c}회)" for w, c in found_words[:5]]
                suggested_text = ", ".join(top_suggested) if top_suggested else "특별히 반복되는 뚜렷한 핵심 단어 부족"
            else:
                suggested_text = "분석 가능한 긍정 리뷰 데이터 부족"

            median_vol = roi_df[roi_df['검색량_num'] > 0]['검색량_num'].median() if not roi_df[roi_df['검색량_num'] > 0].empty else 1000
            median_rate = roi_df[roi_df['적중률_num'] > 0]['적중률_num'].median() if not roi_df[roi_df['적중률_num'] > 0].empty else 5.0
            
            report_title = ""
            report_body = ""
            
            if is_empty:
                report_title = "[위험] 키워드 방치 (검색 노출 포기)"
                report_body = f"현재 <b>{selected_k_store}</b>은(는) 네이버 스마트플레이스 내 대표 키워드가 단 한 개도 등록되지 않은 심각한 마케팅 방치 상태(깡통 매장)입니다. 지역 고객들이 네이버 지도나 검색창에서 메뉴를 검색할 때, 우리 매장은 아예 노출 대상에서 제외되어 경쟁사에게 모든 트래픽과 잠재 고객을 빼앗기고 있습니다. 오프라인으로 비유하자면 간판 불을 끄고 장사하는 것과 같습니다.<br><br>당장 네이버 관리자 센터에 접속하여 상권에 맞는 로컬 타겟 키워드 5개를 꽉 채워 넣으셔야 합니다. 본사에서 추천하는 기본 조합은 <b>[{selected_k_store.replace('점','')} 맛집]</b>, <b>[{selected_k_store.replace('점','')} 생선구이]</b>, <b>[{selected_k_store.replace('점','')} 가족모임]</b> 등 지역명과 목적성이 결합된 단어들입니다. 이 기본 세팅만으로도 잃어버렸던 월간 수천 건의 기본 검색 수요를 즉각적으로 회복할 수 있습니다. 당장 실행해 주십시오."
            elif s_vol > (median_vol * 1.5) and s_rate < (median_rate * 0.5):
                report_title = "[주의] 허수 타겟팅 (볼륨 위주)"
                report_body = f"해당 매장의 검색량 지표는 압도적으로 높게 나타나고 있으나, 이는 매장의 실제 매출이나 방문객 증가로 이어지지 않는 '거품(허수)' 데이터일 확률이 매우 높습니다. 매장을 방문하고 리뷰를 남긴 실제 고객들의 대화 속에서 점주님이 설정한 키워드가 전혀 언급되지 않고 있기 때문입니다. 이는 주로 '전국맛집', '데이트' 등 범위가 너무 넓은 전국구 키워드를 무리하게 세팅했을 때 발생하는 전형적인 타겟팅 실패 사례입니다.<br><br>이런 키워드는 노출이 되더라도 실제 클릭 및 방문 전환율이 현저히 떨어지며, 네이버 알고리즘 점수 하락의 원인이 됩니다. 지금 당장 헛된 검색량에 대한 미련을 버리십시오. 매장 반경 5km 이내의 진짜 동네 고객들이 모임 장소를 찾을 때 검색할 만한 <b>[구체적인 동네 지명 + 가족외식/생선구이]</b> 위주로 단어를 전면 교체하여 실속 있는 진성 고객을 유입시켜야 합니다."
            elif s_rate > (median_rate * 1.5) and s_vol < median_vol:
                report_title = "[우수] 로컬 최적화 (수요 확장 요망)"
                report_body = f"현재 <b>{selected_k_store}</b>의 키워드는 매장을 직접 방문한 고객들의 만족 포인트와 완벽하게 일치하고 있습니다. 이는 점주님이 매장의 핵심 강점을 매우 잘 파악하고 마케팅에 적용했다는 뜻으로, 고객 체감률(ROI) 측면에서 아주 훌륭한 성과를 보여줍니다.<br><br>하지만 유일한 약점은 현재 설정된 단어들의 전체 시장 파이(총 검색량) 자체가 타 매장 대비 다소 부족하다는 점입니다. 아무리 전환율이 좋아도, 모수가 적으면 폭발적인 매출 성장을 견인하기 어렵습니다. 현재 세팅된 키워드 중 성과가 가장 좋은 단어는 유지하시고, 1~2개 정도만 검색 수요가 조금 더 풍부한 <b>[인접한 대형 상권 지명 + 맛집]</b>이나 <b>[주차 편한 식당]</b> 같은 대중적 수요 키워드로 교체하여 유입량(파이)을 서서히 늘려가는 A/B 테스트를 적극 권장합니다."
            elif s_rate >= median_rate and s_vol >= median_vol:
                report_title = "[최우수] 마케팅 밸런스 완벽"
                report_body = f"축하드립니다. 현재 <b>{selected_k_store}</b>의 키워드 마케팅 성과는 브랜드 내 최상위권에 랭크되어 있는 완벽한 모범 사례입니다. 풍부한 검색 볼륨(수요)을 바탕으로 잠재 고객을 성공적으로 끌어모으고 있을 뿐만 아니라, 그 키워드가 실제 방문객들의 긍정적인 체감(리뷰)으로 100% 이어지고 있는 이상적인 '선순환 구조'를 달성하셨습니다.<br><br>매장이 내세운 약속(키워드)을 고객들이 현장에서 정확히 느끼고 칭찬한다는 것은 그만큼 현장 QSC 관리가 압도적이라는 증거이기도 합니다. 현재의 키워드 배열은 더 이상 수정할 필요가 없는 황금 밸런스 상태이므로 절대 건드리지 마십시오. 앞으로의 과제는 이 키워드들로 네이버 플레이스 1페이지(Top 5) 노출 순위를 방어하는 것입니다."
            else:
                report_title = "[개선 요망] 키워드 영점 조절 필요"
                report_body = f"현재 설정된 키워드의 마케팅 효율이 전반적으로 저조하여 전면적인 영점 조절이 시급합니다. 검색량 확보와 실제 고객 체감(리뷰 적중률) 두 가지 지표 모두 브랜드 평균치에 미치지 못하고 있습니다. 이는 점주님이 매장의 강점이라고 생각해서 내세운 단어와, 손님들이 실제로 방문해서 느끼는 매력 포인트 사이에 큰 시각 차이가 존재한다는 의미입니다.<br><br>위의 상세 성과 표를 참고하여, 검색량도 없으면서 리뷰 적중 횟수도 '0회'를 기록 중인 의미 없는 단어들은 이번 주 내로 미련 없이 모두 삭제하십시오. 빈자리에는 아래 AI가 분석해 낸 '실제 긍정 리뷰 최다 언급 강점' 데이터(손님들이 칭찬하는 진짜 이유)를 조합하여 새로운 타겟팅을 이식해야 죽어있던 마케팅 성과가 되살아날 것입니다."
                
            st.markdown(f"""
            <div class="ai-report-box">
                <div class="ai-report-title">{report_title}</div>
                <div class="ai-report-content">
                    {report_body}
                    <br><span class="suggested-keywords">실제 긍정 리뷰 최다 언급 강점: {suggested_text}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
                
        else:
            st.warning("검색된 매장이 없습니다.")
            
        st.divider()
        
        st.markdown("<b style='font-size: 16px;'>전체 가맹점 키워드 마케팅 성적표 원본 (해당 줄을 클릭하면 상단 진단 리포트가 해당 매장으로 변경됩니다)</b>", unsafe_allow_html=True)
        
        st.dataframe(
            sorted_raw_df.drop(columns=['적중률_num', '검색량_num', '미등록_플래그']), 
            use_container_width=True, 
            hide_index=True,
            key="roi_table",
            on_select="rerun",
            selection_mode="single-row"
        )

        st.divider()
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.success("로컬 마케팅 우수 매장 (적중률 Top 5)")
            top_df = roi_df.nlargest(5, '적중률_num')[['매장명', '키워드_적중률', '세팅된_키워드']]
            st.dataframe(top_df, use_container_width=True, hide_index=True)
            
        with col_b:
            st.error("컨설팅 시급 매장 (최악의 상태)")
            bad_mask = (roi_df['적중률_num'] == 0) | (roi_df['미등록_플래그'] == True)
            bad_df = roi_df[bad_mask].sort_values(
                by=['미등록_플래그', '적중률_num', '검색량_num'], 
                ascending=[False, True, True]
            ).head(5)[['매장명', '키워드_적중률', '세팅된_키워드']]
            st.dataframe(bad_df, use_container_width=True, hide_index=True)
        
    else:
        st.warning("키워드 ROI 분석 결과 파일이 서버에 없습니다. 백엔드에서 분석 봇을 먼저 실행하여 파일을 생성해 주십시오.")

st.markdown('</div>', unsafe_allow_html=True)