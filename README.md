# 📕 xhs-research — 小红书调研 Skill

开箱即用的小红书调研工具。安装后只需扫码登录，即可用 Claude Code / OpenClaw 调研小红书。

## 快速开始

复制下面这段话，发给 Claude Code 或 OpenClaw：

```
帮我安装这个小红书调研 Skill：https://github.com/kunhai1994/xhs-research
```

安装完成后，**重新开一个新的对话/session**，然后输入：

```
/xhs-research "你想调研的话题"
```

Skill 会自动安装所有依赖。**唯一需要你操作的是用小红书 App 扫码登录。**

## 使用示例

```
/xhs-research "深圳产检医院推荐"
/xhs-research "AI绘画教程 工具对比"
/xhs-research "露营装备 避雷"
/xhs-research "咖啡机推荐 家用"
```

## 关于定制化需求修改

**由于我们对搜索、整理策略的代码是直接clone 到本地的，所以可以根据你自己的需求（比如扩大搜索时间范围等）做代码修改，自己也不需要修改，让claude code 或openclaw 修改就行了**

## 架构

```
用户: /xhs-research "话题"
  │
  ▼
SKILL.md (prompt)              ← 指导 Claude 做什么
  │
  ├─ 自动安装 last30days 引擎    ← git clone (一次性)
  ├─ 自动安装 xiaohongshu-mcp   ← 下载二进制 (一次性)
  ├─ 自动启动搜索服务            ← localhost:18060
  ├─ 引导扫码登录               ← 用户扫一次码
  │
  ▼
搜索小红书 → AI 合成报告
```

本质上就是一段 prompt（SKILL.md），教会 Claude 如何：
1. 安装和管理依赖（[last30days](https://github.com/mvanhorn/last30days-skill) + [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)）
2. 搜索小红书笔记
3. 合成结构化调研报告

## 文件位置

安装后，依赖文件存放在：

| 文件 | 路径 |
|------|------|
| 搜索引擎 | `~/.local/share/xhs-research/last30days/` |
| MCP 二进制 | `~/.local/share/xhs-research/bin/` |
| 登录 Cookie | `~/.local/share/xhs-research/cookies.json` |
| 配置 | `~/.config/last30days/.env` |
| 调研报告 | `~/Documents/XHS-Research/` |

## 常见问题

### Cookie 过期了？

再次使用 `/xhs-research` 时会自动检测，提示你重新扫码。

### 搜索时间范围？

默认搜索半年内的笔记。如需搜索更长时间（1-2年），修改引擎文件：

```
文件：~/.local/share/xhs-research/last30days/scripts/lib/xiaohongshu_api.py
第 89 行：将 "半年内" 改为 "不限"
```

> 注意：更新引擎（`git pull`）后此修改会被覆盖。

### 想搜索其他平台（Reddit、X 等）？

本 Skill 只负责小红书。其他平台请参考 [last30days 官方文档](https://github.com/mvanhorn/last30days-skill)。

### 支持什么系统？

macOS (Intel/Apple Silicon) 和 Linux。Windows 用户通过 WSL 使用。

## 系统要求

- Python 3.9+
- Git
- Google Chrome（登录时需要）

## 许可证

MIT

## 致谢

- [last30days-skill](https://github.com/mvanhorn/last30days-skill) — 调研引擎
- [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) — 小红书搜索服务
