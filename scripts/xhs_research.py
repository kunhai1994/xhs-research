#!/usr/bin/env python3
"""xhs-research: 小红书调研引擎。

借鉴 last30days 全平台策略（查询扩展、三维评分、去重、评论丰富），
专为小红书设计的一等公民级调研引擎。

使用方式:
  # LLM 传关键字（主路径，通过 SKILL.md）
  python3 xhs_research.py --keywords "kw1,kw2,kw3" --deep

  # 直接传主题（fallback，命令行直接用）
  python3 xhs_research.py "咖啡机推荐 家用" --deep
"""

import argparse
import json
import math
import os
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
MCP_BASE = os.environ.get("XIAOHONGSHU_API_BASE", "http://localhost:18060")

# Depth profiles
DEPTH_CONFIG = {
    "quick": {"detail_top": 8, "comment_top": 5},
    "deep":  {"detail_top": 20, "comment_top": 8},
}

# Days → publish_time mapping
PUBLISH_TIME_MAP = [
    (1,   "一天内"),
    (7,   "一周内"),
    (30,  "一个月内"),
    (180, "半年内"),
]

# ---------------------------------------------------------------------------
# Query intent classification (策略 9)
# ---------------------------------------------------------------------------
QUERY_PATTERNS = {
    "推荐": ["推荐", "最好", "最佳", "top", "排名", "哪个好", "求推荐", "有没有好的"],
    "测评": ["测评", "评测", "对比", "vs", "versus", "区别"],
    "攻略": ["攻略", "教程", "怎么", "如何", "方法", "步骤", "流程", "指南"],
    "避雷": ["避雷", "踩坑", "不推荐", "别买", "差评", "吐槽", "不要"],
    "产品调研": ["产品调研", "用户体验", "使用场景", "为什么用", "怎么评价"],
    "竞品调研": ["竞品", "竞争", "赛道", "格局", "市场份额"],
    "需求调研": ["痛点", "需求", "想要", "希望", "缺", "不足", "改进", "建议"],
    "调研": ["调研", "分析", "场景", "市场", "用户"],
}


def classify_query(topic: str) -> str:
    """Classify query intent. Returns: 推荐/测评/攻略/避雷/调研/通用."""
    topic_lower = topic.lower()
    for qtype, patterns in QUERY_PATTERNS.items():
        for p in patterns:
            if p in topic_lower:
                return qtype
    return "通用"


# ---------------------------------------------------------------------------
# Query expansion — fallback mode (策略 1)
# ---------------------------------------------------------------------------
NOISE_WORDS = frozenset({"推荐", "最好", "最佳", "求", "有没有", "哪个", "怎么样", "吗", "请问", "想问"})

FALLBACK_SUFFIXES = {
    "推荐": ["推荐", "攻略", "排名", "避雷", "种草"],
    "测评": ["测评", "对比", "体验", "优缺点"],
    "攻略": ["攻略", "教程", "新手", "小白"],
    "避雷": ["踩坑", "不推荐", "吐槽", "推荐"],
    "产品调研": ["体验", "吐槽", "优缺点", "使用场景", "推荐"],
    "竞品调研": ["推荐", "对比", "排名", "哪个好", "怎么选"],
    "需求调研": ["痛点", "吐槽", "希望", "建议", "体验"],
    "调研": ["推荐", "攻略", "体验", "痛点"],
    "通用": ["推荐", "攻略", "体验"],
}


def _extract_core(topic: str) -> str:
    """Remove noise words to extract core subject."""
    words = topic.strip().split()
    core = [w for w in words if w not in NOISE_WORDS]
    if not core:
        # All words are noise — return empty, caller handles it
        return ""
    return " ".join(core)


def expand_query_fallback(topic: str, depth: str) -> List[str]:
    """Generate keyword variants using static word library (fallback mode)."""
    qtype = classify_query(topic)
    core = _extract_core(topic)
    suffixes = FALLBACK_SUFFIXES.get(qtype, FALLBACK_SUFFIXES["通用"])

    queries = [topic.strip()]  # Always include original

    if core:  # Only expand if core extraction succeeded
        for suffix in suffixes:
            variant = f"{core}{suffix}"
            if variant not in queries:
                queries.append(variant)

    limit = 3 if depth == "quick" else 5
    return queries[:limit]


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only)
# ---------------------------------------------------------------------------
def _http_post_json(url: str, payload: dict, timeout: int = 30, retries: int = 3) -> Optional[dict]:
    """POST JSON and parse response. Returns None on failure."""
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(retries):
        try:
            req = urllib.request.Request(
                url, data=data,
                headers={"Content-Type": "application/json", "User-Agent": "xhs-research/1.0"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
                _log(f"Retry {attempt + 1}/{retries} for {url}: {e}")
            else:
                _log(f"Failed after {retries} attempts: {url}: {e}")
    return None


def _http_get_json(url: str, timeout: int = 5) -> Optional[dict]:
    """GET and parse JSON."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "xhs-research/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def _log(msg: str):
    sys.stderr.write(f"[xhs-research] {msg}\n")
    sys.stderr.flush()


# ---------------------------------------------------------------------------
# Chinese number parsing (万/亿)
# ---------------------------------------------------------------------------
def _to_int(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        return int(value)
    text = str(value).strip().lower().replace(",", "")
    if not text:
        return 0
    try:
        if text.endswith("万"):
            return int(float(text[:-1]) * 10000)
        if text.endswith("亿"):
            return int(float(text[:-1]) * 100000000)
        return int(float(text))
    except (TypeError, ValueError):
        return 0


# ---------------------------------------------------------------------------
# Multi-round search (策略 4, 11)
# ---------------------------------------------------------------------------
def _search_one(keyword: str, publish_time: str) -> List[Dict]:
    """Search XHS with a single keyword. Returns list of note dicts."""
    payload = {
        "keyword": keyword,
        "filters": {
            "sort_by": "综合",
            "note_type": "不限",
            "publish_time": publish_time,
            "search_scope": "不限",
            "location": "不限",
        },
    }
    resp = _http_post_json(f"{MCP_BASE}/api/v1/feeds/search", payload, timeout=30, retries=3)
    if not resp or not isinstance(resp, dict):
        return []

    feeds = resp.get("data", {}).get("feeds", [])
    if not isinstance(feeds, list):
        return []

    items = []
    for feed in feeds:
        if not isinstance(feed, dict):
            continue
        note = feed.get("noteCard") or {}
        feed_id = str(feed.get("id") or note.get("noteId") or "").strip()
        if not feed_id:
            continue

        interact = note.get("interactInfo") or {}
        xsec = str(feed.get("xsecToken") or note.get("xsecToken") or "")
        title = str(note.get("displayTitle") or note.get("title") or "").strip()
        snippet = str(note.get("desc") or note.get("displayDesc") or title or "").strip()

        likes = _to_int(interact.get("likedCount"))
        comments = _to_int(interact.get("commentCount"))
        favorites = _to_int(interact.get("collectedCount"))

        ts = note.get("time")
        date_str = None
        if ts:
            try:
                iv = int(ts)
                if iv > 0:
                    dt = datetime.fromtimestamp(iv / 1000.0, tz=timezone.utc)
                    date_str = dt.strftime("%Y-%m-%d")
            except (TypeError, ValueError, OSError):
                pass

        items.append({
            "feed_id": feed_id,
            "xsec_token": xsec,
            "title": title[:200],
            "snippet": snippet[:500],
            "url": f"https://www.xiaohongshu.com/explore/{feed_id}",
            "date": date_str,
            "likes": likes,
            "comments": comments,
            "favorites": favorites,
            "keyword": keyword,
        })

    return items


def search_multi(keywords: List[str], publish_time: str) -> List[Dict]:
    """Search multiple keywords in parallel, deduplicate by feed_id."""
    all_items: Dict[str, Dict] = {}

    with ThreadPoolExecutor(max_workers=min(len(keywords), 5)) as executor:
        futures = {executor.submit(_search_one, kw, publish_time): kw for kw in keywords}
        for future in as_completed(futures):
            kw = futures[future]
            try:
                results = future.result(timeout=60)
                for item in results:
                    fid = item["feed_id"]
                    if fid not in all_items:
                        all_items[fid] = item
                _log(f'"{kw}" → {len(results)} results, total unique: {len(all_items)}')
            except Exception as e:
                _log(f'"{kw}" → error: {e}')

    items = list(all_items.values())

    # Jaccard title dedup (策略 4, 阈值 0.60)
    items = _dedupe_by_title(items, threshold=0.60)

    return items


# ---------------------------------------------------------------------------
# Deduplication (策略 4)
# ---------------------------------------------------------------------------
def _trigrams(text: str) -> set:
    """Generate character trigrams from text."""
    t = text.lower().strip()
    if len(t) < 3:
        return {t}
    return {t[i:i + 3] for i in range(len(t) - 2)}


def _jaccard(a: set, b: set) -> float:
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _dedupe_by_title(items: List[Dict], threshold: float = 0.60) -> List[Dict]:
    """Remove near-duplicate notes by title similarity."""
    if len(items) <= 1:
        return items

    # Sort by engagement (higher first) so we keep the more popular version
    items.sort(key=lambda x: x["likes"] + x["comments"] * 2 + x["favorites"], reverse=True)

    trigram_cache = [_trigrams(item["title"]) for item in items]
    keep = [True] * len(items)

    for i in range(len(items)):
        if not keep[i]:
            continue
        for j in range(i + 1, len(items)):
            if not keep[j]:
                continue
            if _jaccard(trigram_cache[i], trigram_cache[j]) >= threshold:
                keep[j] = False  # Remove the lower-engagement duplicate

    return [item for item, k in zip(items, keep) if k]


# ---------------------------------------------------------------------------
# Relevance scoring (策略 8)
# ---------------------------------------------------------------------------
_STOP_WORDS = frozenset("的了在是我你他她它们这那有不也和与及或但如果虽然因为所以".replace("", " ").split() + list("的了在是"))


def _tokenize_cn(text: str) -> List[str]:
    """Simple Chinese tokenization: character bigrams + full words."""
    text = text.lower().strip()
    # Character bigrams for Chinese
    bigrams = [text[i:i + 2] for i in range(len(text) - 1)] if len(text) >= 2 else [text]
    # Filter stop words
    return [b for b in bigrams if b not in _STOP_WORDS and len(b.strip()) > 0]


def compute_relevance(title: str, snippet: str, query: str) -> float:
    """Compute relevance score between note and query. Returns 0.0-1.0."""
    query_tokens = set(_tokenize_cn(query))
    if not query_tokens:
        return 0.5

    # Title gets higher weight than snippet
    title_tokens = set(_tokenize_cn(title))
    snippet_tokens = set(_tokenize_cn(snippet[:200]))
    doc_tokens = title_tokens | snippet_tokens

    # Query coverage (how much of the query appears in the doc)
    coverage = len(query_tokens & doc_tokens) / len(query_tokens) if query_tokens else 0
    coverage_score = coverage ** 1.35  # Penalize incomplete matches

    # Precision (how focused is the match)
    precision = len(query_tokens & doc_tokens) / max(len(doc_tokens), 1) if doc_tokens else 0

    # Title bonus (matches in title are more valuable)
    title_coverage = len(query_tokens & title_tokens) / len(query_tokens) if query_tokens else 0
    title_bonus = 0.15 if title_coverage >= 0.5 else 0

    score = 0.60 * coverage_score + 0.25 * precision + title_bonus
    return min(1.0, max(0.05, round(score, 3)))


# ---------------------------------------------------------------------------
# Three-dimensional scoring (策略 2, 6, 7)
# ---------------------------------------------------------------------------
WEIGHT_RELEVANCE = 0.40
WEIGHT_RECENCY = 0.25
WEIGHT_ENGAGEMENT = 0.35

# XHS engagement weights (收藏 > 赞 > 评论, different from Reddit)
ENG_WEIGHT_FAVORITES = 0.40
ENG_WEIGHT_LIKES = 0.30
ENG_WEIGHT_COMMENTS = 0.30


def _recency_score(date_str: Optional[str], max_days: Optional[int] = None) -> float:
    """Linear recency decay. Returns 0-100."""
    if not date_str:
        return 30  # Unknown date gets moderate score (not 0, XHS dates can be missing)
    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        age_days = (datetime.now(timezone.utc) - dt).days
        if age_days < 0:
            age_days = 0
        window = max_days if max_days and max_days > 0 else 365  # Default 1 year window
        return max(0, min(100, 100 * (1 - age_days / window)))
    except (ValueError, TypeError):
        return 30


def _engagement_raw(likes: int, comments: int, favorites: int) -> float:
    """Compute raw engagement score using log1p compression."""
    return (
        ENG_WEIGHT_FAVORITES * math.log1p(favorites)
        + ENG_WEIGHT_LIKES * math.log1p(likes)
        + ENG_WEIGHT_COMMENTS * math.log1p(comments)
    )


def _normalize_to_100(values: List[float]) -> List[float]:
    """Min-max normalize to 0-100 range."""
    if not values:
        return []
    mn, mx = min(values), max(values)
    if mn == mx:
        return [50.0] * len(values)
    return [100 * (v - mn) / (mx - mn) for v in values]


def score_items(items: List[Dict], query: str, max_days: Optional[int] = None) -> List[Dict]:
    """Score and sort items using three-dimensional scoring."""
    if not items:
        return items

    # Compute raw scores
    for item in items:
        item["_rel"] = compute_relevance(item["title"], item["snippet"], query) * 100
        item["_rec"] = _recency_score(item.get("date"), max_days)
        item["_eng_raw"] = _engagement_raw(item["likes"], item["comments"], item["favorites"])

    # Normalize engagement to 0-100
    eng_raws = [item["_eng_raw"] for item in items]
    eng_norms = _normalize_to_100(eng_raws)

    for item, eng_norm in zip(items, eng_norms):
        item["_eng"] = eng_norm
        item["score"] = int(
            WEIGHT_RELEVANCE * item["_rel"]
            + WEIGHT_RECENCY * item["_rec"]
            + WEIGHT_ENGAGEMENT * item["_eng"]
        )
        item["score"] = max(0, min(100, item["score"]))

    # Sort: score desc, then engagement desc
    items.sort(key=lambda x: (x["score"], x["_eng_raw"]), reverse=True)

    return items


# ---------------------------------------------------------------------------
# Fetch post details + comments (策略 3)
# ---------------------------------------------------------------------------
def fetch_details(items: List[Dict], top: int = 20, depth: str = "deep") -> List[Dict]:
    """Fetch full content and comments for top N items."""
    comment_limit = DEPTH_CONFIG.get(depth, DEPTH_CONFIG["deep"])["comment_top"]
    to_fetch = items[:top]
    _log(f"Fetching details for top {len(to_fetch)} posts...")

    enriched = []
    for item in to_fetch:
        detail = _http_post_json(
            f"{MCP_BASE}/api/v1/feeds/detail",
            {"feed_id": item["feed_id"], "xsec_token": item["xsec_token"]},
            timeout=20, retries=2,
        )
        if not detail or not isinstance(detail, dict):
            item["content"] = ""
            item["top_comments"] = []
            enriched.append(item)
            continue

        note = detail.get("data", {}).get("data", {}).get("note", {})
        comments_data = detail.get("data", {}).get("data", {}).get("comments", {}).get("list", [])

        # Extract content
        item["content"] = str(note.get("desc", ""))[:800]
        item["author"] = note.get("user", {}).get("nickname", "")

        # Update engagement from detail (might be more accurate)
        interact = note.get("interactInfo", {})
        if interact:
            item["likes"] = _to_int(interact.get("likedCount")) or item["likes"]
            item["comments"] = _to_int(interact.get("commentCount")) or item["comments"]
            item["favorites"] = _to_int(interact.get("collectedCount")) or item["favorites"]

        # Extract top comments
        top_comments = []
        if isinstance(comments_data, list):
            for c in comments_data[:comment_limit]:
                if not isinstance(c, dict):
                    continue
                cmt = {
                    "user": c.get("userInfo", {}).get("nickname", "?"),
                    "content": str(c.get("content", ""))[:200],
                    "likes": _to_int(c.get("likeCount")),
                    "sub_comments": [],
                }
                # Sub-comments (replies)
                for sc in c.get("subComments", [])[:2]:
                    if isinstance(sc, dict):
                        cmt["sub_comments"].append({
                            "user": sc.get("userInfo", {}).get("nickname", "?"),
                            "content": str(sc.get("content", ""))[:200],
                            "likes": _to_int(sc.get("likeCount")),
                        })
                top_comments.append(cmt)

        item["top_comments"] = top_comments
        enriched.append(item)

        time.sleep(0.3)  # Be polite to the API

    _log(f"Fetched {len(enriched)} post details")
    return enriched


# ---------------------------------------------------------------------------
# Render output (策略 12)
# ---------------------------------------------------------------------------
def render_output(
    items: List[Dict],
    enriched: List[Dict],
    keywords: List[str],
    topic: str,
    query_type: str,
) -> str:
    """Render structured Markdown output for Claude to synthesize."""
    lines = []

    total_likes = sum(i["likes"] for i in items)
    total_favs = sum(i["favorites"] for i in items)
    total_cmts = sum(i["comments"] for i in items)

    lines.append(f"## 小红书调研: {topic}")
    lines.append(f"查询类型: {query_type}")
    lines.append(f"关键字: {', '.join(keywords)}")
    lines.append(f"搜索结果: {len(items)} 条笔记（去重后）│ {len(enriched)} 篇详情")
    lines.append("")

    # Enriched posts with full content + comments
    lines.append("### 详情笔记（含正文+评论）")
    lines.append("")

    for i, item in enumerate(enriched):
        lines.append(
            f'**XHS{i + 1}** (score:{item.get("score", 0)}) '
            f'{item.get("author", "?")} '
            f'[❤️{item["likes"]} 💬{item["comments"]} ⭐{item["favorites"]}]'
        )
        lines.append(f'  {item["title"]}')
        lines.append(f'  {item["url"]}')
        if item.get("content"):
            lines.append(f'  {item["content"][:500]}')

        if item.get("top_comments"):
            lines.append("  --- 热评 ---")
            for c in item["top_comments"]:
                lines.append(f'  [{c["likes"]}赞] {c["user"]}: {c["content"]}')
                for sc in c.get("sub_comments", []):
                    lines.append(f'    [{sc["likes"]}赞] {sc["user"]}: {sc["content"]}')

        lines.append("")

    # Remaining items (search results without detail)
    remaining = [it for it in items if it["feed_id"] not in {e["feed_id"] for e in enriched}]
    if remaining:
        lines.append("### 其他相关笔记")
        lines.append("")
        for i, item in enumerate(remaining[:30]):
            lines.append(
                f'**XHS{len(enriched) + i + 1}** (score:{item.get("score", 0)}) '
                f'[❤️{item["likes"]} 💬{item["comments"]} ⭐{item["favorites"]}]'
            )
            lines.append(f'  {item["title"]}')
            lines.append(f'  {item["url"]}')
            lines.append("")

    # Stats
    lines.append("---")
    top_post = max(items, key=lambda x: x["likes"]) if items else None
    top_authors = list(dict.fromkeys(e.get("author", "?") for e in enriched if e.get("author")))[:5]

    lines.append(
        f'📕 小红书: {len(items)} 条笔记（{len(keywords)}轮搜索）'
        f'│ {len(enriched)} 篇详情 '
        f'│ {total_likes} 赞 │ {total_favs} 收藏 │ {total_cmts} 评论'
    )
    if top_post:
        lines.append(f'🔥 最高互动: {top_post["title"][:40]}（❤️{top_post["likes"]}）')
    if top_authors:
        lines.append(f'🗣️ 主要作者: {", ".join(top_authors)}')
    lines.append("---")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="小红书调研引擎")
    parser.add_argument("topic", nargs="*", help="调研主题（fallback 模式）")
    parser.add_argument("--keywords", type=str, help="逗号分隔的关键字列表（LLM 生成，主路径）")
    depth_group = parser.add_mutually_exclusive_group()
    depth_group.add_argument("--quick", action="store_true", help="快速模式")
    depth_group.add_argument("--deep", action="store_true", help="深度模式（默认）")
    parser.add_argument("--days", type=int, default=None, help="时间范围（天数），默认不限")
    parser.add_argument("--top", type=int, default=None, help="获取详情的帖子数")
    parser.add_argument("--save-dir", type=str, default=None, help="保存报告目录")
    parser.add_argument("--json", action="store_true", help="JSON 输出")

    args = parser.parse_args()

    # Determine depth
    depth = "quick" if args.quick else "deep"
    config = DEPTH_CONFIG[depth]
    detail_top = args.top or config["detail_top"]

    # Determine keywords
    if args.keywords:
        keywords = [k.strip() for k in args.keywords.split(",") if k.strip()]
        topic = keywords[0] if keywords else ""
    elif args.topic:
        topic = " ".join(args.topic)
        keywords = expand_query_fallback(topic, depth)
    else:
        print("Error: provide topic or --keywords", file=sys.stderr)
        sys.exit(1)

    # Determine time filter
    publish_time = "不限"
    if args.days is not None:
        for max_d, pt in PUBLISH_TIME_MAP:
            if args.days <= max_d:
                publish_time = pt
                break
        else:
            publish_time = "不限"

    # Query type
    query_type = classify_query(topic)

    # Health check
    health = _http_get_json(f"{MCP_BASE}/health", timeout=3)
    if not health or not health.get("success"):
        print("Error: xiaohongshu-mcp not running. Run: python3 scripts/start.py", file=sys.stderr)
        sys.exit(1)

    login = _http_get_json(f"{MCP_BASE}/api/v1/login/status", timeout=8)
    if not login or not login.get("data", {}).get("is_logged_in"):
        print("Error: not logged in. Run: python3 scripts/login.py", file=sys.stderr)
        sys.exit(1)

    _log(f"Topic: {topic}")
    _log(f"Query type: {query_type}")
    _log(f"Keywords: {keywords}")
    _log(f"Depth: {depth}, publish_time: {publish_time}, detail_top: {detail_top}")

    # Step 1: Multi-round search
    items = search_multi(keywords, publish_time)
    _log(f"After dedup: {len(items)} unique notes")

    if not items:
        print("No results found.", file=sys.stderr)
        sys.exit(0)

    # Step 2: Score and sort
    items = score_items(items, topic, args.days)

    # Step 3: Fetch details for top items
    enriched = fetch_details(items, top=detail_top, depth=depth)

    # Step 4: Output
    if args.json:
        output = json.dumps({
            "topic": topic,
            "query_type": query_type,
            "keywords": keywords,
            "total_notes": len(items),
            "enriched_count": len(enriched),
            "items": items,
            "enriched": enriched,
        }, ensure_ascii=False, indent=2)
    else:
        output = render_output(items, enriched, keywords, topic, query_type)

    print(output)

    # Save to file
    if args.save_dir:
        os.makedirs(args.save_dir, exist_ok=True)
        slug = topic.replace(" ", "-")[:50]
        date_str = datetime.now().strftime("%Y%m%d")
        path = os.path.join(args.save_dir, f"{slug}-{date_str}-raw.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)
        _log(f"Saved to {path}")


if __name__ == "__main__":
    main()
