---
title: "Pershing-13f-source-audit"
slug: "sources/pershing-13f-source-audit"
description: "13F 季度材料的覆盖责任、证据边界与传播清单。"
---
## 来源定位

原始材料：[SEC｜Pershing：2022Q4至2026Q3持仓轨迹](/investor-masters/sources/pershing-13f-2026q3/)。责任是 Pershing Square 公开组合行为，报告日为 2026-09-30，核验日为 2026-11-17。结构化快照：`现有资料/data/13f-20261117-batch2/pershing.json`；旧方法讨论随同归档，原始 SEC 文件保留不变。

## source-complete coverage

| 层 | 本轮落点与责任 |
|---|---|
| investors | 不根据持仓倒推个人动机；已有方法保留，新增方法背景明确标时点 |
| ten-questions | 不制造十问新答案；13F 只能证明有限的公开行为 |
| companies | [Alcon](/investor-masters/companies/alcon/)、[Brookfield](/investor-masters/companies/brookfield/)、[Howard Hughes](/investor-masters/companies/howard-hughes/)、[Intercontinental Exchange](/investor-masters/companies/intercontinental-exchange/)、[Mastercard](/investor-masters/companies/mastercard/)、[Meta](/investor-masters/companies/meta/)、[Netflix](/investor-masters/companies/netflix/)、[Restaurant Brands](/investor-masters/companies/restaurant-brands/)、[Uber](/investor-masters/companies/uber/)、[Visa](/investor-masters/companies/visa/)、[亚马逊](/investor-masters/companies/amazon/)、[微软](/investor-masters/companies/microsoft/)；覆盖候选、新进前十和重要分歧 |
| concepts / dialogues | 不因关键词新建概念或对话 |
| institutions | [Pershing Square](/investor-masters/institutions/pershing-square/)；[13F趋势-Pershing](/investor-masters/institutions/13f-trends-pershing/) |
| indexes / matrix | [13F趋势](/investor-masters/institutions/13f-trends/)、[十家横向页](/investor-masters/institutions/13f-trends-2026-q3/)、来源总表与日志；不改方法比较矩阵 |

## 这篇材料明确能回答哪些十问

不能独立回答任一投资十问。股数变化支持“做了什么”，不能证明买卖原因、确信程度、个人决策归属或未来持有期。

## 这篇材料要求回填哪些投资人页

本轮不扩写人物页。机构行为进入机构和公司层；历史方法与当前行为不同之处在趋势页明确解释。

## 这篇材料要求新建或更新哪些公司页

[Alcon](/investor-masters/companies/alcon/)、[Brookfield](/investor-masters/companies/brookfield/)、[Howard Hughes](/investor-masters/companies/howard-hughes/)、[Intercontinental Exchange](/investor-masters/companies/intercontinental-exchange/)、[Mastercard](/investor-masters/companies/mastercard/)、[Meta](/investor-masters/companies/meta/)、[Netflix](/investor-masters/companies/netflix/)、[Restaurant Brands](/investor-masters/companies/restaurant-brands/)、[Uber](/investor-masters/companies/uber/)、[Visa](/investor-masters/companies/visa/)、[亚马逊](/investor-masters/companies/amazon/)、[微软](/investor-masters/companies/microsoft/)。

其余最新申报证券全部保留在轨迹表；小仓、工具或没有实质新增判断的证券暂缓独立公司页，不将持仓名单伪装成商业分析。历史已退出观察标的继续保留。

## 这篇材料要求新建或更新哪些概念 / 对话 / 机构页

机构主页滚动至 2025Q4—2026Q3；长趋势展示 2023Q1—2026Q3 并保留基期；横向页按十家同季度重算，沿用原有评分公式与机构权重口径。可复制候选使用日期明确的价格过滤；关联持股、权证、期权和特殊估值单列。

## 核验重点

历史 CIK 1336528 衔接新 CIK 2026053；旧主体 Q2/Q3 的 13F-NT 是通知而非清仓。Q2 NEW HOLDINGS 修订 0001172661-26-005426 增补 PS 184,289,699 股、$6,055,759,509，须加入原表；它不是重列替换。Q3 PS 股数相同，otherManager 3/4 对应 Partner Group / Management；关联持股不能简化成基金自买。全申报与剔除 PS 的辅助切片均非 PSH NAV 或官方 AUM。ALC 为 Alcon，不是 Air Lease。

## 这篇材料不能回答什么

不能回答真实成交成本、资金申赎、现金与净敞口，也不能把申报总值当作基金净值。股数和估算主动金额不是实际成交记录。价格贡献是端点算术分解；无法可靠比较的条目进入未归因桶，与股数项和价格项共同对账。

## 传播清单

- [x] 新建不可变来源卡，逐份官方原文、日期、accession、金额单位与 SHA-256 可追溯。
- [x] 机构四季、长历史、横向页与公司层按本轮职责联动。
- [x] 来源登记、入口和日志更新；第一批 现有资料 快照不改动。
- [x] 53 项测试、独立进程重放、隔离站点构建及链接检查通过；验收和发布责任记录于 维护日志，线上结果以部署状态为准。

### 申报范围附件

[Pershing Square Inc. Q3 10-Q](https://www.sec.gov/Archives/edgar/data/2026053/000119312526450239/ps-20260930.htm) 原文在 `现有资料/data/13f-20261117-batch2-context/`，用于区分上市管理公司、关联主体与产品资产；未将公司财务报表当作基金持仓净值。
