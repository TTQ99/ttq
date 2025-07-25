#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试海龟交易出场信号功能
"""

import pandas as pd
import os
import sys

# 添加src目录到路径
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from trading.market_monitor import MarketMonitor

def test_exit_signals():
    """测试出场信号功能"""
    print("🧪 开始测试海龟交易出场信号功能...")
    
    # 创建市场监控器实例
    monitor = MarketMonitor()
    
    # 模拟K线数据
    test_klines = pd.DataFrame({
        'timestamp': range(1000, 1100, 10),
        'time': [f'2024-01-01 {i:02d}:00:00' for i in range(10)],
        'open': [1.0, 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7, 1.8, 1.9],
        'high': [1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85, 1.95],
        'low': [0.95, 1.05, 1.15, 1.25, 1.35, 1.45, 1.55, 1.65, 1.75, 1.85],
        'close': [1.02, 1.12, 1.22, 1.32, 1.42, 1.52, 1.62, 1.72, 1.82, 1.92],
        'volume': [1000] * 10,
        'notified': [False] * 10
    })
    
    # 将测试数据添加到监控器中
    monitor.symbol_klines['XRPUSDT'] = test_klines
    
    print(f"✅ 已创建测试K线数据: {len(test_klines)}条记录")
    print(f"📊 过去10条K线最高价: {test_klines['high'].max():.4f}")
    print(f"📊 过去10条K线最低价: {test_klines['low'].min():.4f}")
    print(f"📊 当前价格: {test_klines.iloc[-1]['close']:.4f}")
    
    # 测试出场信号检查
    print("\n🔍 测试出场信号检查...")
    monitor.check_turtle_exit_signals('XRPUSDT')
    
    print("\n✅ 测试完成!")

if __name__ == "__main__":
    test_exit_signals() 