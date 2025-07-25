#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场监控启动脚本
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.trading.market_monitor import MarketMonitor

def main():
    """主函数"""
    print("🚀 启动市场监控系统")
    print("=" * 50)
    
    try:
        monitor = MarketMonitor()
        monitor.run()


    except KeyboardInterrupt:
        print("👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")

if __name__ == "__main__":
    main() 