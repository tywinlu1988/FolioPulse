"""Tests for composite scorer."""
import pytest
from src.composite_scorer import (
    CompositeScorer,
    _normalize_linear, _normalize_inverse,
    _normalize_percentile_inverse, _normalize_target_range,
)


class TestNormalization:
    def test_percentile_inverse(self):
        assert _normalize_percentile_inverse(30) == 7.0
        assert _normalize_percentile_inverse(70) == 3.0

    def test_target_range_inside(self):
        assert _normalize_target_range(25, 1, 50) == 10.0

    def test_target_range_outside(self):
        score = _normalize_target_range(200, 1, 50)
        assert score < 10.0

    def test_linear_roe(self):
        thresholds = [(0, 5, 1), (5, 10, 3), (10, 15, 5), (15, 20, 7), (20, 25, 8.5), (25, 100, 10)]
        score = _normalize_linear(30.5, thresholds)
        assert score == 10.0

    def test_inverse_drawdown(self):
        thresholds = [(0, 5, 10), (5, 10, 9), (10, 15, 7)]
        score = _normalize_inverse(3, thresholds)
        assert score > 8.0


class TestCompositeScorer:
    def test_score_stock_returns_valid_range(self):
        scorer = CompositeScorer()
        products = [{"code": "600519", "type": "stock",
                     "pe_ttm_percentile_5y": 65, "pb_percentile_5y": 55,
                     "roe_ttm": 30.5, "revenue_cagr_3y": 15.2,
                     "price_return_6m": 8.5, "annualized_volatility_90d": 22,
                     "dividend_yield_ttm": 2.1}]
        result = scorer.score(products, None)
        assert 0 <= result[0]["composite_score"] <= 10

    def test_score_fund_returns_valid_range(self):
        scorer = CompositeScorer()
        products = [{"code": "110011", "type": "equity_fund",
                     "alpha_annualized_3y": 5.2, "beta_3y": 0.85,
                     "sharpe_ratio_3y": 1.35, "max_drawdown_3y": 22.5,
                     "aum_yuan": 28, "manager_tenure_years": 8.5,
                     "total_expense_ratio": 1.5}]
        result = scorer.score(products, None)
        assert 0 <= result[0]["composite_score"] <= 10

    def test_empty_products_returns_empty(self):
        scorer = CompositeScorer()
        assert scorer.score([], None) == []

    def test_missing_data_reduces_confidence(self):
        scorer = CompositeScorer()
        products = [{"code": "999999", "type": "equity_fund"}]
        result = scorer.score(products, None)
        assert result[0]["confidence"] < 50
