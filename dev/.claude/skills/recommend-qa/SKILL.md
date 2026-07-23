---
name: recommend-qa
description: >
  FolioPulse 推荐质检技能。接收 Recommend Artifact (YAML) 和原始 Profile Sheet，
  执行 5 项必检门禁（风险匹配/产品准入/客户约束/起投金额/期限匹配），
  输出 QA Verdict (YAML)。触发：上游 recommend-engine 产出推荐制品后自动衔接。
---

## 用途

对推荐制品执行质检，确保每条推荐通过适当性校验和合规检查。

## 5 项必检门禁

| 门禁 | 规则引用 | 不通过处理 |
|------|---------|-----------|
| 风险等级匹配 | suitability-rules.md §风险匹配矩阵 | 标记违规，降级或移除 |
| 产品类型准入 | suitability-rules.md §投资者类型分类 | 直接移除 |
| 客户约束匹配 | filter-rules.md §过滤规则详情 | 直接移除 |
| 起投金额 | suitability-rules.md §适当性校验门禁 | 标注"起投金额不足" |
| 期限匹配 | suitability-rules.md §适当性校验门禁 | 标注"期限不匹配" |

## 输出

质检判定 YAML：

```yaml
path_id: "WP-REC-01"
profile_id: "P-{date}-{seq}"
verdict: "pass"           # pass / pass-with-findings / fail
timestamp: "{timestamp}"
gate_results:
  - gate: "风险等级匹配"
    status: "pass"
    detail: "全部推荐产品风险等级匹配"
remediation: []
```

## 链接

上游：recommend-engine（产出推荐制品）
下游：终端（QA 签章后输出给客户经理）

## 护栏

- 未经 QA 签章的推荐不得输出（R6）
- 所有门禁结果记录到回溯日志（R8）
- 一次自动重试：fail 时允许 S2 修正后重新提交，仍 fail 则阻断
