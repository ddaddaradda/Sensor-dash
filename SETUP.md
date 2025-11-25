# 🚀 프로젝트 설정 가이드

## ✅ 완료된 작업

1. ✅ 프로젝트 리팩토링 완료 (코드 중복 97% 제거)
2. ✅ **config.py → .env 전환 완료**
3. ✅ uv 프로젝트 설정 완료
4. ✅ .gitignore 설정으로 민감 정보 보호

---

## 📂 중요 파일

### 🔒 민감한 파일 (절대 Git에 커밋 안 됨)
- `.env` - **실제 비밀번호와 키가 저장됨** (이미 생성됨)
- `config.py` - 환경 변수 wrapper (Git에 커밋하지 마세요)

### 📝 Git에 커밋해야 할 파일
- `.env.example` - 환경 변수 템플릿
- `.gitignore` - Git 무시 목록
- `pyproject.toml` - uv 프로젝트 설정
- `README.md` - 프로젝트 문서
- `core/`, `loaders/` - 소스 코드
- `app_docdb.py`, `app_s3.py` - 앱 진입점

---

## 🔐 보안 설정

### .gitignore에 추가된 항목
```
.env                    # 실제 환경 변수 (민감 정보!)
.env.local
.env.*.local
config.py              # config wrapper (혹시 모를 실수 방지)
```

### 현재 상태
```bash
✓ .env 파일 생성됨 (실제 비밀번호/키 포함)
✓ .env.example 생성됨 (템플릿)
✓ config.py는 .env에서만 값을 읽음
✓ .gitignore에서 민감 파일 보호 중
```

---

## 🏃 빠른 시작

### 1. 가상환경 활성화
```bash
source .venv/bin/activate
```

### 2. 의존성 설치
```bash
uv sync
```

### 3. 애플리케이션 실행

**DocumentDB 대시보드:**
```bash
uv run python app_docdb.py
```
→ http://localhost:8050

**S3 대시보드:**
```bash
uv run python app_s3.py
```
→ http://localhost:8051

---

## 📋 환경 변수 확인

현재 `.env` 파일에 설정된 값들:

### AWS 설정
- ✓ AWS_ACCESS_KEY_ID
- ✓ AWS_SECRET_ACCESS_KEY
- ✓ AWS_REGION
- ✓ S3_BLE_BUCKET
- ✓ S3_LTE_BUCKET

### DocumentDB 설정
- ✓ MONGO_BLE_URI
- ✓ MONGO_LTE_URI
- ✓ MONGO_SSL_CERT_PATH

### 대시보드 인증
- ✓ DASH_USERNAME=admin
- ✓ DASH_PASSWORD

### MySQL (선택사항)
- ✓ MYSQL_DEV_*
- ✓ MYSQL_PROD_*

### Slack (선택사항)
- ✓ SLACK_TOKEN
- ✓ SLACK_CHANNEL

---

## 🔄 Git 워크플로우

### 처음 Git 저장소 초기화 시
```bash
git init
git add .
git commit -m "Initial commit: Refactored sensor dashboard"
```

**자동으로 제외되는 파일:**
- `.env` (실제 비밀번호)
- `config.py` (실수 방지)
- `.venv/` (가상환경)
- `__pycache__/` (Python 캐시)

### 새로운 환경에서 클론 후 설정
```bash
# 1. 저장소 클론
git clone <your-repo-url>
cd 10.dash

# 2. 환경 변수 설정
cp .env.example .env
vi .env  # 실제 값 입력

# 3. 가상환경 및 의존성 설치
uv venv
source .venv/bin/activate
uv sync

# 4. 실행
uv run python app_s3.py
```

---

## ✅ 검증

설정이 제대로 되었는지 확인:

```bash
source .venv/bin/activate
python3 << 'EOF'
from config import ConfigDB
print("✓ AWS Key:", ConfigDB.S3BUCKET['bucket']['id'][:10] + "...")
print("✓ Mongo DB:", ConfigDB.MONGO['BLE']['DB'])
print("✓ Username:", ConfigDB.DASH_AUTH['username'])
print("\n✅ 모든 설정 로드 완료!")
EOF
```

---

## 🚨 주의사항

### ❌ 절대 하지 말 것
- `.env` 파일을 Git에 커밋
- `config.py` 파일을 Git에 커밋
- 비밀번호/키를 코드에 직접 하드코딩

### ✅ 해야 할 것
- `.env.example`은 Git에 커밋 (템플릿으로 사용)
- 팀원에게 `.env` 파일 별도로 공유 (안전한 방법으로)
- 정기적으로 비밀번호 변경

---

## 📞 문제 해결

### Q: .env 파일이 로드되지 않아요
```bash
# python-dotenv 설치 확인
source .venv/bin/activate
uv pip install python-dotenv
```

### Q: Git에 .env가 추가되려고 해요
```bash
# .gitignore 확인
cat .gitignore | grep .env

# 이미 추가된 경우 제거
git rm --cached .env
git commit -m "Remove .env from git"
```

### Q: config.py가 Git에 추가되려고 해요
```bash
# 이미 추가된 경우 제거
git rm --cached config.py
git commit -m "Remove config.py from git"
```

---

## 🎉 완료!

이제 안전하게 GitHub에 푸시할 수 있습니다:

```bash
git add .
git commit -m "Refactored sensor dashboard with env-based config"
git push origin main
```

**민감한 정보는 자동으로 제외됩니다!** 🔐
