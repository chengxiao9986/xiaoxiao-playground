# 多个 Discord Bot 配置指南

## 概述

在同一个 Azure VM 上通过 OpenClaw 运行多个 Discord bot。一个 OpenClaw gateway 可以同时管理多个 Discord bot 实例。

---

## 前置条件

- 已部署 OpenClaw gateway（参考 [clawdbot-饼饼.md](clawdbot-饼饼.md)）
- Azure VM: openclaw-vm (20.172.149.137)
- SSH 访问权限

---

## 步骤 1: 创建新的 Discord Bot

### 在 Discord Developer Portal 操作

1. 访问 [Discord Developer Portal](https://discord.com/developers/applications)
2. 点击 **New Application**
3. 输入 bot 名称（例如：bot2、bot3）
4. 进入 **Bot** 标签页
5. 点击 **Add Bot**

### 配置 Bot 权限

#### 启用 Privileged Gateway Intents
- ✅ **Message Content Intent** （必需）
- ✅ **Server Members Intent** （推荐）

#### 复制 Bot Token
- 点击 **Reset Token** 生成新 token
- **立即复制并保存**（只显示一次）

#### 生成邀请链接
1. 进入 **OAuth2 → URL Generator**
2. 选择 Scopes: `bot`
3. 选择 Bot Permissions:
   - View Channels
   - Send Messages
   - Read Message History
   - Embed Links
4. 复制生成的 URL 并在浏览器中打开
5. 选择目标服务器并授权

**对每个新 bot 重复以上步骤。**

---

## 步骤 2: 配置 OpenClaw 支持多个 Bot

### SSH 连接到 VM

```bash
ssh azureuser@20.172.149.137
```

### 编辑 OpenClaw 配置文件

```bash
nano ~/.openclaw/openclaw.json
```

### 修改配置为多 Bot 格式

将 `channels.discord` 从单个对象改为数组：

```json5
{
  "ai": {
    "provider": "github-copilot",
    "model": "claude-opus-4.6"
  },
  "channels": {
    "discord": [
      {
        "token": "YOUR_FIRST_BOT_TOKEN_HERE",
        "name": "饼饼"
      },
      {
        "token": "YOUR_SECOND_BOT_TOKEN_HERE",
        "name": "bot2"
      },
      {
        "token": "YOUR_THIRD_BOT_TOKEN_HERE",
        "name": "bot3"
      }
    ]
  }
}
```

**注意事项**:
- 每个 bot 需要不同的 `token`
- `name` 字段用于日志识别，可自定义
- 不要将 token 提交到公开代码库

### 保存并退出

- 按 `Ctrl + O` 保存
- 按 `Enter` 确认
- 按 `Ctrl + X` 退出

---

## 步骤 3: 重启 OpenClaw Gateway

```bash
openclaw daemon restart
```

---

## 步骤 4: 验证 Bot 连接

### 查看实时日志

```bash
journalctl --user -u openclaw-gateway -f
```

**成功标志**:
- 每个 bot 都显示 "Connected to Discord"
- 没有 authentication 错误

### 测试 Bot 响应

在 Discord 服务器中分别 @ 每个 bot 发送消息，确认都能正常响应。

---

## 资源容量规划

### VM 硬件规格 (Standard_B2s)
- **vCPU**: 2 核
- **RAM**: 4 GB

### Bot 资源占用
| 状态 | 单个 Bot 内存占用 |
|------|------------------|
| 空闲 | 300-500 MB       |
| 活跃 | 800 MB           |

### 推荐配置
- **稳定运行**: 2-3 个 Discord bot
- **最大容量**: 4-5 个 bot（需监控内存）

### 示例计算
| Bot 数量 | 活跃时总内存 | 系统剩余内存 |
|----------|--------------|--------------|
| 2 个     | 1.6 GB       | 2.4 GB       |
| 3 个     | 2.4 GB       | 1.6 GB       |
| 4 个     | 3.2 GB       | 0.8 GB ⚠️    |

---

## 监控与维护

### SSH 到 VM

```bash
ssh azureuser@20.172.149.137
```

### 实时内存监控

```bash
watch -n 2 free -h
```

### 查看 OpenClaw 进程资源

```bash
ps aux | grep openclaw
```

### 查看 Bot 连接状态

```bash
journalctl --user -u openclaw-gateway -n 50
```

### 配置 Swap（如内存不足）

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**永久启用 swap**:
```bash
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

---

## 故障排查

### Bot 无法连接

**检查 token 是否正确**:
```bash
cat ~/.openclaw/openclaw.json | grep token
```

**检查 Discord Developer Portal**:
- 确认 Message Content Intent 已启用
- Token 未过期或被重置

### 内存不足

**现象**: Bot 响应缓慢或崩溃

**解决**:
1. 配置 swap（见上文）
2. 减少运行的 bot 数量
3. 升级 VM 到 Standard_B2ms (8 GB RAM)

### 日志错误排查

```bash
# 查看最近 100 行日志
journalctl --user -u openclaw-gateway -n 100

# 搜索特定错误
journalctl --user -u openclaw-gateway | grep -i error
```

---

## 配置示例

### 单个 Bot（原始配置）

```json5
{
  "channels": {
    "discord": {
      "token": "BOT_TOKEN"
    }
  }
}
```

### 多个 Bot（推荐配置）

```json5
{
  "channels": {
    "discord": [
      {
        "token": "FIRST_BOT_TOKEN",
        "name": "饼饼"
      },
      {
        "token": "SECOND_BOT_TOKEN",
        "name": "小助手"
      }
    ]
  }
}
```

---

## 升级路径

### 如需运行更多 Bot

#### 方案一: 升级 VM 规格
- 从 Standard_B2s (4 GB) 升级到 Standard_B2ms (8 GB)
- 可稳定运行 6-8 个 bot

#### 方案二: 分布式部署
- 在不同 VM 上部署多个 OpenClaw gateway
- 每个 gateway 管理 2-3 个 bot
- 共享相同的 AI 模型配置

---

## 安全建议

1. **Token 保护**
   - 不要将 token 提交到 git 仓库
   - 定期轮换 bot token
   - 使用环境变量或密钥管理服务

2. **访问控制**
   - 限制 SSH 访问 IP 白名单
   - 使用 SSH 密钥而非密码
   - 定期更新 VM 安全补丁

3. **日志审计**
   - 定期检查 bot 活动日志
   - 监控异常流量和请求

---

## 参考资源

- [clawdbot-饼饼.md](clawdbot-饼饼.md) - 单 bot 部署文档
- [Discord Developer Portal](https://discord.com/developers/applications)
- [OpenClaw 官网](https://openclaw.ai)

---

**文档创建日期**: 2026-04-02  
**最后更新**: 2026-04-02  
**维护人员**: xiaoxiao
