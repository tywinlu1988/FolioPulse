"""一致性检查工具 — 校验引擎文档与代码之间的完整性.

用法: python scripts/consistency_check.py

检查项:
1. 所有引擎文档存在且可读
2. 引擎文档中的 YAML 块可正确解析
3. 风险匹配矩阵覆盖全部 R1-R5
4. SKILL.md frontmatter 仅含 name 和 description
5. 模板文件不含示例数据
"""

import sys
import re
import yaml
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
ENGINE_DIR = ROOT / "engine"
SKILLS_DIR = ROOT / ".claude" / "skills"
TEMPLATES_DIR = ROOT / "templates"

REQUIRED_ENGINE_DOCS = [
    "engine-overview.md", "product-taxonomy.md", "scoring-framework.md",
    "suitability-rules.md", "filter-rules.md", "dual-track-methodology.md",
    "output-layered.md", "data-architecture.md",
]


def check_engine_docs_exist():
    """检查所有引擎文档存在."""
    errors = []
    for doc in REQUIRED_ENGINE_DOCS:
        path = ENGINE_DIR / doc
        if not path.exists():
            errors.append(f"引擎文档缺失: {doc}")
    return errors


def check_yaml_blocks_parseable():
    """检查引擎文档中的 YAML 块可解析."""
    errors = []
    for doc in REQUIRED_ENGINE_DOCS:
        path = ENGINE_DIR / doc
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        blocks = re.findall(r"```yaml\n(.*?)```", text, re.DOTALL)
        for i, block in enumerate(blocks):
            try:
                yaml.safe_load(block)
            except yaml.YAMLError as e:
                errors.append(f"{doc} 第{i+1}个YAML块解析失败: {e}")
    return errors


def check_risk_matrix_complete():
    """检查风险匹配矩阵覆盖全部 R1-R5."""
    path = ENGINE_DIR / "suitability-rules.md"
    if not path.exists():
        return []
    text = path.read_text(encoding="utf-8")
    blocks = re.findall(r"```yaml\n(.*?)```", text, re.DOTALL)
    for block in blocks:
        data = yaml.safe_load(block)
        if isinstance(data, dict) and "risk_match_matrix" in data:
            matrix = data["risk_match_matrix"]
            for level in ["R1", "R2", "R3", "R4", "R5"]:
                if level not in matrix:
                    return [f"风险匹配矩阵缺失: {level}"]
            return []
    return []


def check_skill_frontmatter():
    """检查 SKILL.md frontmatter 仅含 name 和 description."""
    errors = []
    allowed_keys = {"name", "description"}
    for skill_dir in SKILLS_DIR.iterdir():
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            errors.append(f"SKILL.md 缺失: {skill_dir.name}")
            continue
        text = skill_md.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)---", text, re.DOTALL)
        if not m:
            errors.append(f"{skill_dir.name}/SKILL.md 无 YAML frontmatter")
            continue
        try:
            fm = yaml.safe_load(m.group(1))
            extra = set(fm.keys()) - allowed_keys
            if extra:
                errors.append(f"{skill_dir.name}/SKILL.md 多余字段: {extra}")
        except yaml.YAMLError as e:
            errors.append(f"{skill_dir.name}/SKILL.md frontmatter 解析失败: {e}")
    return errors


def check_templates_no_sample_data():
    """检查模板不含硬编码的示例数据."""
    errors = []
    suspicious_patterns = [
        (r"贵州茅台", "示例产品名"),
        (r"500000", "示例金额"),
        (r"张经理", "示例人名"),
        (r"李客户", "示例人名"),
    ]
    for tmpl in TEMPLATES_DIR.glob("*.md"):
        text = tmpl.read_text(encoding="utf-8")
        for pattern, desc in suspicious_patterns:
            for i, line in enumerate(text.split("\n"), 1):
                if re.search(pattern, line):
                    errors.append(f"{tmpl.name}:{i} 疑似示例数据 '{desc}'")
    return errors


def main():
    all_errors = []
    all_errors.extend(check_engine_docs_exist())
    all_errors.extend(check_yaml_blocks_parseable())
    all_errors.extend(check_risk_matrix_complete())
    all_errors.extend(check_skill_frontmatter())
    all_errors.extend(check_templates_no_sample_data())

    if all_errors:
        print(f"一致性检查: {len(all_errors)} 个问题")
        for e in all_errors:
            print(f"  [FAIL] {e}")
        return 1
    else:
        print("一致性检查: 全部通过 [OK]")
        return 0


if __name__ == "__main__":
    sys.exit(main())
