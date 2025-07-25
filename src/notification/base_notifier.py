# -*- coding: utf-8 -*-
"""
通知基类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

class BaseNotifier(ABC):
    """通知基类"""
    
    def __init__(self, config: Dict[str, Any]):
        """初始化通知器"""
        self.config = config
        self.is_configured = self._check_config()
    
    @abstractmethod
    def _check_config(self) -> bool:
        """检查配置是否完整"""
        pass
    
    @abstractmethod
    def send_text_message(self, content: str, **kwargs) -> bool:
        """发送文本消息"""
        pass
    
    @abstractmethod
    def send_markdown_message(self, title: str, text: str, **kwargs) -> bool:
        """发送Markdown消息"""
        pass
    
    def send_signal_notification(self, signal_info: Dict[str, Any]) -> bool:
        """发送交易信号通知"""
        if not self.is_configured:
            print("通知器配置不完整，跳过通知发送")
            return False
        
        try:
            print(f"signal_info: {signal_info}")

            # 转换numpy类型为Python原生类型
            price = float(signal_info['price'])
            upper_band = float(signal_info['upper_band'])
            lower_band = float(signal_info['lower_band'])
            atr = float(signal_info['atr'])
            position_size = float(signal_info.get('position_size', 0)) if signal_info.get('position_size') is not None else None
            
            # 构建消息内容
            title = f"🐢 海龟交易信号 - BTC {signal_info['signal']} 信号"
            
            text = f"""
# 🐢 海龟交易法 BTC 交易信号

## 📊 信号信息
- **信号类型**: {signal_info['signal']}
- **当前价格**: ${price:,.2f}
- **上轨突破位**: ${upper_band:,.2f}
- **下轨突破位**: ${lower_band:,.2f}
- **ATR**: ${atr:,.2f}
- **信号时间**: {signal_info['timestamp']}

{f"## 📦 仓位建议" + chr(10) + f"- **建议仓位**: {position_size:.4f} BTC" if position_size is not None else ''}

## ⚠️ 风险提示
> 数字货币交易存在风险，请谨慎投资

---
*来自海龟交易法监控系统*
            """
            
            return self.send_markdown_message(title, text)
            
        except Exception as e:
            print(f"发送信号通知失败: {e}")
            return False
    
    def send_status_notification(self, status: str, details: Optional[Dict[str, Any]] = None) -> bool:
        """发送状态通知"""
        if not self.is_configured:
            return False
        
        try:
            title = f"📊 系统状态通知"
            
            text = f"""
# 📊 系统状态通知

## 🔍 状态信息
- **状态**: {status}
- **时间**: {details.get('timestamp', 'N/A') if details else 'N/A'}

{f"## 📈 详细信息" + chr(10) + "\n".join([f"- **{k}**: {v}" for k, v in details.items() if k != 'timestamp']) if details else ""}

---
*来自海龟交易法监控系统*
            """
            
            return self.send_markdown_message(title, text)
            
        except Exception as e:
            print(f"发送状态通知失败: {e}")
            return False 