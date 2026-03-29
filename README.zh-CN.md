[English](README.md) | [中文](README.zh-CN.md)

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
1. **所有代码都在本地，任意根据你的自己需求修改，任意根据你的自己需求修改，任意根据你的自己需求修改**
2. **你自己不需要改，让 Claude Code 或 OpenClaw 改就行了。**
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

## Example: 语音转文字工具竞品调研

**输入：** `/xhs-research "调研语音转文字工具的竞品，用户需求和痛点"`

**完整报告输出**（227 条笔记，20 篇详情+评论）：

---

### 一、竞品格局

| 排名 | 产品 | 提及频次 | 代表帖互动 | 定位 | 免费额度 |
|------|------|---------|-----------|------|---------|
| 1 | **飞书妙记** | 高频 | ❤️3858+❤️1453+❤️933 | 职场会议转录首选 | 原免费，现已限量 |
| 2 | **通义听悟** | 高频 | 评论区多次推荐 | 免费+全能型，阿里系 | 完全免费 |
| 3 | **讯飞听见** | 高频 | ❤️1146 | 中文准确率最高 | 实时免费，转写付费 |
| 4 | **豆包** | 中频 | 评论区多次提及 | 字节系，免费+方便 | 免费 |
| 5 | **听脑AI** | 中频 | ❤️1146+❤️1453 | AI总结+问答，新锐 | 每天20分钟免费 |
| 6 | **Whisper系列** | 中频 | ❤️222+❤️343 | 开源离线，隐私友好 | 完全免费 |

#### 飞书妙记
- per 李linda（❤️1453）[链接](https://www.xiaohongshu.com/explore/68104a7200000000200283aa)：律师群体推荐飞书做录音转文字
- **限量引发不满**：评论区 young特特特特（2赞）：「现在每个月限制语音转换的条数了😭」— [来源](https://www.xiaohongshu.com/explore/687f9859000000000d0186fe)

#### 通义听悟
- per Jennica骄（❤️3858）[链接](https://www.xiaohongshu.com/explore/687f9859000000000d0186fe)：「免费，自动生成全文概要、思维导图，可批量上传50个文件」
- 评论区 就爱吃甜甜（7赞）：「通义=飞书减去语气词」— [来源](https://www.xiaohongshu.com/explore/66a8cfd3000000000503a76a)

#### Whisper 系列
- per 东海化工丁厂长（❤️222）[链接](https://www.xiaohongshu.com/explore/6807cd7e000000001d039682)：「中英文夹杂完全OK转写95%准确」
- per 一套组合拳（❤️107）[链接](https://www.xiaohongshu.com/explore/680c9cf9000000001d0052ce)：「涉及敏感信息，绝对不能传到网上」→ 选 Whisper

#### 竞品对比表

| 维度 | 通义听悟 | 飞书妙记 | 讯飞听见 | 听脑AI | Whisper | 豆包 |
|------|---------|---------|---------|--------|---------|------|
| **价格** | 免费 | 免费→限量 | 付费为主 | 20min/天 | 完全免费 | 免费 |
| **中文准确率** | 中等 | 中等 | 最高 | 较高 | 高 | 中等 |
| **中英混杂** | 一般 | 一般 | 差 | — | 优秀(95%) | — |
| **AI总结/问答** | 有 | 有 | 无 | 强 | 无 | 有 |
| **离线/隐私** | 否 | 否 | 否 | 否 | 是 | 否 |

### 二、用户画像

| 用户类型 | 典型场景 | 代表帖 |
|---------|---------|--------|
| **职场打工人** | 会议纪要 | per 打工人效率研究所（❤️7390）[链接](https://www.xiaohongshu.com/explore/68f1ec00000000000703246a) |
| **律师/咨询师** | 庭审/访谈记录 | per 李linda（❤️1453）[链接](https://www.xiaohongshu.com/explore/68104a7200000000200283aa) |
| **隐私敏感者** | 敏感音频 | per 一套组合拳（❤️107）[链接](https://www.xiaohongshu.com/explore/680c9cf9000000001d0052ce) |
| **灵感记录者** | 随时记录想法 | per Mazzystar（❤️343）[链接](https://www.xiaohongshu.com/explore/642d0ebb00000000130344ba) |

### 三、用户痛点矩阵

| 痛点 | 严重度 | 代表性证据 |
|------|--------|-----------|
| **准确率不够** | 🔴 高 | per 李linda：「需要自己去校对」[链接](https://www.xiaohongshu.com/explore/68104a7200000000200283aa) |
| **方言/口音识别差** | 🔴 高 | per 李linda：「方言需要人工校对」[链接](https://www.xiaohongshu.com/explore/68104a7200000000200283aa) |
| **中英混杂识别差** | 🔴 高 | per 东海化工丁厂长：讯飞、飞书对中英混杂差 [链接](https://www.xiaohongshu.com/explore/6807cd7e000000001d039682) |
| **免费额度不够** | 🔴 高 | 评论区（642赞）「说明没有免费的」[链接](https://www.xiaohongshu.com/explore/671a46080000000021009404) |
| **说话人识别缺失** | 🟡 中 | 评论区 momosaysss：「可以分离说话者吗？」[链接](https://www.xiaohongshu.com/explore/6807cd7e000000001d039682) |
| **隐私/安全顾虑** | 🟡 中 | per 一套组合拳：「绝对不能传到网上」[链接](https://www.xiaohongshu.com/explore/680c9cf9000000001d0052ce) |

### 四、用户需求清单

1. **准确率是第一需求** — 尤其专业术语、方言、混合语言场景
2. **免费/高性价比** — 评论区反复问「免费吗」，飞书限量后用户迅速流失 [链接](https://www.xiaohongshu.com/explore/671a46080000000021009404)
3. **AI总结 & 智能整理** — 从转写升级为「转写+总结+问答」[链接](https://www.xiaohongshu.com/explore/66a8cfd3000000000503a76a)
4. **中英文混杂支持** — 目前仅 Whisper 表现好 [链接](https://www.xiaohongshu.com/explore/6807cd7e000000001d039682)
5. **离线/隐私** — 律师、企业用户刚需

### 五、用户决策逻辑

1. **先试免费的** → 通义/豆包/飞书
2. **免费不够用** → 付费（讯飞/听脑）或找替代
3. **对准确率有要求** → 讯飞（纯中文）、Whisper（中英混杂）
4. **对隐私有要求** → Whisper 系列
5. **要AI总结** → 听脑AI / 通义

评论区 舍与得：「华为备忘录转文字，往豆包一丢就整理完了」— [来源](https://www.xiaohongshu.com/explore/66a8cfd3000000000503a76a) → **用户会组合多工具**

### 六、关键趋势

1. **从「转写」到「理解」** — 用户要 AI 总结+问答，不只是转录
2. **免费正在收缩** — 飞书限量，新产品窗口期
3. **隐私需求上升** — Whisper 离线处理成差异化卖点
4. **iPhone 原生冲击** — iOS 18+ 自带录音转文字（❤️7390+❤️4920）

> **数据偏差声明**：本报告数据仅来源于小红书用户个人体验，可能存在推广帖、幸存者偏差等问题。

---

📕 小红书: 227 条笔记（8轮搜索）│ 20 篇详情 │ 149,458 赞 │ 97,286 收藏 │ 62,328 评论
🔥 最高互动: 语音转文字的尴尬瞬间（❤️50,793）
🗣️ 主要作者: Jennica骄, 打工人效率研究所, 东海化工丁厂长, 就爱吃甜甜, Mazzystar

---

## 文件位置

| 文件 | 路径 |
|------|------|
| MCP 二进制 | `~/.local/share/xhs-research/bin/` |
| 登录 Cookie | `~/.local/share/xhs-research/cookies.json` |
| 调研报告 | `~/Documents/XHS-Research/` |

## 常见问题

### macOS 弹出「钥匙串」密码框？

登录时可能弹出「security 想要使用钥匙串 Chrome Safe Storage」弹窗。**直接点「拒绝」即可**，不影响登录功能。

### 怎么更新 Skill？

直接告诉 Claude Code 或 OpenClaw：

```
帮我更新 xhs-research skill
```

或者手动：
```bash
cd ~/.claude/skills/xhs-research && git pull
```

> 注意：如果你之前让 Claude 修改过代码（如自定义搜索参数），git pull 可能会冲突。建议先备份你的修改。

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
