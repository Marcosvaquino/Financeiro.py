import os, sqlite3

def info(path):
    if not os.path.exists(path):
        return {'exists': False}
    st = os.stat(path)
    size = st.st_size
    mtime = st.st_mtime
    info = {'exists': True, 'size': size, 'mtime': mtime}
    try:
        conn = sqlite3.connect(path)
        cur = conn.cursor()
        # check tables
        tables = ['projecao','contas_receber','contas_pagar']
        for t in tables:
            try:
                cur.execute(f"SELECT COUNT(*), COALESCE(SUM(CASE WHEN typeof(valor_principal)='null' THEN 0 ELSE valor_principal END),0) FROM {t}")
                r = cur.fetchone()
                info[t] = {'count': r[0] or 0, 'sum': r[1] or 0}
            except Exception as e:
                info[t] = {'error': str(e)}
        conn.close()
    except Exception as e:
        info['error'] = str(e)
    return info

roots = [os.path.abspath('financeiro.db'), os.path.abspath(os.path.join('financeiro','financeiro.db'))]
for r in roots:
    print('\nDB:', r)
    inf = info(r)
    print(inf)
