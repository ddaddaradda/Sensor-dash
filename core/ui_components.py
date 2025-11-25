"""
UI 컴포넌트 및 레이아웃 모듈
Dash 앱의 모든 UI 컴포넌트와 레이아웃을 정의합니다.
"""
import dash
import dash_bootstrap_components as dbc
import dash_auth
from dash import dcc, html
import dash_daq as daq
import dash_leaflet as dl


# 색상 정보 팝오버 텍스트
POPOVER_CHILDREN = "초록(센서 연결 O), 주황(센서 연결 X), 빨강(GPS 오류)"


def create_control_card(data_source_name: str = "Data") -> dbc.CardBody:
    """
    날짜, 전화번호, 센서 선택을 위한 컨트롤 카드를 생성합니다.

    Args:
        data_source_name (str): 데이터 소스 이름 (예: "DocumentDB", "S3")

    Returns:
        dbc.CardBody: 컨트롤 카드 컴포넌트
    """
    return dbc.CardBody([
        html.H5(f"{data_source_name} data reading", className="card-title"),
        html.P("확인하고 싶은 날짜, 전화번호, 센서를 순차적으로 선택 후 조회 버튼 클릭하세요."),

        # 날짜(collection) 목록
        dcc.Dropdown(
            placeholder="날짜",
            id='date_dropdown',
            style={"width": "5vw", "color": "black"}
        ),

        # 전화 목록
        dcc.Dropdown(
            placeholder='전화번호',
            style={
                "width": "7.5vw",
                "color": "black",
                "position": "relative",
                "left": "2.7vw",
                "top": "-1.38vh"
            },
            id="phone_dropdown"
        ),

        # 센서 목록
        dcc.Dropdown(
            placeholder='센서 뒤 4자리',
            style={
                "width": "10vw",
                "position": "relative",
                "left": "6.6vw",
                "top": "-2.78vh",
                "color": "black"
            },
            id="sensor_dropdown"
        ),

        # 조회 버튼
        dbc.Button(
            "조회",
            color='warning',
            size="lg",
            id="search_button",
            n_clicks=0,
            className="me-1",
            style={
                "position": "relative",
                "left": "24.5vw",
                "top": "-8.7vh",
                "width": "100px"
            }
        ),

        html.H3(
            id="announce",
            style={
                "position": "relative",
                "left": "0.2vw",
                "top": "-7vh"
            }
        )
    ], style={"height": "20vh"})


def create_sensor_switch_card() -> dbc.CardBody:
    """
    센서 버전(BLE/LTE) 스위치 카드를 생성합니다.

    Returns:
        dbc.CardBody: 센서 스위치 카드 컴포넌트
    """
    return dbc.CardBody([
        html.H5("센서", className="card-title"),
        html.Div(id='boolean-switch-output-1'),
        html.Br(),
        daq.BooleanSwitch(id='my-boolean-switch', on=False),
    ], style={"height": "20vh"})


def create_graph_card(title: str, graph_id: str) -> dbc.CardBody:
    """
    그래프 카드를 생성합니다.

    Args:
        title (str): 그래프 제목
        graph_id (str): 그래프 ID

    Returns:
        dbc.CardBody: 그래프 카드 컴포넌트
    """
    return dbc.CardBody([
        html.H5(title, className="card-title"),
        dcc.Graph(id=graph_id, style={"height": "40vh"})
    ], style={"height": "50vh"})


def create_output_card() -> dbc.Card:
    """
    이동 시간과 거리를 표시하는 출력 카드를 생성합니다.

    Returns:
        dbc.Card: 출력 카드 컴포넌트
    """
    return dbc.Card([
        dbc.CardHeader("이동 시간, 이동 거리"),
        dbc.CardBody(id="output_card")
    ], style={"height": "30vh"})


def create_map_card() -> dbc.CardBody:
    """
    지도 카드를 생성합니다.

    Returns:
        dbc.CardBody: 지도 카드 컴포넌트
    """
    return dbc.CardBody([
        html.H5("지도", className="card-title"),
        dbc.Button(
            "지도 출력",
            color="primary",
            size="sm",
            id="map_button",
            n_clicks=0,
            style={
                "position": "relative",
                "left": "2.5vw",
                "top": "-3vh"
            }
        ),
        dbc.Button(
            "색상 정보",
            id="hover-target",
            color="danger",
            className="me-1",
            n_clicks=0,
            size="sm",
            style={
                "position": "relative",
                "left": "3vw",
                "top": "-3vh"
            }
        ),
        dbc.Popover(
            POPOVER_CHILDREN,
            target="hover-target",
            body=True,
            trigger="hover"
        ),
        dl.Map(
            [dl.TileLayer(
                url="https://tiles.stadiamaps.com/tiles/outdoors/{z}/{x}/{y}{r}.png?api_key=93889be7-805e-4f44-9874-773f0117da64"
            )],
            center=[37.523254, 126.923528],
            zoom=12,
            id="map_card",
            style={"height": "85vh"}
        )
    ], style={"height": "100vh"})


def create_layout(data_source_name: str = "Data") -> html.Div:
    """
    전체 앱 레이아웃을 생성합니다.

    Args:
        data_source_name (str): 데이터 소스 이름 (예: "DocumentDB", "S3")

    Returns:
        html.Div: 전체 레이아웃 컴포넌트
    """
    # 컴포넌트 생성
    control_card = create_control_card(data_source_name)
    sensor_card = create_sensor_switch_card()

    first_graph = create_graph_card("평균 초당 데이터 그래프", "first_graph")
    second_graph = create_graph_card("평균 ACCEL 그래프", "second_graph")
    third_graph = create_graph_card("평균 GYRO 그래프", "third_graph")
    fourth_graph = create_graph_card("평균 ATTITUDE 그래프", "fourth_graph")
    fifth_graph = create_graph_card("평균 VEL 그래프", "fifth_graph")

    output_card = create_output_card()
    map_card = create_map_card()

    # 레이아웃 구성
    return html.Div(children=[
        dbc.Row([
            dbc.Col(dbc.Card(control_card, color="secondary", style={"z-index": "10"}), width=4),
            dbc.Col(dbc.Card(sensor_card, color="secondary", style={"z-index": "10"}), width=2)
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
            dbc.Col(dbc.Card(fifth_graph, color="secondary"), width=6),
            dbc.Col(dbc.Card(output_card, color="secondary"), width=3)
        ]),

        html.Br(),

        dbc.Row([
            dbc.Col(dbc.Card(map_card, color="secondary")),
        ])
    ])


def create_app(loader, app_name: str = "Sensor Dashboard", port: int = 8050):
    """
    Dash 애플리케이션을 생성하고 설정합니다.

    Args:
        loader (BaseLoader): 데이터 로더 인스턴스
        app_name (str): 애플리케이션 이름
        port (int): 서버 포트 번호

    Returns:
        dash.Dash: 설정된 Dash 애플리케이션
    """
    from core.callbacks import register_callbacks
    from config import ConfigDB

    # 로그인 정보 (환경 변수에서 로드)
    VALID_USERNAME_PASSWORD_PAIRS = {
        ConfigDB.DASH_AUTH["username"]: ConfigDB.DASH_AUTH["password"]
    }

    # Dash 앱 생성
    app = dash.Dash(external_stylesheets=[dbc.themes.QUARTZ])
    app.title = app_name

    # Secret key 설정 (세션 관리용)
    import secrets
    app.server.secret_key = secrets.token_hex(16)

    # 인증 설정
    auth = dash_auth.BasicAuth(app, VALID_USERNAME_PASSWORD_PAIRS)

    # 레이아웃 설정
    data_source_name = loader.get_data_source_name()
    app.layout = create_layout(data_source_name)

    # 콜백 등록
    register_callbacks(app, loader)

    return app
