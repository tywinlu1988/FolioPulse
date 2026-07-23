---
name: recommend-engine
description: >
  FolioPulse 推荐引擎技能。接收 Profile Sheet (YAML)，执行四步推荐管道
  （规则过滤 → 多因子打分 → 双轨验证 → 排序+理由生成），
  输出 Recommend Artifact (YAML)。触发：上游 profile-intake 产出画像表后自动衔接。
---

## 用途

按画像表参数执行推荐管道，产出结构化推荐制品。

## 调用协议

接收画像表 YAML → 加载 `engine_reading_order` 中列出的引擎文档 →
执行四步管道 → 输出推荐制品。

## 四步管道

### Step 1: 规则过滤
按 `engine/filter-rules.md` 的 6 阶段过滤顺序执行。
所有被拒绝的产品记录拒绝原因。

### Step 2: 多因子打分
按 `engine/scoring-framework.md` 的因子定义，对通过过滤的产品逐只打分。
归一化方法引用引擎文档各因子的 normalization 字段。

### Step 3: 双轨验证
按 `engine/dual-track-methodology.md` 执行交叉验证。
冲突时轨 A（基本面）优先。

### Step 4: 排序 + 理由生成
按综合评分降序排列。每只产品生成不超过 3 条推荐理由。

## 输出

推荐制品 YAML，结构如下：

```yaml
path_id: "WP-REC-01"
profile_id: "P-{date}-{seq}"
mode: "A"
generated_at: "{timestamp}"
recommendations:
  - rank: 1
    code: "{code}"
    name: "{name}"
    type: "{type}"
    composite_score: 0.0
    risk_match: "匹配"
    factor_scores: {}
    rationale: []
portfolio_summary:
  asset_allocation: []
  risk_exposure: {}
data_completeness:
  density_pct: 0
  confidence: ""
  data_gaps: []
```

## 链接

上游：profile-intake（产出画像表）
下游：recommend-qa（接收推荐制品，执行质检）

## 护栏

- 绝不偏离画像表的参数范围（反漂移铁律 R5）
- 任何未在引擎文档中定义的阈值不得使用——输出"引擎未定义"
- 数据缺失字段标注"数据缺失"，不编造（R4）
- 全部过滤日志和打分明细记录到回溯日志（R8）
