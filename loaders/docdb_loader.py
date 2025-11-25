"""
DocumentDB 데이터 로더
AWS DocumentDB에서 센서 데이터를 로드합니다.
"""
from typing import List
import pandas as pd
from pymongo import MongoClient
from datetime import datetime

from loaders.base import BaseLoader
from core.data_processor import process_raw_data, local_tz
from config import ConfigDB


class DocDBLoader(BaseLoader):
    """
    DocumentDB 데이터 로더 클래스

    AWS DocumentDB에 연결하여 BLE 및 LTE 센서 데이터를 로드합니다.
    """

    def __init__(self):
        """
        DocDBLoader를 초기화합니다.
        DocumentDB 연결을 설정하고 BLE, LTE 데이터베이스 참조를 생성합니다.
        """
        # MongoDB 설정
        self.mongo_config_ble = ConfigDB.MONGO["BLE"]
        self.mongo_config_lte = ConfigDB.MONGO["LTE"]

        # SSL 인증서 경로
        self.key_path = ConfigDB.MONGO_SSL_CERT_PATH

        # BLE MongoDB 클라이언트
        self.client_ble = MongoClient(
            self.mongo_config_ble["URI"],
            tls=True,
            tlsCAFile=self.key_path
        )
        self.monDB_ble = self.client_ble[self.mongo_config_ble["DB"]]

        # LTE MongoDB 클라이언트
        self.client_lte = MongoClient(
            self.mongo_config_lte["URI"],
            tls=True,
            tlsCAFile=self.key_path
        )
        self.monDB_lte = self.client_lte[self.mongo_config_lte["DB"]]

    def load_ble_data(self, date: str, phone: str, sensor: str) -> pd.DataFrame:
        """
        BLE 센서 데이터를 DocumentDB에서 로드합니다.

        Args:
            date (str): 날짜 (collection 이름)
            phone (str): 전화번호
            sensor (str): 센서 ID

        Returns:
            pd.DataFrame: BLE 센서 데이터
        """
        projection = {
            "_id": 0, "time": 1, "sensor_id": 1,
            "ACCEL_X": 1, "ACCEL_Y": 1, "ACCEL_Z": 1,
            "GYRO_X": 1, "GYRO_Y": 1, "GYRO_Z": 1,
            "PITCH": 1, "ROLL": 1,
            "LAT": 1, "LON": 1,
            "VELOCITY": 1, "ALTITUDE": 1, "BEARING": 1
        }

        result = self.monDB_ble[date].find(
            {"phone_num": phone, "sensor_id": sensor},
            projection
        ).batch_size(10000)

        df = pd.DataFrame(result)
        raw_data = df[[
            "time", "sensor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
            "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VELOCITY", "ALTITUDE", "BEARING"
        ]]

        # 데이터 처리
        raw_data = process_raw_data(raw_data, local_tz)

        return raw_data

    def load_lte_data(self, date: str, phone: str, sensor: str) -> pd.DataFrame:
        """
        LTE 센서 데이터를 DocumentDB에서 로드합니다.

        Args:
            date (str): 날짜 (collection 이름)
            phone (str): 전화번호
            sensor (str): 센서 ID

        Returns:
            pd.DataFrame: LTE 센서 데이터
        """
        projection = {
            "_id": 0, "time": 1, "sensor_id": 1,
            "ACCEL_X": 1, "ACCEL_Y": 1, "ACCEL_Z": 1,
            "GYRO_X": 1, "GYRO_Y": 1, "GYRO_Z": 1,
            "PITCH": 1, "ROLL": 1,
            "LAT": 1, "LON": 1,
            "VELOCITY": 1, "ALTITUDE": 1, "BEARING": 1,
            "TIME": 1, "DISTANCE": 1
        }

        result = self.monDB_lte[date].find(
            {"phone_num": phone, "sensor_id": sensor},
            projection
        ).batch_size(10000)

        df = pd.DataFrame(result)
        raw_data = df[[
            "time", "sensor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
            "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VELOCITY", "ALTITUDE", "BEARING", "TIME", "DISTANCE"
        ]]

        # 시간 정렬
        raw_data.sort_values(by=['time'], ascending=True, inplace=True)
        raw_data['time'] = raw_data['time'].apply(
            lambda x: datetime.fromtimestamp(x / 1000, tz=local_tz).strftime('%Y-%m-%d %H:%M:%S')
        )

        # 컬럼명 표준화
        raw_data.columns = [
            "DATE", "senor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
            "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VEL", "ALT", "HEAD", "TIME", "DISTANCE"
        ]

        raw_data["DATE"] = pd.to_datetime(raw_data["DATE"])
        raw_data.drop_duplicates(subset='DATE', inplace=True)

        return raw_data

    def show_date(self, is_lte: bool = False) -> List[str]:
        """
        사용 가능한 날짜 목록을 반환합니다.

        Args:
            is_lte (bool): True면 LTE, False면 BLE (기본값: False)

        Returns:
            List[str]: 날짜 문자열 리스트
        """
        db = self.monDB_lte if is_lte else self.monDB_ble
        date_list = db.list_collection_names()
        return date_list

    def show_phonenum(self, date: str, is_lte: bool = False) -> List[str]:
        """
        특정 날짜에 사용 가능한 전화번호 목록을 반환합니다.

        Args:
            date (str): 날짜
            is_lte (bool): True면 LTE, False면 BLE (기본값: False)

        Returns:
            List[str]: 전화번호 리스트
        """
        db = self.monDB_lte if is_lte else self.monDB_ble
        col = db[date]
        field_name = 'phone_num'
        phone_list = col.distinct(field_name)
        return phone_list

    def show_sensor(self, date: str, phone: str, is_lte: bool = False) -> List[str]:
        """
        특정 날짜와 전화번호에 대해 사용 가능한 센서 ID 목록을 반환합니다.

        Args:
            date (str): 날짜
            phone (str): 전화번호
            is_lte (bool): True면 LTE, False면 BLE (기본값: False)

        Returns:
            List[str]: 센서 ID 리스트
        """
        db = self.monDB_lte if is_lte else self.monDB_ble
        query = {"phone_num": phone}
        col = db[date]
        sensor_ids = col.distinct("sensor_id", query)
        return sensor_ids

    def close(self):
        """
        MongoDB 연결을 종료합니다.
        """
        self.client_ble.close()
        self.client_lte.close()
