"""Tests for suitability validator."""
import pytest
from src.path_sheet import (
    ProfileSheet, RiskLevel, Horizon, RecommendArtifact, Mode, Verdict
)
from src.suitability_validator import SuitabilityValidator


class TestSuitabilityValidator:
    def test_all_valid_recommendations_pass(self):
        validator = SuitabilityValidator()
        artifact = RecommendArtifact(
            path_id="WP-REC-01", profile_id="P-001", mode=Mode.A,
            recommendations=[{
                "code": "000001", "name": "测试产品", "type": "equity_fund",
                "risk_level": "R3", "lock_period_months": 24, "min_amount": 1000,
            }],
        )
        profile = _make_profile()
        verdict = validator.validate(artifact, profile)
        assert verdict.verdict == Verdict.PASS

    def test_r5_product_fails_for_r3_client(self):
        validator = SuitabilityValidator()
        artifact = RecommendArtifact(
            path_id="WP-REC-01", profile_id="P-001", mode=Mode.A,
            recommendations=[{
                "code": "300750", "name": "宁德时代", "type": "stock",
                "risk_level": "R5", "lock_period_months": 0, "min_amount": 100,
            }],
        )
        verdict = validator.validate(artifact, _make_profile())
        assert verdict.verdict == Verdict.FAIL

    def test_constraint_violation_fails(self):
        validator = SuitabilityValidator()
        artifact = RecommendArtifact(
            path_id="WP-REC-01", profile_id="P-001", mode=Mode.A,
            recommendations=[{
                "code": "600001", "name": "军工ETF", "type": "etf",
                "industry": "军工", "risk_level": "R3",
                "lock_period_months": 0, "min_amount": 100,
            }],
        )
        profile = _make_profile(constraints=["不投军工"])
        verdict = validator.validate(artifact, profile)
        assert verdict.verdict == Verdict.FAIL

    def test_empty_recommendations_passes(self):
        validator = SuitabilityValidator()
        artifact = RecommendArtifact(
            path_id="WP-REC-01", profile_id="P-001", mode=Mode.A,
            recommendations=[],
        )
        verdict = validator.validate(artifact, _make_profile())
        assert verdict.verdict == Verdict.PASS

    def test_r4_product_warns_for_r3_client(self):
        validator = SuitabilityValidator()
        artifact = RecommendArtifact(
            path_id="WP-REC-01", profile_id="P-001", mode=Mode.A,
            recommendations=[{
                "code": "600519", "name": "贵州茅台", "type": "stock",
                "risk_level": "R4", "lock_period_months": 0, "min_amount": 100,
            }],
        )
        verdict = validator.validate(artifact, _make_profile())
        assert verdict.verdict == Verdict.PASS_WITH_FINDINGS


def _make_profile(**overrides):
    defaults = {
        "profile_id": "P-001", "risk_level": RiskLevel.R3,
        "amount": 500000, "horizon": Horizon.MEDIUM,
        "goal": "资产增值", "liquidity": "低",
        "investor_type": "普通投资者",
        "rm_name": "张经理", "client_name": "李客户",
    }
    defaults.update(overrides)
    return ProfileSheet(**defaults)
