#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replay the 2026Q3 institution overview and horizontal pages.

Read-only input: immutable JSON snapshots. Writes only institution overview and
horizontal Markdown under --vault; never changes raw evidence, audit cards,
registries, logs, companies or the separate long-history trend pages.
"""
from pathlib import Path
import argparse
import json
import re
import collections
from datetime import datetime
from zoneinfo import ZoneInfo
import generate_13f_trends as g

VAULT=Path(g.DEFAULT_VAULT)
SNAPSHOT_DIR=VAULT/'raw/data/13f-20261117'
DATE='2026-11-17'
WEIGHTS={'berkshire':1.5,'himalaya':1.4,'hh':1.4,'duquesne':.8,'appaloosa':.8}
FIRST_KEYS=tuple(g.MANAGERS)
NEW_MANAGERS={
    'atreides': ('Atreides', 'Atreides Management', 1777813),
    'coatue': ('Coatue', 'Coatue Management', 1135730),
    'altimeter': ('Altimeter', 'Altimeter Capital', 1541617),
    'fundsmith': ('Fundsmith', 'Fundsmith', 1569205),
    'pershing': ('Pershing', 'Pershing Square', 2026053),
}
WEIGHTS.update(atreides=.9,coatue=1.1,altimeter=1.1,fundsmith=1.4,pershing=1.4)
WEIGHTS.update(akre=1.4,dorsey=1.3,ako=1.3,giverny=1.4,oakmark=1.1)
WEIGHTS.update({'third-point':1.0,'kensico':1.0,'maverick':.9,'baupost':1.1,
                'baillie':1.1,'greenlight':1.0,'lone-pine':1.0,'tudor':.6})
META={k:{'title':v[0],'name':v[1],'cik':v[2]} for k,v in g.ALL_MANAGERS.items()}
INSTITUTION_KEYS=FIRST_KEYS
CROSS_KEYS=FIRST_KEYS
SNAPSHOT_PATHS={}
# Stable business descriptions retained from the existing institution pages.
# This catalog makes repeated rendering independent of the previous output.
DESC={'AA': ('Alcoa Corporation', '经营铝土矿、氧化铝及原铝业务，关注商品价格与能源成本'),
 'AAPL': ('Apple Inc', '消费电子与服务平台，iPhone 是核心入口，服务业务贡献高毛利和生态粘性'),
 'AMZN': ('Amazon Com Inc', '电商、物流、AWS 云和广告共同构成的平台公司，长期变量是基础设施外部化能力'),
 'AXP': ('American Express Co', '美国运通，高端支付网络和发卡体系，靠商户网络、会员消费力和信用风控变现'),
 'BABA': ('Alibaba Group Hldg Ltd', '阿里巴巴，电商、云、国际零售和本地生活组合，核心看中国消费、平台效率和云业务重估'),
 'BAC': ('Bk Of America Corp', '美国银行，大型综合银行，核心变量是存款成本、贷款质量、利率周期和资本回报'),
 'BRK-B': ('Berkshire Hathaway Inc Del', '伯克希尔哈撒韦，保险 float、全资经营业务和公开股票组合构成的复合资本配置平台'),
 'CB': ('Chubb Limited', 'Chubb，全球财产险和意外险公司，核心看承保纪律、投资收益和商业保险周期'),
 'CPNG': ('Coupang', 'Coupang，韩国电商与物流平台，优势来自高频消费、仓配密度和会员体系'),
 'CRDO': ('Credo Technology Group Holding', '提供数据中心高速连接芯片与有源电缆，关注带宽需求和客户集中度'),
 'CROX': ('Crocs Inc', 'Crocs，休闲鞋品牌公司，核心看品牌热度、渠道扩张和 HeyDude 整合'),
 'CVX': ('Chevron Corp New', '雪佛龙，综合油气公司，现金流由油气价格、上游资产质量和资本纪律驱动'),
 'DIS': ('Disney Walt Co', '迪士尼，内容 IP、主题乐园、体育媒体和流媒体组成的娱乐资产组合'),
 'EWBC': ('East West Bancorp Inc', '东西银行，服务美国与大中华商业往来的区域银行，核心看存款、信贷和利率周期'),
 'EWY': ('iShares MSCI South Korea ETF', '跟踪韩国股票市场的交易所交易基金，不是单一公司'),
 'EWZ': ('iShares MSCI Brazil ETF', '跟踪巴西股票市场的交易所交易基金，不是单一公司'),
 'FOXA': ('Fox Corporation A 类股', '经营新闻、体育与电视媒体业务，收入来自广告和内容分发'),
 'GOOG': ('Alphabet Inc', 'Alphabet 的 C 类股，核心资产是 Google 搜索、YouTube、广告网络、Android 和 Google Cloud'),
 'GOOGL': ('Alphabet Inc', 'Alphabet 的 A 类股，核心资产是 Google 搜索、YouTube、广告网络、Android 和 Google Cloud'),
 'INSM': ('Insmed Incorporated', '专注严重疾病治疗的生物制药公司，关注药物商业化与研发进展'),
 'KHC': ('Kraft Heinz Co', '卡夫亨氏，包装食品公司，核心看品牌定价力、成本控制和品类增长修复'),
 'KO': ('Coca Cola Co', '可口可乐，全球饮料品牌和装瓶生态系统，护城河来自品牌、渠道和高频消费'),
 'MCO': ('Moodys Corp', '穆迪，信用评级和金融数据分析公司，收入来自债券发行周期与风险数据订阅'),
 'META': ('Meta Platforms Inc', 'Meta，社交网络、广告系统和 AI 推荐平台，核心资产是 Facebook、Instagram、WhatsApp 和广告模型'),
 'MSFT': ('Microsoft Corp', '微软，企业软件、Azure 云、Office、Windows 和 AI 基础设施共同构成的生产力平台'),
 'MU': ('Micron Technology, Inc.', '生产 DRAM、HBM 与 NAND 存储产品，受供需、价格与资本开支周期影响'),
 'NAMS': ('NewAmsterdam Pharma Company N.V.', '研发心血管疾病药物的生物制药公司，关注临床、审批和商业化'),
 'NRG': ('NRG Energy, Inc.', '美国发电、零售能源及相关服务企业，关注电价、负荷和资本配置'),
 'NTRA': ('Natera, Inc.', '提供基因检测服务，覆盖生育健康、肿瘤和器官移植监测'),
 'NVDA': ('Nvidia Corporation', 'AI 加速计算平台，GPU、网络和 CUDA 生态共同支撑数据中心算力需求'),
 'OXY': ('Occidental Pete Corp', '西方石油，上游油气生产商，现金流高度受油价、资本开支和资产负债表约束影响'),
 'PDD': ('Pdd Holdings Inc', '拼多多和 Temu 背后的电商平台，核心变量是低价供给、流量效率和跨境扩张'),
 'RSP': ('Invesco S&P 500 Equal Weight ETF', '跟踪标普500等权重股票组合的交易所交易基金'),
 'SE': ('Sea Limited', '经营东南亚电商 Shopee、游戏 Garena 与数字金融服务'),
 'SPCX': ('Space Exploration Technologies', '航天发射与卫星互联网运营商，业务包含运载火箭与 Starlink'),
 'SPGI': ('S&P Global Inc', 'S&P Global，金融数据、评级、指数和市场情报公司，核心看信息收费和指数授权'),
 'STM': ('STMicroelectronics N.V.', '意法半导体，业务覆盖汽车、工业及其他嵌入式半导体'),
 'STX': ('Seagate Technology', '硬盘存储厂商，业务受云存储需求、近线硬盘容量和技术迭代影响'),
 'TBBB': ('BBB Foods Inc.', '在墨西哥经营硬折扣食品零售门店，关注门店扩张与周转效率'),
 'TEVA': ('Teva Pharmaceutical Inds Ltd', '梯瓦制药，仿制药和专科药公司，核心看债务去化、核心药物增长和诉讼风险'),
 'TME': ('Tencent Music Entmt Group', '腾讯音乐，中国在线音乐和音频娱乐平台，核心看订阅、社交娱乐和版权生态'),
 'TSLA': ('Tesla Inc', '特斯拉，电动车、储能和自动驾驶平台公司，核心变量是制造效率、FSD 与 Robotaxi 期权'),
 'TSM': ('Taiwan Semiconductor Mfg Ltd', '台积电，全球领先晶圆代工厂，是先进制程和先进封装产能的关键瓶颈'),
 'U': ('Unity Software', '实时三维开发工具与游戏广告平台，关注商业化和盈利转化'),
 'UBER': ('Uber Technologies, Inc.', '出行、外卖与物流平台，关注网络密度、抽成和经营现金流'),
 'UNH': ('Unitedhealth Group Inc', '联合健康，医保和医疗服务平台公司，核心看医疗成本率、政策风险和 Optum 服务能力'),
 'VST': ('Vistra Corp', 'Vistra，美国独立发电和零售电力公司，核心看电力价格、负荷增长和发电资产价值'),
 'WHR': ('Whirlpool Corporation', '家用电器制造商，经营受家居消费、产品组合和成本影响'),
 'WWD': ('Woodward, Inc.', '提供航空及工业能源控制系统，收入与装机需求和售后服务相关'),
 'XLF': ('Financial Select Sector SPDR Fund', '跟踪美国金融板块股票的交易所交易基金，不是单一公司'),
 'YPF': ('YPF S.A.', '阿根廷综合油气公司，业务包含油气勘探生产、炼化与销售')}
DESC.update({
 'CIEN':('Ciena Corporation','提供光网络和通信系统，关注云客户订单、网络升级及盈利'),
 'P':('Pure Storage','提供企业级数据存储系统与订阅服务，关注客户支出和现金流'),
 'ALAB':('Astera Labs','提供数据中心连接芯片与平台，关注客户导入、带宽需求和收入兑现'),
 'COHR':('Coherent Corp.','提供光学材料、激光与通信器件，关注数据中心光连接及工业需求'),
 'LITE':('Lumentum','提供光通信与激光器件，关注云网络升级和产品组合'),
 'ECHO':('EchoStar','经营卫星、通信和无线相关业务，关注资产配置、融资及经营变化'),
 'CBRS':('Cerebras Systems','提供大规模AI计算芯片、系统和云服务，上市股份来源须另核'),
 'PANW':('Palo Alto Networks','提供网络与云安全平台，关注订阅、平台整合和现金流'),
 'FIG':('Figma','提供协作设计软件，关注客户扩张、付费转化和盈利能力'),
 'NBIS':('Nebius','提供AI基础设施与计算服务，关注融资、产能及客户订单兑现'),
 'GEV':('GE Vernova','提供发电与电网设备服务，关注订单、交付和长期服务收入'),
 'CEG':('Constellation Energy','经营发电及能源服务，关注电价、用电需求和长期合同'),
 'AVGO':('Broadcom','经营半导体与基础设施软件，关注定制芯片、网络及软件现金流'),
 'LRCX':('Lam Research','提供半导体制造设备与服务，关注存储和先进制程资本开支'),
 'AMAT':('Applied Materials','提供半导体材料工程设备及服务，关注客户资本开支和产品份额'),
 'ETN':('Eaton','提供电力管理设备与系统，关注电气化、数据中心及工业需求'),
 'SNOW':('Snowflake','提供云数据平台，关注消费增长、AI产品与自由现金流'),
 'CRWV':('CoreWeave','提供GPU云计算基础设施，关注客户集中度、交付和融资负担'),
 'CFLT':('Confluent','提供数据流平台，关注企业用量、云业务与经营现金流'),
 'ARM':('Arm Holdings','授权处理器架构与芯片设计，关注版税、产品结构及终端需求'),
 'AXON':('Axon Enterprise','提供公共安全设备与软件，关注订阅服务、合同和交付'),
 'SMH':('VanEck Semiconductor ETF','跟踪半导体股票的交易所交易基金，期权与ETF份额分开解释'),
 'WAT':('Waters','提供分析仪器与实验室技术，关注客户科研支出和耗材服务'),
 'SYK':('Stryker','提供医疗器械与骨科产品，关注手术量、创新及利润率'),
 'IDXX':('IDEXX Laboratories','提供动物诊断产品与服务，关注宠物医疗需求和检测试剂收入'),
 'V':('Visa','经营支付网络，关注交易量、跨境业务和监管成本'),
 'MAR':('Marriott International','经营酒店管理与特许加盟，关注客房需求、收费和扩张'),
 'ADP':('Automatic Data Processing','提供薪资与人力资源服务，关注就业、客户留存和利润率'),
 'PM':('Philip Morris International','经营烟草和无烟产品，关注产品迁移、定价及现金回报'),
 'MA':('Mastercard','经营支付网络与增值服务，关注跨境支付、交易量和估值'),
 'CHD':('Church & Dwight','经营家庭及个人护理消费品牌，关注渠道、定价和成本'),
 'PG':('Procter & Gamble','经营日用消费品牌，关注销量、定价、产品组合和资本回报'),
 'VEEV':('Veeva Systems','提供生命科学行业软件，关注客户迁移、订阅增长和产品扩张'),
 'FTNT':('Fortinet','提供网络安全产品与服务，关注设备更新、订阅和竞争'),
 'YUM':('Yum! Brands','经营餐饮品牌及加盟体系，关注同店销售、开店和加盟商回报'),
 'BN':('Brookfield Corporation','配置资产管理、保险及经营资产，关注资本回报和估值'),
 'QSR':('Restaurant Brands International','经营连锁餐饮品牌与加盟体系，关注门店增长和经营改善'),
 'HHH':('Howard Hughes Holdings','持有社区开发及经营资产，关注资产价值、现金流与资本配置'),
 'HLT':('Hilton','经营酒店管理与特许加盟，关注客房需求、收费和新店拓展'),
 'SEG':('Seaport Entertainment Group','经营地产与娱乐相关资产，关注资产经营、负债及资本需求'),
 'HTZ':('Hertz Global Holdings','经营汽车租赁，关注租金、车辆残值、车队成本和债务'),
 'PS':('Pershing Square Inc.','上市投资管理公司；本项为关联管理公司股份，不等于PSH基金资产'),
 'NFLX':('Netflix','提供流媒体内容和广告服务，关注订阅、内容投入和现金流'),
})

DESC.update({
 'KKR':('KKR & Co.','另类资产管理与保险集团，关注募资、管理费、投资兑现和资本回报'),
 'CSGP':('CoStar Group','房地产数据与在线市场平台，关注订阅及门户投入的回报'),
 'ORLY':("O’Reilly Automotive",'汽车零部件零售商，关注同店增长、专业客户和库存周转'),
 'ROP':('Roper Technologies','经营专业软件与技术业务，关注经常性收入和收购回报'),
 'ABNB':('Airbnb','住宿预订平台，关注供需、客单价、监管和现金流'),
 'FICO':('Fair Isaac','提供信用评分和决策软件，关注定价、客户采用与资本回报'),
 'CPRT':('Copart','运营事故车拍卖平台，关注车辆供给、场地网络和成交收费'),
 'CCC':('CCC Intelligent Solutions','提供财险与汽车理赔软件，关注保险公司采用和订阅续约'),
 'ASML':('ASML Holding','提供光刻系统与服务，关注先进制程资本开支和交付'),
 'DHR':('Danaher','生命科学与诊断企业，关注仪器、耗材及客户研发支出'),
 'AER':('AerCap Holdings','经营飞机租赁，关注租赁现金流、机队价值和融资成本'),
 'BKNG':('Booking Holdings','在线旅游预订集团，关注间夜增长、营销效率和现金流'),
 'RPRX':('Royalty Pharma','投资药品特许权收入，关注药品销售、专利期限和收购回报'),
 'LYV':('Live Nation Entertainment','经营演唱会、票务和场馆，关注活动需求、票务收费和监管'),
 'AZO':('AutoZone','汽车零部件零售商，关注同店增长、商业客户和资本回报'),
 'ENOV':('Enovis','提供骨科与康复医疗技术，关注手术量、产品创新和整合'),
 'SUNB':('Sunbelt Rentals Holdings','设备租赁企业，关注租赁需求、利用率和车队资本开支'),
 'APP':('AppLovin','广告技术平台，关注广告转化、客户留存与自由现金流'),
 'TYL':('Tyler Technologies','提供公共部门软件，关注云迁移、实施和长期续约'),
 'FLUT':('Flutter Entertainment','经营体育博彩和线上娱乐，关注客户获取、监管和利润率'),
 'ALC':('Alcon','眼科设备与耗材企业，关注手术需求、隐形眼镜和产品创新'),
 'RACE':('Ferrari','豪华汽车制造商，关注订单、定价、产品组合和资本回报'),
 'GE':('GE Aerospace','航空发动机与服务企业，关注飞行小时、售后收入和交付'),
 'ADI':('Analog Devices','模拟与混合信号芯片企业，关注工业、汽车周期和库存'),
 'ICE':('Intercontinental Exchange','经营交易所、金融数据和抵押贷款技术，关注交易及订阅收费'),
 'CSCO':('Cisco Systems','企业网络设备与安全软件企业，关注订单、订阅和客户预算'),
 'CP':('Canadian Pacific Kansas City','经营北美铁路，关注运量、定价、运营效率和资本开支'),
 'APD':('Air Products and Chemicals','工业气体企业，关注长期合同、能源成本及项目回报'),
 'AME':('AMETEK','提供电子仪器与机电设备，关注专业市场定价和收购回报'),
 'HEI-A':('HEICO Class A','航空零部件与电子技术企业A类股，关注售后需求和并购回报'),
 'HEI.A':('HEICO Class A','航空零部件与电子技术企业A类股，关注售后需求和并购回报'),
 'SCHW':('Charles Schwab','证券经纪与财富平台，关注客户资产、现金分流和净息差'),
 'MEDP':('Medpace Holdings','临床研究外包企业，关注订单、试验项目和生物医药融资'),
 'IBP':('Installed Building Products','建筑保温等安装服务商，关注住宅建设和施工效率'),
 'PGR':('Progressive','财产险企业，关注承保定价、赔付率和投资收益'),
 'FIVE':('Five Below','折扣零售商，关注门店扩张、同店需求和库存'),
 'COF':('Capital One Financial','消费金融与银行企业，关注信用损失、存款和资本回报'),
 'CRM':('Salesforce','企业客户关系与业务软件平台，关注续约、产品增购和现金流'),
 'IQV':('IQVIA','医疗数据与临床研究服务企业，关注订单、项目转化和研发支出'),
 'KDP':('Keurig Dr Pepper','饮料与咖啡系统企业，关注销量、品牌定价和资本配置'),
 'WBD':('Warner Bros. Discovery','媒体与娱乐企业，关注流媒体、内容价值和债务'),
 'COP':('ConocoPhillips','油气勘探生产企业，关注油气价格、产量和资本纪律'),
 'TRGP':('Targa Resources','天然气中游企业，关注处理运输量、项目和负债'),
 'FCNCA':('First Citizens BancShares','银行控股公司，关注存贷款、信用损失和整合'),
 'ELV':('Elevance Health','医疗保险与健康服务企业，关注医疗成本率和会员结构'),
 'MRSH':('Marsh & McLennan','保险经纪与咨询集团，关注续约、收费、整合和现金流'),
 'NYT':('The New York Times Company','新闻与数字订阅企业，关注组合订阅、留存和每用户收入'),
 'MSA':('MSA Safety','安全设备企业，关注替换需求、客户认证和定价'),
 'TEL':('TE Connectivity','连接器与传感器企业，关注数据连接及汽车、工业需求'),
 'C':('Citigroup','全球银行集团，关注重组、信用成本和资本回报'),
 'RKT':('Rocket Companies','抵押贷款与住房服务平台，关注贷款周期和收购整合'),
 'TDG':('TransDigm Group','航空零部件企业，关注售后定价、杠杆和并购回报'),
 'ROL':('Rollins','害虫防治服务企业，关注客户续约、网点密度和并购回报'),
 'WMB':('The Williams Companies','天然气管道与中游企业，关注合同覆盖和项目回报'),
 'SLB':('SLB','油气技术与服务企业，关注国际订单、客户投入和周期'),
 'EFX':('Equifax','信用与人力数据企业，关注金融活动、数据产品和技术投入'),
})

RADAR={
'berkshire':[
'AAPL、AXP、KO、Alphabet A/C 等核心持仓股数不变；AAPL 权重上升不能记成主动加仓。GOOG/GOOGL 在下表按证券类别分别列示，跨机构比较时合并为 Alphabet。',
'LEN A 类股增加 98.56%，B 类增加 85.50%；DAL 增加 12.44%。新列示 Bending Spoons 20,689,655 股，季末权重 0.23%；这是 7 月 IPO 相关持仓，10 月追加投资属于 Q4，不能计入本季。',
'BAC 减股 5.70%、VRSN 减股 34.12%、COF 减股 61.67%；本季没有完全退出的既有证券。不能把机构交易一概归因于巴菲特个人。'],
'himalaya':[
'PDD 增股 9.29%，TME 增股 124.93%；其余六个证券类别股数不变，组合仍为八个证券类别。',
'Alphabet A/C 分别列示，但属于同一家公司的两类股票；不得把它们当作两个独立行业观点。PDD 的增股与 H&H 同向，TME 则是这五家样本中 Himalaya 的独立增量。'],
'hh':[
'PDD 增股 11.86%、TSLA 增股 20.70%；NVDA 减股 63.07%、GOOG 减股 41.50%。方向以股数为准，不能只凭苹果或伯克希尔的权重变化推断买卖。',
'SpaceX 本季首次列示，权重约 0.18%，仅属于这一申报主体的可见切片；不能推成段永平个人完整资产组合或买入理由。'],
'duquesne':[
'STX 正股增股 180.16%，同时新增 STX CALL；二者分开列示，期权申报值不是支付的权利金。U 增股 435.53%，AMZN 增股 42.65%，SE 增股 44.81%，FOXA 增股 38.17%。',
'TSM 减股 94.45%、STM 减股 47.94%；AMD、ARM、LRCX 在本期表中不再列示。新列示 NEM、B、AEM 等黄金股票与 SGI，完整小仓见趋势页。',
'这组变化更适合观察存储、软件和黄金等资产方向的轮动，不能按长期集中型机构的方式照抄每个证券。LRCX 的退出与 Appaloosa 的加仓构成样本内分歧。'],
'appaloosa':[
'MU 增股 28.21%、NVDA 增股 31.15%、LRCX 增股 63.40%、ASML 增股 30.00%；SpaceX 增股 1,625.92%，升至第四大申报仓位。',
'新列示 ORCL（2.28%）、AMAT（1.52%）、MOD（0.70%）、PCG（0.41%）；AMZN、META、GOOG 减股，AMD、AVGO、QCOM 本期不再列示。',
'半导体与算力承接层仍有买入，但互联网平台同时被减仓。NVDA 与 H&H、LRCX 与 Duquesne、AMZN 与 Duquesne 的动作相反，应读作机构分歧。',
'SpaceX 同 CUSIP 申报隐含价与其他机构存在差异，保留本机构原值；股数增长不全部认定为二级市场买入。其申报值的机械分解也不能当作可比的市场价格收益。'],
}

# Reviewed company/ETF business descriptions shared with batch propagation.
_business_catalog = Path(__file__).resolve().parent/'data/13f-2026q3-propagation.json'
if _business_catalog.exists():
    for _ticker, _business in json.loads(_business_catalog.read_text()).get('business', {}).items():
        DESC.setdefault(_ticker, tuple(_business))


def read(k):
    path=SNAPSHOT_PATHS.get(k,SNAPSHOT_DIR/f'{k}.json')
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('latest_quarter')!='2026Q3':
        raise ValueError(f'This renderer replays 2026Q3 evidence only: {path}')
    return data,g.resolve_filings(data)


def configure_manifest(path, vault):
    """Select explicit frozen inputs; never discover a later snapshot implicitly."""
    manifest=json.loads(Path(path).read_text(encoding='utf-8'))
    if manifest.get('quarter')!='2026Q3':
        raise ValueError('Batch manifest must describe 2026Q3')
    paths={}
    for batch in manifest['batches']:
        directory=Path(batch['snapshot_dir'])
        directory=directory if directory.is_absolute() else Path(vault)/directory
        for key in batch['institutions']:
            if key not in META or key in paths:
                raise ValueError(f'Unknown or duplicate institution: {key}')
            paths[key]=directory/f'{key}.json'
    institutions=tuple(manifest['institution_keys'])
    horizontal=tuple(manifest['horizontal_keys'])
    if len(set(institutions))!=len(institutions) or len(set(horizontal))!=len(horizontal):
        raise ValueError('Duplicate renderer institution keys')
    if not set(institutions)<=set(paths) or not set(horizontal)<=set(paths):
        raise ValueError('Manifest renderer key lacks a frozen snapshot')
    return paths,institutions,horizontal


def ticker(d,r): return g.security(d,r).get('ticker') or r['cusip']
def money(v): return f'${v/1e9:,.3f}bn' if abs(v)>=1e9 else f'${v/1e6:,.2f}m'
def signed(v): return ('+' if v>=0 else '−')+money(abs(v))
def pp(v): return f'{v:+.2f}pct'
def index(f): return f['url'].rsplit('/',1)[0]+'/'+f['accessionNumber']+'-index.htm'
def link(f): return f"[SEC {f['form']} · {f['reportDate']} · {f['filingDate']}]({index(f)})"
def pct(x): return f'{x:+.2%}'
ETF_ISSUER_RE=re.compile(r'\b(?:ETF|ETP|ISHARES|SPDR|INVESCO|VANECK|PROSHARES|DIREXION|KRANESHARES|VANGUARD|WISDOMTREE)\b|\bEXCHANGE[\s-]+TRADED\b',re.I)

def instrument_type(row):
    """Describe the listed instrument without treating all foreign shares as ADRs."""
    cls=row['security_class'].upper()
    if row.get('share_type')=='PRN' or re.search(r'\b(?:NOTE|BOND)\b',cls):
        return '票据/债券'
    if re.search(r'\b(?:PREFERRED|PREF|PFD)\b',cls):
        return '优先股'
    if re.search(r'\b(?:WARRANT|WARRANTS|WEXP)\b|\bW\s+EXP\b',cls):
        return '权证'
    if ETF_ISSUER_RE.search(row['issuer']) or re.search(r'\bETF\b|EXCHANGE[\s-]+TRADED',cls):
        return 'ETF'
    if re.search(r'\b(?:ADR|ADS)\b|\bAMERICAN DEPOSIT|DEPOSITORY RECEIPT',cls):
        return 'ADR/ADS'
    if re.search(r'\b(?:N\s*Y|NEW YORK)\s+REGISTRY\b',cls):
        return '纽约登记股'
    return '普通股'

def intro(d,r):
    t=ticker(d,r); n=g.security(d,r).get('name') or r['issuer']
    if t in DESC: n,des=DESC[t]
    else: des=g.security(d,r).get('description') or '证券与业务范围以申报发行人和对应公司资料为准'
    kind=instrument_type(r)
    tag=f' [{kind}]' if kind!='普通股' else ''
    return f'`{t}`{tag} {n}（{des}）'+(f" **{r['put_call']}**" if r['put_call'] else '')

def update_institution(k):
    d,qs=read(k); meta=META[k]; curr,prev=qs[-1],qs[-2]
    assert curr['date']=='2026-09-30' and prev['date']=='2026-06-30'
    active,price=g.attribution(d,prev,curr)
    optactive,optprice=g.attribution(d,prev,curr,True)
    ordinary=lambda q:sum(r['value'] for r in q['rows'].values() if not r['put_call'])
    nopt=sum(bool(r['put_call']) for r in curr['rows'].values())
    ordinary_total=ordinary(curr)
    ordinary_top=sorted((r for r in curr['rows'].values() if not r['put_call']),key=lambda r:-r['value'])
    top5=sum(r['value'] for r in ordinary_top[:5])/ordinary_total if ordinary_total else 0
    top10=sum(r['value'] for r in ordinary_top[:10])/ordinary_total if ordinary_total else 0
    lines=['## 13F 持仓（近四个季度）','','### 怎么看这组披露','',
    '13F 是季末公开证券多头及部分期权的滞后披露，不是完整资产组合。以下按 CUSIP、证券类别和 PUT/CALL 聚合重复管理人记录；期权与正股不混算。市值和权重变化不能替代股数变化。', '',
    '### 13F 趋势雷达（最近一季横向）','',
    f"最近一季：`2026Q3` vs `2026Q2`；报告日 `2026-09-30`；申报日 `{curr['filings'][-1]['filingDate']}`；核验 `{DATE}`。",'',
    f"- 申报证券行和从 `{money(prev['total'])}` 变为 `{money(curr['total'])}`（`{pct(curr['total']/prev['total']-1)}`）；聚合后 `{len(curr['rows'])}` 个证券类别，其中期权 `{nopt}` 个。非期权证券前五占其切片 `{top5:.2%}`、前十占 `{top10:.2%}`。",
    f"- 非期权证券切片申报值 `{money(ordinary(prev))}` → `{money(ordinary_total)}`；按上季隐含价格估算的股数项 `{signed(active)}`，价格项 `{signed(price)}`。这是两期持仓的机械分解，不是现金流、真实成交额或投资收益；首次上市、估值口径不同的证券另见趋势页边界。"]
    if k not in FIRST_KEYS:
        breakdown=g.attribution_breakdown(d,prev,curr)
        if breakdown['unattributed']:
            lines.append(f"- 不可比分解余项 `{signed(breakdown['unattributed'])}` 保留在申报总值中，不分配为主动交易或市场价格收益；逐项原因见单机构趋势页。")
    if k=='atreides':
        lines.append('- 申报总值包含较大的期权底层证券名义值；以下前十大使用非期权切片及其分母，不能用总申报值推导实际资金投入或净杠杆。')
    if k=='pershing':
        ps='71531U102'
        auxiliary=lambda q:sum(r['value'] for r in q['rows'].values() if not r['put_call'] and r['cusip']!=ps)
        lines.append(f"- 排除 PS 发行人股份的辅助切片：`{money(auxiliary(prev))}` → `{money(auxiliary(curr))}`（`{pct(auxiliary(curr)/auxiliary(prev)-1)}`）。原申报总额照列；此辅助切片不是 PSH 基金 NAV，也不是官方 AUM。")
    if nopt or optactive or optprice:
        lines.append(f'- 期权切片另计：申报值变化的主动项 `{signed(optactive)}`、价格项 `{signed(optprice)}`；缺少期限、执行价、权利金及其他组合腿，不能推导净风险。')
    rounding=curr['filings'][-1].get('cover_difference',0)
    if rounding:
        cover=curr['filings'][-1].get('reported_total',curr['total']-rounding)
        lines.append(f"- 最新封面申报总值 `${cover:,.0f}`，信息表行和 `${curr['total']:,.0f}`，行和减封面的差额为 `${rounding:,.0f}`；本页权重采用行和。差额不自动归因于某项证券，也不补造修正金额。")
    if k=='hh': lines.append('- H&H 是段永平相关的美国申报主体；以下不能代表其个人全部投资。')
    lines += ['- '+s for s in RADAR.get(k,d.get('editorial',{}).get('notes',[]))]
    if k not in FIRST_KEYS:
        lines += ['- '+d['editorial']['summary']]
    cross_label=f'Q3 {len(CROSS_KEYS)} 家样本'
    lines += [f"- 长历史与全部在持证券：[[institutions/13F趋势-{meta['title']}]]；横向页：[[institutions/13F趋势-2026Q3|{cross_label}]]。",'',
    '### 近四个已披露季度前 10 大持仓','']
    for q in reversed(qs[-4:]):
        year=q['date'][:4]; qu=g.quarter(q['date'])[-1]
        lines += [f'#### Q{qu} {year}','',f"申报总值 `{money(q['total'])}`；聚合后 `{len(q['rows'])}` 个证券类别。",'', '| 证券及业务 | 股数／底层份额 | 季末申报市值 | 13F 占比 |','|---|---:|---:|---:|']
        denominator=ordinary(q) if k=='atreides' else q['total']
        rows=sorted((r for r in q['rows'].values() if k!='atreides' or not r['put_call']),key=lambda r:-r['value'])[:10]
        if k=='atreides':
            lines[-2]='| 证券及业务（非期权） | 股数／底层份额 | 季末申报市值 | 非期权切片占比 |'
            lines.insert(-2,f'非期权证券切片 `{money(denominator)}`；期权完整名单与申报名义值另见趋势页。\n')
        for r in rows:
            lines.append(f"| {intro(d,r)} | {r['shares']:,} | {money(r['value'])} | {r['value']/denominator:.2%} |")
        lines.append('')
    lines += ['### 这四季的变化小结','',{
      'berkshire':'2025Q4—2026Q3 的核心大仓仍高度集中；2026Q2 已纳入两类 Alphabet 股票，Q3 股数保持不变。Q3 的新证据是住房、航空的增股与 Bending Spoons 首次披露，同时银行和部分金融证券减股。两季信息分别保留，不能把 Q2 已有仓位写成本季新买。',
      'himalaya':'2025Q4—2026Q1 仍有较多金融和能源证券；Q2 收缩为八个类别并大增 PDD、BRK.B，Q3 再增 PDD 和 TME。最新变化是集中组合内部继续调配，不能把未变股数的 Alphabet 权重移动写成交易。',
      'hh':'四季内 PDD 与 TSLA 的配置变化值得单独跟踪；Q2、Q3 的 NVDA 和 GOOG 减股也应连续观察。苹果和伯克希尔的大权重是组合结构事实，与当季是否增股是两个问题。',
      'duquesne':'四季轨迹显示持续轮动，Q3 的存储、软件、平台和黄金增量与部分芯片证券减仓并存。正股、CALL、PUT 各自沿同一类别追踪，不以期权名义申报值代替净多空判断。',
      'appaloosa':'四季应同时看半导体链、中国互联网、美国平台与首次上市证券。Q3 加仓存储和设备，同时减持部分平台，不能压成“全面看多科技”这一句话；持仓变化也不直接证明管理人的买入动机。',
    }.get(k,d.get('editorial',{}).get('method','')), '', '### 数据来源','']
    for q in reversed(qs[-4:]):
        for f in q['filings']: lines.append('- '+link(f))
    lines += [f"- [[raw/SEC｜{meta['title']}：2022Q4至2026Q3持仓轨迹]]；[[sources/{g.audit_name(d)}]]。",'']
    p=VAULT/f"wiki/institutions/{meta['name']}.md"
    text=p.read_text()
    text=re.sub(r'## 13F 持仓.*?(?=## 机构传承)', '\n'.join(lines)+'\n', text, flags=re.S)
    text=re.sub(r'^updated: .*$',f'updated: {DATE}',text,count=1,flags=re.M)
    count={'berkshire':7,'himalaya':5,'hh':4,'duquesne':4,'appaloosa':12}.get(k,2)
    text=re.sub(r'^source_count: (\d+)$',lambda m:f'source_count: {max(int(m[1]),count)}',text,count=1,flags=re.M)
    if k=='duquesne':
        text=re.sub(r'从公开 13F 看[^\n]*',f"从公开 13F 看，2026Q3 聚合后披露 {len(curr['rows'])} 个证券类别，申报总值约 {money(curr['total'])}；这只是公开证券切片，不等于家族办公室完整资产。{link(curr['filings'][-1])}",text,count=1)
    p.write_text(text)
    print('institution',k,len(curr['rows']),money(curr['total']),signed(active),signed(price))

def family(d,r):
    t=ticker(d,r)
    if r['cusip']=='T19377109': return 'Bending Spoons'
    if t in ('GOOG','GOOGL'): return 'GOOG/GOOGL'
    if t in ('BRK.A','BRK.B','BRK-A','BRK-B'): return 'BRK.A/B'
    if t in ('LEN','LEN.B','LEN-B','LEN/B'): return 'LEN A/B'
    return t

def category(r,t,data=None):
    if r['put_call']: return '期权'
    if r.get('value_reliable') is False: return '金额异常'
    if t in ('SPCX','Bending Spoons','PS','CBRS') or r['cusip'] in ('84615Q103','T19377109','71531U102'): return '特殊披露'
    if instrument_type(r)=='权证': return '权证'
    if instrument_type(r)=='ETF': return 'ETF'
    if data is not None and not g.comparable(data,r): return '不可比证券'
    return '普通股票'

def cross_data():
    out={}; sources=[]
    for k in CROSS_KEYS:
        m=META[k]
        d,qs=read(k); p,c=qs[-2:]; sources.append((k,d,p,c))
        families=[]
        unreliable={r['cusip'] for q in (p,c) for r in q['rows'].values() if r.get('value_reliable') is False}
        for q in (p,c):
            fq=collections.defaultdict(lambda:{'value':0,'rows':[]})
            for key,r in q['rows'].items():
                kind=category(r,ticker(d,r),d)
                if r['cusip'] in unreliable and not r['put_call']: kind='金额异常'
                ident=(family(d,r),kind,r['put_call'])
                fq[ident]['value']+=r['value'];fq[ident]['rows'].append((key,r))
            families.append(fq)
        fp,fc=families
        eligible_top=lambda q:sorted((x for x in q if k!='atreides' or x[1]!='期权'),key=lambda x:q[x]['value'],reverse=True)[:10]
        top0=set(eligible_top(fp));top1=set(eligible_top(fc))
        for f in sorted(set(fp)|set(fc)):
            a,b=fp.get(f,{}),fc.get(f,{})
            keys=set(x[0] for x in a.get('rows',[]))|set(x[0] for x in b.get('rows',[]))
            active=0
            for key in sorted(keys):
                old,new=p['rows'].get(key),c['rows'].get(key)
                if g.uncertain_action(d,p,c,key):
                    continue
                if f[1] in ('特殊披露','不可比证券','金额异常'):
                    continue
                if any(r is not None and r.get('value_reliable') is False for r in (old,new)):
                    continue
                if not old: active+=new['value']
                elif not new: active-=old['value']
                else:
                    q0=old['shares']*g.split_factor(d,old,p['date'],c['date'])
                    active+=(new['shares']-q0)*old['value']/q0 if q0 else new['value']-old['value']
            denominator=lambda q:sum(r['value'] for r in q['rows'].values() if not r['put_call']) if k=='atreides' and f[1]!='期权' else q['total']
            w0=a.get('value',0)/denominator(p)*100;w1=b.get('value',0)/denominator(c)*100
            entry=f in top1 and f not in top0;exit=f in top0 and f not in top1
            buy=(3+2*entry+(w1-w0>=.3))*WEIGHTS[k] if active>1e-6 else 0
            sell=(3+2*exit+(w1-w0<=-.3))*WEIGHTS[k] if active< -1e-6 else 0
            r=(b or a)['rows'][0][1]
            if f not in out: out[f]={'ticker':f[0],'category':f[1],'instrument':instrument_type(r),'put_call':f[2],'buy':0,'sell':0,'active':0,'managers':[],'name':g.security(d,r).get('name') or r['issuer']}
            dest=out[f];dest['buy']+=buy;dest['sell']+=sell;dest['active']+=active
            dest['managers'].append({'key':k,'title':m['title'],'active':active,'w0':w0,'w1':w1,'entry':entry,'exit':exit,'buy':buy,'sell':sell,'old':a,'new':b,'data':d})
    for x in out.values():
        x['net']=x['buy']-x['sell'];x['buyers']=[m for m in x['managers'] if m['active']>1e-6];x['sellers']=[m for m in x['managers'] if m['active']< -1e-6]
    return list(out.values()),sources

def side(ms):
    return '；'.join(f"{m['title']}（{signed(m['active'])}；{pp(m['w1']-m['w0'])}）" for m in ms) or '—'

def quote_citation(quote, label):
    """A tool label is provenance, not a URL; latest trades are not daily closes."""
    source=quote.get('source','来源未标注')
    reference=f'[{label}]({source})' if re.match(r'^https?://',source) else f'{label}；{source}'
    date=quote.get('price_date','N/A')
    if quote.get('price_basis')=='latest_trade':
        timestamp=quote.get('price_timestamp_utc')
        session='最新成交，时段待核'
        if timestamp:
            local=datetime.fromisoformat(timestamp.replace('Z','+00:00')).astimezone(ZoneInfo('America/New_York'))
            minutes=local.hour*60+local.minute
            session='盘后最新成交' if minutes>=960 else '盘前最新成交' if minutes<570 else '盘中最新成交'
        return f'{reference}（纽约 {date}；UTC {timestamp or "N/A"}；{session}）'
    return f'{reference}（纽约 {date} 常规收盘）'

def quote_note(x):
    values=[]
    for m in x['buyers']:
        d=m['data']
        for _,r in m['new'].get('rows',[]):
            t=ticker(d,r);q=d.get('quotes',{}).get(t,{})
            if q.get('price') is None: continue
            if x['category']!='普通股票': continue
            if not g.comparable(d,r): continue
            _,_,move,verdict=g.price_cells(d,r,'2026-09-30')
            if move=='N/A': continue
            v=quote_citation(q,f'{t} {move}')+f'；{verdict}'
            if v not in values: values.append(v)
    return '；'.join(values) if values else 'N/A：未取得可比报价'

def market_table(items,limit=12,score=True):
    lines=['| 标的 | 主动增加侧（估算额；权重变化） | 主动减少侧（估算额；权重变化） | 净主动变化 | 买入分 / 卖出分 / 净分 |','|---|---|---|---:|---:|']
    for x in items[:limit]:
        lab=x['ticker']+((' '+x['put_call']) if x['put_call'] else '')
        tag=f" [{x['instrument']}]" if x['instrument']!='普通股' else ''
        lines.append(f"| `{lab}`{tag} {x['name']} | {side(x['buyers'])} | {side(x['sellers'])} | {signed(x['active'])} | {x['buy']:.1f} / {x['sell']:.1f} / {x['net']:+.1f} |")
    return lines+['']

def update_cross():
    allrows,sources=cross_data();normal=[x for x in allrows if x['category']=='普通股票']
    expanded=len(CROSS_KEYS)>5
    sample=f'{len(CROSS_KEYS)} 家样本'
    coverage='、'.join(META[k]['title'] for k in CROSS_KEYS)
    buys=sorted([x for x in normal if x['net']>1e-6],key=lambda x:(-x['net'],-len(x['buyers']),-abs(x['active'])))
    sells=sorted([x for x in normal if x['net']< -1e-6],key=lambda x:(x['net'],-len(x['sellers']),-abs(x['active'])))
    disagree=sorted([x for x in normal if x['buyers'] and x['sellers']],key=lambda x:(-min(x['buy'],x['sell']),-len(x['buyers'])-len(x['sellers'])))
    lines=['---','type: institution-13f-trend','status: active',f'updated: {DATE}','quarter: 2026Q3','---','',f'# 13F 趋势 · 2026Q3（{sample}）','',
    f'本页覆盖 {coverage}。报告日均为 `2026-09-30`，核验日期 `2026-11-17`；比较基期为 `2026-06-30`。其他机构未纳入本页，不能据此称全体“大师”或市场达成共识，也不能把本页名次与 Q2 的 22 家样本直接比较。','',
    '## 覆盖口径','',
    '| 机构 | Q3 申报日 | Q2 申报行和 | Q3 申报行和 | Q3 聚合证券数（含期权） | 风格权重 |','|---|---|---:|---:|---:|---:|']
    for k,d,p,c in sources:
        lines.append(f"| [[institutions/13F趋势-{META[k]['title']}|{META[k]['title']}]] | {c['filings'][-1]['filingDate']} | {money(p['total'])} | {money(c['total'])} | {len(c['rows'])} | {WEIGHTS[k]:.1f} |")
    if expanded:
        directories=list(dict.fromkeys(str(SNAPSHOT_PATHS.get(k,SNAPSHOT_DIR/f'{k}.json').parent.relative_to(VAULT)) for k in CROSS_KEYS))
        lines += ['','各批独立证据目录：'+'、'.join(f'`{p}`' for p in directories)+'。本页扩充样本并重算，不改写既有原始证据。','',
                  '### 申报总额与辅助切片','',
                  '| 机构与口径 | Q2 | Q3 | 解释 |','|---|---:|---:|---|']
        for k,d,p,c in sources:
            if k=='atreides':
                a,b=g.ordinary_slice(p),g.ordinary_slice(c)
                lines.append(f"| Atreides 非期权证券 | {money(a['total'])} | {money(b['total'])} | 期权底层名义值仍计入上方总额；本机构普通证券权重与前十用本切片分母 |")
            if k=='pershing':
                auxiliary=lambda q:sum(r['value'] for r in q['rows'].values() if not r['put_call'] and r['cusip']!='71531U102')
                lines.append(f"| Pershing 排除 PS 发行人股份 | {money(auxiliary(p))} | {money(auxiliary(c))} | 辅助证券切片，不是 PSH NAV 或官方 AUM；正式权重仍使用全报告分母 |")
            if k=='tudor':
                a,b=g.ordinary_slice(p),g.ordinary_slice(c)
                lines.append(f"| Tudor 非期权证券 | {money(a['total'])} | {money(b['total'])} | 辅助集中度单列；正式前十及横向权重仍以全报告为分母，期权名义值不当资金投入 |")
        lines += ['','Pershing Q2已合并11月16日的 **NEW HOLDINGS** 补充申报；仅补PS发行人股份，不能用这一行替换原季持仓。Altimeter的Grab权证保留原始份额及申报额，作为权证单列，不与GRAB正股比价或进入普通股票榜；封面与信息表行和差额独立保留。']
        if 'oakmark' in CROSS_KEYS:
            lines += ['Oakmark使用Harris Associates全部申报范围，不等同某只Oakmark基金或某一经理的个人组合。']
        for k,d,p,c in sources:
            if k not in FIRST_KEYS and c['filings'][-1].get('cover_difference'):
                f=c['filings'][-1]
                lines.append(f"{META[k]['title']} Q3封面申报总值 `${f['reported_total']:,.0f}`，信息表行和 `${c['total']:,.0f}`，差额 `${f['cover_difference']:,.0f}`；不将其解释为取整或归给某一证券。")
    lines += ['','沿用 [[institutions/13F趋势|总入口]] 的主动额和评分结构：已有仓位按 `股数差 × 上季隐含价`，新列示按本季申报值，退出按上季申报值负数估算；先在机构内部净额，再做横向汇总。Berkshire=1.5、Himalaya/H&H=1.4、Duquesne=0.8；Appaloosa 本轮明确为 0.8，这是规则补记，不追称旧榜单已用此值。',
    '', '只在有主动增加/减少时给相应方向评分：基础 3 倍风格权重，主动进入/退出前十加 2 倍，权重同向变化至少 0.3pct 再加 1 倍。同公司类别先按证券身份比较，再合并公司级金额和权重；GOOG/GOOGL、BRK.A/B、LEN A/B 不当作互相独立的公司信号。ETF、期权和特殊披露不进入普通股票主榜。','',
    '普通股票榜保留 ADR/ADS，但加注存托凭证属性：如 PDD、TME、SE、TSM，申报份额不是可直接等同的当地普通股股数，需另核凭证比例、存托安排与公司注册地风险。ASML 单列“纽约登记股”，不是把所有境外公司一律称作 ADR；其 Nasdaq 证券为注册普通股，见 [ASML 官方股份说明](https://www.asml.com/en/investors/shares)。ETF 以完整名称 token 和申报类别识别，不用股票名称中的字母片段判断。','',
    '## 结论先行','',
    '- **PDD 保留两家长期集中型机构同向动作。** Himalaya 增股 9.29%，H&H 增股 11.86%；两家分别持有、分别决策，不能把它们并成一个买入理由。TME 的大比例增股来自 Himalaya 一家。',
    '- **半导体内部轮动大于行业一致加仓。** Appaloosa 增加 MU、NVDA、LRCX、ASML，Duquesne 减少 TSM、退出 AMD/ARM/LRCX，H&H 继续减 NVDA。相同产业标签不足以覆盖这些相反动作。',
    '- **平台也有分歧。** Duquesne 增加 AMZN、SE、U，Appaloosa 减少 AMZN、META、GOOG。Berkshire 的 AAPL、AXP、KO、Alphabet 股数不动，AAPL 权重提升属于价格/组合分母效应。',
    '- **新增小仓与特殊披露另看。** Berkshire 增加 LEN、DAL 并首次列示 Bending Spoons；Appaloosa 的 SpaceX 股数扩张幅度大，但申报估值与其他机构不同。不能把这些直接写成可复制的成交信号。','',
    '## 普通股票研究优先级','',
    '以下先展示按净分排序的研究入口，再看交易风格、分歧和披露后价格。净分不是胜率或收益预测，也不衡量资金净流；风格加权分数与估算主动金额可能方向相反。缺少可比行情时，不生成“当前可以买”结论。与前期相比，本页把价格导致的前十进入显式单列，不给主动买入分。','',
    '| 标的及证券属性 | 本样本净分 | 主动增加机构 | 13F 锚点后价格变化 | 下一步核验 |','|---|---:|---|---|---|']
    if expanded:
        method_index=lines.index('## 结论先行')
        added_weights='、'.join(f'{META[k]["title"]}={WEIGHTS[k]:.1f}' for k in CROSS_KEYS if k not in FIRST_KEYS)
        lines[method_index:method_index]=[f'后续批次风格权重：{added_weights}；首批五家的权重保持原值。Akre首次加入本季全榜采用1.4，仅为启发式，并非对历史榜单的追溯声明。PS关联管理公司持股、Cerebras、SpaceX、新上市且不可比的证券、Grab权证和期权均不进入普通股票主榜。','']
        conclusion_index=lines.index('## 普通股票研究优先级')
        lines[conclusion_index:conclusion_index]=[
            '- **扩充后的平台信号不是单向共识。** Coatue与Atreides增MSFT/META，Altimeter增META；Fundsmith和Pershing减MSFT/META。必须保留两侧行为与各自方法，不能用净额抹平分歧。',
            '- **质量研究也在换仓。** Fundsmith大增VEEV、YUM、NXT、TJX及支付网络；其2026半年信披露上半年换手51.8%，最新行为不能继续套用“几乎不动”。Pershing新列ALC与ICE并增NFLX，UBER仍是核心但没有主动增股。',
            '- **申报范围会改变观感。** Atreides的期权名义值、Altimeter的Grab权证及独立封面差额、Pershing的PS关联股份和Q2补充修订均单列；不能把申报总额增长直接叫作净买入或基金回报。','']
    if set(g.BATCH3_MANAGERS) <= set(CROSS_KEYS):
        conclusion_index=lines.index('## 普通股票研究优先级')
        lines[conclusion_index:conclusion_index]=[
            '- **Veeva增加了集中质量机构的证据。** Dorsey首次列示VEEV并成为第一大仓，Giverny亦增加股数，与Fundsmith的增股同向；三家方法与仓位起点不同，需分别验证。',
            '- **长期核心也在重新比较机会成本。** Akre退出ABNB、减少CSGP等核心，新列TDG/ROL小仓并增FICO；MA权重上升但股数减少。Giverny增NYT/MSA，减BRK.B/MKL；不能套用上季候选排序。',
            '- **SUNB与平台股保留买卖分歧。** AKO增SUNB，Dorsey不再列示；Dorsey与Harris增META，Giverny减META。Harris增加GOOG、减少GOOGL，Alphabet先合并类别再评分。',
            '- **第三批有三处关键口径。** AKO金额逐份标准化；Giverny Q2采用8月26日修订；Oakmark使用Harris Associates全部申报范围，不能当成单只基金或某位经理的个人组合。','']
    if set(g.BATCH4_MANAGERS) <= set(CROSS_KEYS):
        first=lines.index('## 结论先行'); last=lines.index('## 普通股票研究优先级')
        lines[first:last]=['## 结论先行','',
            '- **平台股两侧都更清楚。** Lone Pine新列AMZN、META，Third Point新列META却退出AMZN；Maverick增MSFT、META，Kensico增AMZN、MSFT，Fundsmith与Pershing减MSFT、META。净额不能代替各家的机会成本与原有仓位。',
            '- **半导体仍是公司选择，不能叫作一致增仓。** Maverick增NVDA、TSM，Lone Pine显著增加TSM并新列INTC；Kensico减TSM并退出INTC，H&H继续减NVDA。Maverick几乎退出ALAB，Atreides却增股。',
            '- **集中质量机构提供另一组证据。** Dorsey首次列示VEEV并成为第一大，Giverny与Fundsmith也增股；Akre退出ABNB、减少CSGP，但增FICO、试仓TDG/ROL。不能只用科技或价值标签归类。',
            '- **中国平台与长期成长之间存在分歧。** Himalaya与H&H同增PDD，Baillie却减PDD 56.28%。Baillie增ALNY和部分设备股；MRNA减股37.18%仍进入前十，属于价格和分母推升。',
            '- **价值与事件框架有具体替换。** Baupost增GPC、FERG、WCC、CME，新列SITE/HONA，AMZN股数不变；Greenlight增VGNT、PCG、DCH，新列CENX。分拆分派和证券转换必须先剔除，不能机械记作买卖。',
            '- **宏观工具单独读。** Tudor的QQQ PUT与CALL同时增加，SPY现货增加而IVV减少；两侧名义值不能相减为净delta。普通股研究榜排除ETF、期权、优先股和特殊披露。',
            '- **23家是固定研究样本。** 各家覆盖范围不同；Baupost逐份金额校准、Greenlight主体边界、Teva一比一证券转换及Tudor历史封面行数差均保留审计。Kensico=1.0为本季新增启发式。','']
    checks={}
    for _, data, _, _ in sources:
        checks.update(data.get('editorial',{}).get('next_checks',{}))
    candidates=set(checks)-{'SPCX','Bending Spoons','NEM','SGI'}
    research=sorted([x for x in normal if x['buyers'] and (x['ticker'] in candidates or x['ticker']=='LEN A/B')],key=lambda x:(-x['net'],-sum(m['entry'] for m in x['buyers']),-len(x['buyers']),x['ticker']))
    for x in research:
        t=x['ticker'];ch=checks.get(t,checks.get('LEN') if t=='LEN A/B' else '回到公司经营、估值与对应机构的持有约束')
        tag=f" [{x['instrument']}]" if x['instrument']!='普通股' else ''
        lines.append(f"| `{t}`{tag} | {x['net']:+.1f} | {', '.join(m['title'] for m in x['buyers'])} | {quote_note(x)} | {ch} |")
    lines += ['','## 资产线 / 趋势跟踪榜','','| 资产方向 | 本季可见动作 | 应继续核验 |','|---|---|---|',
    '| 中国消费与数字平台 | Himalaya、H&H 同增 PDD；Himalaya 增 TME | 商家投入、竞争、海外风险；音乐订阅、内容成本与回报 |',
    '| 存储与半导体设备 | Duquesne 增 STX；Appaloosa 增 MU/LRCX/ASML、新列 AMAT；Duquesne 退出 LRCX | 订单、供需、存储价格、产能与资本开支；保留机构分歧 |',
    '| 芯片与AI平台 | Appaloosa 增 NVDA，H&H 减 NVDA；Duquesne 与 Appaloosa 均不再列示 AMD | 具体公司需求、交付与估值，不用行业标签替代公司差异 |',
    '| 软件与云 | Duquesne 增 U/AMZN/SE；Appaloosa 新列 ORCL、减 AMZN | 订单转化、现金流、竞争及资本开支负担 |',
    '| 住宅与航空 | Berkshire 增 LEN A/B、DAL；Duquesne 退出 DAL，存在分歧 | 住房订单、融资补贴、土地回报；客运收益率与燃油成本 |',
    '| 黄金与消费整合 | Duquesne 新列 NEM/B/AEM、SGI 小仓 | 金价与全维持成本；整合与负债，不升级为长期投资承诺 |','',
    '## 首次披露或口径特殊的标的','',
    '| 标的 | 本季证据 | 解释边界 |','|---|---|---|',
    '| Bending Spoons | Berkshire 首次列示 20,689,655 股，权重约 0.23% | 7 月 IPO 相关持仓；10 月追加属于 Q4。不能拿申报日价格倒推机构买价 |',
    '| SPCX / SpaceX | Appaloosa 股数增加 1,625.92%，成为第四大申报仓位；H&H、Duquesne 首次列示，分别约 0.18%、0.68% | 同 CUSIP 的申报隐含价存在跨机构差异；保留原值，不合并成可比市场估值或把全部增股视作二级市场交易 |','',
    '## 共识加仓榜（仅本样本普通股票）','',
    '“共识”沿用旧榜单名称；一家的正净分也会入榜。真正的同向家数请看买入侧，不能从榜单标题反推多家一致。','']
    if expanded:
        asset_index=lines.index('## 首次披露或口径特殊的标的')
        lines[asset_index-1:asset_index-1]=[
            '| 带宽与连接 | Atreides增ALAB、CIEN；存储和芯片股同时有增减 | 客户导入、订单转化、带宽需求、盈利与估值 |',
            '| 平台与企业软件 | Coatue增MSFT/META、新列CRM/SHOP；Atreides增META、新列MSFT；Altimeter增META；Fundsmith/Pershing减MSFT/META | 订单、广告、AI投入与现金流；同时读买卖两侧 |',
            '| 质量与支付网络 | Fundsmith增VEEV/YUM/NXT/TJX及V/MA；Coatue新列V/MA，Pershing减V/MA | 经营增长、资本回报、估值及各家机会成本 |',
            '| 数据交易与眼科 | Pershing新列ICE与ALC、增NFLX；Coatue亦新列ICE | 交易数据、眼科产品与订阅内容的经营兑现；不混同投资理由 |','']
        if set(g.BATCH3_MANAGERS) <= set(CROSS_KEYS):
            asset_index=lines.index('## 首次披露或口径特殊的标的')
            lines[asset_index-1:asset_index-1]=[
                '| 行业软件与公共部门 | Dorsey新列VEEV/TYL/AXON；Giverny增VEEV；Akre减CSGP、NOW股数不变 | 产品竞争、续约、客户预算与新增资本回报 |',
                '| 租赁、信息与安全 | AKO增SUNB/ICE；Dorsey退出SUNB；Giverny增NYT/MSA | 租赁利用率、数据收费、订阅留存与安全设备需求 |',
                '| 价值框架内的平台与金融 | Harris增META/NFLX/MRSH/TEL及部分金融股，减MRK/STZ等 | 公司级类别净额、业务改善、资本配置和价格折让 |','']
        # Insert new rows inside the existing special-disclosure table.
        special_index=lines.index('## 共识加仓榜（仅本样本普通股票）')
        lines[special_index-1:special_index-1]=[
            '| PS / Pershing Square Inc. | Q3关联管理公司股份184,289,699股，与补正Q2相同；申报值$10.309bn | Q2 NEW HOLDINGS补充$6.056bn须合并原表；不能当成Q3新建或PSH基金买入自家股票 |',
            '| CBRS / Cerebras | Atreides增股，Coatue与Altimeter减股 | 上市前后股权及分配需单列；股份变化不全部等于公开市场成交 |',
            '| SKHY ADR | Coatue在Q3首次列示 | 新上市存托凭证，10份ADS对应1股普通股；不得推成首次投资或与韩国普通股直接相加 |',
            '| GRABW / Grab权证 | Altimeter申报CUSIP G4124C117，Q2/Q3均为3,502,000份 | 权证与GRAB正股是不同证券；保留申报额，普通股票榜剔除，封面差额独立披露 |','']
    lines+=market_table(buys)
    if set(g.BATCH4_MANAGERS) <= set(CROSS_KEYS):
        at=lines.index('## 首次披露或口径特殊的标的')-1
        lines[at:at]=[
            '| 平台内部换仓 | Lone Pine新列AMZN/META；Third Point新列META、退出AMZN；Maverick增MSFT/META；Kensico增AMZN/MSFT | 云、广告、资本开支和现金流，逐家比较基数及卖出侧 |',
            '| 工业分销与价值修复 | Baupost增GPC/FERG/WCC/CME，新列SITE/HONA | 需求、周转、资本回报和独立后的现金流 |',
            '| 分拆、监管与资源 | Greenlight增VGNT/PCG/DCH、新列CENX；ADIG为分派取得路径待核 | 独立经营、监管回报、周期和负债，分派不计现金买入 |',
            '| 生命科学与长期成长 | Baillie增ALNY；Lone Pine新列DHR/TMO；Maverick新列DHR | 产品销售、客户研发预算、订单与估值 |','']
        at=lines.index('## 共识加仓榜（仅本样本普通股票）')-1
        lines[at:at]=[
            '| Alphabet强制可转优先股 | Third Point另报CUSIP02079K404 | 与GOOG/GOOGL普通股不同，单列不可比工具，不合并股数或普通股评分 |',
            '| TEVA ADS转普通股 | 9月14日一比一转换；Greenlight连续比较后减股37.04% | 保留旧新CUSIP原文，不制造清仓加新建 |',
            '| ADIG / Resideo分派 | 8月每两股REZI分派一股ADIG | 母子证券相关季度差额单列未归因，不当成现金买入 |',
            '| CTVA季度后分派 | 10月1日分派Vylor，发生在本季之后 | 不把行情源调整系数当作母公司拆股；现价过滤暂不计算单一证券可比收益 |','']
    lines+=['## 共识减仓榜（仅本样本普通股票）','']+market_table(sells)
    for head,kind in [('新进前十大榜','entry'),('退出前十大榜','exit')]:
        items=[x for x in normal if any(m[kind] for m in x['managers'])]
        items.sort(key=lambda x:(-sum(m[kind] for m in x['managers']),-(x['buy'] if kind=='entry' else x['sell']),-abs(x['active'])))
        lines += [f'## {head}','','| 标的 | 机构与动作 | 判读 |','|---|---|---|']
        for x in items:
            ms=[m for m in x['managers'] if m[kind]]
            desc='；'.join(f"{m['title']}：{m['w0']:.2f}% → {m['w1']:.2f}%；{signed(m['active'])}" for m in ms)
            verdict='；'.join(f"{m['title']}："+('主动增股进入' if kind=='entry' and m['active']>1e-6 else '价格/组合分母推升，非主动买入' if kind=='entry' else '退出前十，不等于全部退出') for m in ms)
            lines.append(f"| `{x['ticker']}` | {desc} | {verdict} |")
        lines.append('')
    lines+=['## 集中度上升榜','','股数不变或减少也可能升权重。此表独立展示，不把权重上升自动计为买入。','','| 标的 | 权重提升至少 0.3pct 的机构 | 股数方向 |','|---|---|---|']
    up=[x for x in normal if any(m['w1']-m['w0']>=.3 for m in x['managers'])]
    up.sort(key=lambda x:(-sum(m['w1']-m['w0']>=.3 for m in x['managers']),-x['buy'],-abs(x['active'])))
    for x in up[:12]:
        ms=[m for m in x['managers'] if m['w1']-m['w0']>=.3]
        lines.append(f"| `{x['ticker']}` | "+'；'.join(f"{m['title']} {pp(m['w1']-m['w0'])}" for m in ms)+' | '+'；'.join(f"{m['title']} "+('增加' if m['active']>1e-6 else '减少' if m['active']< -1e-6 else '不变') for m in ms)+' |')
    lines+=['','## 机构分歧榜','','同一标的买卖两边同时出现，先看每家机构的结构，再看净额。']+['']+market_table(disagree)
    lines+=['## 宏观与交易工具','','期权份额是底层证券数量，申报值不等于权利金、净多空敞口或真实成交额；不再列示可能是到期、平仓或其他结构变化。期权权重使用各家全报告申报总额分母，不能借用非期权切片分母；ETF、权证与个股正股分别解释。','']
    tools=sorted([x for x in allrows if x['category'] in ('期权','ETF','权证')],key=lambda x:(-len(x['buyers'])-len(x['sellers']),-abs(x['active'])))
    lines+=market_table(tools,15)
    lines+=['## 解释边界','',
    f'- 只有本季与上季都取得有效申报的{len(CROSS_KEYS)}家纳入。更正按 RESTATEMENT 替换、NEW HOLDINGS 补充；13F-NT 不当作空仓。历史单位和换股调整留在各家结构化快照及趋势页。',
    '- 股数变化只能显示季末差额；真实成交时点、成本、净申赎、现金、空头及非美资产无法据此还原。首次披露不总等于首次投资，未列示也不能无限外推为从此不再持有。',
    '- 上市初期、不同估值基础和期权使金额分解解释力更弱。Duquesne 原始金额单位异常按逐份证据标准化；Appaloosa SpaceX 的申报隐含价差异保留，不能伪装为市场价格收益。',
    '- 本页价格变化使用各家快照留存的报价日期与来源；缺失明确 N/A。日线收盘与工具返回的最新成交分开注明；最新成交同时保留纽约交易日、UTC时间戳及盘中/盘后状态，不冒充常规收盘。隐含季末价不是买入成本，现价比较只用于研究排序，不产生买入建议。','',
    '## 数据来源','']
    for k,d,p,c in sources:
        filings='；'.join(link(f) for q in (c,p) for f in q['filings'])
        lines += [f"- {META[k]['name']}：[SEC submissions](https://data.sec.gov/submissions/CIK{META[k]['cik']:010d}.json)；{filings}；[[sources/{g.audit_name(d)}]]。"]
    lines += ['',f'不可变来源卡与逐份申报摘要见各家来源审计；完整在持证券和退出轨迹见单机构趋势页。本页只是{sample}横向切片。','']
    (VAULT/'wiki/institutions/13F趋势-2026Q3.md').write_text('\n'.join(lines))
    print('cross ordinary',len(normal),'buy',len(buys),'sell',len(sells),'disagree',len(disagree))


def main():
    global VAULT, SNAPSHOT_DIR, SNAPSHOT_PATHS, INSTITUTION_KEYS, CROSS_KEYS
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault',default=g.DEFAULT_VAULT)
    parser.add_argument('--snapshot-dir',help='Frozen evidence directory; defaults to VAULT/raw/data/13f-20261117')
    parser.add_argument('--batch-manifest',help='Explicit batch directories and separate institution/horizontal scopes')
    parser.add_argument('--only',choices=['all','institutions','horizontal'],default='all')
    args=parser.parse_args()
    if args.snapshot_dir and args.batch_manifest:
        parser.error('--snapshot-dir and --batch-manifest are mutually exclusive')
    VAULT=Path(args.vault).expanduser().resolve()
    SNAPSHOT_DIR=Path(args.snapshot_dir).expanduser().resolve() if args.snapshot_dir else VAULT/'raw/data/13f-20261117'
    SNAPSHOT_PATHS={};INSTITUTION_KEYS=FIRST_KEYS;CROSS_KEYS=FIRST_KEYS
    if args.batch_manifest:
        SNAPSHOT_PATHS,INSTITUTION_KEYS,CROSS_KEYS=configure_manifest(args.batch_manifest,VAULT)
    # Resolve all selected inputs before the first write so missing/malformed evidence
    # cannot produce a partially refreshed family of pages.
    for key in dict.fromkeys(INSTITUTION_KEYS+CROSS_KEYS):
        _,periods=read(key)
        if [q['date'] for q in periods[-4:]]!=['2025-12-31','2026-03-31','2026-06-30','2026-09-30']:
            raise ValueError(f'Missing four-quarter window for {key}')
    if args.only in ('all','institutions'):
        for key in INSTITUTION_KEYS:update_institution(key)
    if args.only in ('all','horizontal'):update_cross()

if __name__=='__main__':
    main()
