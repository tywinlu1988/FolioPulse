"""适当性校验引擎 —— 推荐管道 Step 3/质检门禁."""

from datetime import datetime
from typing import List
from src.path_sheet import (
    ProfileSheet, RecommendArtifact, QAVerdict, Verdict, RiskLevel
)
from src.filter_engine import RISK_MATCH_MATRIX, TYPE_ALIAS


PROHIBITED_LANGUAGE = [
    "保本", "稳赚", "无风险", "绝对收益", "保证收益", "包赚不赔",
]


class SuitabilityValidator:
    """适当性校验引擎.

    对推荐制品执行 5 项门禁校验，输出质检判定。
    风险匹配规则与 filter_engine 共享同一矩阵（单一实现）。
    """

    def validate(
        self, artifact: RecommendArtifact, profile: ProfileSheet
    ) -> QAVerdict:
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

    def _check_risk_match(self, artifact, profile) -> dict:
        """GATE_RISK_MATCH: 风险等级匹配（与 filter_engine 共享矩阵）."""
        matrix = RISK_MATCH_MATRIX.get(profile.risk_level)
        if matrix is None:
            return {"gate": "风险等级匹配", "status": "fail",
                    "detail": f"客户风险等级无效: {profile.risk_level}"}
        for rec in artifact.recommendations:
            product_risk_raw = rec.get("risk_level", "")
            try:
                product_risk = RiskLevel(product_risk_raw)
            except ValueError:
                return {"gate": "风险等级匹配", "status": "fail",
                        "detail": f"产品{rec.get('name','')}风险等级无法识别: {product_risk_raw}"}
            if product_risk in matrix["prohibited"]:
                return {"gate": "风险等级匹配", "status": "fail",
                        "detail": f"产品{product_risk.value}超出客户{profile.risk_level.value}承受范围"}
            if product_risk in matrix["with_warning"]:
                return {"gate": "风险等级匹配", "status": "warn",
                        "detail": f"产品{product_risk.value}跨级匹配客户{profile.risk_level.value}"}
        return {"gate": "风险等级匹配", "status": "pass", "detail": "全部推荐产品风险等级匹配"}

    def _check_product_type_access(self, artifact, profile) -> dict:
        """GATE_PRODUCT_TYPE: 产品类型准入."""
        if profile.investor_type == "普通投资者":
            for rec in artifact.recommendations:
                ptype = rec.get("type", "")
                if ptype in ("reit", "qdii_fund"):
                    return {"gate": "产品类型准入", "status": "fail",
                            "detail": f"普通投资者不得参与{ptype}"}
        return {"gate": "产品类型准入", "status": "pass", "detail": "投资者类型满足准入要求"}

    def _check_constraints(self, artifact, profile) -> dict:
        """GATE_CONSTRAINT: 客户约束匹配（中英文映射）."""
        for rec in artifact.recommendations:
            industry = rec.get("industry", "")
            ptype = rec.get("type", "").lower()
            for constraint in profile.constraints:
                if constraint.startswith("不投") or constraint.startswith("禁投"):
                    keyword = constraint[2:]
                    if keyword in industry:
                        return {"gate": "客户约束匹配", "status": "fail",
                                "detail": f"产品{rec.get('name','')}违反客户约束: {constraint}"}
                    alias = TYPE_ALIAS.get(keyword.lower(), keyword.lower())
                    if alias in ptype or keyword.lower() in ptype:
                        return {"gate": "客户约束匹配", "status": "fail",
                                "detail": f"产品{rec.get('name','')}违反客户约束: {constraint}"}
                    if alias == "fund" and "fund" in ptype:
                        return {"gate": "客户约束匹配", "status": "fail",
                                "detail": f"产品{rec.get('name','')}违反客户约束: {constraint}"}
        return {"gate": "客户约束匹配", "status": "pass", "detail": "无约束冲突"}

    def _check_min_amount(self, artifact, profile) -> dict:
        """GATE_AMOUNT_MIN: 起投金额."""
        for rec in artifact.recommendations:
            min_amount = rec.get("min_amount", 0)
            if min_amount > profile.amount:
                return {"gate": "起投金额", "status": "warn",
                        "detail": f"产品{rec.get('name','')}起投{min_amount}超客户预算{profile.amount}"}
        return {"gate": "起投金额", "status": "pass", "detail": "起投金额满足要求"}

    def _check_horizon_match(self, artifact, profile) -> dict:
        """GATE_HORIZON_MATCH: 期限匹配."""
        horizon_max = {"短期": 12, "中期": 36, "长期": float("inf")}
        max_months = horizon_max.get(profile.horizon.value, 36)
        for rec in artifact.recommendations:
            lock = rec.get("lock_period_months", 0)
            if lock > max_months:
                return {"gate": "期限匹配", "status": "warn",
                        "detail": f"产品{rec.get('name','')}锁定期{lock}月超客户期限"}
        return {"gate": "期限匹配", "status": "pass", "detail": "期限匹配"}
