import sqlite3
import os

class AccessLogger:
    def __init__(self, db_path='screenserver.db'):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        if not os.path.exists(self.db_path):
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute('''
                CREATE TABLE IF NOT EXISTS access_history (
                    session_uuid TEXT,
                    ip TEXT,
                    user_agent TEXT,
                    access_time TEXT
                )
            ''')
            c.execute('''
                CREATE TABLE IF NOT EXISTS user_alias (
                    session_uuid TEXT PRIMARY KEY,
                    alias TEXT
                )
            ''')
            conn.commit()
            conn.close()

    def log_access(self, session_uuid, ip, user_agent, access_time):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO access_history (session_uuid, ip, user_agent, access_time)
            VALUES (?, ?, ?, ?)
        ''', (session_uuid, ip, user_agent, access_time))
        c.execute('''
            INSERT OR IGNORE INTO user_alias (session_uuid, alias)
            VALUES (?, NULL)
        ''', (session_uuid,))
        conn.commit()
        conn.close()

    def get_all_user_aliases(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT session_uuid, alias FROM user_alias')
        results = c.fetchall()
        conn.close()
        # Convertir a lista de diccionarios
        return [{"session_uuid": row[0], "alias": row[1]} for row in results]

    def get_access_history(self, limit=10):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            SELECT ah.session_uuid, ah.ip, ah.user_agent, ah.access_time, ua.alias
            FROM access_history ah
            LEFT JOIN user_alias ua ON ah.session_uuid = ua.session_uuid
            ORDER BY ah.access_time DESC
            LIMIT ?
        ''', (limit,))
        results = c.fetchall()
        conn.close()
        # Convertir a lista de diccionarios
        return [
            {
                "session_uuid": row[0],
                "ip": row[1],
                "user_agent": row[2],
                "access_time": row[3],
                "alias": row[4]
            }
            for row in results
        ]

    def set_user_alias(self, session_uuid, alias):
        """Asigna o actualiza un alias para un session_uuid."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''
            INSERT INTO user_alias (session_uuid, alias)
            VALUES (?, ?)
            ON CONFLICT(session_uuid) DO UPDATE SET alias=excluded.alias
        ''', (session_uuid, alias))
        conn.commit()
        conn.close()

