---
title: "13F 趋势 - Q1 2026"
slug: "institutions/13f-trends-2026-q1"
description: "13F 趋势 - Q1 2026 的跨机构持仓趋势雷达。"
---
抓取时间：`2026-06-06 10:45 CST`。

内容校正：`2026-06-08` 根据后续补齐的 Dorsey、Altimeter、Appaloosa、Pershing 单机构趋势页，补充 Uber 等公司页联动信号。`2026-06-12` 新增 Third Point 单机构趋势页后，补充一个解释约束：Third Point 的 `AMZN / TDS / CRH / SGI` 在 Q1 2026 权重上升主要来自公开 long book 大幅缩表，不应计作主动加仓；`CRS / MTZ / DHR / TSM / APG / LYV` 新进或重回前十，多数也是相对留存导致的前十重排。`2026-06-16` 按新标准重生成 Coatue 单机构趋势页后，补充 Coatue 观察：`EQIX / ASML` 是 Q1 新进/恢复仓位，`AMAT / ETN` 才是真正进入前十；`TSM` 是第一大仓且股数增加，`GEV / CEG` 仍在前十但股数下降，不能写成主动加仓。`2026-07-23` 新增 Atreides 单机构页后，补充其 AI 互连、光通信、存储和平台仓位轮动；由于 Atreides 同时披露普通股和大量期权，本次只把普通股动作接入资产线观察，PUT/CALL 仍单独解释。本页没有伪装成重新抓取；原始横向计算时间仍以上方抓取时间为准，原始纳入机构数也仍按当时横向计算口径显示。

这页不是买入清单，而是把同一季度多个 13F 披露横向拉齐，用来发现值得继续研究的线索。主榜只看普通股票；ETF、指数工具与个股 PUT/CALL 放到最后的交易信号区。

## 覆盖口径

- 纳入机构：21 家。
- 披露滞后：无。
- 加仓/减仓按股数变化折算的主动市值判断，权重变化按 13F 组合占比判断；价格涨跌不会被误认为主动买卖。
- 统一算法口径：[13F 趋势口径](/investor-masters/institutions/13f-trends/#口径)。

## 普通股票抄作业候选榜（过滤后研究优先级，不等同于共识加仓榜）

这张榜只回答“现在还值得拿出来研究吗”。它在共识加仓、新进前十和集中度上升之上，再过滤三件事：进入前十是否来自主动买股、机构风格是否适合抄、13F 后涨幅是否已经透支。`新进前十` 只有在股数主动增加时才按新线索加分；如果只是股数不变但价格上涨挤进前十，只展示、不加分。

当前价来自 Yahoo Finance，抓取时间同本页 `2026-06-06 10:45 CST`；取不到则标 `N/A`，不编价格，也不做追涨扣分。

| 优先级 | 标的 | 13F证据 | 支持机构 | 新线索判定 | 13F隐含价 | 当前价 | 13F后涨幅 | 抄作业结论 | 下一步验证 |
|---:|---|---|---|---|---:|---:|---:|---|---|
| 1 | `SUNB` | 净主动变化 `$1.11bn`；买入分 `17.4` / 卖出分 `0.0` | Oakmark（$0.76bn，+1.0 pct）、AKO（$0.21bn，+4.1 pct）、Dorsey（$0.14bn，+11.4 pct） | 主动买入进前十：Dorsey（$0.14bn，+11.4 pct） | `$65.09` | `$79.36` | `+21.9%` | 优先研究：需要更强验证 | 核对利用率、项目 backlog、租金/价格、客户行业暴露和自由现金流。 |
| 2 | `APP` | 净主动变化 `$0.95bn`；买入分 `17.1` / 卖出分 `1.1` | Lone Pine（$0.46bn，+0.8 pct）、Baillie（$0.36bn，-0.7 pct）、Dorsey（$0.13bn，+10.0 pct） | 主动买入进前十：Lone Pine（$0.46bn，+0.8 pct）、Dorsey（$0.13bn，+10.0 pct） | `$398` | `$557` | `+40.0%` | 研究但不追：涨幅较大，降级研究 | 核对收入增速、广告/云/软件转化、单位经济性和资本开支效率。 |
| 3 | `SPGI` | 净主动变化 `-$0.21bn`；买入分 `16.2` / 卖出分 `3.3` | Dorsey（$0.09bn，+7.5 pct）、Himalaya（$0.05bn，+1.6 pct） | 主动买入进前十：Dorsey（$0.09bn，+7.5 pct）、Himalaya（$0.05bn，+1.6 pct） | `$425` | `$424` | `-0.2%` | 研究但有分歧：未明显透支 | 核对订阅留存、发行周期、指数授权和数据产品定价力。 |
| 4 | `UBER` | Dorsey/Appaloosa 主动买入进前十；Altimeter 主动加仓；Pershing 仍为核心持有 | Appaloosa（股数 +242.3%，+5.5 pct）、Altimeter（股数 +42.6%，+3.2 pct）、Dorsey（新进 6.2%）、Pershing（15.7%，非本季买入） | 主动买入进前十：Appaloosa、Dorsey；主动加仓核心仓：Altimeter | `$71.9` | `$72.3` | `+0.6%` | 优先研究：价格未明显抢跑，且跨机构方法差异清楚 | 核对订单密度、广告/会员、自由现金流、自动驾驶成本和监管风险。 |
| 5 | `LIN` | 净主动变化 `$0.28bn`；买入分 `12.0` / 卖出分 `0.0` | Maverick（$0.21bn，+2.4 pct）、AKO（$0.05bn，+1.2 pct）、Duquesne（$0.02bn，+0.6 pct） | 未进入前十，主要看主动加仓和集中度 | `$496` | `$508` | `+2.4%` | 优先研究：未明显透支 | 核对利用率、项目 backlog、租金/价格、客户行业暴露和自由现金流。 |
| 6 | `AVGO` | 净主动变化 `-$0.16bn`；买入分 `14.8` / 卖出分 `6.0` | Bridgewater（$0.23bn，+1.1 pct）、ARK（$0.13bn，+1.0 pct）、Duquesne（$0.06bn，+1.8 pct） | 主动买入进前十：Bridgewater（$0.23bn，+1.1 pct） | `$310` | `$386` | `+24.6%` | 研究但有分歧：需要更强验证 | 核对订单/积压、客户资本开支、先进制程/封装和网络升级节奏。 |
| 7 | `NU` | 净主动变化 `$0.24bn`；买入分 `11.4` / 卖出分 `3.6` | Maverick（$0.18bn，+1.6 pct）、Lone Pine（$0.14bn，+0.7 pct） | 主动买入进前十：Maverick（$0.18bn，+1.6 pct）、Lone Pine（$0.14bn，+0.7 pct） | `$14.37` | `$11.97` | `-16.7%` | 研究但有分歧：未明显透支 | 核对消费、监管、竞争、利润率和回购/资本回报。 |
| 8 | `TSLA` | 净主动变化 `$1.47bn`；买入分 `10.8` / 卖出分 `4.0` | H&H（$1.27bn，+6.3 pct）、Tudor（$0.24bn，+0.4 pct） | 主动买入进前十：H&H（$1.27bn，+6.3 pct） | `$372` | `$391` | `+5.2%` | 研究但有分歧：未明显透支 | 回到公司基本面、估值和机构方法边界验证。 |
| 9 | `TME` | 净主动变化 `$0.06bn`；买入分 `8.4` / 卖出分 `0.0` | Himalaya（$0.06bn，+1.9 pct） | 主动买入进前十：Himalaya（$0.06bn，+1.9 pct） | `$9.28` | `$9.08` | `-2.2%` | 优先研究：未明显透支 | 核对消费、监管、竞争、利润率和回购/资本回报。 |
| 10 | `Natera` | 净主动变化 `$0.18bn`；买入分 `6.8` / 卖出分 `0.0` | Duquesne（$0.13bn，+5.3 pct）、Maverick（$0.05bn，+0.4 pct） | 未进入前十，主要看主动加仓和集中度 | `$200` | `N/A` | `N/A` | 研究观察：当前价缺失，暂不做追涨过滤 | 回到公司基本面、估值和机构方法边界验证。 |
| 11 | `Intel` | 净主动变化 `$0.15bn`；买入分 `6.8` / 卖出分 `0.0` | Maverick（$0.13bn，+1.5 pct）、Duquesne（$0.02bn，+0.5 pct） | 未进入前十，主要看主动加仓和集中度 | `$44.13` | `N/A` | `N/A` | 研究观察：当前价缺失，暂不做追涨过滤 | 回到公司基本面、估值和机构方法边界验证。 |
| 12 | `GOOG/GOOGL` | 净主动变化 `$10.78bn`；买入分 `40.5` / 卖出分 `39.0` | Berkshire（$11.39bn，+3.9 pct）、Berkshire（$1.03bn，+0.4 pct）、H&H（$0.58bn，+2.0 pct） | 未进入前十，主要看主动加仓和集中度 | `$287` | `$366` | `+27.5%` | 研究但不追：涨幅较大，降级研究 | 核对收入增速、广告/云/软件转化、单位经济性和资本开支效率。 |
| 13 | `PBR` | 净主动变化 `$0.30bn`；买入分 `8.0` / 卖出分 `0.0` | Baillie（$0.18bn，+0.7 pct）、Oaktree（$0.13bn，+1.9 pct） | 未进入前十，主要看主动加仓和集中度 | `$20.75` | `$17.75` | `-14.5%` | 研究观察：未明显透支 | 回到公司基本面、估值和机构方法边界验证。 |

## 资产线 / 趋势跟踪榜（抄趋势，不机械抄 ticker）

这张榜把同一条价值链里的标的合并看。宏观/趋势型机构的 13F 不一定适合直接买同一个 ticker，更适合观察它们在交易哪条资产线。

| 优先级 | 资产线 | 代表标的 | 13F证据 | 参与机构 | 趋势解释 | 价格过滤 | 跟踪结论 | 下一步验证 |
|---:|---|---|---|---|---|---|---|---|
| 1 | AI应用/广告/平台变现 | `GOOG/GOOGL` / `AMZN` / `APP` / `META` / `MSFT` | GOOG/GOOGL 净主动 $10.78bn；AMZN 净主动 -$1.38bn；APP 净主动 $0.95bn | AKO / ARK / Baillie / Baupost / Berkshire / Bridgewater / Citadel / Dorsey | AI应用/广告/平台变现 的 13F 信号来自多个标的/机构，不应只抄单一 ticker。 | 部分标的已涨，需降速验证 | 优先跟踪 | 核对收入增速、广告/云/软件转化、单位经济性和资本开支效率。 |
| 2 | 半导体设备/网络/先进制造 | `TSM` / `TER` / `LRCX` / `CRDO` / `AVGO` / `ASML` / `AMAT` | TSM 净主动 -$0.69bn；TER 净主动 $0.37bn；LRCX 净主动 -$0.34bn；Coatue：TSM 第一大且增股、LRCX/AMAT/AVGO 前十、ASML 新进/恢复仓位 | ARK / Baillie / Bridgewater / Coatue / Dorsey / Duquesne / H&H / Lone Pine / Maverick | 半导体设备/网络/先进制造 的 13F 信号来自多个标的/机构，不应只抄单一 ticker。 | 部分标的已涨，需降速验证 | 优先跟踪 | 核对订单/积压、客户资本开支、先进制程/封装和网络升级节奏。 |
| 3 | 工程/租赁/工业约束 | `SUNB` / `LIN` / `CRS` | SUNB 净主动 $1.11bn；LIN 净主动 $0.28bn；CRS 净主动 $0.01bn | AKO / Dorsey / Duquesne / Lone Pine / Maverick / Oakmark / Third Point | 工程/租赁/工业约束 的 13F 信号来自多个标的/机构，不应只抄单一 ticker。 | 部分标的已涨，需降速验证 | 优先跟踪 | 核对利用率、项目 backlog、租金/价格、客户行业暴露和自由现金流。 |
| 4 | 本地服务平台/经营杠杆 | `UBER` | Dorsey 和 Appaloosa 主动买入进前十；Altimeter 主动加仓；Pershing 仍为核心持有 | Appaloosa / Altimeter / Dorsey / Pershing | 这不是单一“网约车”信号，而是本地服务网络、广告/会员、自由现金流和自动驾驶成本重排的共同研究线索。 | 13F 后价格基本未抢跑 | 优先跟踪 | 核对订单密度、广告/会员、自动驾驶成本分摊、监管和回购。 |
| 5 | 指数/宏观风险对冲 | `SPY PUT` / `IVV CALL` / `GLD CALL` / `SPY CALL` / `QQQ PUT` | SPY PUT 净主动 $5.03bn；IVV CALL 净主动 $2.80bn；GLD CALL 净主动 $1.11bn | Bridgewater / Citadel / Duquesne / Greenlight / Oaktree / Third Point / Tudor | 指数/宏观风险对冲 的 13F 信号来自多个标的/机构，不应只抄单一 ticker。 | 部分标的已涨，需降速验证 | 优先跟踪 | 核对净敞口、波动率、政策路径和组合对冲目的。 |
| 6 | 中国与新兴市场互联网 | `PDD` / `BABA` / `NU` / `TME` | PDD 净主动 $0.63bn；BABA 净主动 -$0.50bn；NU 净主动 $0.24bn | Baillie / H&H / Himalaya / Lone Pine / Maverick / Oaktree / Third Point | 中国与新兴市场互联网 的 13F 信号来自多个标的/机构，不应只抄单一 ticker。 | 未见明显统一追涨障碍或价格缺失 | 优先跟踪 | 核对消费、监管、竞争、利润率和回购/资本回报。 |
| 7 | AI电力/数据中心基础设施 | `PCG` / `HUT` / `AGX` / `TLN` / `GEV` / `ETN` / `EQIX` / `CEG` | PCG 净主动 -$0.58bn；HUT 净主动 $0.33bn；AGX 净主动 $0.22bn；Coatue：GEV/CEG/ETN 前十，EQIX 新进/恢复仓位 | Bridgewater / Coatue / Greenlight / Lone Pine / Maverick / Third Point | AI电力/数据中心基础设施 的 13F 信号来自多个标的/机构，不应只抄单一 ticker。 | 部分标的已涨，需降速验证 | 优先跟踪 | 核对数据中心订单、电力合同、互联排队和项目交付周期。 |
| 8 | 金融数据/信息收费 | `SPGI` | SPGI 净主动 -$0.21bn | Baillie / Dorsey / Himalaya | 金融数据/信息收费 的 13F 信号来自多个标的/机构，不应只抄单一 ticker。 | 未见明显统一追涨障碍或价格缺失 | 优先跟踪 | 核对订阅留存、发行周期、指数授权和数据产品定价力。 |

### Coatue 补充观察（2026-06-16 单机构页晚于横向页）

这组观察来自 [13F趋势-Coatue](/investor-masters/institutions/13f-trends-coatue/)，生成时间晚于本页原始横向计算，所以只作为校正和跟踪，不改上方原始排名。

| 线索 | 13F 事实 | 读法 |
|---|---|---|
| `EQIX / ASML` | `EQIX` 新进/恢复到 `3.7%`，`ASML` 新进/恢复到 `2.3%`。 | 一个落在数据中心互联，一个落在先进制程设备瓶颈；都不是前十，但比普通小仓位更值得跟踪。 |
| `TSM` | Coatue Q1 2026 第一大仓，`10.8%`，股数从 `8.63m` 增至 `9.28m`。 | 这是 Coatue 组合里最干净的主动增股线索，和横向页里其他机构对 `TSM` 的减仓形成分歧。 |
| `GEV / CEG / ETN` | `GEV / CEG / ETN` 仍在前十；`GEV / CEG` 股数下降，`ETN` 股数基本稳定。 | AI 电力线仍是核心资产线，但不能把 `GEV / CEG` 的权重位置误读成 Q1 主动加仓。 |
| `LRCX / AMAT / AVGO` | 三者均在前十；`LRCX` 小幅增股，`AMAT / AVGO` 股数下降或基本持平。 | 半导体设备/网络线继续重要，但 Q1 更多是组合重排和价格/权重结果，不是整条线无差别加仓。 |

### Atreides 补充观察（2026-07-23 单机构页晚于横向页）

这组观察来自 [13F趋势-Atreides](/investor-masters/institutions/13f-trends-atreides/)。它晚于本页原始横向计算，所以不改上方 21 家机构的排名和分数，只补资产线、价格过滤和反向验证。

| 线索 | 13F 事实 | 读法 |
|---|---|---|
| `ALAB / U / AMZN` | 普通股股数分别增加 `108.9% / 86.9% / 38.6%`；`ALAB` 升为普通股第一大仓。 | Atreides 在提高 AI 互连、应用修复与平台敞口，但 `ALAB` 截至 `2026-07-22` 已较季末隐含价上涨约 `201.9%`，不能把旧加仓动作直接翻成当前买入结论。 |
| `CIEN / COHR / NVDA / LITE` | 普通股股数分别减少 `52.6% / 48.9% / 35.1% / 30.2%`；其中 `LITE` 权重仍由 `3.0%` 升至 `4.6%`。 | 同属 AI 基础设施并不代表同向加仓；`LITE` 是“价格推高权重、股数却下降”的典型反例。 |
| `ZM / AKAM / VST / CRDO / PANW` | 2026Q1 新进普通股；截至 `2026-07-22`，`CRDO / PANW` 已较季末隐含价上涨约 `143.2% / 109.1%`。 | 新仓暴露了协作软件、边缘网络、电力、互连和安全五条研究线，但 CRDO/PANW 的价格已明显抢跑，只适合作为 投资论点 线索。 |
| `QQQ PUT` | 由 `3.50m` 降至 `1.40m`，SEC value `$808.05m`；`NVDA CALL`、`MU PUT` 清仓。 | 防守期权名义规模下降，但 13F 不给期权金、delta、到期日和空头，不能据此推断净敞口已转为全面看多。 |

## 共识加仓榜（普通股票；买入分高于卖出分，按风格加权净分、买入机构数、净主动变化排序）

| 股票 | 简介 | 买入侧 | 卖出侧 | 净主动变化 | 解释 |
|---|---|---|---|---:|---|
| `SUNB` | Sunbelt Rentals，设备租赁平台，核心看工程建设、工业维护和高利用率租赁网络 | Oakmark（$0.76bn，+1.0 pct）、AKO（$0.21bn，+4.1 pct）、Dorsey（$0.14bn，+11.4 pct） | 无 | `$1.11bn` | 3 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `APP` | 移动广告和应用分发平台，核心是广告模型、流量匹配和游戏/应用变现效率 | Lone Pine（$0.46bn，+0.8 pct）、Baillie（$0.36bn，-0.7 pct）、Dorsey（$0.13bn，+10.0 pct） | 无 | `$0.95bn` | 3 家加仓，且主动买入进入 2 家前十大，属于需要继续研究的增量信号。 |
| `SPGI` | S&P Global，金融数据、评级、指数和市场情报公司，核心看信息收费和指数授权 | Dorsey（$0.09bn，+7.5 pct）、Himalaya（$0.05bn，+1.6 pct） | Baillie（-$0.36bn，-0.3 pct） | `-$0.21bn` | 2 家加仓，且主动买入进入 2 家前十大，属于需要继续研究的增量信号。 |
| `LIN` | 林德，全球工业气体龙头，核心看长期供气合约、项目执行和半导体/能源等终端需求 | Maverick（$0.21bn，+2.4 pct）、AKO（$0.05bn，+1.2 pct）、Duquesne（$0.02bn，+0.6 pct） | 无 | `$0.28bn` | 3 家加仓，主要观察是否从单点动作扩散成持续共振。 |
| `UBER` | Uber，出行、外卖和本地物流平台，核心看网络密度、司机供给、广告和自动驾驶期权 | Appaloosa（股数 +242.3%，+5.5 pct）、Altimeter（股数 +42.6%，+3.2 pct）、Dorsey（新进 6.2%） | Bridgewater（-$0.10bn，-0.4 pct） | 约 `$0.6bn`（不含 Pershing 核心持有） | Dorsey 和 Appaloosa 主动买入进前十，Altimeter 主动加仓；Pershing 仍为核心仓但不计入本季买入侧。 |
| `CRDO` | Credo，面向 AI 数据中心的高速连接芯片和线缆方案公司，核心看以太网互连升级和大客户导入 | Bridgewater（$0.10bn，+0.3 pct）、H&H（$0.09bn，+0.2 pct）、Oaktree（$0.05bn，+0.8 pct） | 无 | `$0.24bn` | 3 家加仓，主要观察是否从单点动作扩散成持续共振。 |
| `CROX` | Crocs，休闲鞋品牌公司，核心看品牌热度、渠道扩张和 HeyDude 整合 | Greenlight（$0.06bn，+1.7 pct）、Himalaya（$0.02bn，+0.8 pct） | 无 | `$0.08bn` | 2 家加仓，主要观察是否从单点动作扩散成持续共振。 |
| `AGX` | Argan，电力工程和基础设施承包商，核心看燃气、电网和数据中心相关项目订单 | Lone Pine（$0.21bn，+1.7 pct）、Maverick（$0.01bn，+1.4 pct） | 无 | `$0.22bn` | 2 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `AVGO` | 博通，半导体和基础设施软件公司，AI 网络、ASIC 和 VMware 是当前核心变量 | Bridgewater（$0.23bn，+1.1 pct）、ARK（$0.13bn，+1.0 pct）、Duquesne（$0.06bn，+1.8 pct） | Lone Pine（-$0.60bn，-4.4 pct） | `-$0.16bn` | 4 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `TME` | 腾讯音乐，中国在线音乐和音频娱乐平台，核心看订阅、社交娱乐和版权生态 | Himalaya（$0.06bn，+1.9 pct） | 无 | `$0.06bn` | 1 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `HUT` | Hut 8，比特币挖矿和能源/算力基础设施公司，核心看电力成本、币价和托管算力业务 | Lone Pine（$0.29bn，+2.3 pct）、Third Point（$0.04bn，+2.0 pct） | 无 | `$0.33bn` | 2 家加仓，主要观察是否从单点动作扩散成持续共振。 |

## 共识减仓榜（普通股票；卖出分高于买入分，按风格加权净分、卖出机构数、净主动变化排序）

| 股票 | 简介 | 买入侧 | 卖出侧 | 净主动变化 | 解释 |
|---|---|---|---|---:|---|
| `TSM` | 台积电，全球领先晶圆代工厂，是先进制程和先进封装产能的关键瓶颈 | Bridgewater（$0.36bn，+1.6 pct） | Lone Pine（-$0.51bn，-3.1 pct）、H&H（-$0.33bn，-1.9 pct）、Maverick（-$0.13bn，-0.6 pct） | `-$0.69bn` | 6 家减仓，且退出 2 家前十大，信号偏负面。 |
| `V` | Visa，全球支付网络，核心看交易量、跨境支付恢复和网络抽成能力 | Baupost（$0.21bn，+4.1 pct） | Berkshire（-$2.91bn，-1.1 pct）、Citadel（-$1.37bn，-0.2 pct）、Bridgewater（-$0.18bn，-0.7 pct） | `-$4.49bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `COF` | Capital One，信用卡和消费金融银行，核心变量是信贷周期、获客成本和拨备水平 | 无 | Third Point（-$0.23bn，-2.4 pct）、Oakmark（-$0.11bn，-0.8 pct）、Maverick（-$0.01bn，-0.7 pct） | `-$0.36bn` | 4 家减仓，且退出 1 家前十大，信号偏负面。 |
| `BN` | Brookfield，全球另类资产和基础设施平台，核心是长期资本、运营资产和资本循环 | 无 | Third Point（-$0.28bn，-3.9 pct）、Lone Pine（-$0.22bn，-1.8 pct）、Pershing（-$0.08bn，-0.5 pct） | `-$0.58bn` | 3 家减仓，且退出 2 家前十大，信号偏负面。 |
| `FLTR` | Flutter，全球线上博彩和体育投注平台，FanDuel 是美国市场核心增长资产 | 无 | AKO（-$0.56bn，-9.2 pct）、Maverick（-$0.04bn，-0.4 pct）、Duquesne（-$0.02bn，-0.6 pct） | `-$0.63bn` | 3 家减仓，且退出 1 家前十大，信号偏负面。 |
| `DASH` | DoorDash，本地配送和外卖平台，核心看订单密度、商户网络和非餐品类扩张 | 无 | Lone Pine（-$0.57bn，-4.2 pct）、Baillie（-$0.16bn，-0.4 pct）、Maverick（-$0.08bn，-0.9 pct） | `-$0.82bn` | 3 家减仓，且退出 1 家前十大，信号偏负面。 |
| `MSFT` | 微软，企业软件、Azure 云、Office、Windows 和 AI 基础设施共同构成的生产力平台 | Pershing（$2.09bn，+15.3 pct）、H&H（$0.08bn，-0.5 pct） | Baillie（-$0.81bn，-0.8 pct）、Lone Pine（-$0.60bn，-4.4 pct）、Third Point（-$0.45bn，-6.1 pct） | `-$0.02bn` | 5 家减仓，且退出 2 家前十大，信号偏负面。 |
| `BABA` | 阿里巴巴，电商、云、国际零售和本地生活组合，核心看中国消费、平台效率和云业务重估 | 无 | H&H（-$0.38bn，-2.1 pct）、Third Point（-$0.12bn，-1.7 pct） | `-$0.50bn` | 2 家减仓，且退出 1 家前十大，信号偏负面。 |
| `PM` | Philip Morris，烟草和无烟尼古丁公司，核心看 IQOS 等新型烟草迁移和定价力 | 无 | Lone Pine（-$0.42bn，-3.1 pct）、Maverick（-$0.26bn，-2.7 pct）、Fundsmith（-$0.16bn，+0.9 pct） | `-$0.84bn` | 3 家减仓，且退出 1 家前十大，信号偏负面。 |
| `BAC` | 美国银行，大型综合银行，核心变量是存款成本、贷款质量、利率周期和资本回报 | 无 | Himalaya（-$0.41bn，-11.5 pct）、Berkshire（-$0.20bn，-0.9 pct） | `-$0.61bn` | 2 家减仓，主要观察是否只是调仓还是 投资论点 变化。 |

## 新进前十大榜（本季进入机构前 10、上季不在前 10；按进入机构数、买入分、净主动变化排序）

| 股票 | 简介 | 买入侧 | 卖出侧 | 净主动变化 | 解释 |
|---|---|---|---|---:|---|
| `APP` | 移动广告和应用分发平台，核心是广告模型、流量匹配和游戏/应用变现效率 | Lone Pine（$0.46bn，+0.8 pct）、Baillie（$0.36bn，-0.7 pct）、Dorsey（$0.13bn，+10.0 pct） | 无 | `$0.95bn` | 3 家加仓，且主动买入进入 2 家前十大，属于需要继续研究的增量信号。 |
| `SPGI` | S&P Global，金融数据、评级、指数和市场情报公司，核心看信息收费和指数授权 | Dorsey（$0.09bn，+7.5 pct）、Himalaya（$0.05bn，+1.6 pct） | Baillie（-$0.36bn，-0.3 pct） | `-$0.21bn` | 2 家加仓，且主动买入进入 2 家前十大，属于需要继续研究的增量信号。 |
| `NU` | Nu Holdings，拉美数字银行平台，核心看低成本获客、信贷风控和金融产品交叉销售 | Maverick（$0.18bn，+1.6 pct）、Lone Pine（$0.14bn，+0.7 pct） | Oaktree（-$0.07bn，-1.1 pct） | `$0.24bn` | 2 家加仓，且主动买入进入 2 家前十大，属于需要继续研究的增量信号。 |
| `CRS` | Carpenter Technology，特种合金和高性能材料公司，服务航空航天、医疗和能源等场景 | Lone Pine（$0.16bn，+2.7 pct） | Third Point（-$0.15bn，+2.5 pct） | `$0.01bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `SUNB` | Sunbelt Rentals，设备租赁平台，核心看工程建设、工业维护和高利用率租赁网络 | Oakmark（$0.76bn，+1.0 pct）、AKO（$0.21bn，+4.1 pct）、Dorsey（$0.14bn，+11.4 pct） | 无 | `$1.11bn` | 3 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `AVGO` | 博通，半导体和基础设施软件公司，AI 网络、ASIC 和 VMware 是当前核心变量 | Bridgewater（$0.23bn，+1.1 pct）、ARK（$0.13bn，+1.0 pct）、Duquesne（$0.06bn，+1.8 pct） | Lone Pine（-$0.60bn，-4.4 pct） | `-$0.16bn` | 4 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `MSFT` | 微软，企业软件、Azure 云、Office、Windows 和 AI 基础设施共同构成的生产力平台 | Pershing（$2.09bn，+15.3 pct）、H&H（$0.08bn，-0.5 pct） | Baillie（-$0.81bn，-0.8 pct）、Lone Pine（-$0.60bn，-4.4 pct）、Third Point（-$0.45bn，-6.1 pct） | `-$0.02bn` | 5 家减仓，且退出 2 家前十大，信号偏负面。 |
| `TSLA` | 特斯拉，电动车、储能和自动驾驶平台公司，核心变量是制造效率、FSD 与 Robotaxi 期权 | H&H（$1.27bn，+6.3 pct）、Tudor（$0.24bn，+0.4 pct） | ARK（-$0.04bn，-0.5 pct） | `$1.47bn` | 2 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `UBER` | Uber，出行、外卖和本地物流平台，核心看网络密度、司机供给、广告和自动驾驶期权 | Appaloosa（股数 +242.3%，+5.5 pct）、Altimeter（股数 +42.6%，+3.2 pct）、Dorsey（新进 6.2%）、Tudor（$4.82bn，+0.1 pct） | Bridgewater（-$0.10bn，-0.4 pct） | `$5.3bn+` | Dorsey 和 Appaloosa 主动买入进前十，Altimeter 是已有核心仓主动加仓；Pershing 仍为第三大核心仓，但不是本季主动买入。 |
| `AGX` | Argan，电力工程和基础设施承包商，核心看燃气、电网和数据中心相关项目订单 | Lone Pine（$0.21bn，+1.7 pct）、Maverick（$0.01bn，+1.4 pct） | 无 | `$0.22bn` | 2 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |

## 退出前十大榜（上季在机构前 10、本季退出；按退出机构数、卖出分、净主动变化排序）

| 股票 | 简介 | 买入侧 | 卖出侧 | 净主动变化 | 解释 |
|---|---|---|---|---:|---|
| `GOOG/GOOGL` | Alphabet 的 A 类股，核心资产是 Google 搜索、YouTube、广告网络、Android 和 Google Cloud | Berkshire（$11.39bn，+3.9 pct）、Berkshire（$1.03bn，+0.4 pct）、H&H（$0.58bn，+2.0 pct） | Pershing（-$1.84bn，-11.8 pct）、Pershing（-$0.20bn，-1.3 pct）、Fundsmith（-$0.17bn，+0.2 pct） | `$10.78bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `MSFT` | 微软，企业软件、Azure 云、Office、Windows 和 AI 基础设施共同构成的生产力平台 | Pershing（$2.09bn，+15.3 pct）、H&H（$0.08bn，-0.5 pct） | Baillie（-$0.81bn，-0.8 pct）、Lone Pine（-$0.60bn，-4.4 pct）、Third Point（-$0.45bn，-6.1 pct） | `-$0.02bn` | 5 家减仓，且退出 2 家前十大，信号偏负面。 |
| `TSM` | 台积电，全球领先晶圆代工厂，是先进制程和先进封装产能的关键瓶颈 | Bridgewater（$0.36bn，+1.6 pct） | Lone Pine（-$0.51bn，-3.1 pct）、H&H（-$0.33bn，-1.9 pct）、Maverick（-$0.13bn，-0.6 pct） | `-$0.69bn` | 6 家减仓，且退出 2 家前十大，信号偏负面。 |
| `BN` | Brookfield，全球另类资产和基础设施平台，核心是长期资本、运营资产和资本循环 | 无 | Third Point（-$0.28bn，-3.9 pct）、Lone Pine（-$0.22bn，-1.8 pct）、Pershing（-$0.08bn，-0.5 pct） | `-$0.58bn` | 3 家减仓，且退出 2 家前十大，信号偏负面。 |
| `UNP` | 联合太平洋，美国西部铁路网络，核心看货运量、价格、运营效率和基础设施稀缺性 | Bridgewater（$0.11bn，+0.5 pct） | Third Point（-$0.40bn，-4.6 pct）、Maverick（-$0.30bn，-3.3 pct） | `-$0.59bn` | 2 家减仓，且退出 2 家前十大，信号偏负面。 |
| `TEVA` | 梯瓦制药，仿制药和专科药公司，核心看债务去化、核心药物增长和诉讼风险 | 无 | Duquesne（-$0.11bn，-2.0 pct）、Greenlight（-$0.00bn，-0.6 pct） | `-$0.11bn` | 2 家减仓，且退出 2 家前十大，信号偏负面。 |
| `AMZN` | 电商、物流、AWS 云和广告共同构成的平台公司，长期变量是基础设施外部化能力 | Bridgewater（$0.56bn，+2.4 pct）、Pershing（$0.43bn，+3.1 pct）、Baupost（$0.23bn，+3.4 pct） | Citadel（-$1.39bn，-0.2 pct）、Lone Pine（-$0.56bn，-4.1 pct）、Baillie（-$0.30bn，+0.3 pct） | `-$1.38bn` | 8 家减仓，且退出 1 家前十大，信号偏负面。 |
| `COF` | Capital One，信用卡和消费金融银行，核心变量是信贷周期、获客成本和拨备水平 | 无 | Third Point（-$0.23bn，-2.4 pct）、Oakmark（-$0.11bn，-0.8 pct）、Maverick（-$0.01bn，-0.7 pct） | `-$0.36bn` | 4 家减仓，且退出 1 家前十大，信号偏负面。 |
| `NVDA` | AI 加速计算平台，GPU、网络和 CUDA 生态共同支撑数据中心算力需求 | H&H（$1.23bn，+4.4 pct）、Bridgewater（$0.15bn，+1.0 pct）、Maverick（$0.04bn，+0.4 pct） | Baillie（-$0.58bn，+0.5 pct）、Third Point（-$0.51bn，-6.0 pct）、Tudor（-$0.21bn，-0.4 pct） | `$0.07bn` | 4 家减仓，且退出 1 家前十大，信号偏负面。 |
| `FLTR` | Flutter，全球线上博彩和体育投注平台，FanDuel 是美国市场核心增长资产 | 无 | AKO（-$0.56bn，-9.2 pct）、Maverick（-$0.04bn，-0.4 pct）、Duquesne（-$0.02bn，-0.6 pct） | `-$0.63bn` | 3 家减仓，且退出 1 家前十大，信号偏负面。 |

## 集中度上升榜（单一机构内权重提升至少 0.3pct；按机构数、买入分、净主动变化排序）

| 股票 | 简介 | 买入侧 | 卖出侧 | 净主动变化 | 解释 |
|---|---|---|---|---:|---|
| `GOOG/GOOGL` | Alphabet 的 A 类股，核心资产是 Google 搜索、YouTube、广告网络、Android 和 Google Cloud | Berkshire（$11.39bn，+3.9 pct）、Berkshire（$1.03bn，+0.4 pct）、H&H（$0.58bn，+2.0 pct） | Pershing（-$1.84bn，-11.8 pct）、Pershing（-$0.20bn，-1.3 pct）、Fundsmith（-$0.17bn，+0.2 pct） | `$10.78bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `AMZN` | 电商、物流、AWS 云和广告共同构成的平台公司，长期变量是基础设施外部化能力 | Bridgewater（$0.56bn，+2.4 pct）、Pershing（$0.43bn，+3.1 pct）、Baupost（$0.23bn，+3.4 pct） | Citadel（-$1.39bn，-0.2 pct）、Lone Pine（-$0.56bn，-4.1 pct）、Baillie（-$0.30bn，+0.3 pct） | `-$1.38bn` | 8 家减仓，且退出 1 家前十大，信号偏负面。 |
| `AVGO` | 博通，半导体和基础设施软件公司，AI 网络、ASIC 和 VMware 是当前核心变量 | Bridgewater（$0.23bn，+1.1 pct）、ARK（$0.13bn，+1.0 pct）、Duquesne（$0.06bn，+1.8 pct） | Lone Pine（-$0.60bn，-4.4 pct） | `-$0.16bn` | 4 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `NVDA` | AI 加速计算平台，GPU、网络和 CUDA 生态共同支撑数据中心算力需求 | H&H（$1.23bn，+4.4 pct）、Bridgewater（$0.15bn，+1.0 pct）、Maverick（$0.04bn，+0.4 pct） | Baillie（-$0.58bn，+0.5 pct）、Third Point（-$0.51bn，-6.0 pct）、Tudor（-$0.21bn，-0.4 pct） | `$0.07bn` | 4 家减仓，且退出 1 家前十大，信号偏负面。 |
| `SUNB` | Sunbelt Rentals，设备租赁平台，核心看工程建设、工业维护和高利用率租赁网络 | Oakmark（$0.76bn，+1.0 pct）、AKO（$0.21bn，+4.1 pct）、Dorsey（$0.14bn，+11.4 pct） | 无 | `$1.11bn` | 3 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `UBER` | Uber，出行、外卖和本地物流平台，核心看网络密度、司机供给、广告和自动驾驶期权 | Appaloosa（股数 +242.3%，+5.5 pct）、Altimeter（股数 +42.6%，+3.2 pct）、Dorsey（新进 6.2%） | Bridgewater（-$0.10bn，-0.4 pct） | 约 `$0.6bn`（不含 Pershing 核心持有） | 至少 3 家机构权重明显上升，其中两家主动买入进前十，是本季公司页需要补写的典型漏项。 |
| `LIN` | 林德，全球工业气体龙头，核心看长期供气合约、项目执行和半导体/能源等终端需求 | Maverick（$0.21bn，+2.4 pct）、AKO（$0.05bn，+1.2 pct）、Duquesne（$0.02bn，+0.6 pct） | 无 | `$0.28bn` | 3 家加仓，主要观察是否从单点动作扩散成持续共振。 |
| `ASML` | 阿斯麦，EUV/DUV 光刻机龙头，是先进半导体制造最稀缺的设备瓶颈之一 | Lone Pine（$0.05bn，+2.1 pct）、Third Point（$0.02bn，+0.8 pct） | Dorsey（-$0.06bn，-3.1 pct）、Maverick（-$0.00bn，+0.9 pct） | `$0.01bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `TSM` | 台积电，全球领先晶圆代工厂，是先进制程和先进封装产能的关键瓶颈 | Bridgewater（$0.36bn，+1.6 pct） | Lone Pine（-$0.51bn，-3.1 pct）、H&H（-$0.33bn，-1.9 pct）、Maverick（-$0.13bn，-0.6 pct） | `-$0.69bn` | 6 家减仓，且退出 2 家前十大，信号偏负面。 |
| `APP` | 移动广告和应用分发平台，核心是广告模型、流量匹配和游戏/应用变现效率 | Lone Pine（$0.46bn，+0.8 pct）、Baillie（$0.36bn，-0.7 pct）、Dorsey（$0.13bn，+10.0 pct） | 无 | `$0.95bn` | 3 家加仓，且主动买入进入 2 家前十大，属于需要继续研究的增量信号。 |
| `SPGI` | S&P Global，金融数据、评级、指数和市场情报公司，核心看信息收费和指数授权 | Dorsey（$0.09bn，+7.5 pct）、Himalaya（$0.05bn，+1.6 pct） | Baillie（-$0.36bn，-0.3 pct） | `-$0.21bn` | 2 家加仓，且主动买入进入 2 家前十大，属于需要继续研究的增量信号。 |

## 机构分歧榜（同一普通股票同时有买入侧和卖出侧；按买卖两侧较弱分、参与机构数排序）

| 股票 | 简介 | 买入侧 | 卖出侧 | 净主动变化 | 解释 |
|---|---|---|---|---:|---|
| `GOOG/GOOGL` | Alphabet 的 A 类股，核心资产是 Google 搜索、YouTube、广告网络、Android 和 Google Cloud | Berkshire（$11.39bn，+3.9 pct）、Berkshire（$1.03bn，+0.4 pct）、H&H（$0.58bn，+2.0 pct） | Pershing（-$1.84bn，-11.8 pct）、Pershing（-$0.20bn，-1.3 pct）、Fundsmith（-$0.17bn，+0.2 pct） | `$10.78bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `AMZN` | 电商、物流、AWS 云和广告共同构成的平台公司，长期变量是基础设施外部化能力 | Bridgewater（$0.56bn，+2.4 pct）、Pershing（$0.43bn，+3.1 pct）、Baupost（$0.23bn，+3.4 pct） | Citadel（-$1.39bn，-0.2 pct）、Lone Pine（-$0.56bn，-4.1 pct）、Baillie（-$0.30bn，+0.3 pct） | `-$1.38bn` | 8 家减仓，且退出 1 家前十大，信号偏负面。 |
| `NVDA` | AI 加速计算平台，GPU、网络和 CUDA 生态共同支撑数据中心算力需求 | H&H（$1.23bn，+4.4 pct）、Bridgewater（$0.15bn，+1.0 pct）、Maverick（$0.04bn，+0.4 pct） | Baillie（-$0.58bn，+0.5 pct）、Third Point（-$0.51bn，-6.0 pct）、Tudor（-$0.21bn，-0.4 pct） | `$0.07bn` | 4 家减仓，且退出 1 家前十大，信号偏负面。 |
| `MSFT` | 微软，企业软件、Azure 云、Office、Windows 和 AI 基础设施共同构成的生产力平台 | Pershing（$2.09bn，+15.3 pct）、H&H（$0.08bn，-0.5 pct） | Baillie（-$0.81bn，-0.8 pct）、Lone Pine（-$0.60bn，-4.4 pct）、Third Point（-$0.45bn，-6.1 pct） | `-$0.02bn` | 5 家减仓，且退出 2 家前十大，信号偏负面。 |
| `META` | Meta，社交网络、广告系统和 AI 推荐平台，核心资产是 Facebook、Instagram、WhatsApp 和广告模型 | Tudor（$0.12bn，+0.2 pct）、Third Point（$0.05bn，+2.5 pct）、Dorsey（$0.00bn，-1.8 pct） | ARK（-$0.10bn，-0.6 pct）、Fundsmith（-$0.03bn，+0.6 pct）、Giverny（-$0.00bn，-0.5 pct） | `$0.05bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `BKNG` | 在线旅游平台，Booking.com 是核心资产，受益于全球住宿供给、流量和转化效率 | AKO（$0.04bn，+0.6 pct）、Dorsey（$0.00bn，-2.1 pct） | Bridgewater（-$0.43bn，-1.6 pct）、Giverny（-$0.00bn，-0.6 pct） | `-$0.39bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `ASML` | 阿斯麦，EUV/DUV 光刻机龙头，是先进半导体制造最稀缺的设备瓶颈之一 | Lone Pine（$0.05bn，+2.1 pct）、Third Point（$0.02bn，+0.8 pct） | Dorsey（-$0.06bn，-3.1 pct）、Maverick（-$0.00bn，+0.9 pct） | `$0.01bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `V` | Visa，全球支付网络，核心看交易量、跨境支付恢复和网络抽成能力 | Baupost（$0.21bn，+4.1 pct） | Berkshire（-$2.91bn，-1.1 pct）、Citadel（-$1.37bn，-0.2 pct）、Bridgewater（-$0.18bn，-0.7 pct） | `-$4.49bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `AVGO` | 博通，半导体和基础设施软件公司，AI 网络、ASIC 和 VMware 是当前核心变量 | Bridgewater（$0.23bn，+1.1 pct）、ARK（$0.13bn，+1.0 pct）、Duquesne（$0.06bn，+1.8 pct） | Lone Pine（-$0.60bn，-4.4 pct） | `-$0.16bn` | 4 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `UNH` | 联合健康，医保和医疗服务平台公司，核心看医疗成本率、政策风险和 Optum 服务能力 | H&H（$0.16bn，+0.8 pct） | Berkshire（-$1.66bn，-0.6 pct） | `-$1.50bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |

## 宏观与交易工具（ETF、指数工具与 PUT/CALL；按参与机构数和净主动变化排序）

| 标的 | 简介 | 买入侧 | 卖出侧 | 净主动变化 | 解释 |
|---|---|---|---|---:|---|
| `IVV` | iShares Core S&P 500 ETF，用来表达美国大盘指数暴露 | Citadel（$0.66bn，+0.5 pct） | Bridgewater（-$0.82bn，-2.6 pct）、Duquesne（-$0.05bn，-1.1 pct） | `-$0.20bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `SPY PUT` | 标普 500 ETF，用来表达美国大盘指数暴露，也常被交易型机构用于期权和对冲 | Citadel（$5.62bn，+0.9 pct） | Tudor（-$0.59bn，-1.1 pct） | `$5.03bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `IVV CALL` | iShares Core S&P 500 ETF，用来表达美国大盘指数暴露 | Citadel（$2.83bn，+0.3 pct） | Duquesne（-$0.04bn，-0.7 pct） | `$2.80bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `TSLA PUT` | 特斯拉，电动车、储能和自动驾驶平台公司，核心变量是制造效率、FSD 与 Robotaxi 期权 | Tudor（$0.31bn，+0.4 pct） | Citadel（-$3.02bn，-0.6 pct） | `-$2.71bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `NVDA CALL` | AI 加速计算平台，GPU、网络和 CUDA 生态共同支撑数据中心算力需求 | Tudor（$0.18bn，+0.3 pct） | Citadel（-$2.06bn，-0.3 pct） | `-$1.88bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `QQQ PUT` | 纳斯达克 100 ETF，用来表达大型科技和成长股指数暴露 | Oaktree（$0.33bn，+5.0 pct）、Tudor（$0.15bn，+0.0 pct） | 无 | `$0.48bn` | 2 家加仓，且主动买入进入 1 家前十大，属于需要继续研究的增量信号。 |
| `SPY` | 标普 500 ETF，用来表达美国大盘指数暴露，也常被交易型机构用于期权和对冲 | Tudor（$0.46bn，+0.8 pct） | Bridgewater（-$0.06bn，+1.6 pct） | `$0.40bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `SMH PUT` | VanEck Semiconductor ETF，用来表达半导体设计、设备和制造产业链暴露 | Tudor（$0.14bn，+0.3 pct） | Oaktree（-$0.31bn，-4.4 pct） | `-$0.17bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `Ishares` | iShares ETF 工具，用来表达指数、国家/地区或资产类别暴露 | Bridgewater（$0.07bn，+0.7 pct） | Duquesne（-$0.00bn，+1.4 pct） | `$0.07bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
| `GLD` | 暂无简介 | Third Point（$0.04bn，+2.0 pct） | Greenlight（-$0.03bn，-1.0 pct） | `$0.01bn` | 买卖两边同时出现，更像分歧扩大，不适合直接当成共识。 |
