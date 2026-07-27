# 输出分层定义

> 版本：v0.3.0 | L0/L1/L2 输出层级规范

## 三层定义

```yaml
layers:
  L0:
    name: 速配卡
    read_time: 5秒
    audience: 客户经理（CLI 终端）
    content:
      - 推荐产品 Top 5（排名/名称/类型/评分/核心理由）
      - 风险匹配灯号（绿/黄/红）
      - 关键提醒（置信度、数据缺口）
      - 组合配比概览
    format: CLI 表格

  L1:
    name: 推荐列表
    read_time: 5分钟
    audience: 客户经理（内部研究）
    content:
      - 完整排名表 + 每只多维打分
      - 组合风险分析
      - 备选池列表
      - 数据缺口详情
    format: Markdown 文件（本地落盘）

  L2:
    name: 深度报告
    read_time: 15-30分钟
    audience: 客户经理 + 高净值客户
    content:
      - 市场背景概述
      - 资产配置逻辑
      - 每只标的详细分析（基本面+技术面+风险）
      - 风险提示与免责声明
    format: Markdown 文件（本地落盘，可打印）
```

## L0 CLI 模板

```
══════════════════════════════════════════
  FolioPulse 推荐速览
  客户：{client_name} | 风险等级：{risk_level} | 金额：{amount_wan}万元 | 期限：{horizon}
══════════════════════════════════════════

  {risk_match_light} | {qa_verdict} | {confidence_label}

  推荐组合：
  ┌──────┬────────────┬──────┬──────┬──────────┐
  │ 排名  │ 产品名称    │ 类型  │ 评分  │ 核心理由   │
  ├──────┼────────────┼──────┼──────┼──────────┤
  │ {rows}                                     │
  └──────┴────────────┴──────┴──────┴──────────┘

  配置建议：{allocation_summary}

  ⚠ 提醒：{warnings}

  下一步？
  [1] 查看完整推荐列表
  [2] 调整推荐（换产品 / 改配比）
  [3] 确认并生成客户交付物
  [4] 查看备选池
```

## 输出目录结构

```yaml
output_dir:
  pattern: "folio-{date}-{client_name}/"
  files:
    L1:
      - 推荐清单.html
    L2:
      - 标的报告-{product_name}.html
      - 问答清单.html
      - 话术清单.html
      - 配置建议书.html
    trace:
      - 回溯日志.md
```
