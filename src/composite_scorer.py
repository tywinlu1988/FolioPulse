"""多因子综合打分引擎 —— 推荐管道 Step 2.

因子定义与产品映射在运行时从 engine/scoring-framework.md 解析（R7 单一真相源），
不在代码中硬编码。
"""

from typing import Any, Dict, List, Optional
from src.adapters.base import BaseAdapter
from src.engine_loader import load_factor_sets, load_factor_mapping, load_confidence_rules


# 运行时从引擎文档加载（单一真相源：engine/scoring-framework.md）
_FACTOR_SETS = load_factor_sets()
_FACTOR_MAPPING = load_factor_mapping()
_CONFIDENCE_RULES = load_confidence_rules()

STOCK_FACTORS = _FACTOR_SETS["stock_factors"]
FUND_FACTORS = _FACTOR_SETS["fund_factors"]
ETF_FACTORS = _FACTOR_SETS["etf_factors"]

PRODUCT_FACTOR_MAP = {
    ptype: _FACTOR_SETS[set_name]
    for ptype, set_name in _FACTOR_MAPPING.items()
}


def _normalize_threshold(value: float, thresholds: List[tuple]) -> float:
    """统一阈值归一化：区间内线性插值，越界 clamp 到最近区间端点.

    thresholds 格式: [(lo, hi, score_at_lo)]
    区间 hi 端点的分数 = 下一区间的 score_at_lo（最后一区间为自身分数）.
    score 可为升序（direct 指标）或降序（inverse 指标），逻辑通用.
    """
    if not thresholds:
        return 5.0
    first_lo, first_score = thresholds[0][0], float(thresholds[0][2])
    if value <= first_lo:
        return round(first_score, 2)
    for i, (lo, hi, score_lo) in enumerate(thresholds):
        if hi is not None and value <= hi:
            s_lo = float(score_lo)
            s_hi = float(thresholds[i + 1][2]) if i + 1 < len(thresholds) else s_lo
            frac = (value - lo) / (hi - lo) if hi != lo else 0.5
            return round(s_lo + frac * (s_hi - s_lo), 2)
    # 超过最后一个区间上界：clamp 到末端分数
    return round(float(thresholds[-1][2]), 2)


def _normalize_linear(value: float, thresholds: List[tuple]) -> float:
    """正向线性归一化（高值 → 高分）."""
    return _normalize_threshold(value, thresholds)


def _normalize_inverse(value: float, thresholds: List[tuple]) -> float:
    """反向归一化（低值 → 高分）.

    阈值中的 score 已为降序（如最大回撤），直接复用统一插值逻辑.
    """
    return _normalize_threshold(value, thresholds)


def _normalize_percentile_inverse(value: float) -> float:
    """分位数反向归一化: (100 - 分位数) / 10."""
    return round((100.0 - value) / 10.0, 2)


def _normalize_target_range(value: float, lo: float, hi: float) -> float:
    """目标范围归一化: 范围内满分，越远越低."""
    if lo <= value <= hi:
        return 10.0
    distance = min(abs(value - lo), abs(value - hi))
    return round(max(0.0, 10.0 - distance / max(lo, 1) * 5), 2)


def _normalize_factor(factor_def: Dict, raw_value: Optional[float]) -> Optional[float]:
    """按因子定义归一化."""
    if raw_value is None:
        return None
    method = factor_def.get("normalization", "linear")
    if method == "percentile_inverse":
        return _normalize_percentile_inverse(raw_value)
    elif method == "target_range":
        tr = factor_def.get("target_range", [0, 100])
        return _normalize_target_range(raw_value, tr[0], tr[1])
    elif method == "linear":
        thresholds = factor_def.get("thresholds", [(0, 100, 10)])
        return _normalize_linear(raw_value, thresholds)
    elif method == "linear_inverse":
        thresholds = factor_def.get("thresholds", [(0, 100, 10)])
        return _normalize_inverse(raw_value, thresholds)
    return float(raw_value)


class CompositeScorer:
    """多因子综合打分引擎."""

    @staticmethod
    def confidence_label(density_pct: float) -> str:
        """按引擎文档置信度规则返回标签（高/中/低）."""
        thresholds = _CONFIDENCE_RULES.get("density_thresholds", [])
        for t in thresholds:
            if density_pct >= t["threshold"]:
                return t["label"].replace("置信度", "")
        return "低"

    def score(
        self, products: List[Dict[str, Any]], profile: Any, adapter: Optional[BaseAdapter] = None
    ) -> List[Dict[str, Any]]:
        """对产品列表打分，返回附加评分信息的产品列表."""
        scored = []
        for product in products:
            ptype = product.get("type", "equity_fund")
            factors = PRODUCT_FACTOR_MAP.get(ptype, FUND_FACTORS)
            factor_scores = {}
            total_weight = 0.0
            weighted_sum = 0.0
            data_points_count = 0
            data_points_total = len(factors)

            for factor in factors:
                raw = self._get_raw_value(product, factor, adapter)
                normalized = _normalize_factor(factor, raw)
                if normalized is not None:
                    weight = factor["weight"]
                    factor_scores[factor["id"]] = {
                        "name": factor["id"], "raw": raw, "normalized": normalized,
                        "weight": weight, "weighted": round(normalized * weight, 2),
                    }
                    weighted_sum += normalized * weight
                    total_weight += weight
                    data_points_count += 1
                else:
                    factor_scores[factor["id"]] = {
                        "name": factor["id"], "raw": None, "normalized": None,
                        "weight": factor["weight"], "weighted": None,
                    }
                    total_weight += factor["weight"]

            composite_score = (
                round(weighted_sum / total_weight, 2)
                if total_weight > 0 else 0.0
            )

            confidence = (data_points_count / data_points_total * 100) if data_points_total > 0 else 0

            entry = dict(product)
            entry["composite_score"] = composite_score
            entry["confidence"] = round(confidence, 1)
            entry["confidence_label"] = self.confidence_label(confidence)
            if confidence < 50:
                entry["data_note"] = "数据不足"
            entry["factor_scores"] = factor_scores
            scored.append(entry)

        return scored

    def _get_raw_value(
        self, product: Dict[str, Any], factor: Dict, adapter: Optional[BaseAdapter]
    ) -> Optional[float]:
        """获取因子原始值。无数据返回 None（不以 0.0 作为缺失哨兵）."""
        data_point = factor.get("data_point", "")
        # First try product dict directly
        if data_point in product and product[data_point] is not None:
            try:
                return float(product[data_point])
            except (TypeError, ValueError):
                return None
        # Then try adapter
        if adapter:
            code = product.get("code", "")
            data = adapter.fetch_financial_data(code, [data_point])
            value = data.get(data_point)
            if value is not None:
                try:
                    return float(value)
                except (TypeError, ValueError):
                    return None
        return None
