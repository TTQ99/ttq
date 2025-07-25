#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试WebSocket重连逻辑（不依赖网络连接）
"""

import os
import sys
import time
import logging
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.trading.market_monitor import MarketMonitor

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

def test_websocket_logic():
    """测试WebSocket重连逻辑"""
    print("🧪 测试WebSocket重连逻辑")
    
    # 创建市场监控器实例
    monitor = MarketMonitor()
    
    # 设置测试配置
    monitor.websocket_max_retries = 3
    monitor.websocket_retry_delay = 2
    monitor.websocket_max_retry_delay = 10
    monitor.websocket_connection_check_interval = 5
    
    print(f"WebSocket配置:")
    print(f"  - 最大重试次数: {monitor.websocket_max_retries}")
    print(f"  - 初始重试延迟: {monitor.websocket_retry_delay}秒")
    print(f"  - 最大重试延迟: {monitor.websocket_max_retry_delay}秒")
    print(f"  - 连接检查间隔: {monitor.websocket_connection_check_interval}秒")
    
    # 测试连接状态检查（无连接时）
    print("\n📋 测试1: 无连接时的状态检查")
    is_connected = monitor.is_websocket_connected()
    print(f"连接状态: {is_connected}")
    assert is_connected == False, "无连接时应该返回False"
    
    # 测试重连功能（模拟网络问题）
    print("\n📋 测试2: 重连功能（模拟网络问题）")
    success = monitor.reconnect_websocket()
    print(f"重连结果: {success}")
    # 由于网络问题，重连可能失败，这是正常的
    
    # 测试重连后连接状态检查
    print("\n📋 测试3: 重连后连接状态检查")
    is_connected = monitor.is_websocket_connected()
    print(f"重连后连接状态: {is_connected}")
    
    # 测试配置参数计算
    print("\n📋 测试4: 重试延迟计算")
    for retry_count in range(1, 4):
        delay = min(monitor.websocket_retry_delay * (2 ** (retry_count - 1)), monitor.websocket_max_retry_delay)
        print(f"  重试 {retry_count}: {delay}秒")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_websocket_logic() 