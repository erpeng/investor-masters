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
    DEFAULT_VAULT, MANAGERS, ALL_MANAGERS, BATCH3_CLASS_ALIASES, json_bytes, quarter, resolve_filings,
    save_new, top, normalized_class,
)

ROOT = Path(__file__).resolve().parents[1]
ANCHORS = {'023135106': 'AMZN', '594918104': 'MSFT', '02079K305': 'GOOGL',
           '02079K107': 'GOOG', '037833100': 'AAPL', '084670702': 'BRK-B',
           '30303M102': 'META', '060505104': 'BAC', '92826C839': 'V',
           '67066G104': 'NVDA', 'H1467J104': 'CB', '23331A109': 'DHI',
           '169656105': 'CMG', '43300A203': 'HLT', '42806J700': 'HTZ', '71531U102': 'PS',
           '26154D100': 'DFH', '88579Y101': 'MMM'}
ALIASES = {'BRK.B': 'BRK-B', 'BRK/B': 'BRK-B', 'BRK B': 'BRK-B',
           'LEN.B': 'LEN-B', 'BF.B': 'BF-B', 'BF/B': 'BF-B', 'HEI.A': 'HEI-A'}
NO_COMPARABLE_QUOTE = {'BSP', 'SPCX'}
PRICE_ADJUSTMENTS = {
    ('WDC', '2025-02-24'): ('Sandisk distribution; Western Digital parent shares unchanged', 'https://www.sec.gov/Archives/edgar/data/106040/000010604025000012/wdc8-khardxspin.htm'),
    ('LBTYK', '2024-11-13'): ('Sunrise distribution; Liberty Global parent shares unchanged', 'https://www.libertyglobal.com/investors/sunrise-spin-off/'),
    ('J', '2024-09-30'): ('Amentum distribution; Jacobs parent shares unchanged', 'https://www.sec.gov/Archives/edgar/data/52988/000005298825000016/jec-20241227.htm'),
    ('J', '2025-05-16'): ('Additional Amentum distribution; Jacobs parent shares unchanged', 'https://www.sec.gov/Archives/edgar/data/52988/000005298825000032/exhibit991-supplementalinf.htm'),
    ('SPHR', '2023-04-21'): ('MSG Entertainment distribution; Sphere parent shares unchanged', 'https://www.sphereentertainmentco.com/sphere-entertainment-co-completes-spin-off-of-traditional-live-entertainment-businesses/'),
    ('FBIN', '2022-12-15'): ('MasterBrand distribution; Fortune Brands parent shares unchanged', 'https://www.sec.gov/Archives/edgar/data/1519751/000119312522306146/d420098dex991.htm'),
    ('CTVA', '2026-10-01'): ('Vylor distribution; Corteva parent shares unchanged; post-quarter price is not a standalone comparable return', 'https://www.sec.gov/Archives/edgar/data/1755672/000175567226000035/ctva-20260930.htm'),
    ('APTV', '2026-04-01'): ('Versigent distribution; Aptiv parent shares unchanged',
                           'https://www.sec.gov/Archives/edgar/data/1521332/000152133226000075/aptv-20260930.htm'),
    ('REZI', '2026-08-04'): ('ADI Global distribution; Resideo parent shares unchanged',
                           'https://www.sec.gov/Archives/edgar/data/2105139/000162828026073496/adig-20261003.htm'),
    ('HON', '2026-06-29'): ('Honeywell Aerospace distribution; parent shares unchanged',
                          'https://www.sec.gov/Archives/edgar/data/2089271/000208927126000021/hona-20260627.htm'),
    ('DHR', '2023-10-02'): ('Veralto distribution; Danaher parent share count unchanged',
                          'https://www.sec.gov/Archives/edgar/data/313616/000031361623000252/exhibit992.htm'),
    ('ARMK', '2023-10-02'): ('Vestis distribution; Aramark parent share count unchanged',
                           'https://www.sec.gov/Archives/edgar/data/1584509/000162828023033364/cik0-20230929.htm'),
    ('BWA', '2023-07-05'): ('PHINIA distribution; BorgWarner parent share count unchanged',
                          'https://www.sec.gov/Archives/edgar/data/908255/000110465923079180/tm2320751d1_8-k.htm'),
    ('BDX', '2026-02-10'): ('Biosciences distribution and Waters combination; BD parent shares unchanged',
                          'https://www.sec.gov/Archives/edgar/data/1000697/000119312526042819/d23927dex991.htm'),
    ('ILMN', '2024-06-25'): ('GRAIL distribution; Illumina parent shares unchanged',
                           'https://www.sec.gov/Archives/edgar/data/1110803/000119312524167025/d851030d8k.htm'),
    ('LBTYA', '2024-11-13'): ('Sunrise distribution; Liberty Global parent shares unchanged',
                            'https://www.libertyglobal.com/investors/sunrise-spin-off/'),
    ('FWONK', '2023-07-20'): ('Atlanta Braves distribution; Formula One parent shares unchanged',
                            'https://www.libertymedia.com/news/detail/503/liberty-media-corporation-announces-completion-of'),
    ('BN', '2022-12-12'): ('Asset manager distribution; Brookfield parent shares unchanged',
                         'https://www.sec.gov/Archives/edgar/data/1001085/000119312522302324/d435804d6k.htm'),
    ('HHH', '2024-08-01'): ('Seaport Entertainment spin-off; one SEG share per nine HHH shares, parent HHH shares unchanged',
                          'https://www.sec.gov/Archives/edgar/data/1981792/000110465924084903/tm2420480d1_8k.htm'),
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
PRIMARY_SPLITS = [
    {'ticker': 'MNST', 'date': '2026-08-11', 'ratio': 2, 'source': 'https://www.sec.gov/Archives/edgar/data/865752/000110465926123503/mnst-20260930x10q.htm'},
    {'ticker': 'RYAAY', 'date': '2024-09-30', 'ratio': 2.5, 'source': 'https://investor.ryanair.com/wp-content/uploads/2024/10/Form-8937-Ryanair-ADR-Ratio-Change.pdf'},
    {'ticker': 'NVO', 'date': '2023-09-20', 'ratio': 2,
     'source': 'https://www.sec.gov/Archives/edgar/data/353278/000117184323005686/f6k_091323.htm'},
    {'ticker': 'ORLY', 'date': '2025-06-10', 'ratio': 15,
     'source': 'https://corporate.oreillyauto.com/wp-content/uploads/2025/07/2025-IRS-Form-8937.pdf'},
    {'ticker': 'CPRT', 'date': '2023-08-22', 'ratio': 2,
     'source': 'https://www.copart.com/content/us/en/press-releases/copart-announces-two-for-one-stock-split'},
    {'ticker': 'BN', 'date': '2025-10-10', 'ratio': 1.5,
     'source': 'https://bn.brookfield.com/sites/brookfield-bn-v2/files/BN-IR-Master/Brookfield-Security-History/brookfield-security-history-2025.pdf'},
    {'ticker': 'NOW', 'date': '2025-12-18', 'ratio': 5,
     'source': 'https://investor.servicenow.com/news/news-details/2025/ServiceNow-Shareholders-Approve-5-for-1-Stock-Split/default.aspx'},
    {'ticker': 'NFLX', 'date': '2025-11-17', 'ratio': 10,
     'source': 'https://ir.netflix.net/investor-news-and-events/financial-releases/press-release-details/2025/Netflix-Announces-Ten-For-One-Stock-Split/'},
    {'ticker': 'UL', 'date': '2025-12-09', 'ratio': 8/9,
     'source': 'https://www.unilever.com/files/unilever-plc-irs-form-8937-attachment.pdf'},
]
IDENTITY_ACTIONS = [
    {'type': 'ads_conversion', 'ticker': 'TEVA', 'date': '2026-09-14',
     'old_cusip': '881624209', 'new_cusip': 'M8769Q102', 'ratio': 1,
     'source': 'https://ir.tevapharm.com/investor-resources/conversion-of-teva-adss-into-ordinary-shares/default.aspx',
     'note': 'One NYSE ordinary share for each ADS. Preserve original class/CUSIP; do not infer sale and repurchase from the conversion.'},
    {'type': 'cusip_change', 'ticker': 'SOND', 'date': '2023-09-21', 'old_cusip': '83542D102',
     'new_cusip': '83542D300', 'ratio': .05,
     'source': 'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2023-532',
     'note': 'One-for-twenty reverse split; residual fractional-share cash is not a trade inference.'},
    {'type': 'cusip_change', 'ticker': 'LCID', 'date': '2025-09-02', 'old_cusip': '549498103',
     'new_cusip': '549498202', 'ratio': .1,
     'source': 'https://ir.lucidmotors.com/news-releases/news-release-details/lucid-group-inc-announces-effective-date-reverse-stock-split/',
     'note': 'One-for-ten reverse split.'},
    {'type': 'cusip_change', 'ticker': 'NKLA', 'date': '2024-06-25', 'old_cusip': '654110105',
     'new_cusip': '654110303', 'ratio': 1/30,
     'source': 'https://m.nasdaqtrader.com/TraderNews.aspx?id=ECA2024-294',
     'note': 'One-for-thirty reverse split.'},
    {'type': 'cusip_change', 'ticker': 'SMCI', 'date': '2024-10-01', 'old_cusip': '86800U104',
     'new_cusip': '86800U302', 'ratio': 10,
     'source': 'https://infomemo.theocc.com/infomemos?number=55298',
     'note': 'Ten-for-one forward split.'},
    {'type': 'cusip_change_with_settlement', 'ticker': 'AMC', 'date': '2023-08-24', 'old_cusip': '00165C104',
     'new_cusip': '00165C302', 'ratio': .1,
     'source': 'https://investor.amctheatres.com/sec-filings/all-sec-filings/content/0001104659-23-090981/tm2323643d1_8k.htm',
     'note': 'One-for-ten reverse split plus one share per 7.5 settlement and APE conversion. Quarter change is explicitly unattributed, not a plain split-adjusted trade.'},
    {'type': 'historical_cusip_alias', 'ticker': 'GRABW', 'date': '2021-12-02', 'old_cusip': 'G0370L116',
     'new_cusip': 'G4124C117', 'ratio': 1,
     'source': 'https://classic.nasdaqtrader.com/TraderNews.aspx?id=ECA2021-267',
     'note': 'AGCWW warrants became GRABW one-for-one in 2021. Later Altimeter filings continued obsolete CUSIP until 2026Q1; no new economic entry in 2026Q2.'},
    {'type': 'cusip_change', 'ticker': 'CP', 'date': '2023-04-14', 'old_cusip': '13645T100',
     'new_cusip': '13646K108', 'ratio': 1,
     'source': 'https://www.sec.gov/Archives/edgar/data/16875/000119312523102124/d447202d8k.htm',
     'note': 'Canadian Pacific name change after Kansas City Southern combination; existing shares remain outstanding.'},
    {'type': 'cusip_change', 'ticker': 'HHH', 'date': '2023-08-11', 'old_cusip': '44267D107',
     'new_cusip': '44267T102', 'ratio': 1,
     'source': 'https://www.sec.gov/Archives/edgar/data/1981792/000110465923090466/tm2323105d1_ex99-1.htm',
     'note': 'Holding-company reorganization; one HHH share per HHC share.'},
    {'type': 'cusip_change', 'ticker': 'CHPT', 'date': '2025-07-28', 'old_cusip': '15961R105',
     'new_cusip': '15961R303', 'ratio': .05,
     'source': 'https://infomemo.theocc.com/infomemos?number=56950',
     'note': 'One-for-twenty reverse split; share factor recorded separately in splits, never applied twice.'},
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
UNCERTAIN_ACTIONS = [{
    'ticker': 'CNR', 'start': '2024-12-31', 'end': '2025-03-31',
    'cusips': ['20854L108', '218937100', '03940R107'],
    'reason': 'CONSOL与Arch合并为Core Natural Resources，包含续存证券更名及Arch按1.326换股；原证券分别保留，该季度相关差额不认定为现金买卖。',
    'source': 'https://www.sec.gov/Archives/edgar/data/1710366/000119312525007135/d836647dex991.htm',
}, {
    'ticker': 'ADIG', 'start': '2026-06-30', 'end': '2026-09-30',
    'cusips': ['001026103', '76118Y104'],
    'reason': 'Resideo每两股分派一股ADI Global；季度内取得时点未知，母子公司变化单列未归因，不把分派当作新现金买入。',
    'source': 'https://www.sec.gov/Archives/edgar/data/2105139/000162828026073496/adig-20261003.htm',
}, {
    'ticker': 'AMC', 'start': '2023-06-30', 'end': '2023-09-30',
    'cusips': ['00165C104', '00165C302', '00165C203'],
    'reason': 'AMC本季同时并股、APE转换及诉讼和解派股；缺少完整逐账户转换路径，市值差单列未归因，不按简单并股推断买卖。',
    'source': 'https://investor.amctheatres.com/sec-filings/all-sec-filings/content/0001104659-23-090981/tm2323643d1_8k.htm',
}]
PRIMARY_ACTION_REVIEWS = [{
    'ticker': 'REZI', 'start': '2026-06-30', 'end': '2026-09-30',
    'source': 'https://www.sec.gov/Archives/edgar/data/2105139/000162828026073496/adig-20261003.htm',
    'reason': 'ADI spin-off, not a parent stock split; related quarter is explicitly unattributed.',
}, {
    'ticker': 'INIO', 'start': '2026-06-30', 'end': '2026-09-30',
    'source': 'https://www.sec.gov/Archives/edgar/data/2109150/000162828026067448/inio-20260930.htm',
    'reason': 'Q3 10-Q reports 750m weighted-average and September30 outstanding common shares; the conversion was June4 before Q2-end, with no Q3 split identified.',
}]
CLASS_ALIASES = [
    {'cusip': '833445109', 'alias': 'CL A / COM SHS', 'source': 'https://www.sec.gov/Archives/edgar/data/1640147/000164014725000150/snow-20250702.htm',
     'note': 'Snowflake renamed Class A as Common Stock effective July3 2025; shares unchanged.'},
    {'cusip': '82509L107', 'alias': 'CL A / CL A SUB VTG SHS', 'source': 'https://www.sec.gov/Archives/edgar/data/1594805/000159480524000019/a2024nomrd.htm',
     'note': 'Shopify Class A Subordinate Voting Shares; Class B has a different CUSIP.'},
    {'cusip': '770700102', 'alias': 'CL A / COM CL A', 'source': 'https://www.sec.gov/Archives/edgar/data/1783879/000119312525260776/xslSCHEDULE_13G_X01/primary_doc.xml',
     'note': 'Robinhood same-CUSIP Class A spelling variation.'},
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
    if not reference or reference <= 0 or raw_price <= 0:
        return None
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
    for event in PRIMARY_SPLITS:
        if event['ticker'] not in symbols:
            continue
        existing = next((s for s in data['splits'] if s['ticker'] == event['ticker'] and s['date'] == event['date']), None)
        if existing and abs(existing['ratio'] / event['ratio'] - 1) > .002:
            raise ValueError('Primary split conflicts with quote history: ' + event['ticker'])
        if existing:
            existing.update(quote_reported_ratio=existing['ratio'], ratio=event['ratio'], primary_source=event['source'])
        else:
            data['splits'].append(dict(event, evidence_type='primary_corporate_action'))
    # Primary exchange notices supply a share factor even if Yahoo has no history.
    for action in IDENTITY_ACTIONS:
        if action['ratio'] == 1 or not ({action['old_cusip'], action['new_cusip']} & data['securities'].keys()):
            continue
        existing = [event for event in data['splits'] if event['ticker'] == action['ticker'] and event['date'] == action['date']]
        if existing and any(abs(event['ratio'] - action['ratio']) > 1e-10 for event in existing):
            raise ValueError('Primary split evidence conflicts with quote history: ' + action['ticker'])
        for event in existing:
            event['primary_source'] = action['source']
        if not existing:
            data['splits'].append({'ticker': action['ticker'], 'date': action['date'], 'ratio': action['ratio'],
                                   'source': action['source'], 'evidence_type': 'primary_corporate_action'})
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


def apply_quote_overrides(data, stage):
    """Explicit, sourced fallback quotes; preserve the failed/stale attempt."""
    path = stage / 'quote-overrides.json'
    if not path.exists():
        return
    overrides = read_json(path)
    for symbol, verified in overrides.items():
        if symbol not in data.get('quotes', {}):
            continue
        old = data['quotes'][symbol]
        if verified.get('currency') != 'USD' or verified.get('symbol') != symbol:
            raise ValueError('Fallback quote identity/currency mismatch: ' + symbol)
        quote = dict(old, **verified)
        quote['previous_quote_attempt'] = old.get('previous_quote_attempt') or {key: old.get(key) for key in
                                           ('price', 'last_available_price', 'price_date', 'error', 'source', 'fetched_at', 'response_sha256')}
        quote['history_source'] = old.get('source')
        quote.pop('error', None)
        quote.pop('stale', None)
        data['quotes'][symbol] = quote
    data['quote_override_evidence'] = {'path': 'quote-overrides.json', 'sha256': digest(path.read_bytes())}


def normalize(args):
    stage = Path(args.stage)
    datasets = {key: read_json(stage / f'{key}-fetched.json') for key in args.keys}
    class_overrides = read_json(stage / 'class-overrides.json') if (stage / 'class-overrides.json').exists() else {}
    for key, data in datasets.items():
        data['scoped_class_alias_evidence'] = class_overrides.get(key, [])
        for action in data['scoped_class_alias_evidence']:
            for filing in data['filings']:
                for row in filing['rows']:
                    if all(row[field] == action[field] for field in ('cusip', 'put_call', 'share_type')):
                        row['canonical_class'] = action['canonical_class']
    records = mapping_records()
    for override_path in (ROOT / 'scripts/data/13f-2026q3-security-overrides.json', stage / 'mapping-overrides.json'):
        if override_path.exists():
            records.update(read_json(override_path))
    for action in IDENTITY_ACTIONS:
        old, new = action['old_cusip'], action['new_cusip']
        if old not in records and new in records:
            records[old] = dict(records[new], mapping_source=action['source'],
                                mapping_evidence=action, mapping_status='primary_predecessor_security')
        for cusip in (old, new):
            if not records.get(cusip, {}).get('ticker'):
                records[cusip] = dict(records.get(cusip, {}), ticker=action['ticker'],
                                     mapping_source=action['source'], mapping_evidence=action,
                                     mapping_status='primary_corporate_action')
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
                    editorial=metadata.get(key, {}), uncertain_corporate_actions=[
                        action for action in UNCERTAIN_ACTIONS if set(action['cusips']) & securities.keys()])
        classes = {}
        for filing in data['filings']:
            for row in filing['rows']:
                group = (row['cusip'], row['put_call'], row['share_type'])
                classes.setdefault(group, set()).add(normalized_class(row))
        data['class_identity_issues'] = [
            {'cusip': c, 'put_call': pc, 'share_type': st, 'classes': sorted(variants)}
            for (c, pc, st), variants in sorted(classes.items()) if len(variants) > 1]
        if key == 'greenlight':
            data['noncomparable_intervals'] = [{
                'start': '2023-12-31', 'end': '2024-03-31',
                'label': '申报主体切换，不作交易方向判断',
                'reason': 'Greenlight转为DME申报；主体及纳入管理人范围变化，该区间仅展示两端持仓与市值差，不归因为主动交易或价格收益。',
                'source': 'https://www.sec.gov/Archives/edgar/data/1489933/000117266124001504/0001172661-24-001504.txt',
            }]
        apply_charts(data, charts)
        apply_quote_overrides(data, stage)
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
    charts = ({p.stem: read_json(p) for p in (stage / 'quotes').glob('*.json')}
              if args.offline else load_charts(stage, symbols, args.quote_end, args.refresh, args.retry_errors))
    for data in datasets.values():
        # Keep original anchor histories as part of reproducible unit evidence.
        charts.update({k: v for k, v in data.get('quotes', {}).items() if k not in charts})
    for key, data in datasets.items():
        apply_charts(data, charts)
        apply_quote_overrides(data, stage)
        for item in data['corporate_action_screen']:
            chart = charts.get(item['ticker'], {})
            item['status'] = 'unavailable' if not chart or chart.get('error') else 'events_checked'
            item['events'] = [s for s in data['splits'] if s['ticker'] == item['ticker']
                              and item['start'] < s['date'] <= item['end']]
            item['source'] = chart.get('source')
            if any(event.get('evidence_type') == 'primary_corporate_action' or event.get('primary_source') for event in item['events']):
                item['status'] = 'primary_split_verified'
            reviewed = next((review for review in PRIMARY_ACTION_REVIEWS if
                             all(review[field] == item[field] for field in ('ticker', 'start', 'end'))), None)
            if reviewed:
                item.update(status='primary_checked_no_split', source=reviewed['source'], primary_review=reviewed['reason'])
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
    match = re.search(r'^## (?:[一二三四五六七八九十]+、)?用[^\n]*(?:重新读|方法)[^\n]*\n(.*?)(?=^## |\Z)', text, re.M | re.S)
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
        previous_watch = set(data.get('editorial', {}).get('watch', []))
        data['editorial'] = dict(data.get('editorial', {}), **metadata[key])
        data['editorial']['watch'] = sorted(previous_watch | set(data['editorial'].get('watch', [])))
        data['corporate_actions'] = [action for action in IDENTITY_ACTIONS
                                    if action['old_cusip'] in data['securities'] or action['new_cusip'] in data['securities']]
        data['class_alias_evidence'] = [action for action in CLASS_ALIASES if action['cusip'] in data['securities']]
        data['class_alias_evidence'].extend(data.get('scoped_class_alias_evidence', []))
        for cusip, canonical in BATCH3_CLASS_ALIASES.items():
            variants = sorted({r['security_class'] for f in data['filings'] for r in f['rows'] if r['cusip'] == cusip})
            if len(variants) > 1:
                data['class_alias_evidence'].append({
                    'cusip': cusip, 'canonical_class': canonical, 'original_classes': variants,
                    'sources': sorted({f['url'] for f in data['filings'] if any(r['cusip'] == cusip for r in f['rows'])}),
                    'note': 'Same CUSIP identifies the same legal security; reviewed whitespace / class spelling variants only. PUT/CALL remains independent.',
                })
        old = legacy_page(data, vault, stage)
        if old:
            prepared.append((target / 'legacy' / old.name, old.read_bytes()))
        periods = resolve_filings(data)
        if quarter(periods[-1]['date']) != args.quarter or len(periods) != 16:
            raise ValueError(f'Incomplete quarter coverage: {key}')
        data['replay_evidence'] = {'builder_sha256': digest(Path(__file__).read_bytes()),
                                   'generator_sha256': digest((ROOT / 'scripts/generate_13f_trends.py').read_bytes()),
                                   'identity_rules_version': '2026Q3-v3',
                                   'identity_rules': ['CUSIP + normalized class + PUT/CALL; original class retained',
                                                      'Scoped class aliases require matching CUSIP, PUT/CALL and share type; unresolved classes remain separate',
                                                      'Greenlight to DME 2024Q1 scope transition is not attributed to trades or price changes',
                                                      'Teva ADS to ordinary share one-for-one conversion; preserve original CUSIPs',
                                                      'Tudor 2022Q4 and 2023Q1 cover counts use exact-content exceptions verified against standalone XML',
                                                      'PDD/DBV/YPF/JD ADS text aliases; AAL/XLF text aliases',
                                                      'Wave Y95308105 to 94352A104 one-for-one redomestication',
                                                      'LRCX 512807108 to 512807306 ten-for-one split; class COM/COM NEW aliases',
                                                      'Barrick and Liberty parent-security CUSIP changes; distributions recorded separately',
                                                      'LEN.B CUSIP 526057302 fixes mislabeled historical class A',
                                                      'Berkshire 0000950123-25-008361 LEN.B +202 explicit additive amendment',
                                                      'Pershing old/new CIK holdings intervals are disjoint; retain notices and NEW HOLDINGS amendments',
                                                      'Nextpower same-CUSIP CLASS A COM/COM aliases; CP and HHC/HHH one-for-one continuations',
                                                      'ChargePoint CUSIP change plus documented 1-for-20 reverse split',
                                                      'Altimeter 0001541617-26-000010 exact-content cover exception; original rows never altered',
                                                      'GRABW G4124C117 is a warrant, not GRAB ordinary stock; low implied warrant value is not an amount anomaly']}
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
        for source in data.get('submission_evidence_list', []):
            content = (stage / source['path']).read_bytes()
            if digest(content) != source['sha256']:
                raise ValueError('Submission evidence changed: ' + source['path'])
            prepared.append((target / source['path'], content))
        prepared.append((target / f'{key}.json', json_bytes(data)))
    # Preflight every target before writing anything: immutable conflicts do not
    # leave a half-written new batch behind.
    for source in sorted((stage / 'quote-evidence').glob('*')):
        if source.is_file():
            prepared.append((target / 'quote-evidence' / source.name, source.read_bytes()))
    if (stage / 'quote-overrides.json').exists():
        prepared.append((target / 'quote-overrides.json', (stage / 'quote-overrides.json').read_bytes()))
    for name in ('class-overrides.json', 'mapping-overrides.json'):
        if (stage / name).exists():
            prepared.append((target / name, (stage / name).read_bytes()))
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
    if any(key not in ALL_MANAGERS for key in args.keys):
        parser.error('Unknown institution')
    {'normalize': normalize, 'enrich': enrich, 'freeze': freeze}[args.action](args)


if __name__ == '__main__':
    main()
