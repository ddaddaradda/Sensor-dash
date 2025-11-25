# 리팩토링 체크리스트 - Shared Core + Thin Apps

## 📌 프로젝트 개요
- **목표**: DocumentDB/S3 대시보드의 공통 코드 추출 및 중복 제거
- **전략**: Shared Core + Thin Apps 패턴
- **원칙**: 두 앱의 성능 특성은 유지하되, 유지보수성 극대화

---

## Phase 0: 준비 단계 ✅

### ✅ 0.1 현재 상태 분석
- [x] 기존 파일 구조 파악
- [x] 공통 기능 식별
- [x] 차이점 분석 (데이터 로딩 부분)
- [x] 의존성 확인

### ✅ 0.2 백업 생성
- [ ] 기존 파일 백업 디렉토리 생성
- [ ] sensor_dash_docDB.py 백업
- [ ] sensor_dash_S3.py 백업
- [ ] config.py 백업

---

## Phase 1: 프로젝트 구조 생성 🏗️

### 1.1 디렉토리 구조 생성
- [ ] `core/` 디렉토리 생성
- [ ] `core/__init__.py` 생성
- [ ] `loaders/` 디렉토리 생성
- [ ] `loaders/__init__.py` 생성
- [ ] `backup/` 디렉토리 생성 (기존 파일 보관)

### 1.2 목표 구조 확인
```
10.dash/
├── backup/                    # 기존 파일 백업
│   ├── sensor_dash_docDB.py
│   └── sensor_dash_S3.py
├── core/
│   ├── __init__.py
│   ├── data_processor.py      # 데이터 처리 로직
│   ├── ui_components.py       # UI 컴포넌트
│   ├── callbacks.py           # 콜백 함수
│   └── utils.py               # 유틸리티
├── loaders/
│   ├── __init__.py
│   ├── base.py                # 추상 베이스
│   ├── docdb_loader.py        # DocumentDB
│   └── s3_loader.py           # S3
├── config.py                  # 기존 유지
├── app_docdb.py               # 신규 (간소화)
├── app_s3.py                  # 신규 (간소화)
└── requirements.txt           # 의존성
```

---

## Phase 2: Base Loader 인터페이스 구현 🔧

### 2.1 추상 베이스 클래스 작성
- [ ] `loaders/base.py` 생성
- [ ] BaseLoader 추상 클래스 정의
- [ ] 필수 메서드 정의:
  - [ ] `load_ble_data(date, phone, sensor)`
  - [ ] `load_lte_data(date, phone, sensor)`
  - [ ] `show_date()`
  - [ ] `show_phonenum(date)`
  - [ ] `show_sensor(date, phone)`
  - [ ] `get_database_reference()` (optional)

### 2.2 인터페이스 검증
- [ ] 메서드 시그니처 일관성 확인
- [ ] 반환 타입 일관성 확인 (모두 DataFrame)
- [ ] 타입 힌트 추가

---

## Phase 3: 공통 데이터 처리 로직 추출 📊

### 3.1 data_processor.py 작성
- [ ] `core/data_processor.py` 생성
- [ ] `cleaning_data()` 함수 이동
- [ ] 시간대 변환 로직 확인
- [ ] 데이터 정제 로직 확인

### 3.2 검증 포인트
- [ ] local_tz 의존성 확인
- [ ] pandas 연산 정확성 확인
- [ ] 원본과 동일한 출력 보장

### 3.3 유틸리티 함수
- [ ] `core/utils.py` 생성
- [ ] 공통 헬퍼 함수 이동 (있다면)
- [ ] 타임존 관련 유틸리티

---

## Phase 4: UI 컴포넌트 추출 🎨

### 4.1 ui_components.py 작성
- [ ] `core/ui_components.py` 생성
- [ ] UI 컴포넌트 이동:
  - [ ] `popover_children`
  - [ ] `first_card`
  - [ ] `second_card`
  - [ ] `first_graph` ~ `fifth_graph`
  - [ ] `output_card`
  - [ ] `map_card`

### 4.2 레이아웃 함수 작성
- [ ] `create_layout()` 함수 작성
- [ ] Dash 인증 설정 통합
- [ ] VALID_USERNAME_PASSWORD_PAIRS 처리

### 4.3 검증 포인트
- [ ] 모든 컴포넌트 ID 일관성 확인
- [ ] CSS 클래스 확인
- [ ] 반응형 레이아웃 유지

---

## Phase 5: 콜백 함수 추출 🔄

### 5.1 callbacks.py 작성
- [ ] `core/callbacks.py` 생성
- [ ] 콜백 등록 함수 작성: `register_callbacks(app, loader)`
- [ ] 각 콜백 함수 이동:
  - [ ] `update_date` - 날짜 업데이트
  - [ ] `update_phone` - 전화번호 업데이트
  - [ ] `update_sensor` - 센서 업데이트
  - [ ] `update_graph` - 그래프 업데이트
  - [ ] `print_map` - 지도 출력

### 5.2 콜백 의존성 확인
- [ ] Input/Output/State 정확성 확인
- [ ] loader 의존성 주입 확인
- [ ] data_processor 함수 호출 확인

### 5.3 검증 포인트
- [ ] 콜백 체인 동작 확인
- [ ] 에러 핸들링 유지
- [ ] 데이터 흐름 정확성

---

## Phase 6: DocumentDB Loader 구현 📦

### 6.1 docdb_loader.py 작성
- [ ] `loaders/docdb_loader.py` 생성
- [ ] DocDBLoader 클래스 작성 (BaseLoader 상속)
- [ ] 기존 sensor_dash_docDB.py에서 로직 이동:
  - [ ] MongoDB 연결 초기화
  - [ ] `load_ble_data()` 구현
  - [ ] `load_lte_data()` 구현
  - [ ] `show_date()` 구현
  - [ ] `show_phonenum()` 구현
  - [ ] `show_sensor()` 구현

### 6.2 연결 관리
- [ ] pymongo 클라이언트 초기화
- [ ] SSL 인증서 경로 처리
- [ ] 연결 풀 설정
- [ ] 에러 핸들링

### 6.3 검증 포인트
- [ ] 쿼리 성능 유지 확인
- [ ] projection 로직 확인
- [ ] batch_size 설정 유지
- [ ] 데이터 변환 로직 일치

---

## Phase 7: S3 Loader 구현 ☁️

### 7.1 s3_loader.py 작성
- [ ] `loaders/s3_loader.py` 생성
- [ ] S3Loader 클래스 작성 (BaseLoader 상속)
- [ ] 기존 sensor_dash_S3.py에서 로직 이동:
  - [ ] boto3 클라이언트 초기화
  - [ ] `load_ble_data()` 구현
  - [ ] `load_lte_data()` 구현
  - [ ] `show_date()` 구현
  - [ ] `show_phonenum()` 구현
  - [ ] `show_sensor()` 구현

### 7.2 S3 처리
- [ ] Parquet 파일 읽기 로직
- [ ] BytesIO 버퍼 처리
- [ ] 파일 경로 생성 로직
- [ ] 에러 핸들링

### 7.3 검증 포인트
- [ ] Parquet 읽기 성능 유지
- [ ] 파일 경로 포맷 확인
- [ ] 버킷 이름 설정 확인
- [ ] 데이터 변환 로직 일치

---

## Phase 8: 앱 팩토리 함수 구현 🏭

### 8.1 create_app 함수
- [ ] `core/ui_components.py`에 `create_app()` 함수 추가
- [ ] 함수 시그니처: `create_app(loader: BaseLoader, app_name: str, port: int)`
- [ ] Dash 앱 초기화
- [ ] 레이아웃 설정
- [ ] 콜백 등록
- [ ] 인증 설정

### 8.2 설정 통합
- [ ] config.py 읽기
- [ ] 환경별 설정 처리
- [ ] 로거 설정

### 8.3 검증 포인트
- [ ] loader 주입 확인
- [ ] 모든 콜백 등록 확인
- [ ] UI 렌더링 확인

---

## Phase 9: 새로운 앱 파일 작성 ✨

### 9.1 app_docdb.py 작성
- [ ] 파일 생성
- [ ] DocDBLoader import
- [ ] create_app import
- [ ] 로더 인스턴스 생성
- [ ] 앱 생성 (포트 8050)
- [ ] `if __name__ == '__main__'` 블록

### 9.2 app_s3.py 작성
- [ ] 파일 생성
- [ ] S3Loader import
- [ ] create_app import
- [ ] 로더 인스턴스 생성
- [ ] 앱 생성 (포트 8051)
- [ ] `if __name__ == '__main__'` 블록

### 9.3 검증 포인트
- [ ] 각 파일이 20줄 이하인지 확인
- [ ] import 경로 정확성
- [ ] 포트 충돌 없음

---

## Phase 10: 의존성 및 Import 검증 🔍

### 10.1 Import 체인 확인
- [ ] `core/__init__.py` exports 확인
- [ ] `loaders/__init__.py` exports 확인
- [ ] 순환 import 없음 확인

### 10.2 의존성 확인
- [ ] pandas
- [ ] dash
- [ ] dash-auth
- [ ] plotly
- [ ] pymongo
- [ ] boto3
- [ ] pyarrow (Parquet용)

### 10.3 requirements.txt 업데이트
- [ ] 모든 필요한 패키지 나열
- [ ] 버전 명시

---

## Phase 11: 테스트 및 검증 🧪

### 11.1 DocumentDB 앱 테스트
- [ ] `uv run python app_docdb.py` 실행
- [ ] 로그인 테스트
- [ ] 날짜 선택 테스트
- [ ] 전화번호 선택 테스트
- [ ] 센서 선택 테스트
- [ ] 그래프 렌더링 확인
- [ ] 지도 표시 확인
- [ ] 에러 없음 확인

### 11.2 S3 앱 테스트
- [ ] `uv run python app_s3.py` 실행
- [ ] 로그인 테스트
- [ ] 날짜 선택 테스트
- [ ] 전화번호 선택 테스트
- [ ] 센서 선택 테스트
- [ ] 그래프 렌더링 확인
- [ ] 지도 표시 확인
- [ ] 에러 없음 확인

### 11.3 성능 비교
- [ ] DocumentDB 로딩 시간 측정
- [ ] S3 로딩 시간 측정
- [ ] 기존 버전과 비교
- [ ] 성능 저하 없음 확인

### 11.4 기능 검증
- [ ] 모든 드롭다운 동작
- [ ] 모든 그래프 업데이트
- [ ] 지도 인터랙션
- [ ] 데이터 정확성
- [ ] UI 레이아웃 일치

---

## Phase 12: 코드 품질 검증 ✨

### 12.1 코드 리뷰
- [ ] 타입 힌트 추가
- [ ] Docstring 추가
- [ ] 주석 정리
- [ ] 미사용 import 제거
- [ ] 변수명 일관성

### 12.2 에러 핸들링
- [ ] 데이터 로딩 실패 처리
- [ ] 네트워크 오류 처리
- [ ] 빈 데이터 처리
- [ ] 사용자 친화적 에러 메시지

### 12.3 보안 검증
- [ ] config.py의 민감 정보 확인
- [ ] 환경 변수 사용 권장
- [ ] 인증 로직 확인

---

## Phase 13: 문서화 📚

### 13.1 README 작성
- [ ] 프로젝트 구조 설명
- [ ] 설치 방법
- [ ] 실행 방법
- [ ] 환경 설정

### 13.2 코드 문서
- [ ] 각 모듈 Docstring
- [ ] 주요 함수 설명
- [ ] 클래스 사용법

### 13.3 리팩토링 문서
- [ ] 변경 사항 요약
- [ ] 마이그레이션 가이드
- [ ] 기존 파일 위치

---

## Phase 14: 정리 및 마무리 🎯

### 14.1 파일 정리
- [ ] 기존 파일 backup/ 이동
- [ ] 미사용 파일 제거
- [ ] .gitignore 업데이트

### 14.2 최종 검증
- [ ] 전체 프로젝트 구조 확인
- [ ] 모든 테스트 통과
- [ ] 문서 완성도 확인

### 14.3 버전 관리
- [ ] Git commit 메시지 작성
- [ ] 변경 사항 태깅

---

## 🚨 주의 사항 및 리스크

### 데이터 로딩 로직
- ⚠️ DocumentDB와 S3의 데이터 포맷이 완전히 동일한지 확인
- ⚠️ 시간대 변환이 양쪽에서 동일하게 동작하는지 확인
- ⚠️ 컬럼명 매핑이 일치하는지 확인

### 콜백 체인
- ⚠️ Dash 콜백의 Input/Output 순서 유지
- ⚠️ 콜백 간 의존성 확인
- ⚠️ prevent_initial_call 설정 확인

### 성능
- ⚠️ 추가된 추상화 레이어로 인한 오버헤드 최소화
- ⚠️ MongoDB 쿼리 최적화 유지
- ⚠️ S3 읽기 성능 유지

### 호환성
- ⚠️ Python 버전 확인
- ⚠️ 패키지 버전 호환성
- ⚠️ 기존 설정 파일 호환성

---

## 📊 진행 상황 추적

- **Phase 0**: ⬜ 0/2
- **Phase 1**: ⬜ 0/2
- **Phase 2**: ⬜ 0/2
- **Phase 3**: ⬜ 0/3
- **Phase 4**: ⬜ 0/3
- **Phase 5**: ⬜ 0/3
- **Phase 6**: ⬜ 0/3
- **Phase 7**: ⬜ 0/3
- **Phase 8**: ⬜ 0/3
- **Phase 9**: ⬜ 0/3
- **Phase 10**: ⬜ 0/3
- **Phase 11**: ⬜ 0/4
- **Phase 12**: ⬜ 0/3
- **Phase 13**: ⬜ 0/3
- **Phase 14**: ⬜ 0/3

**전체 진행률**: 0/42 (0%)

---

## 💡 각 단계 완료 후 체크
- [ ] 단계 완료 표시 (✅)
- [ ] 다음 단계 시작 전 검증
- [ ] 문제 발견 시 즉시 문서화
- [ ] 각 Phase 완료 시 커밋

---

## 🎓 학습 및 개선 사항
(리팩토링 중 발견한 개선 사항 기록)

-
-
-
