#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海龟交易系统测试脚本
用于测试K线数据获取和信号检测功能
"""

import pandas as pd
from turtle_trading_system import TurtleTradingSystem

def test_klines_data():
    """测试K线数据获取"""
    print("🧪 测试K线数据获取...")
    
    turtle_system = TurtleTradingSystem()
    
    # 获取BTC的56条1小时K线数据
    df = turtle_system.get_klines("BTCUSDT", "1h", 56)
    
    if df is not None:
        print(f"✅ 成功获取 {len(df)} 条K线数据")
        print(f"📅 时间范围: {df['timestamp'].min()} 到 {df['timestamp'].max()}")
        print(f"💰 最新价格: ${df['close'].iloc[-1]:,.2f}")
        print(f"📊 价格范围: ${df['low'].min():,.2f} - ${df['high'].max():,.2f}")
        print()
        
        # 显示最近5条数据
        print("最近5条K线数据:")
        recent_data = df.tail(5)[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
        print(recent_data.to_string(index=False))
        print()
        
        return df
    else:
        print("❌ K线数据获取失败")
        return None

def test_atr_calculation(df):
    """测试ATR计算"""
    print("🧪 测试ATR计算...")
    
    turtle_system = TurtleTradingSystem()
    
    # 计算ATR
    atr = turtle_system.calculate_atr(df, 20)
    
    if atr is not None:
        print(f"✅ ATR计算成功")
        print(f"📊 最新ATR: ${atr.iloc[-1]:,.2f}")
        print(f"📈 ATR范围: ${atr.min():,.2f} - ${atr.max():,.2f}")
        print()
        
        return atr
    else:
        print("❌ ATR计算失败")
        return None

def test_breakout_levels(df):
    """测试突破水平计算"""
    print("🧪 测试突破水平计算...")
    
    turtle_system = TurtleTradingSystem()
    
    # 计算突破水平
    upper_band, lower_band = turtle_system.calculate_breakout_levels(df, 20)
    
    if upper_band is not None and lower_band is not None:
        print(f"✅ 突破水平计算成功")
        print(f"📈 上轨: ${upper_band.iloc[-1]:,.2f}")
        print(f"📉 下轨: ${lower_band.iloc[-1]:,.2f}")
        print(f"📊 通道宽度: ${upper_band.iloc[-1] - lower_band.iloc[-1]:,.2f}")
        print()
        
        return upper_band, lower_band
    else:
        print("❌ 突破水平计算失败")
        return None, None

def test_signal_detection(df):
    """测试信号检测"""
    print("🧪 测试信号检测...")
    
    turtle_system = TurtleTradingSystem()
    
    # 检测信号
    signal = turtle_system.check_turtle_entry_signal(df)
    
    if signal:
        print(f"🔔 检测到 {signal['signal']} 信号!")
        print(f"💰 当前价格: ${signal['price']:,.2f}")
        print(f"📈 上轨: ${signal['upper_band']:,.2f}")
        print(f"📉 下轨: ${signal['lower_band']:,.2f}")
        print(f"📊 ATR: ${signal['atr']:,.2f}")
        if 'position_size' in signal:
            print(f"📦 建议仓位: {signal['position_size']:.4f} BTC")
        print()
    else:
        print("📊 当前无交易信号")
        print(f"💰 当前价格: ${df['close'].iloc[-1]:,.2f}")
        
        # 计算当前距离突破水平的距离
        upper_band, lower_band = turtle_system.calculate_breakout_levels(df, 20)
        current_price = df['close'].iloc[-1]
        
        distance_to_upper = ((upper_band.iloc[-1] - current_price) / current_price) * 100
        distance_to_lower = ((current_price - lower_band.iloc[-1]) / current_price) * 100
        
        print(f"📈 距离上轨: {distance_to_upper:.2f}%")
        print(f"📉 距离下轨: {distance_to_lower:.2f}%")
        print()

def test_dingtalk_config():
    """测试钉钉机器人配置"""
    print("🧪 测试钉钉机器人配置...")
    
    turtle_system = TurtleTradingSystem()
    
    # 检查钉钉机器人配置
    config = turtle_system.dingtalk_config
    
    print(f"🤖 Access Token: {'已配置' if config['access_token'] else '未配置'}")
    print(f"🔐 Secret: {'已配置' if config['secret'] else '未配置'}")
    print(f"📱 @手机号: {config['at_mobiles'] if config['at_mobiles'] else '未配置'}")
    
    if config['access_token']:
        print("✅ 钉钉机器人配置完整")
    else:
        print("⚠️ 钉钉机器人配置不完整，请检查 .env 文件")
        print("📝 请参考 email_config_example.txt 文件进行配置")
    print()

def main():
    """主测试函数"""
    print("🚀 海龟交易系统测试")
    print("=" * 50)
    
    # 测试钉钉机器人配置
    test_dingtalk_config()
    
    # 测试K线数据获取
    df = test_klines_data()
    if df is None:
        print("❌ K线数据获取失败，无法继续测试")
        return
    
    # 测试ATR计算
    test_atr_calculation(df)
    
    # 测试突破水平计算
    test_breakout_levels(df)
    
    # 测试信号检测
    test_signal_detection(df)
    
    print("✅ 测试完成!")
    print("📝 使用说明:")
    print("1. 配置钉钉机器人设置（参考 email_config_example.txt）")
    print("2. 运行 python turtle_trading_system.py 启动监控")
    print("3. 系统将每5分钟检查一次交易信号")
    print("4. 检测到信号时将发送钉钉通知")

if __name__ == "__main__":
    main() 