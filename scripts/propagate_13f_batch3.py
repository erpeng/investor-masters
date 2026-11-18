#!/usr/bin/env python3
"""Propagate frozen third-batch evidence into canonical source/company pages.

Never rewrites raw evidence. Existing prose is retained; dated behavior blocks
are idempotent. This is the explicit 2026Q3 third-batch editorial publication.
"""
import argparse
import json
import re
from pathlib import Path
import generate_13f_trends as g
import update_13f_institutions as u

COMPANIES = {
 'ABNB':'Airbnb','BN':'Brookfield','CCC':'CCC Intelligent Solutions','CRM':'Salesforce',
 'CSGP':'CoStar Group','FICO':'Fair Isaac','KKR':'KKR','MA':'Mastercard','MCO':"Moody's",
 'NOW':'ServiceNow','ORLY':"O'Reilly Automotive",'ROL':'Rollins','ROP':'Roper Technologies',
 'TDG':'TransDigm','V':'Visa','AER':'AerCap','APP':'AppLovin','ASML':'ASML','AXON':'Axon',
 'BKNG':'Booking Holdings','DHR':'丹纳赫','LYV':'Live Nation','META':'Meta','RPRX':'Royalty Pharma',
 'SPGI':'S&P Global','SUNB':'Sunbelt Rentals','TYL':'Tyler Technologies','UBER':'Uber',
 'VEEV':'Veeva Systems','ADI':'Analog Devices','ALC':'Alcon','AMZN':'亚马逊','APD':'Air Products',
 'CP':'Canadian Pacific','CSCO':'Cisco','CSL':'Carlisle','EFX':'Equifax','GE':'GE Aerospace',
 'ICE':'Intercontinental Exchange','MSFT':'微软','RACE':'Ferrari','SLB':'SLB','WMB':'Williams',
 'ADP':'ADP','ANET':'Arista Networks','BLDR':'Builders FirstSource','BRK-B':'伯克希尔·哈撒韦',
 'FIVE':'Five Below','GOOG':'Alphabet','GOOGL':'Alphabet','LULU':'Lululemon','MEDP':'Medpace',
 'MKL':'Markel','MSA':'MSA Safety','NYT':'New York Times','SCHW':'Charles Schwab',
 'ACN':'Accenture','AIG':'AIG','AXP':'American Express','C':'Citigroup','CDW':'CDW',
 'COP':'ConocoPhillips','CTVA':'Corteva','ELV':'Elevance Health','FISV':'Fiserv','ICLR':'ICON',
 'IQV':'IQVIA','KDP':'Keurig Dr Pepper','MRK':'Merck','MRSH':'Marsh & McLennan',
 'NFLX':'Netflix','RKT':'Rocket Companies','STZ':'Constellation Brands','SYF':'Synchrony Financial',
 'SYY':'Sysco','TEL':'TE Connectivity','TRGP':'Targa Resources',
}
EXTRA_DESCRIPTIONS = {
 'CSL':'建筑围护材料企业，关注建筑修缮需求、价格和资本回报',
 'ANET':'数据中心与云网络设备企业，关注客户资本开支、份额和产品迭代',
 'BLDR':'住宅建材与建筑组件供应商，关注住宅需求、产品组合和现金流',
 'LULU':'运动服饰品牌，关注同店销售、渠道、库存和品牌需求',
 'MKL':'保险与资本配置企业，关注承保、投资和长期资本回报',
 'ACN':'咨询、技术与外包服务企业，关注客户IT预算、订单和利润率',
 'AIG':'保险集团，关注承保纪律、风险准备和资本回报',
 'CDW':'企业IT产品与服务商，关注客户预算、设备更新和解决方案需求',
 'CTVA':'种子与作物保护企业，关注农业周期、产品创新和现金回报',
 'FISV':'支付与金融技术企业，关注商户交易、银行技术服务和现金流',
 'ICLR':'临床研究外包企业，关注订单、试验进度和药企研发预算',
 'MRK':'制药企业，关注产品与专利周期、研发管线和资本配置',
 'STZ':'酒类品牌企业，关注销量、定价、渠道和资本开支',
 'SYF':'消费金融企业，关注信用损失、合作渠道和融资成本',
 'SYY':'餐饮食品分销企业，关注客户需求、配送效率和利润率',
}


def upsert(text, key, body, anchor=None):
    start, end = f'<!-- {key}:start -->', f'<!-- {key}:end -->'
    block = start + '\n' + body.strip() + '\n' + end
    if start in text:
        return re.sub(re.escape(start)+r'.*?'+re.escape(end),lambda _:block,text,flags=re.S)
    if anchor and anchor in text:
        return text.replace(anchor, anchor+'\n'+block+'\n',1)
    return text.rstrip()+'\n\n'+block+'\n'


def selection(data, previous, current):
    selected=set(data['editorial']['candidates']+data['editorial']['reverse'])
    for key in set(g.top(current))-set(g.top(previous)):
        selected.add(g.security(data,current['rows'][key])['ticker'])
    for key,row in current['rows'].items():
        if not key[2] and (g.weight(current,key)-g.weight(previous,key)>=.3 or
                          (g.change(data,previous,current,key)[0]>0 and g.weight(current,key)>=1)):
            selected.add(g.security(data,row)['ticker'])
    # Index funds remain complete in the institution tool tables, not company seeds.
    return selected-{'ACWI'}


def company_block(data, previous, current, tickers):
    title,name=data['title'],data['name']
    lines=[f'### [[institutions/{name}]]：2026Q3 公开持仓行为','',
           '| 证券 | Q2股数 | Q3股数 | 调整后变化 | Q2权重 → Q3权重 | 前十变化 |',
           '|---|---:|---:|---|---|---|']
    for key in sorted(previous['rows'].keys()|current['rows'].keys()):
        row=current['rows'].get(key) or previous['rows'][key]
        if key[2] or g.security(data,row)['ticker'] not in tickers:continue
        old=previous['rows'].get(key,{}).get('shares',0);new=current['rows'].get(key,{}).get('shares',0)
        entry=key in g.top(current) and key not in g.top(previous)
        exit_=key not in g.top(current) and key in g.top(previous)
        flag='进入前十' if entry else '退出前十，未必清仓' if exit_ else '仍在前十' if key in g.top(current) else '未进入前十'
        lines.append(f'| {g.label(data,row)} | {old:,} | {new:,} | {g.format_change(data,previous,current,key)} | {g.weight(previous,key):.2f}% → {g.weight(current,key):.2f}% | {flag} |')
    checks=list(dict.fromkeys(data['editorial']['next_checks'].get(t,'继续核对经营、资本配置和估值，区分原有核心与本季增量') for t in sorted(tickers)))
    lines += ['',f'解读框架：{data["editorial"]["candidate_method"]}。这是根据机构既有方法提出的研究问题，不是管理者对本次交易原因的公开解释。',
              '下一步验证：'+'；'.join(checks)+'。',
              '报告日为2026-09-30；季度股数差不是实际交易记录，权重上涨也可能发生在减股时。当前价格过滤与来源审计见 '+f'[[institutions/13F趋势-{title}]]。']
    if name=='Oakmark Funds':lines += ['申报主体为Harris Associates L.P.，不等同于某只Oakmark基金或某位经理的个人组合。']
    if tickers & {'GOOG','GOOGL'}:lines += ['Alphabet A/C股分别保留股数，机构内部合并估算金额后才进入跨机构评分。']
    return '\n'.join(lines)


def raw_card(data, periods):
    q=periods[-1];title=data['title'];files=data['filings']
    lines=['---',f'title: SEC｜{title}：2022Q4至2026Q3持仓轨迹',
           f'source: https://data.sec.gov/submissions/CIK{data["cik"]:010d}.json',
           'date: 报告期2022-12-31至2026-09-30；核验2026-11-17',
           f'author: {data["name"]} / SEC','accessed: 2026-11-17',
           'description: 第三批机构公开行为，保留原表、修订、金额单位和来源哈希','---','',
           f'# SEC｜{title}：2022Q4至2026Q3持仓轨迹','',
           f'CIK `{data["cik"]}`；归档{len(files)}份申报，解析16个季度。2022Q4为基期，展示2023Q1—2026Q3。',
           f'Q3报告日2026-09-30；申报日{q["filings"][-1]["filingDate"]}。聚合{len(q["rows"])}个证券身份，标准化行和`${q["total"]:,.0f}`。','',
           f'不可变证据：`raw/data/13f-20261117-batch3/{data["institution"]}.json`；原始SEC文件、submissions、原方法页及哈希清单位于同一目录。已取得的公司行动附件和SEC证券映射保留在quote-evidence，下载失败亦记录，不能声称附件全部下载成功。','',
           '## 金额与修订','',
           '| 报告期 | 申报日 | 原文 | 倍率 | 修订类型 |','|---|---|---|---:|---|']
    for f in files:lines.append(f'| {f["reportDate"]} | {f["filingDate"]} | [{f["accessionNumber"]}]({f["url"]}) | {f.get("unit_multiplier",0):g} | {f.get("amendment_type") or "原报"} |')
    lines += ['','## 核验重点','']+['- '+n for n in data['editorial']['notes']]
    lines += ['','## 材料边界','','13F不能还原现金、空头、完整全球组合、申赎或真实交易成本。报价只用于日期明确的研究过滤；分拆分派不当作母公司拆股，未充分核验的历史异常明确保留缺口。','']
    return '\n'.join(lines)


def audit_body(data, company_names):
    title=data['title'];links='、'.join(f'[[companies/{n}]]' for n in sorted(company_names))
    lines=['## 来源定位','',f'[[raw/SEC｜{title}：2022Q4至2026Q3持仓轨迹]]；结构化证据`raw/data/13f-20261117-batch3/{data["institution"]}.json`。本轮核验2026-11-17。','',
           '## source-complete coverage','','| 层 | 本轮责任 |','|---|---|',
           '| investors / ten-questions | 13F只证明有限公开行为，不新增人物动机或十问答案 |',
           f'| companies | {links} |',
           f'| institutions | [[institutions/{data["name"]}]]、[[institutions/13F趋势-{title}]] |',
           '| concepts / dialogues | 未新增足够方法证据，保留已有页 |',
           '| indexes / matrix | 更新15家Q3横向页、来源与公司入口；方法矩阵不变 |','',
           '## 这篇材料明确能回答哪些十问','','不能独立回答十问；持仓行为不能代替管理者的原因解释。','',
           '## 这篇材料要求回填哪些投资人页','','不扩写人物页。Akre当前行为归于对应管理时期，Harris申报也不归为单一经理个人交易。','',
           '## 这篇材料要求新建或更新哪些公司页','',links+'。',
           '覆盖候选、反向复盘、新进前十、权重提升至少0.3个百分点及增股且当前权重至少1%的证券。其余小仓、历史退出和ETF保留在完整轨迹；没有新增实质研究问题时暂缓独立公司页。','',
           '## 这篇材料要求新建或更新哪些概念 / 对话 / 机构页','',
           '机构主页滚动至2025Q4—2026Q3，长趋势保留2023Q1起全部季度与旧方法；[[institutions/13F趋势-2026Q3|15家横向页]]重新计算。','',
           '## 核验重点','']+['- '+n for n in data['editorial']['notes']]
    lines += ['- 同CUSIP类别拼写按原始表逐项归一；原文及归一依据保留在快照。',
              '- 当前候选使用2026-11-16行情；缺失保留N/A。同日报价复用保留旧快照哈希与本次失败记录。',
              '- 官方拆股与分拆区别记录：历史分拆价格调整不乘入母公司股数，实际拆并股使用确证比例。','',
              '### 公司行动证据','']
    if data['institution']=='giverny':
        lines += ['Q2原报与8月26日修订的51条证券记录、股数和市值逐项一致，均为$2,974,321,189；采用修订并未改变本次Q2持仓基数。历史2025Q3连续两份RESTATEMENT按申报顺序采用最后一份，不能停在第一份修订。','']
    for x in data.get('audit',{}).get('excluded_price_adjustments',[]):
        lines.append(f'- {x["ticker"]} {x["date"]}：[官方依据]({x["primary_source"]})；母公司股数不因分派而乘以行情价格调整系数。')
    for x in data['splits']:
        lines.append(f'- {x["ticker"]} {x["date"]}：股数倍率{x["ratio"]:g}；[依据]({x.get("primary_source") or x["source"]})。')
    issues=data.get('audit',{}).get('unresolved_splits',[])
    if issues:
        lines += ['','### 历史资料缺口','']+[f'- {x["ticker"] or x["cusip"]}：{x["start"]}→{x["end"]}隐含价异常，尚未完成独立公司行动核验；保留原始股数，相关股数项只作机械比较。' for x in issues]
    lines += ['','## 这篇材料不能回答什么','','不能把总值变化当基金回报，把股数差当真实现金流，也不能由减持证明投资论点失败。研究候选只是下一步核查顺序。','',
              '## 传播清单','','- [x] 原始证据、金额倍率、修订与身份归一可追溯。',
              '- [x] 长趋势、机构四季、公司页、来源登记与15家横向入口联动。',
              '- 构建、测试和路由验收以[[log|维护日志]]的本轮最终验收条目为准。','']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault',default=g.DEFAULT_VAULT)
    args=parser.parse_args();vault=Path(args.vault);wiki=vault/'wiki';snapshot=vault/'raw/data/13f-20261117-batch3'
    affected=set();created=[];obligations={}
    for key in g.BATCH3_MANAGERS:
        data=json.loads((snapshot/f'{key}.json').read_text());periods=g.resolve_filings(data);previous,current=periods[-2:]
        selected=selection(data,previous,current)
        if selected-COMPANIES.keys():raise ValueError(f'Unreviewed company names: {selected-COMPANIES.keys()}')
        names={COMPANIES[t] for t in selected};obligations[key]=sorted(names)
        for name in sorted(names):
            tickers={t for t,n in COMPANIES.items() if n==name};path=wiki/'companies'/f'{name}.md'
            if not path.exists():
                t=next(t for t in sorted(selected) if COMPANIES[t]==name)
                desc=u.DESC.get(t,('',EXTRA_DESCRIPTIONS.get(t,'')))[1]
                if not desc:raise ValueError('Missing business description: '+t)
                path.write_text(f'---\ntype: company\nstatus: seed\nupdated: 2026-11-17\n---\n\n# {name}\n\n## 简介\n\n{desc}。本页由2026Q3机构持仓引出研究问题，尚非独立估值报告。\n\n## 公司点评\n\n## 相关页面\n\n## 主要来源\n')
                created.append(name)
            text=path.read_text();text=upsert(text,f'13f-2026q3-{key}',company_block(data,previous,current,tickers),'## 公司点评\n')
            text=upsert(text,f'13f-2026q3-{key}-links',f'- [[institutions/{data["name"]}]]；[[institutions/13F趋势-{data["title"]}]]；[[institutions/13F趋势-2026Q3]]','## 相关页面\n')
            text=upsert(text,f'13f-2026q3-{key}-sources',f'- [[raw/SEC｜{data["title"]}：2022Q4至2026Q3持仓轨迹]]；[[sources/{g.audit_name(data)}]]','## 主要来源\n')
            path.write_text(re.sub(r'^updated:.*$','updated: 2026-11-17',text,count=1,flags=re.M));affected.add(name)
        g.save_new(vault/'raw'/f'SEC｜{data["title"]}：2022Q4至2026Q3持仓轨迹.md',raw_card(data,periods).encode())
        audit=wiki/'sources'/f'{g.audit_name(data)}.md';body=audit_body(data,names)
        if key=='akre':
            text=audit.read_text();body='## 2026Q3 第三批更新\n\n'+re.sub(r'^(#{2,3}) ',lambda m:'#'+m[0],body,flags=re.M)
            text=upsert(text,'13f-2026q3-third-batch-audit',body)
            audit.write_text(re.sub(r'^updated:.*$','updated: 2026-11-17',text,count=1,flags=re.M))
        else:audit.write_text('---\ntype: source-audit\nstatus: active\nupdated: 2026-11-17\n---\n\n# '+g.audit_name(data)+'\n\n'+body)
    index=wiki/'companies/index.md';text=index.read_text()
    text=text.replace('Pershing 十家的','Pershing，以及 Akre、Dorsey、AKO、Giverny、Harris / Oakmark 十五家的')
    body='\n'.join(f'- [[companies/{name}]]' for name in sorted(affected))
    text=upsert(text,'13f-2026q3-third-company-index','### 第三批质量与价值机构的研究入口\n\n'+body,'## 2026Q3：先看持仓分歧，再看新增线索\n');index.write_text(text)
    # 166 previously tracked articles + 5 new cards; four unregistered inbox
    # interviews are outside this ingest and must not inflate the registry.
    registry=wiki/'sources/来源总表.md';text=registry.read_text()
    text=re.sub(r'^source_count: (170|175)$','source_count: 171',text,flags=re.M)
    text=re.sub(r'当前注册 (170|175) 篇','当前注册 171 篇',text)
    cards='\n'.join(f'- [[raw/SEC｜{g.BATCH3_MANAGERS[k][0]}：2022Q4至2026Q3持仓轨迹]]；[[sources/{"Akre-13F-source-audit" if k=="akre" else g.BATCH3_MANAGERS[k][0]+"-13f-source-audit"}]]。' for k in g.BATCH3_MANAGERS)
    registry.write_text(upsert(text,'13f-2026q3-third-sources','## 2026Q3 第三批：五家机构\n\n'+cards))
    home=wiki/'index.md';home.write_text(re.sub(r'^source_count: (170|175)$','source_count: 171',home.read_text(),flags=re.M).replace('2026Q3 十家机构横向对照','2026Q3 十五家机构横向对照（15/23，余8家）'))
    entry=wiki/'institutions/13F趋势.md';text=entry.read_text();start=text.index('最新增量：');end=text.index('## 趋势解读')
    text=text[:start]+('最新增量：[[institutions/13F趋势-2026Q3|Q3 2026 十五家机构]]。本轮续更Akre、Dorsey、AKO、Giverny、Oakmark / Harris；23张机构专题中15家已更新，余8家保留2026Q2。\n\n'
        '待续更：Third Point、Kensico、Maverick、Baupost、Baillie Gifford、Greenlight、Lone Pine、Tudor。上一季[[institutions/13F趋势-2026Q2|22家样本]]保留档案；不同样本的名次不能直接比较。\n\n'
        '新增证据使质量机构的分歧更清楚：Dorsey与Giverny加入Veeva增股侧；Akre缩减多个核心并新增小仓；AKO增SUNB而Dorsey退出。Harris增加GOOG、减少GOOGL，先合并类别再读净变化。\n\n'
        '核验日期2026-11-17，报告期2026-09-30。最新机构主页展示2025Q4—2026Q3四季，长趋势保留2023Q1起历史。Giverny以修订后Q2为基准，AKO金额逐份校准，Harris申报不等同单只基金。\n\n')+text[end:]
    for title,_,_ in g.BATCH3_MANAGERS.values():
        text=re.sub(r'(^- .*?\[\[institutions/13F趋势-'+re.escape(title)+r'.*$)',lambda m:m[0].replace('2026Q2','2026Q3').replace('最新 CSGP/NOW 加股、老核心缩股','最新FICO增股、TDG/ROL新列、多个核心缩股'),text,flags=re.M)
    text=re.sub(r'Giverny=1\.4, Dorsey=1\.3, AKO=1\.3(?:, Akre=1\.4（本季新增启发式）)*',
                'Giverny=1.4, Dorsey=1.3, AKO=1.3, Akre=1.4（本季新增启发式）',text)
    entry.write_text(text)
    log=wiki/'log.md';text=log.read_text();marker='institution-13f-2026q3-third-five'
    if marker not in text:
        with log.open('a') as out:out.write(f'\n\n## [2026-11-17] {marker} | 第三批五家，扩展至十五家\n\n- 更新Akre、Dorsey、AKO、Giverny、Oakmark / Harris，长历史与最近四季联动，Q3横向按15家重算；剩8家。\n- 原始证据独立冻结，Giverny修订替换、AKO金额单位、Akre历史补报及跨季证券身份校正均保留审计。\n- 联动{len(affected)}家公司页及索引、来源登记；新增五张来源卡，注册171篇。构建及测试结果由后续验收条目记录。\n- 本轮本地更新，不提交、推送或发布。\n')
    print(json.dumps({'companies':len(affected),'created':created,'obligations':obligations},ensure_ascii=False))


if __name__=='__main__':main()
