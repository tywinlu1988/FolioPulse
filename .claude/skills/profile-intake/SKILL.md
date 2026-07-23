---
name: profile-intake
description: >
  FolioPulse 客户画像摄入技能。当客户经理需要为理财客户生成投资推荐时，
  通过 4 问路由协议采集客户画像，生成结构化的 Profile Sheet (YAML)。
  触发场景：客户经理描述客户情况、提供客户风险等级和投资需求时。
---

## 用途

将客户经理的自然语言描述转换为结构化的客户画像表（Profile Sheet YAML），
作为后续推荐引擎的输入。

## 调用协议

客户经理描述客户情况后，按 4 问协议逐一采集：

| 问序 | 问题 | 选项 |
|------|------|------|
| Q1 | 客户的投资目标是什么？ | 资产增值 / 稳健收益 / 养老规划 / 子女教育 / 流动性管理 / 其他 |
| Q2 | 风险承受等级？ | R1（保守）/ R2（稳健）/ R3（平衡）/ R4（进取）/ R5（激进） |
| Q3 | 计划投资金额与期限？ | 金额（万元）+ 短期(<1年) / 中期(1-3年) / 长期(>3年) |
| Q4 | 是否有特殊约束？ | 行业偏好 / 禁投行业 / 流动性要求 / 其他 |

一次只问一个问题。全部回答后生成画像表。

## 输出

```yaml
profile_id: "P-{date}-{seq}"
rm_name: "{客户经理姓名}"
client_name: "{客户姓名}"
risk_level: "R3"
amount: 500000
horizon: "中期"
goal: "资产增值"
liquidity: "低"
constraints: []
investor_type: "普通投资者"
path_id: "WP-REC-01"
engine_reading_order:
  - engine/product-taxonomy.md
  - engine/filter-rules.md
  - engine/scoring-framework.md
  - engine/suitability-rules.md
  - engine/dual-track-methodology.md
quality_gates:
  - "风险等级匹配 (engine/suitability-rules.md §风险匹配矩阵)"
  - "产品禁售过滤 (engine/filter-rules.md §过滤规则详情)"
  - "评分置信度 (engine/scoring-framework.md §置信度规则)"
notes: ""
```

## 链接

下游技能：recommend-engine（将画像表作为输入，执行推荐管道）

## 护栏

- 风险等级仅使用 R1-R5，不得自创等级名称
- 客户姓名和客户经理姓名为必填项
- profile_id 格式为 P-YYYYMMDD-NNN
