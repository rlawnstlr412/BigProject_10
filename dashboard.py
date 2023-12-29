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
gdf = geopandas.read_file("Desktop/BP/cctv.geojson")

gangnam_gdf = gdf[gdf['name'].str.contains("강남구")]

songpa_gdf = gdf[gdf['name'].str.contains("송파구")]

# cctv 정보

cctv_info = pd.read_csv('Desktop/BP/cctv_info.csv', encoding='cp949')
cctv_info.set_index(cctv_info.columns[0], inplace=True)
cctv_info.index.name=None
songpa_cctv = cctv_info.head()
songpa1_cctv = cctv_info.head(1)
gangnam_cctv = cctv_info.tail(4)
gangnam1_cctv = cctv_info.tail(1)
# -------------------------------------------------------------지도 불러오기 함수-------------------------------------------------------------
def show_map(lat, lon, zoom, data):

    df = pd.read_csv("Desktop/BP/seoul_population.csv")

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


# -------------------------------------------------------------맵,마커 불러오기 함수-------------------------------------------------------------

def show_map2(lat, lon, zoom, data, data2):

    df = pd.read_csv("Desktop/BP/seoul_population.csv")


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
        marker=folium.Marker(icon=folium.Icon(icon="video-camera", prefix='fa')),
        tooltip=folium.GeoJsonTooltip(fields=["name", "detected"]),
        popup=folium.GeoJsonPopup(fields=["name", "detected"]),


    ).add_to(m)

    folium.LayerControl().add_to(m)

    linear.add_to(m)
    st_data = st_folium(m, width=1200, height=450)

# -------------------------------------------------------------홈페이지 탭 아이콘, 홈페이지 명 설정-------------------------------------------------------------
st.set_page_config(
        page_title= '빅프로젝트_10조',
        page_icon=":smile:",
        layout = "wide",
        initial_sidebar_state="expanded")

# -------------------------------------------------------------관제, 경로안내, 데이터 탭 내용 설정-------------------------------------------------------------
    
# -------------------------------------------------------------전체 설정-------------------------------------------------------------
def page4():
   # -------------------------------------------------------------전체 상단 탭 설정-------------------------------------------------------------
    
        
    st.markdown('<div style="text-align: center;"><h1>종합</h1></div>', unsafe_allow_html=True)
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
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)

        
# -------------------------------------------------------------전체 데이터 설정-------------------------------------------------------------
    if selected == "데이터":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
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
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        col3, col4 = st.columns([0.7, 0.3])
        with col3:
            st.header('지도')
            show_map2(37.496,127.07,12,gangnam_geo_json,gangnam_gdf)
        with col4:
            st.header('CCTV')
            
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
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
        show_map2(37.496,127.07,12,gangnam_geo_json,gangnam_gdf)
        col1, col2 = st.columns([0.2, 0.8])

        with col1:
            st.subheader('(주)바로견인')
            st.write('바로바로')

        with col2:
            st.dataframe(gangnam1_cctv, width=1800)

# -------------------------------------------------------------강남구 데이터 설정-------------------------------------------------------------
    if selected == "데이터":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
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
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        col3, col4 = st.columns([0.7, 0.3])
        with col3:
            st.header('지도')
            show_map2(37.50,127.12,13,songpa_gu_json,songpa_gdf)
        with col4:
            st.header('CCTV')
        
        # Display the DataFrame using st.dataframe
        st.dataframe(songpa_cctv, width=1800)
# -------------------------------------------------------------송파구 견인관리 설정-------------------------------------------------------------

    if selected == "견인관리":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        col3, col4 = st.columns([0.7, 0.3])
        with col3:
            st.header('지도')
            show_map2(37.50,127.12,13,songpa_gu_json,songpa_gdf)
        with col4:
            st.header('CCTV')
        

        
        col1, col2 = st.columns([0.2, 0.8])
        with col1:
            st.subheader('(주)바로견인')
            st.write('바로바로')

        with col2:
            st.dataframe(gangnam1_cctv, width=1800)
# -------------------------------------------------------------송파구 데이터 설정-------------------------------------------------------------

    if selected == "데이터":
        st.markdown(f'<div style="text-align: center;"><h1>{selected}</h1></div>', unsafe_allow_html=True)
        
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
        # 사이 공간 조정
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
        st.header('정지혜 주무관')
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
        st.header('남종하 주무관')
        st.header('연락처 010-0000-0000')
        st.markdown('<style>div[data-testid="stSidebar"] div div div{text-align: center;}</style>', unsafe_allow_html=True)

        
# streamlit run Desktop\BP\dashboard.py
