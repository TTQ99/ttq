#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数字货币合约价格查询 Demo
使用 Binance Futures Connector Python 库
"""

import time
import json
from datetime import datetime
from binance.um_futures import UMFutures
from binance.cm_futures import CMFutures
from binance.error import ClientError, ServerError


class FuturesPriceDemo:
    def __init__(self):
        """初始化期货价格查询 demo"""
        # 初始化 USDT-M 期货客户端
        self.um_futures_client = UMFutures()
        
        # 初始化 COIN-M 期货客户端
        self.cm_futures_client = CMFutures()
        
        # 常用交易对列表
        self.usdt_symbols = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'SOLUSDT']
        self.coin_symbols = ['BTCUSD_PERP', 'ETHUSD_PERP', 'BNBUSD_PERP']
    
    def get_server_time(self):
        """获取服务器时间"""
        try:
            um_time = self.um_futures_client.time()
            cm_time = self.cm_futures_client.time()
            
            print("=== 服务器时间 ===")
            print(f"USDT-M 服务器时间: {datetime.fromtimestamp(um_time['serverTime']/1000)}")
            print(f"COIN-M 服务器时间: {datetime.fromtimestamp(cm_time['serverTime']/1000)}")
            print()
            
        except Exception as e:
            print(f"获取服务器时间失败: {e}")
    
    def get_exchange_info(self):
        """获取交易所信息"""
        try:
            print("=== 交易所信息 ===")
            
            # USDT-M 期货信息
            um_info = self.um_futures_client.exchange_info()
            print(f"USDT-M 期货交易对数量: {len(um_info['symbols'])}")
            
            # COIN-M 期货信息
            cm_info = self.cm_futures_client.exchange_info()
            print(f"COIN-M 期货交易对数量: {len(cm_info['symbols'])}")
            print()
            
        except Exception as e:
            print(f"获取交易所信息失败: {e}")
    
    def get_current_price(self, symbol, client_type="USDT-M"):
        """获取单个交易对的当前价格"""
        try:
            if client_type == "USDT-M":
                price_info = self.um_futures_client.ticker_price(symbol=symbol)
            else:
                price_info = self.cm_futures_client.ticker_price(symbol=symbol)
            
            return {
                'symbol': price_info['symbol'],
                'price': float(price_info['price']),
                'timestamp': datetime.fromtimestamp(price_info['time']/1000)
            }
            
        except Exception as e:
            print(f"获取 {symbol} 价格失败: {e}")
            return None
    
    def get_multiple_prices(self):
        """获取多个交易对的价格"""
        print("=== 当前价格查询 ===")
        
        # USDT-M 期货价格
        print("USDT-M 期货价格:")
        for symbol in self.usdt_symbols:
            price_info = self.get_current_price(symbol, "USDT-M")
            if price_info:
                print(f"  {symbol}: ${price_info['price']:.4f} ({price_info['timestamp']})")
        
        print()
        
        # COIN-M 期货价格
        print("COIN-M 期货价格:")
        for symbol in self.coin_symbols:
            price_info = self.get_current_price(symbol, "COIN-M")
            if price_info:
                print(f"  {symbol}: ${price_info['price']:.4f} ({price_info['timestamp']})")
        
        print()
    
    def get_24hr_ticker(self, symbol, client_type="USDT-M"):
        """获取24小时价格统计"""
        try:
            if client_type == "USDT-M":
                ticker = self.um_futures_client.ticker_24hr_price_change(symbol=symbol)
            else:
                ticker = self.cm_futures_client.ticker_24hr_price_change(symbol=symbol)
            
            return {
                'symbol': ticker['symbol'],
                'price_change': float(ticker['priceChange']),
                'price_change_percent': float(ticker['priceChangePercent']),
                'high_price': float(ticker['highPrice']),
                'low_price': float(ticker['lowPrice']),
                'volume': float(ticker['volume']),
                'quote_volume': float(ticker['quoteVolume']),
                'open_price': float(ticker['openPrice']),
                'last_price': float(ticker['lastPrice'])
            }
            
        except Exception as e:
            print(f"获取 {symbol} 24小时统计失败: {e}")
            return None
    
    def get_24hr_statistics(self):
        """获取24小时价格统计"""
        print("=== 24小时价格统计 ===")
        
        # USDT-M 期货统计
        print("USDT-M 期货统计:")
        for symbol in self.usdt_symbols[:3]:  # 只显示前3个
            stats = self.get_24hr_ticker(symbol, "USDT-M")
            if stats:
                print(f"  {symbol}:")
                print(f"    当前价格: ${stats['last_price']:.4f}")
                print(f"    24h涨跌: ${stats['price_change']:.4f} ({stats['price_change_percent']:.2f}%)")
                print(f"    24h最高: ${stats['high_price']:.4f}")
                print(f"    24h最低: ${stats['low_price']:.4f}")
                print(f"    24h成交量: {stats['volume']:.2f}")
                print()
        
        # COIN-M 期货统计
        print("COIN-M 期货统计:")
        for symbol in self.coin_symbols[:2]:  # 只显示前2个
            stats = self.get_24hr_ticker(symbol, "COIN-M")
            if stats:
                print(f"  {symbol}:")
                print(f"    当前价格: ${stats['last_price']:.4f}")
                print(f"    24h涨跌: ${stats['price_change']:.4f} ({stats['price_change_percent']:.2f}%)")
                print(f"    24h最高: ${stats['high_price']:.4f}")
                print(f"    24h最低: ${stats['low_price']:.4f}")
                print(f"    24h成交量: {stats['volume']:.2f}")
                print()
    
    def get_orderbook(self, symbol, limit=10, client_type="USDT-M"):
        """获取订单簿深度"""
        try:
            if client_type == "USDT-M":
                orderbook = self.um_futures_client.depth(symbol=symbol, limit=limit)
            else:
                orderbook = self.cm_futures_client.depth(symbol=symbol, limit=limit)
            
            return {
                'symbol': symbol,
                'bids': [[float(price), float(qty)] for price, qty in orderbook['bids']],
                'asks': [[float(price), float(qty)] for price, qty in orderbook['asks']],
                'last_update_id': orderbook['lastUpdateId']
            }
            
        except Exception as e:
            print(f"获取 {symbol} 订单簿失败: {e}")
            return None
    
    def display_orderbook(self, symbol, limit=5):
        """显示订单簿深度"""
        print(f"=== {symbol} 订单簿深度 (前{limit}档) ===")
        
        # USDT-M 期货订单簿
        orderbook = self.get_orderbook(symbol, limit, "USDT-M")
        if orderbook:
            print("买单 (Bids):")
            for i, (price, qty) in enumerate(orderbook['bids'][:limit], 1):
                print(f"  {i}. ${price:.4f} - {qty:.4f}")
            
            print("\n卖单 (Asks):")
            for i, (price, qty) in enumerate(orderbook['asks'][:limit], 1):
                print(f"  {i}. ${price:.4f} - {qty:.4f}")
        
        print()
    
    def get_recent_trades(self, symbol, limit=5, client_type="USDT-M"):
        """获取最近成交"""
        try:
            if client_type == "USDT-M":
                trades = self.um_futures_client.recent_trades(symbol=symbol, limit=limit)
            else:
                trades = self.cm_futures_client.recent_trades(symbol=symbol, limit=limit)
            
            return [{
                'id': trade['id'],
                'price': float(trade['price']),
                'qty': float(trade['qty']),
                'time': datetime.fromtimestamp(trade['time']/1000),
                'is_buyer_maker': trade['isBuyerMaker']
            } for trade in trades]
            
        except Exception as e:
            print(f"获取 {symbol} 最近成交失败: {e}")
            return None
    
    def display_recent_trades(self, symbol, limit=5):
        """显示最近成交"""
        print(f"=== {symbol} 最近成交 (前{limit}笔) ===")
        
        trades = self.get_recent_trades(symbol, limit, "USDT-M")
        if trades:
            for i, trade in enumerate(trades, 1):
                side = "买入" if not trade['is_buyer_maker'] else "卖出"
                print(f"  {i}. {side} {trade['qty']:.4f} @ ${trade['price']:.4f} ({trade['time']})")
        
        print()
    
    def run_demo(self):
        """运行完整的 demo"""
        print("🚀 数字货币合约价格查询 Demo")
        print("=" * 50)
        
        # 1. 获取服务器时间
        self.get_server_time()
        
        # 2. 获取交易所信息
        self.get_exchange_info()
        
        # 3. 获取当前价格
        self.get_multiple_prices()
        
        # 4. 获取24小时统计
        self.get_24hr_statistics()
        
        # 5. 显示订单簿深度
        self.display_orderbook("BTCUSDT", 5)
        
        # 6. 显示最近成交
        self.display_recent_trades("BTCUSDT", 5)
        
        print("✅ Demo 完成!")


def main():
    """主函数"""
    try:
        demo = FuturesPriceDemo()
        demo.run_demo()
        
    except KeyboardInterrupt:
        print("\n👋 程序被用户中断")
    except Exception as e:
        print(f"❌ 程序运行出错: {e}")


if __name__ == "__main__":
    main() 