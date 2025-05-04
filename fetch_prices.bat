@echo off
cd /d C:\Users\tarik\DeepInvestAI
call venv\Scripts\activate
python manage.py fetch_prices --symbol AAPL --period 90d --interval 1d
