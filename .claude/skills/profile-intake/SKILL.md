---
name: profile-intake
description: >
  FolioPulse 客户画像摄入技能。当客户经理描述客户情况、提及投资需求、
  或询问"帮客户看看""给客户推荐"等意图时触发。
  通过预检 + 4 问路由协议采集客户画像，生成结构化 Profile Sheet (YAML)。
---

## 用途

将客户经理的自然语言描述转换为结构化的客户画像表（Profile Sheet YAML），
作为后续推荐引擎的输入。

## 调用协议

### §0 预检：信息覆盖度评估

**收到客户经理输入后，先不提问。** 扫描已有信息，对照画像表必填字段提取：

| 字段 | 提取关键词/模式 |
|------|---------------|
| 风险等级 | R1/R2/R3/R4/R5、保守/稳健/平衡/进取/激进 |
| 投资金额 | 数字 + 万/元/亿 |
| 投资期限 | 短期/中期/长期、<1年/1-3年/>3年、半年/几个月 |
| 投资目标 | 增值/保本/养老/教育/流动性/投机 |
| 客户姓名 | "XX客户""XX先生/女士""客户叫XX" |
| 客户经理 | "我是XX""我叫XX"（默认为当前用户） |
| 投资者类型 | 普通投资者/合格投资者、资产/收入（若提及 ≥500万或 ≥50万年收入） |
| 特殊约束 | "不投XX""偏好XX""禁投XX""只要XX""不要XX" |
| 流动性需求 | "随时赎回""可锁定XX月/年""不急用""随时要用" |

**规则：**
- 提取到的字段，在后续提问中**跳过**
- 未提取到的必填字段，按 §1 的四问顺序逐一提问
- 如果 RM 提供的信息不足以提取**任何**必填字段，从 Q1 开始
- 如果所有必填字段均已覆盖，跳过提问，直接生成画像表

### §1 逐问采集

**仅提问预检中标记为缺失的问题。一次一问。**

| 问序 | 问题 | 选项 |
|------|------|------|
| Q1 | 客户的投资目标是什么？ | 资产增值 / 稳健收益 / 养老规划 / 子女教育 / 流动性管理 / 其他 |
| Q2 | 风险承受等级？ | R1（保守）/ R2（稳健）/ R3（平衡）/ R4（进取）/ R5（激进） |
| Q3 | 计划投资金额与期限？ | 金额（万元）+ 短期(<1年) / 中期(1-3年) / 长期(>3年) |
| Q4 | 是否有特殊约束？ | 行业偏好 / 禁投行业 / 流动性要求 / 其他 |

缺失的必填字段（客户姓名、投资者类型）在四问后补充提问。

## 输出

全部必填字段齐备后生成画像表。**不要等 RM 确认，直接输出 YAML 并衔接下游。**

```yaml
profile_id: "P-{YYYYMMDD}-{3位序号}"
rm_name: "{客户经理姓名}"
client_name: "{客户姓名}"
risk_level: "R3"
amount: 500000
horizon: "中期"
goal: "资产增值"
liquidity: "低"
constraints: []
investor_type: "普通投资者"
mode: "A"
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
profile_completeness:
  mandatory_filled: "{已填数}/{总数}"
  missing_fields: []
  confidence: "高"
notes: ""
```

## 链接

**下游技能：recommend-engine** — 画像表生成后**立即**移交，不需要 RM 确认。

## 护栏

- 风险等级仅使用 R1-R5，不得自创等级名称
- 客户姓名和客户经理姓名为必填项
- profile_id 格式为 P-YYYYMMDD-NNN
- 预检不会因为部分字段缺失而报错——缺失是正常的，提问即可
- 不要为了"快速完成"而跳步或合并问题
