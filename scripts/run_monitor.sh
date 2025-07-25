#!/bin/bash

echo "🚀 启动海龟交易法监控系统"
echo "================================================"
echo ""
echo "📝 请确保已配置钉钉机器人设置（参考 config/templates/.env.template）"
echo ""
read -p "按回车键继续..."

python3 scripts/run_monitor.py 