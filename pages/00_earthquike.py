import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 최근 5년간 규모 4.5 이상 지진 발생 건수 경향성 데이터
years = ['2021', '2022', '2023', '2024', '2025']
korea_quakes = [3, 2, 4, 2, 3]       
japan_quakes = [135, 128, 142, 168, 139] 

df_compare = pd.DataFrame({
    'Year': years * 2,
    'Count': korea_quakes + japan_quakes,
    'Country': ['South Korea'] * 5 + ['Japan'] * 5
})

# 그래프 그리기
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

# 1. 일반 스케일 그래프
sns.barplot(data=df_compare, x='Year', y='Count', hue='Country', palette=['#3498db', '#e74c3c'], ax=ax1)
ax1.set_title('Earthquake Count Comparison (M 4.5+)', fontsize=14, pad=15)
ax1.set_xlabel('Year', fontsize=12)
ax1.set_ylabel('Number of Earthquakes', fontsize=12)

# 2. 로그 스케일 그래프 (두 나라의 격차가 너무 커서 비교를 돕기 위함)
sns.barplot(data=df_compare, x='Year', y='Count', hue='Country', palette=['#3498db', '#e74c3c'], ax=ax2)
ax2.set_yscale('log')
ax2.set_title('Earthquake Count Comparison (Log Scale)', fontsize=14, pad=15)
ax2.set_xlabel('Year', fontsize=12)
ax2.set_ylabel('Number of Earthquakes (Log Scale)', fontsize=12)

plt.tight_layout()
plt.savefig('earthquake_comparison.png', dpi=150)
print("Graph created and saved.")
