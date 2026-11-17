---
title: "Berkshire-13f-source-audit"
slug: "sources/berkshire-13f-source-audit"
description: "13F 季度材料的覆盖责任、证据边界与传播清单。"
---
## 来源定位

原始材料：[SEC｜Berkshire：2022Q4至2026Q3持仓轨迹](/investor-masters/sources/berkshire-13f-2026q3/)；申报主体 Berkshire Hathaway / CIK 1067983。责任是机构公开组合行为，报告期截至 2026-09-30，核验日 2026-11-17。结构化证据：`现有资料/data/13f-20261117/berkshire.json`。

## source-complete coverage

| 层 | 本轮落点与责任 |
|---|---|
| investors | 本轮不改人物方法；13F 不证明个人动机或每笔决策归属 |
| ten-questions | 不新增十问答案；仅提供可验证的组合行为 |
| companies | [Bending Spoons](/investor-masters/companies/bending-spoons/)、[Lennar](/investor-masters/companies/lennar/)、[Delta Air Lines](/investor-masters/companies/delta-air-lines/)；只补持仓行为、机构分歧和研究边界 |
| concepts / dialogues | 不机械新建；本轮证据不足以产生新的方法概念或对话 |
| institutions | [Berkshire Hathaway](/investor-masters/institutions/berkshire-hathaway/)；[13F趋势-Berkshire](/investor-masters/institutions/13f-trends-berkshire/) |
| indexes / matrix | [13F趋势](/investor-masters/institutions/13f-trends/)、[13F趋势-2026Q3](/investor-masters/institutions/13f-trends-2026-q3/)、来源总表与维护日志；不改投资人比较矩阵或十问覆盖数 |

## 这篇材料明确能回答哪些十问

不能独立回答任一投资十问。仓位只能支持“做了什么”的有限观察；买卖原因、研究确信和持有纪律需要原话或其他一手材料。本轮不制造新答案。

## 这篇材料要求回填哪些投资人页

本轮不改人物页。机构背景和投资人既有方法保留，持仓动作写到机构层；不把股数变化追溯成未经证实的个人观点。

## 这篇材料要求新建或更新哪些公司页

[Bending Spoons](/investor-masters/companies/bending-spoons/)、[Lennar](/investor-masters/companies/lennar/)、[Delta Air Lines](/investor-masters/companies/delta-air-lines/)。

优先覆盖本季新进、显著增股或重要分歧；其他小仓仅保留在单机构完整轨迹。不延伸到缺少依据的盈利预测、财务估值或即时买卖建议。

## 这篇材料要求新建或更新哪些概念 / 对话 / 机构页

更新 [Berkshire Hathaway](/investor-masters/institutions/berkshire-hathaway/) 的 2025Q4—2026Q3 四季快照与最近季度雷达；[13F趋势-Berkshire](/investor-masters/institutions/13f-trends-berkshire/) 保留 2023Q1—2026Q3 轨迹，2022Q4 作比较基期；增量进入 [仅五家首批横向页](/investor-masters/institutions/13f-trends-2026-q3/)。

按股数决定主动方向，价格和权重另列；新进、退出、换股、拆股及类别重命名分开。期权不与正股混合，未验证的报价或身份保留缺口。本轮不新建概念/对话页。

## 这篇材料不能回答什么

不能回答真实成交时点与买价、现金和非美资产、净申赎、完整空头和衍生品风险，也不能把首次披露等同首次投资。总市值变化不能当组合收益率；期权名义申报值不能当作权利金。首次上市或估值口径差异的证券不进入可直接复制共识榜。

## 传播清单

- [x] 新建不可变 现有资料 来源卡；官方原文、申报日、报告期与 accession 可追溯。
- [x] 本页区分人物、十问、公司、机构和索引责任；不扩写无证据层级。
- [x] 更新机构四季快照、Q3 横向页与 13F 总入口。
- [x] 来源登记与维护日志追加本次记录。
- [x] 公司联动完成，限定于本轮批准的 17 家；未扩建其他小仓公司页。
- [x] 单机构长历史页已更新，结构化 现有资料 快照及证据清单已冻结；机构/横向页已从同一快照重放。
- [x] 站点首轮编译、构建、检查和本地路由验证通过；最后一轮证券标签修订后的验收记录见 wiki/log。

### 标准化复核补记

Yahoo 将 GE（2023、2024）、FDX（2026-06-01）、LEN（2025-01-21）、SPGI（2026-07-01）的分拆除权调整列为 split 事件；本次依据 SEC 一手材料排除这五条价格调整，不改变母股股数。真实的 LRCX 2024-10-03 十拆一及 CUSIP 512807108→512807306 则同时处理。逐条证据见快照 `audit.excluded_price_adjustments` 与拆股记录。Berkshire 2025Q1 的 NEW HOLDINGS 修订中，LEN.B 的 202 股按该 accession 的明确补充关系加到原 152,572 股，合计 152,774 股；不把这个个案扩成通用重复行相加规则。

### 冻结后补核：Sirius XM 与 Liberty Live 换股

补充时间：`2026-11-17 08:48:13 Asia/Shanghai`。以下两项在 `现有资料/data/13f-20261117/` 冻结后进一步核实，作为审计与重放规则的补充；原始 JSON、原始来源卡及原 SHA-256 清单均不回写。它们影响历史季度的可比性，不改变 2026Q3 的增减股结论。

**Sirius XM：2024-09-09 完成的多证券换股。** 原 SIRI（CUSIP `82968B103`）每股换成新 SIRI（`829933100`）`0.1` 股；原 Liberty SiriusXM 的 A/C 类（LSXMA、LSXMK）每股各换成新 SIRI `0.8375` 股。比例与完成时间见 [SEC 8-K12B，Item 2.01](https://www.sec.gov/Archives/edgar/data/908937/000110465924098260/tm2423473d2_8k12b.htm)；旧、新 CUSIP 与相关类别同 13F 原表交叉对应。

本轮重放保留旧证券行与新证券行，不把不同来源强行当作一个普通拆股序列。比较 2024Q2—2024Q3 时，先将三项上季股数分别乘 `0.1 / 0.8375 / 0.8375` 后相加，折合基准为 `101,380,355.95` 股；2024Q3 新 SIRI 为 `105,155,029` 股，较折合基准约增加 `3.72%`。轨迹标记为“换股后约 +3.72%”及“换股转出”，不写成从零新建与旧仓清仓。

金额端采用合并上季申报值除以折合股数得到比较价格，再计算端点股数差；旧来源证券不重复扣除，价格项补足总值变化。这一调整剔除了已知转换比例造成的假交易，但仍是季末端点估算：无法还原各账户零股现金、真实成交时点、成交成本及期间先买后卖的路径，不能将剩余差额直接当作二级市场成交记录。

**Liberty Live：2025-12-15 收盘后的一比一换股。** LLYVA 从 `531229748` 转为 `530909100`，LLYVK 从 `531229722` 转为 `530909308`，每股换成对应新类别 `1` 股；新代码沿用原 ticker，交易所映射自 12 月 16 日生效。CUSIP 与代码映射见 [Nasdaq DTN2025-38](https://www.nasdaqtrader.com/TraderNews.aspx?id=DTN2025-38)；完成日期和一比一安排见 [Liberty Live 的 SEC Schedule 13D，Item 3](https://www.sec.gov/Archives/edgar/data/1335258/000110465925122173/xslSCHEDULE_13D_X01/primary_doc.xml)，[原始 XML](https://www.sec.gov/Archives/edgar/data/1335258/000110465925122173/primary_doc.xml)。比较时按这两条已证实的对应关系归一类别/CUSIP，避免将 2025Q4 换股误报为一边退出、一边新增。

附录证据目录：`现有资料/data/13f-20261117-corporate-actions-addendum/`。独立保存 Nasdaq 原始 HTML 与 `sha256-addendum.json`，HTML SHA-256 为 `43aa2d0e8d1b8d557a04c2dd982d2a9e89d8c8bf04ccd73cd5db95562b208c8e`。两份 SEC 原文已在线核验；本次直连归档请求返回 403，未伪称保留了本地 SEC 原文副本。附录没有修改原证据清单。
