from pathlib import Path
import pandas as pd

file_path = Path(r"d:\valen.csv")
text = file_path.read_text(encoding='utf-8')
lines = [l.rstrip('\n') for l in text.splitlines()]

blocks = []
current_manifest = None
current_rows = []
header = None

for i, line in enumerate(lines):
    if not line.strip():
        continue
    # detect Manifesto line
    if line.startswith('Manifesto:'):
        # start new block
        if current_manifest is not None:
            blocks.append({'manifesto': current_manifest, 'rows': current_rows, 'header': header})
        current_manifest = line
        current_rows = []
        header = None
        continue
    if line.startswith('Tipo;'):
        header = [c.strip() for c in line.split(';')]
        continue
    if line.startswith('Total - Manifesto:'):
        # push total line as special row
        current_rows.append({'__total_line__': line})
        # end block
        blocks.append({'manifesto': current_manifest, 'rows': current_rows, 'header': header})
        current_manifest = None
        current_rows = []
        header = None
        continue
    # data row
    if header is None:
        # skip lines until header
        continue
    fields = [c.strip() for c in line.split(';')]
    # pad to header length
    while len(fields) < len(header):
        fields.append('')
    row = dict(zip(header, fields))
    current_rows.append(row)

# If any dangling block
if current_manifest is not None and current_rows:
    blocks.append({'manifesto': current_manifest, 'rows': current_rows, 'header': header})

# Process blocks
name_key = 'Remetente'
valor_key = None

processed_rows = []
results = []
for block in blocks:
    hdr = block['header']
    if not hdr:
        continue
    # find valor_key by header name likely 'Valor' or 'Valor ' etc
    candidates = [h for h in hdr if 'Valor' in h]
    # prefer exact 'Valor' else pick last 'Valor' occurrence
    if 'Valor' in hdr:
        valor_key = 'Valor'
    elif len(candidates) > 0:
        valor_key = candidates[-1]
    else:
        # fallback: last numeric-looking column
        valor_key = hdr[-1]

    # check if block contains any FRIGORIFICO VALENCIO LTDA
    has_valencio = any((r.get(name_key,'').upper().strip() == 'FRIGORIFICO VALENCIO LTDA') for r in block['rows'] if isinstance(r, dict))

    block_sum = 0.0
    for r in block['rows']:
        if isinstance(r, dict):
            remet = r.get(name_key,'').strip()
            val_str = r.get(valor_key,'').replace('.', '').replace(',', '.') if r.get(valor_key) else ''
            try:
                val = float(val_str) if val_str != '' else 0.0
            except:
                val = 0.0
            result_N = None
            if has_valencio:
                if remet.upper() == 'FRIGORIFICO VALENCIO LTDA':
                    result_N = round(val * 0.67 / 0.88, 2)
                else:
                    # repeat valor
                    result_N = round(val, 2)
                block_sum += result_N if result_N is not None else 0.0
            # store
            newr = dict(r)
            newr['__manifesto__'] = block['manifesto']
            newr['__result_N__'] = result_N
            processed_rows.append(newr)
        else:
            # total line - attach block sum
            processed_rows.append({'__total_line__': r['__total_line__'], '__manifesto__': block['manifesto'], '__result_N__': round(block_sum,2)})

    results.append({'manifesto': block['manifesto'], 'has_valencio': has_valencio, 'block_sum': round(block_sum,2)})

# Save processed rows to CSV for inspection
out_lines = []
out_lines.append('manifesto;Tipo;Número;Data;Remetente;Origem;Destinatário;Destino;Volumes;Kg Real;Kg Taxado;Valor NF;Valor;RESULTADO_N')
for r in processed_rows:
    if '__total_line__' in r:
        # write total line keeping original text and append result
        out_lines.append(r['__total_line__'] + ';' + (str(r.get('__result_N__',''))))
    else:
        vals = [r.get('__manifesto__',''), r.get('Tipo',''), r.get('Número',''), r.get('Data',''), r.get('Remetente',''), r.get('Origem',''), r.get('Destinatário',''), r.get('Destino',''), r.get('Volumes',''), r.get('Kg Real',''), r.get('Kg Taxado',''), r.get('Valor NF',''), r.get('Valor',''), str(r.get('__result_N__',''))]
        out_lines.append(';'.join(vals))

out_path = Path(r"d:\processed_valen.csv")
out_path.write_text('\n'.join(out_lines), encoding='utf-8')

print({'blocks_processed': len(blocks), 'results': results, 'out_path': str(out_path)})
