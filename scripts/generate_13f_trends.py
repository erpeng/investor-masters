#!/usr/bin/env python3
"""Fetch immutable SEC evidence and replay five institution trend pages.

Fetch uses a dated staging directory; freeze writes new raw snapshots only.
Rendering never needs network access or an untracked research checkout.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import re
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from zoneinfo import ZoneInfo

MANAGERS = {
    'berkshire': ('Berkshire', 'Berkshire Hathaway', 1067983),
    'himalaya': ('Himalaya', 'Himalaya Capital', 1709323),
    'hh': ('HH', 'H&H International Investment', 1759760),
    'duquesne': ('Duquesne', 'Duquesne Family Office', 1536411),
    'appaloosa': ('Appaloosa', 'Appaloosa Management', 1656456),
}
DEFAULT_VAULT = '/Users/zhangshihua/Desktop/investors/investors'
UA = 'Investment research, public SEC filings; contact research@example.com'


def request(url):
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': UA, 'Cache-Control': 'no-cache'})
            with urllib.request.urlopen(req, timeout=40) as response:
                return response.read()
        except Exception:
            if attempt == 2:
                raise
            time.sleep(attempt + 1)


def save_new(path, content):
    """Raw files may be reused byte-for-byte, never silently replaced."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != content:
            raise ValueError(f'Immutable evidence already exists: {path}')
    else:
        with path.open('xb') as out:
            out.write(content)


def json_bytes(data):
    return (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode()


def xml_value(root, tag):
    return next(((e.text or '').strip() for e in root.iter() if e.tag.split('}')[-1] == tag), '')


def parse_filing(content, metadata):
    text = content.decode('utf-8-sig')
    roots = [ET.fromstring(s.strip()) for s in re.findall(r'<XML>\s*(.*?)\s*</XML>', text, re.S | re.I)]
    cover = next(r for r in roots if xml_value(r, 'reportCalendarOrQuarter'))
    date = dt.datetime.strptime(xml_value(cover, 'reportCalendarOrQuarter'), '%m-%d-%Y').date().isoformat()
    if date != metadata['reportDate']:
        raise ValueError(f'Report date conflict: {metadata["accessionNumber"]}')
    rows = []
    for root in roots:
        for e in root.iter():
            if e.tag.split('}')[-1] != 'infoTable':
                continue
            rows.append({
                'issuer': xml_value(e, 'nameOfIssuer'), 'cusip': xml_value(e, 'cusip').upper(),
                'security_class': xml_value(e, 'titleOfClass'), 'put_call': xml_value(e, 'putCall').upper(),
                'share_type': xml_value(e, 'sshPrnamtType').upper(),
                'shares': int(xml_value(e, 'sshPrnamt')), 'value_raw': int(xml_value(e, 'value')),
            })
    count, total = int(xml_value(cover, 'tableEntryTotal')), int(xml_value(cover, 'tableValueTotal'))
    difference = sum(r['value_raw'] for r in rows) - total
    if len(rows) != count or abs(difference) > max(1, count / 2):
        raise ValueError(f'Cover mismatch: {metadata["accessionNumber"]}: {len(rows)}/{count}, {difference}')
    return dict(metadata, rows=rows, reported_count=count, reported_total_raw=total,
                cover_difference_raw=difference, schema_version=xml_value(cover, 'schemaVersion'),
                amendment_type=xml_value(cover, 'amendmentType').upper(),
                confidential_omitted=xml_value(cover, 'isConfidentialOmitted').lower() in ('true', 'y'),
                sha256=hashlib.sha256(content).hexdigest())


def fetch_manager(key, stage, cutoff):
    title, name, cik = MANAGERS[key]
    url = f'https://data.sec.gov/submissions/CIK{cik:010d}.json'
    content = request(url)
    submissions = json.loads(content)
    # Fresh submissions on each explicit fetch; immutable accession documents are reusable.
    (stage / f'{key}-submissions.json').write_bytes(content)
    recent = submissions['filings']['recent']
    items = []
    for i, form in enumerate(recent['form']):
        date = recent['reportDate'][i]
        if form in ('13F-HR', '13F-HR/A', '13F-NT', '13F-NT/A') and '2022-12-31' <= date <= cutoff:
            items.append({k: recent[k][i] for k in ('form', 'reportDate', 'filingDate', 'accessionNumber', 'acceptanceDateTime')})
    if not any(f['reportDate'] == '2022-12-31' for f in items):
        for archive in submissions['filings'].get('files', []):
            if archive['filingFrom'] > '2023-05-31' or archive['filingTo'] < '2023-01-01':
                continue
            old = json.loads(request('https://data.sec.gov/submissions/' + archive['name']))
            for i, form in enumerate(old['form']):
                date = old['reportDate'][i]
                if form.startswith('13F') and '2022-12-31' <= date <= cutoff:
                    items.append({k: old[k][i] for k in ('form', 'reportDate', 'filingDate', 'accessionNumber', 'acceptanceDateTime')})
    results = []
    for f in sorted({x['accessionNumber']: x for x in items}.values(), key=lambda x: (x['filingDate'], x['accessionNumber'])):
        acc = f['accessionNumber']
        f['url'] = f'https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace("-", "")}/{acc}.txt'
        file = stage / 'sec' / f'{acc}.txt'
        if not file.exists():
            save_new(file, request(f['url']))
            time.sleep(.12)
        f['fetched_at'] = dt.datetime.fromtimestamp(file.stat().st_mtime, dt.timezone.utc).isoformat()
        if f['form'].startswith('13F-NT'):
            results.append(dict(f, rows=[], notice=True))
        else:
            results.append(parse_filing(file.read_bytes(), f))
    data = {'institution': key, 'title': title, 'name': name, 'cik': cik, 'filings': results}
    (stage / f'{key}-fetched.json').write_bytes(json_bytes(data))
    print(key, len(results), 'filings', flush=True)
    return data


def normalized_class(row):
    # CUSIP fixes legal share class. Normalize documented spelling variants only.
    c = ' '.join(row['security_class'].upper().split())
    if row['cusip'] in ('722304102', '23306J309', '984245100'):
        return 'SPONSORED ADS'
    if row['cusip'] in ('Y95308105', '94352A104'):
        return 'ORDINARY SHARES'
    if row['cusip'] in ('512807108', '512807306'):
        return 'COM'
    if row['cusip'] in ('067901108', '06849F108'):
        return 'COM'
    if row['cusip'] in ('531229854', '531229755'):
        return 'COM LBTY ONE S C'
    if row['cusip'] in ('531229409', '531229813'):
        return 'COM LBTY SRM S A'
    if row['cusip'] in ('531229607', '531229789'):
        return 'COM LBTY SRM S C'
    if row['cusip'] in ('531229748', '530909100'):
        return 'COM SER A'
    if row['cusip'] in ('531229722', '530909308'):
        return 'COM SHS SER C'
    aliases = {'47215P106': 'SPON ADS CL A', '02376R102': 'COM',
               '81369Y605': 'FINANCIAL', '526057302': 'CL B'}
    if row['cusip'] in aliases:
        return aliases[row['cusip']]
    return c


def identity(row):
    cusip = {'Y95308105': '94352A104', '512807108': '512807306',
             '531229854': '531229755', '531229409': '531229813',
             '531229607': '531229789', '067901108': '06849F108',
             '531229748': '530909100', '531229722': '530909308'}.get(row['cusip'], row['cusip'])
    return (cusip, normalized_class(row), row['put_call'].strip().upper())


def aggregate(rows):
    out = {}
    for row in rows:
        key = identity(row)
        if key not in out:
            out[key] = dict(row)
        else:
            if row['share_type'] != out[key]['share_type']:
                raise ValueError(f'Incompatible share units: {key}')
            out[key]['shares'] += row['shares']
            out[key]['value'] += row['value']
    return out


def resolve_filings(data):
    periods = {}
    for filing in sorted(data['filings'], key=lambda f: (f['filingDate'], f['accessionNumber'])):
        if filing.get('notice'):
            continue  # Notice is not an empty holdings portfolio.
        date = filing['reportDate']
        rows = aggregate(filing['rows'])
        if filing['form'] == '13F-HR':
            if date in periods:
                raise ValueError(f'Duplicate original: {date}')
            periods[date] = {'date': date, 'rows': rows, 'filings': [filing]}
        else:
            if date not in periods:
                raise ValueError(f'Amendment without original: {date}')
            q = periods[date]
            kind = filing['amendment_type']
            if kind == 'RESTATEMENT':
                q['rows'] = rows
            elif kind == 'NEW HOLDINGS':
                for key, row in rows.items():
                    old = q['rows'].get(key)
                    if old and key[0] in filing.get('additive_overlap_cusips', []):
                        if old['share_type'] != row['share_type']:
                            raise ValueError(f'Conflicting amendment overlap: {key}')
                        # Explicitly reviewed additions only, never a general overlap heuristic.
                        row = dict(row, shares=old['shares'] + row['shares'], value=old['value'] + row['value'])
                    elif old and any(old[k] != row[k] for k in ('shares', 'value', 'share_type')):
                        raise ValueError(f'Conflicting amendment overlap: {key}')
                    q['rows'][key] = row
            else:
                raise ValueError(f'Unknown amendment: {kind}')
            q['filings'].append(filing)
    for q in periods.values():
        q['total'] = sum(r['value'] for r in q['rows'].values())
    return sorted(periods.values(), key=lambda q: q['date'])


def quarter(date):
    return f'{date[:4]}Q{(int(date[5:7]) - 1) // 3 + 1}'


def security(data, row):
    return data['securities'].get(row['cusip'], {'ticker': '', 'name': row['issuer']})


def label(data, row):
    s = security(data, row)
    name = f"{s['ticker']}（{s['name']}）" if s.get('ticker') else row['issuer']
    if re.search(r'\b(?:ADR|ADS)\b', row['security_class'], re.I):
        name += ' [ADR/ADS]'
    elif re.search(r'(?:N ?Y|NEW YORK).*REG', row['security_class'], re.I):
        name += ' [纽约登记股]'
    elif re.search(r'\b(?:ISHARES|SPDR|INVESCO|VANECK|PROSHARES|DIREXION|ETF)\b|EXCHANGE TRADED', row.get('issuer',''), re.I):
        name += ' [ETF]'
    return name + (f" {row['put_call']}" if row['put_call'] else '')


def ticker_alias(ticker):
    return {'BRK.B': 'BRK-B', 'LEN.B': 'LEN-B', 'BF.B': 'BF-B'}.get(ticker, ticker)


def matches_ticker(data, row, ticker):
    # BSP is an internal editorial key, not an asserted exchange ticker.
    if ticker == 'BSP':
        return row['cusip'] == 'T19377109'
    return ticker_alias(security(data, row).get('ticker', '')) == ticker_alias(ticker)


def special_disclosure(row):
    return row['cusip'] in ('T19377109', '84615Q103')


def split_factor(data, row, start, end):
    ticker = security(data, row).get('ticker')
    return math.prod(s['ratio'] for s in data.get('splits', []) if s['ticker'] == ticker and start < s['date'] <= end)


def conversion(data, prev, curr):
    """Reviewed many-to-one Sirius exchange; preserve separate raw trajectory rows.

    SEC 8-K12B, 2024-09-09:
    https://www.sec.gov/Archives/edgar/data/908937/000110465924098260/tm2423473d2_8k12b.htm
    Fractional-share cash and intra-quarter timing are not reconstructed.
    """
    if data.get('institution') != 'berkshire' or (prev['date'],curr['date']) != ('2024-06-30','2024-09-30'):
        return None
    ratios = {'82968B103': .1, '531229813': .8375, '531229789': .8375}
    sources = {k for k in prev['rows'] if k[0] in ratios and not k[2]}
    target = next((k for k in curr['rows'] if k[0]=='829933100' and not k[2]), None)
    if len(sources) != 3 or target is None or target in prev['rows']:
        raise ValueError('Reviewed Sirius exchange no longer matches the source evidence')
    return {'sources':sources, 'target':target,
            'shares':sum(prev['rows'][k]['shares']*ratios[k[0]] for k in sources),
            'value':sum(prev['rows'][k]['value'] for k in sources)}


def change(data, prev, curr, key):
    exchange = conversion(data,prev,curr)
    if exchange and key == exchange['target']:
        q0,q1=exchange['shares'],curr['rows'][key]['shares']
        return q1-q0,q1/q0-1
    if exchange and key in exchange['sources']:
        return 0,0  # Exchanged into target; not an ordinary disposal.
    old, new = prev['rows'].get(key), curr['rows'].get(key)
    q0 = old['shares'] * split_factor(data, old, prev['date'], curr['date']) if old else 0
    q1 = new['shares'] if new else 0
    return q1 - q0, q1 / q0 - 1 if q0 else None


def attribution(data, prev, curr, options=False):
    active = price = 0.
    exchange = conversion(data,prev,curr) if not options else None
    skip = set()
    if exchange:
        new=curr['rows'][exchange['target']]
        p0=exchange['value']/exchange['shares']
        active+=(new['shares']-exchange['shares'])*p0
        price+=new['value']-new['shares']*p0
        skip=exchange['sources']|{exchange['target']}
    for key in sorted(set(prev['rows']) | set(curr['rows'])):
        if bool(key[2]) != options or key in skip:
            continue
        old, new = prev['rows'].get(key), curr['rows'].get(key)
        if not old:
            active += new['value']
        elif not new:
            active -= old['value']
        elif old['shares']:
            q0 = old['shares'] * split_factor(data, old, prev['date'], curr['date'])
            p0 = old['value'] / q0
            active += (new['shares'] - q0) * p0
            price += new['value'] - new['shares'] * p0
        else:
            active += new['value'] - old['value']
    return active, price


def top(q, n=10):
    return sorted(q['rows'], key=lambda k: q['rows'][k]['value'], reverse=True)[:n]


def weight(q, key):
    return q['rows'].get(key, {}).get('value', 0) / q['total'] * 100


def fetch_chart(symbol, start, end):
    p1 = int(dt.datetime.fromisoformat(start).replace(tzinfo=dt.timezone.utc).timestamp())
    p2 = int((dt.datetime.fromisoformat(end) + dt.timedelta(days=1)).replace(tzinfo=dt.timezone.utc).timestamp())
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?period1={p1}&period2={p2}&interval=1d&events=splits'
    obj = json.loads(request(url))['chart']['result'][0]
    meta = obj['meta']
    if meta.get('currency') != 'USD' or meta.get('symbol') != symbol:
        raise ValueError('Quote currency/symbol mismatch')
    dates = [dt.datetime.fromtimestamp(t, ZoneInfo(meta['exchangeTimezoneName'])).date().isoformat() for t in obj.get('timestamp', [])]
    close = obj['indicators']['quote'][0]['close']
    history = {d: p for d, p in zip(dates, close) if p and math.isfinite(p) and d <= end}
    last = max(history)
    splits = [{'date': dt.datetime.fromtimestamp(v['date'], ZoneInfo(meta['exchangeTimezoneName'])).date().isoformat(),
               'ratio': v['numerator'] / v['denominator']} for v in obj.get('events', {}).get('splits', {}).values()]
    return {'price': history[last], 'price_date': last, 'currency': 'USD', 'source': url,
            'fetched_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'name': meta.get('longName', ''),
            'daily_closes': history, 'splits': splits}


def money(value):
    return f'${value / 1e9:.3f}bn'


def price_cells(data, row, anchor_date):
    ticker = security(data, row).get('ticker', '')
    if row['put_call'] or row['share_type'] != 'SH' or special_disclosure(row):
        return ('单列工具/披露核验', 'N/A', 'N/A', '不直接用该申报隐含价判断可复制性')
    if not row['shares']:
        return ('N/A', 'N/A', 'N/A', '缺少可用股数')
    anchor = row['value'] / row['shares'] / split_factor(data, row, anchor_date, data['as_of'])
    quote = data.get('quotes', {}).get(ticker, {})
    p = quote.get('price')
    if not p or quote.get('currency') != 'USD':
        return (f'${anchor:.2f}', 'N/A', 'N/A', '行情缺失，不能判断追涨程度')
    if not quote.get('price_date') or not 0 <= (dt.date.fromisoformat(data['as_of']) - dt.date.fromisoformat(quote['price_date'])).days <= 4:
        return (f'${anchor:.2f}', 'N/A', 'N/A', '行情过期，暂不判断追涨程度')
    move = p / anchor - 1
    if move > .5:
        verdict = '仅复盘/等待，已大幅脱离季末价格'
    elif move > .25:
        verdict = '降低优先级，需盈利或趋势继续上修'
    elif move > .1:
        verdict = '需更强经营证据与估值约束'
    elif move < 0:
        verdict = '下跌不证明便宜，先核对经营论点'
    else:
        verdict = '价格未明显阻碍，仍需经营与估值验证'
    return (f'${anchor:.2f}', f'${p:.2f}（{quote.get("price_date", "时间缺失")}）', f'{move:+.1%}', verdict)


def selected_keys(data, quarters):
    selected = set(quarters[-1]['rows'])
    for q in quarters[1:]:
        selected.update(top(q))
        selected.update(k for k in q['rows'] if k[2])
    # Preserve the existing manually chosen research basket when present in evidence.
    watch = set(data.get('editorial', {}).get('watch', []))
    for q in quarters:
        selected.update(k for k, row in q['rows'].items() if ticker_alias(security(data, row).get('ticker')) in {ticker_alias(t) for t in watch})
    return selected


def format_change(data, prev, curr, key):
    diff, rate = change(data, prev, curr, key)
    exchange=conversion(data,prev,curr)
    if exchange and key==exchange['target']:
        return f'换股后约{rate:+.2%}'
    if exchange and key in exchange['sources']:
        return '换股转出'
    if key not in prev['rows']:
        return '首次列示'
    if key not in curr['rows']:
        return '不再列示'
    return f'{rate:+.2%}' if rate is not None else '基期为零'


def render(data, quarters):
    latest, previous = quarters[-1], quarters[-2]
    shown = [q for q in quarters if q['date'] >= '2023-01-01']
    editorial = data['editorial']
    active, market = attribution(data, previous, latest)
    oa, op = attribution(data, previous, latest, True)
    qname = quarter(latest['date'])
    title = 'H&H' if data['title'] == 'HH' else data['title']
    out = [f'---\ntype: institution-13f-single-trend\nstatus: active\nupdated: {data["as_of"]}\nlatest_quarter: {qname}\ninstitution: {data["name"]}\n---\n',
           f'# 13F趋势-{title}\n',
           f'核验日期：{data["as_of"]}。最新报告期：{latest["date"]}；最新相关申报日：{latest["filings"][-1]["filingDate"]}。SEC CIK：{data["cik"]}。',
           f'\n机构背景见 [[institutions/{data["name"]}]]；本季五家横向对照见 [[institutions/13F趋势-{qname}]]。',
           '\n## 结论先行\n', editorial['summary'],
           f'\n最新信息表标准化加总 {money(latest["total"])}，较上季 {latest["total"] / previous["total"] - 1:+.2%}；普通证券股数项 {money(active)}、价格项 {money(market)}。期权另列股数项 {money(oa)}、价格项 {money(op)}。这些是季度端点分解，不是投资收益或实际买卖现金额。',
           '\n## 数据口径\n',
           '- 展示2023Q1起的季度，保留2022Q4基期；原始申报、修订、封面值、逐行值和SHA256独立归档。日期按报告期归属，不按上传日期误归季度。',
           '- CUSIP与证券类别识别股份，PUT/CALL独立。ticker仅供展示；同股不同类别不合并股数，公司级讨论另行合并权重。',
           '- 权重分母采用信息表全部标准化value加总，含期权对应标的名义值，并非机构净资产。ETF、ADR及期权不能等同普通股票；期权股数为对应标的股数，不是合约张数。',
           '- 主动项＝（本季股数－已核实拆股调整后基期股数）×基期隐含价；新列示按本季值，退出按上季值。价格项补足剩余变化；首次列示与公司行动不自动等于二级市场买入。',
           '- 价格项还可能包含分拆分派等公司行动造成的估值变化，不是纯市场涨跌或总回报；母公司分拆不调整其持股数。',
           '- 股数项是机械端点估算，也可能含实物分派或重组获得的股份。例如Liberty分派的Live股份首次列示，不能解释为同金额的主动买入。',
           '- 拆股核验覆盖研究候选、历史前十与相邻期隐含价异常的标的；尚未逐一核验的小仓位列在来源审计中，历史股数项仍需结合公司行动复核。',
           '- 行情仅用于季末之后的价格过滤，写明价格日；获取失败为N/A，不补零。价格上涨不倒推加仓动机。',
           '- 13F缺少现金、空头、绝大多数非美证券与完整衍生品；无法据此判断申赎、真实成交价或今天的持仓。']
    out += ['- ' + n for n in editorial.get('notes', [])]
    if data['institution']=='berkshire':
        out += ['- 2024Q3 Sirius三合一换股：旧SIRI按0.1、LSXMA/LSXMK按0.8375折为新SIRI，先合并基期等值股数和申报值再分解；未还原零股现金与交易时点，不能把新CUSIP全额视为买入。2025Q4 Liberty Live A/C股1:1换号保留连续轨迹。证据见来源审计的冻结后补核附录。']
    unresolved = data.get('audit', {}).get('unresolved_splits', [])
    if unresolved:
        out += ['- 待核公司行动：' + '；'.join(map(str, unresolved)) + '；相关历史股数变化仅作原始申报比较。']
    out += ['\n### 金额与修订审计\n', '| 报告期 | 申报 | 原始封面值 | 标准化倍率 | 原始行和减封面 | 类型 |', '|---|---|---:|---:|---:|---|']
    for f in reversed(data['filings']):
        if f.get('notice'):
            out.append(f'| {quarter(f["reportDate"])} | [{f["accessionNumber"]}]({f["url"]}) | — | — | — | 13F-NT通知，不当清仓 |')
            continue
        out.append(f'| {quarter(f["reportDate"])} | [{f["accessionNumber"]}]({f["url"]}) | {f["reported_total_raw"]:,} | {f["unit_multiplier"]:g} | {f["cover_difference_raw"]:+,} | {f.get("amendment_type") or "原报"} |')
    out += ['\n金额倍率依据及拆股/换号原文见来源审计；差额保留，不改原值凑平。',
            '\n## 集中度和组合骨架\n', '| 季度 | 申报行和 | 非期权/期权项 | 前五证券 | 前十证券 | 普通证券股数项 | 普通证券价格项 |', '|---|---:|---:|---:|---:|---:|---:|']
    for q in reversed(shown):
        prev = quarters[quarters.index(q) - 1]
        a, p = attribution(data, prev, q)
        ordinary = sum(not k[2] for k in q['rows'])
        out.append(f'| {quarter(q["date"])} | {money(q["total"])} | {ordinary}/{len(q["rows"]) - ordinary} | {sum(weight(q,k) for k in top(q,5)):.2f}% | {sum(weight(q,k) for k in top(q)):.2f}% | {money(a)} | {money(p)} |')
    out += ['\n前五/前十按证券类别计算；Alphabet的A/C股在此分开。小数由未取整值计算。',
            f'\n## {qname}主要持仓与变化\n', '| 标的 | Q2原始股数/份额 | Q3原始股数/份额 | 调整后变化 | Q3占比 | 权重变化 |', '|---|---:|---:|---:|---:|---:|']
    allkeys = set(latest['rows']) | set(previous['rows'])
    order = sorted(allkeys, key=lambda k: (-max(weight(latest, k), weight(previous, k)), k))
    for key in order:
        diff, rate = change(data, previous, latest, key)
        if not diff and key not in top(latest):
            continue
        row = latest['rows'].get(key) or previous['rows'][key]
        old = previous['rows'].get(key, {}).get('shares', 0)
        new = latest['rows'].get(key, {}).get('shares', 0)
        out.append(f'| {label(data,row)} | {old:,} | {new:,} | {format_change(data,previous,latest,key)} | {weight(latest,key):.2f}% | {weight(latest,key)-weight(previous,key):+.2f} pp |')
    out += ['\n## 重点标的季度轨迹\n',
            '纳入最新季度全部证券、历史各季前十大、既有观察篮子及全部历史期权。最新持仓按市值排序，历史退出标的随后；不设最新小仓位门槛。每格为「13F占比 / 原始股数或份额」，最新季度在左，未列示为“-”。']
    selected = selected_keys(data, quarters)
    def sort_key(key):
        if key in latest['rows']:
            return (0, -latest['rows'][key]['value'], str(key))
        last = max(q['date'] for q in quarters if key in q['rows'])
        return (1, -int(last.replace('-', '')), str(key))
    ordered = sorted(selected, key=sort_key)
    for options in (False, True):
        out += ['\n### ' + ('PUT/CALL工具' if options else '普通证券与非期权工具') + '\n',
                '| 标的 | ' + ' | '.join(quarter(q['date']) for q in reversed(shown)) + ' |',
                '|---|' + '---:|' * len(shown)]
        for key in ordered:
            if bool(key[2]) != options:
                continue
            row = next(q['rows'][key] for q in reversed(quarters) if key in q['rows'])
            cells = [f'{weight(q,key):.2f}% / {q["rows"][key]["shares"]:,}' if key in q['rows'] else '-' for q in reversed(shown)]
            out.append('| ' + label(data,row) + ' | ' + ' | '.join(cells) + ' |')
        if not any(bool(k[2]) == options for k in ordered):
            out.append('\n该窗口无此类披露。')
    out += ['\n## 逐季度行为解读\n', '股数动作与价格效应分开；以下只描述可观察行为，不代写管理者动机。']
    for q in reversed(shown):
        p = quarters[quarters.index(q) - 1]
        union = set(q['rows']) | set(p['rows'])
        added = [k for k in union if not k[2] and k in q['rows'] and k in p['rows'] and change(data,p,q,k)[0] > 0]
        reduced = [k for k in union if not k[2] and k in q['rows'] and k in p['rows'] and change(data,p,q,k)[0] < 0]
        entered = [k for k in q['rows'] if not k[2] and k not in p['rows']]
        exited = [k for k in p['rows'] if not k[2] and k not in q['rows']]
        out += [f'\n### {quarter(q["date"])}\n',
                f'非期权证券：新列示{len(entered)}项、增股{len(added)}项、减股{len(reduced)}项、不再列示{len(exited)}项。']
        exchange=conversion(data,p,q)
        if exchange:
            out.append(f'- 本季含Sirius多证券换股：基期折合约{exchange["shares"]:,.2f}股，新SIRI {q["rows"][exchange["target"]]["shares"]:,}股，换股后端点净增约{change(data,p,q,exchange["target"])[1]:.2%}；三项转出和一项新列示均含公司行动。')
        for heading, keys in [('新进前十', set(top(q)) - set(top(p))), ('退出前十', set(top(p)) - set(top(q)))]:
            names = [label(data, q['rows'].get(k) or p['rows'][k]) for k in sorted(keys, key=lambda k: (-max(weight(q,k),weight(p,k)),k))]
            out.append(f'- {heading}：' + ('、'.join(names) or '无') + '；前十名次变化不等于买卖。')
        for heading, keys in [('主要增股/新列示', added + entered), ('主要减股/不再列示', reduced + exited)]:
            keys = sorted(keys, key=lambda k: (-max(weight(q,k), weight(p,k)),k))[:6]
            bits = []
            for k in keys:
                row = q['rows'].get(k) or p['rows'][k]
                bits.append(f'{label(data,row)} {format_change(data,p,q,k)}')
            out.append(f'- {heading}：' + ('；'.join(bits) or '无') + '。')
        a, pr = attribution(data,p,q)
        out.append(f'- 普通证券股数项{money(a)}、价格项{money(pr)}；总市值变化不能直接解释为收益或资金流。')
    out += ['\n## 用机构方法重新读\n', editorial['method']]
    if editorial.get('legacy_method'):
        out += ['\n### 既有方法分析\n', '以下保留此前的方法讨论；最新季度数字以本页重核数据为准。\n', editorial['legacy_method']]
    out += ['\n## 最近一季可抄作业 / 趋势跟踪排序\n',
            '这是有顺序的研究候选，不是买入指令。先按机构方法与本季股数动作选出观察顺序，再按季末后涨幅分层：≤10%、10%–25%、25%–50%、>50%；行情缺失或过期放在第三层待核，同层保留观察顺序。此排序为研究启发式，并非回测过的交易规则；下跌不等于便宜。报价使用所列日期纽约常规交易时段收盘价。IPO及披露估值口径不稳定的证券单列观察。',
            '| 优先级 | 标的/资产线 | 13F证据 | 方法解释 | 季末隐含价 | 核验收盘价 | 季末后涨幅 | 研究结论 | 下一步验证 |',
            '|---:|---|---|---|---:|---:|---:|---|---|']
    ranked, special = [], []
    for base_rank, ticker in enumerate(editorial['candidates']):
        key = next((k for k,r in latest['rows'].items() if not k[2] and matches_ticker(data,r,ticker)), None)
        if key is not None and special_disclosure(latest['rows'][key]):
            special.append((ticker,key))
            continue
        layer = 2
        if key is not None:
            anchor, current, move, verdict = price_cells(data,latest['rows'][key],latest['date'])
            if move != 'N/A':
                row=latest['rows'][key]
                nominal_anchor=row['value']/row['shares']/split_factor(data,row,latest['date'],data['as_of'])
                move_value=data['quotes'][security(data,row)['ticker']]['price']/nominal_anchor-1
                layer = 3 if move_value > .5 else 2 if move_value > .25 else 1 if move_value > .1 else 0
        ranked.append((layer,base_rank,ticker,key))
    for index, (_, _, ticker, key) in enumerate(sorted(ranked), 1):
        if key is None:
            out.append(f'| {index} | {ticker} | 证券映射待核 | 暂不排名 | N/A | N/A | N/A | 不补造映射 | 核对CUSIP与发行文件 |')
            continue
        row = latest['rows'][key]
        anchor, current, move, verdict = price_cells(data, row, latest['date'])
        method = '长期核心的增量研究' if data['institution'] in ('berkshire','himalaya','hh') else '条件性趋势/相对机会成本'
        out.append(f'| {index} | {label(data,row)} | {format_change(data,previous,latest,key)}；{weight(latest,key):.2f}% | {method} | {anchor} | {current} | {move} | {verdict} | {editorial["next_checks"].get(ticker,"核对经营与估值")} |')
    if special:
        out += ['\n### IPO及特殊披露观察\n', '| 发行人 | 13F证据 | 后续核验 |', '|---|---|---|']
        for ticker,key in special:
            row = latest['rows'][key]
            out.append(f'| {label(data,row)} | {format_change(data,previous,latest,key)}；{weight(latest,key):.2f}% | {editorial["next_checks"].get(ticker,"核对发行文件和持仓形成路径")}；本栏不按申报隐含价计算可复制排序 |')
    out += ['\n### 反向复盘\n']
    if not editorial['reverse']:
        out.append('本季没有减股或退出；不制造卖出侧结论。继续观察原有核心是否维持，而非把权重自然下降当作卖出。')
    else:
        out += ['| 标的 | 当季动作 | 价格锚日期 | 隐含价 | 核验收盘价 | 此后涨幅 | 待验证 |', '|---|---|---|---:|---:|---:|---|']
        for ticker in editorial['reverse']:
            key = next((k for k in order if not k[2] and matches_ticker(data, latest['rows'].get(k) or previous['rows'][k],ticker)), None)
            if key is None:
                continue
            row = latest['rows'].get(key) or previous['rows'][key]
            date = latest['date'] if key in latest['rows'] else previous['date']
            anchor, current, move, _ = price_cells(data,row,date)
            out.append(f'| {label(data,row)} | {format_change(data,previous,latest,key)} | {date} | {anchor} | {current} | {move} | 区分估值纪律、机会成本与经营变化；后续上涨不证明当时判断错误 |')
    out += ['\n## 继续观察\n',
            '- 下一季股数是否延续，新增是否成为核心、减股是否继续。',
            '- 同一标的在不同机构中承担的角色是否不同，不能把交易型与长期集中型同权解释。',
            '- 当前经营证据与资本开支、现金流、竞争变化是否支持原有研究问题。',
            '\n## 数据来源\n',
            f'- [[raw/SEC｜{data["title"]}：2022Q4至2026Q3持仓轨迹]]',
            f'- [[sources/{data["title"]}-13f-source-audit]]',
            f'- [SEC实时申报列表](https://data.sec.gov/submissions/CIK{data["cik"]:010d}.json)',
            '- 各季度SEC原文链接见上方金额审计表；原始值与标准化依据均保留在冻结快照中。']
    for ticker, quote in sorted(data.get('quotes', {}).items()):
        if ticker in ('BSP', 'SPCX'):
            continue
        if ticker_alias(ticker) not in {ticker_alias(t) for t in editorial['candidates'] + editorial['reverse']}:
            continue
        out.append(f'- {ticker}：[行情来源]({quote.get("source", "https://finance.yahoo.com/")})；价格日{quote.get("price_date") or "N/A"}；抓取{quote.get("fetched_at") or "N/A"}；' + (f'失败原因：{quote.get("error")}' if not quote.get('price') else 'USD收盘价。'))
    return '\n'.join(out) + '\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['fetch', 'render'])
    parser.add_argument('--vault', default=DEFAULT_VAULT)
    parser.add_argument('--institutions', default=','.join(MANAGERS))
    parser.add_argument('--quarter', default='2026Q3')
    parser.add_argument('--as-of', default='2026-11-17')
    parser.add_argument('--stage', default='/tmp/investors-13f-20261117')
    parser.add_argument('--snapshot-dir')
    args = parser.parse_args()
    keys = args.institutions.split(',')
    if any(k not in MANAGERS for k in keys):
        parser.error('Unknown institution')
    if args.action == 'fetch':
        import calendar
        year, q = int(args.quarter[:4]), int(args.quarter[-1])
        cutoff = dt.date(year, q * 3, calendar.monthrange(year, q * 3)[1]).isoformat()
        stage = Path(args.stage)
        stage.mkdir(parents=True, exist_ok=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(lambda k: fetch_manager(k, stage, cutoff), keys))
    else:
        directory = Path(args.snapshot_dir or Path(args.vault) / 'raw/data' / ('13f-' + args.as_of.replace('-', '')))
        for key in keys:
            data = json.loads((directory / f'{key}.json').read_text())
            quarters = resolve_filings(data)
            output = Path(args.vault) / 'wiki/institutions' / f'13F趋势-{data["title"]}.md'
            output.write_text(render(data, quarters), encoding='utf-8')
            print(output)


if __name__ == '__main__':
    main()
