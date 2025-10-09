import sqlite3

# Conectar ao banco de dados
conn = sqlite3.connect('instance/clinica_mentalize.db')
cursor = conn.cursor()

# Verificar tabelas existentes
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tabelas = cursor.fetchall()
print("Tabelas existentes:", [t[0] for t in tabelas])

# Contar registros em cada tabela
for tabela in tabelas:
    nome_tabela = tabela[0]
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {nome_tabela}")
        count = cursor.fetchone()[0]
        print(f"Total {nome_tabela}: {count}")
        
        # Para a tabela usuarios, mostrar tipos
        if nome_tabela == 'usuarios':
            cursor.execute("SELECT tipo_usuario, COUNT(*) FROM usuarios GROUP BY tipo_usuario")
            tipos = cursor.fetchall()
            print(f"  Por tipo: {tipos}")
            
    except Exception as e:
        print(f"Erro ao contar {nome_tabela}: {e}")

conn.close()