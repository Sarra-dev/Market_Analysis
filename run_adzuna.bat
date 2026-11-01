@echo off
cd /d C:\Users\LENOVO\Documents\Market_Analysis\job_market_analyzer

call C:\Users\LENOVO\Documents\Market_Analysis\venv\Scripts\activate.bat

echo [%date% %time%] Starting Adzuna scrape... >> C:\Users\LENOVO\Documents\Market_Analysis\logs\scrape.log 2>&1

scrapy crawl adzuna >> C:\Users\LENOVO\Documents\Market_Analysis\logs\scrape.log 2>&1

echo [%date% %time%] Scrape finished. >> C:\Users\LENOVO\Documents\Market_Analysis\logs\scrape.log 2>&1