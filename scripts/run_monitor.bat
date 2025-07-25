@echo off
chcp 65001 >nul
echo 🚀 启动海龟交易法监控系统
echo ================================================
echo.
echo 📝 请确保已配置钉钉机器人设置（参考 config/templates/.env.template）
echo.
pause
echo.
python scripts/run_monitor.py
pause 