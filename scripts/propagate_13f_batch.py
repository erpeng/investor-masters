#!/usr/bin/env python3
"""Publish a selected frozen 13F batch, preserving raw evidence and existing prose."""
import argparse
import json
import re
from pathlib import Path
import generate_13f_trends as g
import update_13f_institutions as u
import propagate_13f_batch3 as legacy

ROOT = Path(__file__).resolve().parents[1]


def selected_companies(data, previous, current):
    selected = legacy.selection(data, previous, current)
    eligible = set()
    for row in list(previous['rows'].values()) + list(current['rows'].values()):
        ticker = g.security(data, row).get('ticker')
        if ticker and not row['put_call'] and u.category(row, ticker, data) == '普通股票':
            eligible.add(ticker)
    return selected & eligible


def raw_card(data, periods, relative, label):
    text = legacy.raw_card(data, periods)
    return text.replace('raw/data/13f-20261117-batch3/', relative.rstrip('/') + '/').replace('第三批机构公开行为', label + '机构公开行为')


def audit_body(data, names, relative, count):
    text = legacy.audit_body(data, names)
    text = text.replace('raw/data/13f-20261117-batch3/', relative.rstrip('/') + '/')
    text = text.replace('15家', f'{count}家')
    text = text.replace('不扩写人物页。Akre当前行为归于对应管理时期，Harris申报也不归为单一经理个人交易。',
                        '不扩写人物页。机构公开持仓只用于行为比较，不归因为创始人个人决策，也不补造动机。')
    if data.get('noncomparable_intervals'):
        text += '\n### 申报主体边界\n\n' + '\n'.join('- ' + x['reason'] + f' [原文]({x["source"]})' for x in data['noncomparable_intervals']) + '\n'
    if data.get('class_identity_issues'):
        text += '\n### 未合并的证券类别\n\n同CUSIP下出现经济属性冲突或权证期限不一致时，保留原始独立类别；跨类别迁移不作交易方向判断，同类连续股数仍可比较。\n'
        text += '\n'.join('- ' + x['cusip'] + ' ' + (x['put_call'] or '非期权') + ' / ' + x['share_type'] + '：' + '、'.join(x['classes']) for x in data['class_identity_issues']) + '\n'
    return text


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault', default=g.DEFAULT_VAULT)
    parser.add_argument('--batch-manifest', default=str(ROOT/'scripts/data/13f-2026q3-batches.json'))
    parser.add_argument('--batch-id', default='fourth-eight')
    parser.add_argument('--catalog', default=str(ROOT/'scripts/data/13f-2026q3-propagation.json'))
    args = parser.parse_args()
    vault = Path(args.vault); wiki = vault/'wiki'
    manifest = json.loads(Path(args.batch_manifest).read_text())
    batch = next(b for b in manifest['batches'] if b['id'] == args.batch_id)
    relative = batch['snapshot_dir']; snapshot = vault/relative
    label = batch.get('label', {'third-five':'第三批', 'fourth-eight':'第四批'}.get(args.batch_id, args.batch_id))
    catalog = json.loads(Path(args.catalog).read_text()) if Path(args.catalog).exists() else {}
    companies = dict(legacy.COMPANIES, **catalog.get('companies', {}))
    descriptions = dict(legacy.EXTRA_DESCRIPTIONS, **catalog.get('descriptions', {}))
    descriptions.update({ticker: item[1] for ticker, item in catalog.get('business', {}).items()})
    count = len(manifest['horizontal_keys']); prepared = []; missing = set()
    for key in batch['institutions']:
        data = json.loads((snapshot/f'{key}.json').read_text()); periods = g.resolve_filings(data)
        previous, current = periods[-2:]
        selected = selected_companies(data, previous, current)
        missing.update(selected - companies.keys())
        prepared.append((key, data, periods, previous, current, selected))
    if missing:
        raise ValueError('Unreviewed company names: ' + ', '.join(sorted(missing)))
    for _, _, _, _, _, selected in prepared:
        for ticker in selected:
            if not (wiki/'companies'/f'{companies[ticker]}.md').exists() and not u.DESC.get(ticker, ('', descriptions.get(ticker, '')))[1]:
                raise ValueError('Missing business description: ' + ticker)
    # Preflight all immutable source cards before any publication writes.
    for _, data, periods, _, _, _ in prepared:
        path = vault/'raw'/f'SEC｜{data["title"]}：2022Q4至2026Q3持仓轨迹.md'
        content = raw_card(data, periods, relative, label).encode()
        if path.exists() and path.read_bytes() != content:
            raise ValueError('Immutable evidence already exists: ' + str(path))
    affected = set(); created = []; obligations = {}
    for key, data, periods, previous, current, selected in prepared:
        names = {companies[t] for t in selected}; obligations[key] = sorted(names)
        for name in sorted(names):
            tickers = {t for t in selected if companies[t] == name}
            path = wiki/'companies'/f'{name}.md'
            if not path.exists():
                ticker = sorted(tickers)[0]; desc = u.DESC.get(ticker, ('', descriptions.get(ticker, '')))[1]
                path.write_text(f'---\ntype: company\nstatus: seed\nupdated: {manifest["as_of"]}\n---\n\n# {name}\n\n## 简介\n\n{desc}。本页由2026Q3机构持仓引出研究问题，尚非独立估值报告。\n\n## 公司点评\n\n## 相关页面\n\n## 主要来源\n')
                created.append(name)
            text = legacy.upsert(path.read_text(), f'13f-2026q3-{key}', legacy.company_block(data, previous, current, tickers), '## 公司点评\n')
            text = legacy.upsert(text, f'13f-2026q3-{key}-links', f'- [[institutions/{data["name"]}]]；[[institutions/13F趋势-{data["title"]}]]；[[institutions/13F趋势-2026Q3]]', '## 相关页面\n')
            text = legacy.upsert(text, f'13f-2026q3-{key}-sources', f'- [[raw/SEC｜{data["title"]}：2022Q4至2026Q3持仓轨迹]]；[[sources/{g.audit_name(data)}]]', '## 主要来源\n')
            path.write_text(re.sub(r'^updated:.*$', 'updated: '+manifest['as_of'], text, count=1, flags=re.M)); affected.add(name)
        g.save_new(vault/'raw'/f'SEC｜{data["title"]}：2022Q4至2026Q3持仓轨迹.md', raw_card(data, periods, relative, label).encode())
        audit = wiki/'sources'/f'{g.audit_name(data)}.md'
        body = audit_body(data, names, relative, count)
        if key == 'akre':
            body = '## 2026Q3 第三批更新\n\n' + re.sub(r'^(#{2,3}) ', lambda m:'#'+m[0], body, flags=re.M)
            audit.write_text(legacy.upsert(audit.read_text(), '13f-2026q3-third-batch-audit', body))
        else:
            audit.write_text(f'---\ntype: source-audit\nstatus: active\nupdated: {manifest["as_of"]}\n---\n\n# {g.audit_name(data)}\n\n'+body)
    index = wiki/'companies/index.md'
    body = f'### {label}机构的研究入口\n\n' + '\n'.join(f'- [[companies/{n}]]' for n in sorted(affected))
    index.write_text(legacy.upsert(index.read_text(), f'13f-2026q3-{args.batch_id}-company-index', body, '## 2026Q3：先看持仓分歧，再看新增线索\n'))
    registry = wiki/'sources/来源总表.md'
    cards = '\n'.join(f'- [[raw/SEC｜{d["title"]}：2022Q4至2026Q3持仓轨迹]]；[[sources/{g.audit_name(d)}]]。' for _,d,*_ in prepared)
    text = legacy.upsert(registry.read_text(), f'13f-2026q3-{args.batch_id}-sources', f'## 2026Q3 {label}：{len(prepared)}家机构\n\n'+cards)
    registered = {n.removesuffix('.md') for n in re.findall(r'\[\[raw/([^]|]+)', text)}
    source_count = len(registered)
    text = re.sub(r'^source_count: \d+$', f'source_count: {source_count}', text, flags=re.M)
    text = re.sub(r'当前注册 \d+ 篇[^\n]*', f'当前注册 {source_count} 篇 Markdown 来源，按本页已登记的 raw 文章去重计数；结构化 SEC、报价及附件不重复计作文章。', text)
    registry.write_text(text)
    home = wiki/'index.md'; text = home.read_text()
    text = re.sub(r'^source_count: \d+$', f'source_count: {source_count}', text, flags=re.M)
    text = re.sub(r'2026Q3 十五家机构横向对照（15/23，余8家）', f'2026Q3 {count}家机构横向对照（{count}/23）', text)
    home.write_text(text)
    entry = wiki/'institutions/13F趋势.md'; text = entry.read_text()
    start = text.index('最新增量：'); end = text.index('## 趋势解读')
    pending = [k for k in g.ALL_MANAGERS if k not in manifest['horizontal_keys']]
    status = '本轮机构专题已全部更新到2026Q3。' if not pending else '待续更：'+'、'.join(g.ALL_MANAGERS[k][0] for k in pending)+'。'
    text = text[:start] + f'最新增量：[[institutions/13F趋势-2026Q3|Q3 2026 {count}家机构]]。覆盖进度{count}/{len(g.ALL_MANAGERS)}；{status}\n\n上一季[[institutions/13F趋势-2026Q2|22家样本]]保留档案，不同样本的名次不能直接比较。\n\n本轮新增的机构展示平台与半导体的两侧动作、事件驱动换仓及宏观工具；持仓事实与研究解释分别陈列。Greenlight申报主体切换、Teva证券转换、Baupost金额单位、Tudor历史封面差异均保留审计。\n\n核验日期2026-11-17，报告期2026-09-30；机构主页展示2025Q4—2026Q3，长趋势保留2023Q1起历史。\n\n' + text[end:]
    for key in manifest['horizontal_keys']:
        title = g.ALL_MANAGERS[key][0]
        text = re.sub(r'(^- .*?\[\[institutions/13F趋势-'+re.escape(title)+r'.*$)', lambda m:m[0].replace('2026Q2','2026Q3'), text, flags=re.M)
    if 'Kensico=1.0' not in text:
        text = text.replace('Third Point=1.0,', 'Kensico=1.0（本季新增启发式）, Third Point=1.0,')
    text = text.replace('Q3 2026（十家）', f'Q3 2026（{count}家）')
    text = text.replace('本轮五家机构主页', f'本轮{count}家机构主页')
    text = re.sub(r'^- Q2 2025 之前只覆盖 1 家[^\n]*',
                  '- 历史季度页保留当时的样本范围；本轮23家长趋势均含2022Q4基期至2026Q3。跨季度比较先核对纳入机构与申报主体是否一致。', text, flags=re.M)
    if all(k in manifest['horizontal_keys'] for k in g.BATCH4_MANAGERS):
        start = text.index('## 趋势解读'); end = text.index('## 单机构专题')
        text = text[:start] + '''## 趋势解读

2026Q3的23家样本显示，同一公司常处在两种机构动作之间。先看股数，再看权重和价格，才能区分主动换仓与被动集中。

- 平台股分歧扩大：Lone Pine新列AMZN、META，Third Point新列META但退出AMZN；Kensico增加AMZN，Baillie减少AMZN、META。不能只用“科技共识”概括。
- 半导体也有两侧：Maverick增加NVDA、TSM，Kensico减少TSM，Lone Pine大幅增加TSM但大幅减少AMAT。设备、设计与代工应逐个比较。
- PDD的长期集中型买入侧，遇到Baillie的显著减股；质量机构在Veeva等标的上的交集，也需要保留各自的方法和价格约束。
- 事件驱动页更适合追问催化剂：Baupost增加GPC、FERG、WCC并减少GOOG、UNP；Greenlight增加VGNT、PCG。ADIG分拆取得的股份与Teva证券转换单列，不能当作普通建仓。
- 进入前十不等于主动加仓：Baillie的MRNA、Greenlight的DHT都出现减股但权重上升、进入前十。Kensico的HWM股数不变，仍是第一大仓。
- Tudor同时披露指数PUT、CALL与正股。全信息表和非期权分母并列，不能直接把两种期权相减后解释净方向。

这些是公开持仓支持的行为比较。行业主题、催化剂与经营论点属于下一步研究；完整排名和价格过滤见[[institutions/13F趋势-2026Q3]]，此前季度保留在下方档案。

''' + text[end:]
    entry.write_text(text)
    for key in manifest['horizontal_keys']:
        path = wiki/'institutions'/f'{g.ALL_MANAGERS[key][1]}.md'
        if path.exists():
            before = path.read_text()
            after = re.sub(r'\[\[institutions/13F趋势-2026Q3\|Q3 [^\]]*\]\]',
                           f'[[institutions/13F趋势-2026Q3|Q3 {count} 家样本]]', before)
            if after != before:
                path.write_text(after)
    log = wiki/'log.md'; marker = f'institution-13f-2026q3-{args.batch_id}'
    if marker not in log.read_text():
        with log.open('a') as out:
            out.write(f'\n\n## [{manifest["as_of"]}] {marker} | {label}，覆盖{count}家\n\n- 更新'+ '、'.join(d['title'] for _,d,*_ in prepared)+f'；独立快照`{relative}`，此前证据保留。\n- 联动{len(affected)}家公司页、来源审计与索引；注册{source_count}篇来源。\n- 修订、金额单位、主体切换和证券转换均保留原始证据。最终测试、构建及路由结果另追加验收条目。\n- 本轮本地更新，不提交、推送或发布。\n')
    print(json.dumps({'companies':len(affected),'created':created,'obligations':obligations,'source_count':source_count}, ensure_ascii=False))


if __name__ == '__main__':
    main()
