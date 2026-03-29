[English](README.md) | [中文](README.zh-CN.md)

# xhs-research — Xiaohongshu Research Skill

A ready-to-use Xiaohongshu (Little Red Book) research tool. Once installed, just scan the QR code to log in, then use Claude Code / OpenClaw / Gemini CLI to research any topic on Xiaohongshu.

## Quick Start

Copy and paste the following message to Claude Code or OpenClaw:

```
Install this Xiaohongshu research Skill for me: https://github.com/kunhai1994/xhs-research
```

After installation, **start a new conversation/session**, then type:

```
/xhs-research "your research topic"
```

The Skill will automatically install all dependencies. **The only thing you need to do is scan the QR code with the Xiaohongshu app to log in.**

## Usage Examples

```
/xhs-research "best prenatal hospitals in Shenzhen"
/xhs-research "AI art tutorials, tool comparison"
/xhs-research "camping gear, what to avoid"
/xhs-research "home coffee machine recommendations"
```

## Customization

1. **All code lives on your machine — feel free to modify it however you like.**
2. **You don't need to touch the code yourself. Just ask Claude Code or OpenClaw to do it.**

## Architecture

```
User: /xhs-research "topic"
  │
  ▼
SKILL.md (prompt)                ← Instructs the LLM on what to do
  │
  ├─ LLM generates search terms  ← Smart expansion (synonyms / subtopics / pros & cons)
  │
  ▼
xhs_research.py (research engine) ← Inspired by last30days cross-platform strategy
  │
  ├─ Multi-round parallel search   ← 5–8 keywords × ~42 results/round
  ├─ Three-dimensional scoring     ← Relevance 40% + Recency 25% + Engagement 35%
  ├─ Deduplication                 ← feed_id + Jaccard title similarity
  ├─ Top 20 detail fetching        ← Full text + top comments + replies
  │
  ▼
LLM synthesizes research report   ← Rankings / comparisons / red flags / trend analysis
```

Under the hood:
- **[xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp)** — Xiaohongshu search service (auto-installed)
- Research engine inspired by the scoring, deduplication, and query expansion strategies from **[last30days-skill](https://github.com/mvanhorn/last30days-skill)**

## Default Settings

| Setting | Default | Description |
|---------|---------|-------------|
| Search mode | deep | Most comprehensive |
| Time range | unlimited | Searches all history |
| Keywords | 5–8 | LLM-generated |
| Results per round | ~42 | Xiaohongshu API limit |
| Total after dedup | 80–150 | Depends on topic |
| Detail fetching | Top 20 | Includes full text + comments |

Override with flags: `--quick` (fast mode), `--days=7` (last 7 days), `--top=10` (number of detailed results)

## Example: Competitive Analysis of Speech-to-Text Tools

**Input:** `/xhs-research "research speech-to-text tool competitors, user needs and pain points"`

**Full report output** (227 notes, 20 detailed posts + comments):

---

### 1. Competitive Landscape

| Rank | Product | Mention Frequency | Top Post Engagement | Positioning | Free Tier |
|------|---------|------------------|--------------------|----|-----------|
| 1 | **Feishu Minutes** | High | ❤️3858+❤️1453+❤️933 | Go-to for workplace meeting transcription | Was free, now limited |
| 2 | **Tongyi Tingwu** | High | Frequently recommended in comments | Free + all-in-one, Alibaba ecosystem | Completely free |
| 3 | **iFlytek** | High | ❤️1146 | Highest Chinese accuracy | Real-time free, transcription paid |
| 4 | **Doubao** | Medium | Mentioned in comments | ByteDance ecosystem, free + convenient | Free |
| 5 | **Tingnao AI** | Medium | ❤️1146+❤️1453 | AI summary + Q&A, rising star | 20 min/day free |
| 6 | **Whisper** | Medium | ❤️222+❤️343 | Open-source offline, privacy-friendly | Completely free |

#### Feishu Minutes
- Per Li Linda (❤️1453) [link](https://www.xiaohongshu.com/explore/68104a7200000000200283aa): recommended by lawyers for audio-to-text
- **Usage limits cause frustration**: comment by young特特特特 (2 likes): "They now limit the number of voice conversions per month 😭" — [source](https://www.xiaohongshu.com/explore/687f9859000000000d0186fe)

#### Tongyi Tingwu
- Per Jennica骄 (❤️3858) [link](https://www.xiaohongshu.com/explore/687f9859000000000d0186fe): "Free, auto-generates summaries & mind maps, supports batch upload of 50 files"
- Comment by 就爱吃甜甜 (7 likes): "Tongyi = Feishu minus filler words" — [source](https://www.xiaohongshu.com/explore/66a8cfd3000000000503a76a)

#### Whisper
- Per 东海化工丁厂长 (❤️222) [link](https://www.xiaohongshu.com/explore/6807cd7e000000001d039682): "Handles mixed Chinese-English perfectly, 95% accuracy"
- Per 一套组合拳 (❤️107) [link](https://www.xiaohongshu.com/explore/680c9cf9000000001d0052ce): "Sensitive information must never be uploaded" → chose Whisper

#### Competitive Comparison

| Dimension | Tongyi Tingwu | Feishu Minutes | iFlytek | Tingnao AI | Whisper | Doubao |
|-----------|--------------|----------------|---------|------------|---------|--------|
| **Price** | Free | Free → limited | Mostly paid | 20 min/day | Completely free | Free |
| **Chinese accuracy** | Medium | Medium | Highest | High | High | Medium |
| **Mixed CN-EN** | Fair | Fair | Poor | — | Excellent (95%) | — |
| **AI summary/Q&A** | Yes | Yes | No | Strong | No | Yes |
| **Offline/privacy** | No | No | No | No | Yes | No |

### 2. User Profiles

| User Type | Typical Scenario | Representative Post |
|-----------|-----------------|---------------------|
| **Office workers** | Meeting minutes | Per 打工人效率研究所 (❤️7390) [link](https://www.xiaohongshu.com/explore/68f1ec00000000000703246a) |
| **Lawyers / Consultants** | Court / interview transcripts | Per 李linda (❤️1453) [link](https://www.xiaohongshu.com/explore/68104a7200000000200283aa) |
| **Privacy-conscious users** | Sensitive audio | Per 一套组合拳 (❤️107) [link](https://www.xiaohongshu.com/explore/680c9cf9000000001d0052ce) |
| **Idea capturers** | Record thoughts on the go | Per Mazzystar (❤️343) [link](https://www.xiaohongshu.com/explore/642d0ebb00000000130344ba) |

### 3. Pain Point Matrix

| Pain Point | Severity | Key Evidence |
|------------|----------|-------------|
| **Insufficient accuracy** | 🔴 High | Per 李linda: "You still have to proofread it yourself" [link](https://www.xiaohongshu.com/explore/68104a7200000000200283aa) |
| **Poor dialect/accent recognition** | 🔴 High | Per 李linda: "Dialects require manual correction" [link](https://www.xiaohongshu.com/explore/68104a7200000000200283aa) |
| **Poor mixed-language recognition** | 🔴 High | Per 东海化工丁厂长: iFlytek and Feishu struggle with mixed CN-EN [link](https://www.xiaohongshu.com/explore/6807cd7e000000001d039682) |
| **Insufficient free quota** | 🔴 High | Comment (642 likes) "Means there's no free option" [link](https://www.xiaohongshu.com/explore/671a46080000000021009404) |
| **No speaker identification** | 🟡 Medium | Comment by momosaysss: "Can it separate speakers?" [link](https://www.xiaohongshu.com/explore/6807cd7e000000001d039682) |
| **Privacy / security concerns** | 🟡 Medium | Per 一套组合拳: "Must never be uploaded online" [link](https://www.xiaohongshu.com/explore/680c9cf9000000001d0052ce) |

### 4. User Needs

1. **Accuracy is the #1 need** — especially for jargon, dialects, and mixed-language scenarios
2. **Free or affordable** — comments repeatedly ask "Is it free?"; users fled Feishu after limits were imposed [link](https://www.xiaohongshu.com/explore/671a46080000000021009404)
3. **AI summaries & smart organization** — users want more than transcription: "transcription + summary + Q&A" [link](https://www.xiaohongshu.com/explore/66a8cfd3000000000503a76a)
4. **Mixed Chinese-English support** — currently only Whisper handles this well [link](https://www.xiaohongshu.com/explore/6807cd7e000000001d039682)
5. **Offline / privacy** — a hard requirement for lawyers and enterprise users

### 5. User Decision Logic

1. **Try free tools first** → Tongyi / Doubao / Feishu
2. **Free isn't enough** → Pay (iFlytek / Tingnao) or find alternatives
3. **Need high accuracy** → iFlytek (pure Chinese), Whisper (mixed-language)
4. **Need privacy** → Whisper
5. **Need AI summaries** → Tingnao AI / Tongyi

Comment by 舍与得: "Use Huawei Memo to transcribe, then toss it into Doubao to organize" — [source](https://www.xiaohongshu.com/explore/66a8cfd3000000000503a76a) → **Users often combine multiple tools**

### 6. Key Trends

1. **From "transcription" to "comprehension"** — users want AI summaries and Q&A, not just raw text
2. **Free tiers are shrinking** — Feishu's new limits create an opening for newcomers
3. **Rising demand for privacy** — Whisper's offline processing is a real differentiator
4. **Native iOS disruption** — iOS 18+ built-in voice-to-text (❤️7390+❤️4920)

> **Data bias disclaimer**: This report is based solely on individual user experiences shared on Xiaohongshu and may contain promotional posts, survivorship bias, and other distortions.

---

📕 Xiaohongshu: 227 notes (8 search rounds) │ 20 detailed posts │ 149,458 likes │ 97,286 saves │ 62,328 comments
🔥 Highest engagement: Awkward moments with speech-to-text (❤️50,793)
🗣️ Top contributors: Jennica骄, 打工人效率研究所, 东海化工丁厂长, 就爱吃甜甜, Mazzystar

---

## File Locations

| File | Path |
|------|------|
| MCP binary | `~/.local/share/xhs-research/bin/` |
| Login cookie | `~/.local/share/xhs-research/cookies.json` |
| Research reports | `~/Documents/XHS-Research/` |

## FAQ

### macOS pops up a "Keychain" password dialog?

During login, you may see a "security wants to use the Chrome Safe Storage keychain" dialog. **Just click "Deny"** — it won't affect login functionality.

### How do I update the Skill?

Just tell Claude Code or OpenClaw:

```
Update xhs-research skill for me
```

Or manually:
```bash
cd ~/.claude/skills/xhs-research && git pull
```

> Note: If you've previously asked Claude to modify the code (e.g., custom search parameters), `git pull` may cause conflicts. Back up your changes first.

### Cookie expired?

The next time you use `/xhs-research`, it will automatically detect the expiration and prompt you to scan the QR code again.

### What platforms are supported?

macOS (Intel / Apple Silicon), Linux, and Windows (via WSL).

## System Requirements

- Python 3.9+
- Git
- Google Chrome (required for login)

## License

MIT

## Acknowledgments

- [last30days-skill](https://github.com/mvanhorn/last30days-skill) — scoring, deduplication, and query expansion strategies
- [xiaohongshu-mcp](https://github.com/xpzouying/xiaohongshu-mcp) — Xiaohongshu search service
