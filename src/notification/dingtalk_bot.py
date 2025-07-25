#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
钉钉机器人消息推送测试脚本
用于测试钉钉机器人的消息推送功能
"""

import requests
import json
import time
import hmac
import hashlib
import base64
import urllib.parse
from datetime import datetime
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()

from .base_notifier import BaseNotifier

class DingTalkBot(BaseNotifier):
    def __init__(self, config=None):
        """初始化钉钉机器人"""
        if config is None:
            from ..utils.config import Config
            config = Config().get_dingtalk_config()
        
        self.access_token = config.get('access_token')
        self.secret = config.get('secret')
        self.at_mobiles = config.get('at_mobiles', [])
        
        super().__init__(config)
        
        if self.access_token:
            # 构建webhook URL
            self.webhook_url = f"https://oapi.dingtalk.com/robot/send?access_token={self.access_token}"
            
            print(f"✅ 钉钉机器人初始化成功")
            print(f"🔗 Webhook URL: {self.webhook_url}")
            print(f"🔐 是否使用签名: {'是' if self.secret else '否'}")
        else:
            print("❌ 未配置钉钉机器人 access_token")
    
    def _check_config(self) -> bool:
        """检查配置是否完整"""
        return bool(self.access_token)

    def get_sign(self):
        """生成签名"""
        if not self.secret:
            return None
            
        timestamp = str(round(time.time() * 1000))
        string_to_sign = f'{timestamp}\n{self.secret}'
        
        # 使用HmacSHA256算法计算签名
        hmac_code = hmac.new(
            self.secret.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def send_text_message(self, content, at_mobiles=None, at_all=False):
        """
        发送文本消息
        
        Args:
            content: 消息内容
            at_mobiles: 要@的手机号列表
            at_all: 是否@所有人
        """
        try:
            # 构建消息内容
            message = {
                "msgtype": "text",
                "text": {
                    "content": content
                },
                "at": {
                    "atMobiles": at_mobiles or [],
                    "isAtAll": at_all
                }
            }
            
            # 获取签名
            sign_info = self.get_sign()
            if sign_info:
                timestamp, sign = sign_info
                url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
            else:
                url = self.webhook_url
            
            # 发送请求
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json.dumps(message), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print(f"✅ 文本消息发送成功")
                    return True
                else:
                    print(f"❌ 文本消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 发送文本消息出错: {e}")
            return False

    def send_markdown_message(self, title, text, at_mobiles=None, at_all=False):
        """
        发送Markdown消息
        
        Args:
            title: 消息标题
            text: Markdown格式的消息内容
            at_mobiles: 要@的手机号列表
            at_all: 是否@所有人
        """
        try:
            # 构建消息内容
            message = {
                "msgtype": "markdown",
                "markdown": {
                    "title": title,
                    "text": text
                },
                "at": {
                    "atMobiles": at_mobiles or [],
                    "isAtAll": at_all
                }
            }
            
            # 获取签名
            sign_info = self.get_sign()
            if sign_info:
                timestamp, sign = sign_info
                url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
            else:
                url = self.webhook_url
            
            # 发送请求
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json.dumps(message), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print(f"✅ Markdown消息发送成功")
                    return True
                else:
                    print(f"❌ Markdown消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 发送Markdown消息出错: {e}")
            return False

    def send_link_message(self, title, text, message_url, pic_url=None):
        """
        发送链接消息
        
        Args:
            title: 消息标题
            text: 消息内容
            message_url: 点击消息跳转的URL
            pic_url: 图片URL（可选）
        """
        try:
            # 构建消息内容
            message = {
                "msgtype": "link",
                "link": {
                    "title": title,
                    "text": text,
                    "messageUrl": message_url,
                    "picUrl": pic_url or ""
                }
            }
            
            # 获取签名
            sign_info = self.get_sign()
            if sign_info:
                timestamp, sign = sign_info
                url = f"{self.webhook_url}&timestamp={timestamp}&sign={sign}"
            else:
                url = self.webhook_url
            
            # 发送请求
            headers = {'Content-Type': 'application/json'}
            response = requests.post(url, data=json.dumps(message), headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    print(f"✅ 链接消息发送成功")
                    return True
                else:
                    print(f"❌ 链接消息发送失败: {result.get('errmsg')}")
                    return False
            else:
                print(f"❌ 请求失败，状态码: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ 发送链接消息出错: {e}")
            return False

def test_dingtalk_bot():
    """测试钉钉机器人功能"""
    print("🤖 钉钉机器人消息推送测试")
    print("=" * 50)
    
    # 创建钉钉机器人实例
    bot = DingTalkBot()
    
    if not bot.access_token:
        print("❌ 请在 .env 文件中配置 DINGTALK_ACCESS_TOKEN")
        return
    
    print()
    
    # 测试1: 发送简单文本消息
    print("🧪 测试1: 发送简单文本消息")
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text_content = f"🤖 钉钉机器人测试消息\n⏰ 发送时间: {current_time}\n✅ 这是一条测试消息"
    
    success = bot.send_text_message(text_content)
    print(f"结果: {'成功' if success else '失败'}")
    print("-" * 40)
    
    # 等待1秒
    time.sleep(1)
    
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
    
    # 等待1秒
    time.sleep(1)
    
    # 测试3: 发送链接消息
    print("🧪 测试3: 发送链接消息")
    link_title = "📊 Binance BTC价格"
    link_text = f"点击查看BTC实时价格信息\n当前时间: {current_time}"
    link_url = "https://www.binance.com/zh-CN/price/bitcoin"
    pic_url = "https://cryptologos.cc/logos/bitcoin-btc-logo.png"
    
    success = bot.send_link_message(link_title, link_text, link_url, pic_url)
    print(f"结果: {'成功' if success else '失败'}")
    print("-" * 40)
    
    # 等待1秒
    time.sleep(1)
    
    # 测试4: 发送@消息
    print("🧪 测试4: 发送@消息（需要配置手机号）")
    at_mobiles = os.getenv('DINGTALK_AT_MOBILES', '').split(',') if os.getenv('DINGTALK_AT_MOBILES') else []
    
    if at_mobiles:
        at_content = f"🔔 这是一条@消息测试\n⏰ 时间: {current_time}\n📱 已@指定用户"
        success = bot.send_text_message(at_content, at_mobiles=at_mobiles)
        print(f"结果: {'成功' if success else '失败'}")
    else:
        print("⚠️ 未配置 @手机号，跳过@消息测试")
        print("💡 可在 .env 中配置 DINGTALK_AT_MOBILES=手机号1,手机号2")
    
    print("-" * 40)
    
    print("✅ 钉钉机器人测试完成!")
    print("\n📝 使用说明:")
    print("1. 确保 .env 文件中配置了正确的钉钉机器人信息")
    print("2. 如需@特定用户，请在 .env 中配置 DINGTALK_AT_MOBILES")
    print("3. 建议配置 DINGTALK_SECRET 以提高安全性")

def main():
    """主函数"""
    try:
        test_dingtalk_bot()
    except KeyboardInterrupt:
        print("\n👋 测试被用户中断")
    except Exception as e:
        print(f"❌ 测试出错: {e}")

if __name__ == "__main__":
    main() 