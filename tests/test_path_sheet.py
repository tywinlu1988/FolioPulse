"""Tests for path_sheet module."""
import pytest
from src.path_sheet import (
    ProfileSheet, RiskLevel, Horizon,
    validate_profile_sheet, parse_profile_sheet_yaml,
)


class TestProfileSheet:
    """Tests for ProfileSheet dataclass and validation."""

    def test_valid_profile_sheet_passes_validation(self):
        ps = ProfileSheet(
            profile_id="P-20260723-001", rm_name="张经理",
            client_name="李客户", risk_level=RiskLevel.R3,
            amount=500000, horizon=Horizon.MEDIUM,
            goal="资产增值", liquidity="低",
            constraints=["不投军工"], investor_type="普通投资者",
        )
        errors = validate_profile_sheet(ps)
        assert len(errors) == 0

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
        assert ps.profile_id == "P-20260723-001"
        assert ps.risk_level == RiskLevel.R3
        assert ps.amount == 500000
        assert ps.horizon == Horizon.MEDIUM

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

    def test_invalid_horizon_raises(self):
        yaml_str = """
profile_id: "P-001"
risk_level: "R3"
amount: 100000
horizon: "超长期"
goal: "test"
liquidity: "低"
investor_type: "普通投资者"
"""
        with pytest.raises(ValueError, match="投资期限"):
            parse_profile_sheet_yaml(yaml_str)
