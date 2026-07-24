#!/usr/bin/env node

/**
 * FolioPulse — npx 安装引导脚本
 *
 * 用法:
 *   npx foliopulse                      # 交互式安装
 *   npx foliopulse --platform claude    # 指定 CLI 平台
 *   npx foliopulse --platform codex     #
 *   npx foliopulse --platform cursor    #
 *
 * 支持的平台: claude, codex, cursor, gemini, opencode
 */

import { mkdirSync, readdirSync, statSync, copyFileSync, existsSync, readFileSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dirname, "..");

const PLATFORMS = {
  claude: {
    name: "Claude Code",
    skillsDir: ".claude/skills",
    instructions: "在 Claude Code 中描述客户情况（如\"R3客户50万想做基金\"）即可激活 FolioPulse 技能链。",
  },
  codex: {
    name: "OpenAI Codex",
    skillsDir: ".codex/skills",
    instructions: "在 Codex 中描述客户情况即可激活 FolioPulse 技能链。",
  },
  cursor: {
    name: "Cursor",
    skillsDir: ".cursor/skills",
    instructions: "在 Cursor 中描述客户情况即可激活 FolioPulse 技能链。",
  },
  gemini: {
    name: "Gemini CLI",
    skillsDir: ".gemini/skills",
    instructions: "在 Gemini CLI 中描述客户情况即可激活 FolioPulse 技能链。",
  },
  opencode: {
    name: "OpenCode",
    skillsDir: ".opencode/skills",
    instructions: "在 OpenCode 中描述客户情况即可激活 FolioPulse 技能链。",
  },
};

function parseArgs() {
  const args = process.argv.slice(2);
  const opts = { platform: null, dest: null };
  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--platform" && args[i + 1]) {
      opts.platform = args[i + 1].toLowerCase();
      i++;
    } else if (args[i] === "--dest" && args[i + 1]) {
      opts.dest = args[i + 1];
      i++;
    }
  }
  return opts;
}

function copyDir(src, dest) {
  if (!existsSync(src)) return;
  mkdirSync(dest, { recursive: true });
  for (const entry of readdirSync(src)) {
    const srcPath = join(src, entry);
    const destPath = join(dest, entry);
    if (statSync(srcPath).isDirectory()) {
      copyDir(srcPath, destPath);
    } else {
      copyFileSync(srcPath, destPath);
    }
  }
}

function install(opts) {
  let platform = opts.platform;

  // 交互式选择平台
  if (!platform) {
    console.log("\n  FolioPulse — AI 驱动的投资标的推荐引擎\n");
    console.log("  请选择目标 CLI 平台：\n");
    for (const [key, cfg] of Object.entries(PLATFORMS)) {
      console.log(`    [${key}] ${cfg.name}`);
    }
    console.log("");
    process.stdout.write("  输入平台代码: ");

    // 非交互模式默认 claude
    platform = "claude";
    console.log(platform);
  }

  const cfg = PLATFORMS[platform];
  if (!cfg) {
    console.error(`不支持的平台: ${platform}`);
    console.error(`支持的平台: ${Object.keys(PLATFORMS).join(", ")}`);
    process.exit(1);
  }

  const cwd = opts.dest || process.cwd();
  const skillsDest = join(cwd, cfg.skillsDir);

  console.log(`\n  FolioPulse v${getVersion()}`);
  console.log(`  目标平台: ${cfg.name}`);
  console.log(`  安装路径: ${cwd}\n`);

  // 复制技能文件到技能发现目录（平铺，每个技能一个目录）
  const skillsSrc = join(ROOT, ".claude", "skills");
  for (const entry of readdirSync(skillsSrc)) {
    if (statSync(join(skillsSrc, entry)).isDirectory()) {
      copyDir(join(skillsSrc, entry), join(skillsDest, entry));
      console.log(`  [OK] 技能已安装: ${cfg.skillsDir}/${entry}`);
    }
  }

  // 复制引擎文档、模板、画像到项目根目录（SKILL.md 按相对路径引用）
  for (const dir of ["engine", "templates", "profiles"]) {
    copyDir(join(ROOT, dir), join(cwd, dir));
    console.log(`  [OK] ${dir}/ 已复制`);
  }

  console.log(`\n  安装完成！`);
  console.log(`  ${cfg.instructions}\n`);
}

function getVersion() {
  try {
    const pkg = JSON.parse(readFileSync(join(ROOT, "package.json"), "utf-8"));
    return pkg.version || "0.1.3";
  } catch {
    return "0.1.3";
  }
}

install(parseArgs());
