from logging import warning
import dash
from dash import html, dcc, dash_table
import plotly.express as px
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
import dash_daq as daq
from dash.dependencies import Input, Output, State
import os
from time import strftime,localtime
from datetime import datetime, timedelta
from dash.exceptions import PreventUpdate
import plotly.graph_objects as go
import dash_leaflet as dl
import dash_auth

import pymongo
import pytz

local_tz = pytz.timezone('Asia/Seoul')  # 원하는 로컬 시간대로 변경하세요.

import sys
sys.path.append('/home/ubuntu/airflow/')
from utils import config


''' Mongfo DB option'''
conf = config.ConfigDB()
mongo_id = conf.MONGO['BLE']['user']
mongo_passwd = conf.MONGO['BLE']['password']
mongo_host =conf.MONGO['BLE']['host']
mongo_DB = conf.MONGO['BLE']['DB']
mongo_URI = f'mongodb://{mongo_id}:{mongo_passwd}@{mongo_host}:27017/?replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false'
key_path = "/home/ubuntu/airflow/pemkey"
client = pymongo.MongoClient(mongo_URI, tls=True, tlsCAFile=f'{key_path}/global-bundle.pem')

##Specify the database to be used
monDB_ble = client.BLE
monDB_lte = client.LTE
##Specify the collection to be used


# collection 날짜를 돌려주는 함수
def show_date(on):
    # BLE 센서 버전이라면
    if on == False:
        global monDB_ble
        date_list = monDB_ble.list_collection_names()
        return date_list

    # LTE 센서 버전이라면
    else:
        global monDB_lte
        date_list = monDB_lte.list_collection_names()
        return date_list
    
def show_phonenum(date,on): 
    # BLE 센서 버전이라면
    if on == False:
        global monDB_ble
        col = monDB_ble[date]
        field_name = 'phone_num'
        phone_list = col.distinct(field_name) 
        return phone_list
    
    # LTE 센서 버전이라면
    else:
        global monDB_lte
        col = monDB_lte[date]
        field_name = 'phone_num'
        phone_list = col.distinct(field_name) 
        return phone_list


def show_sensor(phone,date,on):
    # BLE 센서 버전이라면
    if on == False:
        query = {"phone_num": phone}
        col = monDB_ble[date]
        sensor_ids = col.distinct("sensor_id", query)
        return sensor_ids
    else :
        query = {"phone_num": phone}
        col = monDB_lte[date]
        sensor_ids = col.distinct("sensor_id", query)
        return sensor_ids


# BLE 데이터 불러오기
def Load_BLEData(date,phone, sensor):
    global monDB_ble
    # result = monDB_ble[date].find({"$and": [
    #     {"sensor_id": sensor},
    #     {"phone_num": phone}
    # ]
    # },
    #     {"_id": 0}).batch_size(10000)
    
    projection = {"_id": 0, "time": 1, "sensor_id": 1, "ACCEL_X": 1, "ACCEL_Y": 1, "ACCEL_Z": 1, "GYRO_X": 1, "GYRO_Y": 1, "GYRO_Z": 1, "PITCH": 1,"ROLL": 1, "LAT": 1, "LON": 1, "VELOCITY": 1, "ALTITUDE": 1,"BEARING": 1 }
    result = monDB_ble[date].find(
    {"phone_num": phone, "sensor_id": sensor},  # 쿼리 조건
    projection                                  # 프로젝션 적용
    ).batch_size(10000)    
    
    df = pd.DataFrame(result)
    raw_data = df[["time","sensor_id","ACCEL_X","ACCEL_Y","ACCEL_Z","GYRO_X","GYRO_Y","GYRO_Z","PITCH","ROLL","LAT","LON","VELOCITY","ALTITUDE","BEARING"]]


    raw_data.sort_values(by=['time'],ascending=True,inplace=True) 
    raw_data['time'] = raw_data['time'].apply(
        lambda x: datetime.fromtimestamp(x / 1000, tz=local_tz).strftime('%Y-%m-%d %H:%M:%S'))
    
    # raw_data['time'] = raw_data['time'].apply(convert_timestamp_to_datetime_with_milliseconds)
    

    raw_data.columns = ["DATE", "senor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
                        "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VEL", "ALT", "HEAD"]
    raw_data = raw_data.reset_index(drop=True)
    raw_data["DATE"] = pd.to_datetime(raw_data["DATE"])
    raw_data.drop_duplicates(subset='DATE')
    return raw_data


# LTE 데이터 불러오기
def Load_LTEData(date, phone, sensor):
    global monDB_lte
    # result = monDB_lte[date].find({"$and": [
    #     {"sensor_id": sensor},
    #     {"phone_num": phone}
    # ]
    # },
    #     {"_id": 0}).batch_size(10000)
    
    projection = {"_id": 0, "time": 1, "sensor_id": 1, "ACCEL_X": 1, "ACCEL_Y": 1, "ACCEL_Z": 1, "GYRO_X": 1, "GYRO_Y": 1, "GYRO_Z": 1, "PITCH": 1,"ROLL": 1, "LAT": 1, "LON": 1, "VELOCITY": 1, "ALTITUDE": 1,"BEARING": 1, "TIME": 1, "DISTANCE": 1 }
    result = monDB_lte[date].find(
    {"phone_num": phone, "sensor_id": sensor},  # 쿼리 조건
    projection                                  # 프로젝션 적용
    ).batch_size(10000)    
    
    df = pd.DataFrame(result)    
    raw_data = df[["time", "sensor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
                    "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VELOCITY", "ALTITUDE", "BEARING","TIME","DISTANCE"]]


    raw_data.sort_values(by=['time'],ascending=True,inplace=True)
    raw_data['time'] = raw_data['time'].apply(
        lambda x: datetime.fromtimestamp(x / 1000, tz=local_tz).strftime('%Y-%m-%d %H:%M:%S'))
    raw_data.columns = ["DATE", "senor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
                        "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VEL", "ALT", "HEAD","TIME","DISTANCE"]
    raw_data["DATE"] = pd.to_datetime(raw_data["DATE"])
    raw_data.drop_duplicates(subset='DATE')
    return raw_data



# 9시간 차이가 나는 행을 삭제하는 함수
def cleaning_data(data):
    # np.where 함수를 이용해 DATE 컬럼을 차분해서 값이 32400000000000인 인덱스만 리스트 형태로 리턴받는다.
    over_9_idx_list = list(np.where((np.diff(data["DATE"]).astype(np.int) == 32400000000000) | (np.diff(data["DATE"]).astype(np.int) == 32401000000000))[0])

    while True:
        if len(over_9_idx_list) != 0:
            data = data.drop(over_9_idx_list)
            data.reset_index(inplace = True, drop = True)
            over_9_idx_list = list(np.where((np.diff(data["DATE"]).astype(np.int) == 32400000000000) | (np.diff(data["DATE"]).astype(np.int) == 32401000000000))[0])
        elif len(over_9_idx_list) == 0:
            break
    
    data.reset_index(inplace = True, drop = True)
    
    return data

popover_children = "초록(센서 연결 O), 주황(센서 연결 X), 빨강(GPS 오류)"

# ------------------------------------------------------------------ 레이아웃 요소 ------------------------------------------------------------------
first_card = dbc.CardBody([html.H5("DocumentDB data reading", className="card-title"),
                            html.P("확인하고 싶은 날짜, 전화번호, 센서를 순차적으로 선택 후 조회 버튼 클릭하세요."),

                            # 날짜(collection) 목록
                            dcc.Dropdown(placeholder = "날짜", id='date_dropdown', style = {"width": "5vw", "color": "black"}),
                            # 전화 목록
                            dcc.Dropdown(placeholder = '전화번호', 
                                        style = {"width": "7.5vw", "color": "black", "position": "relative", "left": "2.7vw", "top": "-1.38vh"}, 
                                        id = "phone_dropdown"),                               
                            # 센서 목록
                            dcc.Dropdown(placeholder = '센서 뒤 4자리', 
                                        style = {"width": "10vw", "position": "relative", "left": "6.6vw", "top": "-2.78vh", "color":"black"},
                                        id = "sensor_dropdown"),
                            # 조회 버튼
                            dbc.Button("조회", color = 'warning', size="lg", id = "search_button", n_clicks=0, className="me-1", 
                                        style= {"position": "relative", "left": "24.5vw", "top": "-8.7vh", "width": "100px"}),

                            html.H3(id = "announce", style= {"position": "relative", "left": "0.2vw", "top": "-7vh"})

                        ], style= {"height": "20vh"})


second_card = dbc.CardBody([html.H5("센서", className="card-title"),
                            html.Div(id='boolean-switch-output-1'),
                            html.Br(),
                            daq.BooleanSwitch(id='my-boolean-switch', on=False),], style= {"height": "20vh"})

# 그래프 영역에 들어갈 구성 목록
first_graph = dbc.CardBody([html.H5("평균 초당 데이터 그래프", className= "card-title"), dcc.Graph(id= "first_graph", style= {"height": "40vh"})], style= {"height": "50vh"})
second_graph = dbc.CardBody([html.H5("평균 ACCEL 그래프", className= "card-title"), dcc.Graph(id= "second_graph",style= {"height": "40vh"})], style= {"height": "50vh"})
third_graph = dbc.CardBody([html.H5("평균 GYRO 그래프", className= "card-title"), dcc.Graph(id= "third_graph",style= {"height": "40vh"})], style= {"height": "50vh"})
fourth_graph = dbc.CardBody([html.H5("평균 ATTITUDE 그래프", className= "card-title"), dcc.Graph(id= "fourth_graph",style= {"height": "40vh"})], style= {"height": "50vh"})
fifth_graph = dbc.CardBody([html.H5("평균 VEL 그래프", className= "card-title"), dcc.Graph(id= "fifth_graph",style= {"height": "40vh"})], style= {"height": "50vh"})
output_card = dbc.Card([dbc.CardHeader("이동 시간, 이동 거리"), dbc.CardBody(id= "output_card")], style= {"height": "30vh"})


map_card = dbc.CardBody([html.H5("지도", className= "card-title"), 
                        dbc.Button("지도 출력", color = "primary", size= "sm", id= "map_button", n_clicks=0, style= {"position": "relative", "left": "2.5vw", "top": "-3vh"}), dbc.Button("색상 정보",id="hover-target", color="danger",className="me-1",n_clicks=0, size = "sm", style = {"position": "relative", "left": "3vw", "top": "-3vh"}),
                                dbc.Popover(popover_children,target="hover-target", body=True,trigger="hover"),
                        dl.Map([dl.TileLayer(url = "https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png?api_key=93889be7-805e-4f44-9874-773f0117da64")], 
                        center=[37.523254, 126.923528], zoom = 12, id= "map_card", style= {"height": "85vh"})], style= {"height": "100vh"})

# ------------------------------------------------------------------ 레이아웃 구성 ------------------------------------------------------------------

# 로그인 정보
VALID_USERNAME_PASSWORD_PAIRS = {
    'admin': 'gambyul9$'
}

app = dash.Dash(external_stylesheets=[dbc.themes.QUARTZ])


auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

app.layout = html.Div(children=[
    dbc.Row([
        dbc.Col(dbc.Card(first_card, color="secondary", style= {"z-index": "10"}), width=4),
        dbc.Col(dbc.Card(second_card, color="secondary", style= {"z-index": "10"}), width=2)
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(dbc.Card(first_graph, color="secondary")),
        dbc.Col(dbc.Card(second_graph, color="secondary"))
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(dbc.Card(third_graph, color="secondary")),
        dbc.Col(dbc.Card(fourth_graph, color="secondary"))
    ]),

    html.Br(),
    
    dbc.Row([
        dbc.Col(dbc.Card(fifth_graph, color="secondary"),width=6),
        dbc.Col(dbc.Card(output_card, color="secondary"),width=3)
    ]),

    html.Br(),

    dbc.Row([
        dbc.Col(dbc.Card(map_card, color="secondary")),
    ])

])


# ------------------------------------------------------------------ callback 영역 ------------------------------------------------------------------
# 현재 센서 버전 상태를 가져오는 함수
@app.callback(
    Output('boolean-switch-output-1', 'children'),
    Output('date_dropdown', 'options'),
    Input('my-boolean-switch', 'on')
)
def update_date(on):
    if on == False:
        status = "BLE 버전"
        date_list = show_date(on)
        return_date_list = []
        for factor in date_list:    
            return_date_list.append({"label": factor[ : 4] + "-" + factor[4 : 6] + "-" + factor[6 : ], "value": factor})
        return '현재 {} 입니다.'.format(status), return_date_list
        

    else:
        status = "LTE 버전"
        date_list = show_date(on)
        return_date_list = []
        for factor in date_list:
            return_date_list.append({"label": factor[ : 4] + "-" + factor[4 : 6] + "-" + factor[6 : ], "value": factor})     
        return '현재 {} 입니다.'.format(status), return_date_list




# phonelist call 
@app.callback(
    Output("phone_dropdown", "options"),
    Input("date_dropdown", "value"),
    State("my-boolean-switch", "on")
)
def update_phone(value, on):
    # dropdown에서 value값이 없다면
    if not value:
        # 아무 일도 일어나지 않도록 설정
        raise PreventUpdate
    # value값이 있다면
    else:
        phone_list = show_phonenum(value,on)
        return_phone_list = []
        for factor in phone_list:
            if len(factor) == 11:
                return_phone_list.append({"label": factor[ : 3] + "-" + factor[3 : 7] + "-" + factor[7 : ], "value": factor})
            else:
                return_phone_list.append({"label": factor, "value": factor})

    return return_phone_list

# phonelist+date 
@app.callback(
    Output("sensor_dropdown", "options"),
    Input("phone_dropdown", "value"), # 폰
    State('date_dropdown', 'value'), # 날짜
    State("my-boolean-switch", "on")  # 센서
)
def update_sensor(value1, value2, on):
    # dropdown에서 value값이 없다면
    if not value1:
        # 아무 일도 일어나지 않도록 설정
        raise PreventUpdate
    else:
        sensor_list = show_sensor(value1,value2, on)
        return_list = []
        for factor in sensor_list:
            return_list.append({"label": factor[-4:], "value": factor})
        
        return return_list




# 그래프 출력
# 조회 버튼을 누르면 그래프를 출력하는 함수
@app.callback(
    Output('first_graph', 'figure'),
    Output('second_graph', 'figure'),
    Output('third_graph', 'figure'),
    Output('fourth_graph', 'figure'),
    Output('fifth_graph', 'figure'),
    Output('output_card', 'children'),
    Output('announce', 'children'),
    Input('search_button', 'n_clicks'),
    State('date_dropdown', 'value'),    
    State('phone_dropdown', 'value'),
    State('sensor_dropdown', 'value'),
    State('my-boolean-switch', 'on'),
    prevent_initial_call=True
)
def update_graph(n_clicks, value1, value2, value3,on):
    os.system("sudo sysctl -w vm.drop_caches=3")

    if on == False: # 센서가 BLE 버전일 때
        # 선택한 라이더/날짜 경로
        data = Load_BLEData(value1, value2, value3)
        try:
            # data = cleaning_data(data)
            # 초당 그래프
            data_per_second = data['DATE'].value_counts().reset_index()
            data_per_second.columns = ['DATE', 'CNT']  # 'count' 대신 'CNT'로 변경
            data_per_second.sort_values("DATE", inplace=True)

            new_data_per = data_per_second['CNT'].value_counts().reset_index()
            new_data_per.columns = ['index', 'count']
            new_data_per.sort_values("index", inplace=True)

            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=new_data_per['index'], y=new_data_per['count'], name="data/second"))
            fig1.update_xaxes(range=[10, 50])
            
            numeric_columns = data.select_dtypes(include=['number']).columns
            mean_data = data.groupby('DATE', as_index=False)[numeric_columns].mean()       

            start_t = data["DATE"].iloc[0]
            end_t = data["DATE"].iloc[len(data)-1]

            # ACCEL 값 그래프
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["ACCEL_X"], mode='lines', name = "ACCEL_X"))
            fig2.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["ACCEL_Y"], mode='lines', name = "ACCEL_Y"))
            fig2.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["ACCEL_Z"], mode='lines', name = "ACCEL_Z"))
            fig2.update_xaxes(range = [start_t, end_t])

            # GYRO 값 그래프
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["GYRO_X"], mode='lines', name = "GYRO_X"))
            fig3.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["GYRO_Y"], mode='lines', name = "GYRO_Y"))
            fig3.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["GYRO_Z"], mode='lines', name = "GYRO_Z"))
            fig3.update_xaxes(range = [start_t, end_t])

            # ATTITUDE 값 그래프
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["ROLL"], mode='lines', name = "ROLL"))
            fig4.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["PITCH"], mode='lines', name = "PITCH"))
            fig4.update_xaxes(range = [start_t, end_t])
            
            # velocity 값 그래프
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["VEL"], mode='lines', name = "VEL"))
            fig5.update_xaxes(range = [start_t, end_t])
            output_card = dbc.CardBody()
            warn_a = " "            

            os.system("sudo sysctl -w vm.drop_caches=3")
            return fig1, fig2, fig3, fig4, fig5, output_card, warn_a
        except:
            fig1 = go.Figure()
            fig2 = go.Figure()
            fig3 = go.Figure()
            fig4 = go.Figure()
            fig5 = go.Figure()
            output_card = dbc.CardBody()
            warn_a = "데이터가 없습니다!" 
            os.system("sudo sysctl -w vm.drop_caches=3")
            return fig1, fig2, fig3, fig4, fig5, output_card, warn_a

    
    else: # 센서가 LTE 버전일 때
        data = Load_LTEData(value1, value2, value3)
        data_mod = data.copy()
        data_mod = data_mod[["TIME","DISTANCE"]]
        d_time = data_mod["TIME"].iloc[-1]
        d_dist = data_mod["DISTANCE"].iloc[-1]
        
        try:
            # data = cleaning_data(data)
            # 초당 그래프
            data_per_second = data['DATE'].value_counts().reset_index()
            data_per_second.columns = ['DATE', 'CNT']  # 'count' 대신 'CNT'로 변경
            data_per_second.sort_values("DATE", inplace=True)

            new_data_per = data_per_second['CNT'].value_counts().reset_index()
            new_data_per.columns = ['index', 'count']
            new_data_per.sort_values("index", inplace=True)

            fig1 = go.Figure()
            fig1.add_trace(go.Bar(x=new_data_per['index'], y=new_data_per['count'], name="data/second"))
            fig1.update_xaxes(range=[10, 50])
            
            numeric_columns = data.select_dtypes(include=['number']).columns
            mean_data = data.groupby('DATE', as_index=False)[numeric_columns].mean()       

            start_t = data["DATE"].iloc[0]
            end_t = data["DATE"].iloc[len(data)-1]

            # ACCEL 값 그래프
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["ACCEL_X"], mode='lines', name = "ACCEL_X"))
            fig2.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["ACCEL_Y"], mode='lines', name = "ACCEL_Y"))
            fig2.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["ACCEL_Z"], mode='lines', name = "ACCEL_Z"))
            fig2.update_xaxes(range = [start_t, end_t])

            # GYRO 값 그래프
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["GYRO_X"], mode='lines', name = "GYRO_X"))
            fig3.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["GYRO_Y"], mode='lines', name = "GYRO_Y"))
            fig3.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["GYRO_Z"], mode='lines', name = "GYRO_Z"))
            fig3.update_xaxes(range = [start_t, end_t])

            # ATTITUDE 값 그래프
            fig4 = go.Figure()
            fig4.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["ROLL"], mode='lines', name = "ROLL"))
            fig4.add_trace(go.Scatter(x = mean_data["DATE"], y = mean_data["PITCH"], mode='lines', name = "PITCH"))
            fig4.update_xaxes(range = [start_t, end_t])
            
            # velocity 값 그래프
            fig5 = go.Figure()
            fig5.add_trace(go.Scatter(x = data["DATE"], y = data["VEL"], mode='lines', name = "VEL"))
            fig5.update_xaxes(range = [start_t, end_t])
            
            
            time_card = dbc.Card(dbc.CardBody( [ html.H5("TIME", className="card-title"), html.H3(f"이동 시간 : {d_time/1000} s"), html.H3(f" 분 : {round(d_time/60000, 2)}")] ))
            distance_card = dbc.Card(dbc.CardBody( [ html.H5("DISTANCE", className="card-title"), html.H3(f"이동 거리 : {d_dist} m") ,html.H3(f" KM : {d_dist/1000} ") ] ))
            output_card = dbc.Row([dbc.Col(time_card, width=6), dbc.Col(distance_card, width=6),])
            warn_a = " "
            os.system("sudo sysctl -w vm.drop_caches=3")
            return fig1, fig2, fig3, fig4, fig5, output_card, warn_a
        except:
            fig1 = go.Figure()
            fig2 = go.Figure()
            fig3 = go.Figure()
            fig4 = go.Figure()
            fig5 = go.Figure()
            output_card = dbc.CardBody()
            warn_a = "데이터가 없습니다!" 
            os.system("sudo sysctl -w vm.drop_caches=3")
            return fig1, fig2, fig3, fig4, fig5, output_card, warn_a


# 지도 출력
@app.callback(
    Output('map_card', 'children'),
    Output('map_card', 'center'),
    Input('map_button', 'n_clicks'), 
    State('date_dropdown', 'value'),    
    State('phone_dropdown', 'value'),
    State('sensor_dropdown', 'value'),
    State('my-boolean-switch', 'on'),
    prevent_initial_call=True
)
def print_map(n_clicks, value1, value2,value3, on):
    os.system("sudo sysctl -w vm.drop_caches=3")

    
    if on == False: # 센서가 BLE 버전일 때
        # 선택한 라이더/날짜 경로
        data = Load_BLEData(value1, value2, value3)
    else: # 센서가 LTE 버전일 때
        data = Load_LTEData(value1, value2, value3)

    gps = data.drop_duplicates(["LAT", "LON"])
    gps.reset_index(inplace = True, drop = True)

    center_list = [gps["LAT"].loc[len(gps) // 2], gps["LON"].loc[len(gps) // 2]]
    
    gps_error = []
    sensor_error = []
    sensor_good = []
    
    for i in range(len(gps) - 1):
        # if (abs(gps["LAT"].loc[i + 1] - gps["LAT"].loc[i]) >= 0.15) & (abs(gps["LON"].loc[i + 1] - gps["LON"].loc[i]) >= 0.15):
        if (gps["LAT"].loc[i + 1] - gps["LAT"].loc[i])**2 + (gps["LON"].loc[i + 1] - gps["LON"].loc[i])**2 >= (0.003)**2:
            gps_error.append(dl.CircleMarker(center = [gps["LAT"].loc[i], gps["LON"].loc[i]], color = 'red', fillColor = "red", radius = 2))
        else:
            try:
                if (gps["ACCEL_X"].loc[i] ==0) & (gps["ACCEL_Y"].loc[i] ==0) & (gps["ACCEL_Z"].loc[i] ==0):
                    sensor_error.append(dl.CircleMarker(center = [gps["LAT"].loc[i], gps["LON"].loc[i]], color = 'orange', fillColor = "orange", radius = 2))
                else:
                    sensor_good.append(dl.CircleMarker(center = [gps["LAT"].loc[i], gps["LON"].loc[i]], color = 'green', fillColor = "green", radius = 2))
            except: 
                sensor_good.append(dl.CircleMarker(center = [gps["LAT"].iloc[i], gps["LON"].loc[i]], color = 'green', fillColor = 'green', radius = 2))

    component_list = [
        dl.LayersControl([dl.BaseLayer(dl.TileLayer(url="https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png?api_key=93889be7-805e-4f44-9874-773f0117da64"),
                    name="Outdoors",
                    checked=True,),
                dl.Overlay(dl.LayerGroup(gps_error), name="GPS jump", checked=True),
                dl.Overlay(dl.LayerGroup(sensor_error), name="센서 미연결", checked=True),
                dl.Overlay(dl.LayerGroup(sensor_good), name="센서 연결", checked=True),
            ]
        )
    ]
    os.system("sudo sysctl -w vm.drop_caches=3")
    return component_list, center_list


if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port='8050')




