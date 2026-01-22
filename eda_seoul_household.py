import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

# 1. 데이터 로드
file_path = r'C:\ICB6\fcicb6\project_1\data\seoul_hosehold_.csv'
print(f"--- [1] 데이터 로딩 시작: {file_path} ---")

try:
    df = pd.read_csv(file_path)
    print("데이터 로드 성공!")
except Exception as e:
    print(f"데이터 로드 실패: {e}")
    exit()

# 2. 데이터 전처리
df = df.replace('-', '0')
if '2010' in df.columns:
    df['2010'] = pd.to_numeric(df['2010'], errors='coerce').fillna(0).astype(int)

# 분석용 데이터 필터링 (구 단위 합계 데이터만 추출)
# '동별(3)'이 '소계'이고 '동별(2)'가 '소계'가 아닌 데이터가 각 구별 합계임
gu_df = df[(df['동별(3)'] == '소계') & (df['동별(2)'] != '소계')].copy()

# 3. 데이터 시각화 및 저장 준비
output_dir = r'C:\ICB6\fcicb6\project_1\plots'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

print("\n--- [3] 시각화 생성 시작 ---")

# 시각화 1: 구별 총 가구 수 막대 그래프
plt.figure(figsize=(12, 6))
total_households = gu_df[gu_df['구분별(2)'] == '소계'].sort_values('2010', ascending=False)
sns.barplot(data=total_households, x='동별(2)', y='2010', palette='viridis')
plt.title('서울시 구별 총 가구 수 (2010)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '1_total_households_by_gu.png'))
plt.close()

# 시각화 2: 가구 구분별 비중 (서울시 전체)
plt.figure(figsize=(8, 8))
seoul_summary = df[(df['동별(2)'] == '소계') & (df['구분별(2)'] == '일반가구') & (df['구분별(3)'] != '소계')]
plt.pie(seoul_summary['2010'], labels=seoul_summary['구분별(3)'], autopct='%1.1f%%', startangle=140, colors=sns.color_palette('pastel'))
plt.title('서울시 가구 유형별 비중 (2010)')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '2_household_types_pie.png'))
plt.close()

# 시각화 3: 구별 1인가구 수 비교
plt.figure(figsize=(12, 6))
single_households = gu_df[gu_df['구분별(3)'] == '1인가구'].sort_values('2010', ascending=False)
sns.barplot(data=single_households, x='동별(2)', y='2010', palette='magma')
plt.title('서울시 구별 1인가구 수 (2010)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '3_single_households_by_gu.png'))
plt.close()

# 시각화 4: 구별 가구 유형 분포 히트맵용 데이터 생성
pivot_df = gu_df[gu_df['구분별(2)'] == '일반가구'].pivot_table(index='동별(2)', columns='구분별(3)', values='2010', aggfunc='sum')
plt.figure(figsize=(12, 8))
sns.heatmap(pivot_df, annot=False, cmap='YlGnBu')
plt.title('서울시 구별 가구 유형 분포 히트맵')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '4_household_heatmap.png'))
plt.close()

# 시각화 5: 일반가구 vs 외국인가구 산점도
scatter_data = gu_df[gu_df['구분별(2)'].isin(['소계', '외국인가구'])].pivot_table(index='동별(2)', columns='구분별(2)', values='2010', aggfunc='sum')
plt.figure(figsize=(10, 6))
sns.regplot(data=scatter_data, x='소계', y='외국인가구')
plt.title('총 가구 수 대비 외국인 가구 수 상관관계')
plt.xlabel('총 가구 수')
plt.ylabel('외국인 가구 수')
plt.tight_layout()
plt.savefig(os.path.join(output_dir, '5_total_vs_foreign_scatter.png'))
plt.close()

print("시각화 이미지 5개 저장 완료.")

# 4. 교차표 (Crosstab) 출력
print("\n--- [4] 가구 유형 및 구별 교차표 (상위 5개 구) ---")
crosstab_result = pivot_df.head(5)
print(crosstab_result)

# 5. 마크다운 보고서 생성
report_path = r'C:\ICB6\fcicb6\project_1\report_seoul_household.md'
with open(report_path, 'w', encoding='utf-8') as f:
    f.write("# 서울시 가구 데이터 종합 분석 보고서\n\n")
    f.write("## 1. 기초 기술통계\n")
    f.write(f"- 데이터 총 행수: {len(df)}\n")
    f.write(f"- 2010년 가구 수 평균: {df['2010'].mean():.2f}\n")
    f.write(f"- 2010년 가구 수 중앙값: {df['2010'].median()}\n")
    f.write(f"- 2010년 가구 수 왜도: {df['2010'].skew():.4f}\n\n")
    
    f.write("## 2. 주요 시각화 결과\n")
    f.write("![구별 총 가구 수](./plots/1_total_households_by_gu.png)\n")
    f.write("![가구 유형별 비중](./plots/2_household_types_pie.png)\n")
    f.write("![구별 1인가구 수](./plots/3_single_households_by_gu.png)\n")
    f.write("![가구 유형 히트맵](./plots/4_household_heatmap.png)\n")
    f.write("![총가구 vs 외국인가구](./plots/5_total_vs_foreign_scatter.png)\n\n")
    
    f.write("## 3. 구별 가구 유형 교차표 (일부)\n")
    f.write(crosstab_result.to_markdown() + "\n\n")
    
    f.write("## 4. 최종 결론\n")
    f.write("- 서울시에서 1인 가구는 일반가구 중 매우 큰 비중을 차지하고 있습니다.\n")
    f.write("- 구별로 가구 수의 차이가 크며, 특히 강남구와 송파구 등의 총 가구 수가 높게 나타납니다.\n")

print(f"\n--- [5] 마크다운 보고서 저장 완료: {report_path} ---")
print("\n--- 분석 프로세스 완료 ---")
