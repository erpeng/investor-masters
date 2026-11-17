---
title: "Coatue-13f-source-audit"
slug: "sources/coatue-13f-source-audit"
description: "13F 季度材料的覆盖责任、证据边界与传播清单。"
---
## 来源定位

原始材料：[SEC｜Coatue：2022Q4至2026Q3持仓轨迹](/investor-masters/sources/coatue-13f-2026q3/)。责任是 Coatue Management 公开组合行为，报告日为 2026-09-30，核验日为 2026-11-17。结构化快照：`现有资料/data/13f-20261117-batch2/coatue.json`；旧方法讨论随同归档，原始 SEC 文件保留不变。

## source-complete coverage

| 层 | 本轮落点与责任 |
|---|---|
| investors | 不根据持仓倒推个人动机；已有方法保留，新增方法背景明确标时点 |
| ten-questions | 不制造十问新答案；13F 只能证明有限的公开行为 |
| companies | [ASML](/investor-masters/companies/asml/)、[Alphabet](/investor-masters/companies/alphabet/)、[AppLovin](/investor-masters/companies/applovin/)、[Applied Materials](/investor-masters/companies/applied-materials/)、[Broadcom](/investor-masters/companies/broadcom/)、[Cerebras Systems](/investor-masters/companies/cerebras-systems/)、[Eaton](/investor-masters/companies/eaton/)、[Equinix](/investor-masters/companies/equinix/)、[GE Vernova](/investor-masters/companies/ge-vernova/)、[Intel](/investor-masters/companies/intel/)、[Intercontinental Exchange](/investor-masters/companies/intercontinental-exchange/)、[Lam Research](/investor-masters/companies/lam-research/)、[Mastercard](/investor-masters/companies/mastercard/)、[Meta](/investor-masters/companies/meta/)、[Micron Technology](/investor-masters/companies/micron-technology/)、[Netflix](/investor-masters/companies/netflix/)、[SK Hynix](/investor-masters/companies/sk-hynix/)、[Salesforce](/investor-masters/companies/salesforce/)、[Shopify](/investor-masters/companies/shopify/)、[SpaceX](/investor-masters/companies/spacex/)、[Uber](/investor-masters/companies/uber/)、[Visa](/investor-masters/companies/visa/)、[亚马逊](/investor-masters/companies/amazon/)、[台积电](/investor-masters/companies/tsmc/)、[微软](/investor-masters/companies/microsoft/)、[特斯拉](/investor-masters/companies/tesla/)、[英伟达](/investor-masters/companies/nvidia/)；覆盖候选、新进前十和重要分歧 |
| concepts / dialogues | 不因关键词新建概念或对话 |
| institutions | [Coatue Management](/investor-masters/institutions/coatue-management/)；[13F趋势-Coatue](/investor-masters/institutions/13f-trends-coatue/) |
| indexes / matrix | [13F趋势](/investor-masters/institutions/13f-trends/)、[十家横向页](/investor-masters/institutions/13f-trends-2026-q3/)、来源总表与日志；不改方法比较矩阵 |

## 这篇材料明确能回答哪些十问

不能独立回答任一投资十问。股数变化支持“做了什么”，不能证明买卖原因、确信程度、个人决策归属或未来持有期。

## 这篇材料要求回填哪些投资人页

本轮不扩写人物页。机构行为进入机构和公司层；历史方法与当前行为不同之处在趋势页明确解释。

## 这篇材料要求新建或更新哪些公司页

[ASML](/investor-masters/companies/asml/)、[Alphabet](/investor-masters/companies/alphabet/)、[AppLovin](/investor-masters/companies/applovin/)、[Applied Materials](/investor-masters/companies/applied-materials/)、[Broadcom](/investor-masters/companies/broadcom/)、[Cerebras Systems](/investor-masters/companies/cerebras-systems/)、[Eaton](/investor-masters/companies/eaton/)、[Equinix](/investor-masters/companies/equinix/)、[GE Vernova](/investor-masters/companies/ge-vernova/)、[Intel](/investor-masters/companies/intel/)、[Intercontinental Exchange](/investor-masters/companies/intercontinental-exchange/)、[Lam Research](/investor-masters/companies/lam-research/)、[Mastercard](/investor-masters/companies/mastercard/)、[Meta](/investor-masters/companies/meta/)、[Micron Technology](/investor-masters/companies/micron-technology/)、[Netflix](/investor-masters/companies/netflix/)、[SK Hynix](/investor-masters/companies/sk-hynix/)、[Salesforce](/investor-masters/companies/salesforce/)、[Shopify](/investor-masters/companies/shopify/)、[SpaceX](/investor-masters/companies/spacex/)、[Uber](/investor-masters/companies/uber/)、[Visa](/investor-masters/companies/visa/)、[亚马逊](/investor-masters/companies/amazon/)、[台积电](/investor-masters/companies/tsmc/)、[微软](/investor-masters/companies/microsoft/)、[特斯拉](/investor-masters/companies/tesla/)、[英伟达](/investor-masters/companies/nvidia/)。

其余最新申报证券全部保留在轨迹表；小仓、工具或没有实质新增判断的证券暂缓独立公司页，不将持仓名单伪装成商业分析。历史已退出观察标的继续保留。

## 这篇材料要求新建或更新哪些概念 / 对话 / 机构页

机构主页滚动至 2025Q4—2026Q3；长趋势展示 2023Q1—2026Q3 并保留基期；横向页按十家同季度重算，沿用原有评分公式与机构权重口径。可复制候选使用日期明确的价格过滤；关联持股、权证、期权和特殊估值单列。

## 核验重点

多管理人行先按稳定证券身份聚合；Alphabet A/C 在轨迹中分列，仅在公司级横向对照合并。SK hynix 新列示的是 SKHY 美国存托凭证，不能拼接韩国普通股股数。

## 这篇材料不能回答什么

不能回答真实成交成本、资金申赎、现金与净敞口，也不能把申报总值当作基金净值。股数和估算主动金额不是实际成交记录。价格贡献是端点算术分解；无法可靠比较的条目进入未归因桶，与股数项和价格项共同对账。

## 传播清单

- [x] 新建不可变来源卡，逐份官方原文、日期、accession、金额单位与 SHA-256 可追溯。
- [x] 机构四季、长历史、横向页与公司层按本轮职责联动。
- [x] 来源登记、入口和日志更新；第一批 现有资料 快照不改动。
- [x] 53 项测试、独立进程重放、隔离站点构建及链接检查通过；验收和发布责任记录于 维护日志，线上结果以部署状态为准。

### 尚未取得完整历史公司行动资料

这些是隐含价异常筛选后仍缺资料的区间，不等于确认发生拆股；原始股数保留，相关历史主动额仅作机械端点比较。最新候选另按有日期的报价过滤。

| 证券 | 区间 | 状态 |
|---|---|---|
| G6674U108 | 2023-06-30 → 2023-09-30 | 尚未完成独立核验 |
| NKLA | 2023-09-30 → 2023-12-31 | 尚未完成独立核验 |
| NKLA | 2024-06-30 → 2024-09-30 | 尚未完成独立核验 |
| API | 2024-09-30 → 2024-12-31 | 尚未完成独立核验 |
| G6674U108 | 2024-09-30 → 2024-12-31 | 尚未完成独立核验 |
| GEV | 2025-03-31 → 2025-06-30 | 尚未完成独立核验 |
| 08862E109 | 2025-06-30 → 2025-09-30 | 尚未完成独立核验 |
| QS | 2025-06-30 → 2025-09-30 | 尚未完成独立核验 |
| G9572D103 | 2025-09-30 → 2025-12-31 | 尚未完成独立核验 |

### 历史身份与公司行动

已核对同一 CUSIP 的类别名称变动，以及涉及 SMCI、Lucid、Sonder、Nikola、ChargePoint 和 Grab 权证的换码或拆并股；具体适用范围与一手链接保留于快照。AMC 2023Q3 同时涉及合股和股东补偿，无法可靠区分的端点变化不强行计作主动交易。原始申报行保持不变。
