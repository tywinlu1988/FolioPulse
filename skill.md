---
name: foliopulse
description: >
  Investment portfolio tracking, analysis, and monitoring skill.
  Track holdings across multiple asset classes (stocks, crypto, ETFs, funds),
  analyze portfolio allocation, calculate returns, monitor risk metrics,
  and generate portfolio health reports. Integrates with market data APIs
  for real-time valuations.
triggers:
  - portfolio
  - holdings
  - investment
  - stock tracking
  - asset allocation
  - portfolio analysis
  - returns calculation
  - risk metrics
  - foliopulse
  - 投资组合
  - 持仓
  - 资产配置
---

# FolioPulse — Investment Portfolio Intelligence

Track, analyze, and optimize investment portfolios with real-time market data.

## Overview

FolioPulse is an investment portfolio tracking skill that helps users:
- **Track** holdings across stocks, ETFs, crypto, mutual funds, and cash
- **Analyze** asset allocation, sector exposure, and geographic distribution
- **Monitor** portfolio performance with time-weighted and money-weighted returns
- **Alert** on significant price movements, allocation drift, and risk threshold breaches
- **Report** portfolio health with summarized dashboards and detailed breakdowns

## Prerequisites

- Market data API keys (e.g., Alpha Vantage, Yahoo Finance, or similar)
- Portfolio data in structured format (JSON, CSV, or manual entry)

## Usage

### 1. Load Portfolio

Tell FolioPulse about your holdings. Accepts:

```
"Load my portfolio from portfolio.json"
"Add 100 shares of AAPL at $175.30"
"Import my holdings CSV"
```

### 2. Analyze Allocation

```
"Analyze my portfolio allocation"
"Show sector breakdown"
"What's my US vs international exposure?"
```

### 3. Calculate Returns

```
"Calculate my portfolio returns YTD"
"Show total return since inception"
"Compare my returns against S&P 500"
```

### 4. Risk Assessment

```
"Assess my portfolio risk"
"Calculate Sharpe ratio for my holdings"
"Show value-at-risk (VaR)"
"Check correlation between my positions"
```

### 5. Generate Reports

```
"Generate a portfolio health report"
"Summarize my portfolio in a dashboard"
"Export portfolio snapshot to PDF"
```

### 6. Alerts & Monitoring

```
"Alert me if any position drops 5% in a day"
"Warn when my tech allocation exceeds 40%"
"Notify on dividend dates for my holdings"
```

## Configuration

Create a `foliopulse.config.json` in your project root:

```json
{
  "data_source": "yahoo_finance",
  "api_keys": {
    "alpha_vantage": "YOUR_KEY_HERE"
  },
  "base_currency": "USD",
  "benchmark": "^GSPC",
  "alert_thresholds": {
    "single_position_drop_pct": 5.0,
    "allocation_drift_pct": 5.0
  },
  "risk_free_rate": 0.05
}
```

## Portfolio Data Format

```json
{
  "name": "My Portfolio",
  "inception_date": "2024-01-15",
  "holdings": [
    {
      "symbol": "AAPL",
      "shares": 100,
      "avg_cost": 175.30,
      "purchase_date": "2024-03-10",
      "asset_class": "stock",
      "sector": "technology",
      "region": "US"
    }
  ],
  "cash": 25000.00,
  "transactions": []
}
```

## Output Conventions

- Currency amounts formatted with 2 decimal places and currency symbol
- Percentages rounded to 2 decimal places
- Color-coded indicators: 🟢 positive, 🔴 negative, 🟡 neutral
- Tables use markdown format for readability
- Charts described in text; implementation left to user's environment

## Limitations

- Not a financial advisor; provides data analysis only
- Market data accuracy depends on configured API provider
- Does not execute trades or connect to brokerage accounts
- Tax implications not calculated
