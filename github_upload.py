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
import geopandas
import altair as alt
from datetime import datetime
from folium.plugins import MarkerCluster
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc
# -------------------------------------------------------------데이터 불러오기-------------------------------------------------------------
chart_data = pd.read_csv('https://raw.githubusercontent.com/huhshin/streamlit/master/data_sales.csv')
medal = pd.read_csv('https://raw.githubusercontent.com/huhshin/streamlit/master/data_medal.csv')

font_path = "C:\\Windows\\Fonts\\malgun.ttf"  # 맥에서의 예시 경로, 실제 폰트 경로에 맞게 수정
font_name = font_manager.FontProperties(fname=font_path).get_name()
rc('font', family=font_name)

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
gdf = geopandas.read_file("변경cctv.geojson")

gangnam_gdf = gdf[gdf['name'].str.contains("강남구")]
gangnam1_gdf = gdf[gdf['name'].str.contains("강남구1")]
gangnam2_gdf = gdf[gdf['name'].str.contains("강남구2")]
gangnam3_gdf = gdf[gdf['name'].str.contains("강남구3")]
gangnam4_gdf = gdf[gdf['name'].str.contains("강남구4")]
gangnam5_gdf = gdf[gdf['name'].str.contains("강남구5")]
songpa_gdf = gdf[gdf['name'].str.contains("송파구")]
songpa1_gdf = gdf[gdf['name'].str.contains("송파구1")]
songpa2_gdf = gdf[gdf['name'].str.contains("송파구2")]
songpa3_gdf = gdf[gdf['name'].str.contains("송파구3")]
songpa4_gdf = gdf[gdf['name'].str.contains("송파구4")]
songpa5_gdf = gdf[gdf['name'].str.contains("송파구5")]
# cctv 정보

cctv_info = pd.read_csv('변경cctv_info.csv', encoding='cp949')

songpa_cctv = cctv_info.head(7)
songpa1_cctv = cctv_info.head(5)
gangnam_cctv = cctv_info.tail(6)
gangnam1_cctv = cctv_info.tail(5)
data_vis = pd.read_csv('변경data_vis.csv', encoding='cp949')

# -------------------------------------------------------------데이터 프레임 글꼴 설정-------------------------------------------------------------
#시각화 데이터

def show_data(cctv_data):
    header_style = '''
                    <style>
                        table {
                            font-size: 18px;
                            width: 100%;
                            font-family: 'Arial', sans-serif;
                            border-collapse: collapse;
                            text-align: center;
                        }
                        th {
                            background-color: #D1D8E4;
                            font-weight: bold;
                            padding: 12px;
                            text-align: center;
                        }
                        td, th {
                            padding: 5px;
                            text-align: center;
                            color: #09203E;
                        }
                        
                        .status-received {
                            background-color: red;
                        }

                        .status-in-progress {
                            background-color: yellow;
                        }

                        .status-completed {
                            background-color: green;
                        }
                    </style>
                '''

    st.markdown(header_style, unsafe_allow_html=True)

    # Exclude the '처리현황' column from background color styling
    columns_to_style = [col for col in cctv_data.columns if col != '처리현황']

    # Apply style to the entire DataFrame excluding '처리현황' column
    styled_df = cctv_data[columns_to_style].style.applymap(lambda cell: f"background-color: {get_status_color(cell)}").render()

    # Render the styled DataFrame
    st.markdown(styled_df, unsafe_allow_html=True)

def show_data_color(cctv_data):
    header_style = '''
                    <style>
                        table {
                            font-size: 18px;
                            width: 100%;
                            font-family: 'Arial', sans-serif;
                            border-collapse: collapse;
                            text-align: center;
                        }
                        th {
                            background-color: #D1D8E4;
                            font-weight: bold;
                            padding: 12px;
                            text-align: center;
                        }
                        td, th {
                            padding: 5px;
                            text-align: center;
                            color: #09203E;
                        }
                        
                        .status-received {
                            background-color: red;
                        }

                        .status-in-progress {
                            background-color: yellow;
                        }

                        .status-completed {
                            background-color: green;
                        }
                    </style>
                '''

    st.markdown(header_style, unsafe_allow_html=True)

    # Apply style to the entire DataFrame
    styled_df = cctv_data.style.applymap(lambda cell: f"background-color: {get_status_color(cell)}", subset=['처리현황']).render()

    # Render the styled DataFrame
    st.markdown(styled_df, unsafe_allow_html=True)

# Function to get the status color
def get_status_color(status):
    if status == '접수':
        return 'red'
    elif status == '처리중':
        return 'yellow'
    elif status == '견인완료':
        return 'green'
    else:
        return ''


# -------------------------------------------------------------지도 불러오기 함수-------------------------------------------------------------
def show_map(lat, lon, zoom, data):

    df = pd.read_csv("변경seoul_population.csv")

    #지도 포화도에 따른 색 표현
    linear = folium.LinearColormap(
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

    df = pd.read_csv("변경seoul_population.csv")


    #지도 포화도에 따른 색 표현
    linear = folium.LinearColormap(
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

def show_map3(lat, lon, zoom, data, data2, data3, data4, data5, data6, wid):

    df = pd.read_csv("변경seoul_population.csv")


    #지도 포화도에 따른 색 표현
    linear = folium.LinearColormap(
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
    
    
    folium.GeoJson(
        data5,
        name = "cctv",
        marker=folium.Marker(icon=folium.Icon(icon="video-camera", prefix='fa', color='green')),
        tooltip=folium.GeoJsonTooltip(fields=["name", "detected"]),
        popup=folium.GeoJsonPopup(fields=["name", "detected"]),
    ).add_to(m)
    
    folium.GeoJson(
        data6,
        name = "cctv",
        marker=folium.Marker(icon=folium.Icon(icon="video-camera", prefix='fa', color='red')),
        tooltip=folium.GeoJsonTooltip(fields=["name", "detected"]),
        popup=folium.GeoJsonPopup(fields=["name", "detected"]),
    ).add_to(m)
    
    
    folium.LayerControl().add_to(m)

    linear.add_to(m)
    st_data = st_folium(m, width=wid, height=450)
    
def show_map4(lat, lon, zoom, data):

    df = pd.read_csv("변경seoul_population.csv")

    #지도 포화도에 따른 색 표현
    linear = folium.LinearColormap(
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
    st_data = st_folium(m, width=1800, height=500)

def show_map_grey(lat, lon, zoom, data):

    df = pd.read_csv("변경seoul_population.csv")

    #지도 포화도에 따른 색 표현
    linear = folium.LinearColormap(
    [ '#E6E6E6', '#848484', '#424242'],
    vmin = df.total.min(),
    vmax = df.total.max(),
    caption="population"

    )

    df_dict = df.set_index("district")["total"]

    m = folium.Map(location=[lat, lon], zoom_start=zoom, tiles='cartodbpositron')


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
    st_data = st_folium(m, width=1000, height=500)
# -------------------------------------------------------------홈페이지 탭 아이콘, 홈페이지 명 설정-------------------------------------------------------------
st.set_page_config(
        page_title= '빅프로젝트_10조',
        page_icon=":smile:",
        layout = "wide",
        initial_sidebar_state="expanded")

# -------------------------------------------------------------관제, 경로안내, 데이터 탭 내용 설정-------------------------------------------------------------
    
# -------------------------------------------------------------전체 설정-------------------------------------------------------------
def page4():
   # -------------------------------------------------------------[전체] 상단 탭 설정-------------------------------------------------------------
    
    
    st.markdown('<div style="text-align: center;"><h1>전체</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "대시보드"],
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
# -------------------------------------------------------------[전체] 관제 설정-------------------------------------------------------------
    if selected == "관제":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([0.7, 0.3])
        with col1:
            st.header('서울특별시')
            show_map(37.56,127,11,geo_json_data)
        
        with col2:
            st.header('지역 별 신고') 
            
            labels = '강남구', '송파구', '서초구', '강동구', '기타'
            sizes = [50, 40, 30, 10, 5]
            explode = (0.1, 0, 0, 0, 0)  # only "explode" the 2nd slice (i.e. 'Hogs')

            # 파이 차트 생성
            fig1, ax1 = plt.subplots(figsize=(5,5))
            ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=True, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # 범례 추가
            ax1.legend(labels, title="지역", loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1))

            # 그래프를 Streamlit에 표시
            st.pyplot(fig1)
        
        col33, col44, col55, col66 = st.columns([0.25, 0.25, 0.25, 0.25])

        with col33:
            st.markdown(
                """
                <div style="text-align: center; font-size: 35px; font-weight: bold; font-family: 'Arial', sans-serif;">
                    <div>23년 누적 견인 수</div>
                    <div style="font-size: 28px;margin-top: 15px;">6.1만 건 <span style="color: green;">(+0.1 만 건)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col44:
            st.markdown(
                """
                <div style="text-align: center; font-size: 35px; font-weight: bold; font-family: 'Arial', sans-serif;">
                    <div>1월 누적 견인 수</div>
                    <div style="font-size: 28px;margin-top: 15px;">4.3천 건 <span style="color: green;">(+0.2천 건)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col55:
            st.markdown(
                """
                <div style="text-align: center; font-size: 35px; font-weight: bold; font-family: 'Arial', sans-serif;">
                    <div>주간 견인 수</div>
                    <div style="font-size: 28px; margin-top: 15px;">980 건 <span style="color: red;">(-40 건)</div>
                </div>
                """,
                unsafe_allow_html=True
            )

        with col66:
            st.markdown(
                """
                <div style="text-align: center; font-size: 35px; font-weight: bold; font-family: 'Arial', sans-serif;">
                    <div>금일 견인 수</div>
                    <div style="font-size: 28px; margin-top: 15px;">100 건 <span style="color: red;">(-11 건)</div>
                </div>
                """,
                unsafe_allow_html=True
            )



        
# -------------------------------------------------------------[전체] 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
       
        show_map4(37.56,127,11,geo_json_data)
        
        
        # Display the DataFrame using st.dataframe
        show_data(cctv_info)
        
# -------------------------------------------------------------[전체] 데이터 설정-------------------------------------------------------------

# -------------------------------------------------------------[전체]전체 견인 통계-------------------------------------------------------------
    line_df = pd.DataFrame({'months': pd.date_range('2023-01-01', periods=12, freq='M'),
                           '총 건수': [7552, 8080, 7707, 7718, 13895, 14423, 14375, 11898, 12326, 12211, 12739, 12927],
                            
                           })
    
    if selected == "대시보드":
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
        
# -------------------------------------------------------------[전체]TOP3통계-------------------------------------------------------------        
        with col2:
            st.header('견인 TOP 3 구') 
            bar_df = pd.DataFrame({
                '업체명': ['강남구', '서초구', '송파구'],
                ' ': [55, 50, 43]
            })

            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(line_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x=alt.X('업체명', axis=alt.Axis(labelAngle=0)),
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title=""

            )
            #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
            bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
                #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
                x=alt.X('업체명', axis=alt.Axis(labelAngle=0)),
                y=' ',
            ).properties(
                #width= 에서 바 차트의 너비 결정
                width=500,
                title=""

            )
            
#             bar_df = pd.DataFrame({
#                 '업체명': ['강남구', '서초구', '송파구'],
#                 ' ': [55, 50, 43]
#             })

#             #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
#             bar = alt.Chart(line_df).mark_bar(size=50, color="#2E9AFE").encode(
#                 #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
#                 x=alt.X('업체명', axis=alt.Axis(labelAngle=0)),
#                 y=' ',
#             ).properties(
#                 #width= 에서 바 차트의 너비 결정
#                 width=500,
#                 title=""

#             )
#             #mark_bar(size= )에서 바의 요소의 너비 결정, color에서 컬러 결정
#             bar = alt.Chart(bar_df).mark_bar(size=50, color="#2E9AFE").encode(
#                 #x축 y축의 이름이 데이터의 컬럼명과 같아야함.
#                 x=alt.X('업체명', axis=alt.Axis(labelAngle=0)),
#                 y=' ',
#             ).properties(
#                 #width= 에서 바 차트의 너비 결정
#                 width=500,
#                 title=""

#             )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)

# ------------------------------------------------------------[전체]위반사항 설정-------------------------------------------------------------
        col3, col99 ,col4= st.columns([0.6,0.1, 0.3])
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
                title=""

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)
        with col99:
            st.header('')
        with col4:
            st.header('위반사항별 견인 건 수')
            labels = '횡단보도', '버스정류장', '지하철입구', '점자블록', '기타'
            sizes = [50, 40, 30, 10, 5]
            

            # 파이 차트 생성
            fig1, ax1 = plt.subplots(figsize=(5,5))
            ax1.pie(sizes,  labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # 범례 추가
            ax1.legend(labels, title="위반사항", loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1))

            # 그래프를 Streamlit에 표시
            st.pyplot(fig1)
            
            
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------[전체]부정견인 설정-------------------------------------------------------------
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
                title=""

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
                '업체명': ['바로견인', '견인왕', '견인빨리','실어날라'],
                '구': ['강남구','강남구',  '송파구', '송파구'],
                '적발내역': ['직접 신고', '불법 견인', '최대 적재대수 초과', '견인규정 미준수']
                
            })
            st.markdown('#')
            show_data(pm_df)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------[전체]주차장 설정-------------------------------------------------------------
        col7, col8 = st.columns([0.6, 0.4])
        with col7:
            st.header('PM 주차장 현황')
            
            show_map_grey(37.56,127,11,geo_json_data)
            
        with col8:           
            st.subheader('필요 주차장 수')
            slider_value = st.slider('',  min_value=0, max_value=5, value=5, step=1, label_visibility="collapsed")
            st.markdown('#')

            st.subheader('필요 지역 우선순위')
            pmm_df = pd.DataFrame({
                '구': ['강남구','강남구', '송파구', '송파구'],
                '동': ['역삼동', '논현동', '가락동', '방이동']
            })

            # Display DataFrame based on slider value
            if slider_value <= 3:
                st.markdown('#')
                show_data(pmm_df.head(2))
            else:
                st.markdown('#')
                show_data(pmm_df)

                        
def page1():
    # -------------------------------------------------------------[강남구]상단 탭 설정-------------------------------------------------------------
    
        
    st.markdown('<div style="text-align: center;"><h1>강남구</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "대시보드"],
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

# -------------------------------------------------------------[강남구] 관제 설정-------------------------------------------------------------
    if selected == "관제":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        col3, col4 = st.columns([0.7, 0.3])
        with col3:
            st.header('지도')
            show_map2(37.496,127.07,12,gangnam_geo_json, gangnam_gdf, 1200)
        with col4:
            st.header('CCTV')
            st.video('변경subway_exit.mp4')

            data_df = pd.DataFrame(
                {
                    "주소": ["강남구 논현로36길 22"],
                    "탐지 PM 수" : 1,
                    "견인 필요": [False],
                }
            )

            st.data_editor(
                data_df,
                 width=510,
                column_config={
                    "favorite": st.column_config.CheckboxColumn(
                        "Your favorite?",
                        help="Select your **favorite** widgets",
                        default=False,
                    )
                },
                disabled=["widgets"],
                hide_index=True,
            )
        show_data(gangnam_cctv)
        
        


# -------------------------------------------------------------[강남구] 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
        show_map3(37.496,127.07,12,gangnam_geo_json,gangnam3_gdf, gangnam4_gdf, gangnam2_gdf,gangnam1_gdf,gangnam5_gdf, 1800)
        
        col1, col2 = st.columns([0.2, 0.8])

        with col1:
            option = st.selectbox(
                '견인 업체를 선택하시오.',
                ('(주)바로견인', '(주)견인왕', '(주)견인빨리'))
            st.subheader('(주)바로견인')
            
            comp = pd.DataFrame(
                [
                    {"-": "전화번호", "":"010-0000-0000"},
                    {"-": "업체주소", "": "서울시 강남구 OO동"},
                    {"-": "대표명", "": "김빅프"},
                ]
            )
            
            
            st.dataframe(comp, width=350, hide_index=True)
          
            
        with col2:
            

            gangnam1_cctv['처리현황'] = ['견인완료', '견인완료' , '처리중', '접수','접수']
            show_data_color(gangnam1_cctv)
            
# -------------------------------------------------------------[강남구] 데이터 설정-------------------------------------------------------------
# -------------------------------------------------------------[강남구]전체 견인 통계-------------------------------------------------------------
    line_df = pd.DataFrame({'months': pd.date_range('2023-01-01', periods=12, freq='M'),
                           '총 건수': [7552, 8080, 7707, 7718, 13895, 14423, 14375, 11898, 12326, 12211, 12739, 12927]
                           })
    if selected == "대시보드":
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
        
# -------------------------------------------------------------[강남구]TOP3통계-------------------------------------------------------------        
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

# ------------------------------------------------------------[강남구]위반사항 설정-------------------------------------------------------------
        col3, col99 ,col4= st.columns([0.6 ,0.1, 0.3])
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
            
        with col99:
            st.header('')
            
        with col4:
            st.header('위반사항별 견인 건 수')
            
            labels = '횡단보도', '버스정류장', '지하철입구', '점자블록', '기타'
            sizes = [50, 40, 30, 10, 5]
            

            # 파이 차트 생성
            fig1, ax1 = plt.subplots(figsize=(5,5))
            ax1.pie(sizes,  labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # 범례 추가
            ax1.legend(labels, title="위반사항", loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1))

            # 그래프를 Streamlit에 표시
            st.pyplot(fig1)
            
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------[강남구]부정견인 설정-------------------------------------------------------------
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
                '업체명': ['바로견인', '견인왕', '견인빨리','실어날라'],
                '구': ['강남구','강남구',  '강남구','강남구'],
                '적발내역': ['직접 신고', '불법 견인', '최대 적재대수 초과', '견인규정 미준수']
            })
            st.markdown('#')
            show_data(pm_df)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------[강남구]주차장 설정-------------------------------------------------------------
        col7, col8 = st.columns([0.6, 0.4])
        with col7:
            st.header('PM 주차장 현황')
            show_map_grey(37.56,127,11,geo_json_data)
            
        with col8:
            st.subheader('필요 주차장 수')
            slider_value = st.slider('',  min_value=0, max_value=5, value=5, step=1, label_visibility="collapsed")
            st.markdown('#')

            st.subheader('필요 지역 우선순위')
            pmm_df = pd.DataFrame({
                '구': ['강남구','강남구', '강남구', '강남구'],
                '동': ['역삼동', '논현동', '대치동', '개포동']
            })

            # Display DataFrame based on slider value
            if slider_value <= 3:
                st.markdown('#')
                show_data(pmm_df.head(2))
            else:
                st.markdown('#')
                show_data(pmm_df)
# -------------------------------------------------------------[송파구] 상단 탭 설정-------------------------------------------------------------
def page2():
    st.markdown('<div style="text-align: center;"><h1>송파구</h1></div>', unsafe_allow_html=True)
    selected = option_menu(
    menu_title="",
    options = ["관제", "견인관리", "대시보드"],
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
# -------------------------------------------------------------[송파구] 관제 설정-------------------------------------------------------------
    if selected == "관제":
        
        
        col3, col4 = st.columns([0.7, 0.3])
        
        with col3:
            st.header('지도')
            show_map2(37.50,127.12,13,songpa_gu_json,songpa_gdf, 1200)
            
        with col4:
            
            st.header('CCTV')
            st.video('변경subway_exit.mp4')
            data_df = pd.DataFrame(
                {
                    "주소": ["송파구 오금로34길 8-23"],
                    "탐지 PM 수" : 1,
                    "견인 필요": [False],
                }
            )

            st.data_editor(
                data_df,
                 width=510,
                column_config={
                    "favorite": st.column_config.CheckboxColumn(
                        "Your favorite?",
                        help="Select your **favorite** widgets",
                        default=False,
                    )
                },
                disabled=["widgets"],
                hide_index=True,
            )
        
        show_data(songpa_cctv)
# -------------------------------------------------------------[송파구] 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        # st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        st.header('지도')
        show_map3(37.50,127.12,13,songpa_gu_json,songpa1_gdf,songpa2_gdf,songpa3_gdf,songpa4_gdf,songpa5_gdf, 1800)
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            option = st.selectbox(
                '견인 업체를 선택하시오.',
                ('(주)바로견인', '(주)견인왕', '(주)견인빨리'))
            st.subheader('(주)바로견인')
            
            comp = pd.DataFrame(
                [
                    {"-": "전화번호", "":"010-0000-0000"},
                    {"-": "업체주소", "": "서울시 송파구 OO동"},
                    {"-": "대표명", "": "김빅프"},
                ]
            )
            
            
            st.dataframe(comp, width=350, hide_index=True)
          
            
        with col2:
            

            songpa1_cctv['처리현황'] = ['견인완료', '견인완료' , '처리중', '접수','접수']
            show_data_color(songpa1_cctv)
# -------------------------------------------------------------[송파구]데이터 설정-------------------------------------------------------------

# -------------------------------------------------------------[송파구]전체 견인 통계-------------------------------------------------------------
    line_df = pd.DataFrame({'months': pd.date_range('2023-01-01', periods=12, freq='M'),
                           '총 건수': [7552, 8080, 7707, 7718, 13895, 14423, 14375, 11898, 12326, 12211, 12739, 12927]
                           })
    if selected == "대시보드":
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
        
# -------------------------------------------------------------[송파구]TOP3통계-------------------------------------------------------------        
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
                title=""

            )

            #바 차트위에 보여줄 텍스트  생성, dy로 텍스트 위치 조정
            bar_text = bar.mark_text(align="center", baseline="bottom", dy=-5).encode(
                    text=alt.Text(" ")
                )

            #바차트와 텍스트 합치기
            bar_concated = bar + bar_text

            #바 차트 보여주기, use_container_width=True를 하면 한 줄을 다 채움

            st.altair_chart(bar_concated, use_container_width=True)

# ------------------------------------------------------------[송파구]위반사항 설정-------------------------------------------------------------
        col3, col99 ,col4= st.columns([0.6,0.1, 0.3])
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
        
        with col99:
            st.header('')
        
        with col4:
            st.header('위반사항별 견인 건 수')
            labels = '횡단보도', '버스정류장', '지하철입구', '점자블록', '기타'
            sizes = [50, 40, 30, 10, 5]
            

            # 파이 차트 생성
            fig1, ax1 = plt.subplots(figsize=(5,5))
            ax1.pie(sizes,  labels=labels, autopct='%1.1f%%', shadow=False, startangle=90)
            ax1.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

            # 범례 추가
            ax1.legend(labels, title="위반사항", loc="upper left", bbox_to_anchor=(1, 0, 0.5, 1))

            # 그래프를 Streamlit에 표시
            st.pyplot(fig1)
            
            
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------[송파구]부정견인 설정-------------------------------------------------------------
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
                title=""

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
                '업체명': ['바로견인', '견인왕', '견인빨리','실어날라'],
                '구': [ '송파구', '송파구',  '송파구', '송파구'],
                '적발내역': ['직접 신고', '불법 견인', '최대 적재대수 초과', '견인규정 미준수']
            })
            st.markdown('#')
            show_data(pm_df)
            st.markdown('#')
            st.markdown('#')
# ------------------------------------------------------------[송파구]주차장 설정-------------------------------------------------------------
        col7, col8 = st.columns([0.6, 0.4])
        with col7:
            st.header('PM 주차장 현황')
            show_map_grey(37.56,127,11,geo_json_data)
            
        with col8:
            st.subheader('필요 주차장 수')
            slider_value = st.slider('',  min_value=0, max_value=5, value=5, step=1, label_visibility="collapsed")
            st.markdown('#')

            st.subheader('필요 지역 우선순위')
            pmm_df = pd.DataFrame({
                '구': ['송파구','송파구', '송파구', '송파구'],
                '동': ['문정동', '장지동', '가락동', '방이동']
            })

            # Display DataFrame based on slider value
            if slider_value <= 3:
                st.markdown('#')
                show_data(pmm_df.head(2))
            else:
                st.markdown('#')
                show_data(pmm_df)
# -------------------------------------------------------------사이드바 설정(사진)-------------------------------------------------------------
with st.sidebar:
    seoul_logo = {"image_url" : "변경seoul_img.png"}

    #서울특별시
    #SEOUL MY SOUL https://www.seoul.go.kr/res_newseoul/images/seoul/seoulmysoul.png
    #휘장 https://www.seoul.go.kr/res_newseoul/images/seoul/img_seoullogo.png
    #해치 심벌 https://www.seoul.go.kr/res_newseoul/images/seoul/img_symbol1.png

    st.image(seoul_logo["image_url"])
# -------------------------------------------------------------사이드바 설정(강남구/송파구/서초구 선택)-------------------------------------------------------------
def page6():
    with st.sidebar:
        st.markdown('#')
def page7():
    with st.sidebar:
        st.markdown('#')
def page8():
    with st.sidebar:
        st.markdown('#')
def page9():
    with st.sidebar:
        st.markdown('#')
def page10():
    with st.sidebar:
        st.markdown('#')
def page11():
    with st.sidebar:
        st.markdown('#')
def page12():
    with st.sidebar:
        st.markdown('#')
def page13():
    with st.sidebar:
        st.markdown('#')
def page14():
    with st.sidebar:
        st.markdown('#')
def page15():
    with st.sidebar:
        st.markdown('#')
def page16():
    with st.sidebar:
        st.markdown('#')
def page17():
    with st.sidebar:
        st.markdown('#')
def page18():
    with st.sidebar:
        st.markdown('#')
def page19():
    with st.sidebar:
        st.markdown('#')
def page20():
    with st.sidebar:
        st.markdown('#')
def page21():
    with st.sidebar:
        st.markdown('#')
def page22():
    with st.sidebar:
        st.markdown('#')
def page23():
    with st.sidebar:
        st.markdown('#')
def page24():
    with st.sidebar:
        st.markdown('#')
def page25():
    with st.sidebar:
        st.markdown('#')
def page26():
    with st.sidebar:
        st.markdown('#')
def page27():
    with st.sidebar:
        st.markdown('#')
def page28():
    with st.sidebar:
        st.markdown('#')
    
# 딕셔너리 선언 {  ‘selectbox항목’ : 페이지명 …  }
page_names_to_funcs = {'전체': page4, '강남구' : page1, '송파구': page2, '강동구': page6, '강북구': page7, '강서구': page8, '관악구': page9, '광진구': page10, '구로구': page11, '금천구': page12, '노원구': page13, '도봉구': page14, '동대문구': page15,
                       '동작구': page16, '마포구': page17, '서대문구': page18, '서초구': page19, '성동구': page20, '성북구': page21, '양천구': page22, '영등포구': page23, '용산구': page24, '은평구': page25,'종로구': page26,'중구': page27,'중랑구': page28}


    
    
    
    
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

        
# streamlit run 변경\github_upload
