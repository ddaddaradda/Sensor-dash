"""
S3 기반 센서 대시보드 애플리케이션

AWS S3 버킷에서 센서 데이터를 로드하여 대시보드로 시각화합니다.
"""
import os
import signal


def kill_port_process(port):
    """포트를 사용 중인 프로세스를 종료합니다."""
    import time
    try:
        result = os.popen(f"lsof -ti:{port}").read()
        if result:
            pids = result.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGKILL)  # SIGTERM 대신 SIGKILL 사용
                    print(f"종료: 포트 {port}를 사용하던 프로세스 {pid}")
                    time.sleep(2)  # 포트 해제를 위해 2초 대기
                except:
                    pass
    except:
        pass


if __name__ == '__main__':
    import time
    from waitress import serve
    from core.ui_components import create_app
    from loaders.s3_loader import S3Loader

    PORT = 8052  # 포트를 8052로 변경

    print(f"[시작] 포트 {PORT} 정리 시작...")
    kill_port_process(PORT)

    print(f"[대기] 포트 해제 대기 중...")
    time.sleep(3)  # 충분한 대기 시간 확보

    print(f"[초기화] S3 로더 생성...")
    loader = S3Loader()

    print(f"[초기화] 앱 생성...")
    app = create_app(loader, app_name="S3 Sensor Dashboard", port=PORT)

    print(f"[시작] Waitress 서버 시작 (http://0.0.0.0:{PORT})...")
    print(f"브라우저에서 http://localhost:{PORT} 로 접속하세요")
    print(f"종료하려면 Ctrl+C를 누르세요")
    serve(app.server, host='0.0.0.0', port=PORT, threads=4)
