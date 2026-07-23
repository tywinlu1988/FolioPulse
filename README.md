# FolioPulse

面向商业银行客户经理的 AI 驱动投资标的推荐引擎。支持 Claude Code 和 OpenAI Codex。

## 这是什么？

FolioPulse 帮助银行客户经理为客户推荐二级市场投资标的（基金、股票、ETF、理财产品等）。
输入客户画像（风险等级、投资金额、期限、目标），输出结构化推荐列表及客户交付物料。

## 核心能力

- **智能推荐** — 规则过滤 + 多因子打分，覆盖全品类投资产品
- **适当性管理** — 内置中国监管规则校验，逐笔风险匹配留痕
- **客户交付物** — 一键生成推荐清单、标的报告、问答清单、话术清单、配置建议书
- **过程可追溯** — 回溯日志记录每一步决策，可复盘可审计

## 三阶段管道

```
画像摄入 → 推荐引擎 → 推荐质检
(profile-intake → recommend-engine → recommend-qa)
```

每个阶段产出 YAML 结构化制品，在 Skill 间传递。

## 两段式交付

1. **CLI TL;DR 速览** — 客户经理在终端快速查看推荐 Top 5 + 风险灯号
2. **本地落盘** — 确认后生成完整交付物目录（全中文 Markdown），可打印交付客户

## 快速开始

```bash
# 安装
pip install -e .

# 运行测试
pytest tests/ -v

# 一致性检查
python scripts/consistency_check.py
```

## 许可

FolioPulse 采用双许可模式：

- **AGPL-3.0** — 个人、教育及 AGPL 兼容场景免费使用
- **商业授权** — 商业闭源使用需单独授权

详见 [LICENSE](./LICENSE)。

## 作者

Tywin Lu

---

*FolioPulse 提供数据分析，不构成投资建议。投资有风险，入市需谨慎。*
