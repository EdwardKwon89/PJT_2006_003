@echo off
REM BOS Documentation Generator - Windows 실행 스크립트
REM UTF-8 출력 + PYTHONIOENCODING 설정 자동 적용

set PYTHONIOENCODING=utf-8
chcp 65001 > nul 2>&1

python -X utf8 "%~dp0generate_docs.py" %*
