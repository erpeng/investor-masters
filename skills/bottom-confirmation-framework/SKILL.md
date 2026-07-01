---
name: bottom-confirmation-framework
description: Use when the user asks whether an asset, stock, company, ETF, commodity, sector, or market has bottomed, whether sell pressure has been released, or requests 底部判断, 底部确认, 卖压释放, 恐慌抛售, ETF赎回, 杠杆平仓, 机构减仓, 批价, 库存, 沽空, 南向, 北向, or price-action confirmation analysis.
---

# Bottom Confirmation Framework

## Core Principle

Judge bottoms as a sell-pressure and absorption problem, not as a lowest-price prediction. The output should answer: who is still selling, whether forced selling is fading, whether bad news is being absorbed, and what would confirm or invalidate the bottom.

Default to Chinese. For current market facts, browse or use live data tools; price, holdings, redemptions, short selling, futures positioning, channel prices, and inventory signals are time-sensitive.

## Workflow

1. Identify the asset type and load `references/asset-maps.md` for the matching indicators. If the user asks for a pure framework without data, skip data collection and output the relevant observation checklist.
2. Load `references/data-checklist.md` before collecting data. Prefer official filings, exchanges, regulators, fund issuers, and company announcements; mark media/channel quotes as weak evidence.
3. For a concrete asset or company, run the default report mode using `references/report-template.md`. Put the conclusion card first.
4. Score bottom confirmation on a 0-100 scale, but let judgment override mechanical averages:
   - `<35`: sell pressure not released.
   - `35-55`: left-side observation zone.
   - `56-70`: observation zone, partial release.
   - `71-84`: right-side confirmation forming.
   - `85+`: sell pressure mostly released, confirmation strong.
5. Save concrete reports to `~/Documents/notes/YYYY-MM-DD-标的名称底部判断报告.md`. Do not save if the user only asks for a short answer or a framework checklist.

## Required Report Behavior

- Start with a short conclusion card: confirmation score, current stage, strongest positive signals, strongest unresolved risks, and one-sentence verdict.
- Separate `price sell pressure` from `business/fundamental pressure`; cheap price alone is not a confirmed bottom.
- Include dates on every current data point. If data is unavailable, state `未取得` and explain what would be needed.
- Adapt the channel/proxy metric to the asset: liquor uses batch price, Pop Mart uses resale premium/search/new-product heat, gold uses ETF holdings and CFTC futures positioning.
- End with confirmation conditions, failure conditions, and a tracking checklist by frequency: daily/weekly/monthly/quarterly as appropriate.
- Avoid buy/sell recommendations. The output is a bottom-confirmation diagnosis, not investment advice.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Treating a large drawdown as a bottom | Require sell-pressure exhaustion plus price absorption. |
| Mixing official data and media quotes | Grade evidence and label weak channel data clearly. |
| Using one-day rebound as confirmation | Require follow-through, repeated support, or confirming high-frequency data. |
| Ignoring asset-specific proxies | Load the asset map and replace irrelevant metrics. |
| Writing only narrative | Include tables for key data, current status, and tracking checklist. |

