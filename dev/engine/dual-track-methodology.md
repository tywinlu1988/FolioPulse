# 双轨验证方法

> 版本：v0.1.0 | 基本面 + 市场信号交叉验证

## 双轨定义

```yaml
tracks:
  track_a:
    name: 基本面分析
    description: 基于财务数据、行业地位、治理评估的审慎分析
    priority: primary
    data_source: [eastmoney, tiantian]

  track_b:
    name: 市场信号
    description: 基于资金流向、机构持仓变化、舆情情绪的市场感知
    priority: secondary
    data_source: [eastmoney]
```

## 冲突裁决

```yaml
conflict_rules:
  rules:
    -
      track_a: positive
      track_b: positive
      result: 互证增强
      action: 评分上调 0.5
    -
      track_a: positive
      track_b: negative
      result: 轨 A 优先
      action: 维持原评分，标注"市场信号分歧"
    -
      track_a: negative
      track_b: positive
      result: 轨 A 优先
      action: 维持原评分，标注"市场信号先行"
    -
      track_a: negative
      track_b: negative
      result: 互证削弱
      action: 评分下调 0.5，列入关注名单
  default_rule: 轨 A（基本面）优先于轨 B（市场信号）
```

## 轨 B 信号

```yaml
track_b_signals:
  - id: fund_flow_5d
    name: 近 5 日主力资金净流入
    direction: direct
    threshold_positive: 10000000
    threshold_negative: -10000000
    data_source: eastmoney

  - id: institution_change
    name: 机构持仓变化
    direction: direct
    threshold_positive: 5
    threshold_negative: -5
    data_source: eastmoney

  - id: sentiment_score
    name: 舆情情绪得分
    direction: direct
    threshold_positive: 0.3
    threshold_negative: -0.3
    data_source: eastmoney
```
