#!/usr/bin/env python3
"""Fnsoko Money Planner tools.

Subcommands
  check   planner.xlsx                      -> what the planner holds (version, categories, rules, accounts)
  parse   FILES... --out parsed.json        -> read statements (M-Pesa / bank, CSV / XLSX / PDF) into clean rows
  sort    parsed.json --planner P --out S   -> apply My Rules, find own-account transfers, fees, reversals, refunds
  write   sorted.json --planner P --answers A --out NEW.xlsx -> write rows, new rules and closing balances
  export  sorted.json [--answers A]         -> paste-ready text for Google Sheets
  log     --folder F --mode M ...           -> opt-in, anonymous usage line (no names, no amounts)

Privacy: account numbers, phone numbers, receipt codes and full personal names never leave the parse step.
Receipt codes are kept only as a one-way hash to catch duplicate statements.
"""
import argparse, csv, datetime as dt, hashlib, io, json, os, re, sys
from collections import defaultdict, OrderedDict

# Planner versions this skill can read and write, newest first. Policy: the current version and the
# one before it. When a new planner version comes out, add it at the front, keep the previous one,
# and drop the one before that. If the new version moves a cell this script reads or writes
# (Setup categories, My Rules, Money Log, Month-End accounts, My Emergency Fund H11, My Goals C15:C26),
# branch on info['version'] where that cell is used. See references/maintenance.md.
SUPPORTED_VERSIONS = ('FNSOKO-PLANNER-v5',)
CURRENT_VERSION = SUPPORTED_VERSIONS[0]
EXPECTED_VERSION = CURRENT_VERSION  # kept for older callers


def version_status(ver):
    """'current', 'previous' (both supported), 'older' (too old to write to) or 'unknown' (newer or not a planner)."""
    if ver == CURRENT_VERSION:
        return 'current'
    if ver in SUPPORTED_VERSIONS:
        return 'previous'
    m = re.fullmatch(r'FNSOKO-PLANNER-v(\d+)', str(ver or '').strip())
    cur = int(re.search(r'(\d+)$', CURRENT_VERSION).group(1))
    if m and int(m.group(1)) < cur:
        return 'older'
    return 'unknown'


def require_supported(ver, nothing_written=False):
    if ver not in SUPPORTED_VERSIONS:
        tail = ' Nothing was written.' if nothing_written else ''
        fail('VERSION', f"Planner version {ver} is not one this skill can write to ({', '.join(SUPPORTED_VERSIONS)}).{tail}")
SPECIALS = ['Transfer between my accounts', 'Cash withdrawal', 'From my emergency fund', 'From my savings', 'Borrowed money']
GROUP_COLS = OrderedDict([('Income', 'B'), ('Bills', 'C'), ('Everyday', 'D'), ('Savings', 'E'), ('Debt', 'F')])


# ----------------------------------------------------------------------------- helpers
def fail(code, msg):
    print(json.dumps({'ok': False, 'error': code, 'message': msg}, ensure_ascii=False))
    sys.exit(2)


def to_amount(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).strip()
    if not s or s in ('-', '--'):
        return None
    neg = s.startswith('(') and s.endswith(')') or s.startswith('-') or s.upper().endswith('DR')
    s = re.sub(r'[^0-9.]', '', s)
    if not s or s == '.':
        return None
    try:
        x = float(s)
    except ValueError:
        return None
    return -x if neg else x


DATE_FORMATS = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%d/%m/%Y %H:%M:%S', '%d/%m/%Y %H:%M', '%d/%m/%Y',
                '%d-%m-%Y', '%d.%m.%Y', '%d/%m/%y', '%d-%b-%Y', '%d %b %Y', '%d-%b-%y', '%d %B %Y', '%b %d, %Y']


def to_date(v):
    if v is None:
        return None
    if isinstance(v, dt.datetime):
        return v
    if isinstance(v, dt.date):
        return dt.datetime(v.year, v.month, v.day)
    s = str(v).strip()
    for f in DATE_FORMATS:
        try:
            return dt.datetime.strptime(s, f)
        except ValueError:
            pass
    m = re.match(r'(\d{4}-\d{2}-\d{2})', s)
    if m:
        return dt.datetime.strptime(m.group(1), '%Y-%m-%d')
    return None


def norm(s):
    return re.sub(r'[^a-z0-9]', '', str(s or '').lower())


# ----------------------------------------------------------------------------- privacy cleaning
RE_RECEIPT = re.compile(r'\b(?=[A-Z0-9]{10}\b)(?=[A-Z0-9]*\d)(?=[A-Z0-9]*[A-Z])[A-Z0-9]{10}\b')
RE_PHONE = re.compile(r'(\+?254|\b0)\s?[17]\d{2}[\s*xX]*\d{0,3}[\s*xX]*\d{3}\b|\b254[17]\d{8}\b|\b0[17]\d{2}\*+\d{3}\b|\b\d{3,6}\*{2,}\d{2,4}\b')
RE_LONGNUM = re.compile(r'\b\d{8,}\b')
OWN_NAMES = []   # the account holder's own name words, removed everywhere
RE_ACC = re.compile(r'\b(acc(?:ount)?\.?\s*(?:no\.?)?\s*[:#]?\s*)[\w-]+', re.I)
PERSON_PATTERNS = [r'customer transfer(?! of funds charge)', r'funds received from', r'send money', r'received from', r'sent to',
                   r'transfer to', r'transfer from', r'p2p']
BUSINESS_PATTERNS = [r'merchant payment', r'pay ?bill', r'buy goods', r'till', r'business payment', r'salary payment',
                     r'pos ', r'online payment']


def normalise_raw(raw):
    s = ' '.join(str(raw or '').replace('|', ' ').split())
    s = re.sub(r'exchange rate\s+\S+', ' ', s, flags=re.I)                              # bank noise
    s = re.sub(r'\b\d{2}-\d{2}-\d{4}\s*/\s*\d{2}:\d{2}(:\d{2})?', ' ', s)                 # card date/time stamps
    s = re.sub(r'\b\d{2}-\d{2}-\d{4}\s+\d{6,8}\b', ' ', s)                               # masked card numbers
    s = re.sub(r'\+\d{8,}', ' ', s)                                                       # international phone numbers
    s = re.sub(r'\bKE-[A-Z0-9-]{6,}\b', ' ', s, flags=re.I)                               # bank transfer references
    s = re.sub(r'\b\w*\d{10,}\w*\b', ' ', s)                                             # long IDs with letters
    s = re.sub(r'\b[A-Z]{1,4}\d{5,}(?:-\d+)*\b', ' ', s)                                   # reference codes like RD2645609-106074
    s = re.sub(r'^(debit card txn at|card purchase at|pos purchase|pos)\s+', '', s, flags=re.I)
    s = re.sub(r'\bfuliza\s*m-?\s?pesa\b', ' ', s, flags=re.I)          # payments made with Fuliza: sort by who was paid
    s = re.sub(r'\b(salary|business) payment from\b', 'Payment from', s, flags=re.I)   # M-Pesa B2C label, not proof of salary
    s = re.sub(r'\s*via API\.?.*$', '', s, flags=re.I)
    s = re.sub(r'original conversation id( is)?\s*\S+', '', s, flags=re.I)
    for nm in OWN_NAMES:
        s = re.sub(r'\b' + re.escape(nm) + r'\b', '', s, flags=re.I)
    return ' '.join(s.split())


def short_person(name):
    words = [w for w in re.findall(r"[A-Za-z']+", name) if len(w) > 1]
    if not words:
        return ''
    if len(words) == 1:
        return words[0].upper()
    return f'{words[0].upper()} {words[1][0].upper()}'


def clean_details(raw):
    """Return (note, counterparty, kind, paybill). Removes codes, phones, account numbers; shortens personal names."""
    s = normalise_raw(raw)
    paybill = None
    m = re.search(r'(?:pay ?bill|merchant payment(?: online)?|buy goods|till)\s*(?:to|no\.?)?\s*(\d{5,7})', s, re.I)
    if m:
        paybill = m.group(1)
    s2 = RE_ACC.sub('', s)
    s2 = RE_RECEIPT.sub('', s2)
    s2 = RE_PHONE.sub('', s2)
    s2 = RE_LONGNUM.sub('', s2)
    low = s2.lower()
    kind = 'other'
    if any(re.search(p, low) for p in PERSON_PATTERNS):
        kind = 'person'
    elif any(re.search(p, low) for p in BUSINESS_PATTERNS):
        kind = 'business'
    if re.search(r'charge|transaction cost|excise|stamp duty|ledger fee|service fee|commission|maintenance fee', low):
        kind = 'fee'
    counterparty = ''
    if ' - ' in s2:
        counterparty = s2.split(' - ', 1)[1].strip()
    elif kind == 'person':
        counterparty = re.sub('|'.join(PERSON_PATTERNS), '', low, flags=re.I).strip().upper()
    counterparty = re.sub(r'\s+', ' ', re.sub(r'[^A-Za-z0-9&\'. -]', ' ', counterparty)).strip(' .-')
    counterparty = re.sub(r'\s+acc\.?$', '', counterparty, flags=re.I)              # account label left after its number was removed
    if kind == 'person':
        counterparty = short_person(counterparty)
    head = s2.split(' - ', 1)[0]
    outward = bool(re.search(r'\b(to|sent)\b', head.lower()))
    head = re.sub(r'\b(to|from)\s*$', '', re.sub(r'\s+', ' ', re.sub(r'[\d*]+', '', head))).strip(' .-')
    if kind == 'person':
        note = ('Sent to ' if outward else 'From ') + counterparty if counterparty else head
    else:
        note = counterparty if (counterparty and kind == 'business') else (head + (' ' + counterparty if counterparty else '')).strip()
    note = re.sub(r'\s+', ' ', note).strip()[:60]
    return note, counterparty.upper(), kind, paybill


def head_of(raw):
    h = normalise_raw(raw).split(' - ', 1)[0]
    h = re.sub(r'[\d*+]+', ' ', RE_PHONE.sub(' ', h))
    return re.sub(r'\s+', ' ', re.sub(r'\b(to|from)\s*$', '', h.strip(), flags=re.I)).strip().upper()[:40]


# ----------------------------------------------------------------------------- reading files
HEAD = {
    'receipt': ['receipt no', 'receipt', 'transaction id', 'trans id', 'reference', 'ref no', 'ref'],
    'date': ['completion time', 'transaction date', 'txn date', 'trans date', 'entry date', 'posting date', 'post date', 'book date',
             'date', 'initiation time', 'value date'],
    'details': ['details', 'narrative', 'description', 'particulars', 'transaction details', 'narration', 'remarks'],
    'status': ['transaction status', 'status'],
    'in': ['paid in', 'money in', 'credit', 'credits', 'deposits', 'deposit', 'cr', 'credit amount'],
    'out': ['withdrawn', 'money out', 'debit', 'debits', 'withdrawals', 'withdrawal', 'dr', 'paid out', 'debit amount'],
    'amount': ['amount', 'transaction amount'],
    'balance': ['balance', 'running balance', 'ledger balance', 'book balance', 'available balance', 'closing balance'],
    'currency': ['currency', 'ccy'],
}


def map_header(cells):
    cols = {}
    low = [str(c or '').strip().lower() for c in cells]
    clean = [re.sub(r'\s+', ' ', re.sub(r'\s*\(.*\)$', '', h)) for h in low]
    for exact in (True, False):            # exact names first, then names squashed into a neighbour (e.g. 'tuspaid in')
        for key, names in HEAD.items():
            for i, hh in enumerate(clean):
                if key in cols or i in cols.values():
                    continue
                if (hh in names) if exact else any(len(n) > 4 and n in hh for n in names):
                    cols[key] = i
    if 'date' in cols and 'details' in cols and ('in' in cols or 'out' in cols or 'amount' in cols):
        cur = None
        for h in low:
            m = re.search(r'\(([a-z]{3})\)', h)
            if m:
                cur = m.group(1).upper()
        return cols, cur
    return None, None


def rows_from_table(table, src, account, kind_hint, currency):
    out, cols, cur, fixed = [], None, None, False
    for row in table:
        if cols is None:
            cols, cur = map_header(row)
            if cols is not None:
                low = ' '.join(str(c or '').lower() for c in row)
                if 'receipt' in low and 'paid in' in low and 'withdrawn' in low:
                    kind_hint = 'M-Pesa'
            continue
        if not row or all(c in (None, '') for c in row):
            continue
        if not out and not fixed:
            fixed = True
            if to_date(row[0]) and cols.get('date') != 0 and 0 not in cols.values():
                cols['date'] = 0                      # an unnamed first column holding the entry date
            last = len(row) - 1
            if 'balance' not in cols and last not in cols.values() and to_amount(row[last]) is not None:
                cols['balance'] = last                # an unnamed last column holding the running balance
        joined = ' '.join(str(c or '') for c in row).lower()
        if re.search(r'closing balance|balance from previous|opening balance|balance b/?f|balance c/?f|brought forward|carried forward', joined):
            continue
        g = lambda k: row[cols[k]] if k in cols and cols[k] < len(row) else None
        d = to_date(g('date'))
        if d is None:
            if out and g('details'):          # wrapped description line
                out[-1]['raw'] += ' ' + str(g('details'))
            continue
        a_in, a_out = to_amount(g('in')), to_amount(g('out'))
        if 'amount' in cols and a_in is None and a_out is None:
            a = to_amount(g('amount'))
            if a is not None:
                a_in, a_out = (a, None) if a > 0 else (None, -a)
        if a_out is not None and a_out < 0:
            a_out = -a_out
        if a_in is not None and a_in < 0:
            a_out, a_in = -a_in, None
        if not a_in and not a_out:
            continue
        status = str(g('status') or 'Completed')
        out.append({'source': os.path.basename(src), 'account': account, 'account_type': kind_hint,
                    'currency': (str(g('currency')).upper() if g('currency') else None) or cur or currency,
                    'date': d, 'raw': str(g('details') or ''), 'status': status,
                    'in': round(a_in or 0, 2), 'out': round(a_out or 0, 2), 'balance': to_amount(g('balance')),
                    'receipt': str(g('receipt') or '')})
    for r in out:
        r['account_type'] = kind_hint
    return out, cols is not None


MPESA_LINE = re.compile(r'^([A-Z0-9]{10})\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}(?::\d{2})?)\s+(.*?)\s+(Completed|Failed|Reversed)\s+'
                        r'(-?[\d,]+\.\d{2})\s+(?:(-?[\d,]+\.\d{2})\s+)?(-?[\d,]+\.\d{2})?\s*$')


def rows_from_mpesa_text(text, src, account, currency):
    out = []
    for line in text.splitlines():
        line = line.strip()
        m = MPESA_LINE.match(line)
        if m:
            rec, when, det, status, a1, a2, bal = m.groups()
            nums = [to_amount(x) for x in (a1, a2) if x]
            a_in = a_out = 0.0
            if len(nums) == 2:
                a_in, a_out = abs(nums[0] or 0), abs(nums[1] or 0)
            elif nums:
                a_out = abs(nums[0]) if nums[0] < 0 else 0
                a_in = nums[0] if nums[0] > 0 else 0
            out.append({'source': os.path.basename(src), 'account': account, 'account_type': 'M-Pesa', 'currency': currency,
                        'date': to_date(when), 'raw': det, 'status': status, 'in': a_in, 'out': a_out,
                        'balance': to_amount(bal), 'receipt': rec})
        elif out and line and not re.match(r'^(page|receipt|m-pesa|statement|customer|mobile|email|date of|disclaimer)', line, re.I):
            if len(line) < 80 and not re.search(r'\d{1,3}(,\d{3})*\.\d{2}', line):
                out[-1]['raw'] += ' ' + line
    return out


def read_pdf(path):
    try:
        from pypdf import PdfReader
        r = PdfReader(path)
        if r.is_encrypted:
            return None, 'LOCKED'
    except Exception:
        pass
    tables, text = [], ''
    try:
        import pdfplumber
        with pdfplumber.open(path) as pdf:
            for p in pdf.pages:
                for t in p.extract_tables() or []:
                    tables.append(t)
                text += (p.extract_text() or '') + '\n'
    except Exception as e:
        if 'password' in str(e).lower() or 'encrypt' in str(e).lower():
            return None, 'LOCKED'
        try:
            import subprocess
            text = subprocess.run(['pdftotext', '-layout', path, '-'], capture_output=True, text=True).stdout
        except Exception:
            text = ''
    if not tables and not text.strip():
        return None, 'NO_TEXT'
    return (tables, text), None


def guess_account(path, header_text):
    name = os.path.basename(path).lower()
    blob = (name + ' ' + header_text[:300].lower())
    if 'mpesa' in name.replace('-', '') or 'safaricom' in name:
        return 'M-Pesa', 'M-Pesa'
    if re.search(r'receipt no.*paid in.*withdrawn', header_text.lower().replace('\n', ' ')) or 'm-pesa statement' in blob:
        return 'M-Pesa', 'M-Pesa'
    for short, full in (('scb', 'Standard Chartered'), ('stanchart', 'Standard Chartered'), ('ncba', 'NCBA'),
                        ('kcb', 'KCB'), ('coop', 'Co-op'), ('im_', 'I&M'), ('dtb', 'DTB')):
        if re.search(r'(^|[^a-z])' + re.escape(short), name):
            return full, 'Bank'
    for bank in ['equity', 'kcb', 'co-op', 'coop', 'cooperative', 'ncba', 'absa', 'stanbic', 'dtb', 'i&m', 'family', 'stanchart',
                 'standard chartered', 'barclays', 'monzo', 'revolut', 'wise', 'hsbc', 'lloyds', 'chase']:
        if bank in blob:
            return bank.replace('coop', 'Co-op').title() if bank != 'i&m' else 'I&M', 'Bank'
    m = re.search(r'\b([A-Z][A-Z&]{2,})\s+BANK\b', header_text[:600])
    if m and m.group(1) not in ('THE', 'YOUR', 'MOBILE', 'ONLINE', 'INTERNET', 'SAMPLE'):
        return m.group(1).title() + ' Bank', 'Bank'
    return os.path.splitext(os.path.basename(path))[0][:24], 'Bank'


def learn_own_name(text):
    """The account holder's name, from 'Customer Name:' or the address block at the top of a bank statement."""
    found = []
    m = re.search(r'(?:customer|account|client)\s*name\s*:?\s*([A-Za-z][A-Za-z \'.-]{2,60})', text[:3000], re.I)
    if m:
        found = re.findall(r"[A-Za-z']{3,}", m.group(1).split('\n')[0])
    else:
        for line in text[:1500].splitlines()[:12]:
            first = re.split(r'\s{3,}', line.strip())[0]
            words = re.findall(r"[A-Za-z']+", first)
            if 2 <= len(words) <= 4 and first.isupper() and not re.search(
                    r'STATEMENT|ACCOUNT|BANK|BOX|KENYA|NAIROBI|BRANCH|LIMITED|LTD|PERIOD|DATE|CURRENT|SAVINGS', first):
                found = words
                break
    for w in found:
        if len(w) >= 3 and w.lower() not in ('mobile', 'number', 'email', 'address', 'mrs', 'miss') \
                and w.upper() not in [x.upper() for x in OWN_NAMES]:
            OWN_NAMES.append(w)


def file_text(path):
    ext = os.path.splitext(path)[1].lower()
    try:
        if ext == '.pdf':
            import subprocess
            return subprocess.run(['pdftotext', '-l', '1', '-layout', path, '-'], capture_output=True, text=True).stdout
        if ext in ('.csv', '.txt'):
            return open(path, encoding='utf-8-sig', errors='replace').read(3000)
    except Exception:
        pass
    return ''


def parse_file(path, account=None, currency=None):
    ext = os.path.splitext(path)[1].lower()
    tables, text = [], ''
    if ext == '.pdf':
        res, err = read_pdf(path)
        if err:
            return [], err
        tables, text = res
    elif ext in ('.csv', '.txt'):
        with open(path, newline='', encoding='utf-8-sig', errors='replace') as f:
            raw = f.read()
        try:
            dialect = csv.Sniffer().sniff(raw[:2000], delimiters=',;\t')
        except csv.Error:
            dialect = csv.excel
        tables = [list(csv.reader(io.StringIO(raw), dialect))]
        text = raw[:3000]
    elif ext in ('.xlsx', '.xls'):
        import pandas as pd
        for _, df in pd.read_excel(path, header=None, sheet_name=None).items():
            tables.append(df.where(df.notna(), None).values.tolist())
    else:
        return [], 'UNKNOWN_TYPE'
    acc, acc_type = guess_account(path, text[:1500])
    learn_own_name(text)
    if account:
        acc = account
    rows, found = [], False
    for t in tables:
        r, ok = rows_from_table(t, path, acc, acc_type, currency)
        rows += r
        found = found or ok
    if not rows and text:
        rows = rows_from_mpesa_text(text, path, acc, currency)
        if rows:
            acc_type = 'M-Pesa'
    if not rows:
        return [], 'NO_ROWS'
    types = {r['account_type'] for r in rows}
    if 'M-Pesa' in types and acc_type != 'M-Pesa' and not account:
        acc = 'M-Pesa'
    for r in rows:
        r['account_type'] = 'M-Pesa' if 'M-Pesa' in types else acc_type
        r['account'] = acc
    return rows, None


def finish_rows(rows, fx):
    out = []
    for r in rows:
        note, cp, kind, paybill = clean_details(r['raw'])
        cur = (r.get('currency') or 'KES').upper()
        rate = 1.0
        if cur != 'KES':
            rate = fx.get(cur)
        h = hashlib.sha1(f"{r['receipt']}|{r['account']}|{r['date']}|{r['raw'][:25]}|{r['in']}|{r['out']}|{r['balance']}".encode()).hexdigest()[:16]
        out.append({'account': r['account'], 'account_type': r['account_type'], 'currency': cur, 'fx_rate': rate,
                    'date': r['date'].strftime('%Y-%m-%d %H:%M:%S'), 'status': r['status'],
                    'in': round(r['in'] * rate, 2) if rate else r['in'], 'out': round(r['out'] * rate, 2) if rate else r['out'],
                    'balance': round(r['balance'] * rate, 2) if (r['balance'] is not None and rate) else r['balance'],
                    'note': note, 'counterparty': cp, 'kind': kind, 'paybill': paybill,
                    'match_text': (r['raw_upper_clean']), 'dup_key': h, 'source': r['source'], 'head': head_of(r['raw'])})
    return out


def cmd_parse(a):
    fx = {}
    for item in a.fx or []:
        k, v = item.split('=')
        fx[k.upper()] = float(v)
    files = []
    for p in a.files:
        if os.path.isdir(p):
            files += [os.path.join(p, f) for f in sorted(os.listdir(p)) if not f.startswith('.')]
        else:
            files.append(p)
    all_rows, problems, statements = [], [], []
    for f in files:
        learn_own_name(file_text(f))
    if a.me:
        OWN_NAMES.extend(w for w in re.findall(r"[A-Za-z']{3,}", a.me) if w not in OWN_NAMES)
    for f in files:
        rows, err = parse_file(f, a.account, a.currency)
        if err:
            problems.append({'file': os.path.basename(f), 'problem': err, 'what_to_do': {
                'LOCKED': 'This statement is password-protected. Open it yourself and save an unlocked copy (Print > Save as PDF). Never share the password.',
                'NO_TEXT': 'This looks like a scan or photo. Download the digital statement (PDF or CSV) from your bank or M-Pesa app instead.',
                'NO_ROWS': 'I could not find a transactions table. Try the CSV or Excel download, or tell me the column names.',
                'UNKNOWN_TYPE': 'Use PDF, CSV or Excel statements.'}[err]})
            continue
        for r in rows:
            r['raw_upper_clean'] = ''
        for r in rows:
            note, cp, kind, pb = clean_details(r['raw'])
            r['raw_upper_clean'] = ' '.join(x for x in [head_of(r['raw']), note.upper(), cp, ('PAYBILL ' + pb) if pb else '', kind.upper()] if x)
        cur = {(r.get('currency') or 'KES').upper() for r in rows}
        missing_fx = [c for c in cur if c != 'KES' and c not in fx]
        if missing_fx:
            problems.append({'file': os.path.basename(f), 'problem': 'NEEDS_RATE', 'currency': missing_fx,
                             'what_to_do': f'Ask: what rate should I use to turn {", ".join(missing_fx)} into KES? (e.g. 1 GBP = 165 KES)'})
            continue
        clean = finish_rows(rows, fx)
        ds = sorted(r['date'] for r in clean)
        statements.append({'file': os.path.basename(f), 'account': clean[0]['account'], 'account_type': clean[0]['account_type'],
                           'currency': clean[0]['currency'], 'from': ds[0][:10], 'to': ds[-1][:10], 'rows': len(clean)})
        all_rows += clean
    res = {'ok': True, 'statements': statements, 'problems': problems, 'transactions': all_rows}
    with open(a.out, 'w') as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    print(json.dumps({'ok': True, 'statements': statements, 'problems': problems, 'transactions': len(all_rows)}, ensure_ascii=False))


# ----------------------------------------------------------------------------- reading the planner
def load_planner(path, data_only=False):
    from openpyxl import load_workbook
    return load_workbook(path, data_only=data_only)


def planner_info(path):
    wb = load_planner(path)
    ver = wb['Workings']['C205'].value if 'Workings' in wb.sheetnames else None
    su = wb['Setup']
    cats = OrderedDict((g, [su[f'{c}{r}'].value.strip() for r in range(13, 28) if su[f'{c}{r}'].value]) for g, c in GROUP_COLS.items())
    rules = []
    rl = wb['My Rules']
    r = 12
    for r in range(12, 312):
        k, c = rl[f'B{r}'].value, rl[f'C{r}'].value
        if k and c:
            rules.append({'row': r, 'keyword': str(k).strip().upper(), 'category': str(c).strip()})
    ef = wb['My Emergency Fund']['H11'].value
    goals = [wb['My Goals'][f'C{r}'].value for r in range(15, 27) if wb['My Goals'][f'C{r}'].value]
    ml = wb['Money Log']
    existing, last = [], 9
    for r in range(10, 2010):
        b, c, d = ml[f'B{r}'].value, ml[f'C{r}'].value, ml[f'D{r}'].value
        if b or c or d:
            last = r
            dd = to_date(b)
            existing.append({'date': dd.strftime('%Y-%m-%d') if dd else None, 'category': c, 'amount': d})
    me = wb['Month-End Check']
    accounts = [{'row': r, 'name': me[f'B{r}'].value, 'type': me[f'C{r}'].value} for r in range(16, 24)]
    year = su['C6'].value
    return {'version': ver, 'year': year, 'currency': su['C7'].value, 'categories': cats, 'specials': SPECIALS,
            'rules': rules, 'ef_category': ef, 'goals': goals, 'existing': existing, 'last_row': last,
            'accounts': accounts}, wb


def cmd_check(a):
    info, _ = planner_info(a.planner)
    status = version_status(info['version'])
    ok = status in ('current', 'previous')
    all_cats = set(sum(info['categories'].values(), [])) | set(SPECIALS)
    broken = [x for x in info['rules'] if x['category'] not in all_cats]
    out = {'ok': ok, 'version': info['version'], 'version_status': status, 'supported': list(SUPPORTED_VERSIONS),
           'current': CURRENT_VERSION, 'year': info['year'], 'currency': info['currency'],
           'categories': info['categories'], 'ef_category': info['ef_category'], 'goals': info['goals'],
           'rules': len(info['rules']), 'broken_rules': broken[:10], 'money_log_rows': len(info['existing']),
           'last_date_logged': max([e['date'] for e in info['existing'] if e['date']], default=None),
           'accounts': [x for x in info['accounts'] if x['name']]}
    if status == 'previous':
        out['message'] = ('This planner is the previous version. Work with it as normal. At the end, mention once that a '
                          'newer planner is available and offer to help move their numbers across. Never push it.')
    elif status == 'older':
        out['message'] = ('This planner is older than this skill can write to. Do not write to it. Keep coaching from what '
                          'it shows, and offer to walk them through copying their white boxes into the latest planner.')
    elif not ok:
        out['message'] = ('This planner is newer than this skill, or not a Fnsoko planner. Do not write to it. Ask them to '
                          'update the Fnsoko Money Skills plugin (Customize > Plugins > Check for updates), then try again.')
    print(json.dumps(out, indent=1, ensure_ascii=False, default=str))


# ----------------------------------------------------------------------------- sorting
def group_of(cat, cats):
    for g, lst in cats.items():
        if cat in lst:
            return g
    return 'Special' if cat in SPECIALS else None


def find_cat(cats, *words):
    for g in cats.values():
        for c in g:
            if any(w in c.lower() for w in words):
                return c
    return None


def cmd_sort(a):
    parsed = json.load(open(a.parsed))
    info, _ = planner_info(a.planner)
    require_supported(info['version'])
    cats = info['categories']
    fees_cat = next((c for c in cats.get('Bills', []) + cats.get('Everyday', []) if re.search(r'(bank|m-?pesa).*(fee|charge)|(fee|charge).*(bank|m-?pesa)', c.lower())), None)
    pool = [t for t in parsed['transactions'] if not a.month or t['date'][:7] in a.month]
    tx = [t for t in pool if t['status'].lower().startswith('complet')]
    failed = len(pool) - len(tx)
    for t in tx:
        t['dt'] = dt.datetime.strptime(t['date'], '%Y-%m-%d %H:%M:%S')
        t['amt'] = t['in'] or t['out']
        t['dir'] = 'in' if t['in'] else 'out'
        t['cat'] = None
        t['why'] = None
    # 1. duplicates across overlapping statements
    seen, uniq, dups = set(), [], 0
    for t in sorted(tx, key=lambda x: x['dt']):
        if t['dup_key'] in seen:
            dups += 1
            continue
        seen.add(t['dup_key'])
        uniq.append(t)
    tx = uniq
    # 2. reversals cancel their original
    reversed_pairs = 0
    for t in tx:
        if t['cat'] is None and re.search(r'revers', t['match_text'], re.I):
            cands = [o for o in tx if o is not t and o['cat'] is None and o['account'] == t['account'] and o['amt'] == t['amt']
                     and o['dir'] != t['dir'] and abs((o['dt'] - t['dt']).days) <= 7]
            if cands:
                o = min(cands, key=lambda o: abs((o['dt'] - t['dt']).total_seconds()))
                t['cat'] = o['cat'] = '__drop__'
                t['why'] = o['why'] = 'reversal'
                reversed_pairs += 1
    # 3. transfers between own accounts (different statements, same amount, opposite direction, within 2 days)
    transfers = 0
    accounts = {t['account'] for t in tx}
    if len(accounts) > 1:
        for t in tx:
            if t['cat'] or t['dir'] != 'out' or t['kind'] == 'fee':
                continue
            cands = [o for o in tx if o['cat'] is None and o['dir'] == 'in' and o['account'] != t['account']
                     and abs(o['amt'] - t['amt']) < 0.01 and abs((o['dt'] - t['dt']).total_seconds()) <= 2 * 86400]
            if cands:
                o = min(cands, key=lambda o: abs((o['dt'] - t['dt']).total_seconds()))
                t['cat'] = 'Transfer between my accounts'
                t['why'] = 'own-account move'
                t['note'] = f"{t['account']} to {o['account']}"
                o['cat'] = '__drop__'
                o['why'] = 'other side of a transfer'
                transfers += 1
    # 4. rules (first match wins) + built-in patterns, direction-aware
    all_cats = set(sum(cats.values(), [])) | set(SPECIALS)
    for t in tx:
        if t['cat']:
            continue
        text = t['match_text'].upper()
        hit = next((r for r in info['rules'] if r['keyword'] and re.search(r'(?<![A-Z0-9])' + re.escape(r['keyword']) + r'(?![A-Z0-9])', text)), None)
        cat = hit['category'] if hit and hit['category'] in all_cats else None
        if hit and not cat:
            t['why'] = f"rule '{hit['keyword']}' points to a missing category"
        if cat is None:
            low = text.lower()
            if re.search(r'agent|atm', low) and re.search(r'withdraw|wdl|cash', low) and t['dir'] == 'out':
                cat = 'Cash withdrawal'
            elif re.search(r'overdraft of credit party|fuliza', low) and t['dir'] == 'in':
                cat = 'Borrowed money'
            elif t['kind'] == 'fee' and fees_cat:
                cat = fees_cat
            elif re.search(r'salary', low) and t['dir'] == 'in':
                cat = find_cat(cats, 'salary')
            elif re.search(r'airtime|bundle', low) and t['dir'] == 'out':
                cat = find_cat(cats, 'airtime')
        if cat:
            g = group_of(cat, cats)
            if t['dir'] == 'in' and g == 'Debt':
                cat = 'Borrowed money'
            elif t['dir'] == 'in' and g == 'Savings':
                cat = 'From my emergency fund' if cat == info['ef_category'] else 'From my savings'
            elif t['dir'] == 'in' and g in ('Bills', 'Everyday'):
                t['why'] = 'money back from a shop: refund?'
                cat = None
            elif t['dir'] == 'out' and g == 'Income':
                t['why'] = 'income category on money going out'
                cat = None
            elif t['dir'] == 'in' and cat in ('Cash withdrawal', 'Transfer between my accounts') and len(accounts) == 1:
                t['why'] = 'money in that looks like a move: from where?'
                cat = None
        t['cat'] = cat
        if cat and not t['why']:
            t['why'] = f"rule '{hit['keyword']}'" if hit and hit['category'] in all_cats else 'built-in pattern'
    # 5. refunds: pair with an earlier purchase from the same counterparty and amount within 60 days
    refunds = 0
    for t in tx:
        if t['cat'] is None and t['why'] == 'money back from a shop: refund?':
            cands = [o for o in tx if o['dir'] == 'out' and o['cat'] not in (None, '__drop__') and o['amt'] == t['amt']
                     and o['counterparty'] == t['counterparty'] and 0 <= (t['dt'] - o['dt']).days <= 60]
            if cands:
                o = cands[-1]
                o['cat'] = t['cat'] = '__drop__'
                o['why'] = t['why'] = 'refunded'
                refunds += 1
    # 6. build ready rows (fees grouped per account per month)
    ready, fee_buckets = [], defaultdict(float)
    micro = defaultdict(list)
    for t in tx:
        if t['cat'] not in (None, '__drop__') and t['dir'] == 'out' and group_of(t['cat'], cats) == 'Savings':
            micro[(t['cat'], t['note'], t['account'], t['dt'].strftime('%Y-%m'))].append(t)
    for (cat_, note_, acc_, ym), items in micro.items():
        if len(items) >= 5:
            y, m = map(int, ym.split('-'))
            last = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)).isoformat()
            ready.append({'date': min(last, max(i['dt'] for i in items).strftime('%Y-%m-%d')), 'category': cat_,
                          'amount': round(sum(i['amt'] for i in items), 2), 'note': f'{note_[:40]} ({len(items)} deposits)',
                          'added_by': 'Claude', 'account': acc_, 'why': 'small savings grouped'})
            for i in items:
                i['cat'] = '__grouped__'
    for t in tx:
        if t['cat'] in (None, '__drop__', '__grouped__'):
            continue
        if fees_cat and t['cat'] == fees_cat and t['dir'] == 'out':
            fee_buckets[(t['account'], t['dt'].strftime('%Y-%m'))] += t['amt']
            continue
        ready.append({'date': t['dt'].strftime('%Y-%m-%d'), 'category': t['cat'], 'amount': round(t['amt'], 2),
                      'note': t['note'], 'added_by': 'Claude', 'account': t['account'], 'why': t['why']})
    for (acc, ym), amt in fee_buckets.items():
        y, m = map(int, ym.split('-'))
        last = (dt.date(y + (m == 12), m % 12 + 1, 1) - dt.timedelta(days=1)).isoformat()
        ready.append({'date': last, 'category': fees_cat, 'amount': round(amt, 2), 'note': f'{acc} fees for the month',
                      'added_by': 'Claude', 'account': acc, 'why': 'fees grouped'})
    # 7. questions, grouped by counterparty + direction, biggest first
    groups = OrderedDict()
    for t in tx:
        if t['cat'] is not None:
            continue
        key = (t['counterparty'] or re.sub(r'\d', '', t['note']).strip().upper()[:40] or 'UNKNOWN', t['dir'])
        g = groups.setdefault(key, {'items': [], 'why': t['why']})
        g['items'].append(t)
    by_head = defaultdict(list)
    for k, g in groups.items():
        if len(g['items']) == 1 and g['items'][0]['kind'] != 'fee':
            by_head[(g['items'][0]['head'], k[1])].append(k)
    for (h, d), keys in by_head.items():
        if h and len(keys) >= 4:
            merged = {'items': [], 'why': f'{len(keys)} different payers, one payment each', 'merged': True}
            for k in keys:
                merged['items'] += groups.pop(k)['items']
            groups[(h, d)] = merged
    income_guess = sum(t['amt'] for t in tx if t['dir'] == 'in' and t['cat'] and group_of(t['cat'], cats) == 'Income')
    months = max(1, len({t['dt'].strftime('%Y-%m') for t in tx}))
    big = 0.1 * income_guess / months if income_guess else None
    questions = []
    for (key, d), g in groups.items():
        kind = g['items'][0]['kind']
        total = round(sum(x['amt'] for x in g['items']), 2)
        inv = re.search(r'\b(UNIT TRUST|MMF|MONEY MARKET|ASSET MANAG|INVEST|SACCO|CHAMA|PENSION|BOND|T-?BILL)', ' '.join(x['match_text'] for x in g['items']).upper())
        bank = re.search(r'\bBANK\b|\bMPESA\b|MOBILE MONEY|\bIBKG\b', ' '.join(x['match_text'] for x in g['items']).upper())
        leisure = re.search(r'RESTAURANT|CAFE|CAFFE|HOTEL|RESORT|LODGE|\bGRILL\b|KITCHEN|EATERY|PIZZA|CHICKEN|BURGER', ' '.join(x['match_text'] for x in g['items']).upper())
        if leisure and d == 'out':
            sug = ['Eating out', 'Entertainment', 'Holidays & travel', 'Gifts & celebrations', 'Miscellaneous']
        elif inv and d == 'out':
            sug = ['Money market fund', 'SACCO savings', 'Emergency fund', 'Shares (NSE)', 'SACCO loan']
        elif inv:
            sug = ['From my savings', 'From my emergency fund', 'Investment income', 'Borrowed money']
        elif bank:
            sug = ['Transfer between my accounts', 'Bank loan', 'Credit card', 'Miscellaneous'] if d == 'out' else \
                  ['Transfer between my accounts', 'Salary', 'Borrowed money', 'Business income']
        elif d == 'out' and kind == 'person':
            sug = ['Family support', 'Rent', 'Gifts & celebrations', 'Side hustle', 'Miscellaneous']
        elif d == 'out':
            sug = ['Groceries', 'Household items', 'Eating out', 'Miscellaneous']
        elif kind == 'person':
            sug = ['Side hustle', 'Gifts received', 'Business income', 'Transfer between my accounts', 'Borrowed money']
        else:
            sug = ['Salary', 'Business income', 'Side hustle', 'From my savings']
        if g['why'] == 'money back from a shop: refund?':
            sug = ['Refund (cancel the purchase)', 'Gifts received', 'Miscellaneous']
        text = ' '.join(x['match_text'] for x in g['items']).upper()
        named = [] if g.get('merged') else [c for c in sorted(all_cats - set(SPECIALS)) if any(len(w) > 3 and re.search(r'\b' + re.escape(w.upper()) + r'\b', text)
                                                     for w in re.findall(r"[A-Za-z]+", c) if w.lower() not in ('fund', 'money', 'payment', 'savings', 'bank', 'from', 'with', 'business', 'income', 'loan', 'loans', 'pesa', 'mpesa'))]
        if 'LOAN' not in text:
            named = [c for c in named if group_of(c, cats) != 'Debt']
        if d == 'in':
            named = [c for c in named if group_of(c, cats) == 'Income']
        if g.get('merged') and d == 'in':
            sug = ['Business income', 'Side hustle', 'Gifts received', 'Transfer between my accounts']
        elif g.get('merged') and kind != 'person':
            sug = ['Miscellaneous', 'Groceries', 'Eating out', 'Household items']
        if d == 'out':
            named = [c for c in named if group_of(c, cats) not in ('Income',) and c not in ('Borrowed money', 'From my savings', 'From my emergency fund')]
        sug = list(dict.fromkeys(named + sug))
        sug = [s for s in sug if s in all_cats or s.startswith('Refund')][:4]
        questions.append({'id': f'q{len(questions) + 1}', 'who': key, 'direction': 'paid' if d == 'out' else 'received',
                          'count': len(g['items']), 'total': total, 'kind': kind, 'reason': g['why'] or 'no rule matched',
                          'big': bool(big and total >= big), 'suggested': sug,
                          'merged': bool(g.get('merged')),
                          'items': [{'date': x['dt'].strftime('%Y-%m-%d'), 'amount': x['amt'], 'note': x['note'],
                                     'account': x['account']} for x in sorted(g['items'], key=lambda x: -x['amt'])],
                          'offer_rule': (key if key != 'UNKNOWN' else None)})
    questions.sort(key=lambda q: (-q['big'], -q['total']))
    for i, q in enumerate(questions):
        q['id'] = f'q{i + 1}'
    # triage: the few questions that explain most of the money, the rest can wait
    tot_q = sum(q['total'] for q in questions) or 1
    run_, ask_now = 0, 0
    for q in questions:
        if run_ / tot_q >= 0.9 and ask_now >= 3:
            break
        run_ += q['total']; ask_now += 1
    ask_now = min(max(ask_now, min(3, len(questions))), 15)
    triage = {'ask_now': [q['id'] for q in questions[:ask_now]],
              'share_of_unsorted_money': round(sum(q['total'] for q in questions[:ask_now]) / tot_q, 2),
              'later': len(questions) - ask_now,
              'later_total': round(sum(q['total'] for q in questions[ask_now:]), 2)}
    # 8. duplicates against what is already on the Money Log
    have = {(e['date'], e['category'], round(float(e['amount']), 2)) for e in info['existing']
            if e['date'] and e['amount'] not in (None, '') and isinstance(e['amount'], (int, float))}
    already = [r for r in ready if (r['date'], r['category'], r['amount']) in have]
    ready = [r for r in ready if (r['date'], r['category'], r['amount']) not in have]
    # 9. closing balances per account per month
    bal = {}
    for t in sorted(tx, key=lambda x: x['dt']):
        if t['balance'] is not None:
            bal[(t['account'], t['account_type'], t['dt'].strftime('%Y-%m'))] = t['balance']
    balances = [{'account': k[0], 'type': k[1], 'month': k[2], 'closing': v} for k, v in sorted(bal.items())]
    outside = [r for r in ready if info['year'] and int(r['date'][:4]) != int(info['year'])]
    ready.sort(key=lambda r: (r['date'], r['category']))
    res = {'ok': True, 'planner_year': info['year'], 'months': sorted({t['dt'].strftime('%Y-%m') for t in tx}),
           'ready': ready, 'questions': questions, 'triage': triage, 'balances': balances,
           'summary': {'transactions': len(pool), 'failed_skipped': failed, 'duplicates_skipped': dups,
                       'reversals_cancelled': reversed_pairs, 'refunds_cancelled': refunds, 'own_transfers': transfers,
                       'ready_rows': len(ready), 'already_on_money_log': len(already), 'questions': len(questions),
                       'ask_now': len(triage['ask_now']), 'ask_later': triage['later'],
                       'outside_planner_year': len(outside), 'money_in': round(sum(r['amount'] for r in ready if group_of(r['category'], cats) == 'Income'), 2),
                       'money_out': round(sum(r['amount'] for r in ready if group_of(r['category'], cats) in ('Bills', 'Everyday', 'Savings', 'Debt')), 2)}}
    with open(a.out, 'w') as fh:
        json.dump(res, fh, indent=1, ensure_ascii=False)
    print(json.dumps(res['summary'], ensure_ascii=False))


# ----------------------------------------------------------------------------- writing
def apply_answers(sorted_, answers):
    rows = list(sorted_['ready'])
    rules = []
    cats = answers.get('_cats')
    by_id = {q['id']: q for q in sorted_['questions']}
    for ans in answers.get('answers', []):
        q = by_id.get(ans['id'])
        if not q or not (ans.get('category') or ans.get('split')):
            continue
        cat = ans.get('category') or 'Miscellaneous'
        if cat.startswith('Refund'):
            continue
        if cats and q['direction'] == 'received':
            g = group_of(cat, cats)
            if g == 'Debt':
                cat = 'Borrowed money'
            elif g == 'Savings':
                cat = 'From my emergency fund' if cat == answers.get('_ef') else 'From my savings'
        splits = ans.get('split', [])
        for it in q['items']:
            c_ = next((sp['category'] for sp in splits if sp['note_contains'].upper() in it['note'].upper()), cat)
            if cats and q['direction'] == 'received':
                g_ = group_of(c_, cats)
                c_ = 'Borrowed money' if g_ == 'Debt' else ('From my emergency fund' if c_ == answers.get('_ef') else 'From my savings') if g_ == 'Savings' else c_
            rows.append({'date': it['date'], 'category': c_, 'amount': it['amount'], 'note': it['note'], 'added_by': 'Me',
                         'account': it['account']})
        for sp in splits:
            if sp.get('always'):
                rules.append({'keyword': sp['note_contains'].upper(), 'category': sp['category'], 'note': 'Added from my answer'})
        if ans.get('always') and (ans.get('keyword') or q.get('offer_rule')):
            rules.append({'keyword': (ans.get('keyword') or q['offer_rule']).upper(), 'category': cat,
                          'note': ans.get('rule_note') or 'Added from my answer'})
    rows.sort(key=lambda r: (r['date'], r['category']))
    return rows, rules


def cmd_write(a):
    import shutil
    sorted_ = json.load(open(a.sorted))
    answers = json.load(open(a.answers)) if a.answers else {}
    info, wb = planner_info(a.planner)
    require_supported(info['version'], nothing_written=True)
    answers['_cats'], answers['_ef'] = info['categories'], info['ef_category']
    rows, rules = apply_answers(sorted_, answers)
    year = int(info['year']) if info['year'] else None
    skipped = [r for r in rows if year and int(r['date'][:4]) != year]
    rows = [r for r in rows if not (year and int(r['date'][:4]) != year)]
    ml = wb['Money Log']
    r = info['last_row'] + 1
    written = 0
    for row in rows:
        if r > 2009:
            break
        ml[f'B{r}'] = dt.datetime.strptime(row['date'], '%Y-%m-%d')
        ml[f'C{r}'] = row['category']
        ml[f'D{r}'] = row['amount']
        ml[f'E{r}'] = row['note']
        ml[f'F{r}'] = row['added_by']
        r += 1
        written += 1
    rl = wb['My Rules']
    existing_kw = {x['keyword'] for x in info['rules']}
    rr = next((i for i in range(12, 312) if not rl[f'B{i}'].value), None)
    new_rules = 0
    for ru in rules:
        if ru['keyword'] in existing_kw or rr is None:
            continue
        rl[f'B{rr}'], rl[f'C{rr}'], rl[f'D{rr}'] = ru['keyword'], ru['category'], ru['note']
        existing_kw.add(ru['keyword'])
        rr = next((i for i in range(rr + 1, 312) if not rl[f'B{i}'].value), None)
        new_rules += 1
    me = wb['Month-End Check']
    amap = answers.get('account_map', {})
    bal_written, bal_skipped = 0, []
    for b in sorted_['balances']:
        y, m = map(int, b['month'].split('-'))
        if year and y != year:
            bal_skipped.append(b)
            continue
        target = amap.get(b['account'], b['account'])
        row = next((x['row'] for x in info['accounts'] if x['name'] and norm(x['name']) == norm(target)), None)
        if row is None:
            row = next((x['row'] for x in info['accounts'] if x['name'] and x['type'] == b['type']
                        and not any(norm(y_['name'] or '') == norm(b['account']) for y_ in info['accounts'])
                        and norm(x['name']) in (norm(b['type']), norm('Main bank'))), None)
        if row is None:
            free = next((x for x in info['accounts'] if not x['name']), None)
            if not free:
                bal_skipped.append(b)
                continue
            row = free['row']
            me[f'B{row}'], me[f'C{row}'] = target, b['type'] if b['type'] in ('M-Pesa', 'Bank', 'Cash') else 'Other'
            free['name'], free['type'] = target, b['type']
        col = chr(ord('E') + m - 1)
        me[f'{col}{row}'] = b['closing']
        bal_written += 1
    out = a.out
    if os.path.abspath(out) == os.path.abspath(a.planner) and not a.in_place:
        fail('OVERWRITE', 'Refusing to overwrite the planner. Pass --in-place if the person agreed.')
    wb.save(out)
    print(json.dumps({'ok': True, 'saved': out, 'rows_written': written, 'rows_outside_year': len(skipped),
                      'new_rules': new_rules, 'balances_written': bal_written, 'balances_skipped': len(bal_skipped)}))


def cmd_export(a):
    sorted_ = json.load(open(a.sorted))
    answers = json.load(open(a.answers)) if a.answers else {}
    rows, rules = apply_answers(sorted_, answers)
    print('=== Money Log: paste into the first empty row, column B (Date | Category | Amount | Note | Added by) ===')
    for r in rows:
        d = dt.datetime.strptime(r['date'], '%Y-%m-%d').strftime('%d/%m/%Y')
        print('\t'.join([d, r['category'], f"{r['amount']:.2f}".rstrip('0').rstrip('.'), r['note'], r['added_by']]))
    if rules:
        print('\n=== My Rules: paste into the first empty row, column B (Words | Category | Notes) ===')
        for ru in rules:
            print('\t'.join([ru['keyword'], ru['category'], ru['note']]))
    if sorted_['balances']:
        print('\n=== Month-End Check: type these end-of-month balances ===')
        for b in sorted_['balances']:
            print(f"{b['account']} ({b['type']}), {b['month']}: {b['closing']:,.2f}")


def cmd_log(a):
    """Opt-in, anonymous: no names, no amounts, no dates finer than the month."""
    path = os.path.join(a.folder, 'fnsoko-usage-log.csv')
    new = not os.path.exists(path)
    with open(path, 'a', newline='') as f:
        w = csv.writer(f)
        if new:
            w.writerow(['month', 'mode', 'rows_auto', 'questions', 'ladder_step', 'stuck_on'])
        w.writerow([dt.date.today().strftime('%Y-%m'), a.mode, a.rows_auto or '', a.questions or '', a.step or '', a.stuck or ''])
    print(json.dumps({'ok': True, 'log': path}))


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    s = p.add_subparsers(dest='cmd', required=True)
    c = s.add_parser('check'); c.add_argument('planner')
    c = s.add_parser('parse'); c.add_argument('files', nargs='+'); c.add_argument('--out', required=True)
    c.add_argument('--fx', nargs='*', help='e.g. GBP=165 USD=129'); c.add_argument('--account'); c.add_argument('--currency')
    c.add_argument('--me', help="the person's own name, removed from every line (found automatically on most statements)")
    c = s.add_parser('sort'); c.add_argument('parsed'); c.add_argument('--planner', required=True); c.add_argument('--out', required=True)
    c.add_argument('--month', nargs='*', help='only these months, e.g. 2026-10 (start with the last full month)')
    c = s.add_parser('write'); c.add_argument('sorted'); c.add_argument('--planner', required=True); c.add_argument('--answers')
    c.add_argument('--out', required=True); c.add_argument('--in-place', action='store_true')
    c = s.add_parser('export'); c.add_argument('sorted'); c.add_argument('--answers')
    c = s.add_parser('log'); c.add_argument('--folder', required=True); c.add_argument('--mode', required=True)
    c.add_argument('--rows-auto', type=int); c.add_argument('--questions', type=int); c.add_argument('--step', type=int); c.add_argument('--stuck')
    a = p.parse_args()
    {'check': cmd_check, 'parse': cmd_parse, 'sort': cmd_sort, 'write': cmd_write, 'export': cmd_export, 'log': cmd_log}[a.cmd](a)


if __name__ == '__main__':
    main()
