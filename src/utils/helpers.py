# -*- coding: utf-8 -*-
"""
辅助函数模块
"""

import time
from datetime import datetime

def format_price(price, decimals=2):
    """格式化价格显示"""
    return f"${price:,.{decimals}f}"

def format_percentage(value, decimals=2):
    """格式化百分比显示"""
    return f"{value:.{decimals}f}%"

def format_timestamp(timestamp):
    """格式化时间戳"""
    if isinstance(timestamp, (int, float)):
        return datetime.fromtimestamp(timestamp / 1000).strftime("%Y-%m-%d %H:%M:%S")
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")

def calculate_distance_to_breakout(current_price, upper_band, lower_band):
    """计算距离突破水平的百分比"""
    distance_to_upper = ((upper_band - current_price) / current_price) * 100
    distance_to_lower = ((current_price - lower_band) / current_price) * 100
    return distance_to_upper, distance_to_lower

def validate_symbol(symbol):
    """验证交易对格式"""
    if not symbol:
        return False
    
    # 基本格式检查
    if not isinstance(symbol, str):
        return False
    
    # 检查是否包含USDT或USD
    valid_suffixes = ['USDT', 'USD', 'BTC', 'ETH']
    return any(symbol.endswith(suffix) for suffix in valid_suffixes)

def safe_float(value, default=0.0):
    """安全转换为浮点数"""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default

def safe_int(value, default=0):
    """安全转换为整数"""
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def retry_on_error(func, max_retries=3, delay=1):
    """错误重试装饰器"""
    def wrapper(*args, **kwargs):
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                time.sleep(delay)
        return None
    return wrapper 