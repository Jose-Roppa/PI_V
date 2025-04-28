import pyodbc
from datetime import datetime, timedelta

# Dados de conexão já configurados para o banco de dados SQL Server
DB_CONFIG = {
    'server': 'SEU_IP_DO_SERVIDOR', 
    'database': 'NOME_DO_BANCO',    
    'username': 'USUARIO',           
    'password': 'SENHA',             
    'driver': 'SQL Server',
}

conn_str = (
    f"DRIVER={{{DB_CONFIG['driver']}}};"
    f"SERVER={DB_CONFIG['server']};"
    f"DATABASE={DB_CONFIG['database']};"
    f"UID={DB_CONFIG['username']};"
    f"PWD={DB_CONFIG['password']}"
)

def get_connection():
    return pyodbc.connect(conn_str)

def get_conversation(phone, limit=100):
    conn = get_connection()
    cursor = conn.cursor()
    query = f'''
        SELECT TOP ({limit}) [id], [phone], [fromMe], [fromApi], [text], [datahora], [senderName]
        FROM [projetovpj].[dbo].[mensagens_whatsapp]
        WHERE [phone] = ?
        ORDER BY [datahora] ASC
    '''
    cursor.execute(query, phone)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_active_sessions(hours=24):
    conn = get_connection()
    cursor = conn.cursor()
    since = (datetime.now() - timedelta(hours=hours)).strftime('%Y-%m-%d %H:%M:%S')
    query = f'''
        SELECT [phone], MAX([datahora]) as last_message
        FROM [projetovpj].[dbo].[mensagens_whatsapp]
        WHERE [datahora] > ?
        GROUP BY [phone]
        ORDER BY last_message DESC
    '''
    cursor.execute(query, since)
    rows = cursor.fetchall()
    conn.close()
    return rows

def format_conversation(messages):
    formatted = []
    for msg in messages:
        if msg.fromMe == 0:
            formatted.append({"role": "cliente", "text": msg.text, "hora": msg.datahora, "nome": msg.senderName})
        elif msg.fromMe == 1 and msg.fromApi == 1:
            formatted.append({"role": "bot", "text": msg.text, "hora": msg.datahora, "nome": msg.senderName})
        elif msg.fromMe == 1 and msg.fromApi == 0:
            formatted.append({"role": "atendente", "text": msg.text, "hora": msg.datahora, "nome": msg.senderName})
    return formatted 