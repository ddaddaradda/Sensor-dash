"""
Base Loader 추상 클래스
모든 데이터 로더가 구현해야 하는 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from typing import List, Any
import pandas as pd


class BaseLoader(ABC):
    """
    데이터 로더의 추상 베이스 클래스

    모든 데이터 소스 로더(DocumentDB, S3 등)는 이 클래스를 상속받아
    필수 메서드들을 구현해야 합니다.
    """

    @abstractmethod
    def load_ble_data(self, date: str, phone: str, sensor: str) -> pd.DataFrame:
        """
        BLE 센서 데이터를 로드합니다.

        Args:
            date (str): 날짜 (예: '2023-01-01')
            phone (str): 전화번호
            sensor (str): 센서 ID

        Returns:
            pd.DataFrame: BLE 센서 데이터
                컬럼: DATE, sensor_id, ACCEL_X, ACCEL_Y, ACCEL_Z, GYRO_X, GYRO_Y, GYRO_Z,
                      PITCH, ROLL, LAT, LON, VEL, ALT, HEAD
        """
        pass

    @abstractmethod
    def load_lte_data(self, date: str, phone: str, sensor: str) -> pd.DataFrame:
        """
        LTE 센서 데이터를 로드합니다.

        Args:
            date (str): 날짜 (예: '2023-01-01')
            phone (str): 전화번호
            sensor (str): 센서 ID

        Returns:
            pd.DataFrame: LTE 센서 데이터
                컬럼: DATE, sensor_id, ACCEL_X, ACCEL_Y, ACCEL_Z, GYRO_X, GYRO_Y, GYRO_Z,
                      PITCH, ROLL, LAT, LON, VEL, ALT, HEAD
        """
        pass

    @abstractmethod
    def show_date(self, is_lte: bool = False) -> List[str]:
        """
        사용 가능한 날짜 목록을 반환합니다.

        Args:
            is_lte (bool): True면 LTE, False면 BLE (기본값: False)

        Returns:
            List[str]: 날짜 문자열 리스트 (예: ['2023-01-01', '2023-01-02'])
        """
        pass

    @abstractmethod
    def show_phonenum(self, date: str, is_lte: bool = False) -> List[str]:
        """
        특정 날짜에 사용 가능한 전화번호 목록을 반환합니다.

        Args:
            date (str): 날짜 (예: '2023-01-01')
            is_lte (bool): True면 LTE, False면 BLE (기본값: False)

        Returns:
            List[str]: 전화번호 리스트
        """
        pass

    @abstractmethod
    def show_sensor(self, date: str, phone: str, is_lte: bool = False) -> List[str]:
        """
        특정 날짜와 전화번호에 대해 사용 가능한 센서 ID 목록을 반환합니다.

        Args:
            date (str): 날짜 (예: '2023-01-01')
            phone (str): 전화번호
            is_lte (bool): True면 LTE, False면 BLE (기본값: False)

        Returns:
            List[str]: 센서 ID 리스트
        """
        pass

    def get_data_source_name(self) -> str:
        """
        데이터 소스 이름을 반환합니다.

        Returns:
            str: 데이터 소스 이름 (예: 'DocumentDB', 'S3')
        """
        return self.__class__.__name__.replace('Loader', '')
