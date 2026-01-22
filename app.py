import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
from dotenv import load_dotenv

# 환경 변수 로드 (.env 파일이 있으면 로드)
load_dotenv()

# 보안 정보 로드 (예시: API 연동 시 사용)
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# 페이지 설정
st.set_page_config(page_title="서울시 가구 데이터 대시보드", layout="wide", page_icon="🏠")

# 1. 데이터 로드 및 전처리
@st.cache_data
def load_data():
    df = pd.read_csv("seoul_hosehold_.csv")
    df = df.replace('-', '0')
    if '2010' in df.columns:
        df['2010'] = pd.to_numeric(df['2010'], errors='coerce').fillna(0).astype(int)
    return df

df = load_data()

# 사이드바 설정
st.sidebar.header("🔍 데이터 필터링")
all_gus = sorted(df['동별(2)'].unique())
if '소계' in all_gus: all_gus.remove('소계')

selected_gus = st.sidebar.multiselect("분석할 구 선택", all_gus, default=all_gus[:5])

# 메인 타이틀
st.title("🏙️ 서울시 가구 데이터 기초 EDA 대시보드 (2010)")
st.markdown("---")

# 탭 구성
tab1, tab2, tab3 = st.tabs(["🏠 개요", "📊 통계 분석", "📈 시각화"])

# 데이터 필터링
gu_df_all = df[(df['동별(3)'] == '소계') & (df['동별(2)'] != '소계')]
filtered_gu_df = gu_df_all[gu_df_all['동별(2)'].isin(selected_gus)]

# --- Tab 1: 개요 ---
with tab1:
    st.header("📌 데이터 요약 및 핵심 지표")
    
    # 핵심 지표 (Metrics)
    seoul_total_val = df[(df['동별(2)'] == '소계') & (df['구분별(2)'] == '소계')]['2010'].values[0]
    seoul_single_val = df[(df['동별(2)'] == '소계') & (df['구분별(3)'] == '1인가구')]['2010'].values[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("서울시 총 가구 수", f"{seoul_total_val:,}")
    col2.metric("서울시 총 1인 가구 수", f"{seoul_single_val:,}")
    col3.metric("1인 가구 비중", f"{(seoul_single_val/seoul_total_val)*100:.2f}%")
    
    st.subheader("📄 데이터 샘플링 (상위 50행)")
    st.dataframe(df.head(50))
    
    st.subheader("📝 데이터셋 정보")
    buffer = pd.DataFrame({
        "컬럼명": df.columns,
        "데이터 타입": [str(d) for d in df.dtypes.values],
        "결측치 수": df.isnull().sum().values
    })
    st.table(buffer)

# --- Tab 2: 통계 분석 ---
with tab2:
    st.header("📊 기초 EDA 및 기술통계")
    
    # 표 1: 구별 기초 통계 요약표
    st.subheader("1. 선택된 구의 가구 수 통계")
    stats_df = filtered_gu_df.groupby('동별(2)')['2010'].describe().reset_index()
    st.dataframe(stats_df)
    
    # 표 2: 가구 유형별 교차표 (Crosstab)
    st.subheader("2. 가구 유형 및 구별 교차표")
    pivot_df = filtered_gu_df[filtered_gu_df['구분별(2)'] == '일반가구'].pivot_table(
        index='동별(2)', columns='구분별(3)', values='2010', aggfunc='sum'
    )
    st.dataframe(pivot_df)
    
    # 표 3: 1인가구 비중 상위 10개 구
    st.subheader("3. 1인가구 수가 가장 많은 구 TOP 10")
    top_single = gu_df_all[gu_df_all['구분별(3)'] == '1인가구'].sort_values('2010', ascending=False).head(10)
    st.table(top_single[['동별(2)', '2010']])
    
    # 표 4: 외국인가구 수 분포
    st.subheader("4. 외국인가구 수 분포 TOP 10")
    top_foreign = gu_df_all[gu_df_all['구분별(2)'].isin(['외국인가구'])].sort_values('2010', ascending=False).head(10)
    st.dataframe(top_foreign[['동별(2)', '2010']])
    
    # 표 5: 가구 구분별 서울시 전체 합계
    st.subheader("5. 가구 구분별 서울시 전체 합계")
    seoul_summary = df[(df['동별(2)'] == '소계') & (df['구분별(3)'] != '소계')]
    st.table(seoul_summary[['구분별(2)', '구분별(3)', '2010']])

# --- Tab 3: 시각화 ---
with tab3:
    st.header("📈 Plotly 기반 인터랙티브 시각화")
    
    # 그래프 1: 구별 총 가구 수 막대 그래프
    st.subheader("1. 선택된 구별 총 가구 수")
    total_bar_data = filtered_gu_df[filtered_gu_df['구분별(2)'] == '소계'].sort_values('2010', ascending=False)
    fig1 = px.bar(total_bar_data, x='동별(2)', y='2010', color='동별(2)', title="구별 총 가구 수 비교")
    st.plotly_chart(fig1, use_container_width=True)
    
    # 그래프 2: 가구 유형별 비중 (Pie)
    st.subheader("2. 가구 유형별 비중 (전체)")
    pie_data = df[(df['동별(2)'] == '소계') & (df['구분별(2)'] == '일반가구') & (df['구분별(3)'] != '소계')]
    fig2 = px.pie(pie_data, values='2010', names='구분별(3)', title="서울시 일반가구 세부 유형 비중")
    st.plotly_chart(fig2, use_container_width=True)
    
    # 그래프 3: 구별 가구 유형 TreeMap
    st.subheader("3. 구별 가구 구조 상세 (TreeMap)")
    tree_data = filtered_gu_df[filtered_gu_df['구분별(2)'] == '일반가구']
    fig3 = px.treemap(tree_data, path=['동별(2)', '구분별(3)'], values='2010', color='2010', color_continuous_scale='RdBu')
    st.plotly_chart(fig3, use_container_width=True)
    
    # 그래프 4: 총 가구 대비 외국인 가구 상관관계 (Scatter)
    st.subheader("4. 총 가구 수 vs 외국인 가구 수 상관관계")
    scatter_data = gu_df_all[gu_df_all['구분별(2)'].isin(['소계', '외국인가구'])].pivot_table(
        index='동별(2)', columns='구분별(2)', values='2010', aggfunc='sum'
    ).reset_index()
    fig4 = px.scatter(scatter_data, x='소계', y='외국인가구', text='동별(2)', size='소계', color='외국인가구', title="가구 수 규모와 외국인 가구 수의 관계")
    st.plotly_chart(fig4, use_container_width=True)
    
    # 그래프 5: 구별 가구 수 분포 (Box Plot)
    st.subheader("5. 구별 가구 수 분포 분석 (Box Plot)")
    fig5 = px.box(filtered_gu_df, x='동별(2)', y='2010', color='동별(2)', points="all", title="구별 가구 수 범위 및 분포")
    st.plotly_chart(fig5, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Data Source: 서울시 가구 통계 (2010)")


