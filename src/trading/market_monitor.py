#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
市场监控模块
获取市值前100的数字货币交易对，管理K线数据，监听WebSocket
"""

import os
import json
import time
import logging
import pandas as pd
import threading
from datetime import datetime
from dotenv import load_dotenv
from binance.um_futures import UMFutures
from binance.websocket.um_futures.websocket_client import UMFuturesWebsocketClient
from ..notification.dingtalk_bot import DingTalkBot
from .turtle_system import TurtleTradingSystem
from .SYMBOLS import CUSTOM_SYMBOLS

# 加载环境变量
load_dotenv()

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("market_monitor.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class MarketMonitor:
    def __init__(self):
        """初始化市场监控器"""
        self.client = UMFutures()
        self.turtle_system = TurtleTradingSystem()
        self.dingtalk_bot = DingTalkBot()

        # 从环境变量获取配置
        self.kline_interval = os.getenv("KLINE_INTERVAL", "1h")  # K线间隔，默认1小时
        self.kline_limit = int(os.getenv("KLINE_LIMIT", "56"))  # K线数量，默认56条
        self.symbol_limit = int(os.getenv("SYMBOL_LIMIT", "50"))  # 交易对数量，默认50个

        self.exit_period = 20  # 出场突破周期
        self.entry_period = 50  # 入场突破周期

        logger.info(
            f"配置参数: interval={self.kline_interval}, limit={self.kline_limit}, symbol_limit={self.symbol_limit}"
        )

        # 数据存储目录
        self.data_dir = "data"
        self.klines_dir = os.path.join(self.data_dir, "klines")
        self.symbols_file = os.path.join(self.data_dir, "top_symbols.json")

        # 创建目录
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.klines_dir, exist_ok=True)

        # 交易对数据
        self.top_symbols = []
        self.symbol_klines = {}
        self.websocket_client = None

        # 线程控制
        self.running = False
        self.websocket_thread = None
        self.exit_signals_thread = None
        
        # WebSocket重连控制
        self.websocket_retry_count = 0
        self.max_websocket_retries = 3

    def get_top_symbols(self, limit=None):
        """获取用户自定义的交易对列表"""
        if limit is None:
            limit = self.symbol_limit

        try:
            # 获取自定义交易对列表
            custom_symbols = CUSTOM_SYMBOLS

            if custom_symbols:
                # 处理自定义交易对列表
                symbols = [
                    symbol.strip().upper()
                    for symbol in custom_symbols
                    if symbol and symbol.strip()
                ]
                logger.info(f"使用自定义交易对列表: {symbols}")
            else:
                # 如果没有自定义配置，使用常用交易对
                from config.symbols.usdt_symbols import COMMON_USDT_SYMBOLS

                symbols = COMMON_USDT_SYMBOLS[:limit]
                logger.info(f"使用常用交易对列表: {symbols}")

            # 验证交易对的有效性
            valid_symbols = []
            for symbol in symbols:
                try:
                    # 检查交易对是否存在
                    exchange_info = self.client.exchange_info()
                    symbol_exists = any(
                        s["symbol"] == symbol for s in exchange_info["symbols"]
                    )

                    if symbol_exists:
                        valid_symbols.append(symbol)
                    else:
                        logger.warning(f"交易对 {symbol} 不存在，已跳过")
                except Exception as e:
                    logger.error(f"验证交易对 {symbol} 时出错: {e}")
                    continue

            # 限制数量
            if len(valid_symbols) > limit:
                valid_symbols = valid_symbols[:limit]
                logger.info(f"交易对数量超过限制，已截取前{limit}个")

            # 保存到文件
            with open(self.symbols_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "timestamp": datetime.now().isoformat(),
                        "symbols": valid_symbols,
                        "count": len(valid_symbols),
                        "source": "custom" if custom_symbols else "common",
                    },
                    f,
                    ensure_ascii=False,
                    indent=2,
                )

            logger.info(f"成功获取{len(valid_symbols)}个有效交易对")
            return valid_symbols

        except Exception as e:
            logger.error(f"获取交易对失败: {e}")
            return []

    def get_symbol_klines(self, symbol, interval=None, limit=None):
        """获取单个交易对的K线数据"""
        if interval is None:
            interval = self.kline_interval
        if limit is None:
            limit = self.kline_limit

        try:
            klines = self.client.klines(symbol=symbol, interval=interval, limit=limit)

            # 转换为DataFrame
            df = pd.DataFrame(klines)
            df.columns = [
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
            ]
            # 数据类型转换
            numeric_columns = ["timestamp", "open", "high", "low", "close", "volume"]
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col])

            # 时间戳转换
            df["time"] = (
                pd.to_datetime(df["timestamp"], unit="ms", utc=True)
                .dt.tz_convert("Asia/Shanghai")
                .dt.strftime("%Y-%m-%d %H:%M:%S")
            )

            # 添加notified列
            df["notified"] = False

            return df[
                [
                    "timestamp",
                    "time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "notified",
                ]
            ]

        except Exception as e:
            logger.error(f"获取{symbol} K线数据失败: {e}")
            return None

    def save_klines_to_file(self, symbol, df):
        """保存K线数据到文件

        Args:
            symbol (str): 交易对符号
            df (pd.DataFrame): 要保存的K线数据
        """
        try:
            if df.empty:
                logger.warning(f"{symbol}数据为空，跳过保存")
                return

            filename = os.path.join(self.klines_dir, f"{symbol}_klines.csv")

            # 确保数据按时间戳排序
            df_sorted = df.sort_values("timestamp").reset_index(drop=True)

            # 保存到文件
            df_sorted.to_csv(filename, index=False, encoding="utf-8")
            logger.debug(f"保存{symbol} K线数据到{filename}: {len(df_sorted)}条记录")

        except Exception as e:
            logger.error(f"保存{symbol} K线数据失败: {e}")
            logger.error(f"DataFrame信息: shape={df.shape}, columns={list(df.columns)}")

    def update_klines_data(self, symbol, new_kline):
        """更新K线数据

        Args:
            symbol (str): 交易对符号
            new_kline (dict): 新的K线数据，包含k字段
        """
        try:
            # 确保symbol_klines中有该交易对的数据
            if symbol not in self.symbol_klines:
                self._load_symbol_data(symbol)
                if symbol not in self.symbol_klines:
                    logger.warning(f"无法加载{symbol}的历史K线数据")
                    return

            df = self.symbol_klines[symbol]

            # 解析新的K线数据
            kline_data = new_kline["k"]
            kline_timestamp = kline_data["t"]  # 毫秒时间戳

            last_kline = df.iloc[-1]

            notified = False

            if last_kline["timestamp"] == kline_timestamp:
                notified = last_kline["notified"]


            # 转换为本地时区的时间字符串
            kline_start_time = pd.to_datetime(
                kline_timestamp, unit="ms", utc=True
            ).tz_convert("Asia/Shanghai")
            kline_time_str = kline_start_time.strftime("%Y-%m-%d %H:%M:%S")

            # 准备新数据
            new_data = {
                "timestamp": kline_timestamp,
                "time": kline_time_str,
                "open": float(kline_data["o"]),
                "high": float(kline_data["h"]),
                "low": float(kline_data["l"]),
                "close": float(kline_data["c"]),
                "volume": float(kline_data["v"]),
                "notified": notified,  # 新K线默认未推送
            }

            # 检查K线是否已完成
            is_kline_completed = kline_data["x"]

            # 使用时间戳作为索引进行查找和更新
            if kline_timestamp in df["timestamp"].values:
                # 更新现有K线
                mask = df["timestamp"] == kline_timestamp
                for col, value in new_data.items():
                    df.loc[mask, col] = value
                logger.debug(f"更新{symbol}现有K线: {kline_time_str}")
            else:
                # 添加新K线
                new_row = pd.DataFrame([new_data])
                df = pd.concat([df, new_row], ignore_index=True)

                # 按时间戳排序
                df = df.sort_values("timestamp").reset_index(drop=True)

                # 限制数据量
                if len(df) > self.kline_limit:
                    df = df.tail(self.kline_limit).reset_index(drop=True)

                logger.debug(f"添加{symbol}新K线: {kline_time_str}")

            # 确保数据类型正确
            df["timestamp"] = df["timestamp"].astype(int)
            numeric_columns = ["open", "high", "low", "close", "volume"]
            for col in numeric_columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

            # 更新内存中的数据
            self.symbol_klines[symbol] = df

            # 保存到文件
            self.save_klines_to_file(symbol, df)

            # 记录更新信息
            if is_kline_completed:
                logger.info(
                    f"完成{symbol} K线更新: {kline_time_str} - 价格: {new_data['close']:.4f}"
                )

        except Exception as e:
            logger.error(f"更新{symbol} K线数据失败: {e}")
            logger.error(
                f"错误详情: symbol={symbol}, kline_data={new_kline.get('k', {}) if new_kline else 'N/A'}"
            )
            if "df" in locals():
                logger.error(
                    f"DataFrame信息: shape={df.shape}, columns={list(df.columns)}"
                )

    def _load_symbol_data(self, symbol):
        """加载交易对的历史数据

        Args:
            symbol (str): 交易对符号
        """
        try:
            filename = os.path.join(self.klines_dir, f"{symbol}_klines.csv")
            if os.path.exists(filename):
                df = pd.read_csv(filename, encoding="utf-8")

                # 确保包含所需列
                required_columns = [
                    "timestamp",
                    "time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "notified",  # 添加推送标识列
                ]
                missing_columns = [
                    col for col in required_columns if col not in df.columns
                ]
                if missing_columns:
                    logger.warning(f"{symbol}数据缺少列: {missing_columns}")
                    return

                # 数据类型转换
                df["timestamp"] = pd.to_numeric(df["timestamp"], errors="coerce")
                numeric_columns = ["open", "high", "low", "close", "volume"]
                for col in numeric_columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce")

                # 处理notified列，如果不存在则添加
                if "notified" not in df.columns:
                    df["notified"] = False
                else:
                    # 确保notified列是布尔类型
                    df["notified"] = df["notified"].astype(bool)

                # 按时间戳排序
                df = df.sort_values("timestamp").reset_index(drop=True)

                # 限制数据量
                if len(df) > self.kline_limit:
                    df = df.tail(self.kline_limit).reset_index(drop=True)

                self.symbol_klines[symbol] = df
                logger.info(f"成功加载{symbol}历史数据: {len(df)}条记录")
            else:
                logger.info(f"{symbol}历史数据文件不存在，将创建新数据")
                # 创建空的DataFrame
                self.symbol_klines[symbol] = pd.DataFrame(
                    {
                        "timestamp": [],
                        "time": [],
                        "open": [],
                        "high": [],
                        "low": [],
                        "close": [],
                        "volume": [],
                        "notified": [],  # 添加推送标识
                    }
                )

        except Exception as e:
            logger.error(f"加载{symbol}历史数据失败: {e}")
            # 创建空的DataFrame作为后备
            self.symbol_klines[symbol] = pd.DataFrame(
                {
                    "timestamp": [],
                    "time": [],
                    "open": [],
                    "high": [],
                    "low": [],
                    "close": [],
                    "volume": [],
                    "notified": [],  # 添加推送标识
                }
            )

    def check_turtle_signals(self, symbol):
        """检查海龟交易信号"""
        try:
            if symbol not in self.symbol_klines:
                return

            df = self.symbol_klines[symbol]
            if len(df) < 20:  # 数据不足
                return

            # 只检查最新的未推送K线
            latest_kline = df.iloc[-1]
            if latest_kline["notified"]:
                logger.debug(f"{symbol} 最新K线已推送过信号，跳过检查")
                return

            # 检查海龟交易信号
            signal = self.turtle_system.check_turtle_entry_signal(df)

            if signal:
                # 发送钉钉通知
                logger.info(f"海龟交易信号: {signal}")
                success = self.send_turtle_signal_notification(symbol, signal)

                if success:
                    # 标记该K线已推送
                    df.loc[df.index[-1], "notified"] = True
                    # 保存更新后的数据
                    self.save_klines_to_file(symbol, df)
                    # 更新内存中的数据 避免多次推送
                    self.symbol_klines[symbol] = df


                    logger.info(f"{symbol} K线已标记为已推送")

        except Exception as e:
            logger.error(f"检查{symbol}海龟信号失败: {e}")

    
    def check_turtle_signals_all(self):
        """检查海龟交易信号"""
        try:
            for symbol in self.top_symbols:
                self.check_turtle_signals(symbol)
                time.sleep(0.2)

        except Exception as e:
            logger.error(f"检查{symbol}海龟信号失败: {e}")


    def check_turtle_exit_signals(self):
        """检查海龟交易出场信号"""
        try:
            filename = os.path.join(self.data_dir, "quit.csv")

            # 读取quit.csv文件
            quit_df = pd.read_csv(filename, encoding="utf-8")

            for index, row in quit_df.iterrows():

                symbol_klines = pd.read_csv(
                    os.path.join(self.data_dir, f"klines/{row['symbol']}_klines.csv")
                )

                # 获取该symbol的记录
                direction = row["direction"]
                current_quit_price = row["quit"]
                entry_price = row["price"]

                # 获取过去10条K线的数据
                recent_klines = symbol_klines.tail(self.exit_period)
                highest_price = recent_klines["high"].max()
                lowest_price = recent_klines["low"].min()
                current_price = symbol_klines.iloc[-1]["close"]

                # 根据方向计算退出价格
                if direction == "BUY":
                    # 做多：使用过去10条K线的最低价格作为退出价格
                    exit_price = lowest_price
                    should_exit = current_quit_price < exit_price
                    exit_type = "止损"
                elif direction == "SELL":
                    # 做空：使用过去10条K线的最高价格作为退出价格
                    exit_price = highest_price
                    should_exit = current_quit_price > exit_price
                    exit_type = "止损"
                else:
                    logger.warning(f"{row['symbol']} 方向未知: {direction}")
                    return

                print(exit_price, current_quit_price, direction, should_exit)

                # 检查是否需要退出
                if should_exit:

                    # 发送钉钉通知
                    success = self.send_exit_signal_notification(
                        row["symbol"],
                        direction,
                        entry_price,
                        current_price,
                        exit_price,
                        highest_price,
                        lowest_price,
                        exit_type,
                    )

                    if success:
                        # 更新quit.csv中的quit价格和notified状态
                        quit_df.loc[index, "quit"] = exit_price

                        print(quit_df)

                        # 保存更新后的quit.csv
                        quit_df.to_csv(filename, index=False, encoding="utf-8")
                        logger.info(
                            f"{row['symbol']} 出场信号已发送并更新quit.csv，退出价格: {exit_price:.6f}"
                        )

        except Exception as e:
            logger.error(f"检查{row['symbol']}海龟交易出场信号失败: {e}")

    def send_turtle_signal_notification(self, symbol, signal):
        """发送海龟交易信号通知"""
        try:
            title = f"🐢 海龟交易信号 - {symbol}"

            # 转换numpy类型为Python原生类型
            price = float(signal["price"])
            upper_band = float(signal["upper_band"])
            lower_band = float(signal["lower_band"])
            atr = float(signal["atr"])

            # 处理时间戳 - 转换为可读格式
            if hasattr(signal["timestamp"], "strftime"):
                # 如果是pandas.Timestamp类型
                timestamp_str = signal["timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            else:
                # 如果是numpy.int64或其他数字类型，转换为datetime
                import pandas as pd

                timestamp_str = pd.to_datetime(signal["timestamp"], unit="ms").strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

            # 计算止损位
            stop_loss = (
                price - atr * 2 if signal["signal"] == "BUY" else price + atr * 2
            )

            text = f"""
- **交易对**: {symbol}
- **信号类型**: {'🟢 买入信号' if signal['signal'] == 'BUY' else '🔴 卖出信号'}
- **当前价格**: ${price:.6f}
- **上轨**: ${upper_band:.6f}
- **下轨**: ${lower_band:.6f}
- **ATR**: ${atr:.6f} 
- **K线间隔**: ${os.getenv("KLINE_INTERVAL", "1h")}
### 交易建议
- 止损位: ${stop_loss:.6f}

---
*自动检测于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
            """

            # 发送Markdown消息
            success = self.dingtalk_bot.send_markdown_message(
                title=title, text=text, at_all=False
            )

            if success:
                logger.info(f"海龟信号通知发送成功: {symbol} - {signal['signal']}")
                return True
            else:
                logger.error(f"海龟信号通知发送失败: {symbol}")
                return False

        except Exception as e:
            logger.error(f"发送海龟信号通知失败: {e}")
            return False

    def send_exit_signal_notification(
        self,
        symbol,
        direction,
        entry_price,
        current_price,
        exit_price,
        highest_price,
        lowest_price,
        exit_type,
    ):
        """发送出场信号通知"""
        try:
            title = f"🚪 海龟交易出场信号 - {symbol}"

            # 计算盈亏
            if direction == "BUY":
                profit_loss = ((current_price - entry_price) / entry_price) * 100
                profit_loss_text = (
                    f"{profit_loss:.2f}%" if profit_loss >= 0 else f"{profit_loss:.2f}%"
                )
            else:  # SELL
                profit_loss = ((entry_price - current_price) / entry_price) * 100
                profit_loss_text = (
                    f"{profit_loss:.2f}%" if profit_loss >= 0 else f"{profit_loss:.2f}%"
                )

            text = f"""
## 🚪 海龟交易出场信号

- **交易对**: {symbol}
- **交易方向**: {'🟢 做多' if direction == 'BUY' else '🔴 做空'}
- **出场类型**: {exit_type}
- **入场价格**: ${entry_price:.6f}
- **当前价格**: ${current_price:.6f}
- **退出价格**: ${exit_price:.6f}
- **盈亏**: {profit_loss_text}

### 价格信息
- **过去10条K线最高价**: ${highest_price:.6f}
- **过去10条K线最低价**: ${lowest_price:.6f}

### 出场条件
- **方向**: {direction}
- **触发条件**: {'当前价格 <= 最低价' if direction == 'BUY' else '当前价格 >= 最高价'}

---
*自动检测于 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
            """

            # 发送Markdown消息
            success = self.dingtalk_bot.send_markdown_message(
                title=title, text=text, at_all=False
            )

            if success:
                logger.info(f"出场信号通知发送成功: {symbol} - {direction}")
                return True
            else:
                logger.error(f"出场信号通知发送失败: {symbol}")
                return False

        except Exception as e:
            logger.error(f"发送出场信号通知失败: {e}")
            return False

    def websocket_message_handler(self, _, message):
        """WebSocket消息处理器"""
        try:
            data = json.loads(message)
            # 处理K线数据
            if "k" in data:
                symbol = data["s"]
                if symbol in self.top_symbols:
                    # 更新K线数据
                    self.update_klines_data(symbol, data)


        except Exception as e:
            logger.error(f"处理WebSocket消息失败: {e}")

    def start_websocket_monitor(self):
        """启动WebSocket监控"""
        try:
            logger.info("启动WebSocket监控...")
            proxies = {
                "http": "http://127.0.0.1:7890",
                "https": "http://127.0.0.1:7890",
            }
            # 创建WebSocket客户端
            self.websocket_client = UMFuturesWebsocketClient(
                on_message=self.websocket_message_handler,
                proxies=proxies,
                on_error=self.on_ws_error,
            )

            # 订阅所有交易对的K线数据
            for symbol in self.top_symbols:
                # 使用正确的方法名
                self.websocket_client.kline(
                    symbol=symbol.lower(), interval=self.kline_interval
                )
                time.sleep(0.2)  # 避免请求过快

            logger.info(f"已订阅{len(self.top_symbols)}个交易对的K线数据")
            
            # 重置重试计数器（连接成功）
            if self.websocket_retry_count > 0:
                logger.info(f"WebSocket连接成功，重置重试计数器 (之前重试了{self.websocket_retry_count}次)")
                self.websocket_retry_count = 0

            # 保持连接，但允许中断
            while self.running:
                time.sleep(1)

        except Exception as e:
            logger.error(f"WebSocket监控失败: {e}")
        finally:
            if self.websocket_client:
                self.websocket_client.stop()

    def on_ws_error(self, ws_client, e):
        """WebSocket错误处理函数"""
        logger.error(f"WebSocket错误: {e}")
        
        # 增加重试计数
        self.websocket_retry_count += 1
        
        if self.websocket_retry_count <= self.max_websocket_retries:
            logger.warning(f"WebSocket连接错误，第{self.websocket_retry_count}次重试 (最多{self.max_websocket_retries}次)")
            
            text = f"""
            WebSocket连接错误，第{self.websocket_retry_count}次重试 (最多{self.max_websocket_retries}次)
            """

            self.dingtalk_bot.send_markdown_message(
                title="WebSocket连接错误",
                text=text,
                at_all=False
            )

            # 停止当前WebSocket客户端
            if self.websocket_client:
                try:
                    self.websocket_client.stop()
                except Exception as stop_error:
                    logger.error(f"停止WebSocket客户端时出错: {stop_error}")
            
            # 等待一段时间后重启
            time.sleep(5)
            
            # 重启WebSocket监控线程
            if self.running:
                logger.info("重启WebSocket监控线程...")
                
                # 如果原线程还在运行，等待它结束
                if self.websocket_thread and self.websocket_thread.is_alive():
                    self.websocket_thread.join(timeout=10)
                
                # 创建新的WebSocket监控线程
                self.websocket_thread = threading.Thread(
                    target=self.websocket_monitor_thread,
                    name="WebSocketThread",
                    daemon=True,
                )
                self.websocket_thread.start()
                logger.info("WebSocket监控线程已重启")
        else:
            logger.error(f"WebSocket重连失败，已达到最大重试次数({self.max_websocket_retries})，停止重连")
            # 停止整个监控系统
            self.running = False

    def websocket_monitor_thread(self):
        """WebSocket监控线程函数"""
        self.start_websocket_monitor()

    def exit_signals_loop(self):
        """出场信号检查循环"""
        try:
            while self.running:
                logger.info("检查信号...")
                self.check_turtle_signals_all()
                self.check_turtle_exit_signals()
                time.sleep(60)  # 每60秒检查一次
        except Exception as e:
            logger.error(f"出场信号检查失败: {e}")

    def run_exit_signals_thread(self):
        """出场信号检查线程函数"""
        self.exit_signals_loop()

    def initialize_data(self):
        """初始化数据"""
        try:
            logger.info("开始初始化数据...")

            # 获取交易对列表
            self.top_symbols = self.get_top_symbols()

            if not self.top_symbols:
                logger.error("无法获取交易对列表")
                return False

            # 获取每个交易对的K线数据
            logger.info("获取K线数据...")
            for i, symbol in enumerate(self.top_symbols):
                logger.info(f"获取{symbol} K线数据 ({i+1}/{len(self.top_symbols)})")

                df = self.get_symbol_klines(symbol)
                if df is not None:
                    self.symbol_klines[symbol] = df
                    self.save_klines_to_file(symbol, df)

                time.sleep(0.1)  # 避免请求过快

            logger.info(f"数据初始化完成，共处理{len(self.symbol_klines)}个交易对")
            return True

        except Exception as e:
            logger.error(f"数据初始化失败: {e}")
            return False

    def run(self):
        """运行市场监控"""
        try:
            logger.info("🚀 启动市场监控系统")

            # 初始化数据
            if not self.initialize_data():
                logger.error("数据初始化失败，程序退出")
                return

            # 设置运行标志
            self.running = True

            # 启动出场信号检查线程
            self.exit_signals_thread = threading.Thread(
                target=self.run_exit_signals_thread,
                name="ExitSignalsThread",
                daemon=True,
            )
            self.exit_signals_thread.start()
            logger.info("出场信号检查线程已启动")

            # 启动WebSocket监控线程
            self.websocket_thread = threading.Thread(
                target=self.websocket_monitor_thread,
                name="WebSocketThread",
                daemon=True,
            )
            self.websocket_thread.start()
            logger.info("WebSocket监控线程已启动")

            # 主线程等待
            try:
                while self.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("收到中断信号，正在停止...")
                self.running = False

        except Exception as e:
            logger.error(f"程序运行出错: {e}")
        finally:
            # 停止所有线程
            self.running = False

            # 等待线程结束
            if self.websocket_thread and self.websocket_thread.is_alive():
                self.websocket_thread.join(timeout=5)
            if self.exit_signals_thread and self.exit_signals_thread.is_alive():
                self.exit_signals_thread.join(timeout=5)

            if self.websocket_client:
                self.websocket_client.stop()
            logger.info("市场监控系统已停止")


def main():
    """主函数"""
    monitor = MarketMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
