# OpenClaw 能力总结

## 什么是 OpenClaw

OpenClaw 是一个开源的 AI Agent 网关（gateway），可以将 AI 模型连接到各种聊天渠道（Discord、Slack 等），并提供多 agent 协作、任务派遣、子 agent 调度等高级能力。

- **官网**: https://openclaw.ai
- **文档**: https://docs.openclaw.ai

---

## 安装方式

### macOS 本地安装
```bash
npm install -g openclaw@latest
openclaw onboard --install-daemon
```

**要求**:
- Node.js 24（推荐）或 Node 22 LTS（22.14+）
- macOS 15+ 可使用 menubar companion app（beta）

### 安装后
- 配置文件位于 `~/.openclaw/openclaw.json`（JSON5 格式）
- 本地控制面板：`http://127.0.0.1:18789/`
- 支持通过 Tailscale 远程访问控制面板

---

## 核心能力

### 1. 多渠道接入

OpenClaw 支持将 AI bot 连接到多种聊天平台：

| 渠道 | 说明 |
|------|------|
| Discord | 支持单 bot 和多 bot 数组配置 |
| Slack | 通过 Slack App 接入 |
| 其他 | 参考官方文档获取最新支持列表 |

### 2. AI 模型配置

支持多种模型提供商：
- **GitHub Copilot** — 通过 GitHub 账号授权，使用 claude-opus-4.6 等模型
- **Anthropic API** — 直接使用 API Key，按量付费
- 其他提供商参考官方文档

### 3. 多 Agent 路由

一个 OpenClaw gateway 可以运行多个独立的 agent，通过路由规则将消息分发到不同 agent。

```json5
{
  agents: {
    list: [
      { id: "home", workspace: "~/.openclaw/workspace-home" },
      { id: "work", workspace: "~/.openclaw/workspace-work" },
    ],
  },
  bindings: [
    { agentId: "home", match: { channel: "discord", accountId: "personal" } },
    { agentId: "work", match: { channel: "discord", accountId: "business" } },
  ],
}
```

**路由优先级**（从高到低）：
1. Peer match — 精确匹配 DM/群组/频道 ID
2. Parent peer match — 线程继承父级路由
3. Guild ID + roles — Discord 角色路由
4. Guild / Team ID
5. Account ID
6. Channel-level match
7. Fallback 到默认 agent

### 4. Agent-to-Agent 通信

不同 agent 之间可以直接通信，需显式启用并配置白名单：

```json5
{
  tools: {
    agentToAgent: {
      enabled: true,
      allow: ["agent-a", "agent-b"],  // 允许互相通信的 agent
    },
  }
}
```

启用后，agent 可以：
- 向其他 agent 发送消息
- 请求其他 agent 执行任务
- 接收来自其他 agent 的结果

### 5. 子 Agent（Sub-Agents）

最强大的协作能力之一 — 一个 agent 可以派生子 agent 来并行执行任务：

```
/subagents spawn <agentId> <task> [--model <model>] [--thinking <level>]
```

**特性**：
- **非阻塞** — 立即返回 run ID，不阻塞主对话
- **结果自动回传** — 子 agent 完成后通过 announce 步骤回报结果
- **可嵌套** — 支持多层级：main → orchestrator → workers
- **并发控制**：
  - `maxConcurrent`: 最大并发数（默认 8）
  - `maxChildrenPerAgent`: 每个 agent 最多子 agent 数（默认 5）
  - `maxSpawnDepth`: 最大嵌套深度（默认 2）

### 6. 任务派遣（Task Dispatch）

三种主要的任务派遣方式：

#### 方式一：CLI 命令派遣
```bash
# 向指定 agent 发送任务
openclaw agent --agent ops --message "Summarize logs"

# 派遣任务并将结果送到聊天频道
openclaw agent --agent ops --message "Generate report" \
  --deliver --reply-channel discord --reply-to "#reports"
```

#### 方式二：Sessions 工具（会话间通信）
内置工具组 `group:sessions`：
- `sessions_send` — 向指定会话发送消息
- `sessions_spawn` — 创建子 agent 会话
- `sessions_list` — 发现活跃会话
- `sessions_history` — 获取历史消息

#### 方式三：Message 工具（跨渠道消息）
```json5
{
  tools: {
    allow: ["message"],
    // 或使用工具组：
    // allow: ["group:messaging"]
  }
}
```
允许 agent 跨所有渠道发送消息。

---

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `openclaw config list` | 查看当前配置 |
| `openclaw config set <key> <value>` | 修改配置 |
| `openclaw daemon restart` | 重启 gateway 服务 |
| `openclaw channels login discord` | 交互式配置 Discord |
| `openclaw agent --agent <id> --message "<task>"` | CLI 派遣任务 |
| `journalctl --user -u openclaw-gateway -f` | 查看实时日志 |

---

## 关键文档链接

| 主题 | 链接 |
|------|------|
| 多 Agent 路由 | https://docs.openclaw.ai/concepts/multi-agent |
| Skills & 协作 | https://docs.openclaw.ai/tools/skills |
| Agent 发送命令 | https://docs.openclaw.ai/tools/agent-send |
| 子 Agent 编排 | https://docs.openclaw.ai/tools/subagents |

---

## 与现有部署的关系

当前已有部署：
- **Azure VM** (20.172.149.137) 上运行 OpenClaw gateway + Discord bot "饼饼"
- 使用 GitHub Copilot 提供的 claude-opus-4.6 模型
- 详见 [clawdbot-饼饼.md](clawdbot-饼饼.md) 和 [多个Discord Bot配置指南.md](多个Discord Bot配置指南.md)

---

**文档创建日期**: 2026-04-08
**维护人员**: xiaoxiao
