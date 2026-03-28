@echo off
title 달빛에구운고등어 마케팅 자동화 시스템
echo [1] 네이버 리뷰 및 SEO 데이터 수집 시작
echo [2] 데이터 정제 및 고도화 분석 실행
echo [3] 마케팅 웹 대시보드 로컬 서버 실행
set /p choice="번호 입력: "
if "%choice%"=="1" ( python src/crawler/naver_review_crawler.py & python src/crawler/naver_seo_crawler.py )
if "%choice%"=="2" ( python src/analyzer/clean_data.py & python src/analyzer/seo_analyzer.py )
if "%choice%"=="3" ( start docs/index.html )
pause
