"""
share.py — ngrok으로 외부 공유 URL 생성
실행: python share.py

사전 준비:
1. https://ngrok.com 가입 (무료)
2. 대시보드 → Your Authtoken 복사
3. 아래 NGROK_TOKEN에 붙여넣기
"""

from pyngrok import ngrok, conf
import time
import webbrowser

# ─────────────────────────────────────────
# ngrok 토큰 설정 (한 번만 입력하면 저장됨)
# https://dashboard.ngrok.com/get-started/your-authtoken
# ─────────────────────────────────────────
NGROK_TOKEN = "YOUR_NGROK_AUTHTOKEN"   # ← 여기에 토큰 붙여넣기

STREAMLIT_PORT = 8501


def main():
    if NGROK_TOKEN == "YOUR_NGROK_AUTHTOKEN":
        print("=" * 50)
        print("ngrok 토큰이 없습니다.")
        print()
        print("1. https://ngrok.com 에서 무료 가입")
        print("2. 대시보드 → Your Authtoken 복사")
        print("3. share.py 파일 열어서")
        print('   NGROK_TOKEN = "여기에 붙여넣기"')
        print("4. 다시 실행")
        print("=" * 50)
        input("\nEnter 키를 눌러 닫으세요...")
        return

    # 토큰 설정
    conf.get_default().auth_token = NGROK_TOKEN

    print("ngrok 터널 연결 중...")
    tunnel = ngrok.connect(STREAMLIT_PORT, "http")
    public_url = tunnel.public_url

    print()
    print("=" * 50)
    print("✅ 외부 공유 URL 생성 완료!")
    print()
    print(f"  🌐 공개 URL:  {public_url}")
    print(f"  💻 내부 URL:  http://localhost:{STREAMLIT_PORT}")
    print()
    print("  이 URL을 카톡/슬랙으로 공유하세요.")
    print("  (이 창을 닫으면 URL이 만료됩니다)")
    print("=" * 50)

    # 브라우저 자동 오픈
    webbrowser.open(public_url)

    print("\n종료하려면 Ctrl+C 를 누르세요.\n")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n터널 종료 중...")
        ngrok.disconnect(public_url)
        ngrok.kill()
        print("종료됐습니다.")


if __name__ == "__main__":
    main()
