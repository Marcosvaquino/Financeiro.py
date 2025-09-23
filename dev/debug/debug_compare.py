import os
import csv
import sqlite3
from datetime import datetime

WORKDIR = r"D:\OneDrive\PROJETOFINANCEIRO.PY"
UPLOADS = os.path.join(WORKDIR, 'uploads')
DB_PATH = os.path.join(WORKDIR, 'financeiro.db')
TARGET_MONTH = 8
TARGET_YEAR = 2025

# find latest lancamentos-a-receber_*.csv
candidates = [f for f in os.listdir(UPLOADS) if f.startswith('lancamentos-a-receber_') and f.lower().endswith('.csv')]
if not candidates:
    print('Nenhum arquivo de receber encontrado em', UPLOADS)
    raise SystemExit(1)

candidates.sort(reverse=True)
latest = candidates[0]
csv_path = os.path.join(UPLOADS, latest)
print('Usando CSV:', csv_path)

matches = []
all_csv_count = 0

with open(csv_path, 'r', encoding='utf-8', errors='replace') as fh:
    reader = csv.reader(fh, delimiter=';')
    headers = next(reader)
    hdr_map = {h.strip(): i for i, h in enumerate(headers)}
    # header names expected: 'Vencimento', 'Status', 'Cliente', 'Valor Principal', 'Data Baixa'
    for row in reader:
        try:
            status = row[hdr_map.get('Status', '')].strip()
        except Exception:
            status = ''
        try:
            venc = row[hdr_map.get('Vencimento', '')].strip()
        except Exception:
            venc = ''
        try:
            cliente = row[hdr_map.get('Cliente', '')].strip()
        except Exception:
            cliente = ''
        try:
            valor_text = row[hdr_map.get('Valor Principal', '')].strip()
        except Exception:
            valor_text = ''

        # parse vencimento date
        month = None
        year = None
        if venc:
            try:
                dt = datetime.strptime(venc, '%d/%m/%Y')
                month = dt.month
                year = dt.year
            except Exception:
                # ignore parse errors
                pass

        if status and ('receb' in status.lower()) and month == TARGET_MONTH and year == TARGET_YEAR:
            matches.append({'cliente': cliente, 'vencimento': venc, 'status': status, 'valor_text': valor_text, 'row': row})

print('\nCSV: linhas com Status contendo "receb" e vencimento {}/{}: {}'.format(str(TARGET_MONTH).zfill(2), TARGET_YEAR, len(matches)))

# connect to DB and get projection clients
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute('SELECT DISTINCT cliente FROM projecao WHERE mes=? AND ano=?', (TARGET_MONTH, TARGET_YEAR))
proj_clients = sorted([r[0] for r in cur.fetchall() if r[0] is not None])
print('Clientes na projeção (count={}):'.format(len(proj_clients)))
for c in proj_clients[:10]:
    print(' -', c)
if len(proj_clients) > 10:
    print(' (lista truncada)')

# counts in CSV for projection clients
csv_proj_count = 0
for m in matches:
    if m['cliente'] in proj_clients:
        csv_proj_count += 1

print('\nCSV: linhas recebidas em {}/{} para clientes da projeção: {}'.format(str(TARGET_MONTH).zfill(2), TARGET_YEAR, csv_proj_count))

# query DB for recebidos matching clients
if proj_clients:
    placeholders = ','.join(['?'] * len(proj_clients))
    params = []
    # Build SQL that checks status and vencimento or data_baixa containing /MM/YYYY
    mm_yyyy = f'/{str(TARGET_MONTH).zfill(2)}/{TARGET_YEAR}'
    sql = f"SELECT COUNT(*), IFNULL(SUM(valor_principal),0) FROM contas_receber WHERE lower(status) LIKE '%recebido%' AND (vencimento LIKE ? OR data_baixa LIKE ?) AND cliente IN ({placeholders})"
    params = [f'%{mm_yyyy}%', f'%{mm_yyyy}%'] + proj_clients
    cur.execute(sql, params)
    db_count, db_sum = cur.fetchone()
else:
    db_count, db_sum = 0, 0.0

print('\nDB: contas_receber com status contendo "recebido" e vencimento/data_baixa em {}/{} e cliente na projeção:'.format(str(TARGET_MONTH).zfill(2), TARGET_YEAR))
print(' count =', db_count, ' sum(valor_principal) =', db_sum)

# also show total DB recebidos for the month regardless of client
sql2 = "SELECT COUNT(*), IFNULL(SUM(valor_principal),0) FROM contas_receber WHERE lower(status) LIKE '%recebido%' AND (vencimento LIKE ? OR data_baixa LIKE ?)"
cur.execute(sql2, (f'%{mm_yyyy}%', f'%{mm_yyyy}%'))
all_db_count, all_db_sum = cur.fetchone()
print('\nDB: total contas_receber RECEBIDO no mes (qualquer cliente):', all_db_count, ' sum=', all_db_sum)

# print sample CSV rows (up to 10) that match but are NOT in DB projection clients
print('\nAmostra de até 10 linhas CSV recebidas em {}/{} (cliente / vencimento / valor):'.format(str(TARGET_MONTH).zfill(2), TARGET_YEAR))
shown = 0
for m in matches:
    if shown >= 10:
        break
    in_proj = m['cliente'] in proj_clients
    if not in_proj:
        print(' -', m['cliente'][:50], '|', m['vencimento'], '|', m['valor_text'], '| status=', m['status'])
        shown += 1

# print sample of matches that are in projection but may be missing in DB
print('\nAmostra de até 10 linhas CSV recebidas em {}/{} para clientes da projeção:'.format(str(TARGET_MONTH).zfill(2), TARGET_YEAR))
shown = 0
for m in matches:
    if shown >= 10:
        break
    if m['cliente'] in proj_clients:
        print(' -', m['cliente'][:50], '|', m['vencimento'], '|', m['valor_text'], '| status=', m['status'])
        shown += 1

conn.close()
print('\nFim do diagnóstico.')
