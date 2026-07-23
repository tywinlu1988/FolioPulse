"""Path sheet — 画像表校验与 YAML 解析."""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from pathlib import Path

import yaml


# ── 枚举定义 ──────────────────────────────────────────

class RiskLevel(str, Enum):
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"
    R4 = "R4"
    R5 = "R5"


class Horizon(str, Enum):
    SHORT = "短期"
    MEDIUM = "中期"
    LONG = "长期"


class Mode(str, Enum):
    A = "A"
    B = "B"


class Verdict(str, Enum):
    PASS = "pass"
    PASS_WITH_FINDINGS = "pass-with-findings"
    FAIL = "fail"


# ── 数据模型 ──────────────────────────────────────────

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


# ── 校验函数 ──────────────────────────────────────────

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


# ── YAML 解析 ──────────────────────────────────────────

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
    """返回引擎文档目录."""
    base = Path(root) if root is not None else Path(__file__).resolve().parent.parent
    return base / "engine"
