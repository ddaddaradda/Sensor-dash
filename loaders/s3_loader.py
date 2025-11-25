"""
S3 데이터 로더
AWS S3 버킷에서 센서 데이터를 로드합니다.
"""
from typing import List
from io import BytesIO
import pandas as pd
import boto3
from datetime import datetime

from loaders.base import BaseLoader
from core.data_processor import local_tz
from config import ConfigDB


class S3Loader(BaseLoader):
    """
    S3 데이터 로더 클래스

    AWS S3 버킷에서 Parquet 파일을 읽어 BLE 및 LTE 센서 데이터를 로드합니다.
    """

    def __init__(self):
        """
        S3Loader를 초기화합니다.
        S3 클라이언트를 생성하고 버킷 정보를 설정합니다.
        """
        # S3 설정
        s3_config_ble = ConfigDB.S3BUCKET["ble_backup"]
        s3_config_lte = ConfigDB.S3BUCKET["lte_backup"]

        # S3 클라이언트 생성
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=s3_config_ble["id"],
            aws_secret_access_key=s3_config_ble["key"],
            region_name=s3_config_ble["region"]
        )

        # 버킷 이름
        self.ble_bucket = s3_config_ble["name"]
        self.lte_bucket = s3_config_lte["name"]

    def load_ble_data(self, date: str, phone: str, sensor: str) -> pd.DataFrame:
        """
        BLE 센서 데이터를 S3에서 로드합니다.

        Args:
            date (str): 날짜 (폴더명)
            phone (str): 전화번호
            sensor (str): 센서 ID

        Returns:
            pd.DataFrame: BLE 센서 데이터
        """
        object_key = f"{date}/{sensor}_{phone}_{date}.parquet"
        response = self.s3_client.get_object(Bucket=self.ble_bucket, Key=object_key)
        parquet_content = response['Body'].read()

        # 가상 메모리의 내용을 BytesIO 객체로 변환
        parquet_buffer = BytesIO(parquet_content)

        # parquet 파일을 pandas DataFrame으로 읽기
        df = pd.read_parquet(parquet_buffer)
        parquet_buffer.close()

        raw_data = df[[
            "time", "sensor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
            "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VELOCITY", "ALTITUDE", "BEARING"
        ]]

        # 시간 정렬
        raw_data.sort_values(by=['time'], ascending=True, inplace=True)
        raw_data['time'] = raw_data['time'].apply(
            lambda x: datetime.fromtimestamp(x / 1000, tz=local_tz).strftime('%Y-%m-%d %H:%M:%S')
        )

        # 컬럼명 표준화
        raw_data.columns = [
            "DATE", "senor_id", "ACCEL_X", "ACCEL_Y", "ACCEL_Z", "GYRO_X",
            "GYRO_Y", "GYRO_Z", "PITCH", "ROLL", "LAT", "LON", "VEL", "ALT", "HEAD"
        ]

        raw_data = raw_data.reset_index(drop=True)
        raw_data["DATE"] = pd.to_datetime(raw_data["DATE"])
        raw_data.drop_duplicates(subset='DATE', inplace=True)

        return raw_data

    def load_lte_data(self, date: str, phone: str, sensor: str) -> pd.DataFrame:
        """
        LTE 센서 데이터를 S3에서 로드합니다.

        Args:
            date (str): 날짜 (폴더명)
            phone (str): 전화번호
            sensor (str): 센서 ID

        Returns:
            pd.DataFrame: LTE 센서 데이터
        """
        object_key = f"{date}/{sensor}_{phone}_{date}.parquet"
        response = self.s3_client.get_object(Bucket=self.lte_bucket, Key=object_key)
        parquet_content = response['Body'].read()

        # 가상 메모리의 내용을 BytesIO 객체로 변환
        parquet_buffer = BytesIO(parquet_content)

        # parquet 파일을 pandas DataFrame으로 읽기
        df = pd.read_parquet(parquet_buffer)
        parquet_buffer.close()

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
        bucket = self.lte_bucket if is_lte else self.ble_bucket
        response = self.s3_client.list_objects_v2(Bucket=bucket, Delimiter='/')
        if 'CommonPrefixes' in response:
            date_list = [prefix['Prefix'].rstrip('/') for prefix in response['CommonPrefixes']]
        else:
            date_list = []
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
        bucket = self.lte_bucket if is_lte else self.ble_bucket
        response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=date)
        file_keys = [
            obj['Key'] for obj in response.get('Contents', [])
            if obj['Key'].strip() and obj['Key'].lower().endswith('.parquet')
        ]

        phone_set = set()
        for key in file_keys:
            parts = key.split('/')[-1].split('_')
            if parts:
                phone_num = parts[1]
                phone_set.add(phone_num)

        return list(phone_set)

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
        bucket = self.lte_bucket if is_lte else self.ble_bucket
        response = self.s3_client.list_objects_v2(Bucket=bucket, Prefix=date)
        file_keys = [
            obj['Key'] for obj in response.get('Contents', [])
            if obj['Key'].strip() and obj['Key'].lower().endswith('.parquet')
        ]

        specific_string = phone
        filtered_keys = list(filter(lambda key: specific_string in key, file_keys))
        sensor_ids = [key.split('/')[-1].split('_')[0] for key in filtered_keys]

        return sensor_ids
