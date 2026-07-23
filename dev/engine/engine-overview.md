# FolioPulse 引擎总览

> 版本：v0.1.0 | 所有数值阈值的唯一来源

## 文档索引

| 文档 | 用途 | 关键产出 |
|------|------|---------|
| [product-taxonomy.md](./product-taxonomy.md) | 产品分类体系 | 产品类型定义、字段规范 |
| [scoring-framework.md](./scoring-framework.md) | 多因子打分框架 | 因子定义、权重、归一化方法、评分区间 |
| [suitability-rules.md](./suitability-rules.md) | 适当性管理规则 | 风险匹配矩阵、投资者类型映射 |
| [filter-rules.md](./filter-rules.md) | 规则过滤逻辑 | 过滤条件、禁售名单、约束匹配 |
| [dual-track-methodology.md](./dual-track-methodology.md) | 双轨验证方法 | 轨A基本面 + 轨B市场信号交叉验证 |
| [output-layered.md](./output-layered.md) | 输出分层定义 | L0/L1/L2 层级内容规范 |
| [data-architecture.md](./data-architecture.md) | 数据架构 | 数据源分层、Mode A/B 定义 |

## 架构概览

推荐管道的四个步骤：

```
规则过滤 → 多因子打分 → 双轨验证 → 排序+理由生成
```

每一步的具体逻辑定义在对应的引擎文档中。

## 评分流水线

```yaml
pipeline:
  steps:
    - id: filter
      doc: dev/engine/filter-rules.md
      produces: filtered_list
    - id: score
      doc: dev/engine/scoring-framework.md
      consumes: filtered_list
      produces: scored_list
    - id: validate
      doc: dev/engine/dual-track-methodology.md
      consumes: scored_list
      produces: validated_list
    - id: rank
      doc: dev/engine/scoring-framework.md
      consumes: validated_list
      produces: ranked_recommendations
```

## 反漂移约束

引擎文档是单一真相源。所有 Python 代码通过运行时解析本文档及子文档获取阈值、权重和规则。
任何未在引擎文档中定义的数值不得出现在推荐输出中——输出 `引擎未定义` 并阻断。
