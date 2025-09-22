from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory
import os
from datetime import datetime
from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter

def process_frete_file(filepath: str) -> str:
    """Processa o arquivo de frete conforme regras do cliente e salva um arquivo processado.
    Retorna o caminho do arquivo processado."""
    p = Path(filepath)
    suffix = p.suffix.lower()

    # If Excel (.xlsx/.xls) use openpyxl: process workbook in-place (add RESULTADO_N column)
    if suffix in ('.xlsx', '.xls'):
        wb = openpyxl.load_workbook(str(p))
        ws = wb.active

        # find header row (where a cell equals 'Tipo' or contains 'Tipo')
        header_row = None
        for r in range(1, ws.max_row + 1):
            first = ws.cell(row=r, column=1).value
            if first is not None and str(first).strip().lower() == 'tipo':
                header_row = r
                break
        if header_row is None:
            # try to find any row that contains 'Tipo' in any cell
            for r in range(1, ws.max_row + 1):
                for c in range(1, ws.max_column + 1):
                    v = ws.cell(row=r, column=c).value
                    if v is not None and 'tipo' in str(v).lower():
                        header_row = r
                        break
                if header_row is not None:
                    break

        if header_row is None:
            raise ValueError('Não foi possível localizar a linha de cabeçalho (Tipo) no arquivo Excel')

        # read header names
        hdr = []
        for c in range(1, ws.max_column + 1):
            v = ws.cell(row=header_row, column=c).value
            hdr.append(str(v).strip() if v is not None else '')

        # find indices for columns (case-insensitive, tolerant)
        def find_header(name):
            name_low = name.lower()
            for i, h in enumerate(hdr, start=1):
                if h.lower() == name_low:
                    return i
            # fallback: find header containing name
            for i, h in enumerate(hdr, start=1):
                if name_low in h.lower():
                    return i
            return None

        # Determine indices: prefer 'Kg Real' as source for calculations
        valor_idx = find_header('Kg Real') or find_header('KgReal') or find_header('Kg') or find_header('Valor') or find_header('Valor NF') or len(hdr)
        remet_idx = find_header('Remetente') or 4
        tipo_idx = find_header('Tipo') or 1

        # Ensure RESULTADO_N is in column N (Excel column letter 'N' => index 14)
        from openpyxl.utils import column_index_from_string
        desired_col_idx = column_index_from_string('N')
        # If worksheet has fewer columns than desired, extend by adding empty cols
        if ws.max_column < desired_col_idx:
            # nothing to shift, just ensure cells exist
            pass
        else:
            # if column N already has any non-empty cells below header, insert a column at N to avoid overwriting
            has_data = False
            for rr in range(header_row, ws.max_row + 1):
                if ws.cell(row=rr, column=desired_col_idx).value not in (None, ''):
                    has_data = True
                    break
            if has_data:
                ws.insert_cols(desired_col_idx)

        resultado_col = desired_col_idx
        ws.cell(row=header_row, column=resultado_col, value='RESULTADO_N')

        # iterate rows, collect blocks between Manifesto: and Total - Manifesto:
        r = header_row + 1
        while r <= ws.max_row:
            cellA = ws.cell(row=r, column=1).value
            if cellA is not None and str(cellA).strip().startswith('Manifesto:'):
                # start a block
                block_rows = []
                r += 1
                # skip possible header row inside block (Tipo ...)
                # collect until Total - Manifesto:
                while r <= ws.max_row:
                    a = ws.cell(row=r, column=1).value
                    if a is not None and str(a).strip().startswith('Total - Manifesto:'):
                        # process block_rows
                        has_valencio = False
                        # first pass: detect presence of Valencio
                        for rr in block_rows:
                            remet = ws.cell(row=rr, column=remet_idx).value
                            if remet is not None and str(remet).strip().upper() == 'FRIGORIFICO VALENCIO LTDA':
                                has_valencio = True
                                break

                        block_sum = 0.0
                        # second pass: compute results and write
                        for rr in block_rows:
                            raw_val = ws.cell(row=rr, column=valor_idx).value
                            # parse numeric value
                            val = 0.0
                            if raw_val is None or str(raw_val).strip() == '':
                                val = 0.0
                            else:
                                try:
                                    val = float(raw_val)
                                except:
                                    s = str(raw_val).replace('.', '').replace(',', '.')
                                    try:
                                        val = float(s)
                                    except:
                                        val = 0.0

                            remet = ws.cell(row=rr, column=remet_idx).value or ''
                            if has_valencio:
                                if str(remet).strip().upper() == 'FRIGORIFICO VALENCIO LTDA':
                                    result_val = round(val * 0.67 / 0.88, 2)
                                else:
                                    result_val = round(val, 2)
                                ws.cell(row=rr, column=resultado_col, value=float(f"{result_val:.2f}"))
                                block_sum += float(result_val)
                            else:
                                # leave blank
                                ws.cell(row=rr, column=resultado_col, value=None)

                        # write block total on the Total - Manifesto row
                        if has_valencio:
                            ws.cell(row=r, column=resultado_col, value=float(f"{round(block_sum,2):.2f}"))
                        else:
                            ws.cell(row=r, column=resultado_col, value=None)

                        # move past total line
                        r += 1
                        break

                    else:
                        # if this is a data row (has Tipo value 'Frete' or non-empty in Tipo column), collect
                        tipo_val = ws.cell(row=r, column=tipo_idx).value
                        # heuristic: collect rows where Tipo column is not empty
                        if tipo_val is not None and str(tipo_val).strip() != '':
                            block_rows.append(r)
                        r += 1
                continue
            else:
                r += 1

        # save processed workbook
        new_path = p.parent / (p.stem + '_processed.xlsx')
        wb.save(str(new_path))
        return str(new_path)
    else:
        text = p.read_text(encoding='utf-8')
        lines = [l.rstrip('\n') for l in text.splitlines()]

    blocks = []
    current_manifest = None
    current_rows = []
    header = None

    for line in lines:
        if not line.strip():
            continue
        if line.startswith('Manifesto:'):
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
            current_rows.append({'__total_line__': line})
            blocks.append({'manifesto': current_manifest, 'rows': current_rows, 'header': header})
            current_manifest = None
            current_rows = []
            header = None
            continue
        if header is None:
            continue
        fields = [c.strip() for c in line.split(';')]
        while len(fields) < len(header):
            fields.append('')
        row = dict(zip(header, fields))
        current_rows.append(row)

    if current_manifest is not None and current_rows:
        blocks.append({'manifesto': current_manifest, 'rows': current_rows, 'header': header})

    # We'll preserve the original file exactly, and only add/update the RESULTADO_N column.
    # Parse original header line (first line that starts with 'manifesto' or 'Tipo;') to keep columns.
    # We'll rebuild each original data line, appending RESULTADO_N as the last column.

    # Determine original header from the first header-like line in the file
    orig_header_line = None
    for l in lines:
        if l.lower().startswith('manifesto;') or l.startswith('Tipo;'):
            orig_header_line = l
            break

    if orig_header_line is None:
        # fallback: use the constructed header
        orig_header = [h.strip() for h in 'manifesto;Tipo;Número;Data;Remetente;Origem;Destinatário;Destino;Volumes;Kg Real;Kg Taxado;Valor NF;Valor'.split(';')]
    else:
        orig_header = [c.strip() for c in orig_header_line.split(';')]

    # we'll output all original lines, but when encountering data rows we append RESULTADO_N
    out_lines = []
    # keep track to know which block we're in
    block_idx = 0
    for block in blocks:
        hdr = block['header']
        if not hdr:
            continue

        # identify input column for calculation in CSV/text blocks: prefer 'Kg Real' then 'Valor'
        if any(h.lower() == 'kg real' for h in hdr):
            valor_key = next(h for h in hdr if h.lower() == 'kg real')
        else:
            candidates = [h for h in hdr if 'valor' in h.lower()]
            if any(h.lower() == 'valor' for h in hdr):
                valor_key = next(h for h in hdr if h.lower() == 'valor')
            elif len(candidates) > 0:
                valor_key = candidates[-1]
            else:
                valor_key = hdr[-1]

        # check if block contains FRIGORIFICO VALENCIO LTDA (normalized)
        has_valencio = any((r.get('Remetente','').upper().strip() == 'FRIGORIFICO VALENCIO LTDA') for r in block['rows'] if isinstance(r, dict))

        block_sum = 0.0
        for r in block['rows']:
            if isinstance(r, dict):
                remet = r.get('Remetente','').strip()
                raw_val = r.get(valor_key,'')
                val_str = raw_val.replace('.', '').replace(',', '.') if raw_val else ''
                try:
                    val = float(val_str) if val_str != '' else 0.0
                except:
                    val = 0.0

                result_N = ''
                if has_valencio:
                    if remet.upper() == 'FRIGORIFICO VALENCIO LTDA':
                        result_val = round(val * 0.67 / 0.88, 2)
                        result_N = f"{result_val:.2f}"
                    else:
                        result_val = round(val, 2)
                        result_N = f"{result_val:.2f}"
                    try:
                        block_sum += float(str(result_val))
                    except:
                        pass

                # Reconstruct the original line values in the original header order, preserving original field text
                # Use values from r when available, otherwise empty string
                ordered_vals = []
                for col in orig_header:
                    # Map column name variants to keys in r: try direct, then normalized versions
                    val_text = ''
                    if col in r:
                        val_text = r.get(col,'')
                    else:
                        # try lowercase/no-accent matches
                        for k in r.keys():
                            if k.lower().replace('ã','a').replace('á','a').replace('à','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('õ','o').replace('ô','o').replace('ú','u').replace('ç','c') == col.lower().replace('ã','a').replace('á','a').replace('à','a').replace('é','e').replace('ê','e').replace('í','i').replace('ó','o').replace('õ','o').replace('ô','o').replace('ú','u').replace('ç','c'):
                                val_text = r.get(k,'')
                                break
                    ordered_vals.append(val_text)

                # Append RESULTADO_N
                ordered_vals.append(result_N)
                out_lines.append(';'.join(ordered_vals))
            else:
                total_text = r['__total_line__']
                if has_valencio:
                    out_lines.append(total_text + ';' + f"{round(block_sum,2):.2f}")
                else:
                    out_lines.append(total_text + ';')

        block_idx += 1

    # If there were any lines before the first Manifesto block (like header), preserve them at the top
    # Build final output: prefix any leading non-block lines from original file
    final_lines = []
    in_first_block = False
    block_line_idx = 0
    # We'll iterate original lines and replace data lines for blocks sequentially using out_lines
    out_iter = iter(out_lines)
    for line in lines:
        if line.startswith('Manifesto:'):
            in_first_block = True
            # output the Manifesto line as-is
            final_lines.append(line)
            continue
        if not in_first_block:
            final_lines.append(line)
            continue
        # For lines inside blocks we consume from out_iter until we hit the next Manifesto or end
        # To keep things simple, when we encounter a data line (contains ';' and not starting with 'Total - Manifesto:')
        # we pop from out_iter and use that as replacement; for total lines we also pop.
        if line.startswith('Tipo;'):
            # skip original header lines inside block
            final_lines.append(line)
            continue
        if line.startswith('Total - Manifesto:'):
            try:
                replacement = next(out_iter)
            except StopIteration:
                replacement = line
            final_lines.append(replacement)
            # next Manifesto will reset
            continue
        if ';' in line:
            # assume it's a data row
            try:
                replacement = next(out_iter)
            except StopIteration:
                replacement = line + ';'
            final_lines.append(replacement)
            continue
        # fallback
        final_lines.append(line)

    processed_name = f"processed_{p.name}"
    out_path = p.parent / processed_name

    # If original was Excel, write Excel preserving columns and adding RESULTADO_N
    if suffix in ('.xlsx', '.xls'):
        # create workbook and write each line splitting by ';'
        new_wb = openpyxl.Workbook()
        new_ws = new_wb.active
        for r_idx, out_line in enumerate(final_lines, start=1):
            parts = out_line.split(';')
            for c_idx, val in enumerate(parts, start=1):
                new_ws.cell(row=r_idx, column=c_idx, value=val)
        new_path = p.parent / (p.stem + '_processed.xlsx')
        new_wb.save(str(new_path))
        return str(new_path)
    else:
        out_path.write_text('\n'.join(final_lines), encoding='utf-8')
        return str(out_path)

bp = Blueprint('frete', __name__, url_prefix='/frete')


@bp.route('/')
def index():
    return render_template('frete.html')


@bp.route('/importacao', methods=['GET', 'POST'])
def importacao():
    if request.method == 'POST':
        if 'files' not in request.files:
            flash('Nenhum arquivo enviado!', 'error')
            return redirect(url_for('frete.importacao'))

        files = request.files.getlist('files')
        if not files or files[0].filename == '':
            flash('Nenhum arquivo selecionado.', 'error')
            return redirect(url_for('frete.importacao'))

        # Criar diretório de uploads do frete se não existir
        uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads', 'frete'))
        os.makedirs(uploads_dir, exist_ok=True)

        for file in files:
            if file.filename:
                # Salvar arquivo temporariamente
                filepath = os.path.join(uploads_dir, file.filename)
                file.save(filepath)
                # Processar o arquivo segundo a regra do FRIGORIFICO VALENCIO
                try:
                    processed = process_frete_file(filepath)
                    flash(f'{file.filename}: Arquivo salvo e processado -> {os.path.basename(processed)}', 'success')
                except Exception as e:
                    # em caso de erro, avisa mas não interrompe o loop
                    flash(f'{file.filename}: Erro no processamento ({str(e)})', 'error')

        return redirect(url_for('frete.importacao'))

    # Lista de arquivos enviados (pasta uploads/frete)
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads', 'frete'))
    uploads = []
    if os.path.isdir(uploads_dir):
        for fname in sorted(os.listdir(uploads_dir), reverse=True):
            fpath = os.path.join(uploads_dir, fname)
            try:
                mtime = os.path.getmtime(fpath)
                size = os.path.getsize(fpath)
                uploads.append({
                    'name': fname,
                    'mtime': datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S'),
                    'size': size
                })
            except Exception:
                continue

    return render_template('frete_importacao.html', uploads=uploads)


@bp.route('/uploads/<path:filename>')
def uploaded_file(filename):
    uploads_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads', 'frete'))
    return send_from_directory(uploads_dir, filename)
