import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="프랜차이즈 리뷰 분석 대시보드", page_icon="📊", layout="wide")

@st.cache_data
def load_data():
    # 과장님이 깃허브에 올리신 엑셀 파일명과 완벽히 일치시켰습니다.
    filename = "가맹점_리뷰수집결과_20260325.csv"
    
    if os.path.exists(filename):
        df = pd.read_csv(filename)
    else:
        st.warning("데이터 파일이 없어 샘플을 표시합니다.")
        df = pd.DataFrame({"매장명": ["샘플"], "작성일": ["2026-03-25"], "리뷰내용": ["내용"], "감정분석": ["긍정"]})
    return df

df = load_data()

st.title("📊 일간 가맹점 네이버 리뷰 모니터링")
st.markdown("매일 오전 9시 수집 완료 | **본사 가맹관리팀 및 점주 공유용**")

st.sidebar.header("🔍 검색 필터")
selected_store = st.sidebar.selectbox("매장 선택", ["전체 가맹점"] + list(df['매장명'].unique()))

if selected_store != "전체 가맹점":
    filtered_df = df[df['매장명'] == selected_store]
else:
    filtered_df = df

st.subheader(f"💡 요약 지표 ({selected_store})")
col1, col2, col3 = st.columns(3)

total_reviews = len(filtered_df)
positive_reviews = len(filtered_df[filtered_df['감정분석'] == '긍정']) if '감정분석' in filtered_df.columns else 0
negative_reviews = total_reviews - positive_reviews

with col1:
    st.metric(label="오늘 신규 수집된 리뷰", value=f"{total_reviews}건")
with col2:
    st.metric(label="긍정 리뷰", value=f"{positive_reviews}건", delta="고객 칭찬")
with col3:
    st.metric(label="부정/주의 리뷰 (CS 필요)", value=f"{negative_reviews}건", delta="- 즉각 대응 필요", delta_color="inverse")

st.divider()

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("📋 신규 리뷰 상세 리스트")
    display_df = filtered_df.sort_values(by='작성일', ascending=False) if '작성일' in filtered_df.columns else filtered_df
    st.dataframe(display_df, width='stretch')

with col_chart2:
    st.subheader("Pie 리뷰 감정 비율")
    if '감정분석' in filtered_df.columns:
        sentiment_counts = filtered_df['감정분석'].value_counts().reset_index()
        sentiment_counts.columns = ['감정', '비율']
        fig2 = px.pie(sentiment_counts, values='비율', names='감정', color='감정', 
                      color_discrete_map={'긍정':'#00CC96', '부정':'#EF553B', '중립':'#636EFA'})
        st.plotly_chart(fig2, width='stretch')
