# 市场监控系统使用说明

## 功能概述

本系统实现了以下功能：

1. **自定义交易对监控** - 支持用户自定义交易对列表，或使用常用交易对列表
2. **获取K线数据** - 为每个交易对获取56条1小时K线数据并保存到本地
3. **WebSocket实时监控** - 通过WebSocket接收最新K线数据，避免频繁轮询API，支持自动重连机制
4. **海龟交易信号检测** - 实时分析K线数据，检测海龟交易法的入场信号
5. **钉钉机器人通知** - 当检测到交易信号时，自动发送钉钉机器人消息

## 安装依赖

```bash
pip install -r requirements.txt
```

## 配置钉钉机器人

1. 复制配置文件模板：
```bash
cp config.env.example .env
```

2. 编辑 `.env` 文件，填入您的配置：
```env
# 钉钉机器人配置
DINGTALK_ACCESS_TOKEN=your_dingtalk_access_token_here
DINGTALK_SECRET=your_dingtalk_secret_here
DINGTALK_AT_MOBILES=13800138000,13800138001

# 市场监控配置
KLINE_INTERVAL=1h          # K线间隔: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
KLINE_LIMIT=56            # K线数量限制，默认56条
SYMBOL_LIMIT=50           # 监控的交易对数量，默认50个

# 自定义交易对配置（可选）
# 如果设置了CUSTOM_SYMBOLS，将使用自定义交易对列表
# 如果没有设置，将使用常用交易对列表
# 支持JSON数组格式，例如: ["BTCUSDT","ETHUSDT","BNBUSDT"]
# 也支持逗号分隔格式（向后兼容），例如: BTCUSDT,ETHUSDT,BNBUSDT
CUSTOM_SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","ADAUSDT","SOLUSDT"]
```

### 如何获取钉钉机器人配置

1. 在钉钉群中添加自定义机器人
2. 获取机器人的Webhook地址中的access_token
3. 如果启用了签名，获取签名密钥

## 运行系统

### 方法1：直接运行启动脚本
```bash
python run_market_monitor.py
```

### 方法2：运行模块
```bash
python -m src.trading.market_monitor
```

## 系统工作流程

1. **初始化阶段**：
   - 获取用户自定义的交易对列表（或使用常用交易对列表）
   - 验证交易对的有效性
   - 为每个交易对获取56条1小时K线数据
   - 将数据保存到 `data/klines/` 目录

2. **监控阶段**：
   - 启动WebSocket连接
   - 订阅所有交易对的K线数据流
   - 实时接收和更新K线数据
   - 自动检测连接状态，支持断线重连

3. **信号检测**：
   - 对每个交易对的K线数据进行海龟交易法分析
   - 检测突破信号（买入/卖出）
   - 计算ATR、唐奇安通道等技术指标

4. **通知发送**：
   - 当检测到交易信号时，自动发送钉钉机器人消息
   - 消息包含交易对、信号类型、价格、技术指标等信息

## 数据存储

- **交易对列表**：`data/top_symbols.json`
- **K线数据**：`data/klines/{symbol}_klines.csv`
- **日志文件**：`market_monitor.log`

## 自定义交易对配置

### 方法1：使用环境变量配置
在 `.env` 文件中设置 `CUSTOM_SYMBOLS` 环境变量：

```env
# 自定义交易对列表（支持JSON数组格式）
CUSTOM_SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT","ADAUSDT","SOLUSDT","XRPUSDT","DOTUSDT"]

# 也支持逗号分隔格式（向后兼容）
CUSTOM_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT,ADAUSDT,SOLUSDT,XRPUSDT,DOTUSDT
```

### 方法2：使用常用交易对列表
如果不设置 `CUSTOM_SYMBOLS`，系统将自动使用预定义的常用交易对列表，包含市值排名前20的交易对。

### 交易对格式要求
- 必须使用USDT交易对格式（例如：BTCUSDT）
- 支持JSON数组格式：`["BTCUSDT","ETHUSDT","BNBUSDT"]`
- 支持逗号分隔格式（向后兼容）：`BTCUSDT,ETHUSDT,BNBUSDT`
- 系统会自动验证交易对的有效性
- 无效的交易对会被自动跳过

### 示例配置
```env
# 只监控主流币种（JSON数组格式）
CUSTOM_SYMBOLS=["BTCUSDT","ETHUSDT","BNBUSDT"]

# 监控DeFi代币（JSON数组格式）
CUSTOM_SYMBOLS=["UNIUSDT","AAVEUSDT","COMPUSDT","CRVUSDT","SUSHIUSDT"]

# 监控游戏代币（JSON数组格式）
CUSTOM_SYMBOLS=["AXSUSDT","SANDUSDT","MANAUSDT","ENJUSDT","CHZUSDT"]

# 也支持逗号分隔格式（向后兼容）
CUSTOM_SYMBOLS=BTCUSDT,ETHUSDT,BNBUSDT
```

## 配置参数说明

### 市场监控配置
- **KLINE_INTERVAL**：K线间隔，支持 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
- **KLINE_LIMIT**：K线数量限制，默认56条
- **SYMBOL_LIMIT**：监控的交易对数量，默认50个
- **CUSTOM_SYMBOLS**：自定义交易对列表（可选），支持JSON数组格式，例如：["BTCUSDT","ETHUSDT","BNBUSDT"]，也支持逗号分隔格式（向后兼容）

### WebSocket重连配置
- **WEBSOCKET_MAX_RETRIES**：WebSocket最大重试次数，默认5次
- **WEBSOCKET_RETRY_DELAY**：WebSocket初始重试延迟（秒），默认10秒
- **WEBSOCKET_MAX_RETRY_DELAY**：WebSocket最大重试延迟（秒），默认300秒（5分钟）
- **WEBSOCKET_CONNECTION_CHECK_INTERVAL**：WebSocket连接检查间隔（秒），默认30秒

### 海龟交易法参数
- **入场周期**：20个周期
- **出场周期**：10个周期
- **ATR周期**：20个周期
- **仓位大小**：2%

## 注意事项

1. **网络连接**：确保能够访问Binance API和钉钉API
2. **API限制**：系统已内置请求间隔，避免触发API限制
3. **数据准确性**：K线数据来自Binance官方API，具有高可靠性
4. **信号频率**：海龟交易信号相对较少，请耐心等待
5. **风险提示**：本系统仅提供信号检测，不构成投资建议

## 故障排除

### 常见问题

1. **无法连接Binance API**
   - 检查网络连接
   - 确认防火墙设置

2. **钉钉消息发送失败**
   - 检查access_token是否正确
   - 确认机器人是否被移除或禁用

3. **WebSocket连接断开**
   - 系统会自动重连，支持指数退避策略
   - 检查网络稳定性
   - 可通过配置调整重连参数

### 日志查看

```bash
tail -f market_monitor.log
```

## 停止系统

使用 `Ctrl+C` 停止程序，系统会优雅地关闭WebSocket连接并保存数据。 