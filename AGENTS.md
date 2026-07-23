# FolioPulse — 跨 CLI 通用入口

FolioPulse 是面向商业银行客户经理的 AI 驱动投资标的推荐引擎。
以 Agent Skill 形式分发，兼容 Claude Code、Codex、Cursor、Gemini、OpenCode。

## 技能索引

| 技能 | 路径 | 用途 |
|------|------|------|
| profile-intake | .claude/skills/profile-intake/SKILL.md | 客户画像摄入，4 问路由，生成画像表 |
| recommend-engine | .claude/skills/recommend-engine/SKILL.md | 推荐引擎，过滤打分排序 |
| recommend-qa | .claude/skills/recommend-qa/SKILL.md | 推荐质检，适当性校验，合规签章 |

## 三阶段管道

profile-intake → recommend-engine → recommend-qa

每个阶段产出 YAML 制品，通过制品传递结构化数据。

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
pytest tests/ -v
python scripts/consistency_check.py
```
