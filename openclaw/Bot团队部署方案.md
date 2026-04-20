# Bot 团队部署方案

## 背景

在现有 Azure VM (Standard_B2s, 20.172.149.137) 上扩展 OpenClaw，从单个饼饼 bot 扩展为 4 bot 协作团队。

---

## Bot 团队

| Bot | Agent ID | 角色 | 职责 |
|-----|----------|------|------|
| 饼饼 | bingbing | 大总管 | 统筹协调、任务分配、进度跟踪 |
| 小圆 | xiaoyuan | 程序员 | 写代码、部署、技术实现 |
| 鸽鸽 | gege | 产品经理 + UX + Marketing | 需求定义、UX 设计、上线后营销 |
| 薯条 | shutiao | 生活管家 | 育儿（喂养/看管）、健康、生活规划、家人共用 |

---

## 第 1 步：VM 内存准备

4 个 bot 活跃时约 3.2GB，当前 4GB 内存会比较紧张。

### 方案 A：先配 swap 撑着（省钱）

```bash
ssh azureuser@20.172.149.137

sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 方案 B：升级到 Standard_B2ms 8GB（推荐）

1. 登录 Azure Portal (https://portal.azure.com)
2. 进入 openclaw-vm → **Size**
3. 选择 **Standard_B2ms**（8GB RAM）
4. 确认升级（需短暂停机，约 2-5 分钟）
5. 月费从 ~$35 涨到 ~$65，$150 额度内完全够用

---

## 第 2 步：创建 3 个新 Discord Bot

在 [Discord Developer Portal](https://discord.com/developers/applications) 对以下每个 bot 重复操作：

### 2.1 创建 Application
1. 点击 **New Application**
2. 输入名称（小圆 / 鸽鸽 / 薯条）
3. 进入 **Bot** 标签页 → **Add Bot**

### 2.2 启用 Intents
- ✅ **Message Content Intent**（必需）
- ✅ **Server Members Intent**（推荐）

### 2.3 复制 Token
- 点击 **Reset Token** → 立即复制保存（只显示一次）

### 2.4 生成邀请链接
1. 进入 **OAuth2 → URL Generator**
2. Scopes: `bot`
3. Bot Permissions:
   - View Channels
   - Send Messages
   - Read Message History
   - Embed Links
4. 复制 URL → 在浏览器打开 → 选择目标服务器 → 授权

### Token 记录（部署后删除此段）

| Bot | Token |
|-----|-------|
| 小圆 | （部署时填入） |
| 鸽鸽 | （部署时填入） |
| 薯条 | （部署时填入） |

> ⚠️ **安全提醒**: Token 不要提交到 git 仓库，部署完成后从此文档删除

---

## 第 3 步：配置 OpenClaw 多 Agent

### 3.1 SSH 连接 VM

```bash
ssh azureuser@20.172.149.137
```

### 3.2 创建 Workspace 目录

```bash
mkdir -p ~/.openclaw/workspace-bingbing
mkdir -p ~/.openclaw/workspace-xiaoyuan
mkdir -p ~/.openclaw/workspace-gege
mkdir -p ~/.openclaw/workspace-shutiao
```

### 3.3 编辑 OpenClaw 配置

```bash
nano ~/.openclaw/openclaw.json
```

修改为以下内容：

```json5
{
  "ai": {
    "provider": "github-copilot",
    "model": "claude-opus-4.6"
  },

  // 4 个 Agent 定义
  "agents": {
    "list": [
      { "id": "bingbing", "workspace": "~/.openclaw/workspace-bingbing" },
      { "id": "xiaoyuan", "workspace": "~/.openclaw/workspace-xiaoyuan" },
      { "id": "gege", "workspace": "~/.openclaw/workspace-gege" },
      { "id": "shutiao", "workspace": "~/.openclaw/workspace-shutiao" }
    ]
  },

  // 4 个 Discord Bot
  "channels": {
    "discord": [
      { "token": "饼饼_TOKEN", "name": "饼饼" },
      { "token": "小圆_TOKEN", "name": "小圆" },
      { "token": "鸽鸽_TOKEN", "name": "鸽鸽" },
      { "token": "薯条_TOKEN", "name": "薯条" }
    ]
  },

  // 路由绑定：每个 Discord Bot → 对应 Agent
  "bindings": [
    { "agentId": "bingbing", "match": { "channel": "discord", "botName": "饼饼" } },
    { "agentId": "xiaoyuan", "match": { "channel": "discord", "botName": "小圆" } },
    { "agentId": "gege", "match": { "channel": "discord", "botName": "鸽鸽" } },
    { "agentId": "shutiao", "match": { "channel": "discord", "botName": "薯条" } }
  ],

  // 启用 Bot 间协作
  "tools": {
    "agentToAgent": {
      "enabled": true,
      "allow": ["bingbing", "xiaoyuan", "gege", "shutiao"]
    }
  }
}
```

---

## 第 4 步：配置 Agent System Prompt

在每个 workspace 下创建角色定义文件。

### 饼饼（大总管）
```bash
cat > ~/.openclaw/workspace-bingbing/system.md << 'EOF'
你是饼饼，团队大总管。

职责：
- 理解用户需求，拆解为具体任务
- 将开发任务 dispatch 给小圆（程序员）
- 将产品/设计/营销任务 dispatch 给鸽鸽（产品经理）
- 跟踪各任务进度，汇总结果给用户
- 在团队成员之间协调沟通

工作原则：
- 收到需求后先拆解再分配，不要自己做具体执行
- 定期向用户汇报进度
- 如有冲突或不确定，请求用户决策
EOF
```

### 小圆（程序员）
```bash
cat > ~/.openclaw/workspace-xiaoyuan/system.md << 'EOF'
你是小圆，团队程序员。

职责：
- 编写代码、调试 bug、技术方案设计
- 应用部署和运维
- 代码审查和技术文档
- 接受饼饼（大总管）的任务派遣

工作原则：
- 写简洁、安全、可维护的代码
- 完成任务后向饼饼汇报结果
- 技术方案有多种选择时，列出优劣让饼饼/用户决策
EOF
```

### 鸽鸽（产品经理 + UX + Marketing）
```bash
cat > ~/.openclaw/workspace-gege/system.md << 'EOF'
你是鸽鸽，团队的产品经理、UX 设计师和营销负责人。

职责：
- 需求分析和产品规划（PRD、用户故事）
- 用户体验设计（信息架构、交互流程、UX 文案）
- App 上线后的营销策略和内容创作
- 接受饼饼（大总管）的任务派遣

工作原则：
- 以用户需求为中心思考问题
- 产出清晰的需求文档供小圆开发
- 营销内容要接地气、有吸引力
- 完成任务后向饼饼汇报结果
EOF
```

### 薯条（生活管家）
```bash
cat > ~/.openclaw/workspace-shutiao/system.md << 'EOF'
你是薯条，家庭生活管家。

职责：
- 育儿管理：喂养记录、作息追踪、成长里程碑、看护提醒
- 健康管理：运动、饮食、睡眠追踪和建议
- 生活规划：日程安排、购物清单、家务分配
- 日常聊天陪伴

工作原则：
- 温暖友善，像一个贴心的家人
- 记住每位家庭成员的偏好和习惯
- 育儿建议基于科学依据
- 涉及健康问题时提醒咨询专业医生
- 不同家庭成员私聊时保持各自记忆独立
EOF
```

---

## 第 5 步：重启并验证

```bash
# 重启 gateway
openclaw daemon restart

# 查看实时日志，确认 4 个 bot 都连接成功
journalctl --user -u openclaw-gateway -f
```

### 验证清单

- [ ] 日志中 4 个 bot 都显示 "Connected to Discord"
- [ ] 在 Discord 分别 @ 饼饼/小圆/鸽鸽/薯条，确认都能回复
- [ ] 测试饼饼 dispatch 任务给小圆
- [ ] 测试饼饼 dispatch 任务给鸽鸽
- [ ] 测试薯条 DM 私聊正常
- [ ] 监控内存使用：`watch -n 2 free -h`

---

## 第 6 步：Discord 频道规划

在 Discord 服务器创建以下频道结构：

```
📁 app-project（工作区）
  #general        — 饼饼统筹、需求讨论
  #dev            — 小圆的开发讨论
  #product        — 鸽鸽的产品/设计讨论
  #deploys        — 部署通知

📁 life（生活区）
  #baby-log       — 育儿记录（全家共享）
  #health         — 健康管理
  #daily          — 日常生活

💬 私聊
  各家庭成员通过 DM 私聊薯条 → 记忆独立不混乱
```

---

## 日常维护

### 监控命令
```bash
ssh azureuser@20.172.149.137

# 实时内存
watch -n 2 free -h

# OpenClaw 进程
ps aux | grep openclaw

# 实时日志
journalctl --user -u openclaw-gateway -f
```

### 常见问题

| 问题 | 解决 |
|------|------|
| Bot 无法读取消息 | Discord Developer Portal 检查 Message Content Intent |
| 内存不足 | 配置 swap 或升级 VM |
| Agent 间通信失败 | 检查 agentToAgent.allow 列表是否包含所有 agent ID |
| 某个 bot 不回复 | 检查 bindings 配置和 token 是否正确 |

---

**文档创建日期**: 2026-04-08
**维护人员**: xiaoxiao
