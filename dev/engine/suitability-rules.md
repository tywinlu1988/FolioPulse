# 适当性管理规则

> 版本：v0.1.0 | 基于中国证监会《证券期货投资者适当性管理办法》和银保监会理财销售适当性规则

## 风险匹配矩阵

```yaml
risk_match_matrix:
  R1:
    allowed: [R1]
    prohibited: [R2, R3, R4, R5]
    with_warning: []
  R2:
    allowed: [R1, R2]
    prohibited: [R3, R4, R5]
    with_warning: []
  R3:
    allowed: [R1, R2, R3]
    prohibited: [R4, R5]
    with_warning: [R4]
  R4:
    allowed: [R1, R2, R3, R4]
    prohibited: [R5]
    with_warning: [R5]
  R5:
    allowed: [R1, R2, R3, R4, R5]
    prohibited: []
    with_warning: []

product_risk_to_investor_min:
  R1产品: R1
  R2产品: R2
  R3产品: R3
  R4产品: R4
  R5产品: R5
```

## 投资者类型分类

```yaml
investor_types:
  ordinary:
    name: 普通投资者
    max_leverage: 0
    product_restrictions:
      - 不得参与融资融券
      - 不得参与科创板（未满2年经验）
    applicable_risk_range: [R1, R2, R3]

  qualified:
    name: 合格投资者
    min_assets: 5000000
    min_income: 500000
    product_restrictions: []
    applicable_risk_range: [R1, R2, R3, R4, R5]
```

## 适当性校验门禁

```yaml
gates:
  - id: GATE_RISK_MATCH
    name: 风险等级匹配
    rule: 推荐产品的风险等级不得超过客户风险承受等级 + 1 级
    fail_action: 降级为"with_warning"，标注"不匹配"

  - id: GATE_PRODUCT_TYPE
    name: 产品类型准入
    rule: 客户投资者类型须满足产品类型的准入门槛
    fail_action: 移除推荐

  - id: GATE_CONSTRAINT
    name: 客户约束匹配
    rule: 推荐产品不得违反客户指定的行业偏好/禁投行业等约束
    fail_action: 移除推荐

  - id: GATE_AMOUNT_MIN
    name: 起投金额
    rule: 客户投资金额须满足产品起投金额要求
    fail_action: 标注"起投金额不足"

  - id: GATE_HORIZON_MATCH
    name: 期限匹配
    rule: 产品锁定期不得超过客户投资期限
    fail_action: 标注"期限不匹配"
```

## 禁售/限售规则

```yaml
restricted_products:
  default: []
  rules:
    - id: BLACKLIST_ST
      description: ST 和 *ST 股票
      scope: [stock]
      action: 禁止推荐
    - id: BLACKLIST_SUSPENDED
      description: 停牌股票
      scope: [stock]
      action: 禁止推荐
    - id: BLACKLIST_DELISTING
      description: 退市整理期股票
      scope: [stock]
      action: 禁止推荐
    - id: RESTRICT_PENNY_STOCK
      description: 股价低于 2 元的股票
      scope: [stock]
      action: 标注"低价股风险"
```

## 合规话术要求

```yaml
disclaimer_required:
  - 历史业绩不代表未来表现
  - 投资有风险，入市需谨慎
  - 本推荐不构成投资建议

prohibited_language:
  - 保本
  - 稳赚
  - 无风险
  - 绝对收益
  - 保证收益
  - 包赚不赔
```
