import pandas as pd
import numpy as np
import datetime
import joblib
from keras.models import load_model
from urllib.parse import quote
import branca
from geopy.geocoders import Nominatim
import ssl
from streamlit_option_menu import option_menu
import plotly.express as px

import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
from branca.colormap import linear
import branca.colormap as cmp
import geopandas
import altair as alt
from datetime import datetime
from folium.plugins import MarkerCluster

# -------------------------------------------------------------데이터 불러오기-------------------------------------------------------------
chart_data = pd.read_csv('https://raw.githubusercontent.com/huhshin/streamlit/master/data_sales.csv')
medal = pd.read_csv('https://raw.githubusercontent.com/huhshin/streamlit/master/data_medal.csv')

geo_json_data = requests.get(
    'https://raw.githubusercontent.com/southkorea/seoul-maps/master/kostat/2013/json/seoul_municipalities_geo_simple.json'
).json()

 # GeoJSON 데이터 중에서 구에 해당하는 부분만 추출
gangnam_geo_json = {
    "type": "FeatureCollection",
    "features": [feature for feature in geo_json_data["features"] if feature["properties"]["name"] == "강남구"]
}
songpa_gu_json = {
    "type": "FeatureCollection",
    "features": [feature for feature in geo_json_data["features"] if feature["properties"]["name"] == "송파구"]
}


# CCTV geojson 구 별 분리
gdf = geopandas.read_file("https://raw.githubusercontent.com/rlawnstlr412/BigProject_10/main/cctv.geojson")

gangnam_gdf = gdf[gdf['name'].str.contains("강남구")]
gangnam2_gdf = gdf[gdf['name'].str.contains("강남구2")]
gangnam3_gdf = gdf[gdf['name'].str.contains("강남구3")]
gangnam4_gdf = gdf[gdf['name'].str.contains("강남구4")]
songpa_gdf = gdf[gdf['name'].str.contains("송파구")]
songpa1_gdf = gdf[gdf['name'].str.contains("송파구1")]
songpa2_gdf = gdf[gdf['name'].str.contains("송파구2")]
songpa3_gdf = gdf[gdf['name'].str.contains("송파구3")]
# cctv 정보

cctv_info = pd.read_csv('https://raw.githubusercontent.com/rlawnstlr412/BigProject_10/main/cctv_info.csv', encoding='cp949')
cctv_info.set_index(cctv_info.columns[0], inplace=True)
cctv_info.index.name=None
songpa_cctv = cctv_info.head()
songpa1_cctv = cctv_info.head(2)
gangnam_cctv = cctv_info.tail(4)
gangnam1_cctv = cctv_info.tail(2)

#시각화 데이터
data_vis = pd.read_csv('https://raw.githubusercontent.com/rlawnstlr412/BigProject_10/main/data_vis.csv', encoding='cp949')
# -------------------------------------------------------------지도 불러오기 함수-------------------------------------------------------------
def show_map(lat, lon, zoom, data):

    df = pd.read_csv("https://raw.githubusercontent.com/rlawnstlr412/BigProject_10/main/seoul_population.csv")

    #지도 포화도에 따른 색 표현
    linear = cmp.LinearColormap(
    [ 'green', 'yellow', 'red'],
    vmin = df.total.min(),
    vmax = df.total.max(),
    caption="population"

    )

    df_dict = df.set_index("district")["total"]

    m = folium.Map(location=[lat, lon], zoom_start=zoom)


    folium.GeoJson(data,
                   name="population",
                   style_function=lambda feature: {
                       "fillColor": linear(df_dict[feature["properties"]["name"]]),
                        "color": "black",
                        "weight": 2,
                        "dashArray": "5, 5",
                       #지도위 색레이어 투명도
                        "fillOpacity":0.5,
                   },

                   highlight_function=lambda feature: {
                        "fillColor": (
                        "#ffc800"
                    ),
        },
    

                   zoom_on_click=True).add_to(m)


    folium.LayerControl().add_to(m)

    linear.add_to(m)
    st_data = st_folium(m, width=1200, height=500)


# -------------------------------------------------------------맵,마커 불러오기 함수2-------------------------------------------------------------

def show_map2(lat, lon, zoom, data, data2, wid):

    df = pd.read_csv("https://raw.githubusercontent.com/rlawnstlr412/BigProject_10/main/seoul_population.csv")


    #지도 포화도에 따른 색 표현
    linear = cmp.LinearColormap(
    [ 'green', 'yellow', 'red'],
    vmin = df.total.min(),
    vmax = df.total.max(),
    caption="population"

    )

    df_dict = df.set_index("district")["total"]

    m = folium.Map(location=[lat, lon], zoom_start=zoom)


    folium.GeoJson(data,
                   name="population",
                   style_function=lambda feature: {
                       "fillColor": linear(df_dict[feature["properties"]["name"]]),
                        "color": "black",
                        "weight": 2,
                        "dashArray": "5, 5",
                       #지도위 색레이어 투명도
                        "fillOpacity":0.5,
                   },

                   highlight_function=lambda feature: {
                        "fillColor": (
                        "#ffc800"
                    ),
        },

    
                   zoom_on_click=True).add_to(m)

    #cctv 위치 마커 맵에 표시
    folium.GeoJson(
        data2,
        name = "cctv",
        marker=folium.Marker(icon=folium.Icon(icon="video-camera", prefix='fa', color='green')),
        tooltip=folium.GeoJsonTooltip(fields=["name", "detected"]),
        popup=folium.GeoJsonPopup(fields=["name", "detected"]),


    ).add_to(m)

    folium.LayerControl().add_to(m)

    linear.add_to(m)
    st_data = st_folium(m, width=wid, height=450)
# -------------------------------------------------------------맵,마커 불러오기 함수3-------------------------------------------------------------

def show_map3(lat, lon, zoom, data, data2, data3,data4, wid):

    df = pd.read_csv("https://raw.githubusercontent.com/rlawnstlr412/BigProject_10/main/seoul_population.csv")


    #지도 포화도에 따른 색 표현
    linear = cmp.LinearColormap(
    [ 'green', 'yellow', 'red'],
    vmin = df.total.min(),
    vmax = df.total.max(),
    caption="population"

    )

    df_dict = df.set_index("district")["total"]

    m = folium.Map(location=[lat, lon], zoom_start=zoom)


    folium.GeoJson(data,
                   name="population",
                   style_function=lambda feature: {
                       "fillColor": linear(df_dict[feature["properties"]["name"]]),
                        "color": "black",
                        "weight": 2,
                        "dashArray": "5, 5",
                       #지도위 색레이어 투명도
                        "fillOpacity":0.5,
                   },

                   highlight_function=lambda feature: {
                        "fillColor": (
                        "#ffc800"
                    ),
        },

    
                   zoom_on_click=True).add_to(m)

    #cctv 위치 마커 맵에 표시
    folium.GeoJson(
        data2,
        name = "cctv",
        marker=folium.Marker(icon=folium.Icon(icon="video-camera", prefix='fa', color='orange')),
        tooltip=folium.GeoJsonTooltip(fields=["name", "detected"]),
        popup=folium.GeoJsonPopup(fields=["name", "detected"]),


    ).add_to(m)
    
    #cctv 위치 마커 맵에 표시
    folium.GeoJson(
        data3,
        name = "cctv",
        marker=folium.Marker(icon=folium.Icon(icon="video-camera", prefix='fa', color='yellow')),
        tooltip=folium.GeoJsonTooltip(fields=["name", "detected"]),
        popup=folium.GeoJsonPopup(fields=["name", "detected"]),
    ).add_to(m)
    #cctv 위치 마커 맵에 표시
    folium.GeoJson(
        data4,
        name = "cctv",
        marker=folium.Marker(icon=folium.Icon(icon="video-camera", prefix='fa', color='green')),
        tooltip=folium.GeoJsonTooltip(fields=["name", "detected"]),
        popup=folium.GeoJsonPopup(fields=["name", "detected"]),

    ).add_to(m)
    folium.LayerControl().add_to(m)

    linear.add_to(m)
    st_data = st_folium(m, width=wid, height=450)
# -------------------------------------------------------------홈페이지 탭 아이콘, 홈페이지 명 설정-------------------------------------------------------------
st.set_page_config(
        page_title= 'test',
        page_icon=":smile:",
        layout = "wide",
        initial_sidebar_state="expanded")

# -------------------------------------------------------------관제, 경로안내, 데이터 탭 내용 설정-------------------------------------------------------------
    
# -------------------------------------------------------------전체 설정-------------------------------------------------------------
def page4():
   # -------------------------------------------------------------전체 상단 탭 설정-------------------------------------------------------------
    
        
    st.markdown('<div style="text-align: center;"><h1>전체</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "데이터"],
    icons = ["camera-video-fill", "cone-striped", "clipboard2-data-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles = {"container" : {"padding": "0!important", "background-color":"#D1D8E4"},
             "icon": {"color": "red", "font-size": "30px"}, # 아이콘 크기
            "nav-link": {"font-size" : "30px", # 글자 크기
                        "text-align" : "center", # 정렬
                        "margin" : "1px",  # 칸 사이 여백
                        "--hover-color": "#eee" #마우스 갖다댈 때 색,
                        },
                        "nav-link-selected": {"background-color": "#09203E"},
             },
)
    st.markdown('#')
# -------------------------------------------------------------전체 관제 설정-------------------------------------------------------------
    if selected == "관제":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
        col1, col5 = st.columns([0.7, 0.3])
        with col1:
            st.header('서울특별시')
            show_map(37.56,127,11,geo_json_data)
        
        with col5:
            st.header('지역 별 신고') 
            fig = px.pie(medal, names = "nation", values = "gold", hole=.5 )
            fig.update_traces(textposition='inside', textinfo = 'percent+label+value')
            fig.update_layout(font = dict(size = 12))
            fig.update(layout_showlegend=False)  # 범례 표시 제거
            fig.update_layout(height=500, width=500)
            st.plotly_chart(fig)
            
        col2, col3, col4 = st.columns([0.3, 0.3, 0.3])

        with col2:
            st.header('1월 누적 견인 수') 
            col2.metric("", "7회", "-2회")
        with col3:
            st.header('날짜별') 
            col3.metric("", "115일", "20일")
        with col4:
            st.header('주간')
            col4.metric("", "12대", "-1대")
        
# -------------------------------------------------------------전체 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
       
        show_map2(37.56,127,11,geo_json_data, gdf,1800)
        
        
        # Display the DataFrame using st.dataframe
        st.dataframe(cctv_info, width=1800)
        
# -------------------------------------------------------------전체 데이터 설정-------------------------------------------------------------

# -------------------------------------------------------------전체 견인 통계-------------------------------------------------------------
    line_df = pd.DataFrame({'months': pd.date_range('2023-01-01', periods=12, freq='M'),
                           '총 건수': [7552, 8080, 7707, 7718, 13895, 14423, 14375, 11898, 12326, 12211, 12739, 12927]
                           })
    if selected == "데이터":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
        with st.sidebar:
            st.header('날짜 구간을 선택하세요')
            slider_data = st.slider('', min_value=datetime(2023, 1, 1), max_value=datetime(2023, 2, 28), value=(datetime(2023, 1, 1), datetime(2023, 12, 31)), format='YYYY-MM-DD')
            day_list_df = line_df[(line_df['months'] >= slider_data[0]) & (line_df['months'] <= slider_data[1])]
            
            st.header('단위를 선택하세요')
            genre = st.radio('보고싶은 기간의 단위를 선택하세요', ('월별', '주별', '일별'))

            if genre == '월별':
                st.write('월별 데이터 알려드리겠습니다.')
            elif genre == '주별':
                st.write('주별 데이터 알려드리겠습니다.')
            else:
                st.write('일별 데이터 알려드리겠습니다.')
            

        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.header('전체 견인 통계')

            group_day_time = line_df.groupby(by=['months'], as_index=False)["총 건수"].mean()
            group_day_time = group_day_time.rename(columns={"총 건수": '총 건수'})
            group_day_time['months'] = pd.to_datetime(group_day_time['months'])
            filtered_data_day = group_day_time[group_day_time['months'].isin(day_list_df['months'])]

            # Altair를 사용하여 그래프 그리기
            line = alt.Chart(filtered_data_day).mark_line(point=True).encode(
                x='months:T',
                y='총 건수:Q',
                color=alt.value("#09203E"),  # 선의 색상 지정
                tooltip=['months:T', '총 건수:Q'],  # 툴팁에 표시될 정보 지정
            ).properties(
                width=1000
            )

            # 라인차트 각 점위에 보여줄 텍스트 생성, dy로 텍스트의 위치 조정
            line_text = line.mark_text(align="center", baseline="bottom", dy=-10).encode(
                text=alt.Text("총 건수:Q", format=',.0f')  # 텍스트로 표시될 정보 지정
            )

            # 라인차트와 라인 텍스트 합치기
            line_concated = line + line_text
            st.altair_chart(line_concated, use_container_width=True)
        
# -------------------------------------------------------------TOP3통계-------------------------------------------------------------        
        with col2:
            st.header('견인 TOP 3 구') 
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C'],
                ' ': [55, 50, 43]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)

# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col3, col4 = st.columns([0.6, 0.4])
        with col3:
            st.header('PM 브랜드별 견인 건 수') 
            #바 형태 차트 만들기
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
                ' ': [28, 55, 43, 91, 81, 53, 19, 87, 52]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)
            
        with col4:
            st.header('위반사항별 견인 건 수')
            #도넛 차트 만들기
            donut_df = pd.DataFrame({
                "category": [1, 2, 3, 4, 5, 6],
                "value": [4, 6, 10, 3, 7, 8]
            })

            donut = alt.Chart(donut_df).mark_arc(innerRadius=50).encode(
                theta="value",
                color="category:N",
            )

            st.altair_chart(donut, use_container_width=True)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col5, col6 = st.columns([0.6, 0.4])
        with col5:
            st.header('견인 업체별 견인 건 수') 
            #바 형태 차트 만들기
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
                ' ': [33, 55, 11, 33, 81, 22, 19, 65, 52]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)
            
        with col6:
            st.header('부정견인 단속 현황') 
            pm_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C'],
                '구': ['강남구', '송파구', '송파구'],
                '위반사항': ['지하철 출입구', '버스정류장', '횡단보도'],
                '조치사항': ['견인 중', '견인 완료', '미처리']
            })
            st.markdown('#')
            st.dataframe(pm_df, width=700, height=180)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col7, col8 = st.columns([0.6, 0.4])
        with col7:
            st.header('PM 주차장 현황')
            # tiles 에서 맵 타일 바꾸기
            m = folium.Map(location=[37.56,127.00], zoom_start=11, tiles='cartodbpositron')

            folium.GeoJson(geo_json_data,
                           name="population",
                           style_function=lambda feature: { 
                                "color": "grey",
                                "weight": 2,
                                "dashArray": "5, 5",
                                "fillOpacity":0.2,
                           },

                           highlight_function=lambda feature: {
                                "fillColor": (
                                "#09203E"
                            ),
                            },


                           zoom_on_click=True).add_to(m)

            folium.LayerControl().add_to(m)


            st_data = st_folium(m, width=1200, height=450)
            
        with col8:
            st.subheader('필요 주차장 수')
            st.slider('',  min_value=0, max_value=10, value=10, step=1, label_visibility="collapsed")
            st.markdown('#')
            st.subheader('필요 지역 우선순위')
            pmm_df = pd.DataFrame({
                '구': ['강남구', '송파구', '송파구'],
                '동': ['역삼동','가락동', '방이동']
            })
            st.markdown('#')
            st.dataframe(pmm_df, width=700, height=180)
def page1():
    # -------------------------------------------------------------상단 탭 설정-------------------------------------------------------------
    
        
    st.markdown('<div style="text-align: center;"><h1>강남구</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "데이터"],
    icons = ["camera-video-fill", "cone-striped", "clipboard2-data-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles = {"container" : {"padding": "0!important", "background-color":"#D1D8E4"},
             "icon": {"color": "red", "font-size": "30px"}, # 아이콘 크기
            "nav-link": {"font-size" : "30px", # 글자 크기
                        "text-align" : "center", # 정렬
                        "margin" : "1px",  # 칸 사이 여백
                        "--hover-color": "#eee" #마우스 갖다댈 때 색,
                        },
                        "nav-link-selected": {"background-color": "#09203E"},
             },
)

# -------------------------------------------------------------강남구 관제 설정-------------------------------------------------------------
    if selected == "관제":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        col3, col4 = st.columns([0.7, 0.3])
        with col3:
            st.header('지도')
            show_map2(37.496,127.07,12,gangnam_geo_json, gangnam_gdf, 1200)
        with col4:
            st.header('CCTV')
            st.video('Desktop/BP/subway_exit.mp4')
            
        st.dataframe(gangnam_cctv, width=1800)      
        
#         col1, col2 = st.columns([0.01, 0.99])
#         with col1:
#             st.markdown('#') # 😄
#             one = st.checkbox('1')
#             two = st.checkbox('2')
#             three = st.checkbox('3')
#             four = st.checkbox('4')
            
#         if one:
#             seoul_logo = {"image_url" : "Desktop/BP/seoul_img.png"}
#             st.image(seoul_logo["image_url"])
#         elif two:
#             st.write(df)

#         with col2:
#             st.dataframe(gangnam_cctv, width=1800)

# -------------------------------------------------------------강남구 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
        show_map3(37.496,127.07,12,gangnam_geo_json,gangnam3_gdf, gangnam4_gdf, gangnam2_gdf, 1800)
        col1, col2 = st.columns([0.2, 0.8])

        with col1:
            st.subheader('(주)바로견인')
            st.write('전화번호 : 010-0000-0000')
            st.write('업체주소 : 서울시 강남구 OO동')
            st.write('대표명 : 김빅프')

        with col2:
            st.dataframe(gangnam1_cctv, width=1800)

# -------------------------------------------------------------강남구 데이터 설정-------------------------------------------------------------
# -------------------------------------------------------------전체 견인 통계-------------------------------------------------------------
    line_df = pd.DataFrame({'months': pd.date_range('2023-01-01', periods=12, freq='M'),
                           '총 건수': [7552, 8080, 7707, 7718, 13895, 14423, 14375, 11898, 12326, 12211, 12739, 12927]
                           })
    if selected == "데이터":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
        with st.sidebar:
            st.header('날짜 구간을 선택하세요')
            slider_data = st.slider('', min_value=datetime(2023, 1, 1), max_value=datetime(2023, 2, 28), value=(datetime(2023, 1, 1), datetime(2023, 12, 31)), format='YYYY-MM-DD')
            day_list_df = line_df[(line_df['months'] >= slider_data[0]) & (line_df['months'] <= slider_data[1])]
            
            st.header('단위를 선택하세요')
            genre = st.radio('보고싶은 기간의 단위를 선택하세요', ('월별', '주별', '일별'))

            if genre == '월별':
                st.write('월별 데이터 알려드리겠습니다.')
            elif genre == '주별':
                st.write('주별 데이터 알려드리겠습니다.')
            else:
                st.write('일별 데이터 알려드리겠습니다.')
                
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.header('강남구 견인 통계')

            group_day_time = line_df.groupby(by=['months'], as_index=False)["총 건수"].mean()
            group_day_time = group_day_time.rename(columns={"총 건수": '총 건수'})
            group_day_time['months'] = pd.to_datetime(group_day_time['months'])
            filtered_data_day = group_day_time[group_day_time['months'].isin(day_list_df['months'])]

            # Altair를 사용하여 그래프 그리기
            line = alt.Chart(filtered_data_day).mark_line(point=True).encode(
                x='months:T',
                y='총 건수:Q',
                color=alt.value("#09203E"),  # 선의 색상 지정
                tooltip=['months:T', '총 건수:Q'],  # 툴팁에 표시될 정보 지정
            ).properties(
                width=1000
            )

            # 라인차트 각 점위에 보여줄 텍스트 생성, dy로 텍스트의 위치 조정
            line_text = line.mark_text(align="center", baseline="bottom", dy=-10).encode(
                text=alt.Text("총 건수:Q", format=',.0f')  # 텍스트로 표시될 정보 지정
            )

            # 라인차트와 라인 텍스트 합치기
            line_concated = line + line_text
            st.altair_chart(line_concated, use_container_width=True)
        
# -------------------------------------------------------------TOP3통계-------------------------------------------------------------        
        with col2:
            st.header('견인 TOP 3 동') 
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C'],
                ' ': [55, 50, 43]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)

# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col3, col4 = st.columns([0.6, 0.4])
        with col3:
            st.header('PM 브랜드별 견인 건 수') 
            #바 형태 차트 만들기
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
                ' ': [28, 55, 43, 91, 81, 53, 19, 87, 52]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)
            
        with col4:
            st.header('위반사항별 견인 건 수')
            #도넛 차트 만들기
            donut_df = pd.DataFrame({
                "category": [1, 2, 3, 4, 5, 6],
                "value": [4, 6, 10, 3, 7, 8]
            })

            donut = alt.Chart(donut_df).mark_arc(innerRadius=50).encode(
                theta="value",
                color="category:N",
            )

            st.altair_chart(donut, use_container_width=True)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col5, col6 = st.columns([0.6, 0.4])
        with col5:
            st.header('견인 업체별 견인 건 수') 
            #바 형태 차트 만들기
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
                ' ': [33, 55, 11, 33, 81, 22, 19, 65, 52]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)
            
        with col6:
            st.header('부정견인 단속 현황') 
            pm_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C'],
                '구': ['강남구', '송파구', '송파구'],
                '위반사항': ['지하철 출입구', '버스정류장', '횡단보도'],
                '조치사항': ['견인 중', '견인 완료', '미처리']
            })
            st.markdown('#')
            st.dataframe(pm_df, width=700, height=180)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col7, col8 = st.columns([0.6, 0.4])
        with col7:
            st.header('PM 주차장 현황')
            # tiles 에서 맵 타일 바꾸기
            m = folium.Map(location=[37.56,127.00], zoom_start=11, tiles='cartodbpositron')

            folium.GeoJson(geo_json_data,
                           name="population",
                           style_function=lambda feature: { 
                                "color": "grey",
                                "weight": 2,
                                "dashArray": "5, 5",
                                "fillOpacity":0.2,
                           },

                           highlight_function=lambda feature: {
                                "fillColor": (
                                "#09203E"
                            ),
                            },


                           zoom_on_click=True).add_to(m)

            folium.LayerControl().add_to(m)


            st_data = st_folium(m, width=1200, height=450)
            
        with col8:
            st.subheader('필요 주차장 수')
            st.slider('',  min_value=0, max_value=10, value=10, step=1, label_visibility="collapsed")
            st.markdown('#')
            st.subheader('필요 지역 우선순위')
            pmm_df = pd.DataFrame({
                '구': ['강남구', '송파구', '송파구'],
                '동': ['역삼동','가락동', '방이동']
            })
            st.markdown('#')
            st.dataframe(pmm_df, width=700, height=180)
# -------------------------------------------------------------송파구 상단 탭 설정-------------------------------------------------------------
def page2():
    st.markdown('<div style="text-align: center;"><h1>송파구</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "데이터"],
    icons = ["camera-video-fill", "cone-striped", "clipboard2-data-fill"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles = {"container" : {"padding": "0!important", "background-color":"#D1D8E4"},
             "icon": {"color": "red", "font-size": "30px"},
            "nav-link": {"font-size" : "30px",
                        "text-align" : "center",
                        "margin" : "0px",
                        "--hover-color": "#fffff",
                        },
                        "nav-link-selected": {"background-color": "#09203E"},
             },
)
# -------------------------------------------------------------송파구 관제 설정-------------------------------------------------------------
    if selected == "관제":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        col3, col4 = st.columns([0.7, 0.3])
        with col3:
            st.header('지도')
            show_map2(37.50,127.12,13,songpa_gu_json,songpa_gdf, 1200)
        with col4:
            st.header('CCTV')
            st.video('Desktop/BP/subway_exit.mp4')
        # Display the DataFrame using st.dataframe
        st.dataframe(songpa_cctv, width=1800)
# -------------------------------------------------------------송파구 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        st.header('지도')
        show_map3(37.50,127.12,13,songpa_gu_json,songpa1_gdf,songpa2_gdf,songpa3_gdf  ,1800)
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.subheader('(주)바로견인')
            st.write('전화번호 : 010-0000-0000')
            st.write('업체주소 : 서울시 송파구 OO동')
            st.write('대표명 : 김빅프')
        with col2:
            st.dataframe(songpa1_cctv, width=1800)
# -------------------------------------------------------------송파구 데이터 설정-------------------------------------------------------------

# -------------------------------------------------------------전체 견인 통계-------------------------------------------------------------
    line_df = pd.DataFrame({'months': pd.date_range('2023-01-01', periods=12, freq='M'),
                           '총 건수': [7552, 8080, 7707, 7718, 13895, 14423, 14375, 11898, 12326, 12211, 12739, 12927]
                           })
    if selected == "데이터":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
        with st.sidebar:
            st.header('날짜 구간을 선택하세요')
            slider_data = st.slider('', min_value=datetime(2023, 1, 1), max_value=datetime(2023, 2, 28), value=(datetime(2023, 1, 1), datetime(2023, 12, 31)), format='YYYY-MM-DD')
            day_list_df = line_df[(line_df['months'] >= slider_data[0]) & (line_df['months'] <= slider_data[1])]
            
            st.header('단위를 선택하세요')
            genre = st.radio('보고싶은 기간의 단위를 선택하세요', ('월별', '주별', '일별'))

            if genre == '월별':
                st.write('월별 데이터 알려드리겠습니다.')
            elif genre == '주별':
                st.write('주별 데이터 알려드리겠습니다.')
            else:
                st.write('일별 데이터 알려드리겠습니다.')
                
        col1, col2 = st.columns([0.6, 0.4])
        with col1:
            st.header('송파구 견인 통계')

            group_day_time = line_df.groupby(by=['months'], as_index=False)["총 건수"].mean()
            group_day_time = group_day_time.rename(columns={"총 건수": '총 건수'})
            group_day_time['months'] = pd.to_datetime(group_day_time['months'])
            filtered_data_day = group_day_time[group_day_time['months'].isin(day_list_df['months'])]

            # Altair를 사용하여 그래프 그리기
            line = alt.Chart(filtered_data_day).mark_line(point=True).encode(
                x='months:T',
                y='총 건수:Q',
                color=alt.value("#09203E"),  # 선의 색상 지정
                tooltip=['months:T', '총 건수:Q'],  # 툴팁에 표시될 정보 지정
            ).properties(
                width=1000
            )

            # 라인차트 각 점위에 보여줄 텍스트 생성, dy로 텍스트의 위치 조정
            line_text = line.mark_text(align="center", baseline="bottom", dy=-10).encode(
                text=alt.Text("총 건수:Q", format=',.0f')  # 텍스트로 표시될 정보 지정
            )

            # 라인차트와 라인 텍스트 합치기
            line_concated = line + line_text
            st.altair_chart(line_concated, use_container_width=True)
        
# -------------------------------------------------------------TOP3통계-------------------------------------------------------------        
        with col2:
            st.header('견인 TOP 3 동') 
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C'],
                ' ': [55, 50, 43]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)

# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col3, col4 = st.columns([0.6, 0.4])
        with col3:
            st.header('PM 브랜드별 견인 건 수') 
            #바 형태 차트 만들기
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
                ' ': [28, 55, 43, 91, 81, 53, 19, 87, 52]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)
            
        with col4:
            st.header('위반사항별 견인 건 수')
            #도넛 차트 만들기
            donut_df = pd.DataFrame({
                "category": [1, 2, 3, 4, 5, 6],
                "value": [4, 6, 10, 3, 7, 8]
            })

            donut = alt.Chart(donut_df).mark_arc(innerRadius=50).encode(
                theta="value",
                color="category:N",
            )

            st.altair_chart(donut, use_container_width=True)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col5, col6 = st.columns([0.6, 0.4])
        with col5:
            st.header('견인 업체별 견인 건 수') 
            #바 형태 차트 만들기
            bar_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I'],
                ' ': [33, 55, 11, 33, 81, 22, 19, 65, 52]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x='업체명',
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title="견인 TOP 3 구"

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)
            
        with col6:
            st.header('부정견인 단속 현황') 
            pm_df = pd.DataFrame({
                '업체명': ['A', 'B', 'C'],
                '구': ['강남구', '송파구', '송파구'],
                '위반사항': ['지하철 출입구', '버스정류장', '횡단보도'],
                '조치사항': ['견인 중', '견인 완료', '미처리']
            })
            st.markdown('#')
            st.dataframe(pm_df, width=700, height=180)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------밑 데이터 설정-------------------------------------------------------------
        col7, col8 = st.columns([0.6, 0.4])
        with col7:
            st.header('PM 주차장 현황')
            # tiles 에서 맵 타일 바꾸기
            m = folium.Map(location=[37.56,127.00], zoom_start=11, tiles='cartodbpositron')

            folium.GeoJson(geo_json_data,
                           name="population",
                           style_function=lambda feature: { 
                                "color": "grey",
                                "weight": 2,
                                "dashArray": "5, 5",
                                "fillOpacity":0.2,
                           },

                           highlight_function=lambda feature: {
                                "fillColor": (
                                "#09203E"
                            ),
                            },


                           zoom_on_click=True).add_to(m)

            folium.LayerControl().add_to(m)


            st_data = st_folium(m, width=1200, height=450)
            
        with col8:
            st.subheader('필요 주차장 수')
            st.slider('',  min_value=0, max_value=10, value=10, step=1, label_visibility="collapsed")
            st.markdown('#')
            st.subheader('필요 지역 우선순위')
            pmm_df = pd.DataFrame({
                '구': ['강남구', '송파구', '송파구'],
                '동': ['역삼동','가락동', '방이동']
            })
            st.markdown('#')
            st.dataframe(pmm_df, width=700, height=180)
# -------------------------------------------------------------사이드바 설정(사진)-------------------------------------------------------------
with st.sidebar:
    seoul_logo = {"image_url" : "Desktop/BP/seoul_img.png"}

    #서울특별시
    #SEOUL MY SOUL https://www.seoul.go.kr/res_newseoul/images/seoul/seoulmysoul.png
    #휘장 https://www.seoul.go.kr/res_newseoul/images/seoul/img_seoullogo.png
    #해치 심벌 https://www.seoul.go.kr/res_newseoul/images/seoul/img_symbol1.png

    st.image(seoul_logo["image_url"])
# -------------------------------------------------------------사이드바 설정(강남구/송파구/서초구 선택)-------------------------------------------------------------
# 딕셔너리 선언 {  ‘selectbox항목’ : 페이지명 …  }
page_names_to_funcs = {'전체': page4, '강남구' : page1, '송파구': page2}

# 사이드 바에서 selectbox 선언 & 선택 결과 저장
selected_page = st.sidebar.selectbox('구를 선택하세요', page_names_to_funcs.keys())

# 해당 페이지 부르기
page_names_to_funcs[selected_page]()

st.markdown("""
         <style>
            h3, h2{
                text-align:center;
            }
         </style>


            """, unsafe_allow_html=True)

if selected_page == '강남구':
    with st.sidebar:
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.header('담당자')
        st.header('김미프 주무관')
        st.header('연락처 010-0000-0000')
    
    
if selected_page == '송파구':
    with st.sidebar:
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.markdown("##")
        st.header('담당자')
        st.header('이빅프 주무관')
        st.header('연락처 010-0000-0000')
        st.markdown('<style>div[data-testid="stSidebar"] div div div{text-align: center;}</style>', unsafe_allow_html=True)

        
# streamlit run Desktop\BP\dashboard.py
