import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 페이지 설정
st.set_page_config(page_title="AhnLab Pulse Survey Analyzer", layout="wide")

# 2. 데이터 전처리 및 점수화 로직
def preprocess_data(df):
    # 1on1 점수 매핑
    one2one_map = {
        "주 1회 이상": 5, "월 2~3회 수준": 4, "월 1회 수준": 3,
        "분기 1회 수준": 2, "반기 1회 수준": 1, "연 1회 이하": 0
    }
    # 호칭제 점수 매핑
    title_map = {
        "님 호칭만 사용": 5, "직위와 님 호칭 혼용": 3, "기존 직위 위주 사용": 1
    }
    
    # 시간 데이터 변환 (시작 시간 기준)
    df['시작 시간'] = pd.to_datetime(df['시작 시간'])
    df['시행월'] = df['시작 시간'].dt.strftime('%Y-%m')
    
    # 점수 컬럼 생성 (이미지 속 컬럼명 반영)
    df['1on1_Score'] = df['현재 직속 상위 리더와의 1on1은 어느 정도 수행되고 있나요?'].map(one2one_map)
    df['Title_Score'] = df['현재 조직 내 호칭제도(님 문화) 정착 수준은 어느 정도인가요?'].map(title_map)
    
    return df

# 3. UI 구성
st.title("📊 Pulse Survey 조직 문화 분석")
st.markdown("안랩 구성원들의 목소리를 통해 부문별/시기별 조직 건강도를 진단합니다.")

# 파일 업로드
uploaded_file = st.file_uploader("Pulse Survey 결과 파일(Excel/CSV)을 업로드하세요.", type=["xlsx", "csv"])

if uploaded_file:
    # 데이터 로드
    df_raw = pd.read_excel(uploaded_file) if uploaded_file.name.endswith('xlsx') else pd.read_csv(uploaded_file)
    df = preprocess_data(df_raw)
    
    # 상단 요약 지표 (Metrics)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("총 응답자 수", f"{len(df)}명")
    c2.metric("평균 1on1 빈도", f"{df['1on1_Score'].mean():.2f} / 5.0")
    c3.metric("호칭제 정착도", f"{df['Title_Score'].mean():.2f} / 5.0")
    c4.metric("응답 부서 수", f"{df['소속 부문을 선택해주세요'].nunique()}개")

    # 분석 탭
    tab1, tab2, tab3 = st.tabs(["🏢 부문별 비교", "📈 시기별 트렌드", "💡 인사이트 리포트"])

    with tab1:
        st.subheader("부문별 조직 문화 지수")
        dept_avg = df.groupby('소속 부문을 선택해주세요')[['1on1_Score', 'Title_Score']].mean().reset_index()
        
        # 가로 바 차트
        fig_dept = px.bar(dept_avg, x=['1on1_Score', 'Title_Score'], y='소속 부문을 선택해주세요',
                          barmode='group', title="부문별 항목 평균 점수",
                          color_discrete_sequence=['#007bff', '#28a745'])
        st.plotly_chart(fig_dept, use_container_width=True)

    with tab2:
        st.subheader("시기별 문화 변화 추이")
        trend_df = df.groupby('시행월')[['1on1_Score', 'Title_Score']].mean().reset_index()
        
        fig_trend = px.line(trend_df, x='시행월', y=['1on1_Score', 'Title_Score'],
                            markers=True, title="월별 만족도 트렌드")
        st.plotly_chart(fig_trend, use_container_width=True)

    with tab3:
        st.subheader("AI 기반 조직 진단 의견")
        
        # 간단한 로직 기반 인사이트 생성
        lowest_dept = dept_avg.loc[dept_avg['1on1_Score'].idxmin(), '소속 부문을 선택해주세요']
        highest_title = dept_avg.loc[dept_avg['Title_Score'].idxmax(), '소속 부문을 선택해주세요']
        
        st.info(f"""
        * **커뮤니케이션 리스크:** `{lowest_dept}` 부문의 1on1 점수가 가장 낮게 측정되었습니다. 해당 부문 리더 대상의 코칭 세션 검토가 필요합니다.
        * **문화 정착 우수 사례:** `{highest_title}` 부문은 '님' 호칭 문화가 가장 안정적으로 정착되어 있습니다. 해당 부문의 사례를 전파할 필요가 있습니다.
        * **종합 제언:** 전월 대비 1on1 빈도가 낮아지는 추세라면, 분기별 성과 리뷰 시즌과 겹치는지 확인하여 구성원 부담을 줄여주는 가이드가 필요합니다.
        """)

else:
    st.warning("데이터 파일을 업로드하면 상세 분석이 시작됩니다.")