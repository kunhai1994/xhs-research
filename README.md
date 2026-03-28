# 📕 xhs-research — 小红书调研 Skill

开箱即用的小红书调研工具。安装后只需扫码登录，即可用 Claude Code / OpenClaw / Gemini CLI 调研小红书。

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

**所有代码都在本地，可以根据你的需求做修改。你自己不需要改，让 Claude Code 或 OpenClaw 改就行了。**

## 架构

```
用户: /xhs-research "话题"
  │
  ▼
SKILL.md (prompt)                ← 指导 LLM 做什么
  │
  ├─ LLM 生成搜索关键字           ← 智能扩展（同义词/细分/正反面）
  │
  ▼
xhs_research.py (调研引擎)       ← 借鉴 last30days 全平台策略
  │
  ├─ 多轮并行搜索                 ← 5-8 关键字 × ~42 条/轮
  ├─ 三维评分                     ← 相关性 40% + 时间 25% + 互动 35%
  ├─ 去重                         ← feed_id + Jaccard 标题去重
  ├─ Top 20 获取详情+评论          ← 正文 + 热评 + 子评论
  │
  ▼
LLM 合成调研报告                  ← 排名/对比/避雷/趋势分析
```

底层依赖：
- **[xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)** — 小红书搜索服务（自动安装）
- 调研引擎借鉴 **[last30days-skill](https://github.com/mvanhorn/last30days-skill)** 的评分/去重/查询扩展策略

## 默认配置

| 配置 | 默认值 | 说明 |
|------|--------|------|
| 搜索模式 | deep | 最全面 |
| 时间范围 | 不限 | 搜索所有历史 |
| 关键字数 | 5-8 个 | LLM 智能生成 |
| 每轮返回 | ~42 条 | 小红书 API 限制 |
| 去重后总量 | 80-150 条 | 取决于话题 |
| 详情获取 | Top 20 | 含正文+评论 |

可用参数覆盖：`--quick`（快速）、`--days=7`（7天内）、`--top=10`（详情数）

## Example: 家用咖啡机推荐

**输入：** `/xhs-research "咖啡机推荐 家用"`

**引擎输出摘要**（117 条笔记去重后，20 篇获取详情+评论）：

> 🏆 小红书热门推荐：
>
> **德龙 (De'Longhi)** — 提及最多的品牌
> - 全自动：德龙 450.86 是「懒人首选」，外观好看操作傻瓜，十秒一杯。per Tdoudou（❤️87）
> - 半自动：德龙 9555 是「咖啡角颜值担当」。per 哇哈哈的装修日记（❤️486）
> - 评论区吐槽：「蹲几个月了，就没下过7000」「做拿铁奶泡还是差点意思」
>
> **半自动 vs 全自动** — 最热门争论
> - per 果果的理想家（❤️1515 💬1218 ⭐1577）：「上限要高，下限要稳」
> - 评论区共识：新手/懒人选全自动，想玩拉花选半自动

> ---
> 📕 小红书: 117 条笔记（5轮搜索）│ 20 篇详情 │ 72,120 赞 │ 48,456 收藏 │ 17,035 评论
> 🔥 最高互动: 终选｜人生第一台咖啡机（❤️13,000）
> 🗣️ 主要作者: 果果的理想家, Cssssssssj, 哇哈哈的装修日记

## 文件位置

| 文件 | 路径 |
|------|------|
| MCP 二进制 | `~/.local/share/xhs-research/bin/` |
| 登录 Cookie | `~/.local/share/xhs-research/cookies.json` |
| 调研报告 | `~/Documents/XHS-Research/` |

## 常见问题

### macOS 弹出「钥匙串」密码框？

登录时可能弹出「security 想要使用钥匙串 Chrome Safe Storage」弹窗。**直接点「拒绝」即可**，不影响登录功能。

### Cookie 过期了？

再次使用 `/xhs-research` 时会自动检测，提示你重新扫码。

### 支持什么系统？

macOS (Intel/Apple Silicon)、Linux、Windows (通过 WSL)。

## 系统要求

- Python 3.9+
- Git
- Google Chrome（登录时需要）

## 许可证

MIT

## 致谢

- [last30days-skill](https://github.com/mvanhorn/last30days-skill) — 评分/去重/查询扩展策略来源
- [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) — 小红书搜索服务
