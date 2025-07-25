#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人测试脚本
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from src.notification.dingtalk_bot import DingTalkBot
from src.utils.config import Config
from datetime import datetime

def test_dingtalk_bot():
    """测试钉钉机器人功能"""
    print("🤖 钉钉机器人测试")
    print("=" * 40)
    
    # 加载配置
    config = Config()
    
    # 检查配置
    if not config.is_dingtalk_configured():
        print("❌ 钉钉机器人配置不完整")
        print("📝 请参考 config/templates/.env.template 进行配置")
        return
    
    # 创建机器人实例
    bot = DingTalkBot()
    
    if not bot.is_configured:
        print("❌ 钉钉机器人初始化失败")
        return
    
    print()
    
    # 测试1: 发送简单文本消息
    print("🧪 测试1: 发送简单文本消息")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text_content = f"🤖 钉钉机器人测试消息 ⏰ 发送时间: {current_time} ✅ 这是一条测试消息"
    
    success = bot.send_text_message(text_content)
    print(f"结果: {'成功' if success else '失败'}")
    print("-" * 40)
    
    # 测试2: 发送Markdown消息
    print("🧪 测试2: 发送Markdown消息")
    markdown_title = "🐢 海龟交易法信号测试"
    markdown_text = f"""
# 🐢 海龟交易法信号测试

## 📊 当前状态
- **时间**: {current_time}
- **状态**: 系统正常运行
- **测试**: Markdown格式消息

## 📈 交易信号
- **BTC价格**: $43,250.50
- **信号类型**: 无信号
- **上轨**: $43,450.00
- **下轨**: $42,800.00

## ⚠️ 风险提示
> 数字货币交易存在风险，请谨慎投资

---
*来自海龟交易法监控系统*
    """
    
    success = bot.send_markdown_message(markdown_title, markdown_text)
    print(f"结果: {'成功' if success else '失败'}")
    print("-" * 40)
    
    # 测试3: 发送信号通知
    print("🧪 测试3: 发送信号通知")
    signal_info = {
        'signal': 'BUY',
        'price': 43250.50,
        'upper_band': 43450.00,
        'lower_band': 42800.00,
        'atr': 850.00,
        'position_size': 0.5,
        'timestamp': current_time
    }
    
    success = bot.send_signal_notification(signal_info)
    print(f"结果: {'成功' if success else '失败'}")
    print("-" * 40)
    
    print("✅ 钉钉机器人测试完成!")

if __name__ == "__main__":
    test_dingtalk_bot() 