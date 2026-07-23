"""End-to-end integration tests for FolioPulse pipeline."""
import os
import tempfile
import pytest
from src.path_sheet import (
    ProfileSheet, RiskLevel, Horizon, Verdict,
    parse_profile_sheet_yaml, validate_profile_sheet,
)
from src.adapters.eastmoney import EastMoneyAdapter
from src.pipeline import Pipeline


class TestEndToEndPipeline:
    """端到端管道测试."""

    def test_r3_client_full_pipeline(self):
        """R3 客户 50 万中期投资 → 管道产出推荐且通过质检."""
        profile = ProfileSheet(
            profile_id="P-TEST-001", rm_name="张经理", client_name="李客户",
            risk_level=RiskLevel.R3, amount=500000, horizon=Horizon.MEDIUM,
            goal="资产增值", liquidity="低", investor_type="普通投资者",
        )
        adapter = EastMoneyAdapter()
        pipeline = Pipeline(adapter)
        artifact, verdict = pipeline.run(profile)

        assert len(artifact.recommendations) > 0, "应至少有一只推荐产品"
        assert all(
            0 <= r.get("composite_score", -1) <= 10
            for r in artifact.recommendations
        ), "所有评分应在 0-10 范围"
        assert verdict.verdict in (
            Verdict.PASS, Verdict.PASS_WITH_FINDINGS
        ), f"质检应通过或带发现，实际: {verdict.verdict}"

    def test_r1_client_only_gets_safe_products(self):
        """R1 保守客户只能收到 R1-R2 风险等级产品."""
        profile = ProfileSheet(
            profile_id="P-TEST-002", rm_name="张经理", client_name="王客户",
            risk_level=RiskLevel.R1, amount=100000, horizon=Horizon.SHORT,
            goal="稳健收益", liquidity="高", investor_type="普通投资者",
        )
        adapter = EastMoneyAdapter()
        pipeline = Pipeline(adapter)
        artifact, verdict = pipeline.run(profile)

        for rec in artifact.recommendations:
            product_risk = rec.get("risk_level", "R1")
            assert product_risk in ("R1", "R2"), (
                f"R1 客户不应收到 {product_risk} 产品: {rec.get('name')}"
            )

    def test_empty_adapter_returns_empty_recommendations(self):
        """无产品数据的适配器应返回空推荐列表."""
        class EmptyAdapter(EastMoneyAdapter):
            def fetch_product_list(self, product_type):
                return []

        profile = ProfileSheet(
            profile_id="P-TEST-003", rm_name="张经理", client_name="赵客户",
            risk_level=RiskLevel.R3, amount=500000, horizon=Horizon.MEDIUM,
            goal="资产增值", liquidity="低", investor_type="普通投资者",
        )
        pipeline = Pipeline(EmptyAdapter())
        artifact, verdict = pipeline.run(profile)
        assert artifact.recommendations == []

    def test_trace_logger_produces_all_sections(self):
        """回溯日志应包含全部关键章节."""
        profile = ProfileSheet(
            profile_id="P-TEST-004", rm_name="张经理", client_name="陈客户",
            risk_level=RiskLevel.R3, amount=500000, horizon=Horizon.MEDIUM,
            goal="资产增值", liquidity="低", investor_type="普通投资者",
        )
        adapter = EastMoneyAdapter()
        pipeline = Pipeline(adapter)
        artifact, verdict = pipeline.run(profile)

        with tempfile.TemporaryDirectory() as tmpdir:
            pipeline.tracer.generate(tmpdir)
            log_path = os.path.join(tmpdir, "回溯日志.md")
            assert os.path.exists(log_path)
            content = open(log_path, encoding="utf-8").read()
            assert "数据溯源表" in content
            assert "过滤日志" in content
            assert "打分明细" in content
            assert "合规校验" in content

    def test_profile_sheet_yaml_roundtrip(self):
        """画像表 YAML 解析后校验通过."""
        yaml_str = """
profile_id: "P-TEST-005"
rm_name: "张经理"
client_name: "李客户"
risk_level: "R3"
amount: 500000
horizon: "中期"
goal: "资产增值"
liquidity: "低"
constraints: []
investor_type: "普通投资者"
"""
        ps = parse_profile_sheet_yaml(yaml_str)
        errors = validate_profile_sheet(ps)
        assert len(errors) == 0

    def test_constraint_filtering_end_to_end(self):
        """客户禁投军工 → 推荐列表中无军工产品."""
        profile = ProfileSheet(
            profile_id="P-TEST-006", rm_name="张经理", client_name="孙客户",
            risk_level=RiskLevel.R3, amount=500000, horizon=Horizon.MEDIUM,
            goal="资产增值", liquidity="低",
            constraints=["不投军工"], investor_type="普通投资者",
        )
        adapter = EastMoneyAdapter()
        pipeline = Pipeline(adapter)
        artifact, verdict = pipeline.run(profile)

        for rec in artifact.recommendations:
            industry = rec.get("industry", "")
            assert "军工" not in industry, (
                f"不应含军工产品: {rec.get('name')}"
            )
