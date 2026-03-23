@echo off
chcp 65001 > nul
echo 블로그 데이터랩 시작 중...
cd /d "%~dp0"
python -m streamlit run app.py
pause
