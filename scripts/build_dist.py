"""构建脚本 — 将 dev/ 目录组装为可分发的发布包.

用法: python scripts/build_dist.py [version]

输出: version/v{version}-release/
"""

import os
import sys
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def build(version: str = "0.1.0") -> Path:
    """组装发布包."""
    dist_dir = ROOT / "version" / f"v{version}-release"
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    dist_dir.mkdir(parents=True, exist_ok=True)

    # 复制引擎文档（跳过 audits）
    engine_src = ROOT / "dev" / "engine"
    engine_dst = dist_dir / "engine"
    engine_dst.mkdir(exist_ok=True)
    for f in engine_src.iterdir():
        if f.is_file() and f.suffix == ".md":
            shutil.copy2(f, engine_dst / f.name)

    # 复制模板
    templates_src = ROOT / "dev" / "templates"
    templates_dst = dist_dir / "templates"
    templates_dst.mkdir(exist_ok=True)
    for f in templates_src.iterdir():
        if f.is_file():
            shutil.copy2(f, templates_dst / f.name)

    # 复制技能
    skills_src = ROOT / "dev" / ".claude" / "skills"
    skills_dst = dist_dir / ".claude" / "skills"
    skills_dst.mkdir(parents=True, exist_ok=True)
    for skill_dir in skills_src.iterdir():
        if skill_dir.is_dir():
            dst = skills_dst / skill_dir.name
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(skill_dir, dst)

    # 复制画像
    profiles_src = ROOT / "dev" / "profiles"
    profiles_dst = dist_dir / "profiles"
    profiles_dst.mkdir(exist_ok=True)
    for f in profiles_src.iterdir():
        if f.is_file():
            shutil.copy2(f, profiles_dst / f.name)

    # 复制 Python 源码
    src_src = ROOT / "src"
    src_dst = dist_dir / "src"
    if src_dst.exists():
        shutil.rmtree(src_dst)
    shutil.copytree(src_src, src_dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # 复制顶层文件
    for name in ["AGENTS.md", "README.md", "LICENSE", "pyproject.toml", "plugin.json"]:
        src_file = ROOT / name
        if src_file.exists():
            shutil.copy2(src_file, dist_dir / name)

    print(f"发布包已生成: {dist_dir}")
    return dist_dir


if __name__ == "__main__":
    version = sys.argv[1] if len(sys.argv) > 1 else "0.1.0"
    build(version)
