from __future__ import annotations

import os
import re
import shutil
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VAULT = Path(os.environ.get("INVESTORS_VAULT", ROOT / "vault")).expanduser()
WIKI_DIR = VAULT / "wiki"
RAW_DIR = VAULT / "raw"
DOCS_DIR = ROOT / "src" / "content" / "docs"
SITE_BASE = "/investor-masters"

if not VAULT.exists():
    raise SystemExit(
        "Vault not found. Set INVESTORS_VAULT to your Obsidian vault root before running compile_site.py."
    )


INVESTOR_META = {
    "沃伦·巴菲特": {
        "slug": "warren-buffett",
        "tagline": "把投资变成企业所有者游戏的人。",
        "institution": ("Berkshire Hathaway", "institutions/berkshire-hathaway"),
        "holdings": "可口可乐、美国运通",
        "methods": "企业所有者 / 护城河 / 资本配置",
    },
    "查理·芒格": {
        "slug": "charlie-munger",
        "tagline": "用多学科框架压缩复杂世界的人。",
        "institution": ("Berkshire Hathaway", "institutions/berkshire-hathaway"),
        "holdings": "伯克希尔、好企业筛选",
        "methods": "多学科 / 反愚蠢 / 高质量企业",
    },
    "霍华德·马克斯": {
        "slug": "howard-marks",
        "tagline": "把风险语言写得比大多数人更清楚的人。",
        "institution": ("Oaktree Capital", "institutions/oaktree-capital"),
        "holdings": "信贷、困境资产",
        "methods": "周期 / 赔率 / 风险控制",
    },
    "比尔·米勒": {
        "slug": "bill-miller",
        "tagline": "用未来折现去打破传统价值边界的人。",
        "institution": ("Legg Mason", None),
        "holdings": "亚马逊、比特币",
        "methods": "时间套利 / 非传统价值 / 未来现金流",
    },
    "比尔·尼格伦": {
        "slug": "bill-nygren",
        "tagline": "把现代无形资产、七年估值和卖出纪律接回价值投资的人。",
        "institution": ("Oakmark Funds", "institutions/oakmark-funds"),
        "holdings": "Netflix、Salesforce、Airbnb、Alphabet、银行股",
        "methods": "Oakmark 会计 / 七年企业价值 / 现代价值 / 卖出纪律",
    },
    "李·安斯利": {
        "slug": "lee-ainslie",
        "tagline": "把老虎基金学徒制压成行业专家制的人。",
        "institution": ("Maverick Capital", "institutions/maverick-capital"),
        "holdings": "行业多空、管理层研究",
        "methods": "行业专家制 / 长短仓 / 资本配置判断",
    },
    "迈克尔·洛温斯坦与托马斯·科尔曼": {
        "slug": "michael-lowenstein-thomas-coleman",
        "tagline": "用低公开曝光和连续组合行为证明自己的 Kensico 核心人物。",
        "institution": ("Kensico Capital Management", "institutions/kensico-capital-management"),
        "holdings": "AppLovin、Howmet、FICO、Alphabet、Visa",
        "methods": "低公开曝光 / 组合型证据 / 集中持仓",
    },
    "大卫·艾因霍恩": {
        "slug": "david-einhorn",
        "tagline": "把反动量、会计审问与多空结构写进机构语言的人。",
        "institution": ("Greenlight Capital", "institutions/greenlight-capital"),
        "holdings": "分拆错价、结构性空头、黄金对冲",
        "methods": "反动量 / 透明度审问 / 法证式多空",
    },
    "尼克·特雷恩": {
        "slug": "nick-train",
        "tagline": "把极低换手、能力圈边界和长期特许经营持有推到极致的人。",
        "institution": ("Lindsell Train", "institutions/lindsell-train"),
        "holdings": "帝亚吉欧、伦敦证券交易所集团、RELX",
        "methods": "慢买入、长持有 / 高质量特许经营 / 低换手",
    },
    "特里·史密斯": {
        "slug": "terry-smith",
        "tagline": "相信挑对公司之后几乎不需要再做什么的人。",
        "institution": ("Fundsmith", "institutions/fundsmith"),
        "holdings": "微软、诺和诺德",
        "methods": "高质量复利 / 少犯错 / 长期持有",
    },
    "弗朗索瓦·罗雄": {
        "slug": "francois-rochon",
        "tagline": "把所有者收益、质量企业和错误复盘绑成长期复利方法的人。",
        "institution": ("Giverny Capital", "institutions/giverny-capital"),
        "holdings": "Alphabet、Berkshire、Meta、Visa、O'Reilly",
        "methods": "所有者收益 / 质量投资 / 错误复盘",
    },
    "段永平": {
        "slug": "duan-yongping",
        "tagline": "把“不懂不碰”执行到生活方式里的投资人。",
        "institution": ("H&H International Investment", "institutions/h-h-international-investment"),
        "holdings": "苹果、BRK.B、英伟达、拼多多",
        "methods": "本分 / 看懂 / 打孔机",
    },
    "詹姆斯·安德森": {
        "slug": "james-anderson",
        "tagline": "愿意为超级赢家承担长时间误解的人。",
        "institution": ("Baillie Gifford", "institutions/baillie-gifford"),
        "holdings": "Tesla、Amazon",
        "methods": "超级赢家 / 非共识成长 / 长期主义",
    },
    "汤姆·斯莱特": {
        "slug": "tom-slater",
        "tagline": "把安德森式成长哲学继续执行下去的人。",
        "institution": ("Baillie Gifford", "institutions/baillie-gifford"),
        "holdings": "SpaceX、软件资产",
        "methods": "成长分布 / 长持 / 约束迁移",
    },
    "劳伦斯·伯恩斯": {
        "slug": "lawrence-burns",
        "tagline": "沿着整条技术价值链去布局成长资产的人。",
        "institution": ("Baillie Gifford", "institutions/baillie-gifford"),
        "holdings": "SpaceX、MiniMax",
        "methods": "价值链布局 / AI / 未上市成长",
    },
    "莫尼什·帕伯莱": {
        "slug": "monish-pabrai",
        "tagline": "把复制优秀先例当成正式方法的人。",
        "institution": ("Pabrai Funds", None),
        "holdings": "巴菲特学派、集中投资",
        "methods": "克隆 / 集中 / 巴芒学习",
    },
    "比尔·阿克曼": {
        "slug": "bill-ackman",
        "tagline": "把投资做成公开战役的人。",
        "institution": ("Pershing Square", None),
        "holdings": "集中持仓、事件驱动",
        "methods": "催化剂 / 主动所有者 / 战役型投资",
    },
    "丹·勒布": {
        "slug": "dan-loeb",
        "tagline": "把事件驱动、催化剂与跨资本结构配置绑成一台组合机器的人。",
        "institution": ("Third Point", "institutions/third-point"),
        "holdings": "事件驱动权益、信用机会、主动推动仓位",
        "methods": "事件驱动 / 催化剂 / 跨资本结构",
    },
    "斯坦利·德鲁肯米勒": {
        "slug": "stanley-druckenmiller",
        "tagline": "知道什么时候该把仓位做大的人。",
        "institution": ("Duquesne Family Office", "institutions/duquesne-family-office"),
        "holdings": "宏观趋势、成长拐点",
        "methods": "仓位 / 趋势 / 快速修正",
    },
    "大卫·泰珀": {
        "slug": "david-tepper",
        "tagline": "把政策反应函数、困境资产和仓位切换压成 Appaloosa 方法的人。",
        "institution": ("Appaloosa Management", "institutions/appaloosa-management"),
        "holdings": "政策交易、中国互联网、大科技、半导体、电力",
        "methods": "政策反应函数 / 困境资产 / 高机动仓位",
    },
    "保罗·都铎·琼斯": {
        "slug": "paul-tudor-jones",
        "tagline": "把流动性、趋势、催化剂和风险预案压成交易员方法的人。",
        "institution": ("Tudor Investment Corporation", "institutions/tudor-investment-corporation"),
        "holdings": "全球宏观、ETF/期权表达、趋势交易",
        "methods": "流动性 / 趋势 / 风险管理 / 执行预案",
    },
    "托德·库姆斯": {
        "slug": "todd-combs",
        "tagline": "把复杂商业问题压缩成可执行单元的人。",
        "institution": ("Berkshire Hathaway", "institutions/berkshire-hathaway"),
        "holdings": "GEICO、伯克希尔资金池",
        "methods": "简化 / 单店经济学 / 资本配置",
    },
    "泰德·韦施勒": {
        "slug": "ted-weschler",
        "tagline": "低调但长期业绩极扎实的伯克希尔传承者。",
        "institution": ("Berkshire Hathaway", "institutions/berkshire-hathaway"),
        "holdings": "Peninsula、伯克希尔证券投资",
        "methods": "长期关系 / 清晰判断 / 低噪音",
    },
    "尼克·斯利普": {
        "slug": "nick-sleep",
        "tagline": "把长期主义写进收费结构和生活方式的人。",
        "institution": ("Nomad Investment Partnership", "institutions/nomad-investment-partnership"),
        "holdings": "Amazon、Costco",
        "methods": "共享规模经济 / 长期集中 / 反噪音",
    },
    "史蒂芬·曼德尔": {
        "slug": "stephen-mandel",
        "tagline": "围绕关键变化下注、同时坚持深企业研究的人。",
        "institution": ("Lone Pine Capital", "institutions/lone-pine-capital"),
        "holdings": "高质量成长、结构变化受益者",
        "methods": "变化驱动投资 / 深企业研究 / 组织传承",
    },
    "凯斯·扎卡里亚": {
        "slug": "qais-zakaria",
        "tagline": "与 Sleep 一起把漫长而简单的游戏做成实验的人。",
        "institution": ("Nomad Investment Partnership", "institutions/nomad-investment-partnership"),
        "holdings": "Amazon、Costco",
        "methods": "长期集中 / 自我约束 / 共享规模经济",
    },
    "格雷格·詹森": {
        "slug": "greg-jensen",
        "tagline": "把宏观、AI 和知识复利编进同一台机器的人。",
        "institution": ("Bridgewater", None),
        "holdings": "Pure Alpha、OpenAI 早期个人投资",
        "methods": "制度拐点 / 分散 / 系统化研究",
    },
    "格雷格·阿贝尔": {
        "slug": "greg-abel",
        "tagline": "把经营接口和资本配置接口接在一起的伯克希尔继任 allocator。",
        "institution": ("Berkshire Hathaway", "institutions/berkshire-hathaway"),
        "holdings": "伯克希尔、Kraft Heinz",
        "methods": "资本桶排序 / owner alignment / 经营现实",
    },
    "凯茜·伍德": {
        "slug": "cathie-wood",
        "tagline": "把一级市场技术地图搬进二级市场组合的人。",
        "institution": ("ARK Invest", "institutions/ark-invest"),
        "holdings": "Tesla、SpaceX、Palantir",
        "methods": "平台收敛 / 生产率跃迁 / 公开市场风投",
    },
    "尼科莱·坦根": {
        "slug": "nicolai-tangen",
        "tagline": "把投资理解成情报学与组织训练的人。",
        "institution": ("挪威主权财富基金", None),
        "holdings": "AKO、主权基金配置",
        "methods": "提问 / 情报学 / 组织训练",
    },
    "李录": {
        "slug": "li-lu",
        "tagline": "把知识诚实、公司专才和长期所有者逻辑绑在一起的人。",
        "institution": ("Himalaya Capital", "institutions/himalaya-capital"),
        "holdings": "比亚迪、长期所有权",
        "methods": "知识诚实 / 专才研究 / 长持 / 制度红利",
    },
    "肯·格里芬": {
        "slug": "ken-griffin",
        "tagline": "把人才密度、平台方法与市场底层管道敏感度合成机构优势的人。",
        "institution": ("Citadel", "institutions/citadel"),
        "holdings": "多策略平台、制度裂缝、风险系统",
        "methods": "平台建造 / 独立思考 / 底层管道风险",
    },
    "特蕾西·布里特·库尔": {
        "slug": "tracy-britt-cool",
        "tagline": "从伯克希尔原则出发，把长期主义压进经营系统的人。",
        "institution": ("Kanbrick", None),
        "holdings": "Kanbrick、中型企业长期持有",
        "methods": "经营型投资 / 文化优先 / 资本配置",
    },
    "塞思·卡拉曼": {
        "slug": "seth-klarman",
        "tagline": "把高现金、逆向纪律与耐心资本写成机构宪法的人。",
        "institution": ("Baupost Group", "institutions/baupost-group"),
        "holdings": "高现金、跨资产错价、危机便宜货",
        "methods": "风险优先 / 耐心资本 / 跨资产价值投资",
    },
    "纳瓦尔·拉维坎特": {
        "slug": "naval-ravikant",
        "tagline": "把财富、判断力、知识与品味压缩成个人操作系统的人。",
        "institution": ("独立 / 创业者投资人", None),
        "holdings": "创业投资、知识杠杆、个人项目",
        "methods": "知识 / 判断力 / 品味",
    },
}

INVESTOR_INFO_SOURCES = {
    "沃伦·巴菲特": "巴菲特的信息来源偏向低频而高确信度。他主要依赖年报、管理层沟通、长期经营数据和对商业模式的反复比较，而不是高频市场噪音。对他来说，最重要的信息不是某个季度的新消息，而是企业护城河、资本配置和管理层品性的长期可验证证据。",
    "查理·芒格": "芒格的信息来源极少是单一渠道，而更像多学科交叉验证。他会把企业经营事实、心理学偏差、行业结构和历史案例放在一起看，尤其擅长从反常识现象和人性弱点里找到判断锚点。对他而言，来源本身不神秘，关键是有没有经过足够严格的交叉检查。",
    "霍华德·马克斯": "马克斯的信息来源更偏市场温度计，而不是单个公司故事。他高度关注信用利差、融资条件、投资者情绪、风险偏好和市场行为的摆动，通过这些指标判断周期走到了哪里。换句话说，他靠的是赔率环境和情绪环境，而不只是资产本身的静态价值。",
    "比尔·米勒": "米勒对信息来源的定义最宽。他明确认为，只要你理解一个信息渠道的优点和盲点，几乎任何来源都可以有用。这使他既愿意读传统财报，也愿意重视市场忽视的新技术、新资产类别和非主流叙事，关键是把这些信息放回未来现金流和长期价值的框架里。",
    "比尔·尼格伦": "尼格伦的信息来源更像一套组织化价值排序系统。他依赖财报、管理层会面、分析师数月研究、全团队挑刺和批准名单，把各种公司统一放回七年企业价值、Oakmark 会计和组合改善问题里比较。对他来说，信息的价值不在于更快，而在于能否让估值更接近真实。",
    "李·安斯利": "李·安斯利的信息来源带有非常强的 Tiger 味道：少而深的行业覆盖、长期关系网络、对管理层和 CFO 的持续交叉验证，以及对资本配置和透明度的反复追问。对他来说，信息优势不是拿到一条神秘消息，而是比别人更持续、更立体地理解一个行业和其中的赢家、输家。",
    "尼克·特雷恩": "尼克·特雷恩的信息来源极其克制，核心还是年报、长期经营记录、品牌与 franchise 的持续表现，以及管理层质量和资本配置行为的长期可验证证据。他几乎不靠宏观预测来形成判断，更像是在少数能看懂的长期资产里反复确认“这家公司十年后二十年后是否仍然更强”。",
    "特里·史密斯": "特里·史密斯的信息来源偏向企业基本面本身，而不是外部故事。他反复盯收入质量、资本回报率、现金流、管理层纪律和竞争地位，核心是从企业长期报表里提炼出“这是不是一台高质量复利机器”。他不太依赖宏观预测，也不太依赖复杂渠道优势。",
    "弗朗索瓦·罗雄": "弗朗索瓦·罗雄的信息来源偏向长期企业所有者视角。他主要依赖年报、年度信、管理层资本配置、企业文化和长期 owner earnings，而不是短期市场新闻。对他来说，真正有价值的信息，是能帮助判断一家高质量企业未来几年真实所有者收益是否仍能复利的信息。",
    "段永平": "段永平的信息来源很克制，几乎都围绕“我能不能真正看懂”展开。他更看重产品体验、企业常识、管理层取向和长期商业逻辑，而不是市场上铺天盖地的信息流。对他来说，来源不是越多越好，而是能不能帮助自己建立足够清楚的能力圈边界。",
    "詹姆斯·安德森": "安德森的信息来源更像变化探测器。他会持续跟踪技术、创业公司、创始人、产业结构变化和极少数可能变成超级赢家的企业，把这些信息组合成对未来分布的判断。相比看静态指标，他更看谁正在真正改变世界，以及这种改变会不会被市场长期低估。",
    "汤姆·斯莱特": "斯莱特延续了 Baillie Gifford 的成长信息系统，重点不是短期数字，而是技术渗透、价值链位置、未上市资产动向和少数卓越公司的长期扩张路径。他的信息来源天然更靠近前沿行业参与者和长期产业趋势，而不是传统价值投资者常用的低估值筛选。",
    "劳伦斯·伯恩斯": "伯恩斯的信息来源带有很强的产业链研究特征。现有资料显示，他擅长沿着 AI 和科技价值链去拆解机会，从硬件、基础设施到应用层逐层看清楚价值是如何传导的。这意味着他获得信息的方式，更像研究一个系统，而不是只盯一家公司的财务表。",
    "莫尼什·帕伯莱": "帕伯莱的信息来源高度依赖可借鉴的先例。他最典型的方法不是从零发明判断，而是研究历史上的成功投资、伟大投资人的公开持仓、股东信和可复制案例，然后在新的标的上寻找相似结构。这使他的来源系统天然带有“克隆”和模式迁移的味道。",
    "比尔·阿克曼": "阿克曼的信息来源更像一套战役情报系统。他会围绕少数核心标的做深研究，结合管理层、资本结构、治理问题、行业错配和公开表达，逐步把投资论点推到市场台前。对他来说，信息不只是用来理解公司，也是用来组织一场能够推动结果的行动。",
    "丹·勒布": "丹·勒布的信息来源更像一套事件驱动情报系统。他不仅看公司价值本身，也持续跟踪资本结构、董事会和管理层决策、潜在催化剂、监管或交易事件，以及 equity 与 credit 之间的错配。对他来说，信息价值不止在“便不便宜”，而在“什么时候、通过什么路径会重新定价”。",
    "斯坦利·德鲁肯米勒": "德鲁肯米勒的信息来源很有辨识度：他既看宏观与价格，也高度依赖自己信任的专家网络。现有资料里最鲜明的一点是，他会非常认真观察那些在细分领域比自己懂得多得多的人在看什么、买什么，再用自己的模式识别和仓位能力把这些线索转成下注。换句话说，他不是靠自己懂所有细节，而是靠识别谁真的懂，以及市场会怎样消化这些变化。",
    "大卫·泰珀": "泰珀的信息来源更像政策和市场状态仪表盘：央行、财政、流动性、信用环境、资产间相对赔率和公开价格共同构成他的判断入口。对他来说，关键不是知道更多公司细节，而是知道什么时候政策反应函数已经改变了资产价格分布，以及仓位该怎样随之切换。",
    "保罗·都铎·琼斯": "PTJ 的信息来源更像交易员 cockpit：全球市场价格、流动性、政策变量、恐惧与贪婪、失衡和催化剂。他不追求把所有信息都收进来，而是把信息压成可执行预案：什么情况下试探，什么情况下重拳，什么情况下立刻撤退。",
    "托德·库姆斯": "托德·库姆斯的信息来源偏经营化而非市场化。现有资料显示，他会从单店模型、回本周期、投资回报率这类非常具体的经营指标切入，把复杂企业先拆成可验证的小单元，再决定是否值得下注。这让他的信息入口更像运营视角，而不是交易视角。",
    "泰德·韦施勒": "韦施勒的信息来源看起来低噪音、重关系、重清晰表达。现有资料里，他更像那种通过长期跟踪企业、管理层和少数高质量机会来形成判断的投资人，而不是靠频繁切换信息渠道。他依赖的不是花哨的情报优势，而是持续积累的商业理解和人与人的判断。",
    "尼克·斯利普": "斯利普的信息来源天然反短期化。他更看重年报、长期经营记录、实地调研和少数高质量企业多年如一日的行为模式，而不是短保质期市场信息。对他来说，真正有价值的信息往往来自那些能解释企业十年后为什么更强的材料，而不是明天的股价催化剂。",
    "史蒂芬·曼德尔": "史蒂芬·曼德尔的信息来源更像变化雷达和企业内部研究的结合。他既关心行业与技术变化会怎样改写结果，又坚持把这些变化压回企业内部，继续看经营驱动、管理层和组织质量。对他来说，变化本身不值钱，能把变化翻译成长期 alpha 的研究系统才值钱。",
    "凯斯·扎卡里亚": "扎卡里亚的信息来源与斯利普高度耦合，但更偏研究补位。现有资料明确提到，他对亚太市场和跨区域机会的理解是 Nomad 研究系统的重要组成部分。这意味着他更像是把局部市场经验、深度研究和组合执行连接起来的人。",
    "格雷格·詹森": "詹森的信息来源更接近一台组织化研究机器。他不仅看宏观和市场数据，也非常在意新研究怎样被系统吸收、怎样在尚未完全模型化时先进入组合测试。对他来说，来源价值不只在信息本身，还在组织能否快速把新认知转成决策。",
    "尼科莱·坦根": "坦根的信息来源非常像高质量传感器系统。他高度重视访谈、提问方式、语言细节和人在压力下暴露出来的真实特征，同时也会训练团队像顶级运动员一样提升研究与复盘能力。换句话说，他获取信息不只靠数据，还靠从人与对话里捕捉真实信号。",
    "李录": "李录的信息来源分成两层：底层是公司原始材料、长期经营事实和把自己变成公司专才的研究过程；上层则是制度、资本市场和文明尺度的长期判断。对他来说，来源不是越多越好，而是能否帮助自己诚实地区分“知道什么、不知道什么”，并在少数 fat pitch 上真正建立长期所有者级别的理解。",
    "肯·格里芬": "肯·格里芬的信息来源不是单一市场观点，而是一整套平台型传感器：价格与流动性、政策和财政现实、制度 plumbing、团队判断、数据与技术基础设施。他既看系统最底层的脆弱点，也看组织能否持续产生 forecast edge，因此信息价值最终要回到人才、风险系统与独立思考能力上。",
    "特蕾西·布里特·库尔": "特蕾西的信息来源更偏一线经营现场。现有资料里，她的方法明显依赖对创始人、组织文化、资本配置方式和管理行为的近距离观察，而不是纯粹靠财务筛选。她的信息优势更像长期陪伴式理解，而不是二级市场上的标准化研究。",
    "纳瓦尔·拉维坎特": "纳瓦尔的信息来源有很强的混合特征：一端是 AI、机器人、自动驾驶这类前沿技术与现代知识，另一端是哲学、宗教、古典文本这类长期稳定的人性材料；中间再由他自己的实践经验、识人直觉和反思把它们缝起来。对他来说，真正的边际优势不是某个独家渠道，而是能否把变化中的知识和不变的人性压缩成可行动的判断。",
}

COMPANY_META = {
    "亚马逊": {"slug": "amazon", "consensus": "这是一家最适合放在一起比较的公司: 比尔·米勒从未来现金流看它，尼克·斯利普从共享规模经济看它，霍华德·马克斯则能从更偏债权与周期的角度理解它。读这页的价值，不是知道大家都喜欢亚马逊，而是看见同一家公司如何被三套完全不同的方法论读取。"},
    "开市客": {"slug": "costco", "consensus": "对很多长期投资人来说，开市客不是零售股，而是一个把客户利益写进系统的商业样板。分歧不大，差异主要在于各自为什么被它吸引。"},
    "伯克希尔·哈撒韦": {"slug": "berkshire-hathaway", "consensus": "读者反复回到伯克希尔，不是因为它只有一条投资逻辑，而是因为它同时是公司、机构和方法论母本。公司页看资产机器，机构页看文化与接班。"},
    "SpaceX": {"slug": "spacex", "consensus": "SpaceX 在 corpus 里代表一种高不确定性但高回报分布的成长押注。真正的分歧不在于它伟不伟大，而在于谁愿意在多长时间里承受它的不可预测。"},
    "特斯拉": {"slug": "tesla", "consensus": "这家公司最好从争议开始读。它同时是成长投资者的信仰样本、质量投资者的警戒样本，也是判断创始人风险与产业终局的试金石。"},
    "诺和诺德": {"slug": "novo-nordisk", "consensus": "诺和诺德的价值不在于它是一家好公司，而在于它让人看到好公司也可能因为管理与执行问题变成坏投资。"},
    "苹果": {"slug": "apple", "consensus": "苹果在这里更像一个“看懂”的范例，而不是争议中心。它帮助读者理解段永平和巴菲特式框架在极少数公司上如何形成高确信度。"},
    "Netflix": {"slug": "netflix", "consensus": "Netflix 是 Oakmark 会计最完整的公司样本：如果只看 GAAP 盈利，会低估订阅用户价值、定价权和规模经济。"},
    "Salesforce": {"slug": "salesforce", "consensus": "Salesforce 是 AI 冲击下重估 SaaS 的样本，关键不是 AI 有没有风险，而是经常性现金流、切换成本和估值门槛是否仍然划算。"},
    "Airbnb": {"slug": "airbnb", "consensus": "Airbnb 是增长投入能否被还原为长期价值的样本，真正的分歧在于体验业务是不是现有平台的自然延伸。"},
    "腾讯": {"slug": "tencent", "consensus": "腾讯是中国互联网质量资产的代表样本，也是中文语境里长期主义投资最容易落地的案例之一。"},
    "小红书": {"slug": "xiaohongshu", "consensus": "它的意义主要在于让读者看到 Baillie Gifford 如何把全球成长框架继续延伸到中国新平台。"},
    "MiniMax": {"slug": "minimax", "consensus": "它不是成熟公司样本，而是新一代 AI 资产如何进入成长机构视野的一个窗口。"},
    "比亚迪": {"slug": "byd", "consensus": "比亚迪在这里不是普通新能源公司介绍，而是李录方法最完整的一次长持样本：工程师文化、第一性思维、受托人精神，以及当市场把价格和真实能力拉开时，长期资本如何反人性地加仓。"},
}

INSTITUTION_META = {
    "ARK Invest": {"slug": "ark-invest"},
    "Appaloosa Management": {"slug": "appaloosa-management"},
    "AKO Capital": {"slug": "ako-capital"},
    "Baillie Gifford": {"slug": "baillie-gifford"},
    "Berkshire Hathaway": {"slug": "berkshire-hathaway"},
    "Bridgewater Associates": {"slug": "bridgewater-associates"},
    "Citadel": {"slug": "citadel"},
    "Duquesne Family Office": {"slug": "duquesne-family-office"},
    "Tudor Investment Corporation": {"slug": "tudor-investment-corporation"},
    "Lindsell Train": {"slug": "lindsell-train"},
    "Nomad Investment Partnership": {"slug": "nomad-investment-partnership"},
    "Oaktree Capital": {"slug": "oaktree-capital"},
    "Oakmark Funds": {"slug": "oakmark-funds"},
    "Pershing Square": {"slug": "pershing-square"},
    "Fundsmith": {"slug": "fundsmith"},
    "Giverny Capital": {"slug": "giverny-capital"},
    "Greenlight Capital": {"slug": "greenlight-capital"},
    "Baupost Group": {"slug": "baupost-group"},
    "Himalaya Capital": {"slug": "himalaya-capital"},
    "H&H International Investment": {"slug": "h-h-international-investment"},
    "Kensico Capital Management": {"slug": "kensico-capital-management"},
    "Lone Pine Capital": {"slug": "lone-pine-capital"},
    "Maverick Capital": {"slug": "maverick-capital"},
    "Third Point": {"slug": "third-point"},
}

CONCEPT_META = {
    "护城河": {"slug": "moat"},
    "质量模式": {"slug": "quality-patterns"},
    "能力圈": {"slug": "circle-of-competence"},
    "事件驱动": {"slug": "event-driven"},
    "第二层思维": {"slug": "second-level-thinking"},
    "共享规模经济": {"slug": "scale-economies-shared"},
    "经常性收入": {"slug": "recurring-revenues"},
    "友好中介": {"slug": "friendly-middlemen"},
    "收费站型生意": {"slug": "toll-roads"},
    "变化驱动投资": {"slug": "investing-behind-change"},
    "Oakmark会计": {"slug": "oakmark-accounting"},
    "所有者收益": {"slug": "owners-earnings"},
    "趋势交易": {"slug": "trend-trading"},
    "政策反应函数": {"slug": "policy-reaction-function"},
    "时间套利": {"slug": "time-arbitrage"},
    "超级赢家": {"slug": "super-winners"},
    "反脆弱与仓位管理": {"slug": "antifragility-and-position-sizing"},
    "空头视角": {"slug": "short-perspective"},
    "企业文化": {"slug": "corporate-culture"},
    "克隆策略": {"slug": "cloning"},
    "判断力": {"slug": "judgment"},
}

COMPANY_SLUG_OVERRIDES = {
    "亚马逊": "amazon",
    "开市客": "costco",
    "伯克希尔·哈撒韦": "berkshire-hathaway",
    "SpaceX": "spacex",
    "特斯拉": "tesla",
    "诺和诺德": "novo-nordisk",
    "苹果": "apple",
    "帝亚吉欧": "diageo",
    "腾讯": "tencent",
    "小红书": "xiaohongshu",
    "MiniMax": "minimax",
    "比亚迪": "byd",
    "微软": "microsoft",
    "可口可乐": "coca-cola",
    "美团": "meituan",
    "拼多多": "pdd",
    "百度": "baidu",
    "英伟达": "nvidia",
    "阿里巴巴": "alibaba",
    "台积电": "tsmc",
    "丹纳赫": "danaher",
    "ASML": "asml",
    "Alphabet": "alphabet",
    "Netflix": "netflix",
    "Salesforce": "salesforce",
    "Airbnb": "airbnb",
    "Constellation Software": "constellation-software",
    "CarMax": "carmax",
    "Markel": "markel",
    "O'Reilly Automotive": "oreilly-automotive",
    "BlackBerry": "blackberry",
    "Coinbase": "coinbase",
    "GEICO": "geico",
    "Howard Hughes": "howard-hughes",
    "Meta": "meta",
    "Palantir": "palantir",
    "PG&E": "pge",
    "Silvergate Capital": "silvergate-capital",
    "Teva": "teva",
    "Visa": "visa",
    "ADP": "adp",
    "Capital One": "capital-one",
    "Live Nation": "live-nation",
    "伦敦证券交易所集团": "london-stock-exchange-group",
}

DIALOGUE_SLUG_OVERRIDES = {
    "质量价值 vs 成长非共识": "quality-vs-growth",
    "保守的风险语言 vs 激进的仓位语言": "risk-and-conviction",
    "复利信仰 vs 流动性信仰": "compound-faith-vs-liquidity-faith",
    "永久复利 vs 七年价值重估": "permanent-compounding-vs-seven-year-revaluation",
    "审计式质量 vs 艺术式质量": "audit-quality-vs-art-quality",
    "不懂不碰 vs 未来信息才重要": "certainty-vs-future",
    "看懂边界 vs 品味判断": "boundary-vs-taste",
    "制度保护时间 vs 性格保护时间": "institution-vs-temperament",
    "复制优秀模式 vs 寻找超级赢家": "cloning-vs-super-winners",
    "提问式判断 vs 仓位式判断": "questioning-vs-positioning",
    "安静持有 vs 战役推动": "quiet-holding-vs-campaign-push",
    "方向判断正确 vs 交易结构正确": "direction-right-vs-structure-right",
    "静态能力圈 vs 可审计能力圈": "static-vs-auditable-circle",
    "交易型反脆弱 vs 资本结构型反脆弱": "trading-vs-capital-structure-antifragility",
    "政策底 vs 估值底": "policy-put-vs-valuation-floor",
    "可验证现金流 vs 站在变化的一边": "verifiable-cashflow-vs-stand-with-change",
    "周期位置 vs 制度裂缝": "cycle-position-vs-structural-fracture",
    "制度裂缝 vs 制度红利": "structural-fracture-vs-reform-dividend",
    "平台收敛赢家 vs 价值链瓶颈赢家": "platform-winners-vs-bottleneck-winners",
    "少犯错游戏 vs 多赢家游戏": "fewer-losers-vs-more-winners",
    "未来分布 vs 负债端现实": "future-distribution-vs-liability-reality",
    "放弃做空 vs 保留空头脑": "stop-shorting-vs-keep-a-short-mind",
    "好生意自己是催化剂 vs 价值需要被推动": "business-itself-vs-value-needs-pushing",
    "访谈型方法论 vs 组合型证据": "interviews-vs-portfolio-evidence",
}


def simple_slug(name: str) -> str:
    slug = name.lower().strip()
    slug = slug.replace('·', '-')
    slug = re.sub(r'[^a-z0-9\-\s]+', '', slug)
    slug = re.sub(r'\s+', '-', slug)
    slug = re.sub(r'-{2,}', '-', slug).strip('-')
    return slug or name


def company_slug(name: str) -> str:
    return COMPANY_SLUG_OVERRIDES.get(name, simple_slug(name))


def question_slug(name: str) -> str:
    slug = name.strip()
    slug = slug.replace('：', '-')
    slug = re.sub(r'\s+', '-', slug)
    return simple_slug(slug)


def all_company_names() -> list[str]:
    companies_dir = WIKI_DIR / 'companies'
    return sorted(p.stem for p in companies_dir.glob('*.md') if p.name != 'index.md')


def all_question_names() -> list[str]:
    questions_dir = WIKI_DIR / 'ten-questions'
    return sorted(p.stem for p in questions_dir.glob('*.md') if p.name != 'index.md')



def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    _, rest = text.split("---\n", 1)
    fm, body = rest.split("\n---\n", 1)
    meta: dict[str, str] = {}
    current_key = None
    for raw_line in fm.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - ") and current_key:
            meta.setdefault(current_key, "")
            meta[current_key] += (", " if meta[current_key] else "") + line[4:].strip().strip('"')
            continue
        if ":" in line:
            key, value = line.split(":", 1)
            current_key = key.strip()
            meta[current_key] = value.strip().strip('"')
    return meta, body.lstrip()


def parse_sections(body: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current = "_lead"
    sections[current] = []
    for line in body.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
        else:
            sections.setdefault(current, []).append(line)
    return {k: "\n".join(v).strip() for k, v in sections.items()}


def strip_images(text: str) -> str:
    kept = []
    for line in text.splitlines():
        if line.strip().startswith("!["):
            continue
        kept.append(line)
    return "\n".join(kept).strip()


def clean_excerpt(text: str) -> str:
    cleaned_lines = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            cleaned_lines.append("")
            continue
        if stripped == "---":
            continue
        if stripped.startswith("#"):
            continue
        if re.fullmatch(r"[,，]\s*\d+\s*分钟", stripped):
            continue
        normalized = re.sub(r"\*+", "", line).strip()
        if not normalized:
            continue
        cleaned_lines.append(normalized)
    cleaned = "\n".join(cleaned_lines)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def extract_source_meta_and_excerpt(body: str) -> tuple[str, str]:
    author = ""
    published = ""
    content_lines = []

    def maybe_capture_meta(line: str):
        nonlocal author, published
        plain = re.sub(r"\*+", "", line).strip()
        plain = re.sub(r"\[[^\]]+\]\([^)]+\)", "", plain).strip()
        if not plain:
            return
        date_match = re.search(r"(\d{4}年\d{1,2}月\d{1,2}日\s*\d{1,2}:\d{2}(?:\s*[^\s]+)?)", plain)
        if date_match and not published:
            published = date_match.group(1).strip()
        if ("原创" in plain or "作者" in plain or "文丨" in plain) and not author:
            meta_text = plain.replace("原创：", "原创 ").replace("原创:", "原创 ")
            meta_text = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日.*$", "", meta_text).strip(" ：:|")
            author = meta_text

    body_lines = body.splitlines()
    for line in body_lines[:12]:
        maybe_capture_meta(line)

    paragraphs = []
    dialogue_candidates = []
    current = []
    for raw_line in body_lines:
        stripped = raw_line.strip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current).strip())
                current = []
            continue
        if stripped.startswith("![") or stripped == "---" or stripped.startswith("#"):
            continue
        if re.fullmatch(r"[,，]\s*\d+\s*分钟", stripped):
            continue
        plain = re.sub(r"\*+", "", stripped)
        plain = re.sub(r"\[[^\]]+\]\([^)]+\)", "", plain).strip()
        if not plain:
            continue
        speaker_match = re.match(r"^(HOST|主持人|ILANA|Ilana|Druckenmiller|巴菲特|芒格|安德森|史密斯|阿克曼|段永平|马克斯|米勒)[：:]\s*(.+)$", plain)
        if speaker_match:
            speaker, content = speaker_match.groups()
            content = content.strip()
            if speaker not in {"HOST", "主持人", "ILANA", "Ilana"} and len(content) >= 18:
                dialogue_candidates.append(content)
            continue
        if any(token in plain for token in ["原创", "编辑丨", "编辑：", "责编", "来源："]) and len(plain) < 60:
            maybe_capture_meta(plain)
            continue
        current.append(plain)
    if current:
        paragraphs.append(" ".join(current).strip())

    excerpt = ""
    excerpt_keywords = ["投资", "市场", "仓位", "买", "卖", "风险", "Nvidia", "股票", "估值", "企业", "组合", "回报", "增长", "周期"]
    for candidate in dialogue_candidates:
        if any(keyword in candidate for keyword in excerpt_keywords):
            excerpt = candidate
            break
    if not excerpt and dialogue_candidates:
        excerpt = dialogue_candidates[0]
    for para in paragraphs:
        if excerpt:
            break
        if len(para) < 45:
            continue
        if any(token in para for token in ["会不会用AI", "砍掉所有知识付费", "那个时代结束了", "值得花钱的只有三样"]):
            continue
        excerpt = para
        break
    if not excerpt and paragraphs:
        excerpt = paragraphs[0]

    meta_lines = []
    if author:
        meta_lines.append(f"**作者**: {author}  ")
    if published:
        meta_lines.append(f"**时间**: {published}")
    return "\n".join(meta_lines), excerpt


def first_quote(section_text: str) -> str:
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return stripped[2:]
    return ""


def first_blockquote(section_text: str) -> str:
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(">"):
            return stripped.lstrip(">").strip()
    return ""


def collect_featured_quotes(limit: int = 4) -> list[str]:
    quotes: list[str] = []
    seen: set[str] = set()
    for source_path in sorted((WIKI_DIR / "investors").glob("*.md")):
        if source_path.name in {"index.md", "比较矩阵.md"}:
            continue
        _, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        sections = parse_sections(body)
        for section_name in ["人物分析", "简介", "来时路", "失误、边界与失效条件"]:
            section_text = sections.get(section_name, "")
            for line in section_text.splitlines():
                stripped = line.strip()
                if not stripped.startswith(">"):
                    continue
                quote = stripped.lstrip(">").strip()
                if (
                    not quote
                    or quote.startswith("——")
                    or quote.startswith("来源")
                    or quote.startswith("验证卡")
                ):
                    continue
                if quote not in seen:
                    seen.add(quote)
                    quotes.append(quote)
    if not quotes:
        return []
    rotation = date.today().toordinal() % len(quotes)
    rotated = quotes[rotation:] + quotes[:rotation]
    return rotated[:limit]


def rel_link(from_doc: Path, target_doc: Path) -> str:
    return str(Path(os_relpath(target_doc, from_doc.parent))).replace("\\", "/")


def os_relpath(target: Path, start: Path) -> str:
    return str(Path(target).relative_to(start)) if str(target).startswith(str(start)) else str(Path(*Path(target).parts[len(Path(start).parts):]))


def safe_relpath(target: Path, start: Path) -> str:
    return str(Path(__import__("os").path.relpath(target, start))).replace("\\", "/")


def source_slug(filename: str, index: int) -> str:
    return f"source-{index:02d}"


def build_link_maps():
    page_map: dict[str, str] = {}
    type_map: dict[str, str] = {}
    for name, meta in INVESTOR_META.items():
        key = f"investors/{name}"
        page_map[key] = f"investors/{meta['slug']}"
        type_map[key] = name
    for name in all_company_names():
        slug = company_slug(name)
        key = f"companies/{name}"
        page_map[key] = f"companies/{slug}"
        type_map[key] = name
    for name, meta in INSTITUTION_META.items():
        key = f"institutions/{name}"
        page_map[key] = f"institutions/{meta['slug']}"
        type_map[key] = name
    for src in (WIKI_DIR / "institutions").glob("13F趋势*.md"):
        if src.stem == "13F趋势":
            slug = "13f-trends"
            title = "13F 趋势"
        elif src.stem == "13F趋势-Duquesne":
            slug = "13f-trends-duquesne"
            title = "13F 趋势 - Duquesne"
        elif src.stem == "13F趋势-HH":
            slug = "13f-trends-hh"
            title = "13F 趋势 - H&H"
        elif src.stem == "13F趋势-Tudor":
            slug = "13f-trends-tudor"
            title = "13F 趋势 - Tudor"
        elif src.stem == "13F趋势-Himalaya":
            slug = "13f-trends-himalaya"
            title = "13F 趋势 - Himalaya"
        elif src.stem == "13F趋势-Lone Pine":
            slug = "13f-trends-lone-pine"
            title = "13F 趋势 - Lone Pine"
        elif src.stem == "13F趋势-Greenlight":
            slug = "13f-trends-greenlight"
            title = "13F 趋势 - Greenlight"
        elif src.stem == "13F趋势-Fundsmith":
            slug = "13f-trends-fundsmith"
            title = "13F 趋势 - Fundsmith"
        elif src.stem == "13F趋势-Giverny":
            slug = "13f-trends-giverny"
            title = "13F 趋势 - Giverny"
        elif src.stem == "13F趋势-AKO":
            slug = "13f-trends-ako"
            title = "13F 趋势 - AKO"
        elif src.stem == "13F趋势-Baillie":
            slug = "13f-trends-baillie"
            title = "13F 趋势 - Baillie Gifford"
        elif src.stem == "13F趋势-Baupost":
            slug = "13f-trends-baupost"
            title = "13F 趋势 - Baupost"
        elif src.stem == "13F趋势-Pershing":
            slug = "13f-trends-pershing"
            title = "13F 趋势 - Pershing"
        elif src.stem == "13F趋势-Maverick":
            slug = "13f-trends-maverick"
            title = "13F 趋势 - Maverick"
        elif src.stem == "13F趋势-Oakmark":
            slug = "13f-trends-oakmark"
            title = "13F 趋势 - Oakmark"
        elif src.stem == "13F趋势-Appaloosa":
            slug = "13f-trends-appaloosa"
            title = "13F 趋势 - Appaloosa"
        elif src.stem == "13F趋势-Kensico":
            slug = "13f-trends-kensico"
            title = "13F 趋势 - Kensico"
        else:
            match = re.match(r"13F趋势-(\d{4})Q([1-4])$", src.stem)
            if not match:
                continue
            slug = f"13f-trends-{match.group(1)}-q{match.group(2)}"
            title = f"13F 趋势 - Q{match.group(2)} {match.group(1)}"
        key = f"institutions/{src.stem}"
        page_map[key] = f"institutions/{slug}"
        type_map[key] = title
    for name, meta in CONCEPT_META.items():
        key = f"concepts/{name}"
        page_map[key] = f"concepts/{meta['slug']}"
        type_map[key] = name
    for name in all_question_names():
        key = f"ten-questions/{name}"
        page_map[key] = f"ten-questions/{question_slug(name)}"
        type_map[key] = name
    page_map["dialogues/index"] = "dialogues"
    dialogues_dir = WIKI_DIR / "dialogues"
    for src in dialogues_dir.glob("*.md"):
        if src.name == "index.md":
            continue
        slug = DIALOGUE_SLUG_OVERRIDES.get(src.stem, src.stem)
        page_map[f"dialogues/{src.stem}"] = f"dialogues/{slug}"
        type_map[f"dialogues/{src.stem}"] = src.stem
    page_map["investors/index"] = "investors"
    page_map["companies/index"] = "companies"
    page_map["institutions/index"] = "institutions"
    page_map["concepts/index"] = "concepts"
    page_map["ten-questions/index"] = "ten-questions"
    page_map["log"] = ""
    return page_map, type_map


def build_source_maps():
    mapping = {}
    raw_files = sorted(RAW_DIR.glob("*.md"))
    for idx, path in enumerate(raw_files, start=1):
        slug = f"sources/{source_slug(path.name, idx)}"
        mapping[path.stem] = slug
        mapping[path.name] = slug
        mapping[f"raw/{path.stem}"] = slug
        mapping[f"raw/{path.name}"] = slug
    return mapping, raw_files


PAGE_LINKS, PAGE_TITLES = build_link_maps()
SOURCE_LINKS, RAW_FILES = build_source_maps()


WIKILINK_RE = re.compile(r"\[\[([^\]\\|]+)(?:\\?\|([^\]]+))?\]\]")

INVESTOR_ANNUALIZED_RETURNS = {
    "尼克·特雷恩": "约 10.5%（[Finsbury 官方 factsheet](https://www.finsburygt.com/download_file/force/326/1)）",
    "特里·史密斯": "约 13.5%（[Fundsmith 官方 factsheet](https://www.fundsmith.co.uk/factsheet/)）",
    "比尔·阿克曼": "约 16.2%（[PSH 2025 年报](https://assets.pershingsquareholdings.com/wp-content/uploads/2026/02/18175039/Pershing-Square-Holdings-Ltd.-2025-Annual-Report.pdf)）",
    "丹·勒布": "约 13.0%（[Third Point 官方月报](https://assets.thirdpointlimited.com/f/166217/x/cafeb5e071/2023-04-april-monthly-report-tpil.pdf)）",
    "塞思·卡拉曼": "约 19.0%（[Bloomberg 人物报道](https://www.bloomberg.com/news/articles/2010-06-17/the-financial-life-seth-klarman)）",
    "肯·格里芬": "约 19.2%（[CNBC 报道](https://www.cnbc.com/2025/07/01/billionaire-ken-griffins-hedge-funds-at-citadel-are-all-in-the-green-for-2025.html)）",
}


def convert_wikilinks(text: str, current_output: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        label = (match.group(2) or "").strip()
        clean = target
        if clean.endswith(".md"):
            clean = clean[:-3]
        clean = clean.lstrip("/")
        href = PAGE_LINKS.get(clean) or SOURCE_LINKS.get(clean)
        display = label or clean.split("/")[-1]
        if not href:
            return display
        absolute = f"{SITE_BASE}/{href}/"
        return f"[{display}]({absolute})"

    return WIKILINK_RE.sub(replace, text)


def normalize_reader_facing_terms(text: str) -> str:
    replacements = [
        ("当前语料未涉及", "现有资料暂未涉及"),
        ("当前语料对", "现有资料对"),
        ("当前语料没有", "现有资料没有"),
        ("当前语料里", "现有资料里"),
        ("当前语料中", "现有资料中"),
        ("当前语料", "现有资料"),
        ("当前资料未涉及", "现有资料暂未涉及"),
        ("当前 raw", "现有资料"),
        ("根据当前 raw", "根据现有资料"),
        ("raw 中", "现有资料中"),
        ("raw 里", "现有资料里"),
        ("raw 给出的", "现有资料给出的"),
        ("raw 给出", "现有资料给出"),
        ("raw 显示", "现有资料显示"),
        ("raw 说明", "现有资料说明"),
        ("raw 也", "现有资料也"),
        ("raw 对", "现有资料对"),
        ("raw 没有", "现有资料没有"),
        ("raw 不是", "现有资料不是"),
        ("raw 仍然", "现有资料仍然"),
        ("raw 最", "现有资料最"),
        ("raw 直接", "现有资料直接"),
        ("raw 明确指出", "现有资料明确提到"),
        ("raw 给出的", "现有资料给出的"),
        ("raw 给出", "现有资料给出"),
        ("raw 对", "现有资料对"),
        ("raw 不", "现有资料不"),
        ("raw 还", "现有资料还"),
        ("raw 已经", "现有资料已经"),
        ("raw 其实", "现有资料其实"),
        ("raw 主要", "现有资料主要"),
        ("raw 更", "现有资料更"),
        ("raw 本身", "现有资料本身"),
        ("当前在 raw 中", "当前在现有资料中"),
        ("在 raw 中", "在现有资料中"),
        ("从当前 raw 看", "从现有资料看"),
        ("根据 raw", "根据现有资料"),
        ("原始中文 corpus", "这批中文资料"),
        ("中文 corpus", "这批中文资料"),
        ("这个 corpus", "这批资料"),
        ("当前 corpus", "这批资料"),
        ("current corpus", "现有资料"),
        ("在 corpus 中", "在这批资料中"),
        ("在 corpus 里", "在这批资料中"),
        ("在这个 corpus 中", "在这批资料中"),
        ("这个 corpus 里", "这批资料里"),
        ("在当前 corpus 里", "在这批资料中"),
        ("在当前 corpus 中", "在这批资料中"),
        ("它在 corpus 里重要", "它在这批资料中重要"),
        ("整个 corpus", "整批资料"),
        ("在当前语料里", "在现有资料里"),
        ("当前 raw 没有", "现有资料没有"),
        ("当前 raw 里", "现有资料里"),
        ("当前 raw 中", "现有资料中"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    text = re.sub(r"(?<![A-Za-z])raw(?![A-Za-z])", "现有资料", text)
    text = re.sub(r"(?<![A-Za-z])corpus(?![A-Za-z])", "这批资料", text)
    return text


def ensure_clean_docs():
    if DOCS_DIR.exists():
        shutil.rmtree(DOCS_DIR)
    for folder in ["investors", "companies", "institutions", "concepts", "sources", "dialogues", "ten-questions"]:
        (DOCS_DIR / folder).mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalize_reader_facing_terms(content).strip() + "\n", encoding="utf-8")


def doc_url(path: str) -> str:
    normalized = path.strip("/")
    if normalized == "index":
        normalized = ""
    elif normalized.endswith("/index"):
        normalized = normalized[:-len("/index")]
    return f"{SITE_BASE}/{normalized}/" if normalized else f"{SITE_BASE}/"


def render_frontmatter(title: str, slug: str, description: str) -> str:
    safe_title = title.replace('"', '\\"')
    safe_slug = slug.replace('"', '\\"')
    safe_description = description.replace('"', '\\"')
    lines = ["---", f'title: "{safe_title}"']
    if slug:
        lines.append(f'slug: "{safe_slug}"')
    lines.append(f'description: "{safe_description}"')
    lines.append("---\n")
    return "\n".join(lines)


def compile_investors():
    for name, meta in INVESTOR_META.items():
        source_path = WIKI_DIR / "investors" / f"{name}.md"
        fm, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        sections = parse_sections(body)
        annualized = INVESTOR_ANNUALIZED_RETURNS.get(name, "未公开")
        institution_name, institution_path = meta["institution"]
        if institution_path:
            institution_md = f"[{institution_name}]({doc_url(institution_path)})"
        else:
            institution_md = institution_name
        output = DOCS_DIR / "investors" / f"{meta['slug']}.md"
        quote = convert_wikilinks(
            translate_common_phrases(
                first_blockquote(sections.get("人物分析", "")) or first_quote(sections.get("标志性语录", ""))
            ),
            output,
        )
        pieces = [
            render_frontmatter(name, f"investors/{meta['slug']}", meta["tagline"]),
            "> **一句话定义**  ",
            f"> {meta['tagline']}\n",
            f"> {quote}\n" if quote else "",
            f"**所属机构**: {institution_md}  ",
            f"**年化收益率**: {annualized}  ",
            f"**代表性持仓**: {meta['holdings']}  ",
            f"**核心方法**: {meta['methods']}\n",
            "## 简介\n",
            convert_wikilinks(translate_common_phrases(sections.get("简介", "现有资料暂未涉及。")), output),
            "\n## 来时路\n",
            convert_wikilinks(
                translate_common_phrases(
                    sections.get("来时路", "") or sections.get("来时路与关键转折", "当前语料未涉及。")
                ),
                output,
            ),
            "\n## 人物分析\n",
            convert_wikilinks(translate_common_phrases(sections.get("人物分析", "当前语料未涉及。")), output),
            "\n## 失误、边界与失效条件\n",
            convert_wikilinks(
                translate_common_phrases(sections.get("失误、边界与失效条件", "当前语料未涉及。")),
                output,
            ),
            "\n## 对我有什么启发\n",
            convert_wikilinks(translate_common_phrases(sections.get("对我有什么启发", "当前语料未涉及。")), output),
            "\n## 横向定位\n",
            convert_wikilinks(translate_common_phrases(sections.get("横向定位", "当前语料未涉及。")), output),
            "\n## 主要来源\n",
            convert_wikilinks(sections.get("主要来源", "当前语料未涉及。"), output),
        ]
        write(output, "\n".join([p for p in pieces if p]))

    matrix_src = WIKI_DIR / "investors" / "比较矩阵.md"
    _, matrix_body = parse_frontmatter(matrix_src.read_text(encoding="utf-8"))
    matrix_body_for_index = re.sub(r"^\s*# .+\n+", "", matrix_body, count=1).strip()

    index_output = DOCS_DIR / "investors" / "index.md"
    lines = [
        render_frontmatter("投资人", "investors", "从人物、约束和边界切入理解不同投资方法。"),
        "这里不是投资人物百科，而是按“这个人为什么会这样投、这套方法在什么边界下成立”来组织的入口。\n",
        "## 从哪里开始\n",
        f"- **价值投资**: [沃伦·巴菲特]({doc_url('investors/warren-buffett')})、[查理·芒格]({doc_url('investors/charlie-munger')})、[特里·史密斯]({doc_url('investors/terry-smith')})、[尼克·特雷恩]({doc_url('investors/nick-train')})、[比尔·尼格伦]({doc_url('investors/bill-nygren')})",
        f"- **经典 long/short / 深度价值 / 事件驱动**: [大卫·艾因霍恩]({doc_url('investors/david-einhorn')})、[李·安斯利]({doc_url('investors/lee-ainslie')})、[塞思·卡拉曼]({doc_url('investors/seth-klarman')})、[丹·勒布]({doc_url('investors/dan-loeb')})",
        f"- **成长投资**: [詹姆斯·安德森]({doc_url('investors/james-anderson')})、[汤姆·斯莱特]({doc_url('investors/tom-slater')})、[劳伦斯·伯恩斯]({doc_url('investors/lawrence-burns')})",
        f"- **宏观与风险**: [霍华德·马克斯]({doc_url('investors/howard-marks')})、[斯坦利·德鲁肯米勒]({doc_url('investors/stanley-druckenmiller')})、[格雷格·詹森]({doc_url('investors/greg-jensen')})",
        f"- **新增材料重点**: [比尔·尼格伦]({doc_url('investors/bill-nygren')})、[保罗·都铎·琼斯]({doc_url('investors/paul-tudor-jones')})、[霍华德·马克斯]({doc_url('investors/howard-marks')})",
        f"- **最不寻常的思维**: [尼克·斯利普]({doc_url('investors/nick-sleep')})、[尼科莱·坦根]({doc_url('investors/nicolai-tangen')})、[纳瓦尔·拉维坎特]({doc_url('investors/naval-ravikant')})\n",
        "## 比较视图\n",
        f"- [投资十问]({doc_url('ten-questions/index')})\n",
        "## 投资人比较矩阵\n",
        convert_wikilinks(matrix_body_for_index, index_output),
        "\n",
        "## 全部投资人\n",
    ]
    for name, meta in INVESTOR_META.items():
        lines.append(f"- [{name}]({doc_url('investors/' + meta['slug'])})")
    write(index_output, "\n".join(lines))

def compile_companies():
    company_names = all_company_names()
    highlights: list[str] = []

    for name in company_names:
        slug = company_slug(name)
        source_path = WIKI_DIR / "companies" / f"{name}.md"
        fm, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        sections = parse_sections(body)
        intro = sections.get("简介", "现有资料暂未涉及。").strip()
        consensus = COMPANY_META.get(name, {}).get("consensus") or intro.split("\n\n", 1)[0].strip()
        output = DOCS_DIR / "companies" / f"{slug}.md"
        content = [
            render_frontmatter(name, f"companies/{slug}", consensus),
            f"> **争议与共识**  \n> {translate_common_phrases(consensus)}\n",
            "## 简介\n",
            convert_wikilinks(translate_common_phrases(intro or "现有资料暂未涉及。"), output),
            "\n## 公司点评\n",
            convert_wikilinks(translate_common_phrases(sections.get("公司点评", "现有资料暂未涉及。")), output),
        ]
        if sections.get("分歧与共识"):
            content.extend(
                ["\n## 分歧与共识\n", convert_wikilinks(translate_common_phrases(sections.get("分歧与共识", "")), output)]
            )
        content.extend(["\n## 相关页面\n", convert_wikilinks(sections.get("相关页面", "现有资料暂未涉及。"), output)])
        write(output, "\n".join(content))

        if len(highlights) < 6 and intro and intro != "现有资料暂未涉及。":
            summary = intro.split("。", 1)[0].strip()
            if summary:
                highlights.append(f"- [{name}]({doc_url('companies/' + slug)}): {summary}。")

    index_src = WIKI_DIR / "companies" / "index.md"
    _, body = parse_frontmatter(index_src.read_text(encoding="utf-8"))
    index_output = DOCS_DIR / "companies" / "index.md"
    pieces = [
        render_frontmatter("公司", "companies", "不是公司百科，而是“为什么顶级投资人反复提到它们”。"),
        convert_wikilinks(body, index_output),
        "\n## 全部公司\n",
    ]
    if highlights:
        pieces.insert(2, "\n" + "\n".join(highlights) + "\n")
    write(index_output, "".join(pieces))
    with index_output.open("a", encoding="utf-8") as f:
        for name in company_names:
            f.write(f"- [{name}]({doc_url('companies/' + company_slug(name))})\n")


def compile_institutions():
    for name, meta in INSTITUTION_META.items():
        source_path = WIKI_DIR / "institutions" / f"{name}.md"
        _, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        output = DOCS_DIR / "institutions" / f"{meta['slug']}.md"
        cleaned_body = re.sub(r"^# .+\n+", "", body, count=1)
        write(
            output,
            render_frontmatter(name, f"institutions/{meta['slug']}", f"{name} 的机构级哲学、文化与传承。")
            + convert_wikilinks(translate_common_phrases(cleaned_body), output),
        )

    for source_path in sorted((WIKI_DIR / "institutions").glob("13F趋势*.md")):
        _, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        stem = source_path.stem
        if stem == "13F趋势":
            title = "13F 趋势"
            slug = "13f-trends"
            description = "把机构 13F 按季度横向拉齐，观察跨机构持仓趋势。"
        elif stem == "13F趋势-Duquesne":
            title = "13F 趋势 - Duquesne"
            slug = "13f-trends-duquesne"
            description = "Duquesne Family Office 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-HH":
            title = "13F 趋势 - H&H"
            slug = "13f-trends-hh"
            description = "H&H International Investment 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Tudor":
            title = "13F 趋势 - Tudor"
            slug = "13f-trends-tudor"
            description = "Tudor Investment Corporation 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Himalaya":
            title = "13F 趋势 - Himalaya"
            slug = "13f-trends-himalaya"
            description = "Himalaya Capital 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Lone Pine":
            title = "13F 趋势 - Lone Pine"
            slug = "13f-trends-lone-pine"
            description = "Lone Pine Capital 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Greenlight":
            title = "13F 趋势 - Greenlight"
            slug = "13f-trends-greenlight"
            description = "Greenlight Capital / DME 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Fundsmith":
            title = "13F 趋势 - Fundsmith"
            slug = "13f-trends-fundsmith"
            description = "Fundsmith 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Giverny":
            title = "13F 趋势 - Giverny"
            slug = "13f-trends-giverny"
            description = "Giverny Capital 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-AKO":
            title = "13F 趋势 - AKO"
            slug = "13f-trends-ako"
            description = "AKO Capital 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Baillie":
            title = "13F 趋势 - Baillie Gifford"
            slug = "13f-trends-baillie"
            description = "Baillie Gifford 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Baupost":
            title = "13F 趋势 - Baupost"
            slug = "13f-trends-baupost"
            description = "Baupost Group 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Pershing":
            title = "13F 趋势 - Pershing"
            slug = "13f-trends-pershing"
            description = "Pershing Square 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Maverick":
            title = "13F 趋势 - Maverick"
            slug = "13f-trends-maverick"
            description = "Maverick Capital 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Oakmark":
            title = "13F 趋势 - Oakmark"
            slug = "13f-trends-oakmark"
            description = "Oakmark / Harris Associates 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Appaloosa":
            title = "13F 趋势 - Appaloosa"
            slug = "13f-trends-appaloosa"
            description = "Appaloosa Management 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        elif stem == "13F趋势-Kensico":
            title = "13F 趋势 - Kensico"
            slug = "13f-trends-kensico"
            description = "Kensico Capital Management 从 2023Q1 到 2026Q1 的单机构 13F 持仓变化。"
        else:
            match = re.match(r"13F趋势-(\d{4})Q([1-4])$", stem)
            if not match:
                continue
            title = f"13F 趋势 - Q{match.group(2)} {match.group(1)}"
            slug = f"13f-trends-{match.group(1)}-q{match.group(2)}"
            description = f"{title} 的跨机构持仓趋势雷达。"
        output = DOCS_DIR / "institutions" / f"{slug}.md"
        cleaned_body = re.sub(r"^# .+\n+", "", body, count=1)
        write(
            output,
            render_frontmatter(title, f"institutions/{slug}", description)
            + convert_wikilinks(translate_common_phrases(cleaned_body), output),
        )


    write(
        DOCS_DIR / "institutions" / "index.md",
        render_frontmatter("机构", "institutions", "激励结构决定投资人能做什么，而不只是想做什么。")
        + "\n".join(
            [
                "读机构页的重点，不是规模大小，而是看清楚：一家机构靠什么保护时间维度、靠什么把理念写进制度。\n",
                f"- [13F 趋势]({doc_url('institutions/13f-trends')}): 把最近季度的 13F 横向拉齐，看哪些股票出现跨机构共振、分歧和集中度变化。",
                f"- [Nomad Investment Partnership]({doc_url('institutions/nomad-investment-partnership')}): 为什么 Sleep 能拿亚马逊二十年。",
                f"- [AKO Capital]({doc_url('institutions/ako-capital')}): 为什么 quality investing 只有在 specialist teams 和反馈闭环里才真正制度化。",
                f"- [Maverick Capital]({doc_url('institutions/maverick-capital')}): 为什么 Tiger 学徒制会长成行业专家制和建设性 long/short。",
                f"- [Lone Pine Capital]({doc_url('institutions/lone-pine-capital')}): 为什么变化驱动投资最终会变成组织与文化问题。",
                f"- [Greenlight Capital]({doc_url('institutions/greenlight-capital')}): 为什么反动量、分拆错价和会计审问会被写成一台公开市场机器。",
                f"- [Baupost Group]({doc_url('institutions/baupost-group')}): 为什么高现金、patient capital 和跨资产比较不是口号，而是机构边界。",
                f"- [Lindsell Train]({doc_url('institutions/lindsell-train')}): 为什么极低换手、franchise 选择和能力圈约束必须被制度保护。",
                f"- [Third Point]({doc_url('institutions/third-point')}): 为什么事件驱动、催化剂和跨资本结构配置会长成一套组合语言。",
                f"- [Berkshire Hathaway]({doc_url('institutions/berkshire-hathaway')}): 为什么永久资本和保险 float 能形成独特制度优势。",
                f"- [Oaktree Capital]({doc_url('institutions/oaktree-capital')}): 为什么备忘录不只是写作，而是组织知识资产。",
                f"- [ARK Invest]({doc_url('institutions/ark-invest')}): 为什么公开市场也能被当成技术平台地图来下注。",
                f"- [Citadel]({doc_url('institutions/citadel')}): 为什么制度裂缝和 market plumbing 会进入机构方法本身。",
                f"- [H&H International Investment]({doc_url('institutions/h-h-international-investment')}): 为什么段永平的看懂和打孔机会在 13F 上表现为极少数美国公开证券切片。",
                "\n## 全部机构\n",
            ]
        ),
    )
    institutions_index = DOCS_DIR / "institutions" / "index.md"
    with institutions_index.open("a", encoding="utf-8") as f:
        for name, meta in INSTITUTION_META.items():
            f.write(f"- [{name}]({doc_url('institutions/' + meta['slug'])})\n")


def compile_concepts():
    for name, meta in CONCEPT_META.items():
        source_path = WIKI_DIR / "concepts" / f"{name}.md"
        _, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        output = DOCS_DIR / "concepts" / f"{meta['slug']}.md"
        cleaned_body = re.sub(r"^# .+\n+", "", body, count=1)
        write(
            output,
            render_frontmatter(name, f"concepts/{meta['slug']}", f"{name} 在这个 corpus 里的最佳入口。")
            + convert_wikilinks(cleaned_body, output),
        )

    index_lines = [
        render_frontmatter("概念", "concepts", "跨人物阅读时，最容易反复出现的那几根骨架。"),
        "如果你不想先读人物，可以先读概念。概念页最适合当作跨投资人的公共词典。\n",
        f"- [护城河]({doc_url('concepts/moat')})",
        f"- [质量模式]({doc_url('concepts/quality-patterns')})",
        f"- [能力圈]({doc_url('concepts/circle-of-competence')})",
        f"- [第二层思维]({doc_url('concepts/second-level-thinking')})",
        f"- [共享规模经济]({doc_url('concepts/scale-economies-shared')})",
        f"- [经常性收入]({doc_url('concepts/recurring-revenues')})",
        f"- [收费站型生意]({doc_url('concepts/toll-roads')})",
        f"- [变化驱动投资]({doc_url('concepts/investing-behind-change')})",
        f"- [判断力]({doc_url('concepts/judgment')})",
        f"- [企业文化]({doc_url('concepts/corporate-culture')})",
        f"- [空头视角]({doc_url('concepts/short-perspective')})",
        "\n## 全部概念\n",
    ]
    for name, meta in CONCEPT_META.items():
        index_lines.append(f"- [{name}]({doc_url('concepts/' + meta['slug'])})")
    write(DOCS_DIR / "concepts" / "index.md", "\n".join(index_lines))


def count_answered_investors(body: str) -> int:
    lines = body.splitlines()
    count = 0
    for i, line in enumerate(lines):
        if not line.startswith("## [[investors/"):
            continue
        block: list[str] = []
        for next_line in lines[i + 1:]:
            if next_line.startswith("## [[investors/"):
                break
            block.append(next_line)
        block_text = "\n".join(block)
        if "当前语料未涉及，已有素材不足以产生有价值的答案。" not in block_text:
            count += 1
    return count


def build_ten_questions_index() -> str:
    denominator = len(INVESTOR_META)
    stats: list[tuple[str, str, int]] = []
    for src in sorted((WIKI_DIR / "ten-questions").glob("Q*.md")):
        fm, body = parse_frontmatter(src.read_text(encoding="utf-8"))
        title = fm.get("title", src.stem)
        stats.append((src.stem, title, count_answered_investors(body)))

    lines = [
        render_frontmatter("投资十问", "ten-questions", "把同一个问题横向放到不同投资人身上读。"),
        "# 投资十问\n",
        f"这里不是人物传记层，而是把同一个问题横着放到不同投资人身上看。真正有价值的，不是某一个人的单独答案，而是同一个问题下，谁在什么地方给出了完全不同的回答。当前覆盖统计的口径已经扩到 `{denominator}`。\n",
        "## 怎么读这页\n",
        f"- 这里的 `x/{denominator}` 表示“当前有多少位核心投资人，在现有资料里能被有依据地回答这个问题”。",
        "- 如果你想看边界与反例，优先读 `Q02 / Q09`。",
        "- 如果你想看风险、路径和活下来，优先读 `Q05 / Q07 / Q08`。",
        "- 如果你想看研究方法与世界观，优先读 `Q01 / Q03 / Q10`。\n",
        "## 按最近提纯后的问题读\n",
        f"- **边界从哪里来**: [Q2]({doc_url('ten-questions/q02')})，最适合接 Buffett / Duan / Ackman 这几条线，看 `不碰什么` 到底是所有者纪律、反能力圈，还是结构性排雷。",
        f"- **风险是不是先于观点**: [Q5]({doc_url('ten-questions/q05')}) 与 [Q7]({doc_url('ten-questions/q07')})，最适合接 Howard / Druckenmiller / Ackman，看 `先活下来`、`路径正确`、`被迫卖出` 这些语言怎样分开。",
        f"- **组合怎么体现方法**: [Q8]({doc_url('ten-questions/q08')})，最适合接 Ted / Todd / Tracy / Druckenmiller，看集中、sizing、结构约束和能力边界怎样真正落到仓位。",
        f"- **错误暴露了什么**: [Q9]({doc_url('ten-questions/q09')})，最适合接 Terry / Tracy / Ackman / Anderson，看错误到底暴露的是管理层、资本结构、路径设计还是分布判断。\n",
        "## 全部问题\n",
    ]
    for stem, title, answered in stats:
        lines.append(f"- [{title}]({doc_url('ten-questions/' + question_slug(stem))}): {answered}/{denominator}")
    return "\n".join(lines)



def compile_ten_questions():
    index_out = DOCS_DIR / "ten-questions" / "index.md"
    write(index_out, build_ten_questions_index())

    questions_dir = WIKI_DIR / "ten-questions"
    for src in sorted(questions_dir.glob("*.md")):
        if src.name == "index.md":
            continue
        fm, body = parse_frontmatter(src.read_text(encoding="utf-8"))
        title = fm.get("title", src.stem)
        slug = question_slug(src.stem)
        out = DOCS_DIR / "ten-questions" / f"{slug}.md"
        cleaned_body = re.sub(r"^# .+\n+", "", body, count=1)
        write(
            out,
            render_frontmatter(title, f"ten-questions/{slug}", title)
            + convert_wikilinks(translate_common_phrases(translate_ten_question_quotes(cleaned_body)), out),
        )


TEN_QUESTION_QUOTE_TRANSLATIONS = {
    "“The approach that he and Lindsell find works best for them is the ‘slow buy and hold’ perspective of Warren Buffett.”": "“他和 Lindsell 最认同、也最适合自己的方法，是巴菲特式的‘慢买入、长持有’视角。”",
    "“The most likely requirement of success is finding the investment approach that is most emotionally satisfying for you.”": "“最可能决定你能否成功的，是找到那套在情绪上最适合你、最能让你长期坚持的方法。”",
    "“His counter-momentum approach to markets”": "“他对市场采取的是一种反动量的方法。”",
    "“We have a habit of looking at spinoffs.”": "“我们有长期研究分拆公司的习惯。”",
    "“there’s many securities that are radically misvalued and undervalued.”": "“市场里有很多证券被严重错定价，而且明显被低估。”",
    "“the intersection of economics and policy has made employing second-order thinking important”": "“经济与政策的交叉影响，使第二层思维变得格外重要。”",
    "“its edge comes from its collaborative culture and ability to allocate flexibly between equities and credit”": "“它的优势来自协作文化，以及在股票和信用之间灵活配置资本的能力。”",
    "“Even if it’s irrational, I think acknowledging one’s weaknesses is helpful, and not straying into areas where you have not demonstrated the ability to pick winners in the past.”": "“哪怕这种克制看上去不完全理性，我仍然认为承认自己的弱点是有帮助的，不要跑到那些你过去从未证明自己能持续挑出赢家的领域里去。”",
    "“I don’t think it’s helpful to think about that sort of thing.”": "“我觉得反复去想那一类事情并没有帮助。”",
    "“Shorting provides cash for you when the market goes down”": "“当市场下跌时，做空会为你提供现金。”",
    "“gold is a very large position for us.”": "“黄金在我们的组合里是一个非常大的头寸。”",
    "“there’s a problem with the overall monetary and fiscal policies”": "“整体货币政策和财政政策本身就存在问题。”",
    "“opportunistic sales ... took its gross and net exposures to multi-year lows and provided dry powder”": "“机会型卖出把总敞口和净敞口都压到了多年低位，也为后续出手腾出了干火药。”",
    "“event-driven, activist, and risk arbitrage positions ... due to their catalyst-oriented nature”": "“之所以增加事件驱动、主动推动和风险套利仓位，是因为这些机会天然带有催化剂导向。”",
    "“We think it’s madness to target a return.”": "“我们认为把回报目标当成硬指标，本身就是一种疯狂。”",
    "“My view is that you can target risk versus return.”": "“在我看来，你能真正设定的，是风险与回报的关系，而不是死盯某个回报数字。”",
    "“After sitting patiently on the sidelines with a mountain of cash”": "“在场边抱着大笔现金耐心等待了很久之后。”",
    "“The gatekeepers such as the SEC and sell-side analysts might not be acting on their behalf.”": "“像 SEC 和卖方分析师这样的守门人，未必真的站在股东一边行事。”",
    "“they should be appropriately skeptical of the various gatekeepers”": "“他们应该对各种守门人保持适度怀疑。”",
    "“improve its capital allocation framework”": "“改进它的资本配置框架。”",
    "“review its executive compensation programs to ensure management’s incentives remain aligned with stockholder value creation”": "“重新审视高管薪酬体系，确保管理层激励始终与股东价值创造保持一致。”",
    "“The importance of meeting management teams and assessing intent”": "“与管理层见面、判断其真实意图，这件事非常重要。”",
    "“Building and educating a long-term oriented client base”": "“建立并教育一批真正面向长期的客户基础。”",
    "“The value investing industry and value investing are two completely different things.”": "“价值投资这个行业，和价值投资这件事本身，是完全不同的两回事。”",
    "“What matters to us is, will the Chinese lose their thirst for Johnnie Walker Blue Label ... over the next 50 years?”": "“我们真正关心的是，未来五十年里，中国消费者会不会失去对尊尼获加蓝牌这类品牌的渴望？”",
    "“alignment of interests”": "“利益一致性。”",
    "“quality of management teams”": "“管理团队的质量。”",
    "“The ‘slow buy and hold’ perspective”": "“慢买入、长持有的视角。”",
    "“running winners”": "“让赢家继续跑。”",
    "“That’s been a core investment strategy for us for many, many, many years.”": "“这在很多很多年里，一直都是我们的核心投资策略。”",
    "“all of our shorts are idiosyncratic ideas”": "“我们的所有空头，都是公司特定型的独立想法。”",
    "“some with event-driven catalysts, others with quality characteristics, and several idiosyncratic themes”": "“其中有些仓位带有事件驱动催化剂，有些带有质量特征，还有一些属于独特主题。”",
    "“ability to allocate flexibly between equities and credit”": "“在股票和信用之间灵活配置的能力。”",
    "“Real focus here, though, on depth, not breadth.”": "“这里真正强调的，是深度，而不是广度。”",
    "“That’s really the founding principle of the firm is a real pursuit of talent.”": "“这家公司真正的创始原则，就是对顶尖人才的持续追求。”",
    "“The role of patient capital”": "“耐心资本所扮演的角色。”",
    "“How Baupost evaluates opportunities across asset classes”": "“Baupost 如何在不同资产类别之间评估机会。”",
    "“They explore timeless principles of market inefficiencies, the importance of temperament, specialization versus generalization, the role of patient capital…”": "“他们讨论的是一些不过时的原则：市场低效、性格的重要性、专精与泛化的取舍，以及耐心资本的作用……”",
    "“value investing is intellectually elegant.”": "“价值投资在智识上是一种非常优雅的方法。”",
    "“there’s a lot fewer people right now looking to try to buy undervalued companies.”": "“现在认真去寻找低估公司的投资者，已经少得多了。”",
    "“there will likely be periodic dislocations caused by the unconventional approach of this Administration”": "“这届政府的非常规做法，很可能会周期性地制造市场错位。”",
    "“What happens is that people always want to believe that this time is different”": "“人们总是想相信，这一次会不一样。”",
    "“securitization ... also gives you a lack of transparency.”": "“证券化这件事……同时也带来了透明度缺失。”",
}


def translate_ten_question_quotes(text: str) -> str:
    for english, chinese in TEN_QUESTION_QUOTE_TRANSLATIONS.items():
        text = text.replace(english, chinese)
    return text


COMMON_PHRASE_TRANSLATIONS = {
    "slow buy and hold": "慢买入、长持有",
    "quality investor": "质量投资者",
    "quality investing": "质量投资",
    "event-driven": "事件驱动",
    "second-order thinking": "第二层思维",
    "opportunistic allocator": "机会型配置者",
    "opportunistic allocation": "机会型配置",
    "special situations": "特殊情境",
    "engagement": "主动推动与沟通",
    "stock picker": "选股者",
    "cross-capital-structure": "跨资本结构",
    "multi-strategy": "多策略",
    "dynamic allocation": "动态配置",
    "credit / structured products / privates": "信用 / 结构化产品 / 私募资产",
    "headline reaction": "标题级反应",
    "gross / net exposure": "总敞口 / 净敞口",
    "dry powder": "干火药",
    "public confrontation": "公开对抗",
    "public combativeness": "公开对抗姿态",
    "patient capital": "耐心资本",
    "risk vs return": "风险与回报",
    "market inefficiencies": "市场低效",
    "value investor": "价值投资者",
    "long/short hedge fund manager": "多空对冲基金经理",
    "long/short": "多空",
    "market plumbing": "市场底层管道",
    "counter-momentum": "反动量",
    "mispricing": "错价",
    "transparency": "透明度",
    "gatekeepers": "守门人",
    "shorting": "做空",
    "spinoffs": "分拆",
    "broken market": "失灵市场",
    "run winners": "让赢家继续跑",
    "masterly inactivity": "高手式不作为",
    "beat market": "跑赢市场",
    "durability": "耐久性",
    "Tiger Cub": "老虎幼崽",
    "depth, not breadth": "重深度，不重广度",
    "founding principle": "创始原则",
    "forecast": "前瞻判断",
    "builder": "建造者",
    "pressure tester": "压力测试者",
    "founder-allocator": "创始人型配置者",
    "platform investing": "平台式投资",
    "edge": "优势来源",
    "catalyst-oriented nature": "催化剂导向特征",
    "quality characteristics": "质量特征",
    "platform assets": "平台型资产",
    "quality compounders": "高质量复利资产",
    "premium brand": "高端品牌",
    "developing economies": "发展中经济体",
    "heritage": "品牌历史积淀",
    "investment diamonds": "投资钻石",
    "tech-enabled": "技术赋能型",
    "intellectual property": "知识产权",
    "tech-enabled companies": "技术赋能型公司",
    "tech-led growth opportunities": "技术驱动的增长机会",
    "activist": "主动推动型投资者",
    "risk arb": "风险套利",
    "home run": "本垒打",
    "skin in the game": "与结果共担",
    "consensus trade": "共识交易",
    "contrarian": "逆向投资者",
    "alpha": "阿尔法收益",
    "regime": "市场体制环境",
    "duration": "持有久期",
    "flexibility": "灵活性",
    "franchise": "特许经营资产",
    "winners": "赢家",
    "losers": "输家",
    "thesis": "投资论点",
    "activism": "主动推动",
    "opportunistic book": "机会型组合",
    "equities": "股票",
    "credit": "信用",
    "focus": "聚焦",
    "Proxy Statement": "委托书文件",
    "variant perception": "非共识认知",
    "charisma": "个人魅力",
    "sell-side": "卖方",
    "opportunistic sales": "机会型卖出",
    "risk arb": "风险套利",
    "idiosyncratic themes": "独特主题",
    "activist positions": "主动推动仓位",
    "forensic long-short": "法证式多空",
    "plumbing risk": "底层管道风险",
    "focus在": "聚焦在",
    "focus（聚焦）": "聚焦",
    "Investment Simulator": "投资模拟器",
    "Mag 7": "美股七巨头",
}


def translate_common_phrases(text: str) -> str:
    for english, chinese in COMMON_PHRASE_TRANSLATIONS.items():
        text = text.replace(english, chinese)
    return text

def compile_sources():
    index_lines = [
        render_frontmatter("来源", "sources", "原始材料的登记表和出处入口。"),
        "这些页面不承担完整阅读体验，主要用于给正文引用提供稳定落点。\n",
    ]
    for idx, raw_path in enumerate(RAW_FILES, start=1):
        meta, body = parse_frontmatter(raw_path.read_text(encoding="utf-8"))
        slug = source_slug(raw_path.name, idx)
        title = meta.get("title", raw_path.stem)
        source = meta.get("source", "")
        description = meta.get("description", "原始材料来源页。")
        source_meta, excerpt = extract_source_meta_and_excerpt(body)
        page = [
            render_frontmatter(title, f"sources/{slug}", description),
            f"**原文件名**: `{raw_path.name}`  ",
            f"**外部来源**: {source}\n" if source else "",
            f"{source_meta}\n" if source_meta else "",
            "## 摘要\n",
            description + "\n",
            "## 节选\n",
            clean_excerpt(strip_images(excerpt)) or "当前未提取节选。",
        ]
        write(DOCS_DIR / "sources" / f"{slug}.md", "\n".join(page))
        index_lines.append(f"- [{title}]({doc_url(f'sources/{slug}')})")
    write(DOCS_DIR / "sources" / "index.md", "\n".join(index_lines))


def compile_dialogues():
    dialogues_dir = WIKI_DIR / "dialogues"
    index_src = dialogues_dir / "index.md"
    if not index_src.exists():
        return

    _, body = parse_frontmatter(index_src.read_text(encoding="utf-8"))
    index_out = DOCS_DIR / "dialogues" / "index.md"
    write(
        index_out,
        render_frontmatter("对话与争议", "dialogues", "对比会逼迫读者形成自己的判断。")
        + convert_wikilinks(body, index_out),
    )

    for src in sorted(dialogues_dir.glob("*.md")):
        if src.name == "index.md":
            continue
        _, body = parse_frontmatter(src.read_text(encoding="utf-8"))
        slug = DIALOGUE_SLUG_OVERRIDES.get(src.stem, src.stem)
        out = DOCS_DIR / "dialogues" / f"{slug}.md"
        cleaned_body = re.sub(r"^# .+\n+", "", body, count=1)
        write(
            out,
            render_frontmatter(src.stem, f"dialogues/{slug}", "把方法冲突显性化的对照页。")
            + convert_wikilinks(cleaned_body, out),
        )


def parse_log_entries(log_text: str) -> list[dict[str, str]]:
    pattern = re.compile(
        r"## \[(?P<date>[^\]]+)\] (?P<title>[^\n]+)\n(?P<body>.*?)(?=\n## \[|\Z)",
        re.S,
    )
    return [match.groupdict() for match in pattern.finditer(log_text)]


def clean_backtick_item(item: str) -> str:
    item = item.strip()
    if item.startswith("[[") and item.endswith("]]"):
        item = item[2:-2]
    if "/" in item:
        item = item.split("/")[-1]
    return item


def unique_keep_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        ordered.append(item)
    return ordered


def summarize_log_entry(entry: dict[str, str]) -> list[str]:
    title = entry["title"]
    body = entry["body"]

    if title.startswith("tangen-ako-pass |"):
        return ["新增 Nicolai / AKO 两篇关键材料，并补出 AKO Capital 机构页与坦根人物线。"]

    if title.startswith("tiger-cubs-lee-stephen-pass |"):
        return ["新增 Lee Ainslie / Stephen Mandel 四篇关键材料，并补出 Maverick / Lone Pine 两条 Tiger Cub 主线。"]

    if title.startswith("seed |"):
        return ["首批内容上线：建立人物页、公司页和来源索引。"]

    if title.startswith("schema-upgrade |"):
        return ["阅读结构升级：人物页更完整了，也新增了概念层和比较矩阵。"]

    if title.startswith("refinement |"):
        added_line = next((line for line in body.splitlines() if "新增 `[[investors/" in line), "")
        names = [clean_backtick_item(item) for item in re.findall(r"`([^`]+)`", added_line)]
        people = unique_keep_order(names)
        if people:
            return [f"新增人物：{'、'.join(people)}。"]
        return ["新增人物：补齐先前匿名人物并进入索引导航。"]

    if title.startswith("institutions |"):
        names = [clean_backtick_item(item) for item in re.findall(r"`([^`]+)`", body)]
        institutions = [
            name for name in names
            if name in {"Baillie Gifford", "Berkshire Hathaway", "Nomad Investment Partnership", "Oaktree Capital", "Fundsmith"}
        ]
        if institutions:
            return [f"新增机构：{'、'.join(institutions)}；机构页现在能单独看长期持有、激励结构和传承。"]
        return ["新增机构页：现在能单独看长期持有、激励结构和传承。"]

    if title == "source-first sync":
        return []

    if title == "source parity fix":
        return ["新增入口：对话与争议页上线，人物、公司、机构、概念首页也补齐了。"]

    if title.startswith("naval ingest |"):
        return ["新增人物：纳瓦尔·拉维坎特；新增概念：判断力。"]

    if title.startswith("naval backfill |"):
        return ["更新公司：苹果、SpaceX；新增对话：看懂边界 vs 品味判断。"]

    if title.startswith("naval quote refinement |"):
        return ["更新公司：苹果、SpaceX，两页的纳瓦尔引言重写。"]

    if title.startswith("schema-finalization |"):
        return ["新增投资十问，并把公司页扩到更完整的一批。"]

    if title.startswith("evidence-tightening |"):
        return ["投资十问和公司页一起收紧了，现在答案和引言更贴原始材料。"]

    if title.startswith("investor-evidence-backfill |"):
        return []

    if title.startswith("investor-section-evidence |"):
        return []

    if title.startswith("extraction-quality-gate |"):
        return ["投资十问更新：一些答案被重写得更锋利，也更能看出彼此差异。"]

    if title.startswith("q1-tightening |"):
        return ["投资十问更新：优势问题下的关键答案重新收紧了。"]

    if title.startswith("q8-q10-tightening |"):
        return ["投资十问更新：组合构建和系统性误判两组答案被补强了。"]

    if title.startswith("investor-why-refactor |"):
        return ["阅读结构升级：人物页现在更回答“为什么这样投”，投资十问则专门负责横向审问。"]

    fallback = title.split("|", 1)[-1].strip() if "|" in title else title.strip()
    return [fallback]


def build_recent_updates(log_text: str) -> list[str]:
    items: list[str] = []
    entries = parse_log_entries(log_text)

    ordered_entries = sorted(enumerate(entries), key=lambda item: (item[1]["date"], item[0]), reverse=True)
    for _, entry in ordered_entries:
        if entry["title"] in {"source-first sync"}:
            continue
        date_text = f"`{entry['date']}` "
        summaries = summarize_log_entry(entry)
        for idx, summary in enumerate(summaries):
            if not summary:
                continue
            if any(token in summary for token in ["源 wiki", "编译站点", "源站对齐", "source", "canonical"]):
                continue
            prefix = date_text if idx == 0 else " " * len(date_text)
            items.append(f"- {prefix}{summary}")
    return items[:8]

def compile_home():
    index_src = WIKI_DIR / "index.md"
    _, index_body = parse_frontmatter(index_src.read_text(encoding="utf-8"))
    sections = parse_sections(index_body)
    log_text = (WIKI_DIR / "log.md").read_text(encoding="utf-8")
    recent_lines = build_recent_updates(log_text)
    featured_quotes = collect_featured_quotes()
    featured_block = "\n\n".join(f"> {quote}" for quote in featured_quotes) if featured_quotes else "> 现有资料暂未提取到可用语录。"
    lead_text = sections.get("_lead", "")
    if lead_text.startswith("# "):
        lead_lines = lead_text.splitlines()
        lead_text = "\n".join(lead_lines[1:]).lstrip()
    filtered_lead_lines = []
    for line in lead_text.splitlines():
        if any(token in line for token in ["canonical", "下游展示层", "重新编译站点", "code/investors", "`wiki/`"]):
            continue
        filtered_lead_lines.append(line)
    lead_text = "\n".join(filtered_lead_lines).strip()
    home = render_frontmatter(
        "投资大师系列",
        "",
        "把分散的投资访谈、合伙人信和机构材料，编译成一个可以持续更新的外部阅读入口。",
    ) + "\n".join(
        [
            convert_wikilinks(lead_text, DOCS_DIR / "index.md"),
            "\n## 从哪里开始\n",
            convert_wikilinks(sections.get("从哪里开始", ""), DOCS_DIR / "index.md"),
            "\n## 精选语录墙\n",
            featured_block,
            "\n## 对话与争议\n",
            convert_wikilinks(sections.get("对话与争议", ""), DOCS_DIR / "index.md"),
            "\n## 最近更新\n",
            "\n".join(recent_lines),
        ]
    )
    write(DOCS_DIR / "index.md", home)


def main():
    ensure_clean_docs()
    compile_investors()
    compile_companies()
    compile_institutions()
    compile_concepts()
    compile_ten_questions()
    compile_sources()
    compile_dialogues()
    compile_home()
    print(f"Compiled docs into {DOCS_DIR}")


if __name__ == "__main__":
    main()
