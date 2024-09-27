import sqlite3 as sqlite
from contextlib import closing
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash

class User(UserMixin):
    def __init__(self, user_record):
        self.id = user_record.account_id
        self.username = user_record.username
        self.password = user_record.password

        self.is_admin = user_record.is_admin

class Record:
    def __init__(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)

    def __repr__(self):
        return f"Record<{', '.join(f'{k}={v}' for k,v in self.__dict__.items())}>"

    def to_user(self) -> User:
        return User(self)


class Database:
    database: sqlite.Connection

    def __init__(self):
        self.initialise = False

        self.connection = sqlite.connect(
            "database/inventory.sqlite",
            check_same_thread=False,
            detect_types=sqlite.PARSE_DECLTYPES | sqlite.PARSE_COLNAMES
        )
        self.connection.row_factory = self.__dict_factory

        self.__init_db()

    @staticmethod
    def __dict_factory(cursor: sqlite.Cursor, row) -> dict[str, any]:
        return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

    def __init_db(self):
        with open("database/schema.sql") as schema_file:
            schema: str = schema_file.read().split("-- NEW QUERY --")

        for query in schema:
            query = query.strip("\n")
            self.execute(query)

        admin_account = self.fetch("SELECT * FROM accounts WHERE username='admin'")

        if not admin_account:
            self.execute(
                "INSERT INTO accounts (username, password, is_admin) VALUES ('admin',?,true)",
                (generate_password_hash("password", method="pbkdf2:sha256"),)
            )
        
        test_account = self.fetch("SELECT * FROM accounts WHERE username='test_user'")

        if not test_account:
            self.execute(
                "INSERT INTO accounts (username, password, is_admin) VALUES ('test_user',?,false)",
                (generate_password_hash("password", method="pbkdf2:sha256"),)
            )
        
        self.initialise = True
    
    def __check_empty(self):
        if not self.initialise:
            return

        with closing(self.connection.cursor()) as cursor:
            cursor.execute("SELECT * FROM tickets")
            results: list[sqlite.Row] = cursor.fetchall()
        
        if not results:
            # DB is empty
            with open("database/rows.sql") as rows_file:
                schema: str = rows_file.read().split("-- NEW ROW --")
            
            for query in schema:
                query = query.strip("\n")
                
                with closing(self.connection.cursor()) as cursor:
                    print(query)
                    cursor.execute(query, (datetime.now(),))
                
            self.connection.commit()

    def fetch(self, query: str, params: tuple[any] = ()) -> None | list[Record]:
        self.__check_empty()

        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, params)
            results: list[sqlite.Row] = cursor.fetchall()

        return [Record(item) for item in results]

    def execute(self, query: str, params: tuple[any] = ()) -> None:
        self.__check_empty()

        with closing(self.connection.cursor()) as cursor:
            cursor.execute(query, params)
            self.connection.commit()
    
    def execute_many(self, query: str, params: list[tuple[any]] = ()) -> None:
        self.__check_empty()

        with closing(self.connection.cursor()) as cursor:
            cursor.executemany(query, params)
            self.connection.commit()
