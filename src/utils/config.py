# -*- coding: utf-8 -*-
"""
配置管理模块
"""

import os
from dotenv import load_dotenv

class Config:
    """配置管理类"""
    
    def __init__(self):
        """初始化配置"""
        # 加载环境变量
        load_dotenv()
        
        # Binance API配置
        self.binance_api_key = os.getenv('BINANCE_API_KEY')
        self.binance_secret_key = os.getenv('BINANCE_SECRET_KEY')
        
        # 钉钉机器人配置
        self.dingtalk_access_token = os.getenv('DINGTALK_ACCESS_TOKEN')
        self.dingtalk_secret = os.getenv('DINGTALK_SECRET')
        self.dingtalk_at_mobiles = os.getenv('DINGTALK_AT_MOBILES', '').split(',') if os.getenv('DINGTALK_AT_MOBILES') else []
        
        # 海龟交易法参数
        self.entry_period = int(os.getenv('ENTRY_PERIOD', '20'))
        self.exit_period = int(os.getenv('EXIT_PERIOD', '10'))
        self.atr_period = int(os.getenv('ATR_PERIOD', '20'))
        self.position_size = float(os.getenv('POSITION_SIZE', '0.02'))
        
        # 监控参数
        self.check_interval = int(os.getenv('CHECK_INTERVAL', '300'))
        self.signal_cooldown = int(os.getenv('SIGNAL_COOLDOWN', '3600'))
    
    def get_dingtalk_config(self):
        """获取钉钉机器人配置"""
        return {
            'access_token': self.dingtalk_access_token,
            'secret': self.dingtalk_secret,
            'at_mobiles': self.dingtalk_at_mobiles
        }
    
    def get_trading_config(self):
        """获取交易配置"""
        return {
            'entry_period': self.entry_period,
            'exit_period': self.exit_period,
            'atr_period': self.atr_period,
            'position_size': self.position_size
        }
    
    def get_monitor_config(self):
        """获取监控配置"""
        return {
            'check_interval': self.check_interval,
            'signal_cooldown': self.signal_cooldown
        }
    
    def is_dingtalk_configured(self):
        """检查钉钉机器人是否配置完整"""
        return bool(self.dingtalk_access_token)
    
    def is_binance_configured(self):
        """检查Binance API是否配置完整"""
        return bool(self.binance_api_key and self.binance_secret_key) 