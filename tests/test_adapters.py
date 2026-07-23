"""Tests for data adapters."""
import pytest
from src.adapters.base import BaseAdapter, AdapterError
from src.adapters.eastmoney import EastMoneyAdapter


class TestEastMoneyAdapter:
    """Tests for EastMoney adapter."""

    def test_is_base_adapter(self):
        assert isinstance(EastMoneyAdapter(), BaseAdapter)

    def test_check_health_returns_bool(self):
        assert EastMoneyAdapter().check_health() is True

    def test_fetch_product_list_returns_list(self):
        products = EastMoneyAdapter().fetch_product_list("stock")
        assert isinstance(products, list)
        assert len(products) > 0

    def test_fetch_product_list_unknown_type_returns_empty(self):
        assert EastMoneyAdapter().fetch_product_list("unknown") == []

    def test_fetch_financial_data_returns_dict(self):
        data = EastMoneyAdapter().fetch_financial_data("600519", ["roe_ttm"])
        assert isinstance(data, dict)
        assert "roe_ttm" in data

    def test_fetch_market_signal_returns_dict(self):
        signals = EastMoneyAdapter().fetch_market_signal("600519", ["fund_flow_5d"])
        assert isinstance(signals, dict)
        assert "fund_flow_5d" in signals

    def test_fetch_product_detail_returns_dict(self):
        detail = EastMoneyAdapter().fetch_product_detail("600519")
        assert detail["code"] == "600519"
        assert detail["name"] == "贵州茅台"

    def test_fetch_product_detail_unknown_returns_empty(self):
        assert EastMoneyAdapter().fetch_product_detail("999999") == {}


class TestBaseAdapter:
    """Tests for abstract adapter interface."""

    def test_cannot_instantiate(self):
        with pytest.raises(TypeError):
            BaseAdapter()
