---
name: recommend-engine
description: >
  FolioPulse 推荐引擎技能。接收 Profile Sheet (YAML)，执行五步推荐管道
  （数据拉取 → 规则过滤 → 多因子打分 → 双轨验证 → 排序+理由生成），
  输出 Recommend Artifact (YAML)。触发：上游 profile-intake 产出画像表后自动衔接。
---

## 用途

按画像表参数执行推荐管道，产出结构化推荐制品。

## 调用协议

S1 产出画像表 YAML 后，**立即**读取并进入本节管道。
加载画像表 `engine_reading_order` 中列出的全部引擎文档。
同时**必须加载**以下未在 reading_order 中列出但对管道执行关键的文件：
- `engine/output-layered.md` — L0 输出模板
- `engine/data-architecture.md` — Mode A/B 判断

加载后执行五步管道。

---

## 五步管道

### Step 0: 数据拉取与模式判断

**0.1 模式判断：**
- 检查画像表 `mode` 字段
- `mode: "A"`（默认）→ 进入 §0.2 公开数据拉取
- `mode: "B"` → 跳转到 §0.3 外部数据接入

**0.2 Mode A — 公开数据拉取：**

使用 **WebSearch** 工具，针对画像表适用的产品类型，逐类搜索当前可投资产品。

搜索关键词模板（替换 `{产品类型}` 为 engine/product-taxonomy.md 中的类型名）：
```
"{产品类型} 业绩排名 {当前年份} 推荐" 基金 OR 股票 OR ETF
```

拉取数据时严格对照 `engine/scoring-framework.md` 中各产品类型因子的 `data_point` 字段。
不可自行增减数据点。

**数据拉取清单（按产品类型）：**

| 产品类型 | 需拉取的数据点 | 搜索轮次 |
|---------|-------------|---------|
| stock | pe_ttm_percentile_5y, pb_percentile_5y, roe_ttm, revenue_cagr_3y, price_return_6m, annualized_volatility_90d, dividend_yield_ttm | 2-3 轮 |
| equity_fund | alpha_annualized_3y, beta_3y, sharpe_ratio_3y, max_drawdown_3y, aum_yuan, manager_tenure_years, total_expense_ratio | 2-3 轮 |
| mixed_fund | 同 equity_fund | 2-3 轮 |
| bond_fund | ytm, duration, sharpe_ratio_3y, max_drawdown_3y, aum_yuan, total_expense_ratio | 2 轮 |
| etf | tracking_error_1y, avg_daily_volume, expense_ratio, aum_yuan | 2 轮 |

每轮搜索后，将获取到的数据点记录到**回溯日志 §2 数据溯源表**：
- 数据点名称
- 数值
- 来源 URL
- 获取时间
- 置信度（搜索引擎返回的直接数据=高 / 推算数据=中 / 无法获取=标注"数据缺失"）

**0.3 Mode B — 外部数据接入：**

仅在客户经理**显式提供**外部数据源时激活。激活方式：

- **CSV 上载**：RM 说"这是产品数据 CSV"并提供文件路径 → 读取 CSV，按 `engine/product-taxonomy.md` 字段规范映射列名
- **API 端点**：RM 提供 REST API base URL 和认证方式 → 构造请求拉取数据
- **MCP Server**：RM 提供 MCP server 名称 → 通过对应 MCP 工具调用

Mode B 数据记录时标注来源为 "Mode B: {source_name}"。

**护栏：**
- 未经 RM 显式授权的 Mode B 数据源，QA 阶段标记为违规
- Mode B 数据缺失时，不降级到 Mode A 搜索——两者不混合
- 如果 Mode B 仅覆盖部分数据点，缺失部分标注 "Mode B 未提供"

完成后输出签章：
> **[0/5] 数据拉取完成：{product_count} 只产品，Mode {A/B}，数据密度 {density_pct}%**

---

### Step 1: 规则过滤

按 `engine/filter-rules.md` 的 6 阶段过滤顺序依次执行：

1. **FILTER_RISK_LEVEL** — 查 `engine/suitability-rules.md §风险匹配矩阵`，移除 prohibited 产品，标记 with_warning 产品
2. **FILTER_HORIZON** — 产品锁定期 > 客户投资期限 → 移除
3. **FILTER_AMOUNT** — 起投金额 > 客户预算 → 移除
4. **FILTER_BLACKLIST** — 查 `engine/suitability-rules.md §禁售/限售规则`（ST/停牌/退市/低价股）→ 移除
5. **FILTER_CONSTRAINT** — 违反客户自定义约束 → 移除
6. **FILTER_INVESTOR_TYPE** — 普通投资者不满足产品准入 → 移除

每条过滤记录拒绝原因。

完成后输出签章：
> **[1/5] 规则过滤完成：{passed} 只通过，{rejected} 只拒绝**  
> *备选池：{candidate} 只（with_warning 产品）*

---

### Step 2: 多因子打分

按 `engine/scoring-framework.md` 对各产品类型的因子定义，逐只打分：

1. 按产品类型选取适用因子表（stock → 股票 7 因子 / fund → 基金 7 因子 / etf → ETF 4 因子）
2. 逐因子归一化：linear / linear_inverse / percentile_inverse / target_range
3. 加权求和，计算 composite_score
4. 计算置信度（有效数据点数 / 总数据点数 × 100）
5. 低于 50% 置信度的产品，标注"中置信度"但不调整分数
6. 任一关键因子数据密度 <20% → 该因子评分输出 null

完成后输出签章：
> **[2/5] 多因子打分完成：{scored} 只评分，平均 {avg_score}/10，平均置信度 {avg_conf}%**

---

### Step 3: 双轨验证

按 `engine/dual-track-methodology.md` 执行交叉验证：

1. **轨 A（基本面）**：基于 Step 1-2 的评分结果，标记 positive / negative
2. **轨 B（市场信号）**：使用 WebSearch 拉取 fund_flow_5d / institution_change / sentiment_score，标记 positive / negative

冲突裁决（查 `engine/dual-track-methodology.md §冲突裁决`）：

| 轨 A | 轨 B | 裁决 |
|------|------|------|
| positive | positive | 互证增强 → 评分 +0.5 |
| positive | negative | 轨 A 优先 → 维持，标注"市场信号分歧" |
| negative | positive | 轨 A 优先 → 维持，标注"市场信号先行" |
| negative | negative | 互证削弱 → 评分 -0.5，列入关注名单 |

完成后输出签章：
> **[3/5] 双轨验证完成：{reinforced} 只增强 / {divergent} 只分歧 / {weakened} 只削弱**

---

### Step 4: 排序 + 理由生成

1. 按最终 composite_score 降序排列
2. 每只产品生成不超过 3 条推荐理由，格式："{因子名} {表现描述}"，引用具体数值
3. 组合层面生成配比建议（按类型分布）
4. 标注数据缺失项

完成后输出签章：
> **[4/5] 排序完成：Top 1 {name}({score}分)**

---

## 输出

输出 Recommend Artifact YAML。**产出后立即移交下游 recommend-qa，不等待。**

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
    risk_level: "R3"
    risk_match: "匹配"
    factor_scores:
      sharpe: { raw: 1.35, normalized: 6.5, weight: 0.25, weighted: 1.63 }
    rationale:
      - "{理由一（含具体数值）}"
      - "{理由二}"
      - "{理由三}"
    risk_flags: []
portfolio_summary:
  asset_allocation:
    - type: "股票型基金"
      ratio: 0.45
  risk_exposure:
    concentration_industry: "适中"
data_completeness:
  density_pct: 82
  confidence: "中"
  data_gaps:
    - "QDII 净值 T+2 延迟"
```

## 链接

- **上游**：profile-intake（产出画像表）
- **下游**：recommend-qa（接收推荐制品，执行质检 → 展示 TL;DR → 等 RM 确认）
- **链式调用规则**：本 Skill 产出 YAML 制品后，**立即调用 recommend-qa**，不等待用户确认

## 护栏

- 绝不偏离画像表的参数范围（反漂移铁律 R5）
- 任何未在引擎文档中定义的阈值不得使用——输出"引擎未定义"
- 数据缺失字段标注"数据缺失"，不编造（R4）
- 全部过滤日志和打分明细记录到回溯日志（R8）
- 每步管道完成后必须输出签章行
- 双轨验证不可跳过——即使轨 B 数据获取困难，也必须标注"轨 B 数据不足"而非省略
