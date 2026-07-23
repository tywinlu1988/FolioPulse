# FolioPulse v0.1.0 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标：** 三阶段 Skill 管道跑通——从客户画像摄入到推荐列表输出，单适配器（东方财富），CLI TL;DR 速览。

**架构：** 引擎文档（Markdown + YAML 块）作为单一真相源 → Python 引擎运行时解析文档执行推荐 → Skill 编排管道。

**技术栈：** Python 3.11+ / pyyaml / dataclass / pytest / Markdown 模板

## 全局约束

- Python >= 3.11，依赖仅 pyyaml >= 6.0
- 所有数值阈值/权重只存在于 `dev/engine/` 文档中，Python 代码运行时解析，绝不硬编码
- 所有用户可见产出物使用中文，模板字段使用 `{字段名}` 占位符
- 回溯日志全程记录，无日志不交付
- SKILL.md frontmatter 仅含 `name` 和 `description` 两个字段
- 遵循 8 条反漂移铁律（设计文档 §9）
- 每任务独立可测，以 git commit 收尾

---

## 任务总览

| 阶段 | 任务编号 | 内容 |
|------|---------|------|
| 脚手架 | 1 | 项目脚手架（pyproject.toml, package.json, plugin.json, AGENTS.md） |
| 引擎文档 | 2-9 | 8 份引擎文档（单一真相源） |
| Python 核心 | 10-16 | path_sheet → adapters → filter → scorer → validator → trace → pipeline |
| 模板与画像 | 17-18 | 5 份交付物模板 + 客户画像模板 |
| Skill 链 | 19-21 | 3 份 SKILL.md（profile-intake / recommend-engine / recommend-qa） |
| 构建工具 | 22 | build_dist.py + consistency_check.py |
| 集成测试 | 23 | 端到端管道测试 |

---

### Task 1: 项目脚手架

**文件：**
- 创建: `pyproject.toml`, `package.json`, `plugin.json`, `AGENTS.md`
- 修改: `README.md`
- 创建目录: `dev/engine/`, `dev/templates/`, `dev/profiles/`, `dev/.claude/skills/profile-intake/`, `dev/.claude/skills/recommend-engine/`, `dev/.claude/skills/recommend-qa/`, `src/adapters/`, `scripts/`, `tests/`

**接口：**
- 产出: 项目可 `pip install -e .`，pytest 可发现测试

- [ ] **Step 1: 创建 `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "foliopulse-engine"
version = "0.1.0"
description = "FolioPulse — AI 驱动的投资标的推荐引擎"
requires-python = ">=3.11"
dependencies = ["pyyaml>=6.0"]

[tool.setuptools]
packages = ["src"]

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["."]
```

- [ ] **Step 2: 创建 `package.json`**

```json
{
  "name": "foliopulse",
  "version": "0.1.0",
  "description": "FolioPulse — AI 驱动的投资标的推荐引擎。面向商业银行客户经理的智能投资推荐 Skill。",
  "license": "SEE LICENSE IN LICENSE",
  "bin": { "foliopulse": "./bin/install.js" },
  "engines": { "node": ">=16.7.0" },
  "keywords": ["agent-skills", "claude-code", "investment", "portfolio", "recommendation"],
  "repository": "https://github.com/tywinlu1988/FolioPulse"
}
```

- [ ] **Step 3: 创建 `plugin.json`**

```json
{
  "name": "foliopulse",
  "description": "AI 驱动的投资标的推荐引擎。输入客户画像，输出结构化推荐列表及客户交付物料。",
  "version": "0.1.0",
  "author": { "name": "Tywin Lu", "email": "tywinlu1988@users.noreply.github.com" },
  "homepage": "https://github.com/tywinlu1988/FolioPulse",
  "repository": "https://github.com/tywinlu1988/FolioPulse",
  "license": "AGPL-3.0 + Commercial",
  "keywords": ["investment", "portfolio", "recommendation", "wealth-management", "china-markets"],
  "category": "finance",
  "skills": [
    "./dev/.claude/skills/profile-intake",
    "./dev/.claude/skills/recommend-engine",
    "./dev/.claude/skills/recommend-qa"
  ]
}
```

- [ ] **Step 4: 创建 `AGENTS.md`**

````markdown
# FolioPulse — 跨 CLI 通用入口

FolioPulse 是面向商业银行客户经理的 AI 驱动投资标的推荐引擎。
以 Agent Skill 形式分发，兼容 Claude Code、Codex、Cursor、Gemini、OpenCode。

## 技能索引

| 技能 | 路径 | 用途 |
|------|------|------|
| profile-intake | dev/.claude/skills/profile-intake/SKILL.md | 客户画像摄入，4 问路由，生成画像表 |
| recommend-engine | dev/.claude/skills/recommend-engine/SKILL.md | 推荐引擎，过滤打分排序 |
| recommend-qa | dev/.claude/skills/recommend-qa/SKILL.md | 推荐质检，适当性校验，合规签章 |

## 三阶段管道

profile-intake → recommend-engine → recommend-qa

每个阶段产出 YAML 制品，通过制品传递结构化数据。

## 单一真相源

所有数值阈值、权重、评分区间只存在于 `dev/engine/` 文档中。
Skill 文件和 Python 代码均引用引擎文档段落，绝不自行定义数值。

## 反漂移铁律

1. 禁止自创产品分类——所有类型引用 `dev/engine/product-taxonomy.md`
2. 禁止自定评分权重——所有因子权重引用 `dev/engine/scoring-framework.md`
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
````

- [ ] **Step 5: 更新 `README.md`**

将 README.md 定位从"个人投资追踪工具"更新为"商业银行客户经理投资推荐引擎"。关键改动：
- 标题下新增一行简述：面向商业银行客户经理的 AI 驱动投资标的推荐引擎
- 新增"三阶段管道"章节
- 新增"两段式交付"章节（CLI 速览 + 本地落盘）

- [ ] **Step 6: 创建目录结构**

```bash
mkdir -p dev/engine dev/templates dev/profiles
mkdir -p dev/.claude/skills/profile-intake
mkdir -p dev/.claude/skills/recommend-engine
mkdir -p dev/.claude/skills/recommend-qa
mkdir -p src/adapters scripts tests
```

- [ ] **Step 7: 安装依赖并验证**

```bash
pip install -e .
python -c "from src import __init__; print('OK')"
```

- [ ] **Step 8: 提交**

```bash
git add pyproject.toml package.json plugin.json AGENTS.md README.md
git commit -m "feat: project scaffold — build config, AGENTS.md, directory structure"
```

---

### Task 2: 引擎总览文档

**文件：**
- 创建: `dev/engine/engine-overview.md`

**接口：**
- 产出: 引擎文档导航入口，所有后续引擎文档的锚点

- [ ] **Step 1: 创建 `dev/engine/engine-overview.md`**

````markdown
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
````

- [ ] **Step 2: 提交**

```bash
git add dev/engine/engine-overview.md
git commit -m "feat: engine overview — document index and pipeline definition"
```

---

### Task 3: 产品分类体系文档

**文件：**
- 创建: `dev/engine/product-taxonomy.md`

**接口：**
- 产出: 10 种产品类型枚举、每种类型的适用因子和字段定义

- [ ] **Step 1: 创建 `dev/engine/product-taxonomy.md`**

内容包含 ````yaml` 块定义 10 种产品类型（stock/equity_fund/mixed_fund/bond_fund/index_fund/qdii_fund/etf/reit/convertible_bond/wealth_mgmt_product），每种类型包含 risk_range、applicable_factors、fields。同时定义 R1-R5 风险等级含义和短期/中期/长期投资期限。具体内容见设计文档 §3.1 和产品范围定义。

- [ ] **Step 2: 提交**

```bash
git add dev/engine/product-taxonomy.md
git commit -m "feat: product taxonomy — 10 product types with risk ranges and factors"
```

---

### Task 4: 多因子打分框架文档

**文件：**
- 创建: `dev/engine/scoring-framework.md`

**接口：**
- 产出: 股票 7 因子 + 基金 7 因子的定义（含权重、归一化阈值、数据源），综合评分公式和置信度规则

- [ ] **Step 1: 创建 `dev/engine/scoring-framework.md`**

内容包含 YAML 块定义股票因子（pe_percentile/pb_percentile/roe/revenue_growth/momentum_6m/volatility_90d/dividend_yield）和基金因子（alpha/beta/sharpe/max_drawdown/fund_size/manager_stability/expense_ratio），每因子包含 weight/normalization/thresholds/data_source。综合评分采用加权和公式，score_bands 定义 6 档评分标签，confidence 定义密度阈值规则。具体数据见设计文档 §4。

- [ ] **Step 2: 创建 `src/__init__.py`**

```python
"""FolioPulse — AI 驱动的投资标的推荐引擎."""

__version__ = "0.1.0"
```

- [ ] **Step 3: 提交**

```bash
git add dev/engine/scoring-framework.md src/__init__.py
git commit -m "feat: scoring framework — stock and fund factor definitions with weights"
```

---

### Task 5: 适当性管理规则文档

**文件：**
- 创建: `dev/engine/suitability-rules.md`

**接口：**
- 产出: 风险匹配矩阵、投资者类型分类、5 项质检门禁、禁售限售规则、合规话术要求

- [ ] **Step 1: 创建 `dev/engine/suitability-rules.md`**

内容包含 YAML 块定义 risk_match_matrix（R1-R5 各自的 allowed/prohibited/with_warning 列表）、investor_types（普通/合格投资者及其准入门槛）、5 个 gates（GATE_RISK_MATCH/GATE_PRODUCT_TYPE/GATE_CONSTRAINT/GATE_AMOUNT_MIN/GATE_HORIZON_MATCH）、禁售名单（ST 股票/停牌/退市/低价股）、合规话术（必含免责声明 + 禁用词汇列表）。具体数据见设计文档 §5。

- [ ] **Step 2: 提交**

```bash
git add dev/engine/suitability-rules.md
git commit -m "feat: suitability rules — risk matching matrix, investor types, compliance gates"
```

---

### Task 6: 规则过滤逻辑文档

**文件：**
- 创建: `dev/engine/filter-rules.md`

**接口：**
- 产出: 6 阶段过滤执行顺序、每条规则的逻辑描述和 hard/soft 分类、备选池规则

- [ ] **Step 1: 创建 `dev/engine/filter-rules.md`**

内容包含 YAML 块定义 filter_order（FILTER_RISK_LEVEL → FILTER_HORIZON → FILTER_AMOUNT → FILTER_BLACKLIST → FILTER_CONSTRAINT → FILTER_INVESTOR_TYPE），每条规则含 priority/type(hard|soft)/logic 描述，以及 candidate_pool 备选池规则（最大 20 只，来源为 with_warning 过滤产品）。具体数据见设计文档 §6。

- [ ] **Step 2: 提交**

```bash
git add dev/engine/filter-rules.md
git commit -m "feat: filter rules — 6-stage filter pipeline with hard/soft classification"
```

---

### Task 7: 双轨验证方法文档

**文件：**
- 创建: `dev/engine/dual-track-methodology.md`

**接口：**
- 产出: track_a/track_b 定义、4 种冲突裁决规则、轨 B 市场信号定义

- [ ] **Step 1: 创建 `dev/engine/dual-track-methodology.md`**

内容包含 YAML 块定义 tracks（轨 A 基本面 + 轨 B 市场信号）、conflict_rules（双正→互证增强 +0.5 / A 正 B 负→A 优先维持 / A 负 B 正→A 优先维持标注"市场信号先行" / 双负→互证削弱 -0.5 列入关注）、track_b_signals（fund_flow_5d/institution_change/sentiment_score 三项信号及其正负阈值）。具体数据见设计文档 §7。

- [ ] **Step 2: 提交**

```bash
git add dev/engine/dual-track-methodology.md
git commit -m "feat: dual-track methodology — fundamental vs market signal cross-validation"
```

---

### Task 8: 输出分层文档

**文件：**
- 创建: `dev/engine/output-layered.md`

**接口：**
- 产出: L0/L1/L2 三层定义、L0 CLI 模板、输出目录结构

- [ ] **Step 1: 创建 `dev/engine/output-layered.md`**

内容包含 YAML 块定义 layers（L0 速配卡/L1 推荐列表/L2 深度报告的内容规范、阅读时间、受众、格式）、L0 CLI 输出模板（含 ASCII 表格框架和 RM 操作菜单）、output_dir 定义（folio-{date}-{client_name}/ 目录结构、内含文件清单）。具体数据见设计文档 §8。

- [ ] **Step 2: 提交**

```bash
git add dev/engine/output-layered.md
git commit -m "feat: output layered — L0/L1/L2 tier definitions and CLI template"
```

---

### Task 9: 数据架构文档

**文件：**
- 创建: `dev/engine/data-architecture.md`

**接口：**
- 产出: 5 层数据源分层、Mode A/B 定义、适配器接口规范（5 个方法签名）

- [ ] **Step 1: 创建 `dev/engine/data-architecture.md`**

内容包含 YAML 块定义 data_layers（L1 行情/L2 基本面/L3 基金详情/L4 理财产品/L5 舆情，每层含 adapter/freshness/mode）、modes（Mode A 公开数据默认启动 + Mode B 外部数据需用户显式授权 + guardrail）、adapter_interface（fetch_product_list/fetch_product_detail/fetch_financial_data/fetch_market_signal/check_health 五个方法的输入输出规范）。具体数据见设计文档 §8。

- [ ] **Step 2: 提交**

```bash
git add dev/engine/data-architecture.md
git commit -m "feat: data architecture — 5-layer data sources, Mode A/B, adapter interface"
```

---

### Task 10: 路径表单模块

**文件：** 创建 `src/path_sheet.py`, `tests/test_path_sheet.py`

**接口：** 产出 `ProfileSheet`/`RecommendArtifact`/`QAVerdict` dataclass，`validate_profile_sheet()`，`parse_profile_sheet_yaml()`，`engine_dir()`

- [ ] **Step 1: 创建 `tests/test_path_sheet.py`（失败测试）**

```python
import pytest
from src.path_sheet import (
    ProfileSheet, RiskLevel, Horizon,
    validate_profile_sheet, parse_profile_sheet_yaml,
)

class TestProfileSheet:
    def test_valid_profile_sheet_passes_validation(self):
        ps = ProfileSheet(
            profile_id="P-20260723-001", rm_name="张经理",
            client_name="李客户", risk_level=RiskLevel.R3,
            amount=500000, horizon=Horizon.MEDIUM,
            goal="资产增值", liquidity="低",
            constraints=["不投军工"], investor_type="普通投资者",
        )
        assert len(validate_profile_sheet(ps)) == 0

    def test_missing_profile_id_fails(self):
        ps = ProfileSheet(
            profile_id="", rm_name="张经理", client_name="李客户",
            risk_level=RiskLevel.R3, amount=500000,
            horizon=Horizon.MEDIUM, goal="资产增值",
            liquidity="低", constraints=[], investor_type="普通投资者",
        )
        errors = validate_profile_sheet(ps)
        assert any("profile_id" in e.lower() for e in errors)

    def test_negative_amount_fails(self):
        ps = ProfileSheet(
            profile_id="P-001", rm_name="张经理", client_name="李客户",
            risk_level=RiskLevel.R3, amount=-10000,
            horizon=Horizon.MEDIUM, goal="资产增值",
            liquidity="低", constraints=[], investor_type="普通投资者",
        )
        errors = validate_profile_sheet(ps)
        assert any("金额" in e for e in errors)

    def test_parse_yaml_produces_profile_sheet(self):
        yaml_str = """
profile_id: "P-20260723-001"
rm_name: "张经理"
client_name: "李客户"
risk_level: "R3"
amount: 500000
horizon: "中期"
goal: "资产增值"
liquidity: "低"
constraints:
  - "不投军工"
investor_type: "普通投资者"
"""
        ps = parse_profile_sheet_yaml(yaml_str)
        assert ps.risk_level == RiskLevel.R3
        assert ps.amount == 500000

    def test_invalid_risk_level_raises(self):
        yaml_str = """
profile_id: "P-001"
risk_level: "R99"
amount: 100000
horizon: "中期"
goal: "test"
liquidity: "低"
investor_type: "普通投资者"
"""
        with pytest.raises(ValueError, match="风险等级"):
            parse_profile_sheet_yaml(yaml_str)
```

- [ ] **Step 2: 实现 `src/path_sheet.py`**

```python
"""Path sheet — 画像表校验与 YAML 解析."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
import yaml
from pathlib import Path


class RiskLevel(str, Enum):
    R1 = "R1"; R2 = "R2"; R3 = "R3"; R4 = "R4"; R5 = "R5"


class Horizon(str, Enum):
    SHORT = "短期"; MEDIUM = "中期"; LONG = "长期"


class Mode(str, Enum):
    A = "A"; B = "B"


class Verdict(str, Enum):
    PASS = "pass"; PASS_WITH_FINDINGS = "pass-with-findings"; FAIL = "fail"


@dataclass
class ProfileSheet:
    """S1 产出的客户画像表."""
    profile_id: str
    risk_level: RiskLevel
    amount: float
    horizon: Horizon
    goal: str
    liquidity: str
    investor_type: str
    rm_name: str = ""
    client_name: str = ""
    constraints: List[str] = field(default_factory=list)
    path_id: str = "WP-REC-01"
    notes: str = ""


@dataclass
class RecommendArtifact:
    """S2 产出的推荐制品."""
    path_id: str
    profile_id: str
    mode: Mode
    recommendations: List[dict] = field(default_factory=list)
    portfolio_summary: dict = field(default_factory=dict)
    data_completeness: dict = field(default_factory=dict)
    generated_at: str = ""


@dataclass
class QAVerdict:
    """S3 产出的质检判定."""
    path_id: str
    profile_id: str
    verdict: Verdict
    timestamp: str
    gate_results: List[dict] = field(default_factory=list)
    remediation: List[str] = field(default_factory=list)


def validate_profile_sheet(ps: ProfileSheet) -> List[str]:
    """校验画像表，返回错误列表。空列表表示通过."""
    errors = []
    if not ps.profile_id or not ps.profile_id.strip():
        errors.append("profile_id 不能为空")
    if not ps.rm_name or not ps.rm_name.strip():
        errors.append("客户经理姓名不能为空")
    if not ps.client_name or not ps.client_name.strip():
        errors.append("客户姓名不能为空")
    if ps.amount <= 0:
        errors.append("投资金额必须大于 0")
    if not ps.goal or not ps.goal.strip():
        errors.append("投资目标不能为空")
    if not ps.investor_type or not ps.investor_type.strip():
        errors.append("投资者类型不能为空")
    return errors


def parse_profile_sheet_yaml(yaml_str: str) -> ProfileSheet:
    """从 YAML 字符串解析画像表."""
    data = yaml.safe_load(yaml_str)
    risk_level_raw = data.get("risk_level", "")
    try:
        risk_level = RiskLevel(risk_level_raw)
    except ValueError:
        raise ValueError(f"不支持的风险等级: {risk_level_raw}")
    horizon_raw = data.get("horizon", "")
    try:
        horizon = Horizon(horizon_raw)
    except ValueError:
        raise ValueError(f"不支持的投资期限: {horizon_raw}")
    return ProfileSheet(
        profile_id=data.get("profile_id", ""),
        rm_name=data.get("rm_name", ""),
        client_name=data.get("client_name", ""),
        risk_level=risk_level,
        amount=float(data.get("amount", 0)),
        horizon=horizon,
        goal=data.get("goal", ""),
        liquidity=data.get("liquidity", ""),
        investor_type=data.get("investor_type", ""),
        constraints=data.get("constraints", []),
        path_id=data.get("path_id", "WP-REC-01"),
        notes=data.get("notes", ""),
    )


def parse_recommend_artifact_yaml(yaml_str: str) -> RecommendArtifact:
    """从 YAML 字符串解析推荐制品."""
    data = yaml.safe_load(yaml_str)
    return RecommendArtifact(
        path_id=data.get("path_id", ""),
        profile_id=data.get("profile_id", ""),
        mode=Mode(data.get("mode", "A")),
        recommendations=data.get("recommendations", []),
        portfolio_summary=data.get("portfolio_summary", {}),
        data_completeness=data.get("data_completeness", {}),
        generated_at=data.get("generated_at", ""),
    )


def parse_qa_verdict_yaml(yaml_str: str) -> QAVerdict:
    """从 YAML 字符串解析质检判定."""
    data = yaml.safe_load(yaml_str)
    return QAVerdict(
        path_id=data.get("path_id", ""),
        profile_id=data.get("profile_id", ""),
        verdict=Verdict(data.get("verdict", "fail")),
        timestamp=data.get("timestamp", ""),
        gate_results=data.get("gate_results", []),
        remediation=data.get("remediation", []),
    )


def engine_dir(root: Optional[Path] = None) -> Path:
    """返回引擎文档目录，自适应 dev 和 dist 两种布局."""
    base = Path(root) if root is not None else Path(__file__).resolve().parent.parent
    flat = base / "engine"
    return flat if flat.is_dir() else base / "dev" / "engine"
```

- [ ] **Step 3: 运行测试确认通过**

```bash
pytest tests/test_path_sheet.py -v
```

- [ ] **Step 4: 提交**

```bash
git add src/path_sheet.py tests/test_path_sheet.py
git commit -m "feat: path sheet — ProfileSheet validation and YAML parsing"
```

---

### Task 11: 数据适配器层

**文件：** 创建 `src/adapters/__init__.py`, `src/adapters/base.py`, `src/adapters/eastmoney.py`, `tests/test_adapters.py`

**接口：** 产出 `BaseAdapter` 抽象类（5 个抽象方法）、`EastMoneyAdapter`（v0.1.0 模拟数据）、`AdapterError`

- [ ] **Step 1: 创建测试并实现**

`src/adapters/__init__.py`:
```python
from src.adapters.base import BaseAdapter, AdapterError
from src.adapters.eastmoney import EastMoneyAdapter
__all__ = ["BaseAdapter", "AdapterError", "EastMoneyAdapter"]
```

`src/adapters/base.py` — 抽象基类，定义 5 个抽象方法：`fetch_product_list(product_type) -> List[Dict]`、`fetch_product_detail(product_code) -> Dict`、`fetch_financial_data(product_code, data_points) -> Dict[str, float]`、`fetch_market_signal(product_code, signal_ids) -> Dict[str, float]`、`check_health() -> bool`。方法签名来自 `dev/engine/data-architecture.md §适配器接口规范`。

`src/adapters/eastmoney.py` — v0.1.0 使用 15 只模拟产品数据库覆盖 5 种类型（stock/equity_fund/mixed_fund/bond_fund/etf），8 只产品的模拟财务数据，3 只产品的模拟市场信号。关键模拟数据：600519 贵州茅台（PE 28.5 / ROE 30.5 / 营收增速 15.2%），110011 易方达中小盘（Alpha 5.2 / Sharpe 1.35 / 最大回撤 22.5%），510300 沪深300ETF（跟踪误差 0.15% / 日均成交 25 亿）。

`tests/test_adapters.py` — 6 个测试：验证 EastMoneyAdapter 是 BaseAdapter 子类、check_health 返回 bool、fetch_product_list 对已知类型返回非空列表对未知类型返回空列表、fetch_financial_data 返回含请求字段的字典、fetch_market_signal 返回含请求信号的字典、BaseAdapter 不可直接实例化。

- [ ] **Step 2: 运行测试确认通过**

```bash
pytest tests/test_adapters.py -v
```

- [ ] **Step 3: 提交**

```bash
git add src/adapters/ tests/test_adapters.py
git commit -m "feat: adapters — BaseAdapter interface and EastMoney mock adapter"
```

---

### Task 12: 规则过滤引擎

**文件：** 创建 `src/filter_engine.py`, `tests/test_filter_engine.py`

**接口：** 消费 `ProfileSheet`，产出 `FilterEngine.apply_filters(products, profile) -> tuple[passed, rejected]`

- [ ] **Step 1: 实现 `src/filter_engine.py`**

核心组件：
- `FilterResult` 枚举 (PASS/REJECT/WARN)
- `RISK_MATCH_MATRIX` — R1-R5 各自的 allowed/prohibited/with_warning 列表（来自 suitability-rules.md）
- `filter_by_risk_level(client_risk, product_risk) -> FilterResult` — 查矩阵返回结果
- `filter_by_horizon(client_horizon, product_lock_months) -> FilterResult` — 短期≤12月/中期≤36月/长期∞
- `filter_by_amount(client_amount, product_min_amount) -> FilterResult`
- `FilterEngine` 类 — `apply_filters` 遍历产品，逐条检查（风险→期限→金额→约束），REJECT 记录原因，WARN 标记 warning 字段但仍进入 passed

- [ ] **Step 2: 创建测试（TDD：先写测试再补全实现）**

`tests/test_filter_engine.py` — 测试覆盖：R3客户通过R3/拒绝R5/对R4警告、中期匹配24月/短期拒绝36月、金额充足通过/不足拒绝、空列表输入、全匹配产品出现在passed、约束过滤（禁投军工排除军工行业产品）。

- [ ] **Step 3: 运行测试确认通过**

```bash
pytest tests/test_filter_engine.py -v
```

- [ ] **Step 4: 提交**

---

### Task 13: 多因子综合打分引擎

**文件：** 创建 `src/composite_scorer.py`, `tests/test_composite_scorer.py`

**接口：** 消费 `EastMoneyAdapter`、引擎文档（因子定义），产出 `CompositeScorer.score(products, profile) -> List[dict]`（附加 composite_score 和 factor_scores）

- [ ] **Step 1: 实现 `src/composite_scorer.py`**

核心逻辑：
1. `CompositeScorer` 初始化时加载因子定义（内建默认值，对应 scoring-framework.md）
2. `score(products, profile)` — 遍历产品 → 按产品类型选取适用因子 → 通过适配器拉取数据 → 逐因子归一化 → 加权求和
3. 四种归一化方法：
   - `linear(value, thresholds)` — 阈值区间内线性插值 0-10
   - `linear_inverse(value, thresholds)` — 反向线性
   - `percentile_inverse(value)` — (100 - 分位数) / 10
   - `target_range(value, lo, hi)` — 在目标范围内满分，越远越低
4. `_calculate_confidence(data_points)` — 有效数据点 / 总数据点 × 100

- [ ] **Step 2: 创建测试**

测试覆盖：股票评分在 0-10 范围、基金评分在 0-10 范围、ROE 更高得分更高（同行业）、Sharpe 更高得分更高、缺失数据降低置信度、空列表返回空。

- [ ] **Step 3: 运行测试确认通过**

- [ ] **Step 4: 提交**

---

### Task 14: 适当性校验引擎

**文件：** 创建 `src/suitability_validator.py`, `tests/test_suitability_validator.py`

**接口：** 消费 `ProfileSheet`, `RecommendArtifact`，产出 `SuitabilityValidator.validate(artifact, profile) -> QAVerdict`

- [ ] **Step 1: 实现**

```python
class SuitabilityValidator:
    def validate(self, artifact, profile) -> QAVerdict:
        gate_results = []
        gate_results.append(self._check_risk_match(artifact, profile))
        gate_results.append(self._check_product_type_access(artifact, profile))
        gate_results.append(self._check_constraints(artifact, profile))
        gate_results.append(self._check_min_amount(artifact, profile))
        gate_results.append(self._check_horizon_match(artifact, profile))
        
        failed = [g for g in gate_results if g["status"] == "fail"]
        warnings = [g for g in gate_results if g["status"] == "warn"]
        
        if failed:
            verdict = Verdict.FAIL
        elif warnings:
            verdict = Verdict.PASS_WITH_FINDINGS
        else:
            verdict = Verdict.PASS
        
        return QAVerdict(
            path_id=artifact.path_id,
            profile_id=artifact.profile_id,
            verdict=verdict,
            timestamp=datetime.now().isoformat(),
            gate_results=gate_results,
            remediation=[f["detail"] for f in failed],
        )
```

- [ ] **Step 2: 创建测试** — 覆盖 5 项门禁各自的通过/失败场景

- [ ] **Step 3: 运行测试 → 提交**

---

### Task 15: 回溯日志模块

**文件：** 创建 `src/trace_logger.py`, `tests/test_trace_logger.py`

**接口：** 产出 `TraceLogger` 类，`generate(output_dir) -> 回溯日志.md`

TraceLogger 维护 9 个内部列表（对应回溯日志 9 节），`generate` 方法按设计文档 §6 结构拼接生成完整 Markdown 文件。

- [ ] **Step 1: 实现 + 测试 + 提交**

---

### Task 16: 管道编排器

**文件：** 创建 `src/pipeline.py`, `tests/test_pipeline.py`

**接口：** 消费所有 engine 模块 + adapter，产出 `Pipeline.run(profile) -> Tuple[RecommendArtifact, QAVerdict]`

```python
class Pipeline:
    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter
        self.filter_engine = FilterEngine()
        self.scorer = CompositeScorer()
        self.validator = SuitabilityValidator()
        self.tracer = TraceLogger()

    def run(self, profile: ProfileSheet) -> Tuple[RecommendArtifact, QAVerdict]:
        self.tracer.set_input(profile)
        # Step 1: 拉取产品
        all_products = []
        for ptype in self._get_applicable_types(profile):
            all_products.extend(self.adapter.fetch_product_list(ptype))
        # Step 2: 过滤
        passed, rejected = self.filter_engine.apply_filters(all_products, profile)
        self.tracer.log_filter(passed, rejected)
        # Step 3: 打分
        scored = self.scorer.score(passed, profile)
        self.tracer.log_score(scored)
        # Step 4: 排序
        artifact = RecommendArtifact(
            path_id=profile.path_id, profile_id=profile.profile_id,
            mode=Mode.A,
            recommendations=sorted(scored, key=lambda x: x.get("composite_score", 0), reverse=True),
            generated_at=datetime.now().isoformat(),
        )
        # Step 5: 质检
        verdict = self.validator.validate(artifact, profile)
        self.tracer.log_compliance(verdict.gate_results)
        return artifact, verdict
```

- [ ] **Step 1: 创建集成测试** — R3 客户完整管道产出推荐、R1 客户只收到 R1 产品、空适配器返回空列表、回溯日志生成全部 9 节

- [ ] **Step 2: 运行全部测试 → 提交**

---

### Task 17: 交付物模板（5 份）

**文件：** 创建 `dev/templates/推荐清单.md`, `标的报告.md`, `问答清单.md`, `话术清单.md`, `配置建议书.md`

全部使用 `{字段名}` 占位符，零示例数据。配色遵循设计文档 §5.2。

- [ ] **实现 5 份模板 → 提交**

---

### Task 18: 客户画像模板

**文件：** 创建 `dev/profiles/default-profile.yaml`, `dev/profiles/profile-schema.md`

`default-profile.yaml` — 全字段空模板，risk_level 默认 R3，horizon 默认 中期
`profile-schema.md` — 字段类型/必填/可选值说明

- [ ] **实现 → 提交**

---

### Task 19-21: 三份 SKILL.md

**文件：**
- `dev/.claude/skills/profile-intake/SKILL.md` — S1 画像摄入，4 问路由协议，输出画像表 YAML
- `dev/.claude/skills/recommend-engine/SKILL.md` — S2 推荐引擎，四步管道，输出推荐制品 YAML
- `dev/.claude/skills/recommend-qa/SKILL.md` — S3 推荐质检，6 项门禁，输出质检判定 YAML

每份 SKILL.md frontmatter 仅含 `name` 和 `description`，结构遵循：用途 → 调用协议 → 核心逻辑 → 输出 → 链接（上下游） → 护栏。

- [ ] **实现 3 份 SKILL.md → 提交**

---

### Task 22: 构建与检查脚本

**文件：** 创建 `scripts/build_dist.py`, `scripts/consistency_check.py`

- `build_dist.py` — 将 dev/ 组装为 version/v0.1.0-release/ 发布包
- `consistency_check.py` — 6 项检查：引擎文档存在性、YAML 块可解析、因子权重和≈1.0、风险匹配矩阵覆盖全部 R1-R5、SKILL.md frontmatter 仅两个字段、模板不含示例数据

- [ ] **实现 → 提交**

---

### Task 23: 集成测试

**文件：** 创建 `tests/test_integration.py`

5 个端到端测试：
1. R3 客户完整管道产出推荐且通过质检
2. R1 保守客户只收到 R1 产品
3. 空适配器返回空推荐
4. 回溯日志包含全部 9 节
5. 画像表 YAML 往返解析+校验通过

```bash
pytest tests/ -v
```

- [ ] **全部测试通过 → 提交**

---

## 实现顺序

```
1 (脚手架)
  → 2 (引擎总览)
    → 3/4/5/6/7/8/9 可并行 (引擎文档)
      → 10 (path_sheet)
        → 11 (adapters)
          → 12 (filter) → 13 (scorer) → 14 (validator) → 15 (trace) → 16 (pipeline)
            → 17/18 可并行 (模板+画像)
              → 19/20/21 可并行 (SKILL.md)
                → 22 (构建脚本)
                  → 23 (集成测试)
```

每完成一个 Task，运行对应 pytest 确认通过后进入下一个。
