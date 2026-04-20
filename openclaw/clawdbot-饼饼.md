# ClawdBot-饼饼 部署文档

## 项目概述

在 Azure VM 上部署 OpenClaw gateway，并配置 Discord bot "饼饼" 实现 Claude AI 对话功能。

---

## Azure VM 配置

### 基本信息
- **VM 名称**: openclaw-vm
- **资源组**: CLAWDBOT-RG
- **区域**: East US
- **公网 IP**: 20.172.149.137
- **操作系统**: Linux (Ubuntu)

### 硬件规格 (Standard_B2s)
- **vCPU**: 2 核
- **内存**: 4 GB RAM
- **临时磁盘**: 8 GB
- **VM 类型**: B系列突发性能实例
- **月费用**: 约 $30-40 (按需计费)

### 容量评估
- **推荐运行**: 2-3 个 OpenClaw bot (稳定)
- **最大容量**: 4-5 个 bot (需监控内存)
- **单 bot 资源占用**: 
  - 空闲：300-500 MB RAM
  - 活跃：800 MB RAM

### SSH 访问
```bash
ssh azureuser@20.172.149.137

从你的本地电脑远程登录到 Azure VM, 作用：

ssh = Secure Shell，安全远程连接协议
azureuser = VM 上的用户名
20.172.149.137 = VM 的公网 IP 地址
执行后：

会提示输入密码（如果用密码认证）或使用 SSH 密钥
连接成功后，你就进入了 VM 的终端
可以在 VM 上执行命令，比如运行 free -h 查看内存、管理 OpenClaw 等
简单说就是：远程登录到你的 Azure 虚拟机，就像在本地操作一样。
```

---

## OpenClaw 安装与配置

### 安装信息
- **安装方式**: 通过 OpenClaw 官方脚本
- **用户**: azureuser
- **配置文件**: `~/.openclaw/openclaw.json` (JSON5 格式)
- **Systemd 服务**: `~/.config/systemd/user/openclaw-gateway.service`

### AI 模型配置
- **模型提供商**: GitHub Copilot
- **模型**: claude-opus-4.6
- **授权**: 通过 GitHub Copilot 账号授权

### 基本命令
```bash
# 查看配置
openclaw config list

# 修改配置
openclaw config set <key> <value>

# 重启服务
openclaw daemon restart

# 查看日志
journalctl --user -u openclaw-gateway -f
```

---

## Discord Bot "饼饼" 配置

### Discord 开发者设置

#### 必需的 Privileged Gateway Intents
在 [Discord Developer Portal](https://discord.com/developers/applications) 中配置：

1. **Message Content Intent** ✅ (必需)
   - 允许 bot 读取消息内容
2. **Server Members Intent** ✅ (推荐)
   - 允许 bot 获取服务器成员信息

#### Bot 权限
使用 OAuth2 URL Generator 生成邀请链接时需要的权限：
- **Scopes**: `bot`
- **Bot Permissions**:
  - View Channels (查看频道)
  - Send Messages (发送消息)
  - Read Message History (读取消息历史)
  - Embed Links (嵌入链接)

### OpenClaw Discord 配置

#### 方式一：交互式配置
```bash
openclaw channels login discord
# 然后按提示输入 Bot Token
```

#### 方式二：命令行直接配置
```bash
openclaw config set channels.discord.token "YOUR_DISCORD_BOT_TOKEN"
openclaw daemon restart
```

### 历史 Token 记录
- **原始 Token** (可能缺少 Message Content Intent 权限):
  ```
  YOUR_DISCORD_BOT_TOKEN_HERE
  ```
- **建议**: 创建新 bot 并启用所有必需的 Intents

---

## 部署步骤总结

### 1. Azure VM 准备
- ✅ 创建 Standard_B2s VM (CLAWDBOT-RG/openclaw-vm)
- ✅ 配置公网 IP 和 SSH 访问
- ✅ Linux (Ubuntu) 操作系统

### 2. OpenClaw 安装
- ✅ 安装 OpenClaw CLI
- ✅ 配置 GitHub Copilot 授权
- ✅ 设置 claude-opus-4.6 模型
- ✅ 启动 openclaw-gateway systemd 服务

### 3. Discord Bot 创建
1. 在 Discord Developer Portal 创建 Application
2. 创建 Bot 并保存 Token
3. 启用 Message Content Intent + Server Members Intent
4. 使用 OAuth2 生成邀请链接
5. 将 Bot 添加到目标 Discord 服务器

### 4. OpenClaw 集成 Discord
1. SSH 到 VM: `ssh azureuser@20.172.149.137`
2. 配置 Discord token
3. 重启 OpenClaw gateway
4. 在 Discord 中测试 bot 响应

---

## 故障排查

### 常见问题

#### Bot Token 权限不足
**错误**: Bot 无法读取消息内容  
**解决**: 在 Discord Developer Portal 中启用 "Message Content Intent"

#### 命令语法错误
**错误**: `openclaw channels login discord` 报错 "too many arguments"  
**解决**: 
- 使用 `openclaw channels login discord` 然后输入 token
- 或直接使用 `openclaw config set channels.discord.token <token>`

#### Gateway 未响应
**检查步骤**:
```bash
# 查看服务状态
systemctl --user status openclaw-gateway

# 查看日志
journalctl --user -u openclaw-gateway -n 50

# 重启服务
openclaw daemon restart
```

---

## 参考资源

- **OpenClaw 官网**: https://openclaw.ai
- **Discord Developer Portal**: https://discord.com/developers/applications
- **Azure Portal**: https://portal.azure.com

---

## 维护建议

### 监控
**SSH 到 VM**:
```bash
ssh azureuser@20.172.149.137
```

**实时监控内存**:
```bash
watch -n 2 free -h
```

**查看 OpenClaw 进程资源占用**:
```bash
ps aux | grep openclaw
```

**如果内存不够，可以配置 swap**:
```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

**监控建议**:
- 定期检查 VM 内存使用
- 监控 CPU credits (B 系列限制)
- 查看 OpenClaw 日志检查错误:
  ```bash
  journalctl --user -u openclaw-gateway -f
  ```

### 安全
- Bot Token 只显示一次，需妥善保存
- 不要将 Token 提交到公开代码库
- 定期更新 VM 安全补丁

### 扩展
- 如需运行更多 bot，考虑升级到 Standard_B2ms (8 GB RAM)
- 监控网络带宽使用情况

---

**文档创建日期**: 2026-04-02  
**最后更新**: 2026-04-02  
**维护人员**: xiaoxiao
