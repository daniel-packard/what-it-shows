#!/usr/bin/env python3
"""Split the reports merged into #4471 into problems and count each.

Usage: python3 -I split.py [kb-root]   (default: kb/support-kb)

Rules (found by reading every body, 2026-10-30):
  one-day-move  the desk's own list (desk-notes.json oneDayMove); the body shows a
                date off by one day, not a day/month flip
  hint          causes.ts rule: day-first tenant, report came through the booking
                form, and the tenant runs booking-v3 (hint prints MM/DD/YYYY)
  parser        every other report from a day-first tenant (shared parser reads
                month first)
Reports are de-duplicated by id first (the export pages overlap).
Any body that names two dates that are not a day/month flip, and is not in the
desk's one-day list, is printed under UNREAD so a person reads it before trusting
the counts.
"""
import glob
import json
import re
import sys
from collections import Counter

root = sys.argv[1] if len(sys.argv) > 1 else 'kb/support-kb'
data = f'{root}/src/lib/data'
rows = json.load(open(f'{data}/reports-4471.json'))
tenants = {}
for f in glob.glob(f'{data}/tenants/*.json'):
    t = json.load(open(f))
    tenants[t['handle']] = t
one_day = set(json.load(open(f'{data}/desk-notes.json'))['oneDayMove'])

reports = list({r['id']: r for r in rows}.values())
merged = [r for r in reports if r['mergedInto'] == 4471]

MONTHS = 'January February March April May June July August September October November December'.split()
DATE = re.compile(r'(\d{1,2}) (' + '|'.join(MONTHS) + ')')
DAY_FIRST = {'en-GB', 'en-IE', 'nl-NL', 'da-DK', 'pl-PL', 'cs-CZ', 'de-DE', 'it-IT', 'pt-PT', 'es-ES', 'fr-FR'}


def problem(r):
    t = tenants.get(r['tenant'])
    if r['id'] in one_day:
        return 'one-day-move'
    if not t or t['locale'] not in DAY_FIRST:
        return 'unplaced'
    if r['channel'] == 'form' and t['form'] == 'booking-v3':
        return 'hint'
    return 'parser'


def not_a_flip(r):
    ds = [(int(d), MONTHS.index(m) + 1) for d, m in DATE.findall(r['body'])]
    return len(ds) == 2 and ds[0] != (ds[1][1], ds[1][0])


by = {}
for r in merged:
    by.setdefault(problem(r), []).append(r)

print(f'rows {len(rows)} · unique {len(reports)} · merged into #4471 {len(merged)}')
for p, rs in sorted(by.items(), key=lambda kv: -len(kv[1])):
    days = sorted(r['receivedAt'][:10] for r in rs)
    print(f'{p:13} {len(rs):4}  tenants {len({r["tenant"] for r in rs}):2}  '
          f'{days[0]} → {days[-1]}  intake tags {dict(Counter(r["meta"]["intakeTag"] for r in rs))}')
unread = [r for r in merged if r['id'] not in one_day and not_a_flip(r)]
for r in unread:
    print('UNREAD', r['id'], r['body'])
