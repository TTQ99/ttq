#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海龟交易系统主启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.trading.turtle_system import TurtleTradingSystem
from src.utils.config import Config

def main():
    """主函数"""
    print("🚀 启动海龟交易法监控系统")
    print("=" * 50)
    
    # 加载配置
    config = Config()

    print(config)
    
    # 检查配置
    if not config.is_dingtalk_configured():
        print("⚠️ 钉钉机器人配置不完整")
        print("📝 请参考 config/templates/.env.template 进行配置")
        return
    
    # 创建海龟交易系统
    turtle_system = TurtleTradingSystem()
    
    # 运行监控
    turtle_system.run_turtle_trading_monitor(
        symbol="BTCUSDT",
        interval="15m",
        check_interval=config.check_interval
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}") 