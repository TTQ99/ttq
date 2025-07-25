#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试WebSocket重连功能
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

def test_websocket_reconnect():
    """测试WebSocket重连功能"""
    print("🧪 测试WebSocket重连功能")
    
    # 创建市场监控器实例
    monitor = MarketMonitor()
    
    # 设置测试配置
    monitor.websocket_max_retries = 3
    monitor.websocket_retry_delay = 5
    monitor.websocket_max_retry_delay = 30
    monitor.websocket_connection_check_interval = 10
    
    print(f"WebSocket配置:")
    print(f"  - 最大重试次数: {monitor.websocket_max_retries}")
    print(f"  - 初始重试延迟: {monitor.websocket_retry_delay}秒")
    print(f"  - 最大重试延迟: {monitor.websocket_max_retry_delay}秒")
    print(f"  - 连接检查间隔: {monitor.websocket_connection_check_interval}秒")
    
    # 测试连接状态检查
    print("\n📋 测试1: 连接状态检查")
    is_connected = monitor.is_websocket_connected()
    print(f"初始连接状态: {is_connected}")
    
    # 测试重连功能
    print("\n📋 测试2: 重连功能")
    success = monitor.reconnect_websocket()
    print(f"重连结果: {success}")
    
    # 测试连接状态检查
    print("\n📋 测试3: 重连后连接状态检查")
    is_connected = monitor.is_websocket_connected()
    print(f"重连后连接状态: {is_connected}")
    
    print("\n✅ 测试完成")

if __name__ == "__main__":
    test_websocket_reconnect() 