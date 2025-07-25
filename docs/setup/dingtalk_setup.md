# 🤖 钉钉机器人配置说明

## 📋 配置步骤

### 1. 创建钉钉机器人

1. **进入钉钉群设置**
   - 打开钉钉群聊
   - 点击群设置（右上角齿轮图标）

2. **添加机器人**
   - 选择"智能群助手"
   - 点击"添加机器人"
   - 选择"自定义"机器人

3. **配置机器人**
   - 输入机器人名称（如：海龟交易监控）
   - 选择安全设置（建议选择"加签"）
   - 点击"完成"

4. **获取配置信息**
   - 复制Webhook地址中的access_token
   - 如果选择了"加签"，复制签名密钥

### 2. 配置环境变量

在 `.env` 文件中添加以下配置：

```env
# 钉钉机器人配置
DINGTALK_ACCESS_TOKEN=your_access_token_here
DINGTALK_SECRET=your_secret_here
DINGTALK_AT_MOBILES=手机号1,手机号2
```

### 3. 测试机器人

运行测试脚本：

```bash
python dingtalk_bot_test.py
```

## 🔧 配置详解

### DINGTALK_ACCESS_TOKEN
- **说明**: 机器人的访问令牌
- **获取方式**: 从Webhook URL中提取
- **示例**: `https://oapi.dingtalk.com/robot/send?access_token=xxxxxxxx`

### DINGTALK_SECRET
- **说明**: 安全设置的签名密钥
- **获取方式**: 创建机器人时选择"加签"后获得
- **可选**: 不配置也可以使用，但安全性较低

### DINGTALK_AT_MOBILES
- **说明**: 要@的手机号列表
- **格式**: 多个手机号用逗号分隔
- **示例**: `13800138000,13900139000`

## 📱 消息类型

### 1. 文本消息
```python
bot.send_text_message("这是一条文本消息")
```

### 2. Markdown消息
```python
bot.send_markdown_message(
    title="消息标题",
    text="# 标题\n## 子标题\n- 列表项"
)
```

### 3. 链接消息
```python
bot.send_link_message(
    title="链接标题",
    text="链接描述",
    message_url="https://example.com",
    pic_url="https://example.com/image.png"
)
```

### 4. @消息
```python
# @指定用户
bot.send_text_message("消息内容", at_mobiles=["13800138000"])

# @所有人
bot.send_text_message("消息内容", at_all=True)
```

## 🛡️ 安全设置

### 推荐配置
1. **使用加签**: 在创建机器人时选择"加签"安全设置
2. **配置密钥**: 将签名密钥填入 `DINGTALK_SECRET`
3. **限制IP**: 在机器人设置中配置IP白名单（可选）

### 安全级别
- **高**: 使用加签 + IP白名单
- **中**: 仅使用加签
- **低**: 不使用安全设置

## ⚠️ 注意事项

1. **消息频率限制**: 钉钉机器人有消息频率限制，建议不要过于频繁发送
2. **消息长度**: 单条消息不要过长，建议分段发送
3. **特殊字符**: 注意消息中的特殊字符可能导致发送失败
4. **网络问题**: 确保网络连接稳定，能够访问钉钉API

## 🔍 故障排除

### 常见错误

1. **access_token错误**
   - 检查access_token是否正确
   - 确认机器人是否被删除或禁用

2. **签名错误**
   - 检查DINGTALK_SECRET是否正确
   - 确认时间戳是否同步

3. **消息发送失败**
   - 检查消息格式是否正确
   - 确认是否超过频率限制

### 调试方法

1. **查看错误信息**: 运行测试脚本查看详细错误信息
2. **检查配置**: 确认.env文件中的配置是否正确
3. **网络测试**: 确认能够访问钉钉API

## 📞 技术支持

如果遇到问题，请检查：

1. **机器人状态**: 确认机器人是否正常工作
2. **配置正确性**: 检查.env文件配置
3. **网络连接**: 确保能访问钉钉API
4. **权限设置**: 确认机器人有发送消息权限 