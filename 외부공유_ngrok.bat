@echo off
chcp 65001 > nul
echo =============================================
echo  블로그 데이터랩 - 외부 공유 모드
echo =============================================
echo.

cd /d "%~dp0"

:: Streamlit 백그라운드 실행
start /B python -m streamlit run app.py --server.port 8501 --server.headless true

:: 3초 대기
timeout /t 3 /nobreak > nul

:: ngrok으로 공개 URL 생성
python share.py

pause
