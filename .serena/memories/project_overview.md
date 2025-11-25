# 프로젝트 개요

## 목적
AWS DocumentDB 또는 S3 버킷에서 센서 데이터를 수집하여 Dash 대시보드로 시각화하는 프로젝트

## 파일 구조

### 주요 파일
- `sensor_dash_docDB.py` - DocumentDB 기반 대시보드
- `sensor_dash_S3.py` - S3 기반 대시보드  
- `config.py` - 설정 정보 (ConfigDB 클래스)

## 공통 기능
두 대시보드 파일은 약 95% 이상 동일한 구조를 가지며, 데이터 로드 부분만 다름:

### 데이터 로드 함수
- `Load_BLEData(date, phone, sensor)` - BLE 센서 데이터 로드
- `Load_LTEData(date, phone, sensor)` - LTE 센서 데이터 로드

### 데이터 처리 함수
- `cleaning_data(df)` - 데이터 정제 및 전처리
- `show_date()`, `show_phonenum()`, `show_sensor()` - 데이터베이스에서 가능한 값 조회

### UI 콜백 함수
- `update_date()` - 날짜 선택 업데이트
- `update_phone()` - 전화번호 선택 업데이트
- `update_sensor()` - 센서 선택 업데이트
- `update_graph()` - 그래프 업데이트
- `print_map()` - 지도 출력

## 데이터 소스 차이점

### DocumentDB 버전
- pymongo 클라이언트 사용
- MongoDB 쿼리로 데이터 조회
- projection을 사용한 필드 선택

### S3 버전
- boto3 클라이언트 사용
- Parquet 파일 직접 읽기
- 파일 경로: `{date}/{sensor}_{phone}_{date}.parquet`

## 설정 정보 (config.py)
ConfigDB 클래스에 다음 설정 포함:
- MYSQL: dev, deploy 환경 설정
- S3BUCKET: bucket, accident, ble_backup, lte_backup 버킷 설정
- SLACK: 알림 설정
- MONGO: BLE, LTE DocumentDB 연결 정보
