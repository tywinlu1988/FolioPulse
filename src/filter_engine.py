"""规则过滤引擎 —— 推荐管道 Step 1."""

from enum import Enum
from typing import Any, Dict, List, Optional, Tuple
from src.path_sheet import ProfileSheet, RiskLevel, Horizon


class FilterResult(str, Enum):
    PASS = "pass"
    REJECT = "reject"
    WARN = "warn"


RISK_MATCH_MATRIX = {
    RiskLevel.R1: {
        "allowed": [RiskLevel.R1],
        "prohibited": [RiskLevel.R2, RiskLevel.R3, RiskLevel.R4, RiskLevel.R5],
        "with_warning": [],
    },
    RiskLevel.R2: {
        "allowed": [RiskLevel.R1, RiskLevel.R2],
        "prohibited": [RiskLevel.R3, RiskLevel.R4, RiskLevel.R5],
        "with_warning": [],
    },
    RiskLevel.R3: {
        "allowed": [RiskLevel.R1, RiskLevel.R2, RiskLevel.R3],
        "prohibited": [RiskLevel.R5],
        "with_warning": [RiskLevel.R4],
    },
    RiskLevel.R4: {
        "allowed": [RiskLevel.R1, RiskLevel.R2, RiskLevel.R3, RiskLevel.R4],
        "prohibited": [],
        "with_warning": [RiskLevel.R5],
    },
    RiskLevel.R5: {
        "allowed": [RiskLevel.R1, RiskLevel.R2, RiskLevel.R3, RiskLevel.R4, RiskLevel.R5],
        "prohibited": [],
        "with_warning": [],
    },
}

HORIZON_MAX_MONTHS = {
    Horizon.SHORT: 12,
    Horizon.MEDIUM: 36,
    Horizon.LONG: float("inf"),
}


def filter_by_risk_level(client_risk: RiskLevel, product_risk: RiskLevel) -> FilterResult:
    matrix = RISK_MATCH_MATRIX.get(client_risk)
    if matrix is None:
        return FilterResult.REJECT
    if product_risk in matrix["prohibited"]:
        return FilterResult.REJECT
    if product_risk in matrix["with_warning"]:
        return FilterResult.WARN
    if product_risk in matrix["allowed"]:
        return FilterResult.PASS
    return FilterResult.REJECT


def filter_by_horizon(client_horizon: Horizon, product_lock_months: int) -> FilterResult:
    max_months = HORIZON_MAX_MONTHS.get(client_horizon, 12)
    if product_lock_months <= max_months:
        return FilterResult.PASS
    return FilterResult.REJECT


def filter_by_amount(client_amount: float, product_min_amount: float) -> FilterResult:
    if product_min_amount <= 0:
        return FilterResult.PASS
    if client_amount >= product_min_amount:
        return FilterResult.PASS
    return FilterResult.REJECT


# 中英文产品类型映射（用于客户约束匹配）
TYPE_ALIAS = {
    "股票": "stock",
    "基金": "fund",
    "股票基金": "equity_fund",
    "混合基金": "mixed_fund",
    "债券基金": "bond_fund",
    "债券": "bond_fund",
    "指数基金": "index_fund",
    "指数": "index_fund",
    "etf": "etf",
    "reits": "reit",
    "reit": "reit",
    "可转债": "convertible_bond",
    "理财": "wealth_mgmt_product",
    "理财产品": "wealth_mgmt_product",
    "qdii": "qdii_fund",
}


def parse_product_risk_level(product: Dict[str, Any]) -> Optional[RiskLevel]:
    """从产品字典中提取风险等级。无法识别时返回 None（拒绝推荐）."""
    raw = product.get("risk_level", "")
    try:
        return RiskLevel(raw)
    except ValueError:
        return None


class FilterEngine:
    """规则过滤引擎."""

    def apply_filters(
        self, products: List[Dict[str, Any]], profile: ProfileSheet,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        passed = []
        rejected = []
        for product in products:
            result, reason = self._check_product(product, profile)
            if result == FilterResult.REJECT:
                rejected.append({**product, "reject_reason": reason})
            else:
                entry = dict(product)
                if result == FilterResult.WARN:
                    entry["warning"] = reason
                passed.append(entry)
        return passed, rejected

    def _check_product(
        self, product: Dict[str, Any], profile: ProfileSheet,
    ) -> Tuple[FilterResult, str]:
        product_risk = parse_product_risk_level(product)
        if product_risk is None:
            return FilterResult.REJECT, f"风险等级未知: {product.get('risk_level', '缺失')}"

        risk_result = filter_by_risk_level(profile.risk_level, product_risk)
        if risk_result == FilterResult.REJECT:
            return FilterResult.REJECT, (
                f"风险等级不匹配: 客户{profile.risk_level.value}, 产品{product_risk.value}"
            )

        lock_months = product.get("lock_period_months", 0)
        horizon_result = filter_by_horizon(profile.horizon, lock_months)
        if horizon_result == FilterResult.REJECT:
            return FilterResult.REJECT, f"期限不匹配: 锁定期{lock_months}月超过客户期限"

        min_amount = product.get("min_amount", 0)
        amount_result = filter_by_amount(profile.amount, min_amount)
        if amount_result == FilterResult.REJECT:
            return FilterResult.REJECT, f"起投金额不足: 需要{min_amount}, 客户{profile.amount}"

        constraint_result, constraint_reason = self._check_constraints(
            product, profile.constraints
        )
        if constraint_result == FilterResult.REJECT:
            return FilterResult.REJECT, constraint_reason

        if risk_result == FilterResult.WARN:
            return FilterResult.WARN, (
                f"风险等级跨级匹配: 客户{profile.risk_level.value}, 产品{product_risk.value}"
            )

        return FilterResult.PASS, ""

    def _check_constraints(
        self, product: Dict[str, Any], constraints: List[str],
    ) -> Tuple[FilterResult, str]:
        industry = product.get("industry", "")
        product_type = product.get("type", "").lower()
        for constraint in constraints:
            if constraint.startswith("不投") or constraint.startswith("禁投"):
                keyword = constraint[2:]
                if keyword in industry:
                    return FilterResult.REJECT, f"客户约束: {constraint}"
                # 中英文映射匹配产品类型
                alias = TYPE_ALIAS.get(keyword.lower(), keyword.lower())
                if alias in product_type or keyword.lower() in product_type:
                    return FilterResult.REJECT, f"客户约束: {constraint}"
                # 基金泛称匹配所有基金类型
                if alias == "fund" and "fund" in product_type:
                    return FilterResult.REJECT, f"客户约束: {constraint}"
        return FilterResult.PASS, ""
