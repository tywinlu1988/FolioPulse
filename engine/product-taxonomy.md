# 产品分类体系

> 版本：v0.1.0 | 所有产品类型的唯一来源

## 一级分类

```yaml
product_types:
  - id: stock
    name: A股股票
    risk_range: [R3, R5]
    applicable_factors: [pe_percentile, pb_percentile, roe, revenue_growth, momentum_6m, volatility_90d, dividend_yield]
    fields: [code, name, industry, market_cap, pe, pb, roe, revenue_growth_3y, volatility_90d, dividend_yield, listing_date]

  - id: equity_fund
    name: 股票型基金
    risk_range: [R3, R5]
    applicable_factors: [alpha, beta, sharpe, max_drawdown, fund_size, manager_stability, expense_ratio]
    fields: [code, name, fund_house, inception_date, aum, expense_ratio, manager_name, manager_tenure, benchmark]

  - id: mixed_fund
    name: 混合型基金
    risk_range: [R2, R4]
    applicable_factors: [alpha, beta, sharpe, max_drawdown, fund_size, manager_stability, expense_ratio]
    fields: [code, name, fund_house, inception_date, aum, expense_ratio, manager_name, manager_tenure, stock_ratio_range, benchmark]

  - id: bond_fund
    name: 债券型基金
    risk_range: [R1, R3]
    applicable_factors: [alpha, beta, sharpe, max_drawdown, fund_size, manager_stability, expense_ratio]
    fields: [code, name, fund_house, inception_date, aum, expense_ratio, manager_name, duration_avg, credit_rating_dist, ytm]

  - id: index_fund
    name: 指数型基金
    risk_range: [R2, R5]
    applicable_factors: [alpha, beta, sharpe, max_drawdown, fund_size, manager_stability, expense_ratio]
    fields: [code, name, fund_house, inception_date, aum, expense_ratio, tracking_index, tracking_error_1y]

  - id: qdii_fund
    name: QDII基金
    risk_range: [R3, R5]
    applicable_factors: [alpha, beta, sharpe, max_drawdown, fund_size, manager_stability, expense_ratio]
    fields: [code, name, fund_house, inception_date, aum, expense_ratio, target_market, currency, fx_hedged]

  - id: etf
    name: ETF
    risk_range: [R2, R5]
    applicable_factors: [tracking_error, liquidity, expense_ratio, fund_size]
    fields: [code, name, fund_house, inception_date, aum, expense_ratio, tracking_index, tracking_error_1y, avg_daily_volume]

  - id: reit
    name: REITs
    risk_range: [R3, R5]
    applicable_factors: [dividend_yield, nav_discount, property_type_diversification, leverage_ratio, occupancy_rate]
    fields: [code, name, property_type, market_cap, dividend_yield, nav_per_share, leverage_ratio, occupancy_rate]

  - id: convertible_bond
    name: 可转债
    risk_range: [R2, R4]
    applicable_factors: [conversion_premium, ytm, underlying_volatility, credit_rating, put_price_protection]
    fields: [code, name, underlying_stock, conversion_price, maturity_date, ytm, credit_rating, issue_size]

  - id: wealth_mgmt_product
    name: 银行理财产品
    risk_range: [R1, R3]
    applicable_factors: [expected_return, risk_level, issuer_rating, history_fulfillment_rate, lock_period]
    fields: [code, name, issuer, risk_level, expected_return_low, expected_return_high, min_amount, lock_period_days, history_fulfillment_rate]
```

## 风险等级定义

```yaml
risk_levels:
  R1:
    name: 保守型
    description: 保本为主，接受极低波动
    max_drawdown_tolerance: -2%
    suitable_horizon: [短期]
  R2:
    name: 稳健型
    description: 适度增值，接受小额波动
    max_drawdown_tolerance: -5%
    suitable_horizon: [短期, 中期]
  R3:
    name: 平衡型
    description: 追求中等回报，接受中等波动
    max_drawdown_tolerance: -15%
    suitable_horizon: [中期, 长期]
  R4:
    name: 进取型
    description: 追求较高回报，接受较大波动
    max_drawdown_tolerance: -25%
    suitable_horizon: [中期, 长期]
  R5:
    name: 激进型
    description: 追求最高回报，接受大幅波动
    max_drawdown_tolerance: -50%
    suitable_horizon: [长期]
```

## 投资期限定义

```yaml
horizons:
  short:
    name: 短期
    max_months: 12
    suitable_for: [R1, R2]
  medium:
    name: 中期
    min_months: 12
    max_months: 36
    suitable_for: [R2, R3, R4]
  long:
    name: 长期
    min_months: 36
    suitable_for: [R3, R4, R5]
```
