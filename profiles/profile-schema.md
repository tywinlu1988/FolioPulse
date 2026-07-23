# 客户画像模板字段说明

> 版本：v0.1.0

## 字段定义

| 字段 | 类型 | 必填 | 可选值/说明 |
|------|------|------|-----------|
| profile_id | string | 是 | 格式 P-YYYYMMDD-NNN |
| rm_name | string | 是 | 客户经理姓名 |
| client_name | string | 是 | 客户姓名 |
| risk_level | string | 是 | R1/R2/R3/R4/R5 |
| amount | number | 是 | 投资金额（元），> 0 |
| horizon | string | 是 | 短期/中期/长期 |
| goal | string | 是 | 资产增值/稳健收益/养老规划/子女教育/流动性管理/其他 |
| liquidity | string | 是 | 高/中/低 |
| constraints | list | 否 | 字符串列表，如 ["不投军工","偏好消费"] |
| investor_type | string | 是 | 普通投资者/合格投资者 |
| path_id | string | 否 | 默认 WP-REC-01 |
| notes | string | 否 | 客户经理备注 |
