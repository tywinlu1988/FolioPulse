"""回溯日志模块 —— 过程透视镜.

记录推荐全过程的每个决策点，用于防过拟合、防幻觉、可复盘。
"""

import os
from datetime import datetime
from typing import Any, Dict, List
from src.path_sheet import ProfileSheet, QAVerdict


class TraceLogger:
    """回溯日志记录器.

    维护 9 个内部列表，generate 方法生成完整回溯日志.md。
    """

    def __init__(self):
        self.input_snapshot: Dict[str, Any] = {}
        self.data_trace: List[Dict] = []
        self.filter_log_passed: List[Dict] = []
        self.filter_log_rejected: List[Dict] = []
        self.score_detail: List[Dict] = []
        self.dual_track: List[Dict] = []
        self.compliance_checks: List[Dict] = []
        self.rm_interventions: List[Dict] = []
        self.output_manifest: List[Dict] = []
        self.engine_metadata: Dict[str, Any] = {
            "engine_version": "0.2.0",
            "mode": "A",
            "adapter_call_count": 0,
            "llm_call_count": 0,
            "start_time": datetime.now().isoformat(),
        }

    def set_input(self, profile: ProfileSheet) -> None:
        """记录输入快照."""
        self.input_snapshot = {
            "profile_id": profile.profile_id,
            "risk_level": profile.risk_level.value,
            "amount": profile.amount,
            "horizon": profile.horizon.value,
            "goal": profile.goal,
            "liquidity": profile.liquidity,
            "investor_type": profile.investor_type,
            "constraints": profile.constraints,
            "path_id": profile.path_id,
        }

    def log_data_source(self, data_point: str, value: Any, adapter: str,
                        fetch_time: str, cached: bool = False) -> None:
        """记录数据溯源."""
        self.data_trace.append({
            "data_point": data_point, "value": value, "adapter": adapter,
            "fetch_time": fetch_time, "cached": cached,
        })

    def log_filter(self, passed: List[Dict], rejected: List[Dict]) -> None:
        """记录过滤结果."""
        self.filter_log_passed = [{
            "code": p.get("code", ""), "name": p.get("name", ""),
            "type": p.get("type", ""),
        } for p in passed]
        self.filter_log_rejected = [{
            "code": r.get("code", ""), "name": r.get("name", ""),
            "reason": r.get("reject_reason", ""),
        } for r in rejected]

    def log_score(self, scored: List[Dict]) -> None:
        """记录打分明细."""
        for p in scored:
            for fid, fs in p.get("factor_scores", {}).items():
                self.score_detail.append({
                    "product_code": p.get("code", ""),
                    "factor_id": fid,
                    "raw": fs.get("raw"),
                    "normalized": fs.get("normalized"),
                    "weight": fs.get("weight"),
                    "weighted": fs.get("weighted"),
                })

    def log_dual_track(self, validated: List[Dict]) -> None:
        """记录双轨验证结果."""
        for p in validated:
            self.dual_track.append({
                "code": p.get("code", ""),
                "track_a": p.get("track_a", "—"),
                "track_b": p.get("track_b", "—"),
                "conflict": p.get("dual_track_note", "—"),
                "final": p.get("composite_score", ""),
            })

    def log_compliance(self, gate_results: List[Dict]) -> None:
        """记录合规校验."""
        self.compliance_checks = gate_results

    def log_rm_action(self, action: str, target: str,
                      before: Any = None, after: Any = None) -> None:
        """记录客户经理干预."""
        self.rm_interventions.append({
            "time": datetime.now().isoformat(),
            "action": action, "target": target,
            "before": str(before) if before is not None else "",
            "after": str(after) if after is not None else "",
        })

    def generate(self, output_dir: str) -> str:
        """生成回溯日志.md，返回文件路径."""
        os.makedirs(output_dir, exist_ok=True)
        now = datetime.now().isoformat()
        lines = [
            f"# 回溯日志 — {self.input_snapshot.get('profile_id', 'UNKNOWN')}",
            "",
            f"> **生成时间**：{now}　|　**引擎版本**：{self.engine_metadata['engine_version']}　|　**数据模式**：{self.engine_metadata['mode']}",
            "",
            "---",
            "",
            "## 一、输入快照",
            "",
            "```yaml",
        ]
        for k, v in self.input_snapshot.items():
            lines.append(f"{k}: {v}")
        lines.extend(["```", "", "## 二、数据溯源表", ""])
        lines.append("| 序号 | 数据点 | 值 | 适配器 | 获取时间 | 是否缓存 |")
        lines.append("|------|--------|---|--------|---------|---------|")
        for i, dt in enumerate(self.data_trace, 1):
            lines.append(
                f"| {i} | {dt['data_point']} | {dt['value']} | "
                f"{dt['adapter']} | {dt['fetch_time']} | {'是' if dt['cached'] else '否'} |"
            )
        lines.extend(["", "## 三、过滤日志", ""])
        lines.append("### 通过的产品")
        lines.append("| 产品代码 | 产品名称 | 类型 |")
        lines.append("|----------|---------|------|")
        for p in self.filter_log_passed:
            lines.append(f"| {p['code']} | {p['name']} | {p['type']} |")
        lines.extend(["", "### 被过滤的产品", ""])
        lines.append("| 产品代码 | 产品名称 | 拒绝原因 |")
        lines.append("|----------|---------|---------|")
        for r in self.filter_log_rejected:
            lines.append(f"| {r['code']} | {r['name']} | {r['reason']} |")
        lines.append(f"| — | — | 被过滤总数：{len(self.filter_log_rejected)} / 通过总数：{len(self.filter_log_passed)} |")
        lines.extend(["", "## 四、打分明细", ""])
        lines.append("| 产品代码 | 因子编号 | 原始值 | 归一化值 | 权重 | 加权分 |")
        lines.append("|----------|---------|--------|---------|------|--------|")
        for s in self.score_detail:
            lines.append(
                f"| {s['product_code']} | {s['factor_id']} | {s['raw']} | "
                f"{s['normalized']} | {s['weight']} | {s['weighted']} |"
            )
        lines.extend(["", "## 五、双轨验证", ""])
        if self.dual_track:
            lines.append("| 产品代码 | 轨 A（基本面） | 轨 B（市场信号） | 冲突标记 | 最终采用 |")
            lines.append("|----------|--------------|----------------|---------|---------|")
            for d in self.dual_track:
                lines.append(
                    f"| {d.get('code','')} | {d.get('track_a','')} | {d.get('track_b','')} | "
                    f"{d.get('conflict','')} | {d.get('final','')} |"
                )
        else:
            lines.append("> 本版本未执行双轨验证（v0.4.0 计划实装）")
        lines.extend(["", "## 六、合规校验", ""])
        lines.append("| 校验项 | 结果 | 详情 |")
        lines.append("|--------|------|------|")
        for c in self.compliance_checks:
            lines.append(f"| {c.get('gate','')} | {c.get('status','')} | {c.get('detail','')} |")
        lines.extend(["", "## 七、客户经理干预记录", ""])
        lines.append("| 时间 | 操作类型 | 对象 | 操作前值 | 操作后值 |")
        lines.append("|------|---------|------|---------|---------|")
        for rm in self.rm_interventions:
            lines.append(
                f"| {rm['time']} | {rm['action']} | {rm['target']} | "
                f"{rm['before']} | {rm['after']} |"
            )
        if not self.rm_interventions:
            lines.append("| — | 无干预记录 | — | — | — |")
        lines.extend(["", "## 八、输出清单", ""])
        lines.append("| 文件名 | 路径 | 生成状态 |")
        lines.append("|--------|------|---------|")
        for o in self.output_manifest:
            status = "OK" if o.get("status") else "FAIL"
            lines.append(f"| {o.get('file','')} | {o.get('path','')} | {status} |")
        lines.extend(["", "## 九、引擎元数据", ""])
        for k, v in self.engine_metadata.items():
            lines.append(f"- **{k}**：{v}")
        lines.append(f"- **总耗时**：—")
        lines.append(f"- **适配器调用次数**：{self.engine_metadata['adapter_call_count']}")
        lines.append(f"- **模型调用次数**：{self.engine_metadata['llm_call_count']}")

        content = "\n".join(lines)
        filepath = os.path.join(output_dir, "回溯日志.md")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        self.output_manifest.append({"file": "回溯日志.md", "path": filepath, "status": True})
        return filepath
