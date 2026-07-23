"""多因子综合打分引擎 —— 推荐管道 Step 2."""

from typing import Any, Dict, List, Optional
from src.adapters.base import BaseAdapter


# ── 因子定义（来自 dev/engine/scoring-framework.md）─

STOCK_FACTORS = [
    {"id": "pe_percentile", "weight": 0.15, "direction": "inverse",
     "normalization": "percentile_inverse", "data_point": "pe_ttm_percentile_5y"},
    {"id": "pb_percentile", "weight": 0.10, "direction": "inverse",
     "normalization": "percentile_inverse", "data_point": "pb_percentile_5y"},
    {"id": "roe", "weight": 0.20, "direction": "direct",
     "normalization": "linear", "data_point": "roe_ttm",
     "thresholds": [(0, 0, 0), (0, 5, 1), (5, 10, 3), (10, 15, 5),
                    (15, 20, 7), (20, 25, 8.5), (25, 100, 10)]},
    {"id": "revenue_growth", "weight": 0.15, "direction": "direct",
     "normalization": "linear", "data_point": "revenue_cagr_3y",
     "thresholds": [(-100, -10, 0), (-10, 0, 2), (0, 5, 4), (5, 10, 5),
                    (10, 20, 7), (20, 30, 8.5), (30, 500, 10)]},
    {"id": "momentum_6m", "weight": 0.15, "direction": "direct",
     "normalization": "linear", "data_point": "price_return_6m",
     "thresholds": [(-100, -30, 0), (-30, -15, 2), (-15, -5, 4), (-5, 5, 5),
                    (5, 15, 6), (15, 30, 8), (30, 500, 10)]},
    {"id": "volatility_90d", "weight": 0.15, "direction": "inverse",
     "normalization": "percentile_inverse", "data_point": "annualized_volatility_90d"},
    {"id": "dividend_yield", "weight": 0.10, "direction": "direct",
     "normalization": "linear", "data_point": "dividend_yield_ttm",
     "thresholds": [(0, 0.5, 0), (0.5, 1, 2), (1, 2, 4), (2, 3, 6),
                    (3, 4, 8), (4, 100, 10)]},
]

FUND_FACTORS = [
    {"id": "alpha", "weight": 0.20, "direction": "direct",
     "normalization": "linear", "data_point": "alpha_annualized_3y",
     "thresholds": [(-100, -5, 0), (-5, 0, 3), (0, 3, 5), (3, 5, 6),
                    (5, 10, 8), (10, 100, 10)]},
    {"id": "beta", "weight": 0.05, "direction": "target_range",
     "normalization": "target_range", "data_point": "beta_3y",
     "target_range": [0.5, 1.2]},
    {"id": "sharpe", "weight": 0.25, "direction": "direct",
     "normalization": "linear", "data_point": "sharpe_ratio_3y",
     "thresholds": [(-100, 0, 0), (0, 0.5, 3), (0.5, 1.0, 5), (1.0, 1.5, 6),
                    (1.5, 2.0, 8), (2.0, 100, 10)]},
    {"id": "max_drawdown", "weight": 0.20, "direction": "inverse",
     "normalization": "linear_inverse", "data_point": "max_drawdown_3y",
     "thresholds": [(0, 5, 10), (5, 10, 9), (10, 15, 7), (15, 20, 5),
                    (20, 25, 3), (25, 100, 0)]},
    {"id": "fund_size", "weight": 0.10, "direction": "target_range",
     "normalization": "target_range", "data_point": "aum_yuan",
     "target_range": [1, 50]},
    {"id": "manager_stability", "weight": 0.10, "direction": "direct",
     "normalization": "linear", "data_point": "manager_tenure_years",
     "thresholds": [(0, 1, 2), (1, 2, 4), (2, 3, 6), (3, 5, 8), (5, 100, 10)]},
    {"id": "expense_ratio", "weight": 0.10, "direction": "inverse",
     "normalization": "linear_inverse", "data_point": "total_expense_ratio",
     "thresholds": [(0, 0.5, 10), (0.5, 1.0, 8), (1.0, 1.5, 6),
                    (1.5, 2.0, 4), (2.0, 100, 2)]},
]

PRODUCT_FACTOR_MAP = {
    "stock": STOCK_FACTORS,
    "equity_fund": FUND_FACTORS,
    "mixed_fund": FUND_FACTORS,
    "bond_fund": FUND_FACTORS,
    "index_fund": FUND_FACTORS,
    "qdii_fund": FUND_FACTORS,
    "etf": [
        {"id": "tracking_error", "weight": 0.30, "direction": "inverse",
         "normalization": "linear_inverse", "data_point": "tracking_error_1y",
         "thresholds": [(0, 0.1, 10), (0.1, 0.3, 8), (0.3, 0.5, 6),
                        (0.5, 1.0, 4), (1.0, 100, 2)]},
        {"id": "liquidity", "weight": 0.30, "direction": "direct",
         "normalization": "linear", "data_point": "avg_daily_volume",
         "thresholds": [(0, 100000, 2), (100000, 500000, 4),
                        (500000, 1000000, 6), (1000000, 5000000, 8),
                        (5000000, 100000000000, 10)]},
        {"id": "expense_ratio", "weight": 0.20, "direction": "inverse",
         "normalization": "linear_inverse", "data_point": "expense_ratio",
         "thresholds": [(0, 0.3, 10), (0.3, 0.5, 8), (0.5, 1.0, 5),
                        (1.0, 100, 3)]},
        {"id": "fund_size", "weight": 0.20, "direction": "target_range",
         "normalization": "target_range", "data_point": "aum_yuan",
         "target_range": [1, 100]},
    ],
}


def _normalize_linear(value: float, thresholds: List[tuple]) -> float:
    """线性归一化到 0-10."""
    for lo, hi, score_lo in thresholds:
        if hi is None:
            if value >= lo:
                return float(score_lo)
            break
        if lo <= value <= hi:
            frac = (value - lo) / (hi - lo) if hi != lo else 0.5
            # find score_hi
            for lo2, hi2, score_hi in thresholds:
                if lo2 == lo and hi2 == hi:
                    continue
            # simple: use the next band's score_lo as target
            next_score = 10.0
            for lo2, hi2, s2 in thresholds:
                if lo2 > lo:
                    next_score = float(s2)
                    break
            return round(float(score_lo) + frac * (next_score - float(score_lo)), 2)
    return 5.0


def _normalize_inverse(value: float, thresholds: List[tuple]) -> float:
    """反向线性归一化：低值→高分，高值→低分.

    在 thresholds 区间内做反向线性插值。
    thresholds 格式: [(lo, hi, score_at_lo)]
    score_at_lo 是 lo 端点的分数，hi 端点的分数为下一区间的 score_at_lo。
    """
    for i, (lo, hi, score_lo) in enumerate(thresholds):
        if lo <= value <= hi:
            # 找到 hi 端点的分数
            if i + 1 < len(thresholds):
                score_hi = thresholds[i + 1][2]
            else:
                score_hi = 0.0  # 最后一个区间 hi → 0
            frac = (value - lo) / (hi - lo) if hi != lo else 0.5
            return round(score_lo - frac * (score_lo - score_hi), 2)
    return 5.0


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
            entry["factor_scores"] = factor_scores
            scored.append(entry)

        return scored

    def _get_raw_value(
        self, product: Dict[str, Any], factor: Dict, adapter: Optional[BaseAdapter]
    ) -> Optional[float]:
        """获取因子原始值."""
        data_point = factor.get("data_point", "")
        # First try product dict directly
        if data_point in product:
            return float(product[data_point])
        # Then try adapter
        if adapter:
            code = product.get("code", "")
            data = adapter.fetch_financial_data(code, [data_point])
            if data_point in data and data[data_point] != 0.0:
                return float(data[data_point])
        return None
