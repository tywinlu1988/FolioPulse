"""双轨验证 —— 推荐管道 Step 3.

轨 A（基本面）与轨 B（市场信号）交叉验证。
规则在运行时从 engine/dual-track-methodology.md 解析（R7 单一真相源）。
"""

from typing import Any, Dict, List, Optional
from src.adapters.base import BaseAdapter
from src.engine_loader import load_dual_track_config

_CONFIG = load_dual_track_config()
_TRACK_A = _CONFIG["track_a"]
_TRACK_B_SIGNALS = _CONFIG["track_b_signals"]


def _evaluate_track_b(signals: Dict[str, Optional[float]]) -> str:
    """聚合轨 B 信号，返回 positive / negative / neutral."""
    pos = 0
    neg = 0
    for sig_def in _TRACK_B_SIGNALS:
        value = signals.get(sig_def["id"])
        if value is None:
            continue
        if value >= sig_def["threshold_positive"]:
            pos += 1
        elif value <= sig_def["threshold_negative"]:
            neg += 1
    if pos == 0 and neg == 0:
        return "neutral"  # 数据不足
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"  # 分歧


def apply_dual_track(
    scored: List[Dict[str, Any]], adapter: Optional[BaseAdapter] = None
) -> List[Dict[str, Any]]:
    """对打分后的产品执行双轨交叉验证.

    冲突裁决（来自 engine/dual-track-methodology.md §冲突裁决）:
      双正 → +0.5（互证增强）
      A正B负 → 维持，标注"市场信号分歧"
      A负B正 → 维持，标注"市场信号先行"
      双负 → -0.5（互证削弱），列入关注名单
      任一轨 neutral → 维持，不标注
    """
    threshold = float(_TRACK_A["positive_threshold"])
    validated = []
    for product in scored:
        entry = dict(product)
        score = entry.get("composite_score", 0.0)

        track_a = "positive" if score >= threshold else "negative"

        track_b = "neutral"
        signal_ids = [s["id"] for s in _TRACK_B_SIGNALS]
        if adapter is not None:
            raw_signals = adapter.fetch_market_signal(entry.get("code", ""), signal_ids)
            track_b = _evaluate_track_b(raw_signals)

        note = None
        adjustment = 0.0
        if track_b != "neutral":
            if track_a == "positive" and track_b == "positive":
                adjustment = 0.5
                note = "互证增强"
            elif track_a == "positive" and track_b == "negative":
                note = "市场信号分歧"
            elif track_a == "negative" and track_b == "positive":
                note = "市场信号先行"
            else:
                adjustment = -0.5
                note = "互证削弱"
                entry["watchlist"] = True

        entry["track_a"] = track_a
        entry["track_b"] = track_b
        if note:
            entry["dual_track_note"] = note
        if adjustment:
            entry["composite_score"] = round(max(0.0, min(10.0, score + adjustment)), 2)
        validated.append(entry)

    return validated
