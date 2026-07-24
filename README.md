# FolioPulse

面向商业银行客户经理的 **AI 驱动投资标的推荐引擎**。  
输入客户画像，输出结构化推荐列表及全套客户交付物料。  
以 Agent Skill 形式分发，兼容 **Claude Code**、**Codex**、**Cursor**、**Gemini**、**OpenCode**。

[![Version](https://img.shields.io/badge/version-0.3.0-blue)](https://github.com/tywinlu1988/FolioPulse)
[![License](https://img.shields.io/badge/license-AGPL--3.0%20%2B%20Commercial-green)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](./pyproject.toml)

---

## 快速安装

### 方式一：npx 从 GitHub 安装（推荐）

```bash
npx github:tywinlu1988/FolioPulse --platform claude
```

支持平台：`claude` / `codex` / `cursor` / `gemini` / `opencode`

### 方式二：Git 克隆

```bash
git clone https://github.com/tywinlu1988/FolioPulse.git
cd FolioPulse
pip install -e .
```

### 方式三：GitHub Release

从 [Releases](https://github.com/tywinlu1988/FolioPulse/releases) 下载 `foliopulse-v{version}.zip`，解压后运行：

```bash
pip install -e .
```

### 验证安装

```bash
python scripts/consistency_check.py   # 应输出"全部通过"
```

---

## 这是什么？

FolioPulse 帮助商业银行客户经理为客户推荐二级市场投资标的。
覆盖 **10 种产品类型**（A 股股票、股票型/混合型/债券型/指数型/QDII 基金、ETF、REITs、可转债、银行理财产品）。

**输入** → 客户画像（风险等级 R1-R5、投资金额、期限、目标、约束条件）

**输出** → 结构化推荐列表（排名、评分、风险匹配、推荐理由）+ 5 份客户交付物料

---

## 核心逻辑

```
客户画像摄入 (S1)  →  推荐引擎 (S2)  →  推荐质检 (S3)  →  交付物生成
     │                    │                  │                │
  Profile Sheet      Recommend          QA Verdict       本地 Markdown
  (YAML)             Artifact (YAML)    (YAML)           文件目录
```

### 三阶段管道

| 阶段 | 技能 | 职责 |
|------|------|------|
| **S1 画像摄入** | [profile-intake](./.claude/skills/profile-intake/SKILL.md) | 4 问路由协议采集客户画像，生成 Profile Sheet YAML |
| **S2 推荐引擎** | [recommend-engine](./.claude/skills/recommend-engine/SKILL.md) | 规则过滤 → 多因子打分 → 双轨验证 → 排序+理由生成 |
| **S3 推荐质检** | [recommend-qa](./.claude/skills/recommend-qa/SKILL.md) | 5 项门禁校验（风险匹配/产品准入/客户约束/起投金额/期限匹配） |

### S2 推荐管道五步详解

```
Step 0: 数据拉取         Step 1: 规则过滤          Step 2: 多因子打分
(Mode A/B 判断)          ↓                        ↓
Step 3: 双轨验证         Step 4: 排序+理由
┌──────────────┐       ┌──────────────┐       ┌──────────────┐       ┌──────────────┐
│ WebSearch拉取  │       │ 股票 7 因子   │       │ 轨A 基本面    │       │ 综合评分降序   │
│ Mode A/B 判断   │  →   │ 基金 7 因子   │  →   │ 轨B 市场信号  │  →   │ 每只 ≤3 条    │
│ CSV/API/MCP    │       │ ETF 4 因子   │       │ 冲突裁决       │       │ 推荐理由      │
│ 数据溯源记录   │       │ 加权求和      │       │               │       │              │
│                │       │ 置信度评估    │       │               │       │              │
└──────────────┘       └──────────────┘       └──────────────┘       └──────────────┘
```

### 两段式交付

1. **CLI TL;DR 速览** — 终端展示推荐 Top 5 + 风险灯号，RM 可即时调整
2. **本地落盘** — 确认后一次性生成完整交付物目录（全中文 Markdown），可打印交付客户

```
folio-{日期}-{客户姓名}/
├── 推荐清单.html
├── 标的报告-{产品名}.html
├── 问答清单.html
├── 话术清单.html
├── 配置建议书.html
└── 回溯日志.md
```

---

## 引擎文档

> 所有数值阈值、权重、评分区间的**单一真相源**。Python 代码和 Skill 文件均引用这些文档段落，绝不自行定义数值。

| 文档 | 用途 | 关键内容 |
|------|------|---------|
| [engine-overview.md](./engine/engine-overview.md) | 架构总览 | 文档索引、流水线定义、反漂移约束 |
| [product-taxonomy.md](./engine/product-taxonomy.md) | 产品分类体系 | 10 种产品类型、适用因子、字段规范、风险等级 R1-R5 定义 |
| [scoring-framework.md](./engine/scoring-framework.md) | 多因子打分框架 | 股票 7 因子 + 基金 7 因子 + ETF 4 因子，含权重、归一化阈值、评分区间 |
| [suitability-rules.md](./engine/suitability-rules.md) | 适当性管理规则 | 风险匹配矩阵、投资者类型分类、5 项质检门禁、禁售名单、合规话术 |
| [filter-rules.md](./engine/filter-rules.md) | 规则过滤逻辑 | 6 阶段过滤执行顺序、过滤规则详情、备选池规则 |
| [dual-track-methodology.md](./engine/dual-track-methodology.md) | 双轨验证方法 | 轨 A 基本面 + 轨 B 市场信号、4 种冲突裁决规则 |
| [output-layered.md](./engine/output-layered.md) | 输出分层定义 | L0 速配卡 / L1 推荐列表 / L2 深度报告、CLI 模板、输出目录结构 |
| [data-architecture.md](./engine/data-architecture.md) | 数据架构 | 5 层数据源分层、Mode A/B 定义、适配器接口规范 |

---

## Python 引擎模块

| 模块 | 文件 | 职责 |
|------|------|------|
| **路径表单** | [src/path_sheet.py](./src/path_sheet.py) | 画像表/推荐制品/质检判定的数据模型与 YAML 解析，枚举定义 |
| **数据适配器** | [src/adapters/](./src/adapters/) | 抽象基类 + 东方财富模拟适配器（v0.1.0），预留 Wind/天天基金接口 |
| **过滤引擎** | [src/filter_engine.py](./src/filter_engine.py) | 风险等级/期限/金额/约束 4 项过滤，PASS/REJECT/WARN 三级判定 |
| **综合打分** | [src/composite_scorer.py](./src/composite_scorer.py) | 4 种归一化方法（线性/反向/分位数/目标区间），加权求和，置信度计算 |
| **适当性校验** | [src/suitability_validator.py](./src/suitability_validator.py) | 5 项门禁逐条校验，pass / pass-with-findings / fail 三级判定 |
| **回溯日志** | [src/trace_logger.py](./src/trace_logger.py) | 9 节完整回溯日志（输入/溯源/过滤/打分/双轨/合规/干预/输出/元数据） |
| **引擎加载器** | [src/engine_loader.py](./src/engine_loader.py) | 运行时解析引擎文档 YAML 块——风险矩阵/因子定义/置信度/双轨配置的单一真相源 |
| **双轨验证** | [src/dual_track.py](./src/dual_track.py) | 轨 A 基本面 × 轨 B 市场信号交叉验证，4 种冲突裁决 |
| **管道编排** | [src/pipeline.py](./src/pipeline.py) | 串联拉取→过滤→打分→双轨→排序→校验全流程，一键执行 |

---

## 反漂移铁律

以下规则约束所有 Skill 和引擎的行为，不可逾越：

| 编号 | 铁律 | 说明 |
|------|------|------|
| R1 | **禁止自创产品分类** | 所有类型引用 [product-taxonomy.md](./engine/product-taxonomy.md) |
| R2 | **禁止自定评分权重** | 所有因子权重引用 [scoring-framework.md](./engine/scoring-framework.md) |
| R3 | **禁止绕过适当性校验** | 每笔推荐须记录匹配规则 |
| R4 | **禁止伪造数据** | 无数据来源标注"数据缺失" |
| R5 | **禁止偏离画像表** | S2 严格按画像表参数执行 |
| R6 | **禁止跳过质检** | 未经 QA 签章不得输出 |
| R7 | **单一真相源** | 阈值和权重只存在于 [engine/](./engine/) |
| R8 | **必录回溯** | 每次推荐生成完整 [回溯日志](#回溯日志设计) |

---

## 版本路线

| 版本 | 里程碑 | 预计 |
|------|--------|------|
| **v0.1.0** ✅ | 三阶段管道跑通，单适配器（东方财富模拟） | 已完成 |
| **v0.1.1** ✅ | README 完善，npx 安装指引，引擎模块文档 | 已完成 |
| **v0.1.2** ✅ | 标准 Skill 目录结构，过程文件清理，npx 修复 | 已完成 |
| **v0.1.3** ✅ | Skill 链质检修复（预检/数据拉取/Mode B/自愈/两段式交付） | 已完成 |
| **v0.1.4** ✅ | 深度审查修复（归一化 clamp/金额解析/约束映射/npx 布局） | 已完成 |
| **v0.2.0** ✅ | 单一真相源实装（运行时解析引擎文档）+ 双轨验证实装 + 置信度规则 | 已完成 |
| **v0.3.0** ✅ | 全类型 HTML 报告模板（藏蓝/琥珀金专业配色，可打印） | 当前版本 |
| **v0.4.0** | RM 交互式调整，备选池，黑名单/投资者类型过滤，推荐理由生成 | 计划中 |
| **v0.5.0** | Mode B 外部数据（Wind），多适配器全覆盖（天天基金等） | 计划中 |
| **v1.0.0** | 生产可用，完整测试覆盖，合规审计报告，商业授权就绪 | 计划中 |

---

## 项目结构

```
foliopulse/
├── .claude/skills/            # 三阶段 Skill 链
│   ├── profile-intake/        #   S1: 客户画像摄入
│   ├── recommend-engine/      #   S2: 推荐引擎
│   └── recommend-qa/          #   S3: 推荐质检
├── engine/                    # 引擎文档（单一真相源，8 份）
├── templates/                 # 交付物模板（5 份，全中文）
├── profiles/                  # 客户画像模板
├── src/                       # Python 引擎（7 个模块）
│   └── adapters/              #   数据适配器层
├── scripts/                   # 构建与检查工具
├── bin/                       # npx 安装脚本
├── AGENTS.md                  # 跨 CLI 通用入口
├── plugin.json                # Marketplace 注册清单
├── pyproject.toml             # Python 构建配置
└── package.json               # npm/npx 分发配置
```

---

## 许可

FolioPulse 采用双许可模式：

- **AGPL-3.0** — 个人、教育及 AGPL 兼容场景免费使用
- **商业授权** — 商业闭源使用需单独授权

详见 [LICENSE](./LICENSE)。

---

## 关于

**FolioPulse** 由 Tywin Lu 创建并维护。

- **仓库**：[github.com/tywinlu1988/FolioPulse](https://github.com/tywinlu1988/FolioPulse)
- **协议**：源码开放，商业使用需授权
- **技术栈**：Python 3.11+ / PyYAML / pytest / Markdown
- **设计参考**：[Credence-China](https://github.com/tywinlu1988/Credence-China) / [Credence-Global](https://github.com/tywinlu1988/Credence-Global) / [Baker-Street](https://github.com/tywinlu1988/Baker-Street)

---

*FolioPulse 提供数据分析，不构成投资建议。投资有风险，入市需谨慎。*
