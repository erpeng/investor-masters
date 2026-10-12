#!/usr/bin/env python3
"""Render Akre's SEC filing snapshot without depending on another checkout.

Canonical evidence: raw/data/akre-13f-20261012.json in INVESTORS_VAULT.
Run: python3 scripts/generate_akre_13f_trend.py --vault /path/to/vault
Use --data for a new, separately archived snapshot. Existing raw is immutable.
Snapshot retains every filing (including amendments), cover totals, source URLs,
CUSIP/class/putCall, split evidence and timestamped quote results.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import re
from pathlib import Path


def identity(row):
    return (row['cusip'].strip().upper(), ' '.join(row['security_class'].upper().split()), row['put_call'].strip().upper())


def aggregate(rows):
    out = {}
    for row in rows:
        key = identity(row)
        if key not in out:
            out[key] = dict(row)
        else:
            if row['share_type'] != out[key]['share_type']:
                raise ValueError(f'Incompatible units: {key}')
            out[key]['shares'] += row['shares']
            out[key]['value'] += row['value']
    return out


def resolve_filings(data):
    quarters = {}
    for f in sorted(data['filings'], key=lambda x: (x['filingDate'], x['accessionNumber'])):
        if f['unit'] != 'USD':
            raise ValueError('Normalize source units explicitly before rendering')
        if sum(r['value'] for r in f['rows']) != f['reported_total'] or len(f['rows']) != f['reported_count']:
            raise ValueError(f"SEC cover mismatch: {f['accessionNumber']}")
        date = f['reportDate']
        rows = aggregate(f['rows'])
        if f['form'] == '13F-HR':
            if date in quarters:
                raise ValueError(f'Duplicate original for {date}')
            quarters[date] = dict(date=date, rows=rows, filings=[f], notes=[])
            continue
        q = quarters[date]
        kind = f['amendment_type']
        if kind == 'RESTATEMENT':
            q['rows'] = rows
        elif kind == 'NEW HOLDINGS':
            duplicate = 0
            for key, row in rows.items():
                if key in q['rows']:
                    old = q['rows'][key]
                    if (old['value'], old['shares'], old['share_type']) != (row['value'], row['shares'], row['share_type']):
                        raise ValueError(f'Ambiguous overlapping NEW HOLDINGS: {key}')
                    duplicate += 1
                else:
                    q['rows'][key] = row
            q['notes'].append(f"{f['accessionNumber']} 标为 NEW HOLDINGS；{duplicate} 条与原表股数、市值相同的重复证券去重，仅补入新增证券。")
        else:
            raise ValueError(f'Unknown amendment type: {kind}')
        q['filings'].append(f)
    for q in quarters.values():
        q['total'] = sum(r['value'] for r in q['rows'].values())
    return sorted(quarters.values(), key=lambda q: q['date'])


def quarter(date):
    return f'{date[:4]}Q{(int(date[5:7])-1)//3+1}'


def ticker(data, row):
    return data['securities'][row['cusip'].upper()]['ticker']


def label(data, row):
    sec = data['securities'][row['cusip'].upper()]
    return f"{sec['ticker']}（{sec['name']}）" + (f" {row['put_call']}" if row['put_call'] else '')


def factor(data, row, start, end):
    return math.prod(s['ratio'] for s in data['splits'] if s['ticker'] == ticker(data, row) and start < s['date'] <= end)


def delta(data, previous, current, key):
    a, b = previous['rows'].get(key), current['rows'].get(key)
    old = a['shares'] * factor(data, a, previous['date'], current['date']) if a else 0
    new = b['shares'] if b else 0
    return new-old, (new/old-1 if old else None)


def attribution(data, previous, current, options=False):
    active = price = 0.
    for k in set(previous['rows']) | set(current['rows']):
        if bool(k[2]) != options:
            continue
        a, b = previous['rows'].get(k), current['rows'].get(k)
        if not a:
            active += b['value']
        elif not b:
            active -= a['value']
        else:
            q0 = a['shares'] * factor(data, a, previous['date'], current['date'])
            p0 = a['value']/q0
            active += (b['shares']-q0)*p0
            price += b['value']-b['shares']*p0
    return active, price


def top(q, n=10):
    return sorted(q['rows'], key=lambda k: q['rows'][k]['value'], reverse=True)[:n]


def weight(q, k):
    return q['rows'].get(k, {}).get('value', 0)/q['total']*100


def money(value):
    return f'${value/1e9:.3f}bn'


def price_cells(data, row, date):
    t = ticker(data, row)
    anchor = row['value']/row['shares']/factor(data, row, date, data['as_of'])
    quote = data['quotes'].get(t, {})
    p = quote.get('price')
    if p is None or quote.get('currency') != 'USD':
        return f'${anchor:.2f}', 'N/A', 'N/A', '行情缺失，暂不判断追涨程度'
    change = p/anchor-1
    if change > .5:
        verdict = '仅复盘/等待，价格已大幅脱离季末'
    elif change > .25:
        verdict = '降低优先级，先验证盈利上修'
    elif change > .1:
        verdict = '需更强基本面验证'
    elif change < 0:
        verdict = '下跌不证明便宜，先排查论点受损'
    else:
        verdict = '价格未明显阻碍，仍需估值验证'
    return f'${anchor:.2f}', f'${p:.2f}', f'{change:+.1%}', verdict


def render(data, quarters):
    qs = [q for q in quarters if q['date'] >= '2023-01-01']
    latest, previous = quarters[-1], quarters[-2]
    name = quarter(latest['date'])
    active, price = attribution(data, previous, latest)
    out = [f'---\ntype: institution-13f-trend\nstatus: active\nupdated: {data["as_of"]}\n---\n', '# 13F 趋势 - Akre',
        f'\n核验日期：{data["as_of"]}。SEC CIK 1112520；最新报告期 {latest["date"]}，提交日 {latest["filings"][-1]["filingDate"]}。',
        '\n## 结论先行\n',
        f'{name} 申报总市值 {money(latest["total"])}，较上季 {latest["total"]/previous["total"]-1:+.1%}。普通股的份额变化估值约 {money(active)}、期末价格变化贡献约 {money(price)}；这是季度端点分解，不是实际资金流。',
        '最新一季只有 CSGP 与 NOW 普通股股数增加，其余以缩股或持平为主。MA 仍是第一大持仓，但属于减股后保留核心位置。CPRT 几乎不变却进入前十，不能叫主动买入进前十。',
        '这组行为应归于 John Neff 主导时期的 Akre 机构。Chuck 已于 2020 年底卸任基金经理。现有 13F 无法判断缩表有多少来自申赎、账户迁移、估值纪律或观点变化。',
        '\n## 数据口径\n',
        '- 展示 2023Q1 起所有季度，另保留 2022Q4 基期；所有源表逐条核对 SEC 封面数量和总值。该组申报均采用 X0202 的美元口径，不再乘 1,000。',
        '- 身份使用 CUSIP + 规范化证券类别 + PUT/CALL，ticker 仅展示。原始股数保留；相邻季度变化按已核实拆股调整。BN 与 BAM 是不同证券，正股与 CALL 也是不同证券。',
        '- 权重分母是申报表全部 value（含期权对应的标的市值），并非基金净资产。期权 value 不是权利金，share 数是对应标的股数，不是合约张数；无法推导 delta、到期日、执行价或净敞口。',
        '- 主动项 = (本季股数 − 拆股调整后上季股数) × 调整后上季隐含价；价格项 = 本季股数 × 隐含价差。新增归主动、退出按上季市值归主动减少。该恒等分解不包含真实交易价、分红或期中路径。',
        '- 13F 看不到现金、空头、绝大部分非美证券和完整衍生品。Constellation Software 是机构重要研究案例，却不在本组 13F 中，不能据此认定机构没有持有。']
    for q in quarters:
        out += ['- '+n for n in q['notes']]
    out += ['\n拆股校正：' + '；'.join(f"{s['ticker']} {s['date']} {s['ratio']:g}:1" for s in data['splits']) + '。', '\n## 集中度和组合骨架\n', '| 季度 | 申报市值 | 普通股/期权条数 | 前五权重 | 前十权重 | 普通股主动项 | 普通股价格项 |', '|---|---:|---:|---:|---:|---:|---:|']
    for q in reversed(qs):
        prev = quarters[quarters.index(q)-1]
        a,p = attribution(data,prev,q)
        n = sum(not k[2] for k in q['rows'])
        out.append(f"| {quarter(q['date'])} | {money(q['total'])} | {n}/{len(q['rows'])-n} | {sum(weight(q,k) for k in top(q,5)):.2f}% | {sum(weight(q,k) for k in top(q)):.2f}% | {money(a)} | {money(p)} |")
    out += ['\n## 重点标的季度轨迹\n','筛选包括最新季度全部证券、窗口内每季前十大，以及人工观察篮子 ADBE / KMX / DLTR / AMT / BAM / UBER。为保留期权历史，本页额外纳入全部历史 PUT/CALL。每格为「13F 占比 / 原始申报股数」，最新季度在左；`-` 表示该季度表中无此证券。']
    selected = set(latest['rows'])
    for q in qs:
        selected.update(top(q))
        selected.update(k for k,r in q['rows'].items() if k[2] or ticker(data,r) in {'ADBE','KMX','DLTR','AMT','BAM','UBER'})
    def sort_key(k):
        seen = max(i for i,q in enumerate(qs) if k in q['rows'])
        return (0,-latest['rows'][k]['value']) if k in latest['rows'] else (1,-seen,-qs[seen]['rows'][k]['value'])
    keys = sorted(selected,key=sort_key)
    for opt in (False,True):
        out += ['\n### '+('PUT/CALL' if opt else '普通证券')+'\n', '| 标的 | '+' | '.join(quarter(q['date']) for q in reversed(qs))+' |', '|---|'+'---:|'*len(qs)]
        for k in keys:
            if bool(k[2]) != opt: continue
            row = next(q['rows'][k] for q in reversed(qs) if k in q['rows'])
            cells = [f"{weight(q,k):.2f}% / {q['rows'][k]['shares']:,}" if k in q['rows'] else '-' for q in reversed(qs)]
            out.append('| '+label(data,row)+' | '+' | '.join(cells)+' |')
    out += ['\n## 逐季度解读\n','以下按股数和权重给行为命名，不用单季披露反推管理层动机。「显著」为股数变化至少 10%；同时列出小幅加股，避免漏掉缩表环境中的差异。']
    for q in reversed(qs):
        prev = quarters[quarters.index(q)-1]
        enter,leave=set(top(q))-set(top(prev)),set(top(prev))-set(top(q))
        out += [f'\n### {quarter(q["date"])}\n',f"总市值 {money(q['total'])}（{q['total']/prev['total']-1:+.1%}）；前十新进入："+('、'.join(ticker(data,q['rows'][k]) for k in sorted(enter)) or '无')+'；退出前十：'+('、'.join(ticker(data,prev['rows'][k]) for k in sorted(leave)) or '无')+'。', '| 标的 | 调整后股数变化 | 权重变化 | 行为 |','|---|---:|---:|---|']
        changes=[]
        for k in set(q['rows'])|set(prev['rows']):
            diff, rate=delta(data,prev,q,k)
            r=q['rows'].get(k) or prev['rows'][k]
            if rate is None: action='首次披露';pct='新增'
            elif k not in q['rows']: action='表中退出';pct='-100.0%'
            else:
                pct=f'{rate:+.2%}'
                action=('加股' if diff>0 else '减股' if diff<0 else '股数不变')+'、'+('权重升' if weight(q,k)>weight(prev,k) else '权重降' if weight(q,k)<weight(prev,k) else '权重持平')
            if rate is None or (rate and abs(rate)>=.1) or diff>0 or k in enter|leave:
                changes.append((max(weight(q,k),weight(prev,k)),f'| {label(data,r)} | {pct} | {weight(q,k)-weight(prev,k):+.2f} pp | {action} |'))
        out += [s for _,s in sorted(changes,reverse=True)] or ['| — | — | — | 无符合上述阈值变化 |']
        ordinary = {k for k in set(q['rows']) | set(prev['rows']) if not k[2]}
        increased = [k for k in ordinary if delta(data, prev, q, k)[0] > 0]
        decreased = [k for k in ordinary if delta(data, prev, q, k)[0] < 0]
        retained = len(set(top(q)) & set(top(prev)))
        a, p = attribution(data, prev, q)
        if a < 0 < p:
            summary = '减股与价格回升并存，不能把市值回升读成主动增持'
        elif a < 0 and p < 0:
            summary = '股数减少与价格下降叠加，需分别核对资本流动和估值/经营变化'
        else:
            summary = '按股数与价格分别观察组合变化'
        out.append(f'本季行为小结：普通股 {len(increased)} 项增股、{len(decreased)} 项减股；前十保留 {retained} 项。{summary}。这是披露端点的命名，尚不是资金流或卖出原因的解释。')
        ups=sorted(q['rows'],key=lambda k: weight(q,k)-weight(prev,k),reverse=True)[:2]
        downs=sorted(prev['rows'],key=lambda k: weight(q,k)-weight(prev,k))[:2]
        out.append('权重变化最大两端：'+ '；'.join(f"{ticker(data,q['rows'].get(k) or prev['rows'][k])} {weight(q,k)-weight(prev,k):+.2f} pp" for k in ups+downs)+'。权重变化仍须与上表股数对照。')
    out += ['\n## 用 Akre 的方法重新读\n','推断：与追逐季度赢家相比，这组数据更适合问「再投资假设还剩哪几条」。CSGP/NOW 的加股是新的研究优先入口；MA/MCO/BN 的核心位置是持续承保的资本配置判断；AMT 的小残仓则提示历史成功案例和今天的机会排序可以相距很远。', '不能把三条腿理解成永不卖出。机构当前大幅减少多项核心股数，正好要求核对管理层公开论点、估值与资本流动；单凭价值观宣言解释不了这些动作。', '\n## 最近一季可抄作业 / 趋势跟踪排序\n','这里排序的是研究任务。先检查真正加股，再结合现价重排：CSGP 优先；CPRT 为相对保留，MA 为历史核心；NOW 虽加股，但季末后涨幅超过 25%，下调到最后。跨机构比较参见 [[institutions/13F趋势-2026Q2]]：MA 的 Akre 减持与原有买入侧形成分歧，不应写成一致共识。', '| 优先级 | 标的/资产线 | 13F 证据 | 机构手法解释 | 13F 季末隐含价 | 当前价 | 13F 后涨幅 | 抄作业结论 | 下一步验证 |', '|---:|---|---|---|---:|---:|---:|---|---|']
    candidates=[('CSGP','地产数据与门户','优先核对新业务投入能否形成高回报增量资本','Homes.com 获客成本、续约、成熟业务现金是否被持续消耗'),('NOW','企业工作流','企业软件再投资，但 AI 收益需要证据','净新增合同、续费、AI 附加收入与股权稀释'),('CPRT','事故车拍卖','进入前十主要反映相对保留，不是新买入','拍卖量、场地利用率、保险全损率和扩场回报'),('MA','支付网络','长期核心仍在，但本季是减股','跨境量、费率、监管、回购价格与预期收益率')]
    # NOW has risen over 25% since quarter-end: demote the new-buy signal.
    candidates.sort(key=lambda c: ['CSGP', 'CPRT', 'MA', 'NOW'].index(c[0]))
    for rank,(t,theme,interpret,check) in enumerate(candidates,1):
        k=next(k for k,r in latest['rows'].items() if ticker(data,r)==t and not k[2]);r=latest['rows'][k]
        _,change=delta(data,previous,latest,k)
        anchor,p,move,verdict=price_cells(data,r,latest['date'])
        out.append(f'| {rank} | {t} / {theme} | 股数 {change:+.2%}；权重 {weight(latest,k):.2f}% | {interpret} | {anchor} | {p} | {move} | {verdict} | {check} |')
    timestamps=sorted({data['quotes'][t]['timestamp'] for t in ['CSGP','NOW','CPRT','MA','ORLY','V','BN','KKR','ABNB','AMT','BRK.B'] if data['quotes'].get(t,{}).get('price') is not None})
    out += ['\n行情抓取日 '+data['as_of']+'；价格截至（行情源时间，UTC）：'+(' / '.join(timestamps) if timestamps else 'N/A，Yahoo Chart 请求未取得可用报价')+'。采用 Yahoo Chart regularMarketPrice；不是投资人实际成交成本，也不是季末至今总回报。', '\n### 反向复盘\n', '| 标的 | 股数变化 | 季末隐含价 | 当前价 | 此后涨幅 | 待验证解释 |','|---|---:|---:|---:|---:|---|']
    for k in top(previous,len(previous['rows'])):
        r=previous['rows'][k]
        if k[2]:continue
        _,rate=delta(data,previous,latest,k)
        if rate is None or rate>-.1:continue
        row=latest['rows'].get(k) or r
        anchor,p,move,verdict=price_cells(data,row,latest['date'] if k in latest['rows'] else previous['date'])
        out.append(f'| {ticker(data,r)} | {rate:+.2%} | {anchor} | {p} | {move} | 缩表、估值纪律与论点变化均待核对；{verdict}，不可仅据后来涨跌判定卖早或卖对 |')
    out += ['\n## 继续观察与不能确认的部分\n','下一季先跟踪 CSGP/NOW 是否继续增股、ORLY/V 是否继续缩股，以及 MA 的核心权重是否靠被动收缩维持。当前基金相对指数的弱表现需要独立检查估值和企业竞争力；持有时间长并不能证明三条腿完好。', '本页没有用机构 AUM 或 ETF 净资产与 13F 总值相减来估算现金；这些统计对象、日期与证券范围不同。未取得现金流资料，不能归因为投资者赎回。CALL 的价值变化不并入普通股主动项。', '\n## 数据来源\n',f'- [SEC submissions]({data["submissions_url"]})；[[sources/Akre-13F-source-audit]]；[[raw/SEC｜Akre Capital Management：2022Q4至2026Q2持仓轨迹]]。', '- [[institutions/Akre Capital Management]]；[[investors/查克·阿克雷]]；[[concepts/再投资跑道]]。']
    for q in reversed(quarters):
        out.append('- '+quarter(q['date'])+'：'+'；'.join(f"[{f['form']} / {f['filingDate']}]({f['url']})" for f in q['filings']))
    out += ['- 拆股：'+'；'.join(f"[{s['ticker']}]({s['source']})" for s in data['splits'])]
    for t in ['CSGP','NOW','CPRT','MA','ORLY','V','BN','KKR','ABNB','AMT','BRK.B']:
        quote=data['quotes'].get(t,{})
        if quote.get('source'):out.append(f"- [{t} 行情]({quote['source']})："+(quote.get('timestamp') or 'N/A；'+quote.get('error','缺失')))
    return '\n'.join(out)+'\n'


def holdings_section(data, quarters):
    out=['## 13F 持仓（近四个季度）','', '本节为机构全部申报账户的公开证券切片，不能代替 Akre Focus ETF 的完整组合或净资产。权重以当季 13F 申报总值为分母。长线行为及完整期权表见 [[institutions/13F趋势-Akre]]。']
    for q in reversed(quarters[-4:]):
        out += ['',f"### {quarter(q['date'])} — {money(q['total'])}",'']
        for k in top(q):
            r=q['rows'][k];s=data['securities'][r['cusip']]
            out.append(f"- **{s['ticker']} / {s['name']}**：{s['description']}；{weight(q,k):.2f}%，{r['shares']:,} 股"+('（'+r['put_call']+' 对应标的股数）' if r['put_call'] else '')+'。')
    out+=['','变化摘要：2026Q2 CSGP/NOW 加股；MA、BN、KKR、ORLY、V 等减少股数。CPRT 进入前十但股数微降。CRM 正股与 CALL 独立披露，期权不是新加的普通股。\n']
    return '\n'.join(out)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault',type=Path,default=Path(os.environ.get('INVESTORS_VAULT', '/Users/zhangshihua/Desktop/investors/investors')))
    parser.add_argument('--data',type=Path)
    args=parser.parse_args()
    path=args.data or args.vault/'raw/data/akre-13f-20261012.json'
    data=json.loads(path.read_text())
    qs=resolve_filings(data)
    target=args.vault/'wiki/institutions/13F趋势-Akre.md'
    target.parent.mkdir(parents=True,exist_ok=True)
    target.write_text(render(data,qs))
    institution=args.vault/'wiki/institutions/Akre Capital Management.md'
    if institution.exists():
        body=institution.read_text()
        body,count=re.subn(r'## 13F 持仓（近四个季度）\n.*?(?=\n## 机构传承)',holdings_section(data,qs),body,flags=re.S)
        if count!=1:raise ValueError('Missing institution holdings section')
        institution.write_text(body)
    print(f'{target}: {len(qs)} quarters; latest {len(qs[-1]["rows"])} securities; ${qs[-1]["total"]:,}')

if __name__=='__main__':main()
