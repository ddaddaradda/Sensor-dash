"""
데이터 처리 및 정제 함수 모듈
센서 데이터를 정제하고 변환하는 공통 함수들을 제공합니다.
"""
import numpy as np
import pandas as pd
from datetime import datetime
import pytz


# 로컬 타임존 설정
local_tz = pytz.timezone('Asia/Seoul')


def cleaning_data(data: pd.DataFrame) -> pd.DataFrame:
    """
    센서 데이터를 정제합니다.

    DATE 컬럼의 차분값이 32400000000000 또는 32401000000000인 인덱스를 제거합니다.
    이는 9시간(32400초 = 9시간 * 3600초/시간 * 1000밀리초/초 * 1000000나노초/밀리초)의
    시간차이를 나타내며, 타임존 관련 이상값을 제거하기 위함입니다.

    Args:
        data (pd.DataFrame): 정제할 데이터프레임 (DATE 컬럼 필수)

    Returns:
        pd.DataFrame: 정제된 데이터프레임
    """
    # np.where 함수를 이용해 DATE 컬럼을 차분해서 값이 32400000000000인 인덱스만 리스트 형태로 리턴받는다.
    over_9_idx_list = list(
        np.where(
            (np.diff(data["DATE"]).astype(np.int64) == 32400000000000) |
            (np.diff(data["DATE"]).astype(np.int64) == 32401000000000)
        )[0]
    )

    while True:
        if len(over_9_idx_list) != 0:
            data = data.drop(over_9_idx_list)
            data.reset_index(inplace=True, drop=True)
            over_9_idx_list = list(
                np.where(
                    (np.diff(data["DATE"]).astype(np.int64) == 32400000000000) |
                    (np.diff(data["DATE"]).astype(np.int64) == 32401000000000)
                )[0]
            )
        elif len(over_9_idx_list) == 0:
            break

    data.reset_index(inplace=True, drop=True)

    return data


def convert_timestamp_to_datetime(timestamp: int, timezone: pytz.timezone = local_tz) -> str:
    """
    밀리초 단위 타임스탬프를 로컬 시간대의 datetime 문자열로 변환합니다.

    Args:
        timestamp (int): 밀리초 단위 타임스탬프
        timezone (pytz.timezone): 변환할 시간대 (기본값: Asia/Seoul)

    Returns:
        str: 'YYYY-MM-DD HH:MM:SS' 형식의 datetime 문자열
    """
    return datetime.fromtimestamp(timestamp / 1000, tz=timezone).strftime('%Y-%m-%d %H:%M:%S')


def process_raw_data(df: pd.DataFrame, timezone: pytz.timezone = local_tz) -> pd.DataFrame:
    """
    원시 센서 데이터를 처리합니다.

    - 시간 컬럼을 밀리초 타임스탬프에서 datetime 문자열로 변환
    - 컬럼명을 표준 형식으로 변경
    - 인덱스 리셋
    - datetime 타입으로 변환
    - 중복 제거

    Args:
        df (pd.DataFrame): 처리할 원시 데이터프레임
        timezone (pytz.timezone): 시간대 (기본값: Asia/Seoul)

    Returns:
        pd.DataFrame: 처리된 데이터프레임
    """
    # 시간 정렬
    df.sort_values(by=['time'], ascending=True, inplace=True)

    # 타임스탬프를 datetime 문자열로 변환
    df['time'] = df['time'].apply(
        lambda x: datetime.fromtimestamp(x / 1000, tz=timezone).strftime('%Y-%m-%d %H:%M:%S')
    )

    # 컬럼명 표준화
    df.columns = [
        "DATE", "senor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
        "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VEL", "ALT", "HEAD"
    ]

    # 인덱스 리셋
    df = df.reset_index(drop=True)

    # DATE를 datetime 타입으로 변환
    df["DATE"] = pd.to_datetime(df["DATE"])

    # 중복 제거
    df.drop_duplicates(subset='DATE', inplace=True)

    return df
