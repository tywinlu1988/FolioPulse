# 数据架构

> 版本：v0.3.0 | 数据源分层与 Mode A/B 定义

## 数据源分层

```yaml
data_layers:
  L1:
    name: 行情数据
    content: 股价、净值、涨跌幅、成交量
    adapter: eastmoney
    freshness: 实时/延迟15分钟
    mode: [A]

  L2:
    name: 基本面数据
    content: PE/PB/ROE/财报/营收增速
    adapter: eastmoney
    freshness: T+1
    mode: [A]

  L3:
    name: 基金详情
    content: 持仓/规模/费率/基金经理/业绩
    adapter: tiantian
    freshness: T+1 ~ T+7
    mode: [A]

  L4:
    name: 理财产品数据
    content: 预期收益/风险等级/历史兑付率
    adapter: wind
    freshness: 按发行周期
    mode: [B]

  L5:
    name: 舆情数据
    content: 新闻/研报/公告情绪
    adapter: eastmoney
    freshness: 实时
    mode: [A]
```

## Mode A / Mode B

```yaml
modes:
  A:
    name: 公开数据模式
    description: 仅使用免费公开数据源
    adapters: [eastmoney, tiantian]
    is_default: true

  B:
    name: 外部数据模式
    description: 用户显式提供外部数据源
    adapters: [wind]
    activation: 用户必须主动指定数据源
    guardrail: QA 校验 Mode B 数据源是否经用户显式授权
```

## 适配器接口规范

```yaml
adapter_interface:
  methods:
    - name: fetch_product_list
      input: "product_type: str"
      output: "List[Product]"
      description: 按产品类型拉取产品列表

    - name: fetch_product_detail
      input: "product_code: str"
      output: "ProductDetail"
      description: 拉取单只产品详情

    - name: fetch_financial_data
      input: "product_code: str, data_points: List[str]"
      output: "Dict[str, float]"
      description: 拉取指定数据点

    - name: fetch_market_signal
      input: "product_code: str, signal_ids: List[str]"
      output: "Dict[str, float]"
      description: 拉取市场信号数据

    - name: check_health
      input: "none"
      output: "bool"
      description: 检查适配器可用性
```
