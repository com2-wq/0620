
import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import st_folium
from datetime import datetime

# 페이지 설정
st.set_page_config(page_title="전세계 지진 시각화 대시보드", layout="wide")
st.title("🌋 전세계 실시간 및 과거 지진 시각화 웹앱")
st.markdown("USGS(미 지질조사국) API 데이터를 기반으로 선택한 연도의 지진 데이터를 지도에 시각화합니다.")

# 1. USGS API로부터 데이터 로드하는 함수 (캐싱 적용으로 속도 향상)
@st.cache_data(ttl=3600)  # 1시간 동안 캐시 유지
def load_earthquake_data(year):
    start_time = f"{year}-01-01"
    end_time = f"{year}-12-31"
    
    # 규모 4.5 이상의 주요 지진만 가져오기 (데이터 양 조절 및 시각화 가독성 목적)
    url = f"https://earthquake.usgs.gov/fdsnws/event/1/query?format=geojson&starttime={start_time}&endtime={end_time}&minmagnitude=4.5"
    
    response = requests.get(url)
    if response.status_code != 200:
        st.error("USGS API로부터 데이터를 가져오는데 실패했습니다.")
        return pd.DataFrame()
        
    data = response.json()
    
    # GeoJSON 데이터를 판다스 데이터프레임으로 변환
    features = data.get("features", [])
    earthquakes = []
    
    for f in features:
        props = f["properties"]
        geom = f["geometry"]
        earthquakes.append({
            "place": props["place"],
            "mag": props["mag"],
            "time": pd.to_datetime(props["time"], unit='ms'),
            "latitude": geom["coordinates"][1],
            "longitude": geom["coordinates"][0],
            "depth": geom["coordinates"][2]
        })
        
    return pd.DataFrame(earthquakes)

# 2. 사이드바 - 연도 선택
current_year = datetime.now().year
selected_year = sidebar_year = st.sidebar.selectbox(
    "조회할 연도를 선택하세요",
    options=list(range(current_year, 2000, -1)),
    index=0
)

# 데이터 불러오기
with st.spinner(f"{selected_year}년 지진 데이터를 가져오는 중..."):
    df = load_earthquake_data(selected_year)

# 3. 메인 화면 구성
if not df.empty:
    # 통계 지표 표시
    col1, col2, col3 = st.columns(3)
    col1.metric("총 발생 건수 (M 4.5+)", f"{len(df)} 건")
    col2.metric("최대 규모", f"M {df['mag'].max():.1f}")
    col3.metric("평균 규모", f"M {df['mag'].mean():.1f}")
    
    st.subheader(f"📍 {selected_year}년 지ban 지도 시각화")
    
    # 4. Folium 지도 생성
    # 전세계를 조망할 수 있도록 중심점을 [0, 0]으로 설정
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB positron")
    
    # 지진 규모별 색상 지정 함수
    def get_color(magnitude):
        if magnitude >= 7.0:
            return "#FF0000"  # 빨강 (강진)
        elif magnitude >= 6.0:
            return "#FF6600"  # 주황
        elif magnitude >= 5.0:
            return "#FFAA00"  # 노랑
        else:
            return "#00AAFF"  # 파랑
            
    # 지도에 마커 추가
    for _, row in df.iterrows():
        # 지진 규모에 따라 반지름 크기 조절
        radius = row['mag'] * 2.5
        
        popup_text = f"""
        <b>위치:</b> {row['place']}<br>
        <b>규모:</b> M {row['mag']}<br>
        <b>깊이:</b> {row['depth']} km<br>
        <b>시간:</b> {row['time'].strftime('%Y-%m-%d %H:%M')}
        """
        
        folium.CircleMarker(
            location=[row['latitude'], row['longitude']],
            radius=radius,
            popup=folium.Popup(popup_text, max_width=300),
            color=get_color(row['mag']),
            fill=True,
            fill_color=get_color(row['mag']),
            fill_opacity=0.6,
            weight=1
        ).add_to(m)
        
    # 스트림릿에 지도 렌더링
    st_folium(m, width="100%", height=600, returned_objects=[])
    
    # 5. 데이터 테이블 표시
    st.subheader("📊 지진 데이터 상세보기")
    st.dataframe(df[['time', 'place', 'mag', 'depth', 'latitude', 'longitude']].sort_values(by='mag', ascending=False), use_container_width=True)

else:
    st.warning(f"{selected_year}년에 해당하는 지진 데이터가 없거나 불러오지 못했습니다.")
