import sqlite3


class RegistrationDatabase:

    def __init__(self, db_path=":memory:"):
        self._connection = sqlite3.connect(db_path)
        self._connection.execute(
            """
            CREATE TABLE IF NOT EXISTS registrations (
                login            TEXT    NOT NULL,
                password         TEXT    NOT NULL,
                password_confirm TEXT    NOT NULL,
                auth_result      INTEGER NOT NULL,
                error_message    TEXT    NOT NULL DEFAULT '',
                PRIMARY KEY (login, password, password_confirm)
            )
            """
        )
        self._connection.commit()

    def add_record(self, login, password, password_confirm, auth_result, error_message=""):
        self._connection.execute(
            "INSERT OR REPLACE INTO registrations VALUES (?, ?, ?, ?, ?)",
            (login, password, password_confirm, int(auth_result), error_message),
        )
        self._connection.commit()

    def get_record(self, login, password, password_confirm):
        row = self._connection.execute(
            "SELECT login, password, password_confirm, auth_result, error_message "
            "FROM registrations WHERE login = ? AND password = ? AND password_confirm = ?",
            (login, password, password_confirm),
        ).fetchone()
        if row is None:
            return None
        return {
            "login": row[0],
            "password": row[1],
            "password_confirm": row[2],
            "auth_result": bool(row[3]),
            "error_message": row[4],
        }

    def delete_record(self, login, password, password_confirm):
        cursor = self._connection.execute(
            "DELETE FROM registrations WHERE login = ? AND password = ? AND password_confirm = ?",
            (login, password, password_confirm),
        )
        self._connection.commit()
        return cursor.rowcount > 0

    def close(self):
        self._connection.close()
