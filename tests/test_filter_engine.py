"""Tests for filter engine."""
import pytest
from src.path_sheet import ProfileSheet, RiskLevel, Horizon
from src.filter_engine import (
    FilterEngine, FilterResult,
    filter_by_risk_level, filter_by_horizon, filter_by_amount,
)


class TestFilterByRiskLevel:
    def test_r3_client_can_receive_r3_product(self):
        assert filter_by_risk_level(RiskLevel.R3, RiskLevel.R3) == FilterResult.PASS

    def test_r3_client_blocked_from_r5_product(self):
        assert filter_by_risk_level(RiskLevel.R3, RiskLevel.R5) == FilterResult.REJECT

    def test_r3_client_warned_for_r4_product(self):
        assert filter_by_risk_level(RiskLevel.R3, RiskLevel.R4) == FilterResult.WARN


class TestFilterByHorizon:
    def test_medium_horizon_matches_medium_product(self):
        assert filter_by_horizon(Horizon.MEDIUM, 24) == FilterResult.PASS

    def test_short_horizon_rejects_long_lock(self):
        assert filter_by_horizon(Horizon.SHORT, 36) == FilterResult.REJECT


class TestFilterByAmount:
    def test_sufficient_amount_passes(self):
        assert filter_by_amount(500000, 100000) == FilterResult.PASS

    def test_insufficient_amount_rejects(self):
        assert filter_by_amount(50000, 100000) == FilterResult.REJECT


class TestFilterEngine:
    def test_empty_product_list_returns_empty(self):
        engine = FilterEngine()
        profile = _make_profile()
        passed, rejected = engine.apply_filters([], profile)
        assert passed == []
        assert rejected == []

    def test_product_matching_all_filters_passes(self):
        engine = FilterEngine()
        products = [{
            "code": "000001", "type": "equity_fund", "risk_level": "R3",
            "lock_period_months": 24, "min_amount": 1000,
        }]
        passed, rejected = engine.apply_filters(products, _make_profile())
        assert len(passed) == 1
        assert len(rejected) == 0

    def test_r5_product_rejected_for_r3_client(self):
        engine = FilterEngine()
        products = [{
            "code": "300750", "type": "stock", "risk_level": "R5",
            "lock_period_months": 0, "min_amount": 100,
        }]
        passed, rejected = engine.apply_filters(products, _make_profile())
        assert len(passed) == 0
        assert len(rejected) == 1


def _make_profile(**overrides):
    defaults = {
        "profile_id": "P-001", "risk_level": RiskLevel.R3,
        "amount": 500000, "horizon": Horizon.MEDIUM,
        "goal": "资产增值", "liquidity": "低",
        "investor_type": "普通投资者",
        "rm_name": "张经理", "client_name": "李客户",
    }
    defaults.update(overrides)
    return ProfileSheet(**defaults)
