# 多因子打分框架

> 版本：v0.3.0 | 所有因子权重、归一化阈值、评分区间的唯一来源

## 股票因子

```yaml
stock_factors:
  - id: pe_percentile
    name: PE 分位数
    description: 当前 PE 在近 5 年的分位数，越低越便宜
    direction: inverse
    weight: 0.15
    normalization: percentile_inverse
    data_source: eastmoney
    data_point: pe_ttm_percentile_5y

  - id: pb_percentile
    name: PB 分位数
    description: 当前 PB 在近 5 年的分位数
    direction: inverse
    weight: 0.10
    normalization: percentile_inverse
    data_source: eastmoney
    data_point: pb_percentile_5y

  - id: roe
    name: ROE
    description: 净资产收益率，衡量盈利能力
    direction: direct
    weight: 0.20
    normalization: linear
    thresholds:
      - [0, 0, 0]
      - [0, 5, 1]
      - [5, 10, 3]
      - [10, 15, 5]
      - [15, 20, 7]
      - [20, 25, 8.5]
      - [25, 100, 10]
    data_source: eastmoney
    data_point: roe_ttm

  - id: revenue_growth
    name: 营收增速
    description: 近 3 年营收复合增长率
    direction: direct
    weight: 0.15
    normalization: linear
    thresholds:
      - [-100, -10, 0]
      - [-10, 0, 2]
      - [0, 5, 4]
      - [5, 10, 5]
      - [10, 20, 7]
      - [20, 30, 8.5]
      - [30, 500, 10]
    data_source: eastmoney
    data_point: revenue_cagr_3y

  - id: momentum_6m
    name: 6 个月动量
    description: 近 6 个月价格涨幅
    direction: direct
    weight: 0.15
    normalization: linear
    thresholds:
      - [-100, -30, 0]
      - [-30, -15, 2]
      - [-15, -5, 4]
      - [-5, 5, 5]
      - [5, 15, 6]
      - [15, 30, 8]
      - [30, 500, 10]
    data_source: eastmoney
    data_point: price_return_6m

  - id: volatility_90d
    name: 90 日波动率
    description: 近 90 个交易日年化波动率
    direction: inverse
    weight: 0.15
    normalization: percentile_inverse
    data_source: eastmoney
    data_point: annualized_volatility_90d

  - id: dividend_yield
    name: 股息率
    description: 近 12 个月股息率
    direction: direct
    weight: 0.10
    normalization: linear
    thresholds:
      - [0, 0.5, 0]
      - [0.5, 1, 2]
      - [1, 2, 4]
      - [2, 3, 6]
      - [3, 4, 8]
      - [4, 100, 10]
    data_source: eastmoney
    data_point: dividend_yield_ttm
```

## 基金因子

```yaml
fund_factors:
  - id: alpha
    name: Alpha
    description: 超越基准的年化超额收益
    direction: direct
    weight: 0.20
    normalization: linear
    thresholds:
      - [-100, -5, 0]
      - [-5, 0, 3]
      - [0, 3, 5]
      - [3, 5, 6]
      - [5, 10, 8]
      - [10, 100, 10]
    data_source: tiantian
    data_point: alpha_annualized_3y

  - id: beta
    name: Beta
    description: 系统性风险暴露，衡量与市场的联动性
    direction: target_range
    weight: 0.05
    normalization: target_range
    target_range: [0.5, 1.2]
    data_source: tiantian
    data_point: beta_3y

  - id: sharpe
    name: Sharpe 比率
    description: 风险调整后收益
    direction: direct
    weight: 0.25
    normalization: linear
    thresholds:
      - [-100, 0, 0]
      - [0, 0.5, 3]
      - [0.5, 1.0, 5]
      - [1.0, 1.5, 6]
      - [1.5, 2.0, 8]
      - [2.0, 100, 10]
    data_source: tiantian
    data_point: sharpe_ratio_3y

  - id: max_drawdown
    name: 最大回撤
    description: 近 3 年最大回撤幅度
    direction: inverse
    weight: 0.20
    normalization: linear_inverse
    thresholds:
      - [0, 5, 10]
      - [5, 10, 9]
      - [10, 15, 7]
      - [15, 20, 5]
      - [20, 25, 3]
      - [25, 100, 0]
    data_source: tiantian
    data_point: max_drawdown_3y

  - id: fund_size
    name: 基金规模
    description: 基金资产管理规模（亿元）
    direction: target_range
    weight: 0.10
    normalization: target_range
    target_range: [1, 50]
    data_source: tiantian
    data_point: aum_yuan

  - id: manager_stability
    name: 基金经理稳定性
    description: 现任基金经理任职年限
    direction: direct
    weight: 0.10
    normalization: linear
    thresholds:
      - [0, 1, 2]
      - [1, 2, 4]
      - [2, 3, 6]
      - [3, 5, 8]
      - [5, 100, 10]
    data_source: tiantian
    data_point: manager_tenure_years

  - id: expense_ratio
    name: 费率
    description: 年度管理费 + 托管费率
    direction: inverse
    weight: 0.10
    normalization: linear_inverse
    thresholds:
      - [0, 0.5, 10]
      - [0.5, 1.0, 8]
      - [1.0, 1.5, 6]
      - [1.5, 2.0, 4]
      - [2.0, 100, 2]
    data_source: tiantian
    data_point: total_expense_ratio
```

## ETF 因子

```yaml
etf_factors:
  - id: tracking_error
    name: 跟踪误差
    description: 近 1 年跟踪误差，越低越好
    direction: inverse
    weight: 0.30
    normalization: linear_inverse
    thresholds:
      - [0, 0.1, 10]
      - [0.1, 0.3, 8]
      - [0.3, 0.5, 6]
      - [0.5, 1.0, 4]
      - [1.0, 100, 2]
    data_source: eastmoney
    data_point: tracking_error_1y

  - id: liquidity
    name: 流动性
    description: 日均成交额
    direction: direct
    weight: 0.30
    normalization: linear
    thresholds:
      - [0, 100000, 2]
      - [100000, 500000, 4]
      - [500000, 1000000, 6]
      - [1000000, 5000000, 8]
      - [5000000, 100000000000, 10]
    data_source: eastmoney
    data_point: avg_daily_volume

  - id: expense_ratio
    name: 费率
    description: 年度管理费 + 托管费率
    direction: inverse
    weight: 0.20
    normalization: linear_inverse
    thresholds:
      - [0, 0.3, 10]
      - [0.3, 0.5, 8]
      - [0.5, 1.0, 5]
      - [1.0, 100, 3]
    data_source: eastmoney
    data_point: expense_ratio

  - id: fund_size
    name: 基金规模
    description: 基金资产管理规模（亿元）
    direction: target_range
    weight: 0.20
    normalization: target_range
    target_range: [1, 100]
    data_source: eastmoney
    data_point: aum_yuan
```

## 产品类型与因子集映射

```yaml
factor_mapping:
  stock: stock_factors
  equity_fund: fund_factors
  mixed_fund: fund_factors
  bond_fund: fund_factors
  index_fund: fund_factors
  qdii_fund: fund_factors
  etf: etf_factors
```

## 综合评分公式

```yaml
composite:
  formula: weighted_sum
  description: 综合评分 = Σ(因子归一化值 × 权重)，取值 0-10

score_bands:
  - range: [9.0, 10.0]
    label: 强烈推荐
    color: green
  - range: [8.0, 9.0]
    label: 推荐
    color: green
  - range: [7.0, 8.0]
    label: 可以考虑
    color: yellow
  - range: [5.0, 7.0]
    label: 中性
    color: yellow
  - range: [3.0, 5.0]
    label: 不推荐
    color: red
  - range: [0.0, 3.0]
    label: 强烈不推荐
    color: red
```

## 置信度规则

```yaml
confidence:
  density_thresholds:
    - threshold: 80
      label: 高置信度
      action: 正常输出
    - threshold: 50
      label: 中置信度
      action: 标注"中置信度"，不调整分数
    - threshold: 0
      label: 低置信度
      action: 评分标注"数据不足"，不参与排名

  critical_factor_floor: 20
  critical_factor_rule: 任一关键因子数据密度低于20%时，该因子评分输出 null
```
