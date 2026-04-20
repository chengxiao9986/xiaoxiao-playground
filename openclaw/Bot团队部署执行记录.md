# Bot 团队部署执行记录

## 概要

在 Azure VM 上完成了 4 bot 团队的完整部署，从只有饼饼一个 bot 扩展为饼饼/小圆/鸽鸽/薯条四个 bot 协作团队。

**执行时间**: 2026-04-08 ~ 2026-04-09
**执行环境**: Azure VM (20.172.149.137), Standard_B2s, Ubuntu

---

## 已完成的工作

### 1. 创建 3 个新 Discord Bot

在 Discord Developer Portal 创建了小圆、鸽鸽、薯条三个 bot：

- 每个 bot 启用了 **Message Content Intent** 和 **Server Members Intent**
- 通过 OAuth2 生成邀请链接，添加到 Discord 服务器
- 权限：View Channels, Send Messages, Read Message History, Embed Links

### 2. 配置 OpenClaw 多 Agent

SSH 到 VM，编辑 `~/.openclaw/openclaw.json`，配置为多 agent 格式：

- 定义 4 个 agent：bingbing, xiaoyuan, gege, shutiao
- 配置 4 个 Discord bot token，分别绑定到对应 agent
- 通过 `bindings` 实现路由：每个 Discord bot → 对应 agent
- 启用 `agentToAgent` 通信，allowlist 包含全部 4 个 agent

### 3. 创建 Agent Workspace 目录

```
~/.openclaw/workspace-bingbing/
~/.openclaw/workspace-xiaoyuan/
~/.openclaw/workspace-gege/
~/.openclaw/workspace-shutiao/
```

### 4. 配置角色定义文件（SOUL.md + AGENTS.md）

每个 workspace 下创建两个文件：

- **SOUL.md** — 人格定义（语气、风格、个性）
- **AGENTS.md** — 操作规则（职责、工作规则、团队关系）

| Bot | SOUL.md 要点 | AGENTS.md 要点 |
|-----|-------------|---------------|
| 饼饼 | 干脆利落，像靠谱的项目经理 | 拆解任务、dispatch 给小圆/鸽鸽、跟踪进度 |
| 小圆 | 技术扎实，表达简洁，代码说话 | 写代码、调试、部署，接受饼饼派遣 |
| 鸽鸽 | 以用户为中心，有条理 | 需求分析、UX 设计、营销内容，接受饼饼派遣 |
| 薯条 | 温暖友善，像贴心的家人 | 育儿、健康、生活规划，DM 记忆隔离 |

### 5. 配置 VM 内存

配置了 2GB swap 以应对 4 bot 同时运行时的内存压力：

```bash
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
# 已写入 /etc/fstab 永久生效
```

### 6. 配置 DM 访问策略（allowlist）

默认 DM 策略是 `pairing`，新用户私聊 bot 需要管理员手动批准 pairing code。改为 `allowlist` 模式，指定允许的 Discord 用户 ID，免审批直接使用。
后续他人要用的话，把他们的 Discord 用户 ID 加进 allowFrom 数组就行。

给 4 个 bot 都配置了：
```json5
"dmPolicy": "allowlist",
"allowFrom": ["discord:884324697427288064"]
```

| DM 策略 | 说明 |
|---------|------|
| `pairing`（默认） | 新用户需 pairing code + 管理员在 VM 上手动批准 |
| **`allowlist`（当前）** | 只允许 allowFrom 列表里的用户，免审批 |
| `open` | 任何人都能 DM，有被滥用风险 |
| `disabled` | 关闭所有 DM |

> 后续新增家庭成员使用时，把他们的 Discord 用户 ID 加入 `allowFrom` 数组即可。

### 7. 验证

- 4 个 bot 全部在 Discord 上线，日志显示 "Connected to Discord"
- 每个 bot 被 @ 后正确回复自己的角色身份
- 饼饼能列出团队成员表，小圆说"代码说话"，鸽鸽介绍产品全流程，薯条回复育儿/健康/生活

---

## 遇到的问题和解决方案

### 问题 1：Bot 不认识自己的角色

**现象**: 4 个 bot 都在线，但回复内容像通用 AI 助手，不知道自己是谁。

**原因**: 最初使用了 `system.md` 作为角色定义文件名，但 OpenClaw 不认这个文件。

**解决**: 查阅 OpenClaw 官方文档，确认正确的文件名是 **SOUL.md**（人格）和 **AGENTS.md**（操作规则）。删除 system.md，创建正确文件后重启，问题解决。

**教训**: OpenClaw workspace 下的特殊文件有固定命名，必须按官方文档来：
- `SOUL.md` — 人格、语气、风格
- `AGENTS.md` — 操作规则、职责
- `USER.md` — 用户上下文（可选）
- `IDENTITY.md`, `TOOLS.md`, `HEARTBEAT.md` 等也有各自用途

### 问题 2：SSH 中 openclaw 命令找不到

**现象**: 通过 SSH 执行 `openclaw daemon restart` 报 `command not found`。

**原因**: 非交互式 SSH 会话不加载用户的 `.bashrc`，而 openclaw 安装在 `~/.npm-global/bin/` 下，不在默认 PATH 中。

**解决**: 手动 export PATH 后执行：
```bash
export PATH="$HOME/.npm-global/bin:$PATH" && openclaw daemon restart
```

---

## 当前架构

```
Azure VM (20.172.149.137)
  └── OpenClaw Gateway (systemd service)
        ├── AI Provider: GitHub Copilot → claude-opus-4.6
        │
        ├── Agent: bingbing (饼饼)
        │     ├── Discord Bot: 饼饼
        │     └── Workspace: ~/.openclaw/workspace-bingbing/
        │
        ├── Agent: xiaoyuan (小圆)
        │     ├── Discord Bot: 小圆
        │     └── Workspace: ~/.openclaw/workspace-xiaoyuan/
        │
        ├── Agent: gege (鸽鸽)
        │     ├── Discord Bot: 鸽鸽
        │     └── Workspace: ~/.openclaw/workspace-gege/
        │
        └── Agent: shutiao (薯条)
              ├── Discord Bot: 薯条
              └── Workspace: ~/.openclaw/workspace-shutiao/

Agent-to-Agent 通信: 全部互通

AI 模型: GitHub Copilot → claude-opus-4.6（gateway 层统一配置，4 个 bot 共享）
```

> **注意**: AI 模型在 OpenClaw gateway 层面统一配置，不是每个 bot 单独连接。4 个 bot 共用同一个 AI provider（GitHub Copilot 提供的 claude-opus-4.6），通过各自的 SOUL.md + AGENTS.md 获得不同的角色人格。

---

## 相关文档

| 文档 | 内容 |
|------|------|
| [clawdbot-饼饼.md](clawdbot-饼饼.md) | 原始单 bot 部署文档 |
| [Bot团队部署方案.md](Bot团队部署方案.md) | 4 bot 团队部署计划 |
| [多个Discord Bot配置指南.md](多个Discord Bot配置指南.md) | 多 bot 配置参考 |
| [Bot团队协作指南.md](Bot团队协作指南.md) | 团队使用方式和频道规范 |
| [OpenClaw能力总结.md](OpenClaw能力总结.md) | OpenClaw 功能概览 |

---

## 后续可做的事

- [✅ ] 搭建 Discord 频道结构（工作区 + 生活区）
- [ ] 测试饼饼 dispatch 任务给小圆/鸽鸽的 agent-to-agent 协作
- [ ] 测试薯条 DM 私聊记忆隔离
- [ ] 考虑升级 VM 到 Standard_B2ms (8GB) 以获得更充裕的内存

---

**文档创建日期**: 2026-04-09
**维护人员**: xiaoxiao
