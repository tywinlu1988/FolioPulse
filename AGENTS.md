# FolioPulse — 跨 CLI 通用入口

FolioPulse 是面向商业银行客户经理的 AI 驱动投资标的推荐引擎。
以 Agent Skill 形式分发，兼容 Claude Code、Codex、Cursor、Gemini、OpenCode。

## 技能索引

| 技能 | 路径 | 用途 |
|------|------|------|
| profile-intake | .claude/skills/profile-intake/SKILL.md | 客户画像摄入，预检 + 4 问路由，生成画像表 |
| recommend-engine | .claude/skills/recommend-engine/SKILL.md | 推荐引擎，五步管道（数据拉取→过滤→打分→双轨→排序） |
| recommend-qa | .claude/skills/recommend-qa/SKILL.md | 推荐质检 + 两段式交付（TL;DR → RM 确认 → 生成交付物） |

## 四阶段管道

```
profile-intake → recommend-engine → recommend-qa(S3) → recommend-qa(S4)
     │                 │                    │                │
  Profile Sheet    Recommend           QA Verdict      交付物落盘
  (YAML)          Artifact (YAML)      + L0 TL;DR      本地目录
```

### 链式调用规则

1. **S1 → S2 自动衔接**：画像表产出后立即移交 recommend-engine，不等待用户确认
2. **S2 → S3 自动衔接**：推荐制品产出后立即移交 recommend-qa，不等待用户确认
3. **S3 → S4 需 RM 确认**：TL;DR 展示后等 RM 选择 [3]，才进入交付物生成
4. **制品传递**：各阶段通过 YAML 制品传递结构化数据，Skill 间不重复解析

## 单一真相源

所有数值阈值、权重、评分区间只存在于 `engine/` 文档中。
Skill 文件和 Python 代码均引用引擎文档段落，绝不自行定义数值。

## 反漂移铁律

1. 禁止自创产品分类——所有类型引用 `engine/product-taxonomy.md`
2. 禁止自定评分权重——所有因子权重引用 `engine/scoring-framework.md`
3. 禁止绕过适当性校验——每笔推荐须记录匹配规则
4. 禁止伪造数据——无来源数据标注"数据缺失"
5. 禁止偏离画像表——S2 严格按画像表参数执行
6. 禁止跳过质检——未经 QA 签章不得输出
7. 单一真相源——阈值和权重只存在于引擎文档
8. 必录回溯——每次推荐生成完整回溯日志

## 验证命令

```bash
python scripts/consistency_check.py
```
