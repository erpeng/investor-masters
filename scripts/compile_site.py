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
    "特里·史密斯": {
        "slug": "terry-smith",
        "tagline": "相信挑对公司之后几乎不需要再做什么的人。",
        "institution": ("Fundsmith", "institutions/fundsmith"),
        "holdings": "微软、诺和诺德",
        "methods": "高质量复利 / 少犯错 / 长期持有",
    },
    "段永平": {
        "slug": "duan-yongping",
        "tagline": "把“不懂不碰”执行到生活方式里的投资人。",
        "institution": ("独立", None),
        "holdings": "苹果、腾讯",
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
    "斯坦利·德鲁肯米勒": {
        "slug": "stanley-druckenmiller",
        "tagline": "知道什么时候该把仓位做大的人。",
        "institution": ("Duquesne", None),
        "holdings": "宏观趋势、成长拐点",
        "methods": "仓位 / 趋势 / 快速修正",
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
    "尼科莱·坦根": {
        "slug": "nicolai-tangen",
        "tagline": "把投资理解成情报学与组织训练的人。",
        "institution": ("挪威主权财富基金", None),
        "holdings": "AKO、主权基金配置",
        "methods": "提问 / 情报学 / 组织训练",
    },
    "特蕾西·布里特·库尔": {
        "slug": "tracy-britt-cool",
        "tagline": "从伯克希尔原则出发，把长期主义压进经营系统的人。",
        "institution": ("Kanbrick", None),
        "holdings": "Kanbrick、中型企业长期持有",
        "methods": "经营型投资 / 文化优先 / 资本配置",
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
    "特里·史密斯": "特里·史密斯的信息来源偏向企业基本面本身，而不是外部故事。他反复盯收入质量、资本回报率、现金流、管理层纪律和竞争地位，核心是从企业长期报表里提炼出“这是不是一台高质量复利机器”。他不太依赖宏观预测，也不太依赖复杂渠道优势。",
    "段永平": "段永平的信息来源很克制，几乎都围绕“我能不能真正看懂”展开。他更看重产品体验、企业常识、管理层取向和长期商业逻辑，而不是市场上铺天盖地的信息流。对他来说，来源不是越多越好，而是能不能帮助自己建立足够清楚的能力圈边界。",
    "詹姆斯·安德森": "安德森的信息来源更像变化探测器。他会持续跟踪技术、创业公司、创始人、产业结构变化和极少数可能变成超级赢家的企业，把这些信息组合成对未来分布的判断。相比看静态指标，他更看谁正在真正改变世界，以及这种改变会不会被市场长期低估。",
    "汤姆·斯莱特": "斯莱特延续了 Baillie Gifford 的成长信息系统，重点不是短期数字，而是技术渗透、价值链位置、未上市资产动向和少数卓越公司的长期扩张路径。他的信息来源天然更靠近前沿行业参与者和长期产业趋势，而不是传统价值投资者常用的低估值筛选。",
    "劳伦斯·伯恩斯": "伯恩斯的信息来源带有很强的产业链研究特征。现有资料显示，他擅长沿着 AI 和科技价值链去拆解机会，从硬件、基础设施到应用层逐层看清楚价值是如何传导的。这意味着他获得信息的方式，更像研究一个系统，而不是只盯一家公司的财务表。",
    "莫尼什·帕伯莱": "帕伯莱的信息来源高度依赖可借鉴的先例。他最典型的方法不是从零发明判断，而是研究历史上的成功投资、伟大投资人的公开持仓、股东信和可复制案例，然后在新的标的上寻找相似结构。这使他的来源系统天然带有“克隆”和模式迁移的味道。",
    "比尔·阿克曼": "阿克曼的信息来源更像一套战役情报系统。他会围绕少数核心标的做深研究，结合管理层、资本结构、治理问题、行业错配和公开表达，逐步把投资论点推到市场台前。对他来说，信息不只是用来理解公司，也是用来组织一场能够推动结果的行动。",
    "斯坦利·德鲁肯米勒": "德鲁肯米勒的信息来源很有辨识度：他既看宏观与价格，也高度依赖自己信任的专家网络。现有资料里最鲜明的一点是，他会非常认真观察那些在细分领域比自己懂得多得多的人在看什么、买什么，再用自己的模式识别和仓位能力把这些线索转成下注。换句话说，他不是靠自己懂所有细节，而是靠识别谁真的懂，以及市场会怎样消化这些变化。",
    "托德·库姆斯": "托德·库姆斯的信息来源偏经营化而非市场化。现有资料显示，他会从单店模型、回本周期、投资回报率这类非常具体的经营指标切入，把复杂企业先拆成可验证的小单元，再决定是否值得下注。这让他的信息入口更像运营视角，而不是交易视角。",
    "泰德·韦施勒": "韦施勒的信息来源看起来低噪音、重关系、重清晰表达。现有资料里，他更像那种通过长期跟踪企业、管理层和少数高质量机会来形成判断的投资人，而不是靠频繁切换信息渠道。他依赖的不是花哨的情报优势，而是持续积累的商业理解和人与人的判断。",
    "尼克·斯利普": "斯利普的信息来源天然反短期化。他更看重年报、长期经营记录、实地调研和少数高质量企业多年如一日的行为模式，而不是短保质期市场信息。对他来说，真正有价值的信息往往来自那些能解释企业十年后为什么更强的材料，而不是明天的股价催化剂。",
    "凯斯·扎卡里亚": "扎卡里亚的信息来源与斯利普高度耦合，但更偏研究补位。现有资料明确提到，他对亚太市场和跨区域机会的理解是 Nomad 研究系统的重要组成部分。这意味着他更像是把局部市场经验、深度研究和组合执行连接起来的人。",
    "格雷格·詹森": "詹森的信息来源更接近一台组织化研究机器。他不仅看宏观和市场数据，也非常在意新研究怎样被系统吸收、怎样在尚未完全模型化时先进入组合测试。对他来说，来源价值不只在信息本身，还在组织能否快速把新认知转成决策。",
    "尼科莱·坦根": "坦根的信息来源非常像高质量传感器系统。他高度重视访谈、提问方式、语言细节和人在压力下暴露出来的真实特征，同时也会训练团队像顶级运动员一样提升研究与复盘能力。换句话说，他获取信息不只靠数据，还靠从人与对话里捕捉真实信号。",
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
    "腾讯": {"slug": "tencent", "consensus": "腾讯是中国互联网质量资产的代表样本，也是中文语境里长期主义投资最容易落地的案例之一。"},
    "小红书": {"slug": "xiaohongshu", "consensus": "它的意义主要在于让读者看到 Baillie Gifford 如何把全球成长框架继续延伸到中国新平台。"},
    "MiniMax": {"slug": "minimax", "consensus": "它不是成熟公司样本，而是新一代 AI 资产如何进入成长机构视野的一个窗口。"},
}

INSTITUTION_META = {
    "Baillie Gifford": {"slug": "baillie-gifford"},
    "Berkshire Hathaway": {"slug": "berkshire-hathaway"},
    "Nomad Investment Partnership": {"slug": "nomad-investment-partnership"},
    "Oaktree Capital": {"slug": "oaktree-capital"},
    "Fundsmith": {"slug": "fundsmith"},
}

CONCEPT_META = {
    "护城河": {"slug": "moat"},
    "能力圈": {"slug": "circle-of-competence"},
    "第二层思维": {"slug": "second-level-thinking"},
    "共享规模经济": {"slug": "scale-economies-shared"},
    "时间套利": {"slug": "time-arbitrage"},
    "超级赢家": {"slug": "super-winners"},
    "反脆弱与仓位管理": {"slug": "antifragility-and-position-sizing"},
    "克隆策略": {"slug": "cloning"},
    "判断力": {"slug": "judgment"},
}


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


def collect_featured_quotes(limit: int = 4) -> list[str]:
    quotes: list[str] = []
    seen: set[str] = set()
    for source_path in sorted((WIKI_DIR / "investors").glob("*.md")):
        if source_path.name in {"index.md", "比较矩阵.md"}:
            continue
        _, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        sections = parse_sections(body)
        for line in sections.get("标志性语录", "").splitlines():
            stripped = line.strip()
            if not stripped.startswith("- "):
                continue
            quote = stripped[2:]
            if "来源：" in quote:
                quote = quote.split("来源：", 1)[0].strip()
            if quote and quote not in seen:
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
    for name, meta in COMPANY_META.items():
        key = f"companies/{name}"
        page_map[key] = f"companies/{meta['slug']}"
        type_map[key] = name
    for name, meta in INSTITUTION_META.items():
        key = f"institutions/{name}"
        page_map[key] = f"institutions/{meta['slug']}"
        type_map[key] = name
    for name, meta in CONCEPT_META.items():
        key = f"concepts/{name}"
        page_map[key] = f"concepts/{meta['slug']}"
        type_map[key] = name
    page_map["dialogues/index"] = "dialogues"
    page_map["dialogues/质量价值 vs 成长非共识"] = "dialogues/quality-vs-growth"
    page_map["dialogues/保守的风险语言 vs 激进的仓位语言"] = "dialogues/risk-and-conviction"
    page_map["dialogues/不懂不碰 vs 未来信息才重要"] = "dialogues/certainty-vs-future"
    page_map["dialogues/看懂边界 vs 品味判断"] = "dialogues/boundary-vs-taste"
    page_map["investors/index"] = "investors/index"
    page_map["companies/index"] = "companies/index"
    page_map["institutions/index"] = "institutions/index"
    page_map["concepts/index"] = "concepts/index"
    page_map["log"] = "index"
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


WIKILINK_RE = re.compile(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]")


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
    for folder in ["investors", "companies", "institutions", "concepts", "sources", "dialogues"]:
        (DOCS_DIR / folder).mkdir(parents=True, exist_ok=True)


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(normalize_reader_facing_terms(content).strip() + "\n", encoding="utf-8")


def doc_url(path: str) -> str:
    return f"{SITE_BASE}/{path.strip('/')}/"


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
        institution_name, institution_path = meta["institution"]
        if institution_path:
            institution_md = f"[{institution_name}]({doc_url(institution_path)})"
        else:
            institution_md = institution_name
        output = DOCS_DIR / "investors" / f"{meta['slug']}.md"
        quote = convert_wikilinks(first_quote(sections.get("标志性语录", "")), output)
        info_sources = sections.get("投资信息来源") or INVESTOR_INFO_SOURCES.get(name, "现有资料更偏观点与案例呈现，尚未把这位投资人的信息来源系统单独展开。")
        pieces = [
            render_frontmatter(name, f"investors/{meta['slug']}", meta["tagline"]),
            "> **一句话定义**  ",
            f"> {meta['tagline']}\n",
            f"> {quote}\n" if quote else "",
            f"**所属机构**: {institution_md}  ",
            f"**代表性持仓**: {meta['holdings']}  ",
            f"**核心方法**: {meta['methods']}\n",
            "## 简介\n",
            convert_wikilinks(sections.get("简介", "现有资料暂未涉及。"), output),
            "\n## 投资信息来源\n",
            convert_wikilinks(info_sources, output),
            "\n## 投资思想\n",
            convert_wikilinks(sections.get("投资思想", "当前语料未涉及。"), output),
            "\n## 投资策略\n",
            convert_wikilinks(sections.get("投资策略", "当前语料未涉及。"), output),
            "\n## 标志性语录\n",
            convert_wikilinks(sections.get("标志性语录", "当前语料未涉及。"), output),
            "\n## 核心失误\n",
            convert_wikilinks(sections.get("核心失误", "当前语料未涉及。"), output),
            "\n## 与其他人的差异\n",
            convert_wikilinks(sections.get("投资风格与其他人的差异", "当前语料未涉及。"), output),
            "\n## 投资业绩\n",
            convert_wikilinks(sections.get("投资业绩", "当前语料未涉及。"), output),
            "\n## 投资风格相近的人\n",
            convert_wikilinks(sections.get("投资风格相近的人", "当前语料未涉及。"), output),
            "\n## 主要来源\n",
            convert_wikilinks(sections.get("主要来源", "当前语料未涉及。"), output),
        ]
        write(output, "\n".join([p for p in pieces if p]))

    index_output = DOCS_DIR / "investors" / "index.md"
    lines = [
        render_frontmatter("投资人", "investors", "从思维方式切入，而不是从履历切入。"),
        "这里不是投资人物百科，而是按“值得花十分钟读谁”来组织的入口。\n",
        "## 从哪里开始\n",
        f"- **价值投资**: [沃伦·巴菲特]({doc_url('investors/warren-buffett')})、[查理·芒格]({doc_url('investors/charlie-munger')})、[特里·史密斯]({doc_url('investors/terry-smith')})",
        f"- **成长投资**: [詹姆斯·安德森]({doc_url('investors/james-anderson')})、[汤姆·斯莱特]({doc_url('investors/tom-slater')})、[劳伦斯·伯恩斯]({doc_url('investors/lawrence-burns')})",
        f"- **宏观与风险**: [霍华德·马克斯]({doc_url('investors/howard-marks')})、[斯坦利·德鲁肯米勒]({doc_url('investors/stanley-druckenmiller')})、[格雷格·詹森]({doc_url('investors/greg-jensen')})",
        f"- **最不寻常的思维**: [尼克·斯利普]({doc_url('investors/nick-sleep')})、[尼科莱·坦根]({doc_url('investors/nicolai-tangen')})、[纳瓦尔·拉维坎特]({doc_url('investors/naval-ravikant')})\n",
        "## 比较视图\n",
        f"- [投资人比较矩阵]({doc_url('investors/comparison-matrix')})",
        "\n## 全部投资人\n",
    ]
    for name, meta in INVESTOR_META.items():
        lines.append(f"- [{name}]({doc_url('investors/' + meta['slug'])})")
    write(index_output, "\n".join(lines))

    matrix_src = WIKI_DIR / "investors" / "比较矩阵.md"
    _, matrix_body = parse_frontmatter(matrix_src.read_text(encoding="utf-8"))
    write(
        DOCS_DIR / "investors" / "comparison-matrix.md",
        render_frontmatter("投资人比较矩阵", "investors/comparison-matrix", "把不同方法放在同一张表里看。")
        + convert_wikilinks(matrix_body, DOCS_DIR / "investors" / "comparison-matrix.md"),
    )


def compile_companies():
    for name, meta in COMPANY_META.items():
        source_path = WIKI_DIR / "companies" / f"{name}.md"
        _, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        sections = parse_sections(body)
        output = DOCS_DIR / "companies" / f"{meta['slug']}.md"
        content = [
            render_frontmatter(name, f"companies/{meta['slug']}", meta["consensus"]),
            f"> **争议与共识**  \n> {meta['consensus']}\n",
            "## 哪些投资人提到过\n",
            convert_wikilinks(sections.get("哪些投资人提到过", "当前语料未涉及。"), output),
            "\n## 当前观察\n",
            convert_wikilinks(sections.get("当前观察", "当前语料未涉及。"), output),
            "\n## 相关页面\n",
            convert_wikilinks(sections.get("相关页面", "当前语料未涉及。"), output),
        ]
        write(output, "\n".join(content))

    write(
        DOCS_DIR / "companies" / "index.md",
        render_frontmatter("公司", "companies", "不是公司百科，而是“为什么顶级投资人反复提到它们”。")
        + "\n".join(
            [
                "这些页面最值得看的不是引言列表，而是同一家公司如何被不同投资人用不同方法读取。\n",
                f"- [亚马逊]({doc_url('companies/amazon')}): 同一家公司，三种完全不同的读法。",
                f"- [特斯拉]({doc_url('companies/tesla')}): 质量价值与成长非共识的正面碰撞。",
                f"- [伯克希尔·哈撒韦]({doc_url('companies/berkshire-hathaway')}): 同时是公司、机构和方法论母本。",
                "\n## 全部公司\n",
            ]
        ),
    )
    companies_index = DOCS_DIR / "companies" / "index.md"
    with companies_index.open("a", encoding="utf-8") as f:
        for name, meta in COMPANY_META.items():
            f.write(f"- [{name}]({doc_url('companies/' + meta['slug'])})\n")


def compile_institutions():
    for name, meta in INSTITUTION_META.items():
        source_path = WIKI_DIR / "institutions" / f"{name}.md"
        _, body = parse_frontmatter(source_path.read_text(encoding="utf-8"))
        output = DOCS_DIR / "institutions" / f"{meta['slug']}.md"
        cleaned_body = re.sub(r"^# .+\n+", "", body, count=1)
        write(
            output,
            render_frontmatter(name, f"institutions/{meta['slug']}", f"{name} 的机构级哲学、文化与传承。")
            + convert_wikilinks(cleaned_body, output),
        )


    write(
        DOCS_DIR / "institutions" / "index.md",
        render_frontmatter("机构", "institutions", "激励结构决定投资人能做什么，而不只是想做什么。")
        + "\n".join(
            [
                "读机构页的重点，不是规模大小，而是看清楚：一家机构靠什么保护时间维度、靠什么把理念写进制度。\n",
                f"- [Nomad Investment Partnership]({doc_url('institutions/nomad-investment-partnership')}): 为什么 Sleep 能拿亚马逊二十年。",
                f"- [Berkshire Hathaway]({doc_url('institutions/berkshire-hathaway')}): 为什么永久资本和保险 float 能形成独特制度优势。",
                f"- [Oaktree Capital]({doc_url('institutions/oaktree-capital')}): 为什么备忘录不只是写作，而是组织知识资产。",
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
        write(
            output,
            render_frontmatter(name, f"concepts/{meta['slug']}", f"{name} 在这个 corpus 里的最佳入口。")
            + convert_wikilinks(body, output),
        )

    index_lines = [
        render_frontmatter("概念", "concepts", "跨人物阅读时，最容易反复出现的那几根骨架。"),
        "如果你不想先读人物，可以先读概念。概念页最适合当作跨投资人的公共词典。\n",
        f"- [护城河]({doc_url('concepts/moat')})",
        f"- [能力圈]({doc_url('concepts/circle-of-competence')})",
        f"- [第二层思维]({doc_url('concepts/second-level-thinking')})",
        f"- [共享规模经济]({doc_url('concepts/scale-economies-shared')})",
        f"- [判断力]({doc_url('concepts/judgment')})",
        "\n## 全部概念\n",
    ]
    for name, meta in CONCEPT_META.items():
        index_lines.append(f"- [{name}]({doc_url('concepts/' + meta['slug'])})")
    write(DOCS_DIR / "concepts" / "index.md", "\n".join(index_lines))


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

    slug_map = {
        "质量价值 vs 成长非共识": "quality-vs-growth",
        "保守的风险语言 vs 激进的仓位语言": "risk-and-conviction",
        "不懂不碰 vs 未来信息才重要": "certainty-vs-future",
        "看懂边界 vs 品味判断": "boundary-vs-taste",
    }
    for src in sorted(dialogues_dir.glob("*.md")):
        if src.name == "index.md":
            continue
        _, body = parse_frontmatter(src.read_text(encoding="utf-8"))
        slug = slug_map.get(src.stem, src.stem)
        out = DOCS_DIR / "dialogues" / f"{slug}.md"
        write(
            out,
            render_frontmatter(src.stem, f"dialogues/{slug}", "把方法冲突显性化的对照页。")
            + convert_wikilinks(body, out),
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

    fallback = title.split("|", 1)[-1].strip() if "|" in title else title.strip()
    return [fallback]


def build_recent_updates(log_text: str) -> list[str]:
    items: list[str] = []
    for entry in reversed(parse_log_entries(log_text)):
        if entry["title"] in {"source-first sync"}:
            continue
        date_text = f"`{entry['date']}` "
        summaries = summarize_log_entry(entry)
        for idx, summary in enumerate(summaries):
            if any(token in summary for token in ["源 wiki", "编译站点", "源站对齐", "source", "canonical"]):
                continue
            prefix = date_text if idx == 0 else " " * len(date_text)
            items.append(f"- {prefix}{summary}")
    return items

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
        "Investors Wiki",
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
    compile_sources()
    compile_dialogues()
    compile_home()
    print(f"Compiled docs into {DOCS_DIR}")


if __name__ == "__main__":
    main()
