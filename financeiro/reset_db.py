import sqlite3

DB_PATH = "financeiro.db"

def reset_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Remove tabelas antigas se existirem
    cur.execute("DROP TABLE IF EXISTS contas_receber")
    cur.execute("DROP TABLE IF EXISTS contas_pagar")
    cur.execute("DROP TABLE IF EXISTS projecao")
    cur.execute("DROP TABLE IF EXISTS usuarios")

    conn.commit()

    # Recria tabelas a partir do schema.sql
    with open("financeiro/schema.sql", "r", encoding="utf-8") as f:
        cur.executescript(f.read())

    conn.commit()
    conn.close()
    print("✅ Banco recriado com sucesso!")

if __name__ == "__main__":
    reset_db()
