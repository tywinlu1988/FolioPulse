# 规则过滤逻辑

> 版本：v0.1.0 | 推荐引擎 Step 1 过滤规则

## 过滤执行顺序

```yaml
filter_order:
  - id: FILTER_RISK_LEVEL
    name: 风险等级过滤
    priority: 1
    description: 按客户风险等级过滤产品类型

  - id: FILTER_HORIZON
    name: 投资期限过滤
    priority: 2
    description: 按客户投资期限过滤锁定期不匹配的产品

  - id: FILTER_AMOUNT
    name: 起投金额过滤
    priority: 3
    description: 过滤起投金额超出客户预算的产品

  - id: FILTER_BLACKLIST
    name: 禁售名单过滤
    priority: 4
    description: 过滤 ST/停牌/退市等禁售产品

  - id: FILTER_CONSTRAINT
    name: 客户自定义约束
    priority: 5
    description: 按客户指定的行业偏好/禁投行业等过滤

  - id: FILTER_INVESTOR_TYPE
    name: 投资者类型过滤
    priority: 6
    description: 按普通/合格投资者类型过滤产品准入
```

## 过滤规则详情

```yaml
rules:
  FILTER_RISK_LEVEL:
    type: hard
    logic: |
      读取客户风险等级 client_risk_level
      读取产品风险等级 product_risk_level
      查 suitability-rules.md §风险匹配矩阵
      如果 product_risk_level 在 prohibited 列表中 → 移除
      如果 product_risk_level 在 with_warning 列表中 → 保留但标记
      如果 product_risk_level 在 allowed 列表中 → 通过

  FILTER_HORIZON:
    type: hard
    logic: |
      读取客户投资期限 client_horizon
      读取产品锁定期或推荐持有期 product_lock_period
      如果 product_lock_period > client_horizon → 移除
      否则 → 通过

  FILTER_AMOUNT:
    type: soft
    logic: |
      读取客户投资金额 client_amount
      读取产品起投金额 product_min_amount
      如果 product_min_amount > client_amount → 移除
      否则 → 通过

  FILTER_BLACKLIST:
    type: hard
    logic: |
      读取产品状态
      如果产品在 suitability-rules.md §禁售/限售规则 中 → 移除
      否则 → 通过

  FILTER_CONSTRAINT:
    type: hard
    logic: |
      读取客户约束列表 client_constraints
      对每条约束，检查产品属性
      如果产品违反任一条约束 → 移除
      否则 → 通过

  FILTER_INVESTOR_TYPE:
    type: hard
    logic: |
      读取客户投资者类型
      读取产品准入门槛
      如果不满足 → 移除
      否则 → 通过
```

## 备选池规则

```yaml
candidate_pool:
  enabled: true
  max_size: 20
  selection: 被 FILTER_RISK_LEVEL 的 with_warning 规则过滤的产品
  sort_by: composite_score
  order: desc
```
