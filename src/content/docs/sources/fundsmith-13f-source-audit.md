---
title: "Fundsmith-13f-source-audit"
slug: "sources/fundsmith-13f-source-audit"
description: "13F 季度材料的覆盖责任、证据边界与传播清单。"
---
## 来源定位

原始材料：[SEC｜Fundsmith：2022Q4至2026Q3持仓轨迹](/investor-masters/sources/fundsmith-13f-2026q3/)。责任是 Fundsmith 公开组合行为，报告日为 2026-09-30，核验日为 2026-11-17。结构化快照：`现有资料/data/13f-20261117-batch2/fundsmith.json`；旧方法讨论随同归档，原始 SEC 文件保留不变。

## source-complete coverage

| 层 | 本轮落点与责任 |
|---|---|
| investors | 不根据持仓倒推个人动机；已有方法保留，新增方法背景明确标时点 |
| ten-questions | 不制造十问新答案；13F 只能证明有限的公开行为 |
| companies | [ADP](/investor-masters/companies/adp/)、[Alphabet](/investor-masters/companies/alphabet/)、[AppLovin](/investor-masters/companies/applovin/)、[Credo Technology](/investor-masters/companies/credo-technology/)、[GE Vernova](/investor-masters/companies/ge-vernova/)、[Mastercard](/investor-masters/companies/mastercard/)、[Meta](/investor-masters/companies/meta/)、[Netflix](/investor-masters/companies/netflix/)、[Nextpower](/investor-masters/companies/nextpower/)、[TJX](/investor-masters/companies/tjx/)、[Uber](/investor-masters/companies/uber/)、[Veeva Systems](/investor-masters/companies/veeva-systems/)、[Visa](/investor-masters/companies/visa/)、[Yum! Brands](/investor-masters/companies/yum-brands/)、[台积电](/investor-masters/companies/tsmc/)、[微软](/investor-masters/companies/microsoft/)；覆盖候选、新进前十和重要分歧 |
| concepts / dialogues | 不因关键词新建概念或对话 |
| institutions | [Fundsmith](/investor-masters/institutions/fundsmith/)；[13F趋势-Fundsmith](/investor-masters/institutions/13f-trends-fundsmith/) |
| indexes / matrix | [13F趋势](/investor-masters/institutions/13f-trends/)、[十家横向页](/investor-masters/institutions/13f-trends-2026-q3/)、来源总表与日志；不改方法比较矩阵 |

## 这篇材料明确能回答哪些十问

不能独立回答任一投资十问。股数变化支持“做了什么”，不能证明买卖原因、确信程度、个人决策归属或未来持有期。

## 这篇材料要求回填哪些投资人页

本轮不扩写人物页。机构行为进入机构和公司层；历史方法与当前行为不同之处在趋势页明确解释。

## 这篇材料要求新建或更新哪些公司页

[ADP](/investor-masters/companies/adp/)、[Alphabet](/investor-masters/companies/alphabet/)、[AppLovin](/investor-masters/companies/applovin/)、[Credo Technology](/investor-masters/companies/credo-technology/)、[GE Vernova](/investor-masters/companies/ge-vernova/)、[Mastercard](/investor-masters/companies/mastercard/)、[Meta](/investor-masters/companies/meta/)、[Netflix](/investor-masters/companies/netflix/)、[Nextpower](/investor-masters/companies/nextpower/)、[TJX](/investor-masters/companies/tjx/)、[Uber](/investor-masters/companies/uber/)、[Veeva Systems](/investor-masters/companies/veeva-systems/)、[Visa](/investor-masters/companies/visa/)、[Yum! Brands](/investor-masters/companies/yum-brands/)、[台积电](/investor-masters/companies/tsmc/)、[微软](/investor-masters/companies/microsoft/)。

其余最新申报证券全部保留在轨迹表；小仓、工具或没有实质新增判断的证券暂缓独立公司页，不将持仓名单伪装成商业分析。历史已退出观察标的继续保留。

## 这篇材料要求新建或更新哪些概念 / 对话 / 机构页

机构主页滚动至 2025Q4—2026Q3；长趋势展示 2023Q1—2026Q3 并保留基期；横向页按十家同季度重算，沿用原有评分公式与机构权重口径。可复制候选使用日期明确的价格过滤；关联持股、权证、期权和特殊估值单列。

## 核验重点

Nextpower 同一 CUSIP 65290E101 的 CLASS A COM / COM 归为连续仓位，不误计新进和退出。2026 半年信披露旗舰基金上半年换手率 51.8%，并讨论基本面与价格动量；这是产品方法背景，不能当作 LLP 13F 的换手率。旗舰基金与 LLP 申报集合不同。

## 这篇材料不能回答什么

不能回答真实成交成本、资金申赎、现金与净敞口，也不能把申报总值当作基金净值。股数和估算主动金额不是实际成交记录。价格贡献是端点算术分解；无法可靠比较的条目进入未归因桶，与股数项和价格项共同对账。

## 传播清单

- [x] 新建不可变来源卡，逐份官方原文、日期、accession、金额单位与 SHA-256 可追溯。
- [x] 机构四季、长历史、横向页与公司层按本轮职责联动。
- [x] 来源登记、入口和日志更新；第一批 现有资料 快照不改动。
- [x] 53 项测试、独立进程重放、隔离站点构建及链接检查通过；验收和发布责任记录于 维护日志，线上结果以部署状态为准。

### 方法背景附件的使用范围

[Fundsmith 2026 半年信](https://www.fundsmith.co.uk/media/lfhpxi1x/2026-fef-semi-annual-letter-to-shareholders-web.pdf) 原始 PDF 在 `现有资料/data/13f-20261117-batch2-context/`；本轮仅吸收第 6—7 页的方法调整与第 10 页的 51.8% 换手率作为解读背景。这是针对 13F 的有限核验，不宣称已完成整封股东信、附录公司评论或十问的全文提纯。

### 尚未取得完整历史公司行动资料

这些是隐含价异常筛选后仍缺资料的区间，不等于确认发生拆股；原始股数保留，相关历史主动额仅作机械端点比较。最新候选另按有日期的报价过滤。

| 证券 | 区间 | 状态 |
|---|---|---|
| M7518J104 | 2025-03-31 → 2025-06-30 | 尚未完成独立核验 |
