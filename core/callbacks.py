"""
Dash 콜백 함수 모듈
모든 인터랙티브 콜백 함수들을 정의하고 등록합니다.
"""
import os
import numpy as np
import pandas as pd
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import plotly.graph_objects as go
from dash import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import html

from core.data_processor import cleaning_data


def register_callbacks(app, loader):
    """
    모든 콜백 함수를 앱에 등록합니다.

    Args:
        app (dash.Dash): Dash 애플리케이션 인스턴스
        loader (BaseLoader): 데이터 로더 인스턴스
    """

    # 현재 센서 버전 상태를 가져오는 함수
    @app.callback(
        Output('boolean-switch-output-1', 'children'),
        Output('date_dropdown', 'options'),
        Input('my-boolean-switch', 'on')
    )
    def update_date(on):
        """
        센서 스위치 상태에 따라 날짜 목록을 업데이트합니다.

        Args:
            on (bool): 스위치 상태 (False: BLE, True: LTE)

        Returns:
            tuple: (상태 텍스트, 날짜 옵션 리스트)
        """
        if on == False:
            status = "BLE 버전"
            date_list = loader.show_date(is_lte=False)
            return_date_list = []
            for factor in date_list:
                return_date_list.append({
                    "label": factor[:4] + "-" + factor[4:6] + "-" + factor[6:],
                    "value": factor
                })
            return '현재 {} 입니다.'.format(status), return_date_list

        else:
            status = "LTE 버전"
            date_list = loader.show_date(is_lte=True)
            return_date_list = []
            for factor in date_list:
                return_date_list.append({
                    "label": factor[:4] + "-" + factor[4:6] + "-" + factor[6:],
                    "value": factor
                })
            return '현재 {} 입니다.'.format(status), return_date_list

    # phonelist call
    @app.callback(
        Output("phone_dropdown", "options"),
        Input("date_dropdown", "value"),
        State("my-boolean-switch", "on")
    )
    def update_phone(value, on):
        """
        선택한 날짜에 따라 전화번호 목록을 업데이트합니다.

        Args:
            value (str): 선택한 날짜
            on (bool): 센서 스위치 상태

        Returns:
            list: 전화번호 옵션 리스트
        """
        # dropdown에서 value값이 없다면
        if not value:
            # 아무 일도 일어나지 않도록 설정
            raise PreventUpdate
        # value값이 있다면
        else:
            phone_list = loader.show_phonenum(value, is_lte=on)
            return_phone_list = []
            for factor in phone_list:
                if len(factor) == 11:
                    return_phone_list.append({
                        "label": factor[:3] + "-" + factor[3:7] + "-" + factor[7:],
                        "value": factor
                    })
                else:
                    return_phone_list.append({
                        "label": factor,
                        "value": factor
                    })

        return return_phone_list

    # phonelist+date
    @app.callback(
        Output("sensor_dropdown", "options"),
        Input("phone_dropdown", "value"),  # 폰
        State('date_dropdown', 'value'),  # 날짜
        State("my-boolean-switch", "on")  # 센서
    )
    def update_sensor(value1, value2, on):
        """
        선택한 날짜와 전화번호에 따라 센서 목록을 업데이트합니다.

        Args:
            value1 (str): 선택한 전화번호
            value2 (str): 선택한 날짜
            on (bool): 센서 스위치 상태

        Returns:
            list: 센서 옵션 리스트
        """
        # dropdown에서 value값이 없다면
        if not value1:
            # 아무 일도 일어나지 않도록 설정
            raise PreventUpdate
        else:
            sensor_list = loader.show_sensor(value2, value1, is_lte=on)
            return_list = []
            for factor in sensor_list:
                return_list.append({
                    "label": factor[-4:],
                    "value": factor
                })

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
    def update_graph(n_clicks, value1, value2, value3, on):
        """
        선택한 조건에 따라 그래프를 업데이트합니다.

        Args:
            n_clicks (int): 조회 버튼 클릭 횟수
            value1 (str): 선택한 날짜
            value2 (str): 선택한 전화번호
            value3 (str): 선택한 센서
            on (bool): 센서 스위치 상태 (False: BLE, True: LTE)

        Returns:
            tuple: (fig1, fig2, fig3, fig4, fig5, output_card, warn_a)
        """
        os.system("sudo sysctl -w vm.drop_caches=3")

        if on == False:  # 센서가 BLE 버전일 때
            # 선택한 라이더/날짜 경로
            data = loader.load_ble_data(value1, value2, value3)
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
                end_t = data["DATE"].iloc[len(data) - 1]

                # ACCEL 값 그래프
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["ACCEL_X"], mode='lines', name="ACCEL_X"))
                fig2.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["ACCEL_Y"], mode='lines', name="ACCEL_Y"))
                fig2.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["ACCEL_Z"], mode='lines', name="ACCEL_Z"))
                fig2.update_xaxes(range=[start_t, end_t])

                # GYRO 값 그래프
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["GYRO_X"], mode='lines', name="GYRO_X"))
                fig3.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["GYRO_Y"], mode='lines', name="GYRO_Y"))
                fig3.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["GYRO_Z"], mode='lines', name="GYRO_Z"))
                fig3.update_xaxes(range=[start_t, end_t])

                # ATTITUDE 값 그래프
                fig4 = go.Figure()
                fig4.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["ROLL"], mode='lines', name="ROLL"))
                fig4.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["PITCH"], mode='lines', name="PITCH"))
                fig4.update_xaxes(range=[start_t, end_t])

                # velocity 값 그래프
                fig5 = go.Figure()
                fig5.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["VEL"], mode='lines', name="VEL"))
                fig5.update_xaxes(range=[start_t, end_t])
                output_card = dbc.CardBody()
                warn_a = " "

                os.system("sudo sysctl -w vm.drop_caches=3")
                return fig1, fig2, fig3, fig4, fig5, output_card, warn_a
            except Exception as e:
                print(f"BLE 데이터 로딩 실패: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                fig1 = go.Figure()
                fig2 = go.Figure()
                fig3 = go.Figure()
                fig4 = go.Figure()
                fig5 = go.Figure()
                output_card = dbc.CardBody()
                warn_a = f"데이터가 없습니다! ({type(e).__name__})"
                os.system("sudo sysctl -w vm.drop_caches=3")
                return fig1, fig2, fig3, fig4, fig5, output_card, warn_a

        else:  # 센서가 LTE 버전일 때
            data = loader.load_lte_data(value1, value2, value3)
            data_mod = data.copy()
            data_mod = data_mod[["TIME", "DISTANCE"]]
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
                end_t = data["DATE"].iloc[len(data) - 1]

                # ACCEL 값 그래프
                fig2 = go.Figure()
                fig2.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["ACCEL_X"], mode='lines', name="ACCEL_X"))
                fig2.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["ACCEL_Y"], mode='lines', name="ACCEL_Y"))
                fig2.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["ACCEL_Z"], mode='lines', name="ACCEL_Z"))
                fig2.update_xaxes(range=[start_t, end_t])

                # GYRO 값 그래프
                fig3 = go.Figure()
                fig3.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["GYRO_X"], mode='lines', name="GYRO_X"))
                fig3.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["GYRO_Y"], mode='lines', name="GYRO_Y"))
                fig3.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["GYRO_Z"], mode='lines', name="GYRO_Z"))
                fig3.update_xaxes(range=[start_t, end_t])

                # ATTITUDE 값 그래프
                fig4 = go.Figure()
                fig4.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["ROLL"], mode='lines', name="ROLL"))
                fig4.add_trace(go.Scatter(x=mean_data["DATE"], y=mean_data["PITCH"], mode='lines', name="PITCH"))
                fig4.update_xaxes(range=[start_t, end_t])

                # velocity 값 그래프
                fig5 = go.Figure()
                fig5.add_trace(go.Scatter(x=data["DATE"], y=data["VEL"], mode='lines', name="VEL"))
                fig5.update_xaxes(range=[start_t, end_t])

                time_card = dbc.Card(dbc.CardBody([
                    html.H5("TIME", className="card-title"),
                    html.H3(f"이동 시간 : {d_time / 1000} s"),
                    html.H3(f" 분 : {round(d_time / 60000, 2)}")
                ]))
                distance_card = dbc.Card(dbc.CardBody([
                    html.H5("DISTANCE", className="card-title"),
                    html.H3(f"이동 거리 : {d_dist} m"),
                    html.H3(f" KM : {d_dist / 1000} ")
                ]))
                output_card = dbc.Row([
                    dbc.Col(time_card, width=6),
                    dbc.Col(distance_card, width=6),
                ])
                warn_a = " "
                os.system("sudo sysctl -w vm.drop_caches=3")
                return fig1, fig2, fig3, fig4, fig5, output_card, warn_a
            except Exception as e:
                print(f"LTE 데이터 로딩 실패: {type(e).__name__}: {str(e)}")
                import traceback
                traceback.print_exc()
                fig1 = go.Figure()
                fig2 = go.Figure()
                fig3 = go.Figure()
                fig4 = go.Figure()
                fig5 = go.Figure()
                output_card = dbc.CardBody()
                warn_a = f"데이터가 없습니다! ({type(e).__name__})"
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
    def print_map(n_clicks, value1, value2, value3, on):
        """
        지도를 출력합니다.

        Args:
            n_clicks (int): 지도 출력 버튼 클릭 횟수
            value1 (str): 선택한 날짜
            value2 (str): 선택한 전화번호
            value3 (str): 선택한 센서
            on (bool): 센서 스위치 상태

        Returns:
            tuple: (지도 컴포넌트 리스트, 지도 중심 좌표)
        """
        os.system("sudo sysctl -w vm.drop_caches=3")

        if on == False:  # 센서가 BLE 버전일 때
            # 선택한 라이더/날짜 경로
            data = loader.load_ble_data(value1, value2, value3)
        else:  # 센서가 LTE 버전일 때
            data = loader.load_lte_data(value1, value2, value3)

        gps = data.drop_duplicates(["LAT", "LON"])
        gps.reset_index(inplace=True, drop=True)

        center_list = [gps["LAT"].loc[len(gps) // 2], gps["LON"].loc[len(gps) // 2]]

        gps_error = []
        sensor_error = []
        sensor_good = []

        for i in range(len(gps) - 1):
            # if (abs(gps["LAT"].loc[i + 1] - gps["LAT"].loc[i]) >= 0.15) & (abs(gps["LON"].loc[i + 1] - gps["LON"].loc[i]) >= 0.15):
            if (gps["LAT"].loc[i + 1] - gps["LAT"].loc[i]) ** 2 + (gps["LON"].loc[i + 1] - gps["LON"].loc[i]) ** 2 >= (
                    0.003) ** 2:
                gps_error.append(
                    dl.CircleMarker(center=[gps["LAT"].loc[i], gps["LON"].loc[i]], color='red', fillColor="red",
                                    radius=2))
            else:
                try:
                    if (gps["ACCEL_X"].loc[i] == 0) & (gps["ACCEL_Y"].loc[i] == 0) & (gps["ACCEL_Z"].loc[i] == 0):
                        sensor_error.append(
                            dl.CircleMarker(center=[gps["LAT"].loc[i], gps["LON"].loc[i]], color='orange',
                                            fillColor="orange", radius=2))
                    else:
                        sensor_good.append(
                            dl.CircleMarker(center=[gps["LAT"].loc[i], gps["LON"].loc[i]], color='green',
                                            fillColor="green", radius=2))
                except:
                    sensor_good.append(
                        dl.CircleMarker(center=[gps["LAT"].iloc[i], gps["LON"].loc[i]], color='green',
                                        fillColor='green', radius=2))

        component_list = [
            dl.LayersControl([
                dl.BaseLayer(dl.TileLayer(
                    url="https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png?api_key=93889be7-805e-4f44-9874-773f0117da64"),
                    name="Outdoors",
                    checked=True, ),
                dl.Overlay(dl.LayerGroup(gps_error), name="GPS jump", checked=True),
                dl.Overlay(dl.LayerGroup(sensor_error), name="센서 미연결", checked=True),
                dl.Overlay(dl.LayerGroup(sensor_good), name="센서 연결", checked=True),
            ]
            )
        ]
        os.system("sudo sysctl -w vm.drop_caches=3")
        return component_list, center_list
