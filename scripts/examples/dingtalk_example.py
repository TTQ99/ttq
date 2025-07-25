#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人使用示例
演示如何使用钉钉机器人发送不同类型的消息
"""

from dingtalk_bot_test import DingTalkBot
from datetime import datetime

def example_usage():
    """钉钉机器人使用示例"""
    print("🤖 钉钉机器人使用示例")
    print("=" * 40)
    
    # 创建机器人实例
    bot = DingTalkBot()
    
    if not bot.access_token:
        print("❌ 请先在 .env 文件中配置钉钉机器人信息")
        print("📝 配置示例:")
        print("DINGTALK_ACCESS_TOKEN=your_access_token")
        print("DINGTALK_SECRET=your_secret")
        print("DINGTALK_AT_MOBILES=手机号1,手机号2")
        return
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print("📱 开始发送示例消息...")
    print()
    
    # 示例1: 发送简单文本消息
    print("📝 示例1: 发送文本消息")
    text_msg = f"""
🤖 钉钉机器人测试
⏰ 时间: {current_time}
✅ 系统运行正常
📊 这是一条测试消息
    """
    bot.send_text_message(text_msg)
    print()
    
    # 示例2: 发送Markdown格式消息
    print("📝 示例2: 发送Markdown消息")
    markdown_title = "🐢 海龟交易法监控"
    markdown_text = f"""
# 🐢 海龟交易法监控系统

## 📊 系统状态
- **运行时间**: {current_time}
- **状态**: ✅ 正常运行
- **监控对象**: BTCUSDT

## 📈 当前数据
- **BTC价格**: $43,250.50
- **24h涨跌**: +2.5%
- **成交量**: 1,234.56 BTC

## 🔔 交易信号
- **信号类型**: 无信号
- **上轨**: $43,450.00
- **下轨**: $42,800.00
- **ATR**: $850.00

---
*来自海龟交易法监控系统*
    """
    bot.send_markdown_message(markdown_title, markdown_text)
    print()
    
    # 示例3: 发送链接消息
    print("📝 示例3: 发送链接消息")
    link_title = "📊 查看BTC实时价格"
    link_text = f"点击查看Binance上的BTC实时价格信息\n当前时间: {current_time}"
    link_url = "https://www.binance.com/zh-CN/price/bitcoin"
    pic_url = "https://cryptologos.cc/logos/bitcoin-btc-logo.png"
    
    bot.send_link_message(link_title, link_text, link_url, pic_url)
    print()
    
    # 示例4: 发送@消息（如果配置了手机号）
    print("📝 示例4: 发送@消息")
    import os
    at_mobiles = os.getenv('DINGTALK_AT_MOBILES', '').split(',') if os.getenv('DINGTALK_AT_MOBILES') else []
    
    if at_mobiles and at_mobiles[0]:  # 确保不是空字符串
        at_msg = f"""
🔔 重要通知
⏰ 时间: {current_time}
📱 这是一条@消息测试
⚠️ 请及时查看交易信号
        """
        bot.send_text_message(at_msg, at_mobiles=at_mobiles)
    else:
        print("⚠️ 未配置@手机号，跳过@消息示例")
        print("💡 可在.env中配置 DINGTALK_AT_MOBILES=手机号1,手机号2")
    
    print()
    print("✅ 示例消息发送完成!")
    print("📝 使用提示:")
    print("1. 确保钉钉机器人配置正确")
    print("2. 注意消息发送频率限制")
    print("3. 可以根据需要自定义消息内容")

if __name__ == "__main__":
    example_usage() 