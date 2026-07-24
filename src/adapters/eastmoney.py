"""东方财富数据适配器.

v0.1.0 使用模拟数据，后续版本接入真实 API.
"""

from typing import Any, Dict, List
from src.adapters.base import BaseAdapter


class EastMoneyAdapter(BaseAdapter):
    """东方财富数据适配器（v0.1.0 模拟数据）."""

    NAME = "eastmoney"

    _MOCK_PRODUCTS = {
        "stock": [
            {"code": "600519", "name": "贵州茅台", "type": "stock",
             "industry": "白酒", "market_cap": 2200000000000,
             "pe": 28.5, "pb": 9.2, "roe": 30.5,
             "revenue_growth_3y": 15.2, "volatility_90d": 22.0,
             "dividend_yield": 2.1, "listing_date": "2001-08-27",
             "risk_level": "R4", "lock_period_months": 0, "min_amount": 100},
            {"code": "000858", "name": "五粮液", "type": "stock",
             "industry": "白酒", "market_cap": 780000000000,
             "pe": 22.3, "pb": 5.8, "roe": 25.3,
             "revenue_growth_3y": 12.5, "volatility_90d": 25.0,
             "dividend_yield": 2.8, "listing_date": "1998-04-27",
             "risk_level": "R4", "lock_period_months": 0, "min_amount": 100},
            {"code": "300750", "name": "宁德时代", "type": "stock",
             "industry": "新能源电池", "market_cap": 980000000000,
             "pe": 35.2, "pb": 7.5, "roe": 22.1,
             "revenue_growth_3y": 45.8, "volatility_90d": 35.0,
             "dividend_yield": 0.5, "listing_date": "2018-06-11",
             "risk_level": "R5", "lock_period_months": 0, "min_amount": 100},
        ],
        "equity_fund": [
            {"code": "110011", "name": "易方达中小盘混合", "type": "equity_fund",
             "fund_house": "易方达基金", "inception_date": "2008-06-19",
             "aum": 28000000000, "expense_ratio": 1.5,
             "manager_name": "张坤", "manager_tenure": 8.5, "benchmark": "沪深300",
             "risk_level": "R4", "lock_period_months": 0, "min_amount": 100},
            {"code": "161725", "name": "招商中证白酒指数", "type": "equity_fund",
             "fund_house": "招商基金", "inception_date": "2015-05-27",
             "aum": 52000000000, "expense_ratio": 1.0,
             "manager_name": "侯昊", "manager_tenure": 5.2, "benchmark": "中证白酒",
             "risk_level": "R4", "lock_period_months": 0, "min_amount": 100},
        ],
        "mixed_fund": [
            {"code": "002001", "name": "华夏回报混合A", "type": "mixed_fund",
             "fund_house": "华夏基金", "inception_date": "2003-09-05",
             "aum": 15000000000, "expense_ratio": 1.5,
             "manager_name": "蔡向阳", "manager_tenure": 6.0,
             "stock_ratio_range": "30-65%", "benchmark": "中债综合指数",
             "risk_level": "R3", "lock_period_months": 0, "min_amount": 100},
        ],
        "bond_fund": [
            {"code": "000014", "name": "华夏聚利债券", "type": "bond_fund",
             "fund_house": "华夏基金", "inception_date": "2013-03-19",
             "aum": 8000000000, "expense_ratio": 0.8,
             "manager_name": "刘明宇", "manager_tenure": 4.5,
             "duration_avg": 2.3, "credit_rating_dist": "AAA 80% AA+ 20%", "ytm": 3.8,
             "risk_level": "R2", "lock_period_months": 0, "min_amount": 100},
        ],
        "etf": [
            {"code": "510300", "name": "华泰柏瑞沪深300ETF", "type": "etf",
             "fund_house": "华泰柏瑞基金", "inception_date": "2012-05-04",
             "aum": 120000000000, "expense_ratio": 0.5,
             "tracking_index": "沪深300", "tracking_error_1y": 0.15,
             "avg_daily_volume": 2500000000,
             "risk_level": "R3", "lock_period_months": 0, "min_amount": 100},
        ],
    }

    _MOCK_FINANCIALS = {
        "600519": {"pe_ttm_percentile_5y": 65.0, "pb_percentile_5y": 55.0,
                   "roe_ttm": 30.5, "revenue_cagr_3y": 15.2,
                   "price_return_6m": 8.5, "annualized_volatility_90d": 22.0,
                   "dividend_yield_ttm": 2.1},
        "000858": {"pe_ttm_percentile_5y": 45.0, "pb_percentile_5y": 40.0,
                   "roe_ttm": 25.3, "revenue_cagr_3y": 12.5,
                   "price_return_6m": -3.2, "annualized_volatility_90d": 25.0,
                   "dividend_yield_ttm": 2.8},
        "300750": {"pe_ttm_percentile_5y": 30.0, "pb_percentile_5y": 35.0,
                   "roe_ttm": 22.1, "revenue_cagr_3y": 45.8,
                   "price_return_6m": -12.0, "annualized_volatility_90d": 35.0,
                   "dividend_yield_ttm": 0.5},
        "110011": {"alpha_annualized_3y": 5.2, "beta_3y": 0.85,
                   "sharpe_ratio_3y": 1.35, "max_drawdown_3y": 22.5,
                   "aum_yuan": 28.0, "manager_tenure_years": 8.5,
                   "total_expense_ratio": 1.5},
        "161725": {"alpha_annualized_3y": 3.8, "beta_3y": 1.05,
                   "sharpe_ratio_3y": 0.95, "max_drawdown_3y": 32.0,
                   "aum_yuan": 52.0, "manager_tenure_years": 5.2,
                   "total_expense_ratio": 1.0},
        "002001": {"alpha_annualized_3y": 3.5, "beta_3y": 0.55,
                   "sharpe_ratio_3y": 1.55, "max_drawdown_3y": 12.0,
                   "aum_yuan": 15.0, "manager_tenure_years": 6.0,
                   "total_expense_ratio": 1.5},
        "000014": {"ytm": 3.8, "duration": 2.3, "credit_quality": "AAA主导",
                   "sharpe_ratio_3y": 1.1, "max_drawdown_3y": 1.8,
                   "aum_yuan": 8.0, "total_expense_ratio": 0.8},
        "510300": {"tracking_error_1y": 0.15, "avg_daily_volume": 2500000000,
                   "expense_ratio": 0.5, "aum_yuan": 120.0,
                   "tracking_index": "沪深300"},
    }

    _MOCK_SIGNALS = {
        "600519": {"fund_flow_5d": 250000000, "institution_change": 3.2,
                   "sentiment_score": 0.35},
        "000858": {"fund_flow_5d": -80000000, "institution_change": -2.1,
                   "sentiment_score": 0.05},
        "300750": {"fund_flow_5d": 500000000, "institution_change": 8.5,
                   "sentiment_score": 0.55},
    }

    def fetch_product_list(self, product_type: str) -> List[Dict[str, Any]]:
        products = self._MOCK_PRODUCTS.get(product_type, [])
        return [dict(p) for p in products]

    def fetch_product_detail(self, product_code: str) -> Dict[str, Any]:
        for products in self._MOCK_PRODUCTS.values():
            for p in products:
                if p["code"] == product_code:
                    return dict(p)
        return {}

    def fetch_financial_data(
        self, product_code: str, data_points: List[str]
    ) -> Dict[str, float]:
        """返回请求的数据点。缺失的数据点返回 None（而非 0.0）."""
        all_data = self._MOCK_FINANCIALS.get(product_code, {})
        return {dp: all_data.get(dp) for dp in data_points}

    def fetch_market_signal(
        self, product_code: str, signal_ids: List[str]
    ) -> Dict[str, float]:
        all_signals = self._MOCK_SIGNALS.get(product_code, {})
        return {sid: all_signals.get(sid, 0.0) for sid in signal_ids}

    def check_health(self) -> bool:
        return True
