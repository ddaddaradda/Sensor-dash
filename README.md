# 센서 데이터 대시보드

AWS DocumentDB 또는 S3 버킷에서 센서 데이터를 로드하여 실시간으로 시각화하는 Dash 기반 대시보드 애플리케이션입니다.

## ✨ 주요 기능

- 📊 **BLE/LTE 센서 데이터 시각화**
  - 초당 데이터 그래프
  - ACCEL, GYRO, ATTITUDE 센서 데이터
  - GPS 기반 지도 시각화

- 🔄 **두 가지 데이터 소스 지원**
  - DocumentDB: MongoDB 쿼리 기반 (느림)
  - S3: Parquet 파일 직접 읽기 (빠름)

- 🔐 **보안**
  - 환경 변수 기반 설정 관리
  - 대시보드 Basic Authentication

## 📦 프로젝트 구조

```
10.dash/
├── core/                        # 공통 기능 모듈
│   ├── callbacks.py            # Dash 콜백 함수
│   ├── data_processor.py       # 데이터 정제 로직
│   ├── ui_components.py        # UI 컴포넌트 & 앱 팩토리
│   └── utils.py                # 유틸리티
│
├── loaders/                     # 데이터 로더
│   ├── base.py                 # 추상 베이스 클래스
│   ├── docdb_loader.py         # DocumentDB 구현
│   └── s3_loader.py            # S3 구현
│
├── app_docdb.py                 # DocumentDB 대시보드 (포트 8050)
├── app_s3.py                    # S3 대시보드 (포트 8051)
├── config.py                    # 설정 관리
├── pyproject.toml               # uv 프로젝트 설정
├── .env.example                 # 환경 변수 템플릿
└── README.md
```

## 🚀 설치 및 실행

### 1. 사전 요구사항

- Python 3.9 이상
- [uv](https://github.com/astral-sh/uv) 설치
- AWS 자격 증명 (S3 사용 시)
- DocumentDB 접근 권한 (DocumentDB 사용 시)

### 2. 저장소 클론

```bash
cd /mnt/e/daun/10.dash
```

### 3. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 실제 값으로 수정합니다:

```bash
cp .env.example .env
vi .env  # 또는 원하는 에디터로 편집
```

**필수 환경 변수:**
- `AWS_ACCESS_KEY_ID` - AWS 액세스 키
- `AWS_SECRET_ACCESS_KEY` - AWS 시크릿 키
- `MONGO_BLE_URI` - DocumentDB BLE 연결 문자열
- `MONGO_LTE_URI` - DocumentDB LTE 연결 문자열
- `DASH_PASSWORD` - 대시보드 로그인 비밀번호

### 4. 의존성 설치

uv를 사용하여 의존성을 설치합니다:

```bash
uv sync
```

또는 수동 설치:

```bash
uv pip install -e .
```

### 5. 애플리케이션 실행

#### DocumentDB 대시보드 실행

```bash
uv run python app_docdb.py
```

브라우저에서 접속: `http://localhost:8050`

#### S3 대시보드 실행

```bash
uv run python app_s3.py
```

브라우저에서 접속: `http://localhost:8051`

## 🔐 인증

대시보드에 접근하려면 로그인이 필요합니다:

- **사용자명**: `.env` 파일의 `DASH_USERNAME` (기본값: `admin`)
- **비밀번호**: `.env` 파일의 `DASH_PASSWORD`

## 📚 사용법

### 1. 센서 버전 선택
- 스위치를 사용하여 **BLE** 또는 **LTE** 센서 버전을 선택합니다.

### 2. 데이터 조회
1. **날짜** 선택
2. **전화번호** 선택
3. **센서 ID** 선택
4. **조회** 버튼 클릭

### 3. 데이터 시각화
- **그래프**: 센서 데이터의 시계열 그래프
- **지도**: GPS 위치 기반 주행 경로
  - 초록: 센서 연결 정상
  - 주황: 센서 미연결
  - 빨강: GPS 오류

## 🛠️ 개발

### 새로운 데이터 소스 추가

1. `loaders/` 디렉토리에 새 로더 클래스 생성:

```python
# loaders/new_loader.py
from loaders.base import BaseLoader

class NewLoader(BaseLoader):
    def load_ble_data(self, date, phone, sensor):
        # 구현
        pass

    def load_lte_data(self, date, phone, sensor):
        # 구현
        pass

    # ... 나머지 메서드 구현
```

2. 새 앱 파일 생성:

```python
# app_new.py
from core.ui_components import create_app
from loaders.new_loader import NewLoader

loader = NewLoader()
app = create_app(loader, app_name="New Dashboard", port=8052)

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8052)
```

### 코드 구조

- **Strategy Pattern**: `BaseLoader` 추상 클래스를 통한 데이터 소스 추상화
- **Dependency Injection**: 로더를 `create_app()`에 주입
- **Separation of Concerns**: 데이터/UI/로직 완전 분리

## 🔍 문제 해결

### pymongo 설치 오류

DocumentDB 사용 시 pymongo가 필요합니다:

```bash
uv pip install pymongo
```

### SSL 인증서 오류

DocumentDB 연결 시 SSL 인증서가 필요합니다:

```bash
wget https://truststore.pki.rds.amazonaws.com/global/global-bundle.pem
```

`.env` 파일에 인증서 경로 설정:

```
MONGO_SSL_CERT_PATH=/path/to/global-bundle.pem
```

### 환경 변수 로드 안 됨

`.env` 파일이 프로젝트 루트에 있는지 확인하세요:

```bash
ls -la .env
```

