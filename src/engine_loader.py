"""引擎文档运行时解析器 —— 单一真相源（R7）的实现.

所有数值阈值、权重、规则在运行时从 engine/*.md 的 YAML 块解析，
Python 代码中不硬编码任何规则值。文档未定义时抛出 EngineDocError，
不得用通用先验补位（对应 SKILL 中的"引擎未定义"协议）。
"""

import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional

import yaml

from src.path_sheet import RiskLevel, engine_dir


class EngineDocError(Exception):
    """引擎文档缺失或规则未定义."""
    pass


def _load_yaml_key(doc_path: Path, key: str):
    """从 Markdown 文档的 YAML 块中解析指定 key."""
    if not doc_path.exists():
        raise EngineDocError(f"引擎文档缺失: {doc_path}")
    text = doc_path.read_text(encoding="utf-8")
    for block in re.findall(r"```yaml\n(.*?)```", text, re.DOTALL):
        data = yaml.safe_load(block)
        if isinstance(data, dict) and key in data:
            return data[key]
    raise EngineDocError(f"引擎未定义: {doc_path.name} 中未找到 '{key}'")


@lru_cache(maxsize=4)
def load_risk_matrix(root: Optional[str] = None) -> Dict[RiskLevel, dict]:
    """从 suitability-rules.md 加载风险匹配矩阵.

    返回: {RiskLevel: {"allowed": [...], "prohibited": [...], "with_warning": [...]}}
    """
    doc = engine_dir(Path(root) if root else None) / "suitability-rules.md"
    raw = _load_yaml_key(doc, "risk_match_matrix")
    matrix = {}
    for level, entry in raw.items():
        try:
            client = RiskLevel(level)
        except ValueError:
            raise EngineDocError(f"风险匹配矩阵包含无效等级: {level}")
        matrix[client] = {
            "allowed": [RiskLevel(r) for r in entry.get("allowed", [])],
            "prohibited": [RiskLevel(r) for r in entry.get("prohibited", [])],
            "with_warning": [RiskLevel(r) for r in entry.get("with_warning", [])],
        }
    return matrix


def _convert_factor(raw: dict) -> dict:
    """将文档因子定义转换为运行时结构（thresholds 列表转元组）."""
    factor = {
        "id": raw["id"],
        "weight": float(raw["weight"]),
        "normalization": raw.get("normalization", "linear"),
        "data_point": raw.get("data_point", ""),
    }
    if "thresholds" in raw:
        factor["thresholds"] = [tuple(t) for t in raw["thresholds"]]
    if "target_range" in raw:
        factor["target_range"] = list(raw["target_range"])
    return factor


@lru_cache(maxsize=4)
def load_factor_sets(root: Optional[str] = None) -> Dict[str, List[dict]]:
    """从 scoring-framework.md 加载全部因子集（stock/fund/etf）."""
    doc = engine_dir(Path(root) if root else None) / "scoring-framework.md"
    sets = {}
    for key in ("stock_factors", "fund_factors", "etf_factors"):
        raw = _load_yaml_key(doc, key)
        sets[key] = [_convert_factor(f) for f in raw]
    return sets


@lru_cache(maxsize=4)
def load_factor_mapping(root: Optional[str] = None) -> Dict[str, str]:
    """从 scoring-framework.md 加载产品类型 → 因子集映射."""
    doc = engine_dir(Path(root) if root else None) / "scoring-framework.md"
    return _load_yaml_key(doc, "factor_mapping")


@lru_cache(maxsize=4)
def load_confidence_rules(root: Optional[str] = None) -> dict:
    """从 scoring-framework.md 加载置信度规则."""
    doc = engine_dir(Path(root) if root else None) / "scoring-framework.md"
    return _load_yaml_key(doc, "confidence")


@lru_cache(maxsize=4)
def load_dual_track_config(root: Optional[str] = None) -> dict:
    """从 dual-track-methodology.md 加载双轨配置."""
    doc = engine_dir(Path(root) if root else None) / "dual-track-methodology.md"
    return {
        "track_a": _load_yaml_key(doc, "track_a_evaluation"),
        "track_b_signals": _load_yaml_key(doc, "track_b_signals"),
        "track_b_aggregation": _load_yaml_key(doc, "track_b_aggregation"),
    }
