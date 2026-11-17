#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replay the 2026Q3 five-institution overview and horizontal pages.

Read-only input: immutable JSON snapshots. Writes only institution overview and
horizontal Markdown under --vault; never changes raw evidence, audit cards,
registries, logs, companies or the separate long-history trend pages.
"""
from pathlib import Path
import argparse
import json
import re
import collections
import generate_13f_trends as g

VAULT=Path(g.DEFAULT_VAULT)
SNAPSHOT_DIR=VAULT/'raw/data/13f-20261117'
DATE='2026-11-17'
WEIGHTS={'berkshire':1.5,'himalaya':1.4,'hh':1.4,'duquesne':.8,'appaloosa':.8}
META={k:{'title':v[0],'name':v[1],'cik':v[2]} for k,v in g.MANAGERS.items()}
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

def read(k):
    path=SNAPSHOT_DIR/f'{k}.json'
    data=json.loads(path.read_text(encoding='utf-8'))
    if data.get('latest_quarter')!='2026Q3':
        raise ValueError(f'This renderer replays 2026Q3 evidence only: {path}')
    return data,g.resolve_filings(data)


def ticker(d,r): return g.security(d,r).get('ticker') or r['cusip']
def money(v): return f'${v/1e9:,.3f}bn' if abs(v)>=1e9 else f'${v/1e6:,.2f}m'
def signed(v): return ('+' if v>=0 else '−')+money(abs(v))
def pp(v): return f'{v:+.2f}pct'
def index(f): return f['url'].rsplit('/',1)[0]+'/'+f['accessionNumber']+'-index.htm'
def link(f): return f"[SEC {f['form']} · {f['reportDate']} · {f['filingDate']}]({index(f)})"
def pct(x): return f'{x:+.2%}'
ETF_ISSUER_RE=re.compile(r'\b(?:ETF|ISHARES|SPDR|INVESCO|VANECK|PROSHARES|DIREXION|KRANESHARES|VANGUARD|WISDOMTREE)\b|\bEXCHANGE\s+TRADED\b',re.I)

def instrument_type(row):
    """Describe the listed instrument without treating all foreign shares as ADRs."""
    cls=row['security_class'].upper()
    if ETF_ISSUER_RE.search(row['issuer']) or re.search(r'\bETF\b',cls):
        return 'ETF'
    if re.search(r'\b(?:ADR|ADS)\b',cls):
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
    top5=sum(curr['rows'][x]['value'] for x in g.top(curr,5))/curr['total']
    top10=sum(curr['rows'][x]['value'] for x in g.top(curr,10))/curr['total']
    lines=['## 13F 持仓（近四个季度）','','### 怎么看这组披露','',
    '13F 是季末公开证券多头及部分期权的滞后披露，不是完整资产组合。以下按 CUSIP、证券类别和 PUT/CALL 聚合重复管理人记录；期权与正股不混算。市值和权重变化不能替代股数变化。', '',
    '### 13F 趋势雷达（最近一季横向）','',
    f"最近一季：`2026Q3` vs `2026Q2`；报告日 `2026-09-30`；申报日 `{curr['filings'][-1]['filingDate']}`；核验 `{DATE}`。",'',
    f"- 申报总值从 `{money(prev['total'])}` 变为 `{money(curr['total'])}`（`{pct(curr['total']/prev['total']-1)}`）；聚合后 `{len(curr['rows'])}` 个证券类别，其中期权 `{nopt}` 个。证券口径前五占 `{top5:.2%}`、前十占 `{top10:.2%}`。",
    f"- 非期权证券切片：按上季隐含价格估算的主动变化 `{signed(active)}`，价格项 `{signed(price)}`。这是两期持仓的机械分解，不是现金流、真实成交额或投资收益；首次上市、估值口径不同的证券另见趋势页边界。"]
    if nopt or optactive or optprice:
        lines.append(f'- 期权切片另计：申报值变化的主动项 `{signed(optactive)}`、价格项 `{signed(optprice)}`；缺少期限、执行价、权利金及其他组合腿，不能推导净风险。')
    rounding=curr['filings'][-1].get('cover_difference',0)
    if rounding:
        lines.append(f"- 信息表逐行合计与封面总额相差 `${rounding:,.0f}`，来自原始申报取整；本页市值和权重统一采用信息表行和，原值与差额保留在证据快照。")
    if k=='hh': lines.append('- H&H 是段永平相关的美国申报主体；以下不能代表其个人全部投资。')
    lines += ['- '+s for s in RADAR[k]]
    lines += [f"- 长历史与全部在持证券：[[institutions/13F趋势-{meta['title']}]]；横向页：[[institutions/13F趋势-2026Q3|Q3 首批五家]]。",'',
    '### 近四个已披露季度前 10 大持仓','']
    for q in reversed(qs[-4:]):
        year=q['date'][:4]; qu=g.quarter(q['date'])[-1]
        lines += [f'#### Q{qu} {year}','',f"申报总值 `{money(q['total'])}`；聚合后 `{len(q['rows'])}` 个证券类别。",'', '| 证券及业务 | 股数／底层份额 | 季末申报市值 | 13F 占比 |','|---|---:|---:|---:|']
        for key in g.top(q):
            r=q['rows'][key]
            lines.append(f"| {intro(d,r)} | {r['shares']:,} | {money(r['value'])} | {r['value']/q['total']:.2%} |")
        lines.append('')
    lines += ['### 这四季的变化小结','',{
      'berkshire':'2025Q4—2026Q3 的核心大仓仍高度集中；2026Q2 已纳入两类 Alphabet 股票，Q3 股数保持不变。Q3 的新证据是住房、航空的增股与 Bending Spoons 首次披露，同时银行和部分金融证券减股。两季信息分别保留，不能把 Q2 已有仓位写成本季新买。',
      'himalaya':'2025Q4—2026Q1 仍有较多金融和能源证券；Q2 收缩为八个类别并大增 PDD、BRK.B，Q3 再增 PDD 和 TME。最新变化是集中组合内部继续调配，不能把未变股数的 Alphabet 权重移动写成交易。',
      'hh':'四季内 PDD 与 TSLA 的配置变化值得单独跟踪；Q2、Q3 的 NVDA 和 GOOG 减股也应连续观察。苹果和伯克希尔的大权重是组合结构事实，与当季是否增股是两个问题。',
      'duquesne':'四季轨迹显示持续轮动，Q3 的存储、软件、平台和黄金增量与部分芯片证券减仓并存。正股、CALL、PUT 各自沿同一类别追踪，不以期权名义申报值代替净多空判断。',
      'appaloosa':'四季应同时看半导体链、中国互联网、美国平台与首次上市证券。Q3 加仓存储和设备，同时减持部分平台，不能压成“全面看多科技”这一句话；持仓变化也不直接证明管理人的买入动机。',
    }[k], '', '### 数据来源','']
    for q in reversed(qs[-4:]):
        for f in q['filings']: lines.append('- '+link(f))
    lines += [f"- [[raw/SEC｜{meta['title']}：2022Q4至2026Q3持仓轨迹]]；[[sources/{meta['title']}-13f-source-audit]]。",'']
    p=VAULT/f"wiki/institutions/{meta['name']}.md"
    text=p.read_text()
    text=re.sub(r'## 13F 持仓.*?(?=## 机构传承)', '\n'.join(lines)+'\n', text, flags=re.S)
    text=re.sub(r'^updated: .*$',f'updated: {DATE}',text,count=1,flags=re.M)
    count={'berkshire':7,'himalaya':5,'hh':4,'duquesne':4,'appaloosa':12}[k]
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

def category(r,t):
    if r['put_call']: return '期权'
    if t in ('SPCX','Bending Spoons') or r['cusip'] in ('84615Q103','T19377109'): return '特殊披露'
    if instrument_type(r)=='ETF': return 'ETF'
    return '普通股票'

def cross_data():
    out={}; sources=[]
    for k,m in META.items():
        d,qs=read(k); p,c=qs[-2:]; sources.append((k,d,p,c))
        families=[]
        for q in (p,c):
            fq=collections.defaultdict(lambda:{'value':0,'rows':[]})
            for key,r in q['rows'].items():
                ident=(family(d,r),category(r,ticker(d,r)),r['put_call'])
                fq[ident]['value']+=r['value'];fq[ident]['rows'].append((key,r))
            families.append(fq)
        fp,fc=families
        top0=set(sorted(fp,key=lambda x:fp[x]['value'],reverse=True)[:10]);top1=set(sorted(fc,key=lambda x:fc[x]['value'],reverse=True)[:10])
        for f in sorted(set(fp)|set(fc)):
            a,b=fp.get(f,{}),fc.get(f,{})
            keys=set(x[0] for x in a.get('rows',[]))|set(x[0] for x in b.get('rows',[]))
            active=0
            for key in sorted(keys):
                old,new=p['rows'].get(key),c['rows'].get(key)
                if not old: active+=new['value']
                elif not new: active-=old['value']
                else:
                    q0=old['shares']*g.split_factor(d,old,p['date'],c['date'])
                    active+=(new['shares']-q0)*old['value']/q0 if q0 else new['value']-old['value']
            w0=a.get('value',0)/p['total']*100;w1=b.get('value',0)/c['total']*100
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

def quote_note(x):
    values=[]
    for m in x['buyers']:
        d=m['data']
        for _,r in m['new'].get('rows',[]):
            t=ticker(d,r);q=d.get('quotes',{}).get(t,{})
            if q.get('price') is None: continue
            if x['category']!='普通股票': continue
            ratio=g.split_factor(d,r,'2026-09-30',q['price_date'])
            anchor=r['value']/r['shares']/ratio
            change=q['price']/anchor-1
            v=f"[{t} {change:+.1%}]({q['source']})（{q['price_date']}）"
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
    buys=sorted([x for x in normal if x['net']>1e-6],key=lambda x:(-x['net'],-len(x['buyers']),-abs(x['active'])))
    sells=sorted([x for x in normal if x['net']< -1e-6],key=lambda x:(x['net'],-len(x['sellers']),-abs(x['active'])))
    disagree=sorted([x for x in normal if x['buyers'] and x['sellers']],key=lambda x:(-min(x['buy'],x['sell']),-len(x['buyers'])-len(x['sellers'])))
    lines=['---','type: institution-13f-trend','status: active',f'updated: {DATE}','quarter: 2026Q3','---','','# 13F 趋势 · 2026Q3（首批五家）','',
    '本页仅覆盖本轮已更新的 Berkshire、Himalaya、H&H、Duquesne、Appaloosa。报告日均为 `2026-09-30`，核验日期 `2026-11-17`；比较基期为 `2026-06-30`。其他机构未纳入本页，不能据此称全体“大师”或市场达成共识，也不能把本页名次与 Q2 的 22 家样本直接比较。','',
    '## 覆盖口径','',
    '| 机构 | Q3 申报日 | Q2 申报值 | Q3 申报值 | Q3 聚合证券数（含期权） | 风格权重 |','|---|---|---:|---:|---:|---:|']
    for k,d,p,c in sources:
        lines.append(f"| [[institutions/13F趋势-{META[k]['title']}|{META[k]['title']}]] | {c['filings'][-1]['filingDate']} | {money(p['total'])} | {money(c['total'])} | {len(c['rows'])} | {WEIGHTS[k]:.1f} |")
    lines += ['','沿用 [[institutions/13F趋势|总入口]] 的主动额和评分结构：已有仓位按 `股数差 × 上季隐含价`，新列示按本季申报值，退出按上季申报值负数估算；先在机构内部净额，再做横向汇总。Berkshire=1.5、Himalaya/H&H=1.4、Duquesne=0.8；Appaloosa 本轮明确为 0.8，这是规则补记，不追称旧榜单已用此值。',
    '', '只在有主动增加/减少时给相应方向评分：基础 3 倍风格权重，主动进入/退出前十加 2 倍，权重同向变化至少 0.3pct 再加 1 倍。同公司类别先按证券身份比较，再合并公司级金额和权重；GOOG/GOOGL、BRK.A/B、LEN A/B 不当作互相独立的公司信号。ETF、期权和特殊披露不进入普通股票主榜。','',
    '普通股票榜保留 ADR/ADS，但加注存托凭证属性：如 PDD、TME、SE、TSM，申报份额不是可直接等同的当地普通股股数，需另核凭证比例、存托安排与公司注册地风险。ASML 单列“纽约登记股”，不是把所有境外公司一律称作 ADR；其 Nasdaq 证券为注册普通股，见 [ASML 官方股份说明](https://www.asml.com/en/investors/shares)。ETF 以完整名称 token 和申报类别识别，不用股票名称中的字母片段判断。','',
    '## 结论先行','',
    '- **PDD 是本样本最清楚的两家长期集中型机构同向动作。** Himalaya 增股 9.29%，H&H 增股 11.86%；两家分别持有、分别决策，不能把它们并成一个买入理由。TME 的大比例增股来自 Himalaya 一家。',
    '- **半导体内部轮动大于行业一致加仓。** Appaloosa 增加 MU、NVDA、LRCX、ASML，Duquesne 减少 TSM、退出 AMD/ARM/LRCX，H&H 继续减 NVDA。相同产业标签不足以覆盖这些相反动作。',
    '- **平台也有分歧。** Duquesne 增加 AMZN、SE、U，Appaloosa 减少 AMZN、META、GOOG。Berkshire 的 AAPL、AXP、KO、Alphabet 股数不动，AAPL 权重提升属于价格/组合分母效应。',
    '- **新增小仓与特殊披露另看。** Berkshire 增加 LEN、DAL 并首次列示 Bending Spoons；Appaloosa 的 SpaceX 股数扩张幅度大，但申报估值与其他机构不同。不能把这些直接写成可复制的成交信号。','',
    '## 普通股票研究优先级','',
    '以下先展示按净分排序的研究入口，再看交易风格、分歧和披露后价格。净分不是胜率或收益预测；缺少可比行情时，不生成“当前可以买”结论。与前期相比，本页把价格导致的前十进入显式单列，不给主动买入分。','',
    '| 标的及证券属性 | 本样本净分 | 主动增加机构 | 13F 锚点后价格变化 | 下一步核验 |','|---|---:|---|---|---|']
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
    lines+=market_table(buys)
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
    lines+=['## 宏观与交易工具','','期权份额是底层证券数量，申报值不等于权利金、净多空敞口或真实成交额；不再列示可能是到期、平仓或其他结构变化。ETF 与个股正股分别解释。','']
    tools=sorted([x for x in allrows if x['category'] in ('期权','ETF')],key=lambda x:(-len(x['buyers'])-len(x['sellers']),-abs(x['active'])))
    lines+=market_table(tools,15)
    lines+=['## 解释边界','',
    '- 只有本季与上季都取得有效申报的五家纳入。更正按 RESTATEMENT 替换、NEW HOLDINGS 补充；13F-NT 不当作空仓。历史单位和换股调整留在各家结构化快照及趋势页。',
    '- 股数变化只能显示季末差额；真实成交时点、成本、净申赎、现金、空头及非美资产无法据此还原。首次披露不总等于首次投资，未列示也不能无限外推为从此不再持有。',
    '- 上市初期、不同估值基础和期权使金额分解解释力更弱。Duquesne 原始金额单位异常按逐份证据标准化；Appaloosa SpaceX 的申报隐含价差异保留，不能伪装为市场价格收益。',
    '- 本页价格变化使用各家快照留存的报价日期与来源；缺失明确 N/A。隐含季末价不是买入成本，现价比较只用于研究排序，不产生买入建议。','',
    '## 数据来源','']
    for k,d,p,c in sources:
        lines += [f"- {META[k]['name']}：[SEC submissions](https://data.sec.gov/submissions/CIK{META[k]['cik']:010d}.json)；{link(c['filings'][-1])}；{link(p['filings'][-1])}；[[sources/{META[k]['title']}-13f-source-audit]]。"]
    lines += ['','不可变来源卡与逐份申报摘要见各家来源审计；完整在持证券和退出轨迹见单机构趋势页。本页只是首批五家横向切片。','']
    (VAULT/'wiki/institutions/13F趋势-2026Q3.md').write_text('\n'.join(lines))
    print('cross ordinary',len(normal),'buy',len(buys),'sell',len(sells),'disagree',len(disagree))


def main():
    global VAULT, SNAPSHOT_DIR
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault',default=g.DEFAULT_VAULT)
    parser.add_argument('--snapshot-dir',help='Frozen evidence directory; defaults to VAULT/raw/data/13f-20261117')
    parser.add_argument('--only',choices=['all','institutions','horizontal'],default='all')
    args=parser.parse_args()
    VAULT=Path(args.vault).expanduser().resolve()
    SNAPSHOT_DIR=Path(args.snapshot_dir).expanduser().resolve() if args.snapshot_dir else VAULT/'raw/data/13f-20261117'
    # Resolve all five inputs before the first write so missing/malformed evidence
    # cannot produce a partially refreshed family of pages.
    for key in META:
        _,periods=read(key)
        if [q['date'] for q in periods[-4:]]!=['2025-12-31','2026-03-31','2026-06-30','2026-09-30']:
            raise ValueError(f'Missing four-quarter window for {key}')
    if args.only in ('all','institutions'):
        for key in META:update_institution(key)
    if args.only in ('all','horizontal'):update_cross()

if __name__=='__main__':
    main()
