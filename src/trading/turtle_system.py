#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
海龟交易法 BTC 交易信号检测系统
基于海龟交易法判断BTC买入信号并发送邮件通知
"""

import time
import pandas as pd
import numpy as np
from binance.um_futures import UMFutures
from dotenv import load_dotenv
import os

# 加载环境变量
load_dotenv()


class TurtleTradingSystem:
    def __init__(self):
        """初始化海龟交易系统"""
        # 初始化 Binance 期货客户端
        self.client = UMFutures()

        # 海龟交易法参数
        self.entry_period = 50  # 入场突破周期
        self.exit_period = 20  # 出场突破周期
        self.atr_period = 20  # ATR周期
        self.position_size = 0.02  # 仓位大小（2%）

        # 钉钉机器人配置
        self.dingtalk_config = {
            "access_token": os.getenv("DINGTALK_ACCESS_TOKEN"),
            "secret": os.getenv("DINGTALK_SECRET"),
            "at_mobiles": (
                os.getenv("DINGTALK_AT_MOBILES", "").split(",")
                if os.getenv("DINGTALK_AT_MOBILES")
                else []
            ),
        }

        # 交易状态
        self.last_signal_time = None
        self.signal_cooldown = 3600  # 信号冷却时间（秒）

    def get_klines(self, symbol="BTCUSDT", interval="1h", limit=56):
        """
        获取K线数据

        Args:
            symbol: 交易对
            interval: K线间隔 (1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M)
            limit: 获取数量

        Returns:
            DataFrame: 包含OHLCV数据的DataFrame
        """
        try:
            klines = self.client.klines(symbol=symbol, interval=interval, limit=limit)

            # 转换为DataFrame
            df = pd.DataFrame(
                klines,
                columns=[
                    "timestamp",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "quote_volume",
                    "trades",
                    "taker_buy_base",
                    "taker_buy_quote",
                    "ignore",
                ],
            )

            # 数据类型转换
            numeric_columns = ["open", "high", "low", "close", "volume"]
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])

            # 时间戳转换 - 转换为本地时间
            df["timestamp"] = pd.to_datetime(
                df["timestamp"], unit="ms", utc=True
            ).dt.tz_convert("Asia/Shanghai")

            return df[["timestamp", "open", "high", "low", "close", "volume"]]

        except Exception as e:
            print(f"获取K线数据失败: {e}")
            return None

    def calculate_atr(self, df, period=20):
        """
        计算平均真实波幅 (ATR)

        Args:
            df: 包含OHLC数据的DataFrame
            period: ATR计算周期

        Returns:
            Series: ATR值（保留两位小数）
        """
        high = df["high"]
        low = df["low"]
        close = df["close"]

        # 计算真实波幅
        tr1 = high - low
        tr2 = abs(high - close.shift(1))
        tr3 = abs(low - close.shift(1))

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # 计算ATR
        atr = tr.rolling(window=period).mean()

        # 保留6位小数
        atr = atr.round(6)

        return atr

    def calculate_breakout_levels(self, df, period=20):
        """
        计算突破水平（基于历史数据，不包含当前K线）

        Args:
            df: 包含OHLC数据的DataFrame
            period: 突破周期

        Returns:
            tuple: (上轨, 下轨)
        """
        # 计算唐奇安通道 - 使用历史数据计算突破价
        # 对于每个位置，使用前period个K线计算最高价和最低价
        upper_band = df["high"].rolling(window=period, min_periods=period).max()
        lower_band = df["low"].rolling(window=period, min_periods=period).min()

        return upper_band, lower_band

    def get_historical_breakout_levels(self, df, period=20):
        """
        获取基于历史数据的突破水平（排除当前K线）

        Args:
            df: 包含OHLC数据的DataFrame
            period: 突破周期

        Returns:
            tuple: (上轨, 下轨)
        """
        if len(df) <= period:
            return None, None

        # 使用前period个K线计算突破价（排除当前K线）
        historical_data = df.iloc[:-1]  # 排除当前K线

        if len(historical_data) < period:
            return None, None

        # 计算历史数据的最高价和最低价
        upper_band = (
            historical_data["high"]
            .rolling(window=period, min_periods=period)
            .max()
            .iloc[-1]
        )
        lower_band = (
            historical_data["low"]
            .rolling(window=period, min_periods=period)
            .min()
            .iloc[-1]
        )

        return upper_band, lower_band

    def check_turtle_entry_signal(self, df):
        """
        检查海龟交易法入场信号

        Args:
            df: 包含OHLC数据的DataFrame

        Returns:
            dict: 信号信息
        """
        if len(df) < max(self.entry_period, self.atr_period):
            return None

        # 计算ATR
        df["atr"] = self.calculate_atr(df, self.atr_period)

        # 获取基于历史数据的突破水平（排除当前K线）
        current_upper, current_lower = self.get_historical_breakout_levels(
            df, self.entry_period
        )

        # 获取最新数据
        current_price = df["close"].iloc[-1]
        current_atr = df["atr"].iloc[-1]

        # 检查突破价是否有效
        if current_upper is None or current_lower is None or pd.isna(current_atr):
            return None

        # 获取前一个K线的价格，用于确认突破
        prev_price = df["close"].iloc[-2] if len(df) > 1 else current_price

        # 检查买入信号（突破上轨）
        # 确保当前价格突破上轨，且前一价格未突破
        if current_price > current_upper and prev_price <= current_upper:
            # 计算仓位大小
            account_balance = 10000  # 假设账户余额，实际应该从API获取
            position_size = (account_balance * self.position_size) / current_atr

            return {
                "signal": "BUY",
                "price": current_price,
                "upper_band": current_upper,
                "lower_band": current_lower,
                "atr": current_atr,
                "position_size": position_size,
                "timestamp": df["timestamp"].iloc[-1],
            }

        # 检查卖出信号（突破下轨）
        # 确保当前价格突破下轨，且前一价格未突破
        elif current_price < current_lower and prev_price >= current_lower:
            return {
                "signal": "SELL",
                "price": current_price,
                "upper_band": current_upper,
                "lower_band": current_lower,
                "atr": current_atr,
                "timestamp": df["timestamp"].iloc[-1],
            }

        return None


    def send_dingtalk_notification(self, signal_info):
        """
        发送钉钉机器人通知

        Args:
            signal_info: 信号信息字典
        """
        if not self.dingtalk_config["access_token"]:
            print("钉钉机器人配置不完整，跳过通知发送")
            return False

        try:
            # 导入钉钉机器人类
            from src.notification.dingtalk_bot import DingTalkBot

            # 创建机器人实例
            bot = DingTalkBot()

            if not bot.access_token:
                print("钉钉机器人初始化失败")
                return False

            # 转换numpy类型为Python原生类型
            price = float(signal_info["price"])
            upper_band = float(signal_info["upper_band"])
            lower_band = float(signal_info["lower_band"])
            atr = float(signal_info["atr"])
            position_size = (
                float(signal_info.get("position_size", 0))
                if signal_info.get("position_size") is not None
                else None
            )

            # 构建消息内容
            title = f"🐢 海龟交易信号 - BTC {signal_info['signal']} 信号"

            # Markdown格式的消息内容
            text = f"""
                # 🐢 海龟交易法 BTC 交易信号

                ## 📊 信号信息
                - **信号类型**: {signal_info['signal']}
                - **当前价格**: ${price:,.2f}
                - **上轨突破位**: ${upper_band:,.2f}
                - **下轨突破位**: ${lower_band:,.2f}
                - **ATR**: ${atr:,.2f}
                - **信号时间**: {signal_info['timestamp']}

                {f"## 📦 仓位建议\n- **建议仓位**: {position_size:.4f} BTC" if position_size is not None else ''}

                ## ⚠️ 风险提示
                > 数字货币交易存在风险，请谨慎投资

                ---
                *来自海龟交易法监控系统*
            """

            # 发送Markdown消息
            success = bot.send_markdown_message(
                title=title,
                text=text,
                at_mobiles=(
                    self.dingtalk_config["at_mobiles"]
                    if self.dingtalk_config["at_mobiles"]
                    else None
                ),
            )

            if success:
                print(f"✅ 钉钉通知发送成功 - {signal_info['signal']} 信号")
                return True
            else:
                print(f"❌ 钉钉通知发送失败")
                return False

        except Exception as e:
            print(f"❌ 钉钉通知发送出错: {e}")
            return False

    def should_send_signal(self):
        """
        检查是否应该发送信号（避免重复信号）

        Returns:
            bool: 是否应该发送信号
        """
        if self.last_signal_time is None:
            return True

        time_since_last = time.time() - self.last_signal_time
        return time_since_last > self.signal_cooldown

    def run_turtle_trading_monitor(
        self, symbol="BTCUSDT", interval="1h", check_interval=300
    ):
        """
        运行海龟交易监控

        Args:
            symbol: 交易对
            interval: K线间隔
            check_interval: 检查间隔（秒）
        """
        print(f"🚀 启动海龟交易法监控系统")
        print(f"📊 监控交易对: {symbol}")
        print(f"⏰ K线间隔: {interval}")
        print(f"🔄 检查间隔: {check_interval}秒")
        print("=" * 60)

        while True:
            try:
                # 获取K线数据
                df = self.get_klines(symbol, interval, 56)
                if df is None:
                    print("❌ 无法获取K线数据，等待下次检查...")
                    time.sleep(check_interval)
                    continue

                # 检查交易信号
                signal = self.check_turtle_entry_signal(df)

                if signal and self.should_send_signal():
                    # 转换numpy类型为Python原生类型用于显示
                    price = float(signal["price"])
                    upper_band = float(signal["upper_band"])
                    lower_band = float(signal["lower_band"])
                    atr = float(signal["atr"])

                    print(f"🔔 检测到 {signal['signal']} 信号!")
                    print(f"   价格: ${price:,.2f}")
                    print(f"   上轨: ${upper_band:,.2f}")
                    print(f"   下轨: ${lower_band:,.2f}")
                    print(f"   ATR: ${atr:,.2f}")

                    # 发送钉钉通知
                    if self.send_dingtalk_notification(signal):
                        self.last_signal_time = time.time()

                    print("-" * 40)
                else:
                    current_price = df["close"].iloc[-1]
                    current_time = df["timestamp"].iloc[-1]
                    # 格式化时间，处理不同类型的时间戳
                    if hasattr(current_time, "strftime"):
                        time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        # 如果是numpy.int64或其他数字类型，转换为datetime
                        time_str = pd.to_datetime(current_time, unit="ms").strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                    print(f"⏰ {time_str} - 当前价格: ${current_price:,.2f} - 无信号")

                # 等待下次检查
                time.sleep(check_interval)

            except KeyboardInterrupt:
                print("\n👋 监控已停止")
                break
            except Exception as e:
                print(f"❌ 监控出错: {e}")
                time.sleep(check_interval)


def main():
    """主函数"""


if __name__ == "__main__":
    main()
