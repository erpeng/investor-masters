#!/usr/bin/env python3
"""Build auditable 13F snapshots; stage freely, freeze immutable evidence explicitly.

normalize imports mapping evidence into the snapshot and checks each filing's
amount unit against dated market prices (then independent SEC peer filings).
enrich fetches a bounded set of quotes plus split histories. freeze performs no
network requests and preserves the pre-update method pages alongside SEC TXT.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime as dt
import hashlib
import json
import math
import re
import sqlite3
import urllib.parse
import urllib.request
from pathlib import Path
from zoneinfo import ZoneInfo

from generate_13f_trends import (
    DEFAULT_VAULT, MANAGERS, json_bytes, quarter, resolve_filings,
    save_new, top,
)

ROOT = Path(__file__).resolve().parents[1]
ANCHORS = {'023135106': 'AMZN', '594918104': 'MSFT', '02079K305': 'GOOGL',
           '02079K107': 'GOOG', '037833100': 'AAPL', '084670702': 'BRK-B',
           '30303M102': 'META', '060505104': 'BAC', '92826C839': 'V',
           '67066G104': 'NVDA', 'H1467J104': 'CB', '23331A109': 'DHI'}
ALIASES = {'BRK.B': 'BRK-B', 'BRK/B': 'BRK-B', 'BRK B': 'BRK-B',
           'LEN.B': 'LEN-B', 'BF.B': 'BF-B', 'BF/B': 'BF-B'}
NO_COMPARABLE_QUOTE = {'BSP', 'SPCX'}
PRICE_ADJUSTMENTS = {
    ('GE', '2023-01-04'): ('GE HealthCare spin-off; parent GE shares unchanged',
                         'https://www.sec.gov/Archives/edgar/data/40545/000004054523000033/ge-20230103.htm'),
    ('GE', '2024-04-02'): ('GE Vernova spin-off; parent GE shares unchanged',
                         'https://www.sec.gov/Archives/edgar/data/40545/000004054524000088/ge-20240402.htm'),
    ('FDX', '2026-06-01'): ('FedEx Freight spin-off; one FDXF share per two FDX shares, parent shares unchanged',
                          'https://www.sec.gov/Archives/edgar/data/2082247/000110465926068521/tm2615735d2_8k.htm'),
    ('LEN', '2025-01-21'): ('Millrose spin-off record date, completed February 7; one MRP share per two LEN shares, parent shares unchanged',
                          'https://www.sec.gov/Archives/edgar/data/920760/000119312525022309/d933374d8k.htm'),
    ('SPGI', '2026-07-01'): ('Mobility Global pro-rata spin-off; parent SPGI shares unchanged',
                           'https://www.sec.gov/Archives/edgar/data/2090312/000209031226000014/mbgl-2026063010q.pdf'),
}
IDENTITY_ACTIONS = [
    {'type': 'cusip_change', 'ticker': 'LRCX', 'date': '2024-10-03', 'old_cusip': '512807108',
     'new_cusip': '512807306', 'ratio': 10, 'source': 'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2024-460',
     'note': 'Ten-for-one split; share factor is in splits and must not be applied twice.'},
    {'type': 'cusip_change', 'ticker': 'B', 'date': '2025-05-09', 'old_cusip': '067901108',
     'new_cusip': '06849F108', 'ratio': 1, 'source': 'https://www.sec.gov/Archives/edgar/data/756894/000119312525113917/d33942dex992.htm',
     'note': 'Barrick name/ticker change; existing certificates and shareholder rights remain valid.'},
    {'type': 'cusip_change_with_distribution', 'ticker': 'FWONK', 'date': '2023-08-04',
     'old_cusip': '531229854', 'new_cusip': '531229755', 'ratio': 1,
     'distributed_ticker': 'LLYVK', 'distributed_ratio': .0428,
     'source': 'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2023-420'},
    {'type': 'cusip_change_with_distribution', 'ticker': 'LSXMA', 'date': '2023-08-04',
     'old_cusip': '531229409', 'new_cusip': '531229813', 'ratio': 1,
     'distributed_ticker': 'LLYVA', 'distributed_ratio': .25,
     'source': 'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2023-420'},
    {'type': 'cusip_change_with_distribution', 'ticker': 'LSXMK', 'date': '2023-08-04',
     'old_cusip': '531229607', 'new_cusip': '531229789', 'ratio': 1,
     'distributed_ticker': 'LLYVK', 'distributed_ratio': .25,
     'source': 'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2023-420'},
    {'type': 'cusip_change', 'ticker': 'WVE', 'date': '2026-08-07', 'old_cusip': 'Y95308105',
     'new_cusip': '94352A104', 'ratio': 1, 'source': 'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2026-560'},
]
NORMALIZATION_METHOD = (
    'Each filing independently uses dated Yahoo unadjusted nominal closing price '
    '(reverse subsequent splits from split-adjusted historical closes), or the '
    'same CUSIP/share type in a previously validated independent SEC filing. '
    'Candidate multipliers are 1 and 1000; all matching anchors must agree. '
    'Option rows use reported underlying share notionals, never option premiums; '
    'original amounts and rounding remain intact.'
)


def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(content):
    return hashlib.sha256(content).hexdigest()


def symbol_name(value):
    return ALIASES.get(value, value)


def fetch_chart(symbol, start, end):
    """One bounded network attempt; missing prices remain explicit, not blocking."""
    if symbol in NO_COMPARABLE_QUOTE:
        raise ValueError('New listing / reporting-price comparability requires separate review')
    p1 = int(dt.datetime.fromisoformat(start).replace(tzinfo=dt.timezone.utc).timestamp())
    p2 = int((dt.datetime.fromisoformat(end) + dt.timedelta(days=1)).replace(tzinfo=dt.timezone.utc).timestamp())
    url = f'https://query1.finance.yahoo.com/v8/finance/chart/{urllib.parse.quote(symbol)}?period1={p1}&period2={p2}&interval=1d&events=splits'
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Cache-Control': 'no-cache'})
    with urllib.request.urlopen(req, timeout=10) as response:
        payload = response.read()
    obj = json.loads(payload)['chart']['result'][0]
    meta = obj['meta']
    if meta.get('currency') != 'USD' or meta.get('symbol') != symbol:
        raise ValueError('Quote currency/symbol mismatch')
    zone = ZoneInfo(meta['exchangeTimezoneName'])
    dates = [dt.datetime.fromtimestamp(t, zone).date().isoformat() for t in obj.get('timestamp', [])]
    history = {day: price for day, price in zip(dates, obj['indicators']['quote'][0]['close'])
               if price and math.isfinite(price) and day <= end}
    last = max(history)
    splits = [{'date': dt.datetime.fromtimestamp(v['date'], zone).date().isoformat(),
               'ratio': v['numerator'] / v['denominator']}
              for v in obj.get('events', {}).get('splits', {}).values()]
    return {'price': history[last], 'price_date': last, 'currency': 'USD', 'source': url,
            'fetched_at': dt.datetime.now(dt.timezone.utc).isoformat(), 'name': meta.get('longName', ''),
            'daily_closes': history, 'splits': splits, 'response_sha256': digest(payload)}


def mapping_records():
    """Bootstrap only. All adopted records are embedded; replay needs no research."""
    records = {}

    def add(cusip, record, source_file, verified=False):
        ticker = record.get('ticker') or record.get('symbol') or ''
        if not ticker or record.get('status') == 'unresolved':
            return
        old = records.get(cusip)
        item = {
            'ticker': symbol_name(ticker),
            'name': record.get('name') or record.get('issuer') or '',
            'description': record.get('description', ''),
            'mapping_source': record.get('mapping_source') or record.get('source', ''),
            'mapping_evidence': record,
            'mapping_import_file': str(source_file.relative_to(ROOT)),
            'mapping_status': 'quote_checked' if verified else 'reference_candidate',
        }
        if old and symbol_name(old['ticker']) != item['ticker']:
            item['mapping_alternatives'] = [old]
        records[cusip] = item

    database = ROOT / 'research/13f_market_backtest/data/2026Q2_20260814_20261014/market.sqlite'
    if database.exists():
        with sqlite3.connect(f'file:{database}?mode=ro', uri=True) as db:
            for _, payload in db.execute("SELECT key,payload FROM records WHERE kind IN ('mapping','cusip_reference') ORDER BY kind,key"):
                item = json.loads(payload)
                if item.get('cusip'):
                    add(item['cusip'], item, database)
    for relative, verified in [
        ('research/duquesne_13f_backtest/security_master.json', False),
        ('research/13f_copy_backtest/security_master.json', True),
    ]:
        path = ROOT / relative
        if path.exists():
            for cusip, item in read_json(path).items():
                add(cusip, item, path, verified)
    return records


def load_charts(stage, symbols, end, refresh=False, retry_errors=False):
    directory = stage / 'quotes'
    directory.mkdir(parents=True, exist_ok=True)

    def one(symbol):
        file = directory / (symbol.replace('/', '_') + '.json')
        previous = read_json(file) if file.exists() else None
        if file.exists() and not refresh:
            if not (retry_errors and previous.get('error') and 'timed out' in previous['error']):
                return symbol, previous
        try:
            data = fetch_chart(symbol, '2022-12-01', end)
        except Exception as exc:
            data = {'price': None, 'price_date': None, 'currency': None,
                    'source': 'https://query1.finance.yahoo.com/v8/finance/chart/' + symbol,
                    'fetched_at': dt.datetime.now(dt.timezone.utc).isoformat(),
                    'error': str(exc), 'daily_closes': {}, 'splits': []}
        data['requested_end'] = end
        data['symbol'] = symbol
        if previous and previous.get('error'):
            data['previous_errors'] = previous.get('previous_errors', []) + [
                {'error': previous['error'], 'fetched_at': previous.get('fetched_at')}]
        file.write_bytes(json_bytes(data))
        return symbol, data

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        return dict(pool.map(one, sorted(set(symbols))))


def nominal_price(chart, date):
    days = [day for day in chart.get('daily_closes', {}) if day <= date]
    if not days:
        return None
    day = max(days)
    if (dt.date.fromisoformat(date) - dt.date.fromisoformat(day)).days > 4:
        return None
    factor = math.prod(s['ratio'] for s in chart.get('splits', []) if date < s['date'])
    return chart['daily_closes'][day] * factor, day


def compare_unit(raw_price, reference):
    # A price gap cannot bridge three orders of magnitude. Reject inconsistent
    # anchors instead of choosing a manager-wide or schema-wide multiplier.
    matches = [m for m in (1, 1000) if abs(raw_price * m / reference - 1) <= .12]
    return matches[0] if len(matches) == 1 else None


def filing_unit(filing, charts, peers):
    evidence = []
    for row in filing['rows']:
        if row['share_type'] != 'SH' or not row['shares']:
            continue
        implied = row['value_raw'] / row['shares']
        ticker = ANCHORS.get(row['cusip'])
        price = nominal_price(charts[ticker], filing['reportDate']) if ticker in charts else None
        if price:
            reference, day = price
            multiplier = compare_unit(implied, reference)
            if multiplier:
                evidence.append({'method': 'dated_market_price', 'cusip': row['cusip'],
                                 'ticker': ticker, 'raw_implied_price': implied,
                                 'reference_price': reference, 'reference_date': day,
                                 'multiplier': multiplier, 'source': charts[ticker]['source'],
                                 'put_call': row['put_call'], 'price_basis': 'underlying shares, not option premium'})
        for peer, peer_row in peers.get((filing['reportDate'], row['cusip'], row['share_type']), []):
            if peer['accessionNumber'] == filing['accessionNumber']:
                continue
            reference = peer_row['value'] / peer_row['shares']
            multiplier = compare_unit(implied, reference)
            if multiplier:
                evidence.append({'method': 'independent_sec_same_date_cusip', 'cusip': row['cusip'],
                                 'raw_implied_price': implied, 'reference_price': reference,
                                 'multiplier': multiplier, 'source': peer['url'],
                                 'accession': peer['accessionNumber']})
                break
    votes = {e['multiplier'] for e in evidence}
    if len(votes) > 1:
        raise ValueError(f'Conflicting unit evidence: {filing["accessionNumber"]}: {evidence}')
    return (next(iter(votes)), evidence) if votes else (None, [])


def apply_charts(data, charts):
    symbols = {s['ticker'] for s in data['securities'].values() if s.get('ticker')}
    editorial = data.get('editorial', {})
    symbols.update(symbol_name(t) for t in editorial.get('candidates', []) + editorial.get('reverse', []))
    data['quotes'] = {}
    for symbol, chart in sorted(charts.items()):
        if symbol not in symbols:
            continue
        quote = dict(chart)
        if quote.get('price_date') and quote['price_date'] != quote.get('requested_end'):
            quote['last_available_price'] = quote['price']
            quote['price'] = None
            quote['stale'] = True
            quote['error'] = f'Stale quote: latest available {quote["price_date"]}, requested {quote.get("requested_end")}'
        data['quotes'][symbol] = quote
    data['splits'] = []
    excluded = []
    for symbol, chart in sorted(charts.items()):
        if symbol not in symbols:
            continue
        for event in chart.get('splits', []):
            item = dict(event, ticker=symbol, source=chart['source'], fetched_at=chart['fetched_at'])
            adjustment = PRICE_ADJUSTMENTS.get((symbol, event['date']))
            if adjustment:
                item.update(reason=adjustment[0], primary_source=adjustment[1])
                excluded.append(item)
            else:
                data['splits'].append(item)
    data.setdefault('audit', {})['excluded_price_adjustments'] = excluded
    data['split_coverage'] = {
        'checked': sorted(symbols & charts.keys()),
        'unavailable': sorted(s for s in symbols & charts.keys() if charts[s].get('error')),
        'not_fetched': sorted(symbols - charts.keys()),
        'unmapped_cusips': sorted(c for c, s in data['securities'].items() if not s.get('ticker')),
    }
    data['split_coverage']['scope'] = 'Editorial candidates/reverse, every historical top ten, and every adjacent-quarter implied-price ratio outside 0.6–1.7. Other small historical positions are explicitly not checked.'


def suspected_actions(data):
    """Screen every position for material nominal-price discontinuities."""
    result = []
    periods = resolve_filings(data)
    for previous, current in zip(periods, periods[1:]):
        for key in sorted(previous['rows'].keys() & current['rows'].keys()):
            old, new = previous['rows'][key], current['rows'][key]
            if not all((old['shares'], new['shares'], old['value'], new['value'])):
                continue
            ratio = (old['value'] / old['shares']) / (new['value'] / new['shares'])
            if ratio > 1.7 or ratio < .6:
                result.append({'cusip': new['cusip'], 'ticker': data['securities'][new['cusip']].get('ticker', ''),
                               'start': previous['date'], 'end': current['date'], 'implied_price_ratio': ratio,
                               'put_call': new['put_call']})
    return result


def normalize(args):
    stage = Path(args.stage)
    datasets = {key: read_json(stage / f'{key}-fetched.json') for key in args.keys}
    records = mapping_records()
    for override_path in (ROOT / 'scripts/data/13f-2026q3-security-overrides.json', stage / 'mapping-overrides.json'):
        if override_path.exists():
            records.update(read_json(override_path))
    charts = ({p.stem: read_json(p) for p in (stage / 'quotes').glob('*.json')}
              if args.offline else load_charts(stage, ANCHORS.values(), args.quote_end, args.refresh))
    pending = [f for d in datasets.values() for f in d['filings'] if not f.get('notice')]
    peers = {}
    while pending:
        unresolved = []
        for filing in pending:
            multiplier, evidence = filing_unit(filing, charts, peers)
            if multiplier is None:
                unresolved.append(filing)
                continue
            filing['unit_multiplier'] = multiplier
            filing['unit_evidence'] = evidence
            filing['reported_total'] = filing['reported_total_raw'] * multiplier
            filing['cover_difference'] = filing['cover_difference_raw'] * multiplier
            for row in filing['rows']:
                row['value'] = row['value_raw'] * multiplier
                if not row['put_call'] and row['shares'] and row['share_type'] == 'SH':
                    peers.setdefault((filing['reportDate'], row['cusip'], row['share_type']), []).append((filing, row))
        if len(unresolved) == len(pending):
            raise ValueError('Unresolved filing units: ' + ', '.join(f['accessionNumber'] for f in pending))
        pending = unresolved
    metadata = read_json(args.editorial)
    for key, data in datasets.items():
        for filing in data['filings']:
            if filing['accessionNumber'] == '0000950123-25-008361':
                filing['additive_overlap_cusips'] = ['526057302']
                filing['additive_overlap_evidence'] = {
                    'source': filing['url'], 'amendment_type': 'NEW HOLDINGS',
                    'explanation': 'LEN.B supplemental 202 shares / $22,032 are added to original 152,572 shares / $16,641,028; the other three rows are new holdings. This is an accession-specific exception, never a generic overlap policy.',
                    'original_accession': '0000950123-25-005701',
                }
        securities = {}
        for filing in data['filings']:
            for row in filing['rows']:
                cusip = row['cusip']
                security = dict(records.get(cusip, {}))
                security.setdefault('ticker', '')
                security.setdefault('name', row['issuer'])
                security.setdefault('description', '')
                security.setdefault('mapping_status', 'unresolved')
                security.setdefault('mapping_source', filing['url'])
                security.setdefault('mapping_evidence', {'issuer': row['issuer'], 'cusip': cusip,
                                                         'security_class': row['security_class']})
                security['issuer'] = row['issuer']
                securities[cusip] = security
        data.update(schema_version=1, as_of=args.as_of, latest_quarter=args.quarter,
                    securities=securities, normalization_method=NORMALIZATION_METHOD,
                    editorial=metadata.get(key, {}))
        apply_charts(data, charts)
        periods = resolve_filings(data)
        data['validation'] = {'quarters': len(periods), 'latest_total': periods[-1]['total'],
                              'latest_count': len(periods[-1]['rows'])}
        output = stage / f'{key}-normalized.json'
        output.write_bytes(json_bytes(data))
        print(key, 'normalized', len(periods), 'quarters', periods[-1]['total'], flush=True)


def enrich(args):
    stage = Path(args.stage)
    datasets = {key: read_json(stage / f'{key}-normalized.json') for key in args.keys}
    symbols = set()
    for data in datasets.values():
        legacy_page(data, Path(args.vault), stage)
        editorial = data['editorial']
        symbols.update(symbol_name(t) for t in editorial.get('candidates', []) + editorial.get('reverse', []))
        if args.all_splits:
            symbols.update(s['ticker'] for s in data['securities'].values() if s.get('ticker'))
        else:
            for period in resolve_filings(data):
                for key in top(period):
                    ticker = data['securities'][period['rows'][key]['cusip']].get('ticker')
                    if ticker:
                        symbols.add(ticker)
        data['corporate_action_screen'] = suspected_actions(data)
        symbols.update(item['ticker'] for item in data['corporate_action_screen'] if item['ticker'])
    charts = load_charts(stage, symbols, args.quote_end, args.refresh, args.retry_errors)
    for data in datasets.values():
        # Keep original anchor histories as part of reproducible unit evidence.
        charts.update({k: v for k, v in data.get('quotes', {}).items() if k not in charts})
    for key, data in datasets.items():
        apply_charts(data, charts)
        for item in data['corporate_action_screen']:
            chart = charts.get(item['ticker'], {})
            item['status'] = 'unavailable' if not chart or chart.get('error') else 'events_checked'
            item['events'] = [s for s in data['splits'] if s['ticker'] == item['ticker']
                              and item['start'] < s['date'] <= item['end']]
            item['source'] = chart.get('source')
        data.setdefault('audit', {})['unresolved_splits'] = [
            item for item in data['corporate_action_screen'] if item['status'] == 'unavailable']
        (stage / f'{key}-normalized.json').write_bytes(json_bytes(data))
        print(key, 'enriched', len(data['quotes']), 'quotes', len(data['splits']), 'split events', flush=True)


def legacy_page(data, vault, stage):
    key = data['institution']
    output = stage / 'legacy' / f'{key}.md'
    if not output.exists():
        path = vault / 'wiki/institutions' / f'13F趋势-{data["title"]}.md'
        if not path.exists():
            return None
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(path.read_bytes())
    text = output.read_text()
    match = re.search(r'^## (?:三、用[^\n]*|用 Appaloosa 方法重新读[^\n]*)\n(.*?)(?=^## |\Z)', text, re.M | re.S)
    if match:
        data['editorial']['legacy_method'] = match.group(1).strip()
    # Keep the entire former trajectory basket, including historical exits.
    # Unknown issuer-only labels remain available in the archived original page.
    watch = set(data['editorial'].get('watch', []))
    for match in re.finditer(r'^\|\s*`?([A-Z][A-Z0-9.\-]{0,9})(?:（|\s+(?:PUT|CALL)\b)', text, re.M):
        watch.add(symbol_name(match.group(1)))
    data['editorial']['watch'] = sorted(watch)
    data['legacy_source'] = {'path': f'legacy/{key}.md', 'sha256': digest(output.read_bytes())}
    return output


def freeze(args):
    stage, vault = Path(args.stage), Path(args.vault)
    target = Path(args.snapshot_dir) if args.snapshot_dir else vault / 'raw/data' / ('13f-' + args.as_of.replace('-', ''))
    metadata = read_json(args.editorial)
    prepared = []
    for key in args.keys:
        data = read_json(stage / f'{key}-normalized.json')
        data['editorial'] = dict(data.get('editorial', {}), **metadata[key])
        data['corporate_actions'] = [action for action in IDENTITY_ACTIONS
                                    if action['old_cusip'] in data['securities'] or action['new_cusip'] in data['securities']]
        old = legacy_page(data, vault, stage)
        if old:
            prepared.append((target / 'legacy' / old.name, old.read_bytes()))
        periods = resolve_filings(data)
        if quarter(periods[-1]['date']) != args.quarter or len(periods) != 16:
            raise ValueError(f'Incomplete quarter coverage: {key}')
        data['replay_evidence'] = {'builder_sha256': digest(Path(__file__).read_bytes()),
                                   'generator_sha256': digest((ROOT / 'scripts/generate_13f_trends.py').read_bytes()),
                                   'identity_rules_version': '2026Q3-v1',
                                   'identity_rules': ['CUSIP + normalized class + PUT/CALL; original class retained',
                                                      'PDD/DBV/YPF/JD ADS text aliases; AAL/XLF text aliases',
                                                      'Wave Y95308105 to 94352A104 one-for-one redomestication',
                                                      'LRCX 512807108 to 512807306 ten-for-one split; class COM/COM NEW aliases',
                                                      'Barrick and Liberty parent-security CUSIP changes; distributions recorded separately',
                                                      'LEN.B CUSIP 526057302 fixes mislabeled historical class A',
                                                      'Berkshire 0000950123-25-008361 LEN.B +202 explicit additive amendment']}
        for filing in data['filings']:
            acc = filing['accessionNumber']
            content = (stage / 'sec' / f'{acc}.txt').read_bytes()
            if filing.get('sha256') and digest(content) != filing['sha256']:
                raise ValueError(f'SEC hash changed: {acc}')
            filing['local_source'] = f'sec/{acc}.txt'
            filing['sha256'] = digest(content)
            prepared.append((target / filing['local_source'], content))
        submission = (stage / f'{key}-submissions.json').read_bytes()
        data['submission_evidence'] = {'path': f'{key}-submissions.json', 'sha256': digest(submission),
                                       'source': f'https://data.sec.gov/submissions/CIK{data["cik"]:010d}.json'}
        prepared.append((target / f'{key}-submissions.json', submission))
        prepared.append((target / f'{key}.json', json_bytes(data)))
    # Preflight every target before writing anything: immutable conflicts do not
    # leave a half-written new batch behind.
    manifest = {str(p.relative_to(target)): digest(content) for p, content in prepared}
    prepared.append((target / 'sha256.json', json_bytes(manifest)))
    for path, content in prepared:
        if path.exists() and path.read_bytes() != content:
            raise ValueError(f'Immutable evidence already exists: {path}')
    for path, content in prepared:
        save_new(path, content)
    print('Frozen:', target, len(manifest), 'files', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['normalize', 'enrich', 'freeze'])
    parser.add_argument('--stage', default='/tmp/investors-13f-20261117')
    parser.add_argument('--vault', default=DEFAULT_VAULT)
    parser.add_argument('--institutions', default=','.join(MANAGERS))
    parser.add_argument('--as-of', default='2026-11-17')
    parser.add_argument('--quarter', default='2026Q3')
    parser.add_argument('--quote-end', default='2026-11-16')
    parser.add_argument('--editorial', default=str(ROOT / 'scripts/data/13f-2026q3-editorial.json'))
    parser.add_argument('--snapshot-dir')
    parser.add_argument('--all-splits', action='store_true', help='Fetch split histories for every mapped historical security')
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--retry-errors', action='store_true', help='Retry cached transient timeout failures once')
    parser.add_argument('--offline', action='store_true', help='Normalize using staged quote evidence only')
    args = parser.parse_args()
    args.keys = args.institutions.split(',')
    if any(key not in MANAGERS for key in args.keys):
        parser.error('Unknown institution')
    {'normalize': normalize, 'enrich': enrich, 'freeze': freeze}[args.action](args)


if __name__ == '__main__':
    main()
