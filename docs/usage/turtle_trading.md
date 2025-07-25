# 🐢 海龟交易法 BTC 交易信号检测系统

基于经典海龟交易法的BTC交易信号检测和邮件通知系统。

## 🚀 快速开始

### 1. 安装依赖

```bash
# 方法1: 使用安装脚本
python install_turtle_system.py

# 方法2: 手动安装
pip install -r requirements.txt
```

### 2. 配置邮件设置

1. 复制配置模板：
```bash
copy email_config_example.txt .env
```

2. 编辑 `.env` 文件，填入您的邮箱信息：
```env
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
RECIPIENT_EMAIL=recipient@example.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 3. 测试系统

```bash
python test_turtle_system.py
```

### 4. 启动监控

```bash
# Windows
run_turtle_monitor.bat

# Linux/Mac
./run_turtle_monitor.sh

# 直接运行
python turtle_trading_system.py
```

## 📊 系统功能

### 核心功能

- **📈 K线数据获取**: 自动获取BTC的56条1小时K线数据
- **🐢 海龟交易法**: 基于20周期突破和ATR指标的交易信号检测
- **📧 邮件通知**: 检测到交易信号时自动发送邮件通知
- **⏰ 实时监控**: 每5分钟检查一次交易信号
- **🛡️ 信号冷却**: 避免重复信号，1小时内只发送一次相同信号

### 海龟交易法参数

- **入场周期**: 20周期（价格突破20周期最高价时买入）
- **出场周期**: 10周期（价格突破10周期最低价时卖出）
- **ATR周期**: 20周期（用于计算平均真实波幅）
- **仓位大小**: 账户的2%（基于ATR计算具体仓位）
- **信号冷却**: 1小时（避免重复信号）

## 📧 邮件配置详解

### Gmail 配置

1. **开启两步验证**：
   - 登录Gmail账户
   - 进入"安全性"设置
   - 开启"两步验证"

2. **生成应用专用密码**：
   - 在"安全性"设置中找到"应用专用密码"
   - 选择"邮件"应用
   - 生成16位密码

3. **配置.env文件**：
```env
EMAIL_ADDRESS=your_gmail@gmail.com
EMAIL_PASSWORD=your_16_digit_app_password
RECIPIENT_EMAIL=your_notification_email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
```

### 其他邮箱配置

#### QQ邮箱
```env
EMAIL_ADDRESS=your_qq@qq.com
EMAIL_PASSWORD=your_authorization_code
RECIPIENT_EMAIL=recipient@example.com
SMTP_SERVER=smtp.qq.com
SMTP_PORT=587
```

#### 163邮箱
```env
EMAIL_ADDRESS=your_email@163.com
EMAIL_PASSWORD=your_authorization_code
RECIPIENT_EMAIL=recipient@example.com
SMTP_SERVER=smtp.163.com
SMTP_PORT=587
```

## 🔧 系统参数调整

### 修改交易参数

在 `turtle_trading_system.py` 中可以调整以下参数：

```python
class TurtleTradingSystem:
    def __init__(self):
        # 海龟交易法参数
        self.entry_period = 20    # 入场突破周期
        self.exit_period = 10     # 出场突破周期
        self.atr_period = 20      # ATR周期
        self.position_size = 0.02 # 仓位大小（2%）
        
        # 信号冷却时间（秒）
        self.signal_cooldown = 3600  # 1小时
```

### 修改监控参数

```python
# 在 main() 函数中调整
turtle_system.run_turtle_trading_monitor(
    symbol="BTCUSDT",      # 交易对
    interval="1h",         # K线间隔
    check_interval=300     # 检查间隔（秒）
)
```

## 📊 信号说明

### 买入信号 (BUY)
- **触发条件**: 当前价格 > 20周期最高价
- **信号含义**: 价格突破上轨，可能开始上涨趋势
- **建议操作**: 考虑买入，仓位基于ATR计算

### 卖出信号 (SELL)
- **触发条件**: 当前价格 < 20周期最低价
- **信号含义**: 价格突破下轨，可能开始下跌趋势
- **建议操作**: 考虑卖出或减仓

### 邮件通知内容

邮件包含以下信息：
- 信号类型（买入/卖出）
- 当前价格
- 上轨和下轨价格
- ATR值
- 建议仓位（买入信号）
- 信号时间

## ⚠️ 风险提示

1. **投资风险**: 数字货币交易存在高风险，可能导致资金损失
2. **信号延迟**: 交易信号仅供参考，实际交易需要结合其他分析
3. **市场波动**: 市场剧烈波动时可能出现假突破信号
4. **技术风险**: 网络中断、API限制等可能影响系统运行
5. **历史表现**: 历史表现不代表未来收益

## 🔍 故障排除

### 常见问题

1. **K线数据获取失败**
   - 检查网络连接
   - 确认Binance API可访问
   - 检查交易对名称是否正确

2. **邮件发送失败**
   - 检查邮箱配置是否正确
   - 确认应用专用密码有效
   - 检查SMTP服务器设置

3. **依赖包安装失败**
   - 更新pip: `pip install --upgrade pip`
   - 使用国内镜像: `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple/`

4. **权限错误**
   - Windows: 以管理员身份运行
   - Linux/Mac: 使用 `sudo` 或调整文件权限

### 日志查看

系统运行时会显示详细日志：
- ✅ 成功操作
- ❌ 错误信息
- ⏰ 时间戳和价格信息
- 🔔 信号检测结果

## 📈 性能优化

### 系统优化建议

1. **调整检查频率**: 根据市场活跃度调整 `check_interval`
2. **优化邮件发送**: 使用更快的SMTP服务器
3. **数据缓存**: 避免重复获取相同时间段的K线数据
4. **错误重试**: 网络错误时自动重试

### 监控建议

1. **定期检查**: 确保系统正常运行
2. **日志监控**: 关注错误日志和信号频率
3. **参数调优**: 根据市场情况调整交易参数
4. **备份配置**: 定期备份重要的配置文件

## 📞 技术支持

如果遇到问题，请检查：

1. **系统要求**: Python 3.7+
2. **依赖版本**: 查看 `requirements.txt`
3. **配置正确性**: 确认 `.env` 文件配置
4. **网络连接**: 确保能访问Binance API

## 📄 许可证

MIT License - 详见 LICENSE 文件

## 🔗 相关链接

- [Binance API 文档](https://binance-docs.github.io/apidocs/futures/en/)
- [海龟交易法介绍](https://en.wikipedia.org/wiki/Turtle_trading)
- [Python pandas 文档](https://pandas.pydata.org/)
- [Python 邮件发送教程](https://docs.python.org/3/library/email.html) 