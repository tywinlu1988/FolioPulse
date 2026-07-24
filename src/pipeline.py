"""管道编排器 —— 串联过滤→打分→校验全流程."""

from datetime import datetime
from typing import Dict, List, Tuple, Optional
from src.adapters.base import BaseAdapter
from src.path_sheet import ProfileSheet, RecommendArtifact, QAVerdict
from src.filter_engine import FilterEngine
from src.composite_scorer import CompositeScorer
from src.suitability_validator import SuitabilityValidator
from src.trace_logger import TraceLogger
from src.dual_track import apply_dual_track


class Pipeline:
    """推荐管道编排器.

    串联四步管道：拉取产品 → 过滤 → 打分 → 校验，产出推荐制品和质检判定。
    """

    def __init__(self, adapter: BaseAdapter):
        self.adapter = adapter
        self.filter_engine = FilterEngine()
        self.scorer = CompositeScorer()
        self.validator = SuitabilityValidator()
        self.tracer = TraceLogger()

    def run(
        self, profile: ProfileSheet, output_dir: Optional[str] = None
    ) -> Tuple[RecommendArtifact, QAVerdict]:
        """执行完整推荐管道.

        Args:
            profile: 客户画像表
            output_dir: 若提供，管道结束后将回溯日志落盘到该目录
        """
        self.tracer.set_input(profile)
        self.tracer.engine_metadata["mode"] = profile.mode.value

        # Step 1: 拉取产品（按画像适用的产品类型）
        all_products = []
        for ptype in self._get_applicable_types(profile):
            all_products.extend(self.adapter.fetch_product_list(ptype))

        # Step 2: 过滤
        passed, rejected = self.filter_engine.apply_filters(all_products, profile)
        self.tracer.log_filter(passed, rejected)

        # Step 3: 打分
        scored = self.scorer.score(passed, profile, self.adapter)
        self.tracer.log_score(scored)

        # Step 4: 双轨验证（轨 A 基本面 × 轨 B 市场信号）
        validated = apply_dual_track(scored, self.adapter)
        self.tracer.log_dual_track(validated)

        # Step 5: 排序（置信度 <50% 的产品标注"数据不足"，不参与排名）
        rankable = [p for p in validated if p.get("confidence", 0) >= 50]
        excluded = [
            {**p, "excluded_from_ranking": True}
            for p in validated if p.get("confidence", 0) < 50
        ]
        ranked = sorted(
            rankable,
            key=lambda x: x.get("composite_score", 0),
            reverse=True,
        ) + excluded

        artifact = RecommendArtifact(
            path_id=profile.path_id,
            profile_id=profile.profile_id,
            mode=profile.mode,
            recommendations=ranked,
            portfolio_summary=self._build_portfolio_summary(ranked),
            data_completeness=self._build_completeness(ranked),
            generated_at=datetime.now().isoformat(),
        )

        # Step 5: 校验
        verdict = self.validator.validate(artifact, profile)
        self.tracer.log_compliance(verdict.gate_results)

        if output_dir:
            self.tracer.generate(output_dir)

        return artifact, verdict

    def _get_applicable_types(self, profile: ProfileSheet) -> List[str]:
        """根据客户风险等级返回适用产品类型."""
        risk = profile.risk_level
        all_types = ["stock", "equity_fund", "mixed_fund", "bond_fund",
                     "index_fund", "etf", "qdii_fund", "reit",
                     "convertible_bond", "wealth_mgmt_product"]
        # R1 仅债券基金和理财产品
        if risk.value == "R1":
            return ["bond_fund", "wealth_mgmt_product"]
        # R2 加上混合型、指数型、ETF、可转债
        if risk.value == "R2":
            return ["bond_fund", "mixed_fund", "index_fund", "etf",
                    "convertible_bond", "wealth_mgmt_product"]
        # R3-R5 全部
        return all_types

    def _build_portfolio_summary(self, ranked: List[Dict]) -> Dict:
        """构建组合概览."""
        if not ranked:
            return {"asset_allocation": [], "risk_exposure": {}}
        # 简单按类型统计
        type_count: Dict[str, int] = {}
        for r in ranked:
            ptype = r.get("type", "unknown")
            type_count[ptype] = type_count.get(ptype, 0) + 1
        total = len(ranked)
        allocation = [
            {"type": t, "ratio": round(c / total, 2)}
            for t, c in type_count.items()
        ]
        return {
            "asset_allocation": allocation,
            "risk_exposure": {
                "concentration_industry": "待计算",
                "concentration_rating": "待计算",
            },
        }

    def _build_completeness(self, ranked: List[Dict]) -> Dict:
        """构建数据完整度报告."""
        if not ranked:
            return {"density_pct": 0, "confidence": "低", "data_gaps": ["无产品数据"]}
        avg_confidence = sum(r.get("confidence", 0) for r in ranked) / len(ranked)
        if avg_confidence >= 80:
            label = "高"
        elif avg_confidence >= 50:
            label = "中"
        else:
            label = "低"
        return {
            "density_pct": round(avg_confidence, 1),
            "confidence": label,
            "data_gaps": [],
        }
