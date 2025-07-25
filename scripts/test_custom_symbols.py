#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试自定义交易对功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trading.market_monitor import MarketMonitor

def test_custom_symbols():
    """测试自定义交易对功能"""
    print("🧪 测试自定义交易对功能")
    
    # 创建市场监控器实例
    monitor = MarketMonitor()
    
    # 测试1: 使用JSON数组格式的自定义交易对
    print("\n📋 测试1: 使用JSON数组格式的自定义交易对")
    os.environ['CUSTOM_SYMBOLS'] = '["BTCUSDT","ETHUSDT","BNBUSDT","ADAUSDT","SOLUSDT"]'
    symbols1 = monitor.get_top_symbols(limit=10)
    print(f"获取到的交易对: {symbols1}")
    
    # 测试2: 使用逗号分隔格式的自定义交易对（向后兼容）
    print("\n📋 测试2: 使用逗号分隔格式的自定义交易对（向后兼容）")
    os.environ['CUSTOM_SYMBOLS'] = 'BTCUSDT,ETHUSDT,BNBUSDT,ADAUSDT,SOLUSDT'
    symbols2 = monitor.get_top_symbols(limit=10)
    print(f"获取到的交易对: {symbols2}")
    
    # 测试3: 不使用自定义交易对（使用常用交易对）
    print("\n📋 测试3: 使用常用交易对列表")
    if 'CUSTOM_SYMBOLS' in os.environ:
        del os.environ['CUSTOM_SYMBOLS']
    symbols3 = monitor.get_top_symbols(limit=5)
    print(f"获取到的交易对: {symbols3}")
    
    # 测试4: 测试无效交易对
    print("\n📋 测试4: 测试无效交易对")
    os.environ['CUSTOM_SYMBOLS'] = '["BTCUSDT","INVALIDUSDT","ETHUSDT","FAKEUSDT"]'
    symbols4 = monitor.get_top_symbols(limit=10)
    print(f"获取到的有效交易对: {symbols4}")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_custom_symbols() 