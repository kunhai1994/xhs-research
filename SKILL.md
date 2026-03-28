---
name: xhs-research
version: "1.0.0"
description: "小红书调研工具 — 开箱即用搜索小红书笔记，AI 合成调研报告。"
argument-hint: 'xhs-research 深圳产检医院推荐, xhs-research AI绘画教程'
allowed-tools: Bash, Read, Write, AskUserQuestion
author: kunhai1994
license: MIT
user-invocable: true
metadata:
  openclaw:
    emoji: "📕"
    requires:
      bins:
        - python3
        - git
    primaryEnv: ""
---

# xhs-research: 小红书调研工具

> 搜索小红书笔记，AI 合成调研报告。
> 底层：[last30days](https://github.com/mvanhorn/last30days-skill) + [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)

---

## Step 0: 环境检查与自动安装

**每次调用前必须先检查环境。** 运行状态检查脚本：

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/status.py" --json
```

根据返回的 JSON，按顺序修复失败项：

1. **`last30days_installed` 或 `mcp_binary_installed` 为 false** → 运行安装：
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/setup.py"
   ```

2. **`mcp_running` 为 false** → 启动服务：
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/start.py"
   ```

3. **`xhs_logged_in` 为 false** → 先告诉用户「正在打开小红书登录页面，请准备好手机扫码」，然后**直接运行**：
   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/scripts/login.py"
   ```
   Chrome 会自动弹出二维码。用户扫码后脚本会自动完成验证和启动服务。等脚本执行完毕即可。

   **macOS 用户注意**：可能会弹出「security 想要使用钥匙串 Chrome Safe Storage」的系统弹窗，点击「拒绝」即可，不影响登录功能。

4. **`all_ready` 为 true** → 进入搜索。

---

## Step 1: 解析用户意图

从用户输入提取：
- **TOPIC**：调研主题
- **QUERY_TYPE**：
  - **推荐** — 「推荐」「最好的」「top」「排名」
  - **调研** — 「调研」「了解」「怎么样」「痛点」「需求」
  - **对比** — 「A vs B」「A 和 B 哪个好」

显示：
```
我将在小红书上调研「{TOPIC}」。
- 类型 = {QUERY_TYPE}
搜索中，通常需要 30s - 2min...
```

---

## Step 2: 执行搜索

```bash
XIAOHONGSHU_API_BASE=http://localhost:18060 python3 \
  "$HOME/.local/share/xhs-research/last30days/scripts/last30days.py" \
  "{TOPIC}" \
  --search xiaohongshu \
  --deep \
  --emit=compact \
  --no-native-web \
  --save-dir="$HOME/Documents/XHS-Research"
```

**timeout 300000**（5 分钟），前台运行。读取完整输出。

### 时间范围

`--deep` 默认搜索**半年内**。如果用户要求更长时间（1-2年），用 Edit 工具修改引擎：
- 文件：`~/.local/share/xhs-research/last30days/scripts/lib/xiaohongshu_api.py`
- 第 89 行：`"半年内"` → `"不限"`

---

## Step 3: 合成报告

### 权重
小红书互动数据权重：**收藏 > 评论 > 赞**。收藏 = 最强信号（实用）。

### 内容模式
识别并标注：**测评** / **教程**（保姆级） / **种草** / **避雷** / **经验分享** / **求助**（评论区是金矿）

### 引用格式
正文引用：`per 作者昵称（❤️N）`

详细引用：
```
「笔记标题」— 作者昵称（❤️N 💬N ⭐N）
链接：https://www.xiaohongshu.com/explore/xxx
```

评论区引用：`评论区 用户昵称（N赞）：「评论内容」`

**不要贴裸 URL。**

### 统计格式（报告末尾）
```
---
📕 小红书: {N} 条笔记 │ {总赞} 赞 │ {总收藏} 收藏 │ {总评论} 评论
🔥 最高互动: {帖标题}（❤️{N}）
🗣️ 主要作者: {作者1}, {作者2}, {作者3}
---
```

---

## Step 4: 输出

**推荐类**：按提及频次/互动量排序列表，每项标注来源。

**调研类**：按主题分组，每个发现标注来源，末尾列关键趋势。

**对比类**：表格对比，标注来源。

---

## Step 5: 邀请后续

```
我已经是「{TOPIC}」的小红书调研专家。可以继续问我：
- [基于实际调研内容的具体建议1]
- [具体建议2]
- [具体建议3]
```

后续提问从已有结果回答，不重新搜索。用户明确要求新话题才重新搜索。

---

## Security & Permissions

- 只读搜索，不发帖/点赞/评论
- 搜索通过本地 MCP 服务（localhost:18060），不直接发送数据到外部
- Cookie 由 xiaohongshu-mcp 管理，存在 `~/.local/share/xhs-research/cookies.json`
- 调研报告保存到 `~/Documents/XHS-Research/`
