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
    destDir: ".claude/skills/foliopulse",
    instructions: "在 Claude Code 中输入 /foliopulse 或描述客户情况即可激活技能。",
  },
  codex: {
    name: "OpenAI Codex",
    destDir: ".codex/skills/foliopulse",
    instructions: "在 Codex 中引用 foliopulse 技能目录即可使用。",
  },
  cursor: {
    name: "Cursor",
    destDir: ".cursor/skills/foliopulse",
    instructions: "在 Cursor 中加载 .cursor/skills/foliopulse 目录。",
  },
  gemini: {
    name: "Gemini CLI",
    destDir: ".gemini/skills/foliopulse",
    instructions: "在 Gemini CLI 中加载技能目录。",
  },
  opencode: {
    name: "OpenCode",
    destDir: ".opencode/skills/foliopulse",
    instructions: "在 OpenCode 中加载技能目录。",
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
  const destBase = join(cwd, cfg.destDir);

  console.log(`\n  FolioPulse v${getVersion()}`);
  console.log(`  目标平台: ${cfg.name}`);
  console.log(`  安装路径: ${destBase}\n`);

  // 复制技能文件
  const skillsSrc = join(ROOT, "dev", ".claude", "skills");
  copyDir(skillsSrc, destBase);
  console.log("  [OK] 技能文件已复制");

  // 复制引擎文档
  const engineSrc = join(ROOT, "dev", "engine");
  const engineDest = join(cwd, cfg.destDir, "engine");
  copyDir(engineSrc, engineDest);
  console.log("  [OK] 引擎文档已复制");

  // 复制模板
  const templatesSrc = join(ROOT, "dev", "templates");
  const templatesDest = join(cwd, cfg.destDir, "templates");
  copyDir(templatesSrc, templatesDest);
  console.log("  [OK] 模板已复制");

  // 复制画像
  const profilesSrc = join(ROOT, "dev", "profiles");
  const profilesDest = join(cwd, cfg.destDir, "profiles");
  copyDir(profilesSrc, profilesDest);
  console.log("  [OK] 画像模板已复制");

  console.log(`\n  安装完成！`);
  console.log(`  ${cfg.instructions}\n`);
}

function getVersion() {
  try {
    const pkg = JSON.parse(readFileSync(join(ROOT, "package.json"), "utf-8"));
    return pkg.version || "0.1.1";
  } catch {
    return "0.1.1";
  }
}

install(parseArgs());
